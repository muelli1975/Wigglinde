# DEFOM comparison for 1.2 Test 2 — 23 October 2026

Christoph authorizes Small/RVC and Large/Middlebury research, including the
Large model's CC-BY-NC-4.0 restriction. Separate branch `test-defom-1.2`, based on
stable main/v1.1 `9449c3359cc339ecd8c1978bab82eaca4c1cb9d8`. Previous GREAT/VWS
test branch/artifact retained; no public release or stable replacement.

## Native photo comparison

Private original Full-SBS railing photograph, SHA-256
`67855bd0d131560195d945a9e336c3c271079e35ebb15c4b0fcac9407a8b6bb3`,
1024×682 per eye, no resizing/crop/alignment. Existing signed offset 68 removed
after inference; original symmetric edge padding to 32. Both directions computed
by the same swapped/mirrored right-eye contract. Unchanged CPU RVS P1/RGB/Simple5,
positions 0/.25/.5/.75/1. Inputs, disparity arrays and rendered photographs stay
private, outside this repository and public CI.

Eight CPU threads; Linux container with eight CPU cores and 8 GiB memory limit.
Times are one measurement, not a benchmark average or Windows/RTX3060 estimate.
Peak resident memory includes imports/model load and inference. Reuse the saved
verified baseline scenes rather than recompute the unchanged H/IGEV estimators.
Baseline image arrays were compared with the original split before reuse.

| Model/backend | Both disparity maps | Model load | Peak RSS |
| --- | ---: | ---: | ---: |
| LAS2-H, existing ONNX FP32 | 7.2 s | 1.0 s | 3.0 GiB |
| IGEV++ Middlebury, existing ONNX FP32 | 50.7 s | 7.1 s | 2.8 GiB |
| DEFOM-S/RVC, native PyTorch FP32 | 64.0 s | 0.6 s | 3.0 GiB |
| DEFOM-L/Middlebury, native PyTorch FP32 | 114.0 s | 3.8 s | 4.8 GiB |
| DEFOM-S/RVC, ONNX FP32 | 58.0 s | 9.7 s | 2.7 GiB |
| DEFOM-L/Middlebury, ONNX FP32 | 109.2 s | 13.0 s | 5.6 GiB |

Official checkpoint sizes: Small 173,496,207 bytes, Large 1,530,895,934 bytes.
Total parameters: Small 43,290,177 (18,505,088 trainable), Large 382,619,745
(47,304,096 trainable). Trainable counts alone omit the frozen depth backbone.

Visual assessment of the original native depth maps and rendered railing crops:
both DEFOM variants distinguish substantially more openings than H on this
photograph. Small and IGEV++ both retain useful thin structures, with different
local errors. Large has individual cleaner transitions/openings but also errors;
neither a universally superior model nor a flawless grid reconstruction is
established. This modest, photograph-specific signal justifies a separate user
test, not changing the H default. Assess the full movement on further photographs.
No ground-truth disparity or withheld target photograph exists for this input.

## Faithful export, numerical limits

Pinned official revision and hashes: [research tool](../tools/defom/README.md).
Complete official checkpoints loaded strictly, no missing/unexpected keys.
Original 32 updates with 8 scale updates, original correlation and DA2 size cap.
No training, pruning or changes to intended reductions. Native PyTorch uses the
upstream attention implementation provided when optional xFormers is absent.

Export-only adaptations address Python/numpy size calculation and Python-float
positional scales, which otherwise freeze image size during tracing. The ONNX
graph preserves the original dynamic dimensions, 2688 DA2 cap, bicubic offset and
equivalent single-channel unfold. Size formulas checked in both orientations,
including the original cap. Native adapter output was identical on 416×128 and
448×160 cases. ONNX FP32 errors on those cases: Small maximum 0.000615 px; Large
maximum 0.00210 px. Full-size photo and RVS views also run, not only small tensors.

Full-photo native/ONNX FP32 mean differences: Small 0.032–0.040 px, Large
0.020–0.029 px. 99% quantiles: Small 0.70–0.89 px, Large 0.40–0.53 px;
individual ambiguous pixels differ up to 21.44 px. Railing-band 99% quantiles:
Small 1.86–2.18 px, Large 1.00–1.35 px. Rendered details retained in visual checks;
this is not a claim of photographic numerical equality.

Mixed graphs retain FP32 correspondence, normalization, distributions and
resampling, with FP16 suitable convolutions/transformer operations. Large's
feature decoder was measured to exceed FP16's finite range, causing Inf/NaN.
Its complete decoder path, transport and fusion convolution through normalization
are therefore a fixed FP32 island in the corrected mixed graph. No runtime
fallback or clipping of those activations. Mixed checks execute on CPU and do
not establish physical DirectML behavior or GPU memory savings.

## Runtime and scope

DEFOM runs in a spawned ONNX worker. This contains native model/provider failures
and keeps GIL-blocking model initialization outside the GUI process, based on
Christoph's GREAT startup hangs/crash. Cancellation kills the active worker;
one session is reused within a batch. Native child errors preserve diagnostic
details; fatal exits are reported. Local model hashing streams bytes to avoid
allocating another entire Large model in memory. H/IGEV inference and RVS math
remain unchanged. Worker memory/GPU counters are identified separately as
worker-lifetime measurements; they are not the parent GUI's GPU usage.

Only four explicit models, default H; single RVS renderer. No GREAT, VWS,
OpenGL, iteration selector or lenticular functions. Same formats, resolutions,
per-format settings and 720p/CPU defaults. Separate test settings. Large's model
selector and packaged notices visibly retain `(CC-BY-NC-4.0)`.

Packaged Windows checks and actual artifact hashes are recorded after the build.
No physical Windows GPU is available in the local research environment.
