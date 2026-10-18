"""Build-time native/ONNX parity checks, not per-photo product validation."""
from pathlib import Path
import argparse,json,time
import numpy as np
import onnx,onnxruntime as ort

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--photo-reference',type=Path);a=p.parse_args()
    ort.disable_telemetry_events();onnx.checker.check_model(str(a.model),full_check=True)
    options=ort.SessionOptions();options.intra_op_num_threads=8
    start=time.monotonic();session=ort.InferenceSession(str(a.model),sess_options=options,providers=['CPUExecutionProvider']);load_seconds=time.monotonic()-start
    reference=np.load(a.model.with_suffix('.validation.npz'));cases=[]
    for i in range(2):
        feed={k:reference[f'{i}_{k}'] for k in ('left','right')};expected=reference[f'{i}_disparity'];start=time.monotonic()
        value=session.run(None,feed)[0];error=np.abs(value-expected)
        row=dict(size=list(value.shape[-2:][::-1]),seconds=time.monotonic()-start,max_error_px=float(error.max()),mean_error_px=float(error.mean()),p99_error_px=float(np.quantile(error,.99)),finite=bool(np.isfinite(value).all()))
        print(json.dumps(row),flush=True);cases.append(row)
        if not row['finite'] or value.shape!=expected.shape:raise ValueError('Invalid ONNX output')
        np.testing.assert_allclose(value,expected,rtol=.001,atol=.01)
    report=dict(status='passed',iterations=16,providers=session.get_providers(),load_seconds=load_seconds,native_onnx_cases=cases,physical_gpu_validated=False)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2))
    if a.photo_reference:
        from wigglinde.igev import IGEVMiddlebury
        from wigglinde.stereo import StereoScene
        model=IGEVMiddlebury.__new__(IGEVMiddlebury);model.session=session
        import threading
        model.lock=threading.Lock();model.active=None
        ref=np.load(a.photo_reference);arrays={};photo=[]
        for eye in ('left','right'):
            l,r=(ref['left'],ref['right']) if eye=='left' else (ref['right'][:,::-1],ref['left'][:,::-1])
            start=time.monotonic();d=model.predict(l,r,68,lambda:False)
            if eye=='right':d=d[:,::-1].copy()
            error=np.abs(d-ref[eye+'_disparity']);arrays[eye+'_disparity']=d
            row=dict(eye=eye,seconds=time.monotonic()-start,max_error_px=float(error.max()),mean_error_px=float(error.mean()),p99_error_px=float(np.quantile(error,.99)),rail_p99_error_px=float(np.quantile(error[510:],.99)))
            print(json.dumps(row),flush=True);photo.append(row)
        report['photo_comparison']=photo;a.report.write_text(json.dumps(report,indent=2))
        StereoScene(ref['left'],ref['right'],arrays['left_disparity'],arrays['right_disparity']).save(a.report.with_suffix('.scene.npz'))
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()
