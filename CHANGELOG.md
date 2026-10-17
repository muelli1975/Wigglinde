# Changelog

## 1.0

- Portable Windows Full-SBS to MP4, GIF and PNG-sequence conversion.
- LAS2-H depth estimation on CPU or DirectML; parallel MPEG-I RVS CPU rendering.
- Precision 1, RGB, Multispectral 1/4; normalized sRGB input without extra gamma conversions.
- Default MP4 output: 720p, 30 fps, two-second cycle; CPU selected on first launch.
- Optional jointly normalized left/right 16-bit PNG depth maps with scale metadata.
- Separate `wiggle` and `depth_maps` output folders; relative source paths encoded in filenames.
- German/English interface, batch processing, cancellation, icon and completion sound.
- Bounded rotating logs and depth-only diagnostics.
