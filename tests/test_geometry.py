import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from wigglinde.model import prepare_pair
from wigglinde.render import ViewRenderer, lenticular_positions
from wigglinde.stereo import StereoScene, consistency, load_sbs


def layer_reference(t):
    """Analytic front rectangle and textured background, not a renderer call."""
    h, w = 24, 96
    x = np.arange(w)[None, :] + int(t * 4)
    y = np.arange(h)[:, None]
    rgb = np.empty((h, w, 3), dtype=np.uint8)
    rgb[..., 0] = (x * 3) % 251
    rgb[..., 1] = (y * 7 + x) % 251
    rgb[..., 2] = 37
    d = np.full((h, w), 4.0, dtype=np.float32)
    foreground = slice(32 - int(t * 16), 48 - int(t * 16))
    rgb[:, foreground] = [241, 23, 19]
    d[:, foreground] = 16
    return rgb, d


class GeometryTests(unittest.TestCase):
    def test_withheld_layered_views_match_analytic_scene(self):
        left, dl = layer_reference(0)
        right, dr = layer_reference(1)
        renderer = ViewRenderer(StereoScene(left, right, dl, dr))
        for t in (0.25, 0.5, 0.75):
            expected, _ = layer_reference(t)
            result = renderer.render(t)
            np.testing.assert_array_equal(result.rgb[:, 8:-8], expected[:, 8:-8])
            self.assertTrue(result.covered[:, 8:-8].all())

    def test_negative_disparity_retains_depth_order(self):
        left, dl = layer_reference(0)
        right, dr = layer_reference(1)
        # Convergence shifts right view by +8 px and subtracts 8 from d.
        # Background d becomes -4; foreground remains in front at +8.
        right = np.pad(right, ((0, 0), (8, 0), (0, 0)), mode="edge")[:, :96]
        dr = np.pad(dr, ((0, 0), (8, 0)), mode="edge")[:, :96] - 8
        renderer = ViewRenderer(StereoScene(left, right, dl - 8, dr))
        middle = renderer.render(0.5)
        expected, _ = layer_reference(0.5)
        expected = np.pad(expected, ((0, 0), (4, 0), (0, 0)), mode="edge")[:, :96]
        np.testing.assert_array_equal(middle.rgb[:, 12:-12], expected[:, 12:-12])

    def test_endpoints_are_exact_and_return_views_are_deterministic(self):
        left, dl = layer_reference(0)
        right, dr = layer_reference(1)
        renderer = ViewRenderer(StereoScene(left, right, dl, dr))
        np.testing.assert_array_equal(renderer.render(0).rgb, left)
        np.testing.assert_array_equal(renderer.render(1).rgb, right)
        np.testing.assert_array_equal(renderer.render(0.37).rgba(), renderer.render(0.37).rgba())

    def test_unknown_geometry_remains_transparent(self):
        left, _ = layer_reference(0)
        d = np.full(left.shape[:2], np.nan, dtype=np.float32)
        view = ViewRenderer(StereoScene(left, left.copy(), d, d.copy())).render(0.5)
        self.assertFalse(view.covered.any())
        self.assertFalse(view.rgba()[..., 3].any())

    def test_consistency_does_not_clamp_outside_matches(self):
        d = np.full((4, 16), 3, dtype=np.float32)
        left_ok, right_ok = consistency(d, d)
        self.assertFalse(left_ok[:, :3].any())
        self.assertTrue(left_ok[:, 3:].all())
        self.assertFalse(right_ok[:, -3:].any())
        self.assertTrue(right_ok[:, :-3].all())

    def test_preprocessing_preserves_source_pixels_and_explicit_offset(self):
        rng = np.random.default_rng(1)
        left = rng.integers(0, 256, (37, 65, 3), dtype=np.uint8)
        right = left[:, ::-1].copy()
        a, b, crop = prepare_pair(left, right, 7)
        self.assertEqual(a.shape, (1, 3, 64, 416))
        self.assertEqual(a.shape, b.shape)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        restored = np.rint((a[0].transpose(1, 2, 0)[crop] * std + mean) * 255).astype(np.uint8)
        np.testing.assert_array_equal(restored, left)

    def test_sbs_layout_is_explicit_and_original_file_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "stereo.png"
            image = np.zeros((8, 24, 3), np.uint8)
            image[:, :12] = [255, 0, 0]
            image[:, 12:] = [0, 255, 0]
            Image.fromarray(image).save(path)
            original = path.read_bytes()
            left, right = load_sbs(path)
            self.assertEqual(left.shape, (8, 12, 3))
            wide_left, _ = load_sbs(path, "half-sbs")
            self.assertEqual(wide_left.shape, (8, 24, 3))
            swapped, _ = load_sbs(path, swap=True)
            np.testing.assert_array_equal(swapped, right)
            self.assertEqual(path.read_bytes(), original)

    def test_lenticular_views_are_uniform(self):
        np.testing.assert_allclose(lenticular_positions(5), [0, 0.25, 0.5, 0.75, 1])


if __name__ == "__main__":
    unittest.main()
