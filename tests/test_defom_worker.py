"""Real worker transport, cancellation and native-process failure containment."""

import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from wigglinde.defom import DEFOMStereo, WorkerError
from wigglinde.models import DEFOM_SMALL
from wigglinde.wiggle_export import ExportCancelled

# Tiny ONNX Sub/ReduceMean graph, not a stereo estimator. Exercises the actual
# spawned ORT worker and transport without downloading research weights in tests.
FIXTURE = base64.b64decode('CAg68QEKGAoEbGVmdAoFcmlnaHQSBGRpZmYiA1N1Ygo7CgRkaWZmEglkaXNwYXJpdHkiClJlZHVjZU1lYW4qCwoEYXhlc0ABoAEHKg8KCGtlZXBkaW1zGAGgAQISEXRyYW5zcG9ydC1maXh0dXJlWikKBGxlZnQSIQofCAESGwoCCAEKAggDCggSBmhlaWdodAoHEgV3aWR0aFoqCgVyaWdodBIhCh8IARIbCgIIAQoCCAMKCBIGaGVpZ2h0CgcSBXdpZHRoYi4KCWRpc3Bhcml0eRIhCh8IARIbCgIIAQoCCAEKCBIGaGVpZ2h0CgcSBXdpZHRoQgQKABAR')


class DEFOMWorkerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'model.onnx'
        self.path.write_bytes(FIXTURE)
        self.path.with_suffix('.json').write_text(json.dumps(dict(
            model=DEFOM_SMALL, iterations=32, scale_iterations=8, precision='float32',
            onnx_sha256=hashlib.sha256(FIXTURE).hexdigest())))
        self.model = None

    def tearDown(self):
        if self.model:
            self.model.close()
        self.directory.cleanup()

    def load(self):
        self.model = DEFOMStereo(self.path, threads=1)
        return self.model

    def test_real_worker_reuses_session_and_retains_signed_offsets(self):
        model = self.load()
        pid = model.process.pid
        left = np.full((35, 46, 3), 150, dtype=np.uint8)
        right = np.full_like(left, 120)
        dl, dr = model.predict_pair(left, right, 8, lambda: False, lambda *_: None)
        np.testing.assert_array_equal(dl, np.full((35, 46), 22, dtype=np.float32))
        np.testing.assert_array_equal(dr, np.full((35, 46), -38, dtype=np.float32))
        self.assertEqual(model.process.pid, pid)
        self.assertTrue(model.process.is_alive())
        self.assertEqual(model.session.get_providers(), ['CPUExecutionProvider'])
        self.assertIn('inference', model.worker_lifetime_memory['stages'])

    def test_cancel_terminates_the_child_and_returns_to_the_caller(self):
        model = self.load()
        model.cancel()
        image = np.zeros((32, 32, 3), dtype=np.uint8)
        with self.assertRaises(ExportCancelled):
            model.predict(image, image, 0, lambda: False)
        self.assertFalse(model.process.is_alive())

    def test_native_child_exit_is_reported_without_killing_parent(self):
        model = self.load()
        model.process.terminate()
        model.process.join(timeout=5)
        image = np.zeros((32, 32, 3), dtype=np.uint8)
        with self.assertRaisesRegex(RuntimeError, 'worker stopped'):
            model.predict(image, image, 0, lambda: False)
        self.assertFalse(model.process.is_alive())

    def test_cancelled_start_does_not_load_the_model(self):
        with self.assertRaises(ExportCancelled):
            DEFOMStereo(self.path, cancel=lambda: True)

    def test_model_load_error_keeps_child_diagnostic_details(self):
        self.path.write_bytes(b'corrupt')
        with self.assertRaises(WorkerError) as caught:
            self.load()
        self.assertIn('beschädigt', str(caught.exception))
        self.assertIn('ValueError', caught.exception.remote_traceback)
