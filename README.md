# Wigglinde

Wigglinde creates wiggle animations from already aligned Full-SBS stereo photographs,
using Lite Any Stereo V2 (LAS2-H) and MPEG-I RVS.

**Version 1.0 · Windows 10/11 x64 · portable.** Extract the complete folder and start
`Wigglinde.exe`. Model, renderer, runtimes, icon and completion sound are included.
Processing works locally and offline, without accounts, telemetry or automatic downloads.
German instructions: [Liesmich.md](Liesmich.md).

- German/English interface, single-image or image-folder processing, no file list. Image folders are processed without subfolders.
- Default: **MP4, 720p, 30 fps, two-second cycle, CPU**.
- LAS2-H, four iterations, float32. CPU or compatible NVIDIA/AMD/Intel GPU via DirectML.
- RVS CPU renderer: Precision 1, RGB, Multispectral 1/4. Intermediate views run
  concurrently within CPU and available-memory limits estimated for Precision 1; return views and repeated cycles are reused.
- Full-SBS only: normal-width left half followed by the right half. No alignment,
  L/R swap, source crop or convergence adjustment.
- ICC-managed RGB input, Lanczos scaling before depth estimation, preserved aspect
  ratio and no upscaling of smaller inputs. Opaque 8-bit RGB/grayscale images.
- Optional left/right depth maps as **16-bit grayscale PNG**, disabled by default.
- Cancellation, separate input/output dialog memories and completion sound.
- Language, device, last input paths, output mode/folder, depth-map option and
  animation settings are remembered; processing never starts automatically.

| Format | Maximum size | Frame rate | Playback |
| --- | --- | --- | --- |
| MP4 | 720 / 1080 / 2160 px height | 30 / 60 fps | Five cycles |
| GIF | 640 / 800 / 1024 px long side | 10 / 15 / 20 / 25 fps | Infinite loop |
| PNG sequence | 1080 / 2160 px height | 30 / 60 fps | One cycle |

Cycle duration: 0.5–30 seconds; sinusoidal motion without a duplicated final endpoint.
MP4 uses H.264 CRF 18/slow; GIF uses one common palette. Odd MP4 dimensions are
padded by at most one black pixel row/column, without cropping.

## Output

Default destination: `output` in the input folder; a custom destination is optional.
Animations are stored under `wiggle`, optional depth maps under `depth_maps`.
Only images directly inside the selected input folder are processed; subfolders are
ignored. Output filenames retain the original stem, without source-folder prefixes,
e.g. `Image_wiggle_30fps_720p.mp4`. Suffixes are lowercase.
PNG sequences have their own `_png` folder. Existing animation outputs are replaced
only after successful export. Originals remain unchanged.

Depth maps use the selected processing size, one map for each corresponding SBS
half. Both maps share a linear normalization: white is near, black is far.
They contain **relative disparity, not distance in metres**. A JSON companion records
the shared minimum/maximum, map names and decoding formula. Use a map with its
matching, equally scaled left/right RGB half. No depth-only export or lenticular
print preparation is included.

## Devices and diagnostics

CPU is selected on first launch; a saved device choice is retained. DirectML requires
a compatible DirectX 12 driver. Individual unsupported ONNX operators may execute on
CPU within the DirectML session. A failed GPU initialization is reported; the whole
job never silently switches device, model, precision or resolution.
**RVS rendering uses CPU in both modes.** High resolutions require more time and memory.

**Test depth estimation** runs the same preprocessing and both depth calculations for
a selected single image, without rendering or writing maps. Choose the resolution first.
`logs/latest_run.json` is overwritten each run and records stage times, render scheduling,
sampled RAM/commit and available DXGI process GPU usage/budget. `wigglinde.jsonl` and
`errors.log` rotate at 5 MiB with three backups each. Temporary PNG compression is unchanged. Temporary files are removed after processing; an empty `_temp` parent is removed as well.

Extreme disparities, occlusions, glass, reflections and fine structures can cause
transition artifacts or doubled contours. No artifact-free result is guaranteed.

Own code is MIT; third-party code, model weights and runtime components retain their
licenses. See [third-party notices](tools/THIRD_PARTY.md). The package contains the exact
application source in `source` and notices in `licenses`.

Development: `python -m pip install -e .`; `wigglinde` launches the GUI with the local
model under `models/las2` and renderer under `backend`. Do not install overlapping
ONNX Runtime distributions. [Development status](docs/DEVELOPMENT.md).
