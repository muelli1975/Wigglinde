// MIT. Development-only command-recording regression; no Vulkan driver or GPU.
// Exercise the actual adapter's window and the compiled upstream drawing code.
// Test access uses an explicit-instantiation friend, preserving the original
// class declaration and MSVC's access-dependent member-name mangling.
#include "SourcesVulkan/commonVulkan.h"
#include "SourcesVulkan/InputProvider.h"
#include <optional>
#include "SourcesVulkan/VulkanDrawing.h"
#include "SourcesVulkan/VulkanRenderPassAbstract.h"
#define WIGGLINDE_OUTPUT_CHECK
#include "stream.cpp"

namespace {
struct RecordingMethod {
  using Pointer=void (VulkanDrawing::*)(vk::CommandBuffer&,int,int,std::span<InputProvider::StreamFrameInfo>);
  friend Pointer recordingMethod(RecordingMethod);
};
template<class Tag,typename Tag::Pointer method> struct TestAccess {
  friend typename Tag::Pointer recordingMethod(Tag){return method;}
};
// C++ explicitly permits private names as explicit-instantiation arguments.
template struct TestAccess<RecordingMethod,&VulkanDrawing::recordCommandBuffers>;
int began=0,ended=0,copied=0,recorded=0;
VkImage copiedImage=VK_NULL_HANDLE;
VkBuffer copiedBuffer=VK_NULL_HANDLE;
VkImageLayout copiedLayout=VK_IMAGE_LAYOUT_UNDEFINED;
VkBufferImageCopy copiedRegion{};
VKAPI_ATTR VkResult VKAPI_CALL begin(VkCommandBuffer,const VkCommandBufferBeginInfo*) {++began;return VK_SUCCESS;}
VKAPI_ATTR VkResult VKAPI_CALL end(VkCommandBuffer) {++ended;return VK_SUCCESS;}
VKAPI_ATTR void VKAPI_CALL copy(VkCommandBuffer,VkImage image,VkImageLayout layout,VkBuffer buffer,uint32_t count,const VkBufferImageCopy* regions) {
  if(count!=1)throw std::runtime_error("Expected one output copy");
  ++copied;copiedImage=image;copiedLayout=layout;copiedBuffer=buffer;copiedRegion=regions[0];
}
class TestPass final:public VulkanRenderPassAbstract {
public:
  TestPass(VulkanContext* c,VulkanWrapper* w):VulkanRenderPassAbstract(c,w){}
  void recordCommandBuffer(vk::CommandBuffer&,int,std::span<InputProvider::StreamFrameInfo>,int)override{++recorded;}
  vk::Image getImageToBlit(int)override{return vk::Image(reinterpret_cast<VkImage>(uintptr_t(7)));}
  std::vector<vk::Format> getSupportedDepthFormats()const override{return {};}
};
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
}
int main() {
  try {
    VULKAN_HPP_DEFAULT_DISPATCHER.vkBeginCommandBuffer=begin;
    VULKAN_HPP_DEFAULT_DISPATCHER.vkEndCommandBuffer=end;
    VULKAN_HPP_DEFAULT_DISPATCHER.vkCmdCopyImageToBuffer=copy;
    for(auto extent:{vk::Extent2D(1080,720),vk::Extent2D(1619,1080)}) {
      FileWindow window(extent.width,extent.height,json::array());
      VulkanWrapper wrapper(&window,PipelineMode::Raster);
      TestPass pass(&wrapper.context,&wrapper);
      VulkanDrawing drawing(&wrapper.context,&pass,&window,&wrapper);
      vk::CommandBuffer command(reinterpret_cast<VkCommandBuffer>(uintptr_t(1)));
      require(!window.isSwapChainNeeded(),"Offline window unexpectedly needs a display");
      require(wrapper.getAttachmentSize()==1,"Offline rendering must retain one render slot");
      // The pre-fix drawing code throws the user's exact 'No display image'
      // exception here, before any output-copy command can be recorded.
      (drawing.*recordingMethod(RecordingMethod{}))(command,0,0,{});
      require(copiedImage==static_cast<VkImage>(pass.getImageToBlit(0)),"Wrong render-result image");
      require(copiedBuffer==static_cast<VkBuffer>(window.getRenderingDestination()),"Wrong export buffer");
      require(copiedLayout==VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,"Wrong source layout");
      require(copiedRegion.imageExtent.width==extent.width && copiedRegion.imageExtent.height==extent.height && copiedRegion.imageExtent.depth==1,"Output dimensions changed");
      require(copiedRegion.bufferOffset==0 && copiedRegion.bufferRowLength==0 && copiedRegion.bufferImageHeight==0,"Expected tightly packed output");
    }
    require(began==2 && ended==2 && recorded==2 && copied==2,"Incomplete command recording");
    std::cout<<"Headless output routing passed: actual FileWindow, one render slot, direct image-to-buffer copy at 1080x720 and 1619x1080. Command recording only; no GPU render.\n";
    return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
