// Hidden context only; rendering remains in the pinned upstream RVS classes.
#pragma once
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#ifdef _WIN32
#define GLFW_EXPOSE_NATIVE_WIN32
#define GLFW_EXPOSE_NATIVE_WGL
#else
#define GLFW_EXPOSE_NATIVE_X11
#define GLFW_EXPOSE_NATIVE_GLX
#endif
#include <GLFW/glfw3native.h>
#include "helpersGL.hpp"
#include "RFBO.hpp"
#include <stdexcept>
#include <string>
struct GLContext {
 GLFWwindow* window=nullptr;
 std::string vendor,renderer,version;
 GLContext(){
  glfwSetErrorCallback([](int,const char* error){std::cerr<<"OPENGL_INIT: "<<error<<std::endl;});
  if(!glfwInit())throw std::runtime_error("OPENGL_INIT: OpenGL konnte nicht initialisiert werden. Treiber pruefen oder CPU waehlen. / OpenGL initialization failed. Check the graphics driver or select CPU.");
  glfwWindowHint(GLFW_VISIBLE,GLFW_FALSE);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,4);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,4);
  glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
  window=glfwCreateWindow(32,32,"Wigglinde OpenGL",nullptr,nullptr);
  if(!window){glfwTerminate();throw std::runtime_error("OPENGL_INIT: OpenGL 4.4 ist nicht verfuegbar. Treiber pruefen oder CPU waehlen. / OpenGL 4.4 is unavailable. Check the graphics driver or select CPU.");}
  glfwMakeContextCurrent(window);
  auto& native=rvs::opengl::context_NO_WRITE;
#ifdef _WIN32
  native.fakewindow=glfwGetWin32Window(window);native.gldc=GetDC(native.fakewindow);native.glrc=glfwGetWGLContext(window);
#else
  native.disp=glfwGetX11Display();native.win=glfwGetX11Window(window);native.ctx=glfwGetGLXContext(window);
#endif
  native.initialized=true;
  if(ogl_LoadFunctions()==ogl_LOAD_FAILED || !glClearTexImage || !glGenFramebuffers){
   cleanup();throw std::runtime_error("OPENGL_INIT: Required OpenGL functions are unavailable.");
  }
  vendor=reinterpret_cast<const char*>(glGetString(GL_VENDOR));
  renderer=reinterpret_cast<const char*>(glGetString(GL_RENDERER));
  version=reinterpret_cast<const char*>(glGetString(GL_VERSION));
  std::cerr<<"OpenGL: "<<vendor<<" | "<<renderer<<" | "<<version<<std::endl;
 }
 void cleanup(){
#ifdef _WIN32
  auto& native=rvs::opengl::context_NO_WRITE;
  if(native.gldc){ReleaseDC(native.fakewindow,native.gldc);native.gldc=nullptr;}
#endif
  if(window){glfwDestroyWindow(window);window=nullptr;}
  glfwTerminate();rvs::opengl::context_NO_WRITE.initialized=false;
 }
 ~GLContext(){cleanup();}
};
