// Research adapter to the unmodified MPEG-I RVS CPU classes.
// Wigglinde adapter: MIT. RVS retains its own LICENSE.
#include "Config.hpp"
#include "View.hpp"
#include "SynthesizedView.hpp"
#include "BlendedView.hpp"
#include "SpaceTransformer.hpp"
#include "inpainting.hpp"
#include <opencv2/imgproc.hpp>
#include <fstream>
#include <iostream>
#include <chrono>
#include <memory>
#include <cmath>
#include <sys/resource.h>
template<class M> M readmat(const std::string& path, cv::Size size) {
 M m(size);std::ifstream f(path,std::ios::binary);
 f.read((char*)m.data,m.total()*m.elemSize());if(!f)throw std::runtime_error("Read failed: "+path);return m;
}
void save(const std::string& p,cv::Mat m){std::ofstream f(p,std::ios::binary);f.write((char*)m.data,m.total()*m.elemSize());if(!f)throw std::runtime_error("Write failed");}
int main(int argc,char**argv){try{
 if(argc!=4 && argc!=5)throw std::runtime_error("runner config.json output-prefix simple|multi [--verify-projection]");
 const bool verify=argc==5;
 if(verify && std::string(argv[4])!="--verify-projection")throw std::runtime_error("Unknown option");
 cv::setNumThreads(8);rvs::g_with_opengl=false;
 auto cfg=rvs::Config::loadFromFile(argv[1]);
 std::vector<rvs::View> inputs;
 for(int i=0;i<2;i++){
  auto size=cfg.params_real[i].getSize();
  inputs.emplace_back(readmat<cv::Mat3f>(cfg.texture_names[i],size),readmat<cv::Mat1f>(cfg.depth_names[i],size),cv::Mat1f(size,1.f),cv::Mat1f(size,1.f));
 }
 double error=0.,verification=0.,synthesis=0.,blending=0.,filling=0.,resizing=0.,writing=0.;
 auto now=[](){return std::chrono::steady_clock::now();};
 auto seconds=[&](std::chrono::steady_clock::time_point start){return std::chrono::duration<double>(now()-start).count();};
 auto allstart=now();
 for(size_t v=0;v<cfg.params_virtual.size();v++){
  auto start=std::chrono::steady_clock::now();
  std::unique_ptr<rvs::BlendedView> blender;
  if(std::string(argv[3])=="multi")blender.reset(new rvs::BlendedViewMultiSpec(1.f,4.f));
  else blender.reset(new rvs::BlendedViewSimple(1.f));
  for(int i=0;i<2;i++){
   rvs::GenericTransformer tr;tr.set_inputPosition(&cfg.params_real[i]);tr.set_targetPosition(&cfg.params_virtual[v]);
   // Explicit development test only; never repeat in normal batch rendering.
   if(verify){auto checkstart=now();
   auto uv=tr.generateImagePos();auto xyz=tr.unproject(uv,inputs[i].get_depth());auto trans=tr.get_translation();auto rot=tr.get_rotation();
   for(int y=0;y<xyz.rows;y++)for(int x=0;x<xyz.cols;x++)xyz(y,x)=rot*xyz(y,x)+trans;
   cv::Mat1f z;rvs::WrappingMethod wrap;auto projected=tr.project(xyz,z,wrap);
   double t=-cfg.params_virtual[v].getPosition()[1];
   for(int y=0;y<uv.rows;y++)for(int x=0;x<uv.cols;x++){
    double d=cfg.params_real[i].getFocal()[0]/inputs[i].get_depth()(y,x)-64.;
    double expected=uv(y,x)[0]+(i?1-t:-t)*d;
    error=std::max(error,std::abs(projected(y,x)[0]-expected));
    error=std::max(error,std::abs(double(projected(y,x)[1]-uv(y,x)[1])));
   }
   verification+=seconds(checkstart);}
   rvs::SynthetisedViewTriangle synth;synth.setSpaceTransformer(&tr);
   auto partstart=now();synth.compute(inputs[i]);synthesis+=seconds(partstart);
   partstart=now();blender->blend(synth);blending+=seconds(partstart);
  }
  auto partstart=now();auto mask=blender->get_inpaint_mask();
  auto color=rvs::detail::inpaint(blender->get_color(),mask,true);
  filling+=seconds(partstart);partstart=now();
  cv::resize(color,color,cfg.params_virtual[v].getSize());
  cv::resize(mask,mask,cfg.params_virtual[v].getSize(),0,0,cv::INTER_NEAREST);
  resizing+=seconds(partstart);partstart=now();
  std::string stem=std::string(argv[2])+"_"+std::to_string(v);
  save(stem+".rgb",color);save(stem+".mask",mask);
  writing+=seconds(partstart);
  std::cout<<"view "<<v<<" seconds "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<std::endl;
 }
 struct rusage ru;getrusage(RUSAGE_SELF,&ru);
 if(verify)std::cout<<"projection_max_error_px "<<error<<std::endl;
 std::cout<<"total_seconds "<<seconds(allstart)<<" peak_rss_kib "<<ru.ru_maxrss<<std::endl;
 std::cout<<"stages_seconds verification "<<verification<<" synthesis "<<synthesis<<" blending "<<blending<<" filling "<<filling<<" resizing "<<resizing<<" writing "<<writing<<std::endl;
 return error<0.001?0:2;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
