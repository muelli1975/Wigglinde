"""Explicit CPU ONNX/native checks and optional private full-resolution photo run."""

import argparse
import json
from pathlib import Path
import resource
import sys
import threading
import time

import numpy as np
import onnx
import onnxruntime as ort
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from wigglinde.onnx_stereo import OnnxStereo
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--references", type=Path)
    parser.add_argument("--photo-reference", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rvs", type=Path)
    parser.add_argument("--offset", type=int, default=68)
    args = parser.parse_args()
    if args.photo_reference and not (args.output and args.rvs):
        parser.error("Photo mode requires new --output directory and --rvs")
    if args.output and args.output.exists():
        parser.error("Select a new output directory")
    ort.disable_telemetry_events()
    onnx.checker.check_model(str(args.model), full_check=True)
    settings = ort.SessionOptions()
    settings.intra_op_num_threads = 8
    settings.enable_cpu_mem_arena = False
    started = time.monotonic()
    session = ort.InferenceSession(str(args.model), sess_options=settings, providers=["CPUExecutionProvider"])
    report = dict(model=str(args.model.name), load_seconds=time.monotonic() - started,
                  physical_gpu_validated=False, native_onnx_cases=[])
    references = np.load(args.references or args.model.with_suffix(".validation.npz"))
    mixed = "mixed" in args.model.stem.lower()
    for i in range(2):
        feed = {name: references[f"{i}_{name}"] for name in ["left", "right"]}
        expected = references[f"{i}_disparity"]
        started = time.monotonic()
        actual = session.run(None, feed)[0]
        if actual.shape != expected.shape or not np.isfinite(actual).all():
            raise ValueError("Invalid output")
        error = np.abs(actual - expected)
        row = dict(size=list(actual.shape[-2:][::-1]), seconds=time.monotonic() - started,
                   max_error_px=float(error.max()), mean_error_px=float(error.mean()),
                   p99_error_px=float(np.quantile(error, .99)))
        report["native_onnx_cases"].append(row)
        print(json.dumps(row), flush=True)
        np.testing.assert_allclose(actual, expected, rtol=.01 if mixed else .001, atol=.1 if mixed else .01)
    if args.photo_reference:
        args.output.mkdir(parents=True)
        reference = np.load(args.photo_reference)
        model = OnnxStereo.__new__(OnnxStereo)
        model.session, model.lock, model.active = session, threading.Lock(), None
        arrays = {}
        report["photo"] = []
        for eye in ["left", "right"]:
            left, right = (reference["left"], reference["right"]) if eye == "left" else (reference["right"][:, ::-1], reference["left"][:, ::-1])
            started = time.monotonic()
            actual = model.predict(left, right, args.offset, lambda: False)
            if eye == "right":
                actual = actual[:, ::-1].copy()
            if actual.shape != reference[eye + "_disparity"].shape or not np.isfinite(actual).all():
                raise ValueError("Invalid photographic disparity")
            arrays[eye + "_disparity"] = actual
            error = np.abs(actual - reference[eye + "_disparity"])
            row = dict(eye=eye, seconds=time.monotonic() - started,
                       max_error_px=float(error.max()), mean_error_px=float(error.mean()),
                       p99_error_px=float(np.quantile(error, .99)),
                       rail_p99_error_px=float(np.quantile(error[510:], .99)))
            report["photo"].append(row)
            print(json.dumps(row), flush=True)
        scene = StereoScene(reference["left"], reference["right"], arrays["left_disparity"], arrays["right_disparity"])
        scene.save(args.output / "scene.npz")
        renderer = RVSRenderer(args.rvs.resolve(), scene, [0, .25, .5, .75, 1], args.output / "rvs", args.offset)
        for i, frame in enumerate(renderer.frames(lambda: False)):
            Image.fromarray(frame).save(args.output / f"view-{i}.png")
    report["peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    report["status"] = "passed"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
