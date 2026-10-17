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
- Current milestone: portable test version (0.1 Test 3), LAS2-H (four iterations, float32), CPU/DirectML + RVS CPU.
  A passing packaged smoke test does not establish full real-photo quality,
  Windows 10/11 desktop validation, or parity with SplatTricia. Not a 1.0 release.
- Changes stay in this repository. Do not edit other Stereo-Tools repositories
  as a side effect. A change to the shared standard requires explicit coordination.
- Test geometry and output behavior with meaningful examples. Do not create
  slow, arbitrary acceptance gates or claim unrun tests have passed.
