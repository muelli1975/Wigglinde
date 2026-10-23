"""Explicit-device handling must not accept a silent whole-session CPU fallback."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,json,types,unittest
from wigglinde.las2 import LiteAnyStereo
from wigglinde.models import model_path,DEFAULT_MODEL,MODELS,IGEV_MODEL,DEFOM_SMALL,DEFOM_LARGE

class DeviceSelectionTests(unittest.TestCase):
    def runtime(self,providers):
        self.options=None;self.request=None
        class Session:
            def get_providers(_):return providers
            def disable_fallback(_):pass
        def create(path,sess_options,providers):
            self.options=sess_options;self.request=providers;return Session()
        return types.SimpleNamespace(disable_telemetry_events=lambda:None,get_available_providers=lambda:['CPUExecutionProvider','DmlExecutionProvider'],SessionOptions=types.SimpleNamespace,InferenceSession=create,ExecutionMode=types.SimpleNamespace(ORT_SEQUENTIAL='sequential'))
    def model(self,folder,precision='float32'):
        path=Path(folder)/'model.onnx';path.write_bytes(b'test')
        path.with_suffix('.json').write_text(json.dumps({'onnx_sha256':hashlib.sha256(b'test').hexdigest(),'precision':precision,'model':'LAS2-H','iterations':4}))
        return path
    def test_directml_options_and_selected_adapter_are_explicit(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['DmlExecutionProvider','CPUExecutionProvider'])):
            model=LiteAnyStereo(self.model(folder,'mixed_float16_float32'),device_id=2)
            self.assertEqual(self.request[0],('DmlExecutionProvider',{'device_id':2}))
            self.assertFalse(self.options.enable_mem_pattern)
            self.assertEqual(self.options.execution_mode,'sequential')
            self.assertEqual(model.device_id,2)
    def test_provider_initialization_losing_gpu_is_reported(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['CPUExecutionProvider'])):
            with self.assertRaisesRegex(RuntimeError,'GPU_INIT'):
                LiteAnyStereo(self.model(folder,'mixed_float16_float32'),device_id=0)
    def test_cpu_selection_requests_only_cpu(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['CPUExecutionProvider'])):
            LiteAnyStereo(self.model(folder))
            self.assertEqual(self.request,['CPUExecutionProvider'])

    def test_model_paths_distinguish_cpu_and_gpu_zero(self):
        self.assertEqual(model_path('/app',DEFAULT_MODEL).name,'LAS2_H_dynamic.onnx')
        self.assertEqual(model_path('/app',DEFAULT_MODEL,0).name,'LAS2_H_mixed.onnx')

    def test_wrong_model_precision_is_rejected_before_session_creation(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['DmlExecutionProvider','CPUExecutionProvider'])):
            with self.assertRaisesRegex(ValueError,'incorrect model precision'):
                LiteAnyStereo(self.model(folder),device_id=0)
            self.assertIsNone(self.request)

    def test_eight_iteration_graph_is_rejected(self):
        with TemporaryDirectory() as folder,patch.dict('sys.modules',onnxruntime=self.runtime(['CPUExecutionProvider'])):
            path=self.model(folder)
            meta=json.loads(path.with_suffix('.json').read_text());meta['iterations']=8
            path.with_suffix('.json').write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError,'iteration count'):LiteAnyStereo(path)
            self.assertIsNone(self.request)

    def test_all_selected_models_have_separate_cpu_and_gpu_graphs(self):
        for label in MODELS:
            with self.subTest(model=label):
                stem={IGEV_MODEL:'IGEV_Middlebury',DEFOM_SMALL:'DEFOM_S',DEFOM_LARGE:'DEFOM_L'}.get(label,label.replace('-','_'))
                self.assertEqual(model_path('/app',label).name,stem+'_dynamic.onnx')
                self.assertEqual(model_path('/app',label,0).name,stem+'_mixed.onnx')
