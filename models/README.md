# Local LAS2 models — 1.1 Test 3

This test bundles LAS2-S/M/L/H. H is the default and retains the stable exports:

- `las2/LAS2_H_dynamic.onnx`: Float32 for CPU.
- `las2/LAS2_H_mixed.onnx`: mixed Float16/Float32 for GPU via DirectML.

S/M/L each use `LAS2_<size>_dynamic.onnx` for Float32 CPU and a separate
`LAS2_<size>_mixed.onnx` for mixed Float16/Float32 DirectML, just like H.
S/M/L use the same conversion operation policy; each has its own recorded numeric
comparison. S has larger deviations on ambiguous random textures; no equivalence
to Float32 or photographic quality gain is asserted.

Each has matching JSON metadata with its SHA-256 and source provenance. The selected
model and device determine the file; there is no automatic substitution, download,
account or external model-cache dependency is used.

- LAS2 source: `TomTomTommi/LiteAnyStereo`, revision `8c97bd4c4da3712c2ac60003a23201dfdb5935f4`.
- Weights: `tomtomtommi/LiteAnyStereoV2`, revision `17788d91618646fa781a14462e2926a034b9f49d`.
- Original H checkpoint SHA-256: `758585a25c3a332711f92a28ad1437e08080fb714ad1146de7cf2c01ce8479f4`.
- H: four fixed iterations; S/M/L: feed-forward (iteration metadata null).
- Maximum-disparity setting 192, Float32 RGB input 0–255 and Float32 disparity output.
- Symmetric edge padding to multiples of 32; temporary matching offset removed after inference.
- GPU conversion retains selected operations and their required parameters in Float32.
  This includes normalization parameters outside the representable Float16 range.
- Own application code, LAS2 code and published LAS2 weights use MIT; supplied notices apply.

See [BUILD.md](../BUILD.md) for reproducible exports and [THIRD_PARTY.md](../THIRD_PARTY.md)
for third-party components. Model binaries are distributed with the Windows release,
not committed as Git source files.

S/M/L checkpoint hashes are pinned in `tools/export_las2.py`; every export records
its matching weight hash and native/ONNX numerical validation. No H iter8 graphs
or OpenGL executable are part of Test 3.
