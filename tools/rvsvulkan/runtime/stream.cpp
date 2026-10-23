// Offline file/stream adapter: MIT. Rasterization, visibility and blending use
// pinned HoviTron RVSVulkan sources and shaders (Apache-2.0). The build corrects
// one headless-output branch; rasterization and all shaders remain unchanged.
#include "WindowAbstract.h"
#include "SourcesVulkan/VulkanWrapper.h"
#include "SourcesVulkan/VulkanDrawing.h"
#include "SourcesVulkan/VulkanHelperFunction.h"
#include <nlohmann/json.hpp>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <limits>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using json=nlohmann::json;
using Clock=std::chrono::steady_clock;
namespace fs=std::filesystem;
static double elapsed(Clock::time_point start) {return std::chrono::duration<double>(Clock::now()-start).count();}
static json readJson(const fs::path& path) {std::ifstream f(path);if(!f)throw std::runtime_error("Cannot read "+path.string());return json::parse(f);}
template<class T> static std::vector<T> readRaw(const fs::path& path,size_t size) {
  std::vector<T> data(size);std::ifstream f(path,std::ios::binary);
  if(!f.read(reinterpret_cast<char*>(data.data()),size*sizeof(T)))throw std::runtime_error("Incomplete input: "+path.string());
  return data;
}

// Supply the one fixed output view expected by WindowAbstract. No display or
// swapchain is created; upstream's existing image-to-buffer path is used.
class OutputSlot final:public SwapchainAbstract {
public:
  OutputSlot(uint32_t w,uint32_t h) {swapchainExtent=vk::Extent2D(w,h);swapchainFormat=vk::Format::eR8G8B8A8Unorm;}
  std::tuple<uint32_t,std::optional<vk::Semaphore>> acquireImage()override{return {0,{}};}
  void presentImage(uint32_t,vk::Semaphore&)override{}
  void presentImage(uint32_t,vk::Fence&)override{}
  void cleanup()override{}
  vk::ImageView getSwapchainImageView(int)override{throw std::logic_error("No display image");}
  int getAttachmentSize()override{return 1;}
  vk::Image getSwapchainImage(int)override{throw std::logic_error("No display image");}
  vk::Image getCurrentImage()override{throw std::logic_error("No display image");}
};

