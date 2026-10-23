# Additional components in 1.2 Test 2

DEFOM-Stereo code/project: MIT, Insta360 Research Team. Official Small/RVC and
Large/Middlebury checkpoints include Depth Anything V2 weights with separate
terms: Small Apache-2.0; Large **CC-BY-NC-4.0 (noncommercial)**. Large is visibly
marked in the model selector. DINOv2 retains Apache-2.0 attribution. Exact source,
authors, checkpoint hashes, conversion notices and complete license texts are in
[DEFOM notices](tools/defom/NOTICE.md), distributed under `licenses/DEFOM`.
No DEFOM PyTorch/timm/xFormers/CUDA runtime is bundled.

# Third-party components

Wigglinde's own source is MIT. Bundled components retain their own licenses.

| Component | License and source |
| --- | --- |
| LAS2 code and published LAS2-H weights | MIT; https://github.com/TomTomTommi/LiteAnyStereo and https://huggingface.co/tomtomtommi/LiteAnyStereoV2 |
| IGEV++ Middlebury | MIT project notice; https://github.com/gangweiX/IGEV-plusplus . Official checkpoint linked by its authors; source/weight hashes in models/README.md. No separate contradictory weight terms found. |
| timm architecture used for IGEV export | Apache-2.0 notice included; build-only, no timm runtime in the app; https://github.com/huggingface/pytorch-image-models/tree/v0.5.4 |
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
