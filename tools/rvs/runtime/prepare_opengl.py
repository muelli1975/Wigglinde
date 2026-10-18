"""Small integration fixes on copied sources; upstream raster/blend shaders retained."""
from pathlib import Path
import sys
source,output=map(Path,sys.argv[1:]);output.mkdir(parents=True,exist_ok=True)
changes={
 'SynthesizedView.cpp': [('static_cast<InputView&>(input).get_max_depth()', 'input.get_max_depth()')],
 'BlendedView.cpp': [('\t\t\tFBO->toggle();', '\t\t\tFBO->toggle();\n            glDeleteBuffers(1, &quadVBO);\n            glDeleteVertexArrays(1, &quadVAO);')],
 'Shader.cpp': [('#include "Shader.hpp"', '#include "Shader.hpp"\n#include <stdexcept>'), ('if (error) {', 'if (error) {\n                throw std::runtime_error(std::string("OPENGL_INIT: shader ")+type+": "+infoLog);')],
}
for name,replacements in changes.items():
 text=(source/name).read_text()
 for old,new in replacements:
  if text.count(old)!=1:raise ValueError('Unexpected pinned RVS source: '+name+' '+old)
  text=text.replace(old,new)
 (output/name).write_text(text)
