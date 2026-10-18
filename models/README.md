# Wigglinde 1.1 models

Only LAS2-H and IGEV++ Middlebury are bundled. Windows has four graphs (CPU and
mixed for each model); native Linux/macOS packages have the two CPU graphs.

## IGEV++ Middlebury

- models/igev/IGEV_Middlebury_dynamic.onnx: CPU Float32.
- models/igev/IGEV_Middlebury_mixed.onnx: DirectML mixed FP16/FP32.
- Each has JSON identity/hash metadata; fixed16 iterations, max disparity768.
- RGB Float32 0..255; model includes −1..1 normalization. Symmetric multiple32
  padding; temporary matching offset removed afterward. No source alignment/crop.
- Official source commit099dec97989780d151700459c682df1cc2c18e88;
  official Middlebury weights SHA256eecddfa4549dc6180ce96e7ed8bf24a0bb0d702d5e747623eac54abed1fd7579.
- Project MIT notice and official checkpoint provenance retained; see
  [review](../docs/IGEV_REVIEW.md) and [third-party notices](../THIRD_PARTY.md).

The LAS2 files below are reused unchanged from Test3.

## LAS2-H

LAS2 source revision `8c97bd4c4da3712c2ac60003a23201dfdb5935f4`.
Four fixed iterations, max disparity 192. Unchanged verified Float32 graph SHA-256:
`ba2260dcc0aaff33a9fc1c41f729f727eb58eb034dfaec022713b3848ff5af76`.
The separate mixed graph retains Float32 computation islands. JSON files record
source and checkpoint hashes. No model substitution, external cache or download
at runtime. Model choice is saved; default LAS2-H.
