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

## Authorized 1.1 Test 2 experiment (18 October 2026)

On the separate test-opengl-iterations-1.1 branch, Christoph requested an OpenGL
test build with selectable four/eight LAS2-H iterations. CPU/OpenGL selection
provides an explicit comparison; test defaults OpenGL/four. Same H weights and
precision policy; eight uses separate verified ONNX exports. Retain Simple 5.
Do not update main, v1.0, or stable release assets. The older blending test branch
remains separate. OpenGL adapter is driver-selected and recorded independently
of the DirectML depth device. No automatic renderer fallback.
