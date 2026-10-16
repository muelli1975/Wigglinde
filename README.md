# Wigglinde

Wigglinde creates interpolated views and wiggle animations from already aligned
stereo SBS photographs, using Lite Any Stereo V2 (LAS2-M) and MPEG-I RVS.

The first portable Windows test version runs on the CPU, locally and offline.
It includes the model, renderer and runtime. Extract the complete folder and start
`Wigglinde.exe`. See [Liesmich.md](Liesmich.md) for German instructions.

- Individual files or folders, batch processing and cancellation.
- Full-SBS / Half-SBS input and explicit left/right swap.
- MP4: 720/1080/2160 maximum height, 30/60 fps, five cycles.
- GIF: 640/800/1024 maximum long side, 10/15/20/25 fps, infinite loop.
- PNG sequence: 1080/2160 maximum height, 30/60 fps, one cycle.
- Two-second sinusoidal cycle by default; reuse of views for return/repetition.
- No alignment, source crop, convergence adjustment or automatic quality reduction.
- ICC-managed RGB input, preserved aspect ratio, no upscaling of smaller inputs.

This is **0.1 Test 1**, not a 1.0 release. Windows 10/11 x64 is the target. CPU-only
rendering can take time at high resolution; memory use rises with size. LAS2-M has
a fixed 192-pixel correspondence range. Extreme disparities, occlusions, glass and
reflections remain limitations. GPU acceleration is not included yet.

Own source is MIT; third-party software and model weights retain their licenses.
See [third-party notices](tools/THIRD_PARTY.md). The portable package includes the
exact application source in `source` and license notices in `licenses`.

Development: `python -m pip install -e .`; `wigglinde` launches the GUI when the local
model under `models/las2` and renderer under `backend` are present. These components
are never downloaded by the application. Legacy geometry diagnostics remain
available through `python -m wigglinde --help`.

[Project scope](docs/PROJECT.md) · [RVS comparison](docs/RVS_COMPARISON.md) ·
[Development status](docs/DEVELOPMENT.md)
