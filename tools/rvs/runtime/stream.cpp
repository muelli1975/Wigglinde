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
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
template<class M> M readmat(const std::string&p,cv::Size size){M m(size);std::ifstream f(p,std::ios::binary);f.read((char*)m.data,m.total()*m.elemSize());if(!f)throw std::runtime_error("Datei konnte nicht gelesen werden: "+p);return m;}
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("wigglinde_rvs config.json");
#ifdef _WIN32
 _setmode(_fileno(stdout),_O_BINARY);
#endif
 // Upstream diagnostic text must never enter the binary frame stream.
 std::cout.rdbuf(std::cerr.rdbuf());cv::setNumThreads(8);rvs::g_with_opengl=false;
 auto cfg=rvs::Config::loadFromFile(argv[1]);std::vector<rvs::View> inputs;
 for(int i=0;i<2;i++){
  auto size=cfg.params_real[i].getSize();
  inputs.emplace_back(readmat<cv::Mat3f>(cfg.texture_names[i],size),readmat<cv::Mat1f>(cfg.depth_names[i],size),cv::Mat1f(size,1.f),cv::Mat1f(size,1.f));
 }
 for(size_t v=0;v<cfg.params_virtual.size();v++){
  rvs::BlendedViewMultiSpec blender(1.f,4.f);
  for(int i=0;i<2;i++){
   rvs::GenericTransformer tr;tr.set_inputPosition(&cfg.params_real[i]);tr.set_targetPosition(&cfg.params_virtual[v]);
   rvs::SynthetisedViewTriangle synth;synth.setSpaceTransformer(&tr);synth.compute(inputs[i]);blender.blend(synth);
  }
  auto color=rvs::detail::inpaint(blender.get_color(),blender.get_inpaint_mask(),true);
  cv::resize(color,color,cfg.params_virtual[v].getSize());
  if(!color.isContinuous())color=color.clone();
  size_t bytes=color.total()*color.elemSize();
  if(std::fwrite(color.data,1,bytes,stdout)!=bytes)throw std::runtime_error("Ausgabe abgebrochen");
  std::fflush(stdout);std::cerr<<"view "<<v+1<<"/"<<cfg.params_virtual.size()<<std::endl;
 }
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
