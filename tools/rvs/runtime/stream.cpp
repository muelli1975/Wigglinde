// Thin application adapter to unmodified MPEG-I RVS classes. Adapter license: MIT.
#include "Config.hpp"
#include "View.hpp"
#include "SynthesizedView.hpp"
#include "BlendedView.hpp"
#include "SpaceTransformer.hpp"
#include "inpainting.hpp"
#include <opencv2/imgproc.hpp>
#include <fstream>
#include <iostream>
#include <cstdio>
#include <chrono>
#include <future>
#include <vector>
#include <algorithm>
#include <memory>
#ifdef WIGGLINDE_OPENGL
#include "gl_context.hpp"
#endif
#ifndef _WIN32
#include <unistd.h>
#endif
#ifdef _OPENMP
#include <omp.h>
#endif
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using Clock=std::chrono::steady_clock;
double seconds(Clock::time_point t){return std::chrono::duration<double>(Clock::now()-t).count();}
std::string quoted(const std::string& s){std::string out="\"";for(char c:s){if(c=='"' || c=='\\')out+='\\';if(static_cast<unsigned char>(c)>=32)out+=c;}return out+"\"";}
struct Stats {
 std::string path,backend="cpu",vendor,gpu,version;double input=0,render=0,write=0,pipeline=0;size_t views=0;int workers=1,inner=0,opencv=8;
 void save()const noexcept{try{if(path.empty())return;std::ofstream f(path);f<<"{\"schema_version\":2,\"input_seconds\":"<<input<<",\"render_work_seconds\":"<<render<<",\"render_pipeline_seconds\":"<<pipeline<<",\"stream_write_seconds\":"<<write<<",\"views\":"<<views<<",\"parallel_workers\":"<<workers<<",\"threads_per_view\":"<<inner<<",\"opencv_threads\":"<<opencv<<",\"backend\":"<<quoted(backend)<<",\"gl_vendor\":"<<quoted(vendor)<<",\"gl_renderer\":"<<quoted(gpu)<<",\"gl_version\":"<<quoted(version)<<"}";}catch(...){}}
};
template<class M> M readmat(const std::string&p,cv::Size size){M m(size);std::ifstream f(p,std::ios::binary);f.read((char*)m.data,m.total()*m.elemSize());if(!f)throw std::runtime_error("Datei konnte nicht gelesen werden: "+p);return m;}
int main(int argc,char**argv){Stats stats;try{
 if(argc!=3 && argc!=5)throw std::runtime_error("wigglinde_rvs config.json metrics.json [workers threads_per_view]");
 if(argc==5){stats.workers=std::stoi(argv[3]);stats.inner=std::stoi(argv[4]);if(stats.workers<1 || stats.inner<1)throw std::runtime_error("Invalid thread count");}
 stats.opencv=stats.workers>1?1:(stats.inner?stats.inner:8);
 stats.path=argv[2];auto input_start=Clock::now();
#ifdef _WIN32
 _setmode(_fileno(stdout),_O_BINARY);
#endif
 // Upstream diagnostic text must never enter the binary frame stream.
 std::cout.rdbuf(std::cerr.rdbuf());
 // Keep C printf diagnostics out of the binary pipe as well as C++ cout.
#ifdef _WIN32
 FILE* output=_fdopen(_dup(_fileno(stdout)),"wb");_dup2(_fileno(stderr),_fileno(stdout));
#else
 FILE* output=fdopen(dup(fileno(stdout)),"wb");dup2(fileno(stderr),fileno(stdout));
#endif
 if(!output)throw std::runtime_error("Could not open frame stream");
#ifdef WIGGLINDE_OPENGL
 stats.workers=1;stats.backend="opengl";stats.opencv=stats.inner?stats.inner:8;
 GLContext context;stats.vendor=context.vendor;stats.gpu=context.renderer;stats.version=context.version;
 rvs::g_with_opengl=true;
#else
 rvs::g_with_opengl=false;
#endif
 cv::setNumThreads(stats.opencv);
 auto cfg=rvs::Config::loadFromFile(argv[1]);std::vector<rvs::View> inputs;
 for(int i=0;i<2;i++){
  auto size=cfg.params_real[i].getSize();
  inputs.emplace_back(readmat<cv::Mat3f>(cfg.texture_names[i],size),readmat<cv::Mat1f>(cfg.depth_names[i],size),cv::Mat1f(size,1.f),cv::Mat1f(size,1.f));
 }
 stats.input=seconds(input_start);
 struct Result {cv::Mat3f color;double elapsed;};
 auto compute=[&](size_t v){
#ifdef _OPENMP
  if(stats.inner)omp_set_num_threads(stats.inner);
#endif
  auto render_start=Clock::now();
#ifdef WIGGLINDE_OPENGL
  const auto target_size=cfg.params_virtual[v].getSize();
  auto fbo=rvs::opengl::RFBO::getInstance();fbo->init(target_size);fbo->clear_buffers();
  if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE && glGetError()!=GL_NO_ERROR)
   throw std::runtime_error("OpenGL framebuffer initialization failed");
#endif
  rvs::BlendedViewSimple blender(5.f);
  for(int i=0;i<2;i++){
#ifdef WIGGLINDE_OPENGL
   rvs::OpenGLTransformer tr;
#else
   rvs::GenericTransformer tr;
#endif
   tr.set_inputPosition(&cfg.params_real[i]);tr.set_targetPosition(&cfg.params_virtual[v]);
   rvs::SynthetisedViewTriangle synth;synth.setSpaceTransformer(&tr);synth.compute(inputs[i]);blender.blend(synth);
  }
#ifdef WIGGLINDE_OPENGL
  blender.assignFromGL2CV(target_size);
  GLenum gl_error=glGetError();if(gl_error!=GL_NO_ERROR)throw std::runtime_error("OpenGL rendering failed: "+std::to_string(gl_error));
#endif
  auto color=rvs::detail::inpaint(blender.get_color(),blender.get_inpaint_mask(),true);
  cv::resize(color,color,cfg.params_virtual[v].getSize());
  if(!color.isContinuous())color=color.clone();
  return Result{color,seconds(render_start)};
 };
 // A fixed-size rolling window preserves output order and bounds completed
 // frames as well as active work. Input matrices/configuration remain read-only.
 stats.workers=std::min(stats.workers,std::max(1,int(cfg.params_virtual.size())));
 auto pipeline_start=Clock::now();
 std::vector<std::future<Result>> pending(stats.workers);
 size_t next=0;
 auto launch=[&](size_t slot){
  const size_t index=next++;
  pending[slot]=std::async(std::launch::async,compute,index);
 };
 if(stats.workers>1)for(int slot=0;slot<stats.workers && next<cfg.params_virtual.size();++slot)launch(slot);
 for(size_t v=0;v<cfg.params_virtual.size();v++){
  Result result;
  if(stats.workers==1)result=compute(v);
  else{
   const size_t slot=v%stats.workers;
   result=pending[slot].get();
   if(next<cfg.params_virtual.size())launch(slot);
  }
  const auto& color=result.color;
  size_t bytes=color.total()*color.elemSize();
  stats.render+=result.elapsed;auto write_start=Clock::now();
  if(std::fwrite(color.data,1,bytes,output)!=bytes)throw std::runtime_error("Ausgabe abgebrochen");
  std::fflush(output);std::cerr<<"view "<<v+1<<"/"<<cfg.params_virtual.size()<<std::endl;
  stats.write+=seconds(write_start);stats.views++;
 }
#ifdef WIGGLINDE_OPENGL
 rvs::opengl::RFBO::getInstance()->free();
#endif
 std::fclose(output);stats.pipeline=seconds(pipeline_start);stats.save();return 0;
}catch(const std::exception&e){stats.save();std::cerr<<e.what()<<std::endl;return 1;}}
