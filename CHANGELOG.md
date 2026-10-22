# Changelog

## 1.1 — export update, 2026-10-22

- Add animated WebP at fixed quality 85 and animated AVIF at fixed quality 60, 4:4:4, speed 6.
- Both new formats: 720/1080/2160 maximum image height, 30/60 fps, default 720p/30 fps, infinite looping and no upscaling.
- Preserve existing GIF/MP4/PNG outputs, model/renderer settings and version number.

## 1.1 — 2026-10-18

- Add IGEV++ Middlebury with sixteen fixed iterations as an alternative to LAS2-H.
- Keep LAS2-H as default, with four iterations and 720p on first launch.
- CPU Float32 and Windows DirectML mixed Float16/Float32 for both models.
- Include both CPU models on Linux and macOS; preserve CPU RVS Precision 1 / Simple 5.
- Fixed `las2-h` / `igev-middlebury` suffixes distinguish all animation and depth outputs.
- Add model, iterations, precision and device to depth-map scale metadata.
- Save model selection and show the actual model in the bilingual depth-test result.
- No experimental renderer, iteration selector or LAS2-S/M/L choices in this release.


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
