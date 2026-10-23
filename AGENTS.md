# Repository guidance

Read `DESIGN_STANDARD_STEREOTOOLS.txt` before GUI, labels, interaction, output-path,
or asset changes. The file is an unchanged reference from SplatTricia; its explicit
rules for other projects do not become Wigglinde features. Read `docs/PROJECT.md`
for this project's agreed scope and `docs/DEVELOPMENT.md` for its actual status.

- The user is Christoph. Product language is German, with English support.
- Build a restrained converter, with the established Stereo-Tools colors and
  SplatTricia interaction conventions. Do not invent controls or alter stereo
  mathematics or defaults without discussing meaningful changes.
- Quality and resolution must not be lowered automatically. Do not silently
  switch devices, replace an estimator, crop source images, or make model downloads.
- The application must run locally and offline after setup. Keep required models
  under `models`; report missing local files clearly. No accounts or telemetry.
- Preserve originals. Record transforms and inference settings in diagnostic output.
- Input pairs are already aligned. No automatic/manual alignment, source crop,
  or convergence/window change. Remove temporary matching offsets after inference.
- The converter assumes Full-SBS with normal-width eye images, like the other
  Stereo-Tools. No Half-SBS selector or format auto-detection was agreed.
- Input order is fixed: left view on the left, right view on the right. No L/R swap.
- Normal PCs remain a target. Measure CPU time and RAM; never hide resource limits
  by silently lowering resolution, quality, or model precision.
- Keep expensive geometry verification and full output-decode checks in explicit
  development tests, outside normal batch processing. Reuse model sessions and
  computed views; do not rerender repeated animation cycles or the return path.
- Use established stereo correspondence, visibility, and view-synthesis methods.
  Keep research diagnostics separate from product input validation. Do not add
  speculative checks that reject otherwise usable photographs.
- Code, model weights and runtime dependencies can have different licenses.
  Retain the exact notices applicable to each distributed component. Never copy
  the research-only FoundationStereo source into the application.
- User-authorized 1.0 rebuild (17 October 2026): fixed native Simple factor 5,
  no blending controls. Rebuild all four released platforms. Retain the separate
  experimental 1.1 Test 1 branch; do not merge its options into 1.0.
- Current milestone: version 1.0, LAS2-H (four iterations; CPU Float32, GPU mixed Float16/Float32), CPU/DirectML + RVS CPU.
  Precision 1, RGB, Simple 5, normalized encoded sRGB without extra gamma
  conversions. Default MP4 720p / CPU. Optional jointly normalized 16-bit depth maps.
  Output folders wiggle/depth_maps. Folder input processes direct images only,
  no subfolders or folder prefixes in filenames. Precision-1 memory estimates;
  existing temporary/final PNG compression retained. Persist language, device,
  last input paths, output mode/folder, depth option and animation settings,
  matching SplatTricia without automatically starting processing.
  Lenticular options remain postponed.
  A passing packaged smoke test does not establish full real-photo quality,
  Windows 10/11 desktop validation, or parity with SplatTricia.
- Changes stay in this repository. Do not edit other Stereo-Tools repositories
  as a side effect. A change to the shared standard requires explicit coordination.
- Test geometry and output behavior with meaningful examples. Do not create
  slow, arbitrary acceptance gates or claim unrun tests have passed.

## Authorized 1.1 Test 3 experiment (18 October 2026)

Christoph requests removing OpenGL and the iteration selector from the test build,
cleaning their code/dependencies/models, and comparing LAS2 variants. Work on
`test-models-1.1`; retain stable main/v1.0 and the historical test branches.
Explicit S/M/L/H model menu, default H. H has four fixed iterations and its
existing CPU FP32 / DirectML mixed policy. S/M/L use the same explicit CPU FP32 /
DirectML mixed policy at Christoph's request. Numerical differences are recorded;
S exceeds the H small-shape comparison tolerance and is not claimed equivalent.
Unchanged CPU RVS Precision 1 Simple 5 and geometry/export behavior. No GL backend
or eight-iteration graphs in this package. Separately investigate IGEV++ quality,
code/weight licenses, CPU/ONNX/DirectML; do not bundle an unverified integration.

## Authorized 1.1 Test 4: IGEV++ Middlebury

Christoph requests integrating official Middlebury and assessing requirements.
Work on test-igev-middlebury-1.1. Add it to existing model menu, preserve H default
and LAS2 graphs. Fixed16 iterations and maxdisp768; CPU Float32, GPU mixed, CPU RVS.
No torch/timm/CUDA runtime dependency, no automatic download/fallback. Preserve
shared ONNX transport math and signed offsets. Verify native/operator/ONNX parity,
small widths, real-photo render, mixed graph, cancellation and actual Windows EXE.
Use official MIT project notice for the official linked checkpoint, recording
that this is the project-license reading and no separate weight statement exists.
Include provenance and relevant notices; do not invent a new permission gate.

## Authorized final 1.1 (18 October 2026)

Christoph requests finishing and releasing 1.1 after practical testing. Only
LAS2-H (default, 4 iterations) and IGEV++ Middlebury (16 iterations). No S/M/L,
ETH3D or Selective/RT variants in the package. Preserve CPU Float32 / Windows
DirectML mixed, CPU RVS P1/Simple5, geometry and all export settings. Fixed model
suffixes las2-h / igev-middlebury on animations, sequences and depth maps; include
model/iterations/precision/device in depth JSON. Preserve bilingual GUI layout.
User reports successful Middlebury 2160p processing on RTX 3060 12 GB; record as
one real-hardware success, not a universal memory guarantee. Finish the existing
four platform packages and release v1.1; do not overwrite historical v1.0.

## Authorized 1.2 Test 1: GREAT-IGEV and TMIV/VWS (23 October 2026)

Christoph requests a separate portable Windows test package to compare GREAT-IGEV
and VWS personally. Work on `test-great-vws-1.2`; preserve main, v1.1, releases
and the research branch. Retain LAS2-H and IGEV++ Middlebury, default LAS2-H and
CPU RVS P1/Simple5. Add explicit GREAT-IGEV Middlebury (32 iterations, maxdisp768,
CPU FP32 / DirectML mixed) and independent RVS/VWS renderer selection. VWS uses
unchanged official TMIV source and best-reference defaults, including its 10-bit
geometry and YUV420 transport. Christoph explicitly requests using the intended
original functions first; modifications require an evidenced need. No torch/timm/CUDA runtime. Keep
geometry, export formats/options and per-format settings. Distinct test version,
archive and settings file; renderer suffix on animation outputs to compare without
overwriting. Bilingual restrained GUI; inspect 100/125/150% and minimum size.
Build an Actions artifact, not a public prerelease or stable replacement.
Evaluate quality before a possible 1.2; lenticular work follows afterwards.
