# GREAT-IGEV research adapter

The streamed volume computation and the Outlook export adaptations follow
GREAT-Stereo by Jiahao Li and contributors, revision
`2a6b1efede8c3a9eec9540790c2700ea2f3dee7d`:
https://github.com/JarvisLee0423/GREAT-Stereo

Upstream source is available under Apache License 2.0; the unchanged license
is in `UPSTREAM_LICENSE.txt`. Changes made for this experiment: chunked execution
of the concat-volume stem, identity-convolution implementations of unfold/fold,
dynamic indexing for roll, and symbolic stride-one Outlook dimensions. These
changes are build/research adapters and are not imported by Wigglinde.

The original repository is loaded from an explicit separate checkout. No upstream
checkpoint, input photograph or generated ONNX model is included in this branch.
Full provenance, licensing observations and numerical limits are documented in
`docs/GREAT_IGEV_STUDY.md`.
