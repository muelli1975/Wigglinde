# Wigglinde 1.2 Test 2 · Windows x64

Separate portable test version. The published 1.1 is unchanged.
Extract the complete ZIP into its own folder and start `Wigglinde.exe`.

| Model | Purpose |
| --- | --- |
| LAS2-H | Unchanged fast default |
| IGEV++ Middlebury | Existing alternative for difficult photographs |
| DEFOM-S/RVC | New Small/RVC comparison |
| DEFOM-L (CC-BY-NC-4.0) | New Large/Middlebury comparison; noncommercial model license |

RVS remains the unchanged CPU renderer (Precision 1, RGB, Simple 5).
GREAT-IGEV and VWS are omitted following the practical comparisons. No iteration
or renderer selector. Export formats, per-format settings and 720p/CPU defaults
are retained. The test uses its own settings file.

CPU uses Float32; the explicitly selected Windows GPU uses mixed Float16/Float32
through DirectML. DEFOM loads and runs in a separate process so native failures
can be reported without taking down the window. Cancellation also terminates
that worker. Models are local; no download or automatic fallback occurs.

The Large model substantially increases package size and memory needs. Resource
measurements and numerical comparisons are documented in
[DEFOM_STUDY.md](docs/DEFOM_STUDY.md). Successful hosted CPU checks do not establish
performance, memory limits or stability on a physical GPU.

Please compare the same photograph, output size and device. Inspect the railing
and other thin structures throughout the movement. A different depth map alone
does not prove improved animation quality. Lenticular functions remain postponed.

License attribution and complete terms: `licenses/DEFOM` in the package,
[source notice](tools/defom/NOTICE.md). In particular, the Large model carries
CC-BY-NC-4.0; it is visibly marked in the model selector.
