"""Rectified stereo geometry, with signed disparity in source-image pixels.

Convention: d = x_left - x_right. The right map contains the SAME signed
quantity at right-image coordinates; it is not a reversed optical-flow vector.
Larger disparities are closer, including when a convergence shift makes them
negative. No metric camera calibration is needed for interpolation on this line.
"""
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps


def load_sbs(path, layout="full-sbs", swap=False):
    with Image.open(path) as source:
        oriented = ImageOps.exif_transpose(source)
        image = oriented.convert("RGB")
        width, height = image.size
        if width % 2 or width < 4:
            raise ValueError("SBS-Bild benötigt zwei gleich breite Halbbilder.")
        left = image.crop((0, 0, width // 2, height))
        right = image.crop((width // 2, 0, width, height))
        if layout == "half-sbs":
            left = left.resize((width, height), Image.Resampling.LANCZOS)
            right = right.resize((width, height), Image.Resampling.LANCZOS)
        elif layout != "full-sbs":
            raise ValueError("Unbekanntes SBS-Layout.")
        pair = np.asarray(left).copy(), np.asarray(right).copy()
    return pair[::-1] if swap else pair


def sample_horizontal(values, x):
    """Bilinear 1-D lookup; no clamping an out-of-image match into validity."""
    height, width = values.shape
    finite = np.isfinite(x)
    safe = np.clip(np.where(finite, x, 0), 0, width - 1)
    low = np.floor(safe).astype(np.int64)
    high = np.minimum(low + 1, width - 1)
    rows = np.arange(height)[:, None]
    fraction = safe - low
    a, b = values[rows, low], values[rows, high]
    # At integer coordinates an invalid neighbour has zero contribution.
    out = np.where(fraction == 0, a, a * (1 - fraction) + b * fraction)
    valid = finite & (x >= 0) & (x <= width - 1) & np.isfinite(out)
    return out, valid


def consistency(left_disparity, right_disparity, tolerance=1.0):
    """Left/right agreement, not a confidence output supplied by the model."""
    if left_disparity.shape != right_disparity.shape or left_disparity.ndim != 2:
        raise ValueError("Disparitätskarten müssen dieselbe zweidimensionale Form haben.")
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("Konsistenztoleranz muss positiv sein.")
    x = np.arange(left_disparity.shape[1], dtype=np.float32)[None, :]
    at_right, valid_left = sample_horizontal(right_disparity, x - left_disparity)
    at_left, valid_right = sample_horizontal(left_disparity, x + right_disparity)
    valid_left &= np.isfinite(left_disparity)
    valid_right &= np.isfinite(right_disparity)
    return (valid_left & (np.abs(left_disparity - at_right) <= tolerance),
            valid_right & (np.abs(right_disparity - at_left) <= tolerance))


@dataclass
class StereoScene:
    left: np.ndarray
    right: np.ndarray
    left_disparity: np.ndarray
    right_disparity: np.ndarray

    def __post_init__(self):
        if self.left.shape != self.right.shape or self.left.ndim != 3 or self.left.shape[2] != 3:
            raise ValueError("Zwei gleich große RGB-Halbbilder erforderlich.")
        if self.left.dtype != np.uint8 or self.right.dtype != np.uint8:
            raise ValueError("Dieser Prototyp erwartet RGB-Bilder mit 8 Bit pro Kanal.")
        if self.left_disparity.shape != self.left.shape[:2] or self.right_disparity.shape != self.left.shape[:2]:
            raise ValueError("Disparitätskarten müssen zur unskalierten Bildgröße passen.")
        self.left_disparity = self.left_disparity.astype(np.float32, copy=False)
        self.right_disparity = self.right_disparity.astype(np.float32, copy=False)

    def save(self, path):
        np.savez_compressed(path, left=self.left, right=self.right,
                            left_disparity=self.left_disparity, right_disparity=self.right_disparity)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as data:
            return cls(**{key: data[key] for key in ("left", "right", "left_disparity", "right_disparity")})
