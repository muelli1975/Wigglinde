from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,json,types,unittest
import numpy as np
from wigglinde.igev import IGEVMiddlebury
from wigglinde.las2 import LiteAnyStereo
from wigglinde.models import model_path,model_iterations,IGEV_MODEL

class StereoModelTests(unittest.TestCase):
    def test_middlebury_is_a_separate_fixed_sixteen_iteration_model(self):
        self.assertEqual(model_iterations(IGEV_MODEL),16)
        self.assertEqual(model_path('/app',IGEV_MODEL).parts[-2:],('igev','IGEV_Middlebury_dynamic.onnx'))
        self.assertEqual(model_path('/app',IGEV_MODEL,0).name,'IGEV_Middlebury_mixed.onnx')

    def test_cross_family_graph_is_rejected_before_runtime_creation(self):
        with TemporaryDirectory() as folder:
            p=Path(folder)/'model.onnx';p.write_bytes(b'model')
            p.with_suffix('.json').write_text(json.dumps(dict(model=IGEV_MODEL,iterations=16,onnx_sha256=hashlib.sha256(b'model').hexdigest())))
            fake=types.SimpleNamespace(disable_telemetry_events=lambda:None)
            with patch.dict('sys.modules',onnxruntime=fake):
                with self.assertRaisesRegex(ValueError,'model family'):LiteAnyStereo(p)

    def test_igev_padding_preserves_rgb_and_removes_only_temporary_offset(self):
        import threading
        model=IGEVMiddlebury.__new__(IGEVMiddlebury);model.lock=threading.Lock();model.active=None
        left=np.arange(35*101*3,dtype=np.uint8).reshape(35,101,3);right=left.copy();offset=7
        class Session:
            def run(self,outputs,inputs,run_options):
                self.inputs=inputs
                # The model itself contains its RGB normalization. Adapter must
                # preserve RGB0..255 and return signed disparity in source pixels.
                return [np.full((1,1,*inputs['left'].shape[-2:]),5,np.float32)]
        model.session=Session()
        with patch.dict('sys.modules',onnxruntime=types.SimpleNamespace(RunOptions=types.SimpleNamespace)):
            result=model.predict(left,right,offset,lambda:False)
        np.testing.assert_array_equal(result,np.full((35,101),-2,np.float32))
        np.testing.assert_array_equal(model.session.inputs['left'][0,:,14:49,17:118].transpose(1,2,0),left)
