"""Explicit native DEFOM research run; no product models or settings are changed."""

import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np
from PIL import Image


SOURCE_REVISION = "5b27591d83956e5d329ff66704271a9e68b1c75f"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--encoder", choices=["vits", "vitl"], required=True)
    parser.add_argument("--offset", type=int, required=True)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--rvs", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Select a new output directory to preserve earlier results.")
    revision = subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    status = subprocess.check_output(
        ["git", "-C", str(args.source), "status", "--porcelain"], text=True
    ).strip()
    dirty = [line for line in status.splitlines() if not (line.startswith("?? ") and line.endswith("/__pycache__/"))]
    if revision != SOURCE_REVISION or dirty:
        parser.error("Expected the pinned, unchanged official DEFOM source.")
    if args.offset < 0 or args.threads < 1:
        parser.error("Offset must be nonnegative and threads positive.")
    args.output.mkdir(parents=True)
    sys.path[:0] = [str(args.source.resolve()), str(args.source.resolve() / "core")]
    import torch
    from core.defom_stereo import DEFOMStereo
    from core.utils.utils import InputPadder, get_danv2_io_size

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from wigglinde.rvs import RVSRenderer
    from wigglinde.stereo import StereoScene

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    with Image.open(args.input) as image:
        rgb = np.array(image.convert("RGB"))
    height, full_width = rgb.shape[:2]
    if full_width % 2:
        parser.error("Expected even-width Full-SBS input.")
    width = full_width // 2
    left, right = rgb[:, :width], rgb[:, width:]
    config = SimpleNamespace(
        dinov2_encoder=args.encoder,
        idepth_scale=0.5,
        hidden_dims=[128, 128, 128],
        corr_implementation="reg",
        corr_levels=2,
        corr_radius=4,
        scale_list=[0.125, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        scale_corr_radius=2,
        n_downsample=2,
        context_norm="batch",
        n_gru_layers=3,
        shared_backbone=False,
        mixed_precision=False,
    )
    report = dict(
        input_sha256=sha256(args.input),
        weights_sha256=sha256(args.weights),
        weights_bytes=args.weights.stat().st_size,
        source_revision=revision,
        runtime="PyTorch CPU Float32; unchanged official operators",
        torch_version=torch.__version__,
        encoder=args.encoder,
        eye_size=[width, height],
        offset=args.offset,
        threads=args.threads,
        iterations=32,
        scale_iterations=8,
        config=vars(config),
        eyes=[],
    )

    def checkpoint_report():
        report["peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    print("Loading official checkpoint (strict)", flush=True)
    started = time.monotonic()
    model = DEFOMStereo(config)
    state = torch.load(args.weights, map_location="cpu", weights_only=True, mmap=True)
    state = state.get("model", state)
    incompatible = model.load_state_dict(state, strict=True)
    del state
    model.eval()
    report["load_seconds"] = time.monotonic() - started
    report["parameters_total"] = sum(p.numel() for p in model.parameters())
    report["parameters_trainable"] = sum(p.numel() for p in model.parameters() if p.requires_grad)
    report["missing_keys"] = incompatible.missing_keys
    report["unexpected_keys"] = incompatible.unexpected_keys
    checkpoint_report()
    print(json.dumps({k: report[k] for k in ["load_seconds", "parameters_total", "parameters_trainable"]}), flush=True)

    def predict(a, b):
        def tensor(image, extra):
            padded = np.pad(image, ((0, 0), extra, (0, 0)), mode="edge")
            return torch.from_numpy(np.ascontiguousarray(padded.transpose(2, 0, 1)[None], dtype=np.float32))

        a, b = tensor(a, (args.offset, 0)), tensor(b, (0, args.offset))
        padder = InputPadder(a.shape, divis_by=32)
        a, b = padder.pad(a, b)
        report["padded_input_size"] = list(a.shape[-2:][::-1])
        report["native_da2_sizes_h_w"] = list(get_danv2_io_size(*a.shape[-2:], config.n_downsample))
        with torch.inference_mode():
            disp = model(a, b, iters=32, scale_iters=8, test_mode=True)
        disp = padder.unpad(disp)[0, 0, :, args.offset:].numpy().copy() - args.offset
        if disp.shape != (height, width) or not np.isfinite(disp).all():
            raise ValueError("Invalid native disparity output")
        return disp

    maps = {}
    for eye in ["left", "right"]:
        print("Starting " + eye + " eye", flush=True)
        a, b = (left, right) if eye == "left" else (right[:, ::-1], left[:, ::-1])
        started = time.monotonic()
        disparity = predict(a, b)
        if eye == "right":
            disparity = disparity[:, ::-1].copy()
        maps[eye + "_disparity"] = disparity
        np.save(args.output / (eye + ".npy"), disparity)
        report["eyes"].append(dict(eye=eye, seconds=time.monotonic() - started))
        checkpoint_report()
        print(json.dumps(report["eyes"][-1]), flush=True)
    report["depth_seconds"] = sum(row["seconds"] for row in report["eyes"])
    scene = StereoScene(left, right, maps["left_disparity"], maps["right_disparity"])
    scene.save(args.output / "scene.npz")
    renderer = RVSRenderer(args.rvs.resolve(), scene, [0, 0.25, 0.5, 0.75, 1], args.output / "rvs", args.offset)
    for index, frame in enumerate(renderer.frames(lambda: False)):
        Image.fromarray(frame).save(args.output / f"view-{index}.png")
    report["complete"] = True
    checkpoint_report()
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
