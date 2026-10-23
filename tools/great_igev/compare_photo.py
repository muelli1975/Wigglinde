"""Explicit full-resolution SBS research run; no application settings are changed."""

import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import threading
import time

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from wigglinde.onnx_stereo import OnnxStereo
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rvs", type=Path, required=True)
    parser.add_argument("--offset", type=int, required=True)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--onnx", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--export-ops", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Select a new output directory to preserve earlier results.")
    if not args.onnx and (not args.source or not args.weights):
        parser.error("Native mode requires --source and --weights.")
    if args.onnx and args.export_ops:
        parser.error("--export-ops applies only to the native research model.")
    args.output.mkdir(parents=True)
    with Image.open(args.input) as image:
        rgb = np.asarray(image.convert("RGB")).copy()
    if rgb.shape[1] % 2:
        parser.error("Full-SBS image must have even width.")
    height, width = rgb.shape[0], rgb.shape[1] // 2
    left, right = rgb[:, :width], rgb[:, width:]
    started = time.monotonic()
    if args.onnx:
        import onnxruntime as ort

        ort.disable_telemetry_events()
        options = ort.SessionOptions()
        options.intra_op_num_threads = args.threads
        options.enable_cpu_mem_arena = False
        # Research graph has no product model manifest. Reuse the unchanged
        # transport contract explicitly; this does not register a product model.
        model = OnnxStereo.__new__(OnnxStereo)
        model.session = ort.InferenceSession(
            str(args.onnx), sess_options=options, providers=["CPUExecutionProvider"]
        )
        model.lock, model.active = threading.Lock(), None

        def predict(a, b):
            return model.predict(a, b, args.offset, lambda: False)

        runtime = "ONNX Runtime CPU Float32"
    else:
        import torch
        from adapter import load, use_export_ops, use_streaming

        torch.set_num_threads(args.threads)
        model = use_streaming(load(args.source, args.weights))
        if args.export_ops:
            use_export_ops(model)

        def predict(a, b):
            pad_width = (-(width + args.offset)) % 32
            pad_height = (-height) % 32
            pads = (
                (pad_height // 2, pad_height - pad_height // 2),
                (pad_width // 2, pad_width - pad_width // 2),
                (0, 0),
            )

            def tensor(image, extra):
                padded = np.pad(image, ((0, 0), extra, (0, 0)), mode="edge")
                padded = np.pad(padded, pads, mode="edge")
                return torch.from_numpy(
                    np.ascontiguousarray(
                        padded.transpose(2, 0, 1)[None], dtype=np.float32
                    )
                )

            with torch.inference_mode():
                disparity = (
                    model(
                        tensor(a, (args.offset, 0)),
                        tensor(b, (0, args.offset)),
                        iters=32,
                        test_mode=True,
                    )[1]
                    .numpy()
                    .squeeze()
                )
            return (
                disparity[
                    pads[0][0] : pads[0][0] + height,
                    pads[1][0] + args.offset : pads[1][0] + args.offset + width,
                ]
                - args.offset
            ).copy()

        runtime = "PyTorch CPU Float32; streamed concat stem"
    report = dict(
        input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
        eye_size=[width, height],
        offset=args.offset,
        threads=args.threads,
        runtime=runtime,
        export_ops=args.export_ops,
        load_seconds=time.monotonic() - started,
        eyes=[],
    )
    maps = {}
    for eye in ["left", "right"]:
        a, b = (left, right) if eye == "left" else (right[:, ::-1], left[:, ::-1])
        started = time.monotonic()
        disparity = predict(a, b)
        if eye == "right":
            disparity = disparity[:, ::-1].copy()
        assert disparity.shape == (height, width) and np.isfinite(disparity).all()
        maps[eye + "_disparity"] = disparity
        np.save(args.output / (eye + ".npy"), disparity)
        report["eyes"].append(dict(eye=eye, seconds=time.monotonic() - started))
    report["depth_seconds"] = sum(row["seconds"] for row in report["eyes"])
    report["peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    scene = StereoScene(left, right, maps["left_disparity"], maps["right_disparity"])
    scene.save(args.output / "scene.npz")
    renderer = RVSRenderer(
        args.rvs.resolve(),
        scene,
        [0, 0.25, 0.5, 0.75, 1],
        args.output / "rvs",
        args.offset,
    )
    for index, frame in enumerate(renderer.frames(lambda: False)):
        Image.fromarray(frame).save(args.output / f"view-{index}.png")
    (args.output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
