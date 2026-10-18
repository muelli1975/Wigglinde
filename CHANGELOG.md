# 1.1 Test 3 (experimental)

- Replace the OpenGL/iteration experiment with explicit LAS2-S/M/L/H selection.
- Keep H as default, four fixed iterations, unchanged H precision and CPU RVS Simple 5.
- S/M/L retain Float32 on CPU and DirectML; save model choice between runs.
- Remove GL backend/dependencies and iteration-8 graphs from this test package.

# Changelog


## 1.0 — updated build, 2026-10-17

- Use native RVS Simple blending with factor 5 after practical image comparisons.
- Keep the reduced 1.0 interface, without experimental blending controls.
- Retain LAS2-H, four iterations, CPU/GPU model precision, resolution and exports.
- Rebuild all existing platform packages with the same fixed blending standard.

## 1.0

- Portable Windows Full-SBS to MP4, GIF and PNG-sequence conversion.
- LAS2-H depth estimation: Float32 on CPU, mixed Float16/Float32 on DirectML GPU.
- Parallel MPEG-I RVS CPU rendering.
- Precision 1, RGB, Multispectral 1/4; normalized sRGB input without extra gamma conversions.
- Default MP4 output: 720p, 30 fps, two-second cycle; CPU selected on first launch.
- Optional jointly normalized left/right 16-bit PNG depth maps with scale metadata.
- Separate `wiggle` and `depth_maps` output folders; direct folder images only, without recursion.
- Precision-1 memory scheduling.
- Remembered input/output paths, language, device, depth-map option and animation settings.
- German/English interface, batch processing, cancellation, icon and completion sound.
- Bounded rotating logs and depth-only diagnostics.
