# Source use and portable builds

Wigglinde uses Python 3.12. Install the application dependencies with
`python -m pip install -e .`; `wigglinde` launches the interface. The application
expects local prerequisites and never downloads them at startup:

- `models/las2/LAS2_H_dynamic.onnx` and matching JSON: Float32 CPU model.
- `models/las2/LAS2_H_mixed.onnx` and matching JSON: GPU mixed-precision model.
- `backend/wigglinde_rvs.exe` and its OpenCV/OpenMP runtime libraries on Windows.
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
`dist/Wigglinde_1.0_Windows.zip`, containing a stable `Wigglinde` application folder.
Settings, logs, temporary files, development outputs and external checkouts are excluded.

Publication uses the already verified workflow artifact and checks its SHA-256;
it does not rebuild the package. Tag/source identity and release-asset digest are
verified before reporting publication complete.

## Other platforms

The current released and packaged target is Windows x64. Native CPU packages for
Linux x64, macOS Apple Silicon and macOS Intel are feasible, following the separate
native-build approach used by Freeda. These are not yet built or validated for
Wigglinde, and no Linux/macOS download is currently provided.

The Python dependencies already select CPU ONNX Runtime outside Windows; the
Float32 H model can be reused. The C++ RVS adapter and application bundle must be
built for each target. Before releasing these packages, adapt the Apple linker
options, platform sound playback, macOS memory counters and packaging of local
models, libraries and assets, then check the actual native applications. DirectML
is Windows-specific; another GPU backend would require separate integration and
validation. It is not enabled merely by building on another operating system.

## Validation limits

The hosted Windows runner does not provide a suitable physical DirectML GPU.
A successful build, CPU model execution or software-adapter probe does not establish
GPU memory savings, speed, 2160p compatibility or photographic quality on every card.
CPU remains Float32. No silent device, model, resolution or precision fallback is used.

Research diagnostics and historical comparisons are kept in `docs`; they are not
extra acceptance gates in normal image-folder processing.
