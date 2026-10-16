"""Development-only export of pinned LAS2-M, using the author's ONNX substitutions."""
from pathlib import Path
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import argparse,hashlib,json,subprocess,sys
import numpy as np
import torch

SOURCE='8c97bd4c4da3712c2ac60003a23201dfdb5935f4'
WEIGHTS='c41b61efce9b36e6b8b38b580421cd20cc9e84a47f0f45361767281938f69696'
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--weights',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()==SOURCE
 assert not subprocess.check_output(['git','-C',str(a.source),'status','--porcelain','--','core','export_onnx.py'],text=True).strip()
 assert hashlib.sha256(a.weights.read_bytes()).hexdigest()==WEIGHTS
 torch.set_num_threads(8);torch.manual_seed(17);sys.path.insert(0,str(a.source.resolve()))
 from core.models import build_model,load_model_weights
 m=build_model('las2',model_size='m',fnet_pretrained=False).eval();load_model_weights(m,torch.load(a.weights,map_location='cpu',weights_only=True))
 checks=[]
 with torch.inference_mode():
  for w,h in [(416,128),(448,160)]:
   l=torch.randint(0,256,(1,3,h,w),dtype=torch.float32);r=torch.randint(0,256,(1,3,h,w),dtype=torch.float32)
   checks.append((l.numpy(),r.numpy(),m(l,r,max_disp=192,test_mode=True).numpy()))
 import export_onnx
 original=torch.onnx.export
 def dynamic(*args,**kwargs):
  kwargs['dynamic_axes']={'left':{2:'height',3:'width'},'right':{2:'height',3:'width'},'disparity':{2:'height',3:'width'}}
  return original(*args,**kwargs)
 torch.onnx.export=dynamic;a.output.parent.mkdir(parents=True,exist_ok=True)
 export_onnx.export('las2','m',str(a.weights),416,128,192,str(a.output))
 import onnxruntime as ort
 ort.disable_telemetry_events()
 opt=ort.SessionOptions();opt.intra_op_num_threads=8;s=ort.InferenceSession(str(a.output),sess_options=opt,providers=['CPUExecutionProvider'])
 errors=[float(np.max(np.abs(s.run(None,{'left':l,'right':r})[0]-ref))) for l,r,ref in checks]
 assert max(errors)<0.001,errors
 meta=dict(model='LAS2-M',source_revision=SOURCE,weights_sha256=WEIGHTS,onnx_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),native_max_errors_px=errors,input='RGB float32 0..255; symmetric edge padding to multiple of 32; no normalization outside model',max_disparity=192)
 a.output.with_suffix('.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta),flush=True)
if __name__=='__main__':main()
