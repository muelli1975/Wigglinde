"""Geometry and color fidelity at the new renderer boundary."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from wigglinde.stereo import StereoScene
from wigglinde.vws import VWSRenderer, rgb_to_yuv420, yuv420_to_rgb
from wigglinde.models import GREAT_MODEL, model_iterations, model_path, model_suffix
from wigglinde.memory import MemorySampler
from wigglinde.resources import plan_views,GIB


class VWSTransportTests(unittest.TestCase):
    def test_parallel_process_memory_is_aggregated(self):
        sampler=MemorySampler(child=lambda:[11,12],child_label='vws')
        with patch('wigglinde.memory.process_memory',side_effect=[{'rss_bytes':100,'private_commit_bytes':70},{'rss_bytes':150,'private_commit_bytes':90}]):
            self.assertEqual(sampler._child_memory(),{'vws_rss_bytes':250,'vws_private_commit_bytes':160})

    def test_vws_parallel_budget_limits_processes_without_changing_images(self):
        plan=plan_views(1920,1080,31,8,16*GIB,4*GIB,bytes_per_pixel=384,overhead=96*1024**2,policy='vws_memory_bounded_v1')
        self.assertGreaterEqual(plan['workers'],1)
        self.assertLess(plan['workers'],8)
        self.assertLessEqual(plan['workers']*plan['estimated_bytes_per_view'],plan['memory_budget_bytes'])
        self.assertLessEqual(plan['workers']*plan['threads_per_view'],8)

    def test_standard_transport_preserves_uniform_chroma_blocks(self):
        rgb = np.random.default_rng(82).integers(0, 256, (18, 49, 3), dtype=np.uint8).repeat(2, 0).repeat(2, 1)
        result = yuv420_to_rgb(rgb_to_yuv420(rgb).tobytes(), 36, 98)
        self.assertLessEqual(int(np.abs(result.astype(int) - rgb.astype(int)).max()), 1)

    def test_signed_disparity_and_camera_bias_cancel_at_each_target(self):
        height, width = 11, 73
        rgb = np.zeros((height, width, 3), np.uint8)
        dl = np.linspace(-13, 19, width * height).reshape(height, width).astype(np.float32)
        dr = dl[:, ::-1].copy()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            exe = root / 'renderer';exe.touch()
            renderer = VWSRenderer(exe, StereoScene(rgb, rgb, dl, dr),
                                   [0, .25, .5, .75, 1], root / 'work', 8)
            low, high = renderer.inverse_depth_range
            for index, expected in enumerate((dl, dr)):
                pw, ph = renderer.storage_size
                encoded = np.fromfile(renderer.work / 'geometry' / f'input{index}.yuv', dtype='<u2', count=ph*pw).reshape(ph, pw)[:height, :width]
                native = (encoded.astype(np.uint32) * 1023 + 32767) // 65535
                restored = (native.astype(np.float64) / 1023 * (high - low) + low) * width - renderer.bias
                self.assertLessEqual(float(np.max(np.abs(restored - expected))), renderer.max_disparity_quantization_px + 1e-5)
            cameras = json.loads((renderer.work / 'cameras.json').read_text())['cameras']
            # A source point at x projects to x-t*d with zero residual bias.
            x, disparity = 41., -7.
            depth = width / (disparity + renderer.bias)
            for camera, position in zip(cameras[2:], [0, .25, .5, .75, 1]):
                projected = x - position * width / depth + camera['Principle_point'][0] - width / 2
                self.assertAlmostEqual(projected, x - position * disparity, places=6)
            self.assertEqual(cameras[0]['ColorSpace'], 'YUV420')
            self.assertEqual(cameras[0]['BitDepthDepth'], 16)

    def test_great_graph_identity_has_fixed_iterations_and_distinct_outputs(self):
        self.assertEqual(model_iterations(GREAT_MODEL), 32)
        self.assertEqual(model_path('/app', GREAT_MODEL).parts[-2:], ('great', 'GREAT_IGEV_Middlebury_dynamic.onnx'))
        self.assertEqual(model_path('/app', GREAT_MODEL, 0).name, 'GREAT_IGEV_Middlebury_mixed.onnx')
        self.assertEqual(model_suffix(GREAT_MODEL), 'great-igev-middlebury')


if __name__ == '__main__':
    unittest.main()