class FileWindow final:public WindowAbstract {
  vk::Buffer buffer;vk::DeviceMemory memory;void* mapped=nullptr;
public:
  json cameras;json metrics;
  FileWindow(uint32_t w,uint32_t h,json virtualCameras):cameras(std::move(virtualCameras)) {
    needSwapchain=false;separateFromWindowDim=true;
    swapchains.emplace_back(std::make_unique<OutputSlot>(w,h));
  }
  void initWindow()override{}
  void continueInit()override {
    auto e=getSwapchainExtent(0);auto& c=wrapper->context;
    createBuffer(vk::DeviceSize(e.width)*e.height*4,vk::BufferUsageFlagBits::eTransferDst,
      vk::MemoryPropertyFlagBits::eHostVisible|vk::MemoryPropertyFlagBits::eHostCoherent,buffer,memory,c.device,c.physicalDevice);
    mapped=c.device.mapMemory(memory,0,VK_WHOLE_SIZE,{});
  }
  void cleanUp()override {
    if(mapped){wrapper->context.device.unmapMemory(memory);mapped=nullptr;}
    if(buffer){wrapper->context.device.destroyBuffer(buffer);buffer=nullptr;}
    if(memory){wrapper->context.device.freeMemory(memory);memory=nullptr;}
  }
  void cleanUpSurface()override{}
  void createSurface()override{}
  std::vector<const char*> getRequiredExtensions()override{return {};}
  VkBool32 isDeviceSupportingSufaceKHR(VkPhysicalDevice device,int i)override {
    return bool(vk::PhysicalDevice(device).getQueueFamilyProperties().at(i).queueFlags&vk::QueueFlagBits::eGraphics);
  }
  std::vector<const char*> getRequiredDeviceExtensions()override{return {};}
  SwapChainSupportDetails querySwapChainSupport(vk::PhysicalDevice)override{return {};}
  bool isSynchroWithSemaphore()override{return false;}
  void getFrameBufferSize(int* w,int* h,vk::PhysicalDevice&)override {auto e=getSwapchainExtent(0);*w=e.width;*h=e.height;}
  void checkForCorrectSize()override{}
  vk::Buffer getRenderingDestination()override{return buffer;}
  void resetOrigin()override{}
  void mainLoop(VulkanDrawing* drawing)override {
    auto e=getSwapchainExtent(0);std::vector<float> rgb(size_t(e.width)*e.height*3);
    double render=0,write=0;size_t count=0;auto pipelineStart=Clock::now();
    for(const auto& cam:cameras) {
      auto start=Clock::now();auto p=cam.at("Principle_point");auto f=cam.at("Focal");
      float px=p[0],py=p[1],fx=f[0],fy=f[1];auto position=cam.at("Position");
      // CPU RVS uses OMAF coordinates. The target API uses OpenXR coordinates.
      glm::vec3 target(-float(position[1]),float(position[2]),-float(position[0]));
      glm::vec4 fov(std::atan(-px/fx),std::atan((e.width-px)/fx),std::atan(py/fy),std::atan(-(e.height-py)/fy));
      wrapper->updateSpaceTransform(target,glm::vec3(0),fov,0);
      std::vector<vk::Semaphore> signals;
      auto fence=drawing->submitDrawCall({0,0},{},signals,0);
      if(wrapper->context.device.waitForFences(fence,true,UINT64_MAX)!=vk::Result::eSuccess)throw std::runtime_error("Vulkan output fence failed");
      const auto* rgba=static_cast<const uint8_t*>(mapped);
      for(size_t i=0;i<rgb.size()/3;++i)for(int ch=0;ch<3;++ch)rgb[3*i+ch]=rgba[4*i+ch]/255.f;
      render+=elapsed(start);start=Clock::now();
      if(std::fwrite(rgb.data(),sizeof(float),rgb.size(),stdout)!=rgb.size())throw std::runtime_error("Output cancelled");
      std::fflush(stdout);write+=elapsed(start);++count;
      std::cerr<<"view "<<count<<"/"<<cameras.size()<<std::endl;
    }
    metrics={{"schema_version",1},{"renderer","HoviTron RVSVulkan raster"},{"views",count},{"render_work_seconds",render},
      {"render_pipeline_seconds",elapsed(pipelineStart)},{"stream_write_seconds",write},{"parallel_workers",1},
      {"blending_factor",5.0},{"triangle_threshold",30},{"internal_color_format","RGBA8_UNORM"},
      {"upstream_commit","e0f00f9c67dfd868d2b1489051e9118158b6de03"},
      {"vulkan_device",std::string(wrapper->context.physicalDevice.getProperties().deviceName.data())}};
  }
};

