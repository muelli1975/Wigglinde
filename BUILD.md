# Isolated 1.2 Test 1

The `test-great-vws-1.2` branch builds a Windows Actions artifact through
`.github/workflows/great-vws-test-build.yml`. It never calls a publication job.
The GREAT model job builds and checks pinned Float32/mixed graphs; the Windows
job reuses the unchanged LAS2-H/Middlebury graphs and no-telemetry DirectML wheel.
PyTorch/timm and the GREAT source are build-only Linux dependencies.

TMIV/VWS is built from unchanged commit
`8faacbe722f0e2fc1dc6f8247eb2da166a0297c6` with fmt
`0c9fce2ffefecfdce794e1859584e25877b7b592`; only renderer-related libraries are
enabled. No geometry/chroma patches, codecs or GPU renderer are added. VWS
parallelism uses separate original processes and the native `-j` option, bounded
by CPU/RAM. `tools/vws/check_native.py` verifies geometry, exact serial/parallel
image equality and cleanup of all processes on cancellation.

The Windows packaging call additionally requires `--tmiv tmiv-reference` and
`--fmt fmt-reference`. The actual packaged EXE checks all three estimators with both
renderers, all output formats, persisted options and bilingual GUI geometry at
100/125/150% scaling, including 780×600 minimum size. Notices and provenance are
included. Physical DirectML availability is recorded separately from CPU graph
verification. See `TESTVERSION.md` for the user-facing test scope.

The following instructions document the retained 1.1 build.

# Building Wigglinde 1.1

Use Python 3.12 and `python -m pip install -e .`; `wigglinde` launches the GUI.
Application startup and processing never download models or dependencies.

## Local prerequisites

- `models/las2/LAS2_H_dynamic.onnx` and matching JSON: CPU Float32.
- `models/igev/IGEV_Middlebury_dynamic.onnx` and matching JSON: CPU Float32.
- Windows also includes corresponding `_mixed.onnx` files and JSON for DirectML.
- CPU RVS adapter under `backend`, its native runtimes, and original `assets`.

Model hashes and source/checkpoint revisions are recorded in the JSON beside each
ONNX file. The release reuses the unchanged verified H graphs from Actions run
39041230523 and Middlebury graphs from run 39124980286. Windows also reuses the
telemetry-free DirectML 1.24.4 runtime from run 39041230523.

## Model export

`tools/export_las2.py` exports pinned LAS2-H using the author's ONNX substitutions;
`tools/convert_las2_mixed.py` creates the FP16/FP32 graph. Middlebury export uses
`tools/igev/export.py`, `verify.py` and `convert_mixed.py`, pinned IGEV++ source
099dec97989780d151700459c682df1cc2c18e88, the official Middlebury checkpoint,
all 16 iterations and max disparity 768. Build-only dependencies are CPU
PyTorch 2.6.0, torchvision 0.21.0, isolated timm 0.5.4, scipy, ONNX 1.17.0 and
ONNX Runtime 1.24.4. No PyTorch, timm or CUDA installation is required by users.
The ONNX mixed policy retains selected sensitive operations in Float32; it is
not claimed identical to CUDA autocast. Export and photograph comparisons are
recorded in [development notes](docs/DEVELOPMENT.md).

## Portable packages

[Release workflow](.github/workflows/release-build.yml) builds Windows x64 and calls
[the native workflow](.github/workflows/unix-release-build.yml) for Linux x64,
macOS Apple Silicon and macOS Intel. Native CPU ONNX Runtime is pinned to 1.24.4
except Intel macOS (1.23.2, the available wheel). RVS and OpenCV sources are pinned;
Linux/macOS build a minimal static OpenCV, collecting native dependencies.

Windows: `tools/package_windows.py --opencv opencv-sdk/opencv --rvs rvs-reference
--las2 las2-reference --igev igev-reference` after building `build/rvs/Release`.
Native: `tools/package_unix.py --label Linux_x64` (or the matching macOS label)
after preparing the sources and building `build/rvs/wigglinde_rvs` as in the workflow.
All packages contain exact tracked project source, model provenance and applicable
third-party notices. External checkouts, logs, settings and test output are excluded.
Keep the complete application folder together. macOS apps are ad-hoc signed,
not notarized; Linux tar.gz retains executable permissions and macOS ditto ZIPs
retain framework links/signatures. Portable data stays outside the signed app.

The actual packaged application runs MP4/GIF/PNG, both CPU estimators, model-separated
output names, depth metadata, session reuse, language/settings and GUI checks.
Native packages are extracted before this check. Serial/parallel RVS output is
compared separately. These are development checks, never per-photo startup gates.

[Publication workflow](.github/workflows/publish-1.1.yml) waits for all four packages,
checks reports, commit identity, model set and archive SHA-256, uploads into a draft
v1.1 release, verifies uploaded digests, then publishes. It never changes v1.0.

## Validation limits

Hosted build runners do not establish physical GPU speed or memory limits.
Christoph reports successful Middlebury 2160p processing on RTX 3060 12 GB with the
same mixed graph in Test4. This is one practical hardware result, not a guarantee
for every image or graphics adapter. No silent device/model/resolution fallback.
