"""Explicit-device handling must not accept a silent whole-session CPU fallback."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,json,types,unittest
from wigglinde.las2 import LiteAnyStereo

class DeviceSelectionTests(unittest.TestCase):
    def runtime(self,providers):
        self.options=None;self.request=None
        class Session:
            def get_providers(_):return providers
            def disable_fallback(_):pass
        def create(path,sess_options,providers):
            self.options=sess_options;self.request=providers;return Session()
        return types.SimpleNamespace(disable_telemetry_events=lambda:None,get_available_providers=lambda:['CPUExecutionProvider','DmlExecutionProvider'],SessionOptions=types.SimpleNamespace,InferenceSession=create,ExecutionMode=types.SimpleNamespace(ORT_SEQUENTIAL='sequential'))
    def model(self,folder):
        path=Path(folder)/'model.onnx';path.write_bytes(b'test')
        path.with_suffix('.json').write_text(json.dumps({'onnx_sha256':hashlib.sha256(b'test').hexdigest()}))
        return path
    def test_directml_options_and_selected_adapter_are_explicit(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['DmlExecutionProvider','CPUExecutionProvider'])):
            model=LiteAnyStereo(self.model(folder),device_id=2)
            self.assertEqual(self.request[0],('DmlExecutionProvider',{'device_id':2}))
            self.assertFalse(self.options.enable_mem_pattern)
            self.assertEqual(self.options.execution_mode,'sequential')
            self.assertEqual(model.device_id,2)
    def test_provider_initialization_losing_gpu_is_reported(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['CPUExecutionProvider'])):
            with self.assertRaisesRegex(RuntimeError,'GPU_INIT'):
                LiteAnyStereo(self.model(folder),device_id=0)
    def test_cpu_selection_requests_only_cpu(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['CPUExecutionProvider'])):
            LiteAnyStereo(self.model(folder))
            self.assertEqual(self.request,['CPUExecutionProvider'])