class StaticInputs final:public InputProvider {
  VulkanContext& context;vk::CommandPool pool;
  struct Image {vk::Image image;vk::DeviceMemory memory;vk::ImageView view;};
  std::vector<Image> colors,depths;
  std::vector<StreamParameters> parameters;
  std::vector<StreamFrameInfo> frames;
  Image upload(const void* data,size_t bytes,uint32_t w,uint32_t h,vk::Format format) {
    Image result;vk::Buffer staging;vk::DeviceMemory memory;
    createBuffer(bytes,vk::BufferUsageFlagBits::eTransferSrc,vk::MemoryPropertyFlagBits::eHostVisible|vk::MemoryPropertyFlagBits::eHostCoherent,staging,memory,context.device,context.physicalDevice);
    auto mapped=context.device.mapMemory(memory,0,bytes,{});std::memcpy(mapped,data,bytes);context.device.unmapMemory(memory);
    createImage(context.device,context.physicalDevice,w,h,format,vk::ImageTiling::eOptimal,
      vk::ImageUsageFlagBits::eTransferDst|vk::ImageUsageFlagBits::eSampled,vk::MemoryPropertyFlagBits::eDeviceLocal,result.image,result.memory);
    transitionImageLayout(&context,pool,result.image,format,vk::ImageLayout::eUndefined,vk::ImageLayout::eTransferDstOptimal);
    auto cmd=beginSingleTimeCommands(&context,pool);
    vk::BufferImageCopy copy(0,0,0,vk::ImageSubresourceLayers(vk::ImageAspectFlagBits::eColor,0,0,1),vk::Offset3D(0,0,0),vk::Extent3D(w,h,1));
    cmd.copyBufferToImage(staging,result.image,vk::ImageLayout::eTransferDstOptimal,copy);
    endSingleTimeCommands(&context,pool,cmd);
    transitionImageLayout(&context,pool,result.image,format,vk::ImageLayout::eTransferDstOptimal,vk::ImageLayout::eShaderReadOnlyOptimal);
    context.device.destroyBuffer(staging);context.device.freeMemory(memory);
    result.view=createImageView(context.device,result.image,format,vk::ImageAspectFlagBits::eColor);return result;
  }
public:
  StaticInputs(VulkanWrapper& wrapper,const json& cfg,const json& real):context(wrapper.context) {
    pool=context.device.createCommandPool(vk::CommandPoolCreateInfo({},context.queueFamilyIndex));
    // The CPU adapter's .01/999 metadata are unused by its float-depth loader.
    // RVSVulkan normalizes quality by farDepth: supply the actual common bounds
    // of the metric float maps, as required by its streaming API. Depth samples,
    // projection and shaders are unchanged. Do not normalize the depth images.
    std::vector<std::vector<float>> depthData;float zMin=FLT_MAX,zMax=0;
    for(size_t i=0;i<real.size();++i) {
      size_t pixels=size_t(real[i]["Resolution"][0].get<uint32_t>())*real[i]["Resolution"][1].get<uint32_t>();
      depthData.push_back(readRaw<float>(fs::u8path(cfg["DepthMapNames"][i].get<std::string>()),pixels));
      for(float z:depthData.back()){zMin=std::min(zMin,z);zMax=std::max(zMax,z);}
    }
    float nearDepth=std::nextafter(zMin,0.f),farDepth=std::nextafter(zMax,std::numeric_limits<float>::infinity());
    for(size_t i=0;i<real.size();++i) {
      auto cam=real[i];uint32_t w=cam["Resolution"][0],h=cam["Resolution"][1];size_t pixels=size_t(w)*h;
      auto color=readRaw<float>(fs::u8path(cfg["ViewImageNames"][i].get<std::string>()),pixels*3);
      std::vector<uint8_t> rgba(pixels*4,255);
      for(size_t p=0;p<pixels;++p)for(int ch=0;ch<3;++ch)rgba[4*p+ch]=uint8_t(std::lround(std::clamp(color[3*p+ch],0.f,1.f)*255.f));
      const auto& depth=depthData[i];
      colors.push_back(upload(rgba.data(),rgba.size(),w,h,vk::Format::eR8G8B8A8Unorm));
      depths.push_back(upload(depth.data(),depth.size()*sizeof(float),w,h,vk::Format::eR32Sfloat));
      StreamParameters param;param.streamName=cam["Name"];param.colorResolution=param.depthResolution=glm::ivec2(w,h);
      param.nearDepth=nearDepth;param.farDepth=farDepth;
      param.colorFormat=vk::Format::eR8G8B8A8Unorm;param.depthFormat=vk::Format::eR32Sfloat;
      param.projectionType=ProjectionType::PROJECTION_PERSPECTIVE;
      auto sampler=[](vk::Filter filter){return vk::SamplerCreateInfo({},filter,filter,vk::SamplerMipmapMode::eNearest,vk::SamplerAddressMode::eClampToEdge,vk::SamplerAddressMode::eClampToEdge,vk::SamplerAddressMode::eClampToEdge).setBorderColor(vk::BorderColor::eFloatOpaqueBlack);};
      // Same color/depth sampling as upstream DynamicInputProvider's RGB path.
      param.colorSampler=context.device.createSampler(sampler(vk::Filter::eLinear));
      param.depthSampler=context.device.createSampler(sampler(vk::Filter::eNearest));parameters.push_back(param);
      StreamFrameInfo frame;frame.imageIndex=0;auto p=cam["Position"];
      frame.extrinsics.position=glm::vec3(float(p[0]),float(p[1]),float(p[2]));frame.extrinsics.rotation=glm::vec3(0);
      frame.intrinsics=PerspectiveIntrinsics{glm::vec2(float(cam["Focal"][0]),float(cam["Focal"][1])),glm::vec2(float(cam["Principle_point"][0]),float(cam["Principle_point"][1]))};frames.push_back(frame);
    }
  }
  std::vector<StreamParameters> enumerateStreamsParameters()const override{return parameters;}
  std::vector<StreamImage> enumerateStreamImages(uint32_t i,bool depth)const override{const auto& image=(depth?depths:colors).at(i);return {{image.image,image.view}};}
  void acquireStreamsFrames(const Extrinsics&,std::span<StreamFrameInfo> out)override{std::copy(frames.begin(),frames.end(),out.begin());}
  void releaseStreamsFrames()override{}
  ~StaticInputs()override {
    for(auto& p:parameters){context.device.destroySampler(p.colorSampler);context.device.destroySampler(p.depthSampler);}
    for(const auto* images:{&colors,&depths})for(auto& im:*images){context.device.destroyImageView(im.view);context.device.destroyImage(im.image);context.device.freeMemory(im.memory);}
    context.device.destroyCommandPool(pool);
  }
};

