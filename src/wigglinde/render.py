"""Diagnostic bidirectional forward splatting of rectified stereo photographs.

This is a visibility baseline, not a finished layered/inpainting renderer.
Uncovered pixels stay transparent. No per-frame invented background is hidden
inside the output. The depth band and agreement weighting are research settings.
"""
from dataclasses import dataclass
import math

import numpy as np

from .stereo import StereoScene, consistency


def _linear(rgb):
    v = rgb.astype(np.float32) / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def _srgb(rgb):
    v = np.clip(rgb, 0, 1)
    v = np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)
    return np.rint(v * 255).astype(np.uint8)


@dataclass
class RenderedView:
    rgb: np.ndarray
    covered: np.ndarray

    def rgba(self):
        return np.dstack((self.rgb, self.covered.astype(np.uint8) * 255))


class ViewRenderer:
    def __init__(self, scene: StereoScene, consistency_tolerance=1.0, depth_band=0.5):
        if not np.isfinite(depth_band) or depth_band < 0:
            raise ValueError("Tiefenband muss endlich und nicht negativ sein.")
        self.scene = scene
        self.depth_band = depth_band
        self.agreement = consistency(scene.left_disparity, scene.right_disparity, consistency_tolerance)

    def render(self, position):
        t = float(position)
        if not math.isfinite(t) or not 0 <= t <= 1:
            raise ValueError("Blickposition muss zwischen 0 (links) und 1 (rechts) liegen.")
        scene = self.scene
        h, w = scene.left.shape[:2]
        if t in (0, 1):
            source = scene.left if t == 0 else scene.right
            return RenderedView(source.copy(), np.ones((h, w), dtype=bool))
        output = np.zeros((h, w, 3), dtype=np.uint8)
        coverage = np.zeros((h, w), dtype=bool)
        # Bound working memory; never resize input or disparity to save memory.
        for start in range(0, h, 32):
            end = min(h, start + 32)
            n = end - start
            zbuffer = np.full(n * w, -np.inf, dtype=np.float32)
            contributions = []
            for rgb, disp, agreement, shift, source_weight in (
                (scene.left, scene.left_disparity, self.agreement[0], -t, 1 - t),
                (scene.right, scene.right_disparity, self.agreement[1], 1 - t, t),
            ):
                d = disp[start:end]
                good = np.isfinite(d)
                target = np.arange(w, dtype=np.float32)[None, :] + shift * np.where(good, d, 0)
                inside = good & (target >= -1) & (target <= w)
                low = np.floor(np.clip(target, -1, w)).astype(np.int64)
                fraction = target - low
                color = _linear(rgb[start:end]).reshape(-1, 3)
                reliability = np.where(agreement[start:end], 1.0, 0.25)
                rows = np.arange(n)[:, None] * w
                for xx, spatial_weight in ((low, 1 - fraction), (low + 1, fraction)):
                    valid = inside & (xx >= 0) & (xx < w) & (spatial_weight > 0)
                    source_indices = np.flatnonzero(valid)
                    target_indices = (rows + xx)[valid]
                    depths = d[valid]
                    weights = (spatial_weight * reliability * source_weight)[valid]
                    np.maximum.at(zbuffer, target_indices, depths)
                    contributions.append((target_indices, depths, weights, color[source_indices]))
            color_sum = np.zeros((n * w, 3), dtype=np.float32)
            weight_sum = np.zeros(n * w, dtype=np.float32)
            for indices, depths, weights, color in contributions:
                front = depths >= zbuffer[indices] - self.depth_band
                indices, weights, color = indices[front], weights[front], color[front]
                np.add.at(weight_sum, indices, weights)
                np.add.at(color_sum, indices, color * weights[:, None])
            covered = weight_sum > 0
            color_sum[covered] /= weight_sum[covered, None]
            output[start:end] = _srgb(color_sum).reshape(n, w, 3)
            coverage[start:end] = covered.reshape(n, w)
        return RenderedView(output, coverage)


def lenticular_positions(count):
    """Uniform view positions; no wiggle timing is baked into lenticular views."""
    if type(count) is not int or count < 2:
        raise ValueError("Mindestens zwei Ansichten erforderlich.")
    return np.linspace(0, 1, count).tolist()
