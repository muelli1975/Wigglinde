# Third-party components

Wigglinde's own source is MIT. Bundled components retain their own licenses.

| Component | License and source |
| --- | --- |
| LAS2 code and published LAS2-H weights | MIT; https://github.com/TomTomTommi/LiteAnyStereo and https://huggingface.co/tomtomtommi/LiteAnyStereoV2 |
| IGEV++ Middlebury | MIT project notice; https://github.com/gangweiX/IGEV-plusplus . Official checkpoint linked by its authors; source/weight hashes in models/README.md. No separate contradictory weight terms found. |
| timm architecture used for IGEV export | Apache-2.0 notice included; build-only, no timm runtime in the app; https://github.com/huggingface/pytorch-image-models/tree/v0.5.4 |
| RVS | Modified BSD, including its patent/third-party-rights reservation; https://gitlab.com/mpeg-i-visual/rvs |
| HoviTron RVSVulkan (separate test) | Apache-2.0; https://gitlab.ulb.be/hovitron/hovitron-pipeline |
| GLM 0.9.9.8 | MIT; https://github.com/g-truc/glm/tree/0.9.9.8 |
| nlohmann/json 3.11.3 | MIT; https://github.com/nlohmann/json/tree/v3.11.3 |
| Vulkan-Headers 1.3.275 | Apache-2.0 / MIT notices included; https://github.com/KhronosGroup/Vulkan-Headers/tree/v1.3.275 |
| OpenCV 4.10 | Apache-2.0 and third-party notices; https://github.com/opencv/opencv/tree/4.10.0 |
| ONNX Runtime | MIT; https://github.com/microsoft/onnxruntime |
| NumPy | BSD-3-Clause and bundled notices; https://numpy.org |
| Pillow | HPND and bundled notices; https://python-pillow.org |
| CustomTkinter / darkdetect | MIT / BSD-3-Clause; https://github.com/TomSchimansky/CustomTkinter |
| imageio-ffmpeg wrapper | BSD-2-Clause; https://github.com/imageio/imageio-ffmpeg |
| FFmpeg executable | Bundled GPL-3.0 text and executable configuration. Source/build scripts: https://github.com/imageio/imageio-ffmpeg and https://ffmpeg.org/download.html#get-sources |
| Microsoft VC runtime | Microsoft redistributable runtime terms; https://visualstudio.microsoft.com/license-terms/ |
| Python / Tcl / Tk | Respective PSF/Tcl/Tk licenses included with the runtime |

Exact versions and build commit accompany the package. No claim is made that these
licenses grant all third-party patent rights. No component is downloaded by the app.

RVSVulkan copyright 2023 Université Libre de Bruxelles (ULB), Universidad
Politécnica de Madrid (UPM), CREAL, Deutsches Zentrum für Luft- und Raumfahrt
(DLR). The separate test uses revision
`e0f00f9c67dfd868d2b1489051e9118158b6de03`. Its Apache-2.0 license and the
dependency notices accompany the package. The offline file adapter is Wigglinde
code. One generated build copy of `VulkanDrawing.cpp` corrects its headless-output
condition to use `isSwapChainNeeded()` instead of the internal render-slot count;
the original checkout, rasterization, blending and all shaders remain unchanged.
The installed graphics driver's
Vulkan runtime is used and is not redistributed in the package.

The Windows package uses ONNX Runtime DirectML 1.24.4 from official source on Windows
(including the CPU provider), with `onnxruntime_USE_TELEMETRY=OFF`.
Source revision: `2d924974ef147392ced8409d36bd6d2e7fcc8a74`.
Retain its bundled MIT license, third-party notices and DirectML redistributable
license. Official provider requirements: https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
The unchanged completion sound is from SplatTricia commit
`6217bb40629fd2c6f06a4662850e14610919b9b7`, `assets/ready.wav`,
Git blob `260fb0d49982873a13dabd750b997448acb675ca`, same project owner.

The GPU model is converted from the same H export with ONNX Runtime’s Float16
converter, retaining Float32 islands. No separate weights or model license is introduced.

## Native Linux and macOS packages

CPU packages use official ONNX Runtime (MIT); Intel macOS uses 1.23.2 because
1.24.4 publishes macOS wheels only for Apple Silicon. macOS memory accounting uses
psutil (BSD-3-Clause). OpenCV is built statically with bundled zlib/libpng and its
third-party notices are included. RVS OpenMP uses LLVM libomp on macOS (Apache-2.0
with LLVM exceptions) or GCC libgomp on Linux (GPL with GCC Runtime Library
Exception). The original completion WAV and ICO are included unchanged.

## IGEV++ checkpoint provenance

The official MIT repository explicitly links the pretrained checkpoints, including
Middlebury. We apply that project notice to its official checkpoint distribution;
this is the recorded project-license reading, not a claim of a separate PTH-specific
author statement. No added research/noncommercial restriction was found.
Official download confirmation: https://github.com/gangweiX/IGEV-plusplus/issues/2 .
The same author confirms MIT when asked about commercial use of the predecessor:
https://github.com/gangweiX/IGEV/issues/6 . The project notices and SHA provenance
accompany the converted ONNX weights. LAS2 and RVS notices remain applicable.
