# GREAT-IGEV Middlebury experiment — 23 October 2026

This is an internal model and ONNX feasibility experiment. It changes no
application code, model menu, defaults, stable tag or released package.

## Exact model and environment

- Official source: https://github.com/JarvisLee0423/GREAT-Stereo
- Revision: `2a6b1efede8c3a9eec9540790c2700ea2f3dee7d`.
- Classical GREAT-IGEV, not Solid, DepthAny or GREATEN. No depth foundation model.
- Official weights: `basic_version/IGEV/great-igev-middlebury-submit.pth` in the
  README-linked [checkpoint folder](https://drive.google.com/drive/folders/1EZ_hScBixV9opzX7W3ItJXlqS5uNKZvJ).
  Google Drive file ID: `1OPRHwfLid56J4Bvo7Lzx_7wkJujGD40f`.
- Checkpoint SHA-256:
  `2f11060a718713df561cfb402494c11f05b157ce8a5da1b8364a0b9d53ef29cb`.
- Complete strict state-dictionary load, 14,436,744 parameters. Constructor-only
  `timm` pretrained downloads disabled because the complete checkpoint replaces
  those parameters. No omitted weights or separate ImageNet dependency.
- Official Middlebury settings: 32 iterations, max disparity 768, three GRU
  layers, channels 128/128/128, downsample 2, cost-volume levels 2/radius 4.
- Linux x64, eight CPU threads, no GPU. torch 2.6.0+cpu, torchvision 0.21.0+cpu,
  timm 0.5.4, ONNX 1.17.0, ONNX Runtime 1.24.4, NumPy 2.5.2, Pillow 12.3.0.
  Other source imports: scipy 1.18.1, einops 0.8.2, OpenCV headless 5.0.0.93.

The source has Apache-2.0 licensing. No separate license statement for the
official linked checkpoint was found. Applying the project license to that
checkpoint is a project-license reading, not an independent explicit weight
license. This research branch does not distribute it. Retain the exact upstream
and dependency notices if it is later packaged. The application's own MIT license
does not replace these component licenses.

## Memory-preserving execution and export

At the photograph's padded 1120×704 dimensions, the original concat volume alone
is approximately 6.8 GiB: 1×192×192×176×280 Float32 values. The test host has an
8 GiB cgroup limit. The native experiment therefore evaluates the concat stem in
chunks of 32 disparity planes with two halo planes per side. The three stem
convolutions have disparity kernels 1/3/3. All 192 planes are retained; there is
no image tiling, reduced search range, cropping, smoothing or changed weight.

Feature-volume comparison at widths 17 and 208: maximum absolute differences
3.70e-6 and 4.95e-6. A complete 416×128 synthetic 32-iteration model run was
bit-identical to original execution. This establishes those checked cases only.

Dynamic ONNX export additionally requires equivalent operator implementations:

1. Identity grouped convolutions for `Unfold`.
2. Identity grouped transposed convolutions for overlapping `Fold` sums, using
   the model's kernels 3/5/7, stride 1 and padding kernel//2.
3. Symbolic height/width in stride-one Outlook layers instead of Python ceil.
4. Dynamic roll through modular indices and index selection.
5. Identity convolution for the final 3×3 disparity-neighborhood extraction.

The source checkout remains unchanged. The export process patches only the
loaded upstream modules; it must run separately from native-reference runs.
Opset 18, dynamic height/width, RGB Float32 0..255 input. ONNX checker succeeds.
No custom CUDA, xformers, Col2Im or Im2Col operator is required. The graph is
approximately 62 MB and has roughly 30,000 nodes; session creation is substantial.
This is a feasible export, not yet an efficient production integration.

The initial export-operator/native synthetic comparison had max 0.00844 px error.
CPU ONNX versus original native at 416×128: max 0.00502 px, mean 0.000140 px,
p99 0.001021 px. At dynamic 448×160 versus the adapted native graph: max
0.00229 px, mean 0.000111 px, p99 0.000624 px. Both satisfy the explicit small-case
allclose tolerance atol 0.01/rtol 0.001. These are numerical substitution checks,
not measurements of stereo accuracy.

The committed export CLI was also run from scratch: native/streaming max 0 px,
native/export-ops max 0.00844 px, native/ONNX max 0.00502 px. Its second
448×160 random texture has max 0.00552 px/mean 0.000150 px/p99 0.001002 px;
the same explicit tolerances pass. This uses a different random texture than
the initial dynamic-shape probe above.

The committed photo-runner CLI was additionally executed with the reproduced
ONNX graph on a 416×128-per-eye synthetic SBS pair: both maps finite, scene saved
and all five requested CPU RVS views produced. Python compilation and Ruff's
F/E401 checks pass for the research scripts. No application code was changed.

## Full photograph and unchanged renderer

Private railing photograph: full SBS 2048×682, 1024×682 per eye, SHA-256
`67855bd0d131560195d945a9e336c3c271079e35ebb15c4b0fcac9407a8b6bb3`.
No resizing or cropping. Existing reversible matching offset 68 and symmetric
edge padding to multiples of 32; remove the offset after inference. Right maps
use the same swap/mirror convention as the application. Both maps are finite.

All models use the released CPU RVS, Precision 1, RGB Simple factor 5, unchanged
geometry/color handling. Five lossless probe views at 0/.25/.5/.75/1 and full
wiggles were rendered. AVIF comparisons: 1024×682, 60 frames/30 fps/2 s, 31 unique
sinusoidal positions with reused return views, quality 60/4:2:0/speed 6, infinite
loop. All three AVIFs were fully decoded and container loop flags checked.

Single-run CPU depth timings, excluding model load, RVS and file export:

| Model/runtime | Iterations | Left | Right | Both | Peak process RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| LAS2-H / released CPU ONNX | 4 | 3.44 s | 3.71 s | 7.15 s | 3039 MiB |
| IGEV++ Middlebury / released CPU ONNX | 16 | 25.25 s | 25.41 s | 50.66 s | 2901 MiB |
| GREAT-IGEV Middlebury / native CPU | 32 | 54.14 s | 53.77 s | 107.90 s | 5179 MiB |
| GREAT-IGEV Middlebury / CPU ONNX | 32 | 71.11 s | 62.31 s | 133.42 s | 6613 MiB |

GREAT ONNX session creation took 47.64 s. RSS includes the respective runtime,
weights and caches and is not a VRAM requirement. The different runtimes and
single runs limit performance conclusions. No claim about Windows GPU speed,
DirectML compatibility or 2160p memory use follows from these measurements.

Visual inspection: GREAT separates much of the railing from the background and
some areas look calmer than IGEV++ Middlebury; double contours/distortions remain.
LAS2-H misassigns several openings. There is no depth ground truth and one photo
does not establish a general quality winner. The private comparison archive
contains the three animations and identical-coordinate lossless railing crops.

Full-photo CPU ONNX versus streamed native reference:

| Eye | Mean error | p99 | Railing-band p99 | Pixels >1 px | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Left | 0.00406 px | 0.02001 px | 0.07614 px | 0.02835% | 61.75 px |
| Right | 0.00218 px | 0.00856 px | 0.02382 px | 0.01289% | 78.84 px |

Do not omit the outliers or call the graph pixel-identical. A separate native
export-operator run on the full left photograph versus the streamed reference
has mean 0.000789 px/p99 0.00641 px, but max 58.00 px and 0.00573% >1 px.
Thus sparse large differences already occur with the export substitutions;
additional numerical differences arise in ORT. The render is usable for study,
but the outliers need further inspection before a product parity claim.

## Reproduce without application changes

Use an isolated environment with the versions above. Clone the official source
at the pinned revision and obtain the exact official checkpoint explicitly.
The adapter checks revision, tracked source cleanliness and checkpoint hash.
No script downloads anything. Example from the repository root:

```sh
python tools/great_igev/export.py --source /path/to/GREAT-Stereo \
  --weights /path/to/great-igev-middlebury-submit.pth \
  --output /path/to/new-research.onnx
python tools/great_igev/compare_photo.py --source /path/to/GREAT-Stereo \
  --weights /path/to/great-igev-middlebury-submit.pth \
  --input /path/to/full-sbs.jpg --output /path/to/new-native-result \
  --rvs /path/to/wigglinde_rvs --offset 68
python tools/great_igev/compare_photo.py --onnx /path/to/new-research.onnx \
  --input /path/to/full-sbs.jpg --output /path/to/new-onnx-result \
  --rvs /path/to/wigglinde_rvs --offset 68
```

The supplied offset is explicit and photograph-specific. The scripts preserve
source resolution and originals. The photo runner uses Linux resource accounting.
No private image, derived picture, checkpoint or binary graph is committed.

Before a GUI test build: validate mixed precision and actual DirectML execution,
inspect sparse photo outliers, assess graph/session overhead and cancellation,
then add explicit provenance/model metadata and local-file discovery. No silent
fallback, dependency download or precision change is appropriate. No production
model integration or release replacement has been performed by this experiment.
