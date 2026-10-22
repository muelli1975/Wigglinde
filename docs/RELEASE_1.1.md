## Animation export update — 22 October 2026

- Add animated **WebP**, fixed quality **85**, without a quality selector or lossless option.
- Add animated **AVIF**, fixed quality **60**, **4:4:4**, encoder speed **6**.
- Both formats offer maximum image heights **720/1080/2160 pixels** and **30/60 fps**, preserve the aspect ratio and never enlarge smaller images. Default: **720p/30 fps**.
- One complete pendulum cycle repeats indefinitely; existing motion and cycle duration are retained.
- Existing GIF, MP4 and PNG-sequence encoding, stereo processing and application defaults are unchanged. The version remains **1.1**.

Wigglinde creates wiggle animations from already aligned Full-SBS stereo photographs.

New in 1.1:

- Choose **LAS2-H** (established default, four fixed iterations) or **IGEV++ Middlebury** (sixteen fixed iterations), a slower alternative for difficult structures such as railings. Results depend on the photograph.
- Both models use Float32 on CPU and mixed Float16/Float32 through DirectML on Windows GPUs. Linux/macOS include both CPU models.
- Fixed `las2-h` / `igev-middlebury` suffixes distinguish MP4, GIF, WebP, AVIF, PNG-sequence and depth-map outputs.
- Depth-map JSON also records model, iteration count, precision and processing device.
- Saved model selection; depth-test results identify the actual selected model.

The established CPU RVS renderer (Precision 1, Simple blending factor 5), image geometry, animation timing and MP4/GIF/PNG settings are retained. First-launch defaults remain LAS2-H, MP4, 720p, 30 fps, two-second cycle and CPU. No renderer or iteration selector.

**Portable, local and offline.** Extract the complete matching package and keep its `Wigglinde` folder together. No separate Python, PyTorch, timm or CUDA installation is required.

- Windows 10/11 x64: start `Wigglinde.exe`; compatible GPUs use DirectML for depth estimation.
- Linux x64, Ubuntu 22.04 or newer: start `Wigglinde`; CPU processing.
- macOS 15 or newer: separate Apple Silicon/Intel packages; open `Wigglinde.app`; CPU processing. Apps are ad-hoc signed, without Apple notarization.

Each package passes source checks, CPU RVS serial/parallel comparison and actual packaged application checks for both models, MP4/GIF/PNG/WebP/AVIF, depth metadata, distinct model filenames, GUI and settings. Physical GPU execution is not established by hosted runners. The same Middlebury mixed graph completed 2160p processing on Christoph's RTX 3060 12 GB in practical testing; other images/cards can need more memory. Fine structures, occlusions, glass and reflections can still produce artifacts.

Matching project source, German/English instructions, model provenance and third-party license notices are included. Original Wigglinde code is MIT; bundled components and model weights retain their applicable terms. See `THIRD_PARTY.md`.
