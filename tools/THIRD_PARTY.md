# Third-party components

Wigglinde's own source is MIT. Bundled components retain their own licenses.

| Component | License and source |
| --- | --- |
| LAS2 code and published LAS2-M/L/H weights | MIT; https://github.com/TomTomTommi/LiteAnyStereo and https://huggingface.co/tomtomtommi/LiteAnyStereoV2 |
| RVS | Modified BSD, including its patent/third-party-rights reservation; https://gitlab.com/mpeg-i-visual/rvs |
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

Test 2 builds ONNX Runtime DirectML 1.24.4 from official source on Windows
(including the CPU provider), with `onnxruntime_USE_TELEMETRY=OFF`.
Source revision: `2d924974ef147392ced8409d36bd6d2e7fcc8a74`.
Retain its bundled MIT license, third-party notices and DirectML redistributable
license. Official provider requirements: https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
The unchanged completion sound is from SplatTricia commit
`6217bb40629fd2c6f06a4662850e14610919b9b7`, `assets/ready.wav`,
Git blob `260fb0d49982873a13dabd750b997448acb675ca`, same project owner.
