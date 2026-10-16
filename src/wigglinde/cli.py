"""Development diagnostics. This is not yet the end-user converter."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import logging
import sys
import time

import numpy as np
from PIL import Image

from . import __version__
from .model import FoundationStereo
from .render import ViewRenderer, lenticular_positions
from .stereo import StereoScene, load_sbs


def main(argv=None):
    parser = ArgumentParser(description="Wigglinde: Diagnoseprototyp für ausgerichtete SBS-Fotos.")
    parser.add_argument("input", type=Path, help="SBS-Bild; mit --scene ein vorhandenes Diagnose-NPZ")
    parser.add_argument("--scene", action="store_true", help="Gespeicherte Geometrie wiederverwenden")
    parser.add_argument("--model", type=Path, help="Lokales dynamisches C-FoundationStereo-S ONNX")
    parser.add_argument("--provider", choices=("cpu", "cuda"), help="Gerät ausdrücklich auswählen")
    parser.add_argument("--layout", choices=("full-sbs", "half-sbs"), default="full-sbs")
    parser.add_argument("--swap", action="store_true", help="L/R vor der Berechnung tauschen")
    parser.add_argument("--matching-offset", type=int, default=0, help="Expliziter Suchversatz in Pixeln; Forschungsoption")
    parser.add_argument("--views", type=int, default=9, help="Gleichmäßig verteilte Diagnoseansichten")
    parser.add_argument("--output", type=Path, required=True, help="Neuer Diagnoseordner")
    args = parser.parse_args(argv)
    if args.views < 2 or args.matching_offset < 0:
        parser.error("Mindestens zwei Ansichten und nicht negativer Suchversatz erforderlich.")
    if not args.scene and (args.model is None or args.provider is None):
        parser.error("Für die Modellberechnung --model und --provider angeben.")
    if args.scene and (args.swap or args.layout != "full-sbs" or args.matching_offset != 0
                       or args.model is not None or args.provider is not None):
        parser.error("Bei gespeicherter Geometrie keine Eingabe-/Modelltransformationen angeben.")
    program_root = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2]
    log_root = program_root / "logs"
    log_root.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        handlers=[logging.FileHandler(log_root / "prototype.log", encoding="utf-8"),
                                  logging.StreamHandler()], force=True)
    logger = logging.getLogger("wigglinde")
    report = {"prototype_version": __version__, "status": "running",
              "input": str(args.input.resolve()), "diagnostic_only": True}
    start = time.monotonic()
    output_created = False
    try:
        # Existing folders are left intact. This is diagnostic-run separation,
        # not a proposed end-user filename/overwrite policy.
        args.output.mkdir(parents=True, exist_ok=False)
        output_created = True
        if args.scene:
            scene = StereoScene.load(args.input)
            report["geometry_reused"] = True
        else:
            left, right = load_sbs(args.input, args.layout, args.swap)
            model = FoundationStereo(args.model, args.provider, logger.info)
            dl, dr = model.predict_pair(left, right, args.matching_offset)
            scene = StereoScene(left, right, dl, dr)
            with args.input.open("rb") as source:
                report["input_sha256"] = hashlib.file_digest(source, "sha256").hexdigest()
            report.update(model_sha256=model.sha256, provider=model.provider,
                          runtime_version=model.runtime_version, load_seconds=model.load_seconds,
                          inference_seconds=model.inference_seconds, layout=args.layout,
                          swap=args.swap, matching_offset=args.matching_offset,
                          preprocessing="RGB /255, ImageNet mean/std, edge-pad to multiple of 32 and width >=416; no resize",
                          memory_reuse=False, memory_pattern=False)
            scene.save(args.output / "scene.npz")
        report["eye_size"] = [scene.left.shape[1], scene.left.shape[0]]
        renderer = ViewRenderer(scene)
        report["left_right_agreement_fraction"] = [float(mask.mean()) for mask in renderer.agreement]
        report["render_settings"] = {"consistency_tolerance_px": 1.0, "depth_band_px": 0.5,
                                     "inconsistent_sample_weight": 0.25,
                                     "background_inpainting": False, "uncovered_pixels": "transparent"}
        report["views"] = []
        for index, position in enumerate(lenticular_positions(args.views)):
            logger.info("Ansicht %d/%d, Blickposition %.4f", index + 1, args.views, position)
            view = renderer.render(position)
            filename = f"view_{index:03d}.png"
            Image.fromarray(view.rgba()).save(args.output / filename)
            report["views"].append({"file": filename, "position": position,
                                     "uncovered_fraction": float(1 - view.covered.mean())})
        for name, mask in zip(("agreement_left", "agreement_right"), renderer.agreement):
            Image.fromarray(mask.astype(np.uint8) * 255).save(args.output / f"{name}.png")
        report["status"] = "completed"
        logger.info("Diagnose abgeschlossen. Kein Nachweis der Fotoqualität oder Windows-Portabilität.")
        return 0
    except KeyboardInterrupt:
        report.update(status="cancelled")
        logger.info("Abgebrochen.")
        return 130
    except Exception as exc:
        report.update(status="error", error=str(exc))
        logger.exception("Diagnose fehlgeschlagen")
        return 1
    finally:
        report["elapsed_seconds"] = time.monotonic() - start
        if output_created:
            (args.output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
