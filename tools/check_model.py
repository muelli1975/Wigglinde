"""Opt-in local model experiment; not part of the fast unit tests.

Outputs measurements, not a photo-quality acceptance gate. No download occurs.
Run after installing the package and the selected ONNX Runtime provider.
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import time

import numpy as np
from PIL import Image, ImageFilter

from wigglinde.model import FoundationStereo
from wigglinde.render import ViewRenderer
from wigglinde.stereo import StereoScene


def main():
    parser = ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--provider", required=True, choices=("cpu", "cuda"))
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--threads", type=int, help="Explizite Threadzahl nur für diesen Versuch")
    args = parser.parse_args()
    rng = np.random.default_rng(17)
    left = np.asarray(Image.fromarray(rng.integers(0, 256, (128, 416, 3), dtype=np.uint8))
                      .filter(ImageFilter.GaussianBlur(1)))
    # Known 8-pixel translation of one textured plane. No geometric estimator
    # produced these endpoints or the withheld midpoint reference.
    right = np.pad(left[:, 8:], ((0, 0), (0, 8), (0, 0)), mode="edge")
    expected = np.pad(left[:, 4:], ((0, 0), (0, 4), (0, 0)), mode="edge")
    report = {"experiment": "known_translation_8px", "photo_quality_proven": False}
    start = time.monotonic()
    try:
        model = FoundationStereo(args.model, args.provider, lambda text: print(text, flush=True),
                                 intra_op_threads=args.threads)
        dl, dr = model.predict_pair(left, right)
        renderer = ViewRenderer(StereoScene(left, right, dl, dr))
        view = renderer.render(0.5)
        region = (slice(16, -16), slice(24, -24))
        report.update(status="completed", model_sha256=model.sha256, runtime=model.runtime_version,
                      provider=model.provider, intra_op_threads=args.threads, load_seconds=model.load_seconds,
                      inference_seconds=model.inference_seconds,
                      median_disparity_left=float(np.nanmedian(dl[region])),
                      median_abs_disparity_error_left=float(np.nanmedian(np.abs(dl[region] - 8))),
                      median_abs_disparity_error_right=float(np.nanmedian(np.abs(dr[region] - 8))),
                      agreement_fraction=[float(x.mean()) for x in renderer.agreement],
                      midpoint_mae=float(np.abs(view.rgb[region].astype(float) - expected[region]).mean()),
                      midpoint_coverage=float(view.covered[region].mean()))
    except Exception as exc:
        report.update(status="error", error=str(exc))
        raise
    finally:
        report["total_seconds"] = time.monotonic() - start
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
