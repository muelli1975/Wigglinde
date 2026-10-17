# Source use and portable builds

Wigglinde uses Python 3.12. Install the application dependencies with
`python -m pip install -e .`; `wigglinde` launches the interface. The application
expects local prerequisites and never downloads them at startup:

- `models/las2/LAS2_H_dynamic.onnx` and matching JSON: Float32 CPU model.
- `models/las2/LAS2_H_mixed.onnx` and matching JSON: Windows GPU mixed-precision model.
- `backend/wigglinde_rvs.exe` and its OpenCV/OpenMP runtime libraries on Windows.
  Native source runs use `backend/wigglinde_rvs`; frozen Linux/macOS packages
  collect the native adapter and its runtime dependencies inside the bundle.
- Original icon and completion sound under `assets`.

## Models

[The Windows build workflow](.github/workflows/windows-test-build.yml) pins the
LAS2 source revision and weight hashes. `tools/export_las2.py` uses the author's
ONNX substitutions, exports dynamic image dimensions and compares the Float32
model with native inference on two small shapes. Cached Float32 exports are reused.

`tools/convert_las2_mixed.py` creates the GPU model using ONNX Runtime 1.24.4's
Float16 converter. It retains Float32 public inputs/output and selected sensitive
operations. The generated metadata records source/output hashes, conversion policy
and retained operation types. The build checks graph validity and small-shape
numerical differences. This is an ONNX mixed-precision policy, not an assertion
that it reproduces PyTorch/CUDA autocast operation for operation.

## Windows package

The workflow builds ONNX Runtime DirectML 1.24.4 from its pinned source with telemetry
compiled out. Do not replace this with overlapping CPU/DirectML Python distributions.
It builds the pinned MPEG-I RVS CPU adapter against OpenCV 4.10, runs source checks,
compares serial/parallel native outputs and tests the actual packaged executable.

`tools/package_windows.py` collects the application, both H models, local runtimes,
original assets, README files, license notices and exact tracked source. It creates
`dist/Wigglinde_1.0_Windows_x64.zip`, containing a stable `Wigglinde` application folder.
Settings, logs, temporary files, development outputs and external checkouts are excluded.

Publication uses the already verified workflow artifact and checks its SHA-256;
it does not rebuild the package. Tag/source identity and release-asset digest are
verified before reporting publication complete.

## Native Linux and macOS packages

[The native workflow](.github/workflows/unix-release-build.yml) builds Linux x64 on
Ubuntu 22.04 and separate Apple Silicon/Intel macOS packages on macOS 15. It reuses
the verified original Float32 H export; no model conversion or GPU provider is
needed. Official CPU ONNX Runtime is pinned to 1.24.4 on Linux/Apple Silicon and
1.23.2 on Intel macOS, for which 1.24.4 does not publish a wheel.

It builds pinned RVS against static OpenCV 4.10 (core/imgproc/photo/imgcodecs),
collecting native runtime dependencies with PyInstaller. OpenMP and independent
view concurrency remain available. macOS memory counters use psutil. Completion
sound uses afplay on macOS and paplay/aplay, when installed, on Linux. The icon is
converted from the supplied ICO for the macOS bundle; the original assets remain
included unchanged.

`tools/package_unix.py --label Linux_x64` (or `macOS_AppleSilicon` / `macOS_Intel`)
runs on the respective native host after building `build/rvs/wigglinde_rvs` and
preparing the pinned prerequisites from the workflow. It includes local models,
assets, license notices, exact tracked source and platform build information.
Linux archives use tar.gz to retain executable permissions; macOS uses ditto ZIPs
to retain framework links and ad-hoc signatures. The complete application folder
must stay together. Portable settings and logs live outside the signed .app.
The Mac apps are not Apple-notarized.

Before publication, the extracted archive runs the same packaged MP4/GIF/PNG,
optional depth-map, GUI, language and settings checks, plus the native
serial/parallel RVS comparison. The workflow appends only successful packages to
the existing 1.0 release. It preserves the Windows archive and tag; native package
source commits are recorded separately in build-info.json and release notes.

## Validation limits

The hosted Windows runner does not provide a suitable physical DirectML GPU.
A successful build, CPU model execution or software-adapter probe does not establish
GPU memory savings, speed, 2160p compatibility or photographic quality on every card.
CPU remains Float32. No silent device, model, resolution or precision fallback is used.

Research diagnostics and historical comparisons are kept in `docs`; they are not
extra acceptance gates in normal image-folder processing.
