"""Prepare mounted LAS2 disparities for RVS, preserving signed screen disparity.

With B=1 and delta=cxL-cxR=-64: Z=f/(d+64), C(t)=(0,-t,0),
cx(t)=w/2+64*t. Hence RVS projects xL-t*d / xR+(1-t)*d.
No image alignment, crop, convergence change, or metric calibration is applied.
"""
from pathlib import Path
import json,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from wigglinde.stereo import StereoScene
from wigglinde.render import _linear

def prepare(scene_path,folder,positions,precision=2):
 folder=Path(folder).resolve();folder.mkdir(exist_ok=True,parents=True)
 scene=StereoScene.load(scene_path);h,w=scene.left.shape[:2]
 depths=[np.float32(w)/(d+64) for d in [scene.left_disparity,scene.right_disparity]]
 for d in depths:assert np.isfinite(d).all() and (d>0).all()
 for i,(rgb,z) in enumerate(zip([scene.left,scene.right],depths)):
  _linear(rgb).tofile(folder/f'color{i}.rgb');z.tofile(folder/f'depth{i}.z')
 def camera(name,t):return dict(Name=name,Position=[0,-float(t),0],Rotation=[0,0,0],Depthmap=1,Background=0,Depth_range=[.01,999],Resolution=[w,h],Projection='Perspective',Focal=[w,w],Principle_point=[w/2+64*float(t),h/2],BitDepthColor=8,BitDepthDepth=16,ColorSpace='YUV420',DepthColorSpace='YUV400',HasInvalidDepth=False)
 cameras=[camera('left',0),camera('right',1)]+[camera(f'v{i}',t) for i,t in enumerate(positions)]
 (folder/'cameras.json').write_text(json.dumps(dict(Version='2.0',cameras=cameras)))
 cfg=dict(Version='2.0',InputCameraParameterFile=str(folder/'cameras.json'),VirtualCameraParameterFile=str(folder/'cameras.json'),InputCameraNames=['left','right'],VirtualCameraNames=[f'v{i}' for i in range(len(positions))],ViewImageNames=[str(folder/f'color{i}.rgb') for i in range(2)],DepthMapNames=[str(folder/f'depth{i}.z') for i in range(2)],StartFrame=0,NumberOfFrames=1,Precision=precision,ColorSpace='RGB',ViewSynthesisMethod='Triangles',BlendingMethod='Multispectral',BlendingLowFreqFactor=1.,BlendingHighFreqFactor=4.)
 (folder/'config.json').write_text(json.dumps(cfg,indent=2));(folder/'positions.json').write_text(json.dumps(positions))
 return scene
if __name__=='__main__':prepare(sys.argv[1],sys.argv[2],[0.,1e-6,.5,1.-1e-6,1.])
