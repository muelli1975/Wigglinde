# Local LAS2-H models

Wigglinde 1.0 bundles two computational versions of the same LAS2-H model:

- `las2/LAS2_H_dynamic.onnx`: Float32 for CPU.
- `las2/LAS2_H_mixed.onnx`: mixed Float16/Float32 for GPU via DirectML.

Each has matching JSON metadata with its SHA-256 and source provenance. The selected
device determines the file; no model-size selector, automatic substitution, download,
account or external model-cache dependency is used.

- LAS2 source: `TomTomTommi/LiteAnyStereo`, revision `8c97bd4c4da3712c2ac60003a23201dfdb5935f4`.
- Weights: `tomtomtommi/LiteAnyStereoV2`, revision `17788d91618646fa781a14462e2926a034b9f49d`.
- Original H checkpoint SHA-256: `758585a25c3a332711f92a28ad1437e08080fb714ad1146de7cf2c01ce8479f4`.
- Four iterations, maximum-disparity setting 192, Float32 RGB input 0–255 and Float32 disparity output.
- Symmetric edge padding to multiples of 32; temporary matching offset removed after inference.
- GPU conversion retains selected operations and their required parameters in Float32.
  This includes normalization parameters outside the representable Float16 range.
- Own application code, LAS2 code and published H weights use MIT; supplied notices apply.

See [BUILD.md](../BUILD.md) for reproducible exports and [THIRD_PARTY.md](../THIRD_PARTY.md)
for third-party components. Model binaries are distributed with the Windows release,
not committed as Git source files.
