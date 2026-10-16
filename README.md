# Wigglinde

Wigglinde creates interpolated views and wiggle animations from already aligned
stereo SBS photographs, using Lite Any Stereo V2 (LAS2-M) and MPEG-I RVS.

**0.1 Test 2** is a portable Windows test version. Extract the complete folder and
start `Wigglinde.exe`. The model, renderer, runtimes and completion sound are included;
processing works locally and offline. See [Liesmich.md](Liesmich.md) for German instructions.

- German/English interface with single-image and image-folder path fields.
- Batch processing, preserved subfolders and cancellation; no file list.
- Explicit CPU or GPU selection for LAS2 depth estimation. DirectML supports
  compatible NVIDIA, AMD and Intel adapters; a DirectX 12 driver is required.
- RVS retains the tested **CPU, Precision 2, Multispectral 1/4** renderer in both modes.
- Full-SBS / Half-SBS input and explicit left/right swap.
- MP4: 720/1080/2160 maximum height, 30/60 fps, five cycles.
- GIF: 640/800/1024 maximum long side, 10/15/20/25 fps, infinite loop.
- PNG sequence: 1080/2160 maximum height, 30/60 fps, one cycle.
- Two-second sinusoidal cycle by default; reuse of views for return/repetition.
- No alignment, source crop, convergence adjustment or automatic quality reduction.
- ICC-managed RGB input, preserved aspect ratio, no upscaling of smaller inputs.

Select a graphics adapter under **Depth estimation** to try DirectML. CPU remains
the default on first launch. Unsupported individual ONNX operators may execute on
CPU as part of DirectML graph partitioning. Failure to initialize the chosen GPU is
reported; the application does not silently switch the whole job to CPU. There is
no automatic model, precision or resolution reduction.

This is a test version, not a 1.0 release. Windows 10/11 x64 is the target. GPU speed
and quality require testing on physical graphics cards; a hosted Windows build test
cannot establish those. RVS rendering still takes CPU time at high resolution.
LAS2-M has a fixed 192-pixel correspondence range. Extreme disparities, occlusions,
glass and reflections remain limitations. Fine branches can appear doubled during
the animation; that reported quality issue is still under investigation. No icon has been supplied yet.

Own source is MIT; third-party software and model weights retain their licenses.
See [third-party notices](tools/THIRD_PARTY.md). The portable package includes the
exact application source in `source` and license notices in `licenses`.

Development: `python -m pip install -e .`; `wigglinde` launches the GUI when the local
model under `models/las2` and renderer under `backend` are present. These components
are never downloaded by the application. Windows uses ONNX Runtime DirectML (including
its CPU provider); other systems use the CPU runtime. Do not install overlapping
ONNX Runtime distributions in the same environment. Legacy geometry diagnostics
remain available through `python -m wigglinde --help`.

[Project scope](docs/PROJECT.md) · [RVS comparison](docs/RVS_COMPARISON.md) ·
[Development status](docs/DEVELOPMENT.md)
