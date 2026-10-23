# DEFOM-Stereo model notices

DEFOM-Stereo, Hualie Jiang, Zhiqiang Lou, Laiyan Ding, Rui Xu, Minglang Tan,
Wenjie Jiang and Rui Huang; CVPR 2025, "DEFOM-Stereo: Depth Foundation Model
Based Stereo Matching". Copyright 2024 Insta360 Research Team. Code under MIT;
the complete notice is included in `DEFOM-MIT.txt` in packaged notices (source:
`UPSTREAM_LICENSE.txt`).

Official source: <https://github.com/antigravity-tech/DEFOM-Stereo>, revision
`5b27591d83956e5d329ff66704271a9e68b1c75f`.
Paper: <https://arxiv.org/abs/2501.09466>.
The official linked weights have no distinct weight-specific statement. The
project MIT license is the documented project-license reading, subject to the
underlying components' retained terms below.

## Depth Anything V2

Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng and
Hengshuang Zhao, "Depth Anything V2", 2024.
<https://github.com/DepthAnything/Depth-Anything-V2>.

**DEFOM-S/RVC** contains Depth Anything V2 Small weights under Apache-2.0.
**DEFOM-L (CC-BY-NC-4.0)** contains Depth Anything V2 Large weights under
Creative Commons Attribution-NonCommercial 4.0 International:
<https://creativecommons.org/licenses/by-nc/4.0/>.
The Large-derived model is for noncommercial use, with attribution, the license
and indication of modifications retained. These restrictions apply to this model
component; the other model options keep their own licenses.

The package includes complete Apache-2.0 and CC-BY-NC-4.0 terms. The CC text is
the SPDX license-list transcription of the identified Creative Commons license:
<https://github.com/spdx/license-list-data/blob/main/text/CC-BY-NC-4.0.txt>.

DINOv2, Meta Platforms, Inc. and affiliates, Apache-2.0:
<https://github.com/facebookresearch/dinov2>. Complete upstream notice included.

## Converted models

Wigglinde converts the official Small/RVC and Large/Middlebury PyTorch weights
to ONNX, with optional mixed Float16/Float32 graphs. No retraining, pruning,
iteration reduction or replacement of the model's native size cap. All 32 updates,
including 8 scale updates, are retained. Export adaptations preserve dynamic
Depth Anything input sizes, bicubic position interpolation including the original
scale offset, and the equivalent single-channel 3x3 unfold. Per-model JSON files
record hashes, exact source revision, precision and conversion details.

| Original checkpoint | SHA-256 |
| --- | --- |
| `defomstereo_vits_rvc.pth` | `aeb52a008f9c689ed23eaea562126ac1307d563fb8687002a657f06a6bf49da4` |
| `defomstereo_vitl_middlebury.pth` | `e8f17e18e8eb4455ddaf6130c6067b40063444acf7558c66d57963e60b539e25` |
