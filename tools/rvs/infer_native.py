"""Offline research recovery of LAS2-M maps from saved 960px endpoint PNGs.

Usage: infer_native.py LAS2_SOURCE LAS2_M.pth LEFT.png RIGHT.png SCENE.npz
Requires torch, torchvision, timm. Does not change the application's estimator.
"""
from pathlib import Path
import sys,time,hashlib
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from core.models import build_model,load_model_weights
from wigglinde.stereo import StereoScene
torch.set_num_threads(8)
weights=Path(sys.argv[2]);assert hashlib.sha256(weights.read_bytes()).hexdigest()=='c41b61efce9b36e6b8b38b580421cd20cc9e84a47f0f45361767281938f69696'
model=build_model('las2',model_size='m',fnet_pretrained=False).eval()
load_model_weights(model,torch.load(weights,map_location='cpu',weights_only=True))
left=np.array(Image.open(sys.argv[3]).convert('RGB'));right=np.array(Image.open(sys.argv[4]).convert('RGB'))
assert left.shape==right.shape
def infer(a,b):
 a=np.pad(a,((0,0),(64,0),(0,0)),mode='edge');b=np.pad(b,((0,0),(0,64),(0,0)),mode='edge')
 h,w=a.shape[:2];ph=(-h)%32;pw=(-w)%32;pad=(pw//2,pw-pw//2,ph//2,ph-ph//2)
 def tensor(x):return F.pad(torch.from_numpy(x.copy()).permute(2,0,1).float()[None],pad,mode='replicate')
 start=time.perf_counter()
 with torch.inference_mode():d=model(tensor(a),tensor(b),max_disp=192,test_mode=True).numpy().squeeze()
 print('native inference seconds',time.perf_counter()-start,flush=True)
 return (d[pad[2]:pad[2]+h,pad[0]+64:pad[0]+w]-64).copy()
dl=infer(left,right);dr=infer(right[:,::-1],left[:,::-1])[:,::-1].copy()
StereoScene(left,right,dl,dr).save(sys.argv[5])
