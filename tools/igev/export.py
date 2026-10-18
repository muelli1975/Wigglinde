"""Build-only IGEV++ Middlebury export; no PyTorch/timm dependency at runtime."""
from pathlib import Path
from types import SimpleNamespace
import argparse,hashlib,json,os,subprocess,sys,time
os.environ['ORT_DISABLE_TELEMETRY']='1'
import numpy as np
import torch
import torch.nn.functional as F

SOURCE='099dec97989780d151700459c682df1cc2c18e88'
WEIGHTS='eecddfa4549dc6180ce96e7ed8bf24a0bb0d702d5e747623eac54abed1fd7579'

def configuration():
    return SimpleNamespace(hidden_dims=[128]*3,corr_levels=2,corr_radius=4,n_downsample=2,n_gru_layers=3,max_disp=768,s_disp_range=48,m_disp_range=96,l_disp_range=192,s_disp_interval=1,m_disp_interval=2,l_disp_interval=4,mixed_precision=False,precision_dtype='float32')

def correlation_volume(left,right,maxdisp,groups):
    # Exact zero-padded horizontal shifts. Unlike traced slice assignment, every
    # slice retains image width even for maxdisp > feature width.
    b,c,h,w=left.shape
    padded=F.pad(right,(maxdisp-1,0))
    costs=[]
    for disparity in range(maxdisp):
        shifted=padded[:,:,:,maxdisp-1-disparity:maxdisp-1-disparity+w]
        costs.append((left*shifted).reshape(b,groups,c//groups,h,w).mean(dim=2))
    return torch.stack(costs,dim=2).contiguous()

def upsample(depth,weights):
    # Same 3x3 zero-padded neighborhood as F.unfold; exportable identity Conv.
    b,c,h,w=depth.shape
    kernel=torch.eye(9,dtype=depth.dtype,device=depth.device).reshape(9,1,3,3)
    values=F.conv2d(depth,kernel,padding=1)
    values=F.interpolate(values,(h*4,w*4),mode='nearest')
    return (values*weights).sum(dim=1,keepdim=True)

def load(source,weights):
    assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==SOURCE
    assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=no','--','core'],text=True).strip()
    assert hashlib.sha256(weights.read_bytes()).hexdigest()==WEIGHTS
    import timm
    if timm.__version__!='0.5.4':raise ValueError('Export requires isolated timm 0.5.4')
    original=timm.create_model
    def offline(*args,**kwargs):
        kwargs['pretrained']=False
        return original(*args,**kwargs)
    timm.create_model=offline
    sys.path.insert(0,str(source.resolve()))
    from core.igev_stereo import IGEVStereo
    try:model=IGEVStereo(configuration()).eval()
    finally:timm.create_model=original
    state=torch.load(weights,map_location='cpu',weights_only=True)
    model.load_state_dict({k.removeprefix('module.'):v for k,v in state.items()},strict=True)
    return model

class Export(torch.nn.Module):
    def __init__(self,model):super().__init__();self.model=model
    def forward(self,left,right):return self.model(left,right,iters=16,test_mode=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--weights',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    torch.set_num_threads(8);torch.manual_seed(19)
    model=load(a.source,a.weights)
    from core import igev_stereo,submodule
    # Compare author math before replacing export-incompatible operators.
    cases=[]
    with torch.inference_mode():
        for width,height in [(416,128),(448,160)]:
            texture=torch.randint(0,256,(1,3,height,width+8),dtype=torch.float32)
            l=texture[:,:,:,:width].contiguous();r=texture[:,:,:,8:].contiguous()
            d=model(l,r,iters=16,test_mode=True)
            cases.append((l.numpy(),r.numpy(),d.numpy()))
    igev_stereo.build_gwc_volume=correlation_volume
    igev_stereo.context_upsample=upsample
    submodule.build_gwc_volume=correlation_volume;submodule.context_upsample=upsample
    wrapped=Export(model).eval();a.output.parent.mkdir(parents=True,exist_ok=True)
    with torch.inference_mode():
        substitution_errors=[]
        for l,r,ref in cases:
            actual=wrapped(torch.from_numpy(l),torch.from_numpy(r)).numpy()
            np.testing.assert_allclose(actual,ref,rtol=1e-4,atol=1e-4)
            substitution_errors.append(float(np.max(np.abs(actual-ref))))
        print('Native operator substitution verified; exporting 16 iterations',flush=True)
        torch.onnx.export(wrapped,(torch.from_numpy(cases[0][0]),torch.from_numpy(cases[0][1])),str(a.output),opset_version=18,input_names=['left','right'],output_names=['disparity'],dynamic_axes={'left':{2:'height',3:'width'},'right':{2:'height',3:'width'},'disparity':{2:'height',3:'width'}},do_constant_folding=True,dynamo=False)
    refs=a.output.with_suffix('.validation.npz');np.savez_compressed(refs,**{f'{i}_{key}':value for i,row in enumerate(cases) for key,value in zip(('left','right','disparity'),row)})
    metadata=dict(native_operator_errors_px=substitution_errors,model='IGEV++ Middlebury',source_revision=SOURCE,weights_sha256=WEIGHTS,onnx_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),precision='float32',iterations=16,max_disparity=768,input='RGB Float32 0..255; internal normalization to -1..1; symmetric edge padding to multiple of 32; reversible matching offset',export_substitutions=['zero-padded correlation volume without slice assignment','identity Conv equivalent to F.unfold'])
    a.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata),flush=True)
if __name__=='__main__':main()
