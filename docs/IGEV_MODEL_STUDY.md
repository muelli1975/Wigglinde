# Internal model study: 18 October 2026

Christoph requests a 16/32-iteration Middlebury comparison, an assessment of the
LAS2 options, and internal comparisons with other useful IGEV models. This is
research on the existing test branch, not a change to the application defaults,
model menu, packaged ONNX graphs, or precision policy.

## Method

One supplied photograph, `bild054_cs.jpg`, SHA-256
`67855bd0d131560195d945a9e336c3c271079e35ebb15c4b0fcac9407a8b6bb3`.
Unchanged sRGB eye images, 1024 x 682 pixels each; no source upscaling/crop,
no extra smoothing, original signed matching offset 68, original replicate padding
to multiples of 32. Both disparity directions, second by horizontal reflection.
Same CPU RVS Precision 1 / Simple 5 at positions 0, .25, .5, .75, 1.
The diagnostic figure crops the displayed views/maps only; inference uses the
complete images. Disparity visualization uses a common clipped display range
of -40 to +5 pixels, rather than independent per-model normalization.

IGEV comparisons use original unmodified upstream PyTorch inference in Float32,
8 CPU threads, complete official checkpoints loaded strictly. The only model
construction override avoids downloading unrelated ImageNet weights before the
full stereo checkpoint is loaded. No ONNX operator substitutions in this study.
This isolates model/iteration behavior from export and GPU rounding differences.
LAS2 reference maps are the previously calculated CPU Float32 ONNX maps, with
native/export validation documented in the Test3/Test4 records.

No ground-truth disparity or third physical camera view exists for this photo.
Map agreement and prediction differences are diagnostics, not accuracy scores.
Five synthesized positions are a spatial check, not a full temporal benchmark.
CPU timings below are single observations, exclude load/render/export, and are
not Windows/DirectML performance claims. Small background jobs may cause noise;
the large 16/32 comparison was calculated sequentially in the same process.

## Middlebury 16 versus 32

IGEV++ source: `099dec97989780d151700459c682df1cc2c18e88`.
Official Middlebury checkpoint SHA-256:
`eecddfa4549dc6180ce96e7ed8bf24a0bb0d702d5e747623eac54abed1fd7579`.
Model settings: max disparity 768, original ranges 48/96/192 and intervals 1/2/4,
original context/correlation/GRU dimensions. Only iteration count changes.

| Iterations | Left | Right | Both eyes |
| --- | ---: | ---: | ---: |
| 16 | 19.463 s | 17.732 s | 37.195 s |
| 32 | 33.769 s | 32.291 s | 66.061 s |

32 is 1.776 times the observed depth time, not twice the complete application
runtime. The repeated native 16-iteration results exactly equal both previously
saved native Middlebury maps. Mean absolute 16/32 prediction differences are
0.180/0.158 px (left/right); 4.14/3.30 percent of pixels differ by more than 1 px.
These are differences, not measured errors. The changes concentrate around the
railing and ambiguous boundaries. The full middle view and the .25/.5/.75 railing
views show local changes, without a clear overall quality breakthrough. Remaining
artifacts are not eliminated. Do not change Test4's 16 iterations on this evidence.

The upstream demo defaults to 16, while upstream evaluation defaults to 32.
Neither is a universally mandatory iteration setting. A failure of 4-to-8 LAS2-H
to improve this photo does not predict IGEV's convergence behavior.

## Other official candidates

### IGEV++ ETH3D

Same IGEV++ source/configuration, 32 iterations, full RGB input as in upstream
inference. Official ETH3D checkpoint SHA-256:
`4595ac1c164b92e9b749907f09248c05abb6485e3121924b2d0bcd3eb3572e97`.
Left 32.902 s, right 31.647 s, both 64.549 s. Peak process RSS about 2872 MiB.
Good foreground-bar/background separation on this photograph, with local
behavior different from Middlebury; no established overall advantage yet.
Retain as an internal comparison candidate, not an automatic model replacement.

### RT-IGEV SceneFlow

Same upstream repository, its original `core_rt` model, evaluation-default
8 iterations, hidden dimension 96, max disparity 192. Official checkpoint SHA-256:
`7b7b6ac42d51dbc357a4f7fde3f9278c0da9d2128d1f09ce6c20fd3dcbaa9209`.
4,165,162 parameters. Left 3.442 s, right 3.519 s, both 6.961 s.
Peak process RSS about 1432 MiB. Fast, but the disparity maps again connect large
areas of the railing openings to the foreground. Does not meet the reason for
adding Middlebury here. No additional product option recommended from this test.

### Selective-IGEV Middlebury

Author repository `Windsrain/Selective-Stereo`, source revision
`c39acbfef9fbe36fbc01efa4abeafc62bbe2da36`, MIT notice (Xianqi Wang, 2024).
Official `middlebury_finetune.pth`, SHA-256
`ce019e97bbe8d806765cc9189399388393e400cbbf197bdece82acd4d9250798`.
The author README specifically recommends 80 iterations and max disparity 768
for Middlebury. Original architecture defaults, CPU Float32. Build-only missing
`opt_einsum` supplied locally as version 3.4.0; application has no new dependency.
Initial two-eye process terminated during second-eye inference with
`fatal library error, lookup self`; first-eye prediction completed in 94.931 s.
Separate-eye retries with 8 and 1 CPU threads also terminated with the same
message before a complete pair was produced. The cause is not established.
Do not label this an inherent model failure or infer its quality from it. There
is no complete Selective pair/render to compare, and no completed runtime claim
for 80 iterations. Keep it a research candidate, not a bundled model.

## Product recommendation from this limited study

Keep LAS2-H as the proven default with 720p; keep IGEV++ Middlebury as the
explicit alternative with a demonstrated benefit on this difficult photo.
Keep the CPU Float32 / GPU mixed policy; this native CPU study does not validate
physical DirectML execution for the new candidates or for a 32-iteration export.

S/M/L have different failure patterns, not a supported quality hierarchy on every
photograph. S/M are faster in previous depth-only CPU measurements, but no need
for a separate speed mode has been demonstrated for the intended product.
L's calmer railing can result from incorrectly assigning coherent foreground
depth to entire openings, consistent with Christoph's observations of errors and
a static-looking background. Different-looking results alone are insufficient
reason for three extra product choices. Recommend omitting S/M/L from the eventual
release unless a distinct repeatable benefit emerges on other photos. This is a
recommendation, not a removal implemented in the current five-model Test4.

## Primary sources

- https://github.com/gangweiX/IGEV-plusplus
- https://github.com/gangweiX/IGEV-plusplus/blob/099dec97989780d151700459c682df1cc2c18e88/demo_imgs.py
- https://github.com/gangweiX/IGEV-plusplus/blob/099dec97989780d151700459c682df1cc2c18e88/evaluate_stereo.py
- https://github.com/gangweiX/IGEV-plusplus/blob/099dec97989780d151700459c682df1cc2c18e88/evaluate_stereo_rt.py
- Official IGEV++/RT checkpoint folders linked from that author's README:
  https://drive.google.com/drive/folders/1eubNsu03MlhUfTtrbtN7bfAsl39s2ywJ
- https://github.com/Windsrain/Selective-Stereo
- Official Selective-IGEV checkpoint folder linked from that author's README:
  https://drive.google.com/drive/folders/1HwwGicI9f_WWOdjh3t5l6l4cn64zr_V5
