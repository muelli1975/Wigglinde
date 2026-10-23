// MIT. Exercise the actual frame packer/channel without a Vulkan driver.
#include "frame_output.h"
#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
int main(int argc,char** argv) {
  try {
    if(argc!=4 && argc!=5)throw std::runtime_error("mode width height [--legacy]");
    bool packed=std::string(argv[1])=="rgb24";
    bool legacy=argc==5 && std::string(argv[4])=="--legacy";
    int w=std::stoi(argv[2]),h=std::stoi(argv[3]);
    std::unique_ptr<wigglinde::BinaryFrameOutput> channel;
    FILE* output=stdout;
    if(!legacy) {
      channel=std::make_unique<wigglinde::BinaryFrameOutput>();
      output=channel->get();
    }
#ifdef _WIN32
    else _setmode(_fileno(stdout),_O_BINARY);
#endif
    auto* previous=std::cout.rdbuf(std::cerr.rdbuf());
    // The exact upstream diagnostic: 32 bytes at 1080x720; 33 at 1620x1080.
    std::printf("Real number of elements %i\n",6*(w-1)*(h-1));
    std::cout<<"C++ renderer diagnostic\n";
    wigglinde::RGBFrameBlock block(256,packed);
    std::vector<uint8_t> rgba(256*4);
    for(int frame=0;frame<2;++frame) {
      if(frame)std::printf("C diagnostic between frames\n");
      for(int i=0;i<256;++i) {
        rgba[4*i]=uint8_t((i+17*frame)%256);
        rgba[4*i+1]=uint8_t((37*i+29*frame)%256);
        rgba[4*i+2]=uint8_t((255-i+11*frame)%256);
        rgba[4*i+3]=uint8_t((19*i)%256); // Alpha must not enter RGB.
      }
      block.pack(rgba.data());block.write(output);
    }
    std::cout.rdbuf(previous);
    return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
