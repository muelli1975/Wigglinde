# Changelog


## 1.1 Test 1 — separate Windows test build, 2026-10-17

- Select native RVS Multispectral or Simple blending.
- Edit Areas/Details or Weight; retain 1/4 and 5 as initial factors.
- Reset factors, preserve settings, and log actual native parameters.
- Fixed control geometry, German/English labels and inactive-field states.
- Keep LAS2-H at four iterations, Precision 1, RGB and existing CPU/GPU models.
- Stable version 1.0 remains unchanged. No grid-quality improvement is claimed.

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
