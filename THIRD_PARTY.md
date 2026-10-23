# Components added by the isolated 1.2 Test 1 branch

- GREAT-Stereo, classical GREAT-IGEV Middlebury: Apache-2.0 project source at
  `2a6b1efede8c3a9eec9540790c2700ea2f3dee7d`; exact official linked checkpoint
  SHA-256 `2f11060a718713df561cfb402494c11f05b157ce8a5da1b8364a0b9d53ef29cb`.
  No separate weight-license statement was found; applying the project license
  is recorded as that reading. See [GREAT study](docs/GREAT_IGEV_STUDY.md).
  The package includes the unchanged Apache text, attribution and build adapter
  source. PyTorch, timm, OpenCV Python and other training tools are not runtime
  components; the existing timm Apache notice is retained.
- TMIV/VWS: unchanged source at `8faacbe722f0e2fc1dc6f8247eb2da166a0297c6`,
  BSD three-clause ISO/IEC license, including its contributor/patent-rights
  reservation. No source patches, VVC/HEVC codecs or MIV bitstream support added.
- fmt 11.0.2, commit `0c9fce2ffefecfdce794e1859584e25877b7b592`, MIT license;
  statically linked into the TMIV renderer.

Source provenance and notices are included in `licenses` in the test package.
The following sections describe the retained 1.1 components.

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
