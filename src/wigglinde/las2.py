"""Local LAS2 M/L/H ONNX inference; explicit CPU/DirectML, signed mounted disparity."""
from pathlib import Path
import hashlib,json,threading
import numpy as np
from .wiggle_export import ExportCancelled

class LiteAnyStereo:
    def __init__(self,model_path,threads=None,device_id=None):
        import onnxruntime as ort
        ort.disable_telemetry_events()
        path=Path(model_path)
        if not path.is_file():raise FileNotFoundError(f"Die Modelldatei fehlt: {path}")
        meta=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=meta['onnx_sha256']:
            raise ValueError('Die LAS2-Modelldatei ist beschädigt. Bitte das Testpaket erneut entpacken.')
        settings=ort.SessionOptions()
        if threads:settings.intra_op_num_threads=threads
        self.model_name=meta.get('model');self.device_id=device_id
        if device_id is None:
            self.session=ort.InferenceSession(str(path),sess_options=settings,providers=['CPUExecutionProvider'])
        else:
            # Official DirectML constraints: sequential execution, no memory pattern.
            # Keep the same float32 model; no quantization or image-size change.
            if 'DmlExecutionProvider' not in ort.get_available_providers():
                raise RuntimeError('GPU_INIT: DirectML is not available in this runtime.')
            settings.enable_mem_pattern=False
            settings.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
            try:
                self.session=ort.InferenceSession(str(path),sess_options=settings,providers=[('DmlExecutionProvider',{'device_id':int(device_id)}),'CPUExecutionProvider'])
                # ORT may retry CPU on provider initialization errors. Never accept
                # a session that lost the explicitly selected GPU provider.
                if 'DmlExecutionProvider' not in self.session.get_providers():
                    raise RuntimeError('DirectML initialization failed.')
                self.session.disable_fallback()
            except Exception as error:
                raise RuntimeError('GPU_INIT: '+str(error)) from error
        self.active=None;self.lock=threading.Lock()

    def cancel(self):
        with self.lock:
            if self.active is not None:self.active.terminate=True

    def predict(self,left,right,offset,cancel):
        import onnxruntime as ort
        if cancel():raise ExportCancelled()
        h,w=left.shape[:2];padw=(-(w+offset))%32;padh=(-h)%32
        pads=((padh//2,padh-padh//2),(padw//2,padw-padw//2),(0,0))
        a=np.pad(left,((0,0),(offset,0),(0,0)),mode='edge')
        b=np.pad(right,((0,0),(0,offset),(0,0)),mode='edge')
        def tensor(x):return np.ascontiguousarray(np.pad(x,pads,mode='edge').transpose(2,0,1)[None],dtype=np.float32)
        inputs={'left':tensor(a),'right':tensor(b)};run=ort.RunOptions()
        with self.lock:self.active=run
        try:
            if cancel():raise ExportCancelled()
            d=self.session.run(None,inputs,run_options=run)[0].squeeze()
        except Exception:
            if cancel():raise ExportCancelled() from None
            raise
        finally:
            with self.lock:self.active=None
        return (d[pads[0][0]:pads[0][0]+h,pads[1][0]+offset:pads[1][0]+offset+w]-offset).copy()

    def predict_pair(self,left,right,offset,cancel,progress):
        progress('Tiefenkarte links berechnen',0.)
        dl=self.predict(left,right,offset,cancel)
        progress('Tiefenkarte rechts berechnen',.18)
        dr=self.predict(right[:,::-1],left[:,::-1],offset,cancel)[:,::-1].copy()
        return dl,dr