int run(int argc,char** argv) {
  try {
    if(argc==2 && std::string(argv[1])=="--identity") {
      std::cout<<"HoviTron RVSVulkan e0f00f9c67dfd868d2b1489051e9118158b6de03; raster; Simple 5; threshold 30; unmodified shaders\n";return 0;
    }
    if(argc!=3 && argc!=5)throw std::runtime_error("wigglinde_rvsvulkan config.json metrics.json [ignored_CPU_workers ignored_CPU_threads]");
    auto cfg=readJson(fs::absolute(fs::u8path(argv[1])));auto metricsPath=fs::absolute(fs::u8path(argv[2]));
    // Resolve the existing RVS adapter's paths before entering the shader folder.
    for(const char* key:{"InputCameraParameterFile","VirtualCameraParameterFile"}) {
      auto path=fs::absolute(fs::u8path(cfg.at(key).get<std::string>())).u8string();
      cfg[key]=std::string(path.begin(),path.end());
    }
    for(const char* key:{"ViewImageNames","DepthMapNames"})for(auto& value:cfg.at(key)) {
      auto path=fs::absolute(fs::u8path(value.get<std::string>())).u8string();
      value=std::string(path.begin(),path.end());
    }
    auto allCameras=readJson(fs::u8path(cfg.at("InputCameraParameterFile").get<std::string>())).at("cameras");
    auto lookup=[&](const json& names){json result=json::array();for(auto& name:names){bool found=false;for(auto& cam:allCameras)if(cam["Name"]==name){result.push_back(cam);found=true;break;}if(!found)throw std::runtime_error("Camera missing");}return result;};
    auto real=lookup(cfg.at("InputCameraNames")),targets=lookup(cfg.at("VirtualCameraNames"));
    if(real.size()!=2 || targets.empty())throw std::runtime_error("Expected stereo inputs and target views");
    uint32_t w=real[0]["Resolution"][0],h=real[0]["Resolution"][1];
    fs::current_path(fs::absolute(fs::u8path(argv[0])).parent_path());
#ifdef _WIN32
    _setmode(_fileno(stdout),_O_BINARY);
#endif
    std::cout.rdbuf(std::cerr.rdbuf());auto inputStart=Clock::now();
    // Upstream also links the loader. Keep our dynamically loaded copy alive
    // until all function pointers and Vulkan objects have finished using it.
    vk::DynamicLoader loaderLifetime;
    FileWindow window(w,h,targets);VulkanWrapper wrapper(&window,PipelineMode::Raster);wrapper.init();
    if(wrapper.context.physicalDevice.getProperties().deviceType==vk::PhysicalDeviceType::eCpu)
      throw std::runtime_error("RVSVulkan GPU selected, but the Vulkan driver is a CPU software renderer");
    {
      StaticInputs inputs(wrapper,cfg,real);wrapper.endInit(&inputs,StartingPosition::Zero);
      double inputTime=elapsed(inputStart);wrapper.start();wrapper.waitIdle();
      window.metrics["input_seconds"]=inputTime;
      auto streams=inputs.enumerateStreamsParameters();
      window.metrics["input_depth_range"]={streams[0].nearDepth,streams[0].farDepth};
      std::ofstream output(metricsPath);output<<window.metrics.dump(2);output.close();
      wrapper.cleanUp();
    }
    wrapper.context.cleanUp();return 0;
  }catch(const std::exception& e){std::cerr<<"RVSVulkan: "<<e.what()<<std::endl;return 1;}
}
#ifndef WIGGLINDE_OUTPUT_CHECK
#ifdef _WIN32
int wmain(int argc,wchar_t** argv) {
  std::vector<std::string> encoded;std::vector<char*> args;
  for(int i=0;i<argc;++i){auto u8=fs::path(argv[i]).u8string();encoded.emplace_back(u8.begin(),u8.end());}
  for(auto& s:encoded)args.push_back(s.data());
  return run(argc,args.data());
}
#else
int main(int argc,char** argv){return run(argc,argv);}
#endif
#endif
