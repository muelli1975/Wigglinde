"""Build unmodified upstream CPU renderer classes plus the research adapter.

Usage: python build.py RVS_SOURCE OPENCV_PREFIX OUTPUT_EXECUTABLE
OPENCV_PREFIX contains include/opencv4 and lib/x86_64-linux-gnu.
Dependencies are explicitly provided by the developer; no downloads here.
"""
from pathlib import Path
import subprocess,sys
source=Path(sys.argv[1]).resolve()/'src';sdk=Path(sys.argv[2]).resolve();lib=sdk/'lib/x86_64-linux-gnu'
names=['BlendedView','PolynomialDepth','Config','Parameters','JsonParser','SynthesizedView','View','blending','inpainting','transform','Unprojector','Projector','PerspectiveUnprojector','PerspectiveProjector','EquirectangularUnprojector','EquirectangularProjector','PoseTraces','SpaceTransformer']
cmd=['g++','-O3','-std=c++11','-DWITH_OPENGL=0','-ffunction-sections','-fdata-sections','-fopenmp','-I'+str(source),'-I'+str(sdk/'include/opencv4')]+[str(source/(n+'.cpp')) for n in names]+[str(Path(__file__).with_name('runner.cpp')),'-L'+str(lib),'-Wl,--gc-sections','-Wl,-rpath,'+str(lib),'-lopencv_photo','-lopencv_imgproc','-lopencv_core','-o',str(Path(sys.argv[3]).resolve())]
subprocess.run(cmd,check=True)
