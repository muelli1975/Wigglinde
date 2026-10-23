// MIT. Keep renderer diagnostics separate from the binary frame transport.
#pragma once
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <vector>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#else
#include <unistd.h>
#endif

namespace wigglinde {
inline int descriptor(FILE* stream) {
#ifdef _WIN32
  return _fileno(stream);
#else
  return fileno(stream);
#endif
}
inline int duplicate(int fd) {
#ifdef _WIN32
  return _dup(fd);
#else
  return dup(fd);
#endif
}
inline int redirect(int from,int to) {
#ifdef _WIN32
  return _dup2(from,to);
#else
  return dup2(from,to);
#endif
}
inline void closeDescriptor(int fd) {
#ifdef _WIN32
  _close(fd);
#else
  close(fd);
#endif
}

// Save the parent's output pipe before redirecting BOTH C printf and C++ logs.
// Changing cout.rdbuf alone cannot redirect upstream's C printf diagnostics.
class BinaryFrameOutput {
  FILE* frames_=nullptr;
public:
  BinaryFrameOutput() {
    std::fflush(stdout);
    int fd=duplicate(descriptor(stdout));
    if(fd<0)throw std::runtime_error("Cannot duplicate the frame output pipe");
#ifdef _WIN32
    if(_setmode(fd,_O_BINARY)<0) {
      closeDescriptor(fd);
      throw std::runtime_error("Cannot set binary frame output mode");
    }
    frames_=_fdopen(fd,"wb");
#else
    frames_=fdopen(fd,"wb");
#endif
    if(!frames_) {
      closeDescriptor(fd);
      throw std::runtime_error("Cannot open the binary frame output");
    }
    if(redirect(descriptor(stderr),descriptor(stdout))<0) {
      std::fclose(frames_);frames_=nullptr;
      throw std::runtime_error("Cannot redirect renderer diagnostics");
    }
  }
  BinaryFrameOutput(const BinaryFrameOutput&)=delete;
  BinaryFrameOutput& operator=(const BinaryFrameOutput&)=delete;
  ~BinaryFrameOutput() {
    if(frames_) {
      std::fflush(frames_);std::fflush(stdout);
      redirect(descriptor(frames_),descriptor(stdout));
      std::fclose(frames_);
    }
  }
  FILE* get()const{return frames_;}
};

// RVSVulkan already produces RGBA8_UNORM. RGB24 preserves those exact RGB
// bytes; the historical float32 transport remains an explicit supported mode.
class RGBFrameBlock {
  bool packed_;
  std::vector<uint8_t> bytes_;
  std::vector<float> floats_;
public:
  RGBFrameBlock(size_t pixels,bool packed):packed_(packed),
    bytes_(packed?pixels*3:0),floats_(packed?0:pixels*3) {}
  void pack(const uint8_t* rgba) {
    size_t pixels=packed_?bytes_.size()/3:floats_.size()/3;
    for(size_t i=0;i<pixels;++i)for(int ch=0;ch<3;++ch) {
      if(packed_)bytes_[3*i+ch]=rgba[4*i+ch];
      else floats_[3*i+ch]=rgba[4*i+ch]/255.f;
    }
  }
  const void* data()const {
    return packed_?static_cast<const void*>(bytes_.data()):static_cast<const void*>(floats_.data());
  }
  size_t sizeBytes()const{return packed_?bytes_.size():floats_.size()*sizeof(float);}
  void write(FILE* output)const {
    if(std::fwrite(data(),1,sizeBytes(),output)!=sizeBytes() || std::fflush(output))
      throw std::runtime_error("Output cancelled");
  }
};
}
