"""Explicit research-only export. Downloads nothing and does not edit application models.

Run in a separate process: the upstream transformer globals are adapted for export.
See docs/GREAT_IGEV_STUDY.md for pinned dependencies, provenance and limitations.
"""

import argparse
import collections
import json
import hashlib
from pathlib import Path
import time

import numpy as np
import onnx
import onnxruntime as ort
import torch

from adapter import load, use_export_ops, use_streaming, SOURCE_REVISION, WEIGHTS_SHA256


class Wrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, left, right):
        return self.model(left, right, iters=32, test_mode=True)[1]


def error(actual, reference):
    values = np.abs(actual - reference)
    return dict(
        max_px=float(values.max()),
        mean_px=float(values.mean()),
        p99_px=float(np.quantile(values, 0.99)),
        over_1px_percent=float(np.mean(values > 1) * 100),
        finite=bool(np.isfinite(actual).all()),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; select a new research graph path.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(args.threads)
    torch.manual_seed(19)
    model = load(args.source, args.weights)
    cases = []
    with torch.inference_mode():
        for width, height in [(416, 128), (448, 160)]:
            texture = torch.randint(0, 256, (1, 3, height, width + 8), dtype=torch.float32)
            a, b = texture[:, :, :, :width].contiguous(), texture[:, :, :, 8:].contiguous()
            cases.append((a, b, Wrapper(model)(a, b).numpy()))
    left, right, baseline = cases[0]
    with torch.inference_mode():
        use_streaming(model)
        streamed = Wrapper(model)(left, right).numpy()
        use_export_ops(model)
        wrapped = Wrapper(model).eval()
        adapted = wrapped(left, right).numpy()
    checks = {
        "streamed_vs_original": error(streamed, baseline),
        "export_ops_vs_original": error(adapted, baseline),
    }
    np.testing.assert_allclose(streamed, baseline, atol=0.01, rtol=0.001)
    np.testing.assert_allclose(adapted, baseline, atol=0.01, rtol=0.001)
    started = time.monotonic()
    with torch.inference_mode():
        torch.onnx.export(
            wrapped,
            (left, right),
            str(args.output),
            opset_version=18,
            input_names=["left", "right"],
            output_names=["disparity"],
            dynamic_axes={
                name: {2: "height", 3: "width"}
                for name in ["left", "right", "disparity"]
            },
            dynamo=False,
            do_constant_folding=True,
        )
    export_seconds = time.monotonic() - started
    graph = onnx.load(str(args.output))
    onnx.checker.check_model(graph)
    options = ort.SessionOptions()
    options.intra_op_num_threads = args.threads
    options.enable_cpu_mem_arena = False
    ort.disable_telemetry_events()
    session = ort.InferenceSession(
        str(args.output), sess_options=options, providers=["CPUExecutionProvider"]
    )
    actual = session.run(None, {"left": left.numpy(), "right": right.numpy()})[0]
    checks["onnx_vs_original"] = error(actual, baseline)
    np.testing.assert_allclose(actual, baseline, atol=0.01, rtol=0.001)
    left, right, expected = cases[1]
    actual = session.run(None, {"left": left.numpy(), "right": right.numpy()})[0]
    checks["dynamic_shape_448x160"] = error(actual, expected)
    np.testing.assert_allclose(actual, expected, atol=0.01, rtol=0.001)
    result = dict(
        iterations=32,
        max_disparity=768,
        precision="float32",
        export_seconds=export_seconds,
        threads=args.threads,
        checks=checks,
        operators=dict(collections.Counter(n.op_type for n in graph.graph.node)),
        physical_gpu_validated=False,
    )
    args.output.with_suffix(".research.json").write_text(json.dumps(result, indent=2))
    metadata = dict(model='GREAT-IGEV Middlebury', precision='float32', iterations=32,
                    max_disparity=768, source_revision=SOURCE_REVISION,
                    weights_sha256=WEIGHTS_SHA256,
                    onnx_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                    input='RGB Float32 0..255; model internal normalization; symmetric edge padding to multiple 32; reversible offset',
                    export_substitutions=['disparity-chunked concat stem, full search range',
                                          'identity Conv/ConvTranspose unfold/fold',
                                          'dynamic index roll, symbolic Outlook dimensions'],
                    native_onnx_checks=checks, physical_gpu_validated=False)
    args.output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    np.savez_compressed(args.output.with_suffix('.validation.npz'),
                        **{f'{i}_{key}': value.numpy() if hasattr(value, 'numpy') else value
                           for i, row in enumerate(cases)
                           for key, value in zip(('left', 'right', 'disparity'), row)})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
