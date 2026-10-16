import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from wigglinde.export_options import WiggleOptions, camera_weight, cycle_index, gif_frame_durations
from wigglinde.wiggle_export import export_wiggle, ffmpeg_path, ExportCancelled


class ExportTests(unittest.TestCase):
    def test_splattricia_timing_and_no_upscale(self):
        options = WiggleOptions()
        options.validate()
        self.assertEqual(options.frame_count, 60)
        self.assertEqual(options.output_size(640, 480), (640, 480))
        self.assertEqual(camera_weight(0, 60), 0)
        self.assertEqual(camera_weight(30, 60), 1)
        self.assertEqual(cycle_index(59, 60), 1)
        self.assertEqual(sum(gif_frame_durations(30, 15)), 2000)

    @staticmethod
    def frame(t):
        out = np.zeros((9, 17, 3), dtype=np.uint8)
        out[:] = [round(t * 200), 90, 30]
        return out

    def test_png_sequence_contains_one_cycle_and_mirrored_return(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            calls = []
            def render(t):
                calls.append(t)
                return self.frame(t)
            export_wiggle(render, (17, 9), WiggleOptions(format="png", cycle_seconds=0.5),
                          root / "frames", root / "_temp")
            frames = sorted((root / "frames").glob("*.png"))
            self.assertEqual(len(frames), 15)
            self.assertEqual(len(calls), 8)
            self.assertEqual(frames[1].read_bytes(), frames[-1].read_bytes())

    def test_gif_loops_with_complete_cycle_duration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            export_wiggle(self.frame, (17, 9), WiggleOptions(format="gif", cycle_seconds=2),
                          root / "wiggle.gif", root / "_temp")
            with Image.open(root / "wiggle.gif") as image:
                self.assertEqual(image.info["loop"], 0)
                self.assertEqual(image.size, (17, 9))
                duration = 0
                for i in range(image.n_frames):
                    image.seek(i)
                    duration += image.info["duration"]
                self.assertEqual(duration, 2000)

    def test_mp4_has_five_cycles_and_pads_odd_dimensions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "wiggle.mp4"
            export_wiggle(self.frame, (17, 9), WiggleOptions(cycle_seconds=0.5), target, root / "_temp")
            result = subprocess.run([ffmpeg_path(), "-v", "error", "-i", str(target),
                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                    check=True, capture_output=True)
            self.assertEqual(len(result.stdout), 18 * 10 * 3 * 75)

    def test_cancel_preserves_previous_completed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            previous = root / "wiggle.mp4"
            previous.write_bytes(b"previous completed result")
            with self.assertRaises(ExportCancelled):
                export_wiggle(self.frame, (17, 9), WiggleOptions(), previous, root / "_temp", cancel=lambda: True)
            self.assertEqual(previous.read_bytes(), b"previous completed result")


if __name__ == "__main__":
    unittest.main()
