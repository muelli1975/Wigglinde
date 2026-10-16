"""Offline adapter for the separately licensed C-FoundationStereo-S ONNX.

No NVlabs research source is imported. RGB/ImageNet preprocessing and padding
follow the public TAO inference interface; source references are in models/README.md.
Only the inspected model hash is accepted by this initial adapter.
"""
from pathlib import Path
import hashlib
import time

import numpy as np

MODEL_SHA256 = "a001a7bc0512a0bc3b3218194e924784e58b20656c6f1ea2c151024e555cfd64"
MODEL_FILENAME = "deployable_foundation_stereo_s_dynamic.onnx"
PROVIDERS = {"cpu": "CPUExecutionProvider", "cuda": "CUDAExecutionProvider"}


def prepare_pair(left, right, matching_offset=0):
    """Pad without changing source resolution. Offset is explicit research input.

    Padding left's left edge and right's right edge adds offset to d. Subtract
    it after prediction. This permits experiments with mounted signed disparities
    while retaining all original source pixels. No offset is guessed automatically.
    """
    if left.shape != right.shape or left.ndim != 3 or left.shape[2] != 3:
        raise ValueError("Zwei gleich große RGB-Halbbilder erforderlich.")
    if left.dtype != np.uint8 or right.dtype != np.uint8:
        raise ValueError("RGB-Daten mit 8 Bit pro Kanal erforderlich.")
    if type(matching_offset) is not int or matching_offset < 0:
        raise ValueError("Suchversatz muss eine nicht negative ganze Pixelzahl sein.")
    h, w = left.shape[:2]
    left = np.pad(left, ((0, 0), (matching_offset, 0), (0, 0)), mode="edge")
    right = np.pad(right, ((0, 0), (0, matching_offset), (0, 0)), mode="edge")
    # The inspected graph constructs 104 cost-volume disparities at 1/4 size.
    # Width <= 412 produces an empty Slice/Reshape. Pad, do not upscale a photo.
    padded_width = ((max(416, w + matching_offset) + 31) // 32) * 32
    extra_h, extra_w = (-h) % 32, padded_width - (w + matching_offset)
    top, before = extra_h // 2, extra_w // 2
    pad = ((top, extra_h - top), (before, extra_w - before), (0, 0))
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def prepare(image):
        image = np.pad(image, pad, mode="edge").astype(np.float32) / 255.0
        return np.ascontiguousarray(((image - mean) / std).transpose(2, 0, 1)[None])

    crop = (slice(top, top + h), slice(before + matching_offset, before + matching_offset + w))
    return prepare(left), prepare(right), crop


class FoundationStereo:
    def __init__(self, path, provider, log=lambda message: None, *, intra_op_threads=None):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Lokale Modelldatei fehlt: {path}. Es erfolgt kein Download.")
        if provider not in PROVIDERS:
            raise ValueError("Gerät ausdrücklich als cpu oder cuda wählen.")
        with path.open("rb") as stream:
            self.sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
        if self.sha256 != MODEL_SHA256:
            raise ValueError("Diese Modelldatei wurde für den Prototyp noch nicht geprüft (andere SHA-256).")
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("Die gewählte ONNX-Laufzeit ist nicht installiert.") from exc
        requested = PROVIDERS[provider]
        if requested not in ort.get_available_providers():
            raise RuntimeError(f"Gewähltes Gerät nicht verfügbar: {requested}. Kein automatischer Gerätewechsel.")
        log(f"ONNX-Modell laden ({requested}) …")
        start = time.monotonic()
        options = ort.SessionOptions()
        options.log_severity_level = 3
        # Optional explicit experimental setting; the application default does
        # not impose a thread cap.
        if intra_op_threads is not None:
            if type(intra_op_threads) is not int or intra_op_threads < 1:
                raise ValueError("Threadzahl muss eine positive ganze Zahl sein.")
            options.intra_op_num_threads = intra_op_threads
        # The 53k-node dynamic graph spends minutes in ORT's reuse planner.
        # Disable allocation reuse in this diagnostic adapter, not precision,
        # resolution, or model layers. Peak memory still needs photo-size tests.
        options.enable_mem_reuse = False
        options.enable_mem_pattern = False
        self.session = ort.InferenceSession(str(path), sess_options=options, providers=[requested])
        self.session.disable_fallback()
        if self.session.get_providers()[0] != requested:
            raise RuntimeError("ONNX konnte das gewählte Gerät nicht initialisieren. Kein CPU-Ersatzlauf.")
        expected_inputs = {"left_image", "right_image"}
        if {v.name for v in self.session.get_inputs()} != expected_inputs:
            raise ValueError("Unerwartete Modell-Eingaben.")
        if [v.name for v in self.session.get_outputs()] != ["disparity"]:
            raise ValueError("Unerwartete Modell-Ausgabe.")
        self.provider = provider
        self.runtime_version = ort.__version__
        self.load_seconds = time.monotonic() - start
        self.inference_seconds = []
        self.log = log
        log(f"Modell geladen: {self.load_seconds:.1f} s.")

    def predict(self, left, right, matching_offset=0):
        a, b, crop = prepare_pair(left, right, matching_offset)
        self.log(f"Disparität berechnen: {left.shape[1]} × {left.shape[0]} px pro Halbbild …")
        start = time.monotonic()
        value = self.session.run(["disparity"], {"left_image": a, "right_image": b})[0]
        self.inference_seconds.append(time.monotonic() - start)
        if value.shape != (1, 1, a.shape[2], a.shape[3]):
            raise ValueError(f"Unerwartete Disparitätsgröße: {value.shape}.")
        return value[0, 0][crop].astype(np.float32) - matching_offset

    def predict_pair(self, left, right, matching_offset=0):
        dl = self.predict(left, right, matching_offset)
        # Swap AND mirror. Swapping alone would violate the positive-disparity
        # model's camera ordering. Both outputs use d = x_left - x_right.
        dr = self.predict(right[:, ::-1], left[:, ::-1], matching_offset)[:, ::-1].copy()
        return dl, dr
