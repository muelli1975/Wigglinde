"""RGB24 renderer transport, CPU compatibility and corrupt-stream rejection."""
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np

from wigglinde.rvs import RVSRenderer


class ChunkedBytes(io.BytesIO):
    def readinto(self, view):
        return super().readinto(view[:11])


class FakeProcess:
    def __init__(self, data):
        self.stdout=ChunkedBytes(data)
    def poll(self):return 0
    def wait(self):return 0
    def kill(self):raise AssertionError("Completed process must not be killed")


class RVSStreamTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.rgb=np.arange(2*128*3,dtype=np.uint8).reshape(2,128,3)
        d=np.full((2,128),4,np.float32)
        self.scene=SimpleNamespace(left=self.rgb,right=self.rgb,
                                   left_disparity=d,right_disparity=d)

    def renderer(self, **kwargs):
        return RVSRenderer(Path(sys.executable),self.scene,[0,1],self.root/"rvs",**kwargs)

    def test_default_cpu_float_transport_is_unchanged(self):
        renderer=self.renderer()
        expected=[self.rgb,self.rgb[:,::-1].copy()]
        data=b"".join((x.astype(np.float32)/np.float32(255)).tobytes() for x in expected)
        with patch("wigglinde.rvs.subprocess.Popen",return_value=FakeProcess(data)) as launch:
            frames=list(renderer.frames(lambda:False))
        for actual,wanted in zip(frames,expected):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual(len(frames),2)
        self.assertNotIn("--rgb24",launch.call_args.args[0])

    def test_vulkan_rgb24_preserves_all_rgb_values_with_short_reads(self):
        renderer=self.renderer(stream_format="rgb24")
        expected=[self.rgb,self.rgb[:,::-1].copy()]
        with patch("wigglinde.rvs.subprocess.Popen",
                   return_value=FakeProcess(b"".join(x.tobytes() for x in expected))) as launch:
            frames=list(renderer.frames(lambda:False))
        for actual,wanted in zip(frames,expected):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual(len(frames),2)
        self.assertEqual(launch.call_args.args[0][-1],"--rgb24")

    def test_vulkan_rejects_text_after_the_last_expected_frame(self):
        renderer=self.renderer(stream_format="rgb24")
        with patch("wigglinde.rvs.subprocess.Popen",
                   return_value=FakeProcess(self.rgb.tobytes()*2+b"stray diagnostic\n")):
            with self.assertRaisesRegex(RuntimeError,"unexpected bytes"):
                list(renderer.frames(lambda:False))

    def test_vulkan_rejects_incomplete_frame(self):
        renderer=self.renderer(stream_format="rgb24")
        with patch("wigglinde.rvs.subprocess.Popen",
                   return_value=FakeProcess(self.rgb.tobytes()[:-1])):
            with self.assertRaises(RuntimeError):list(renderer.frames(lambda:False))

    def test_unknown_transport_is_rejected(self):
        with self.assertRaises(ValueError):self.renderer(stream_format="unknown")


if __name__=="__main__":unittest.main()
