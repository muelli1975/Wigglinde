# Native DEFOM-Stereo comparison

Development-only tool. Does not register a product model or add runtime
dependencies. No claim of ONNX or DirectML compatibility.

Official source: <https://github.com/antigravity-tech/DEFOM-Stereo>, revision
`5b27591d83956e5d329ff66704271a9e68b1c75f`.

The official `scripts/download_models.sh` and linked public Drive folder identify:

| Variant | Checkpoint | Official Drive file ID |
| --- | --- | --- |
| ViT-S/RVC | `defomstereo_vits_rvc.pth` | `1xEPS7gceJSFn_IHdzebBCgQaRNGwf1aG` |
| ViT-L/Middlebury | `defomstereo_vitl_middlebury.pth` | `1Dy1eGDdtkp2GQYQRTvMwR-3eAzaRCe_k` |

The native script uses the intended evaluation settings from `demo.py` and
`scripts/make_submission.sh`: 32 updates, including 8 scaling updates, the
original correlation implementation and native Depth Anything V2 input-size
calculation. No attention/operator substitutions, changes to the model's built-in
reduction, clipping, iterations or weights. The upstream PyTorch attention path
is used when optional xFormers is absent. Original `InputPadder` pads to 32.

Wigglinde's existing reversible horizontal offset is added before model inference
and removed afterwards. The right disparity is calculated using swapped,
horizontally mirrored eye images, then unmirrored. Input is original-resolution
RGB 0..255; the official network performs its own ImageNet normalization.

Run each model in a separate process to measure peak resident memory. Example:

```sh
python tools/defom/compare_photo.py \
  --source /path/to/pinned/DEFOM-Stereo \
  --weights /path/to/defomstereo_vits_rvc.pth --encoder vits \
  --input /private/FullSBS.jpg --offset 68 --threads 8 \
  --rvs /path/to/wigglinde_rvs --output /private/new-small-run
```

Use `--encoder vitl` with the Middlebury checkpoint for the Large run. Existing
output directories are refused. The tool strictly loads the complete checkpoint,
records its SHA-256 and source revision, saves both signed disparity maps, the
scene, and five unmodified RVS views. It never uploads inputs or outputs.

Research environment: Python 3.12, torch 2.6.0 CPU, torchvision 0.21.0,
timm 0.5.4, opt_einsum 3.4.0, numpy, scipy, Pillow. This is a CPU compatibility
test with those versions; the upstream environment instead specifies torch 2.1.1,
torchvision 0.16.1 and optional accelerated xFormers.

## Licenses

DEFOM-Stereo code: MIT, copyright 2024 Insta360 Research Team. Its official
checkpoint distribution has no separate weight-specific license statement;
applying the project license to those files is the documented project-license
reading. The included Depth Anything V2 components retain their own terms:

- Small weights: Apache-2.0.
- Large weights: CC-BY-NC-4.0, noncommercial use, attribution, license link and
  modification notice required. A subsequent converted package must identify
  the derived model as `DEFOM-L (CC-BY-NC-4.0)`.

Sources: <https://github.com/DepthAnything/Depth-Anything-V2#license>,
<https://creativecommons.org/licenses/by-nc/4.0/>. Record exact distributed
notices if a model is integrated. This branch does not distribute DEFOM source
or weights at this research stage.
