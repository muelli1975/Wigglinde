"""RVS process adapter. Stream one frame at a time; no per-frame verification."""
from pathlib import Path
import json,os,subprocess,threading
import numpy as np
from .render import _linear,_srgb
from .wiggle_export import ExportCancelled,check_cancelled

class RVSRenderer:
    def __init__(self,executable,scene,positions,work,matching_offset=64):
        self.executable=Path(executable);self.scene=scene;self.positions=positions;self.work=Path(work)
        self.work.mkdir(parents=True,exist_ok=True);self.process=None
        if not self.executable.is_file():raise FileNotFoundError(f'Der RVS-Renderer fehlt: {self.executable}')
        h,w=scene.left.shape[:2]
        bias=max(float(matching_offset),1-float(min(scene.left_disparity.min(),scene.right_disparity.min())))
        self.bias=bias
        for i,(rgb,d) in enumerate(zip((scene.left,scene.right),(scene.left_disparity,scene.right_disparity))):
            _linear(rgb).tofile(self.work/f'color{i}.rgb')
            (np.float32(w)/(d+bias)).astype(np.float32).tofile(self.work/f'depth{i}.z')
        def camera(name,t):return dict(Name=name,Position=[0,-float(t),0],Rotation=[0,0,0],Depthmap=1,Background=0,Depth_range=[.01,999],Resolution=[w,h],Projection='Perspective',Focal=[w,w],Principle_point=[w/2+bias*float(t),h/2],BitDepthColor=8,BitDepthDepth=16,ColorSpace='YUV420',DepthColorSpace='YUV400',HasInvalidDepth=False)
        cameras=[camera('left',0),camera('right',1)]+[camera(f'v{i}',t) for i,t in enumerate(positions)]
        cp=self.work/'cameras.json';cp.write_text(json.dumps(dict(Version='2.0',cameras=cameras)),encoding='utf-8')
        config=dict(Version='2.0',InputCameraParameterFile=str(cp),VirtualCameraParameterFile=str(cp),InputCameraNames=['left','right'],VirtualCameraNames=[f'v{i}' for i in range(len(positions))],ViewImageNames=[str(self.work/f'color{i}.rgb') for i in range(2)],DepthMapNames=[str(self.work/f'depth{i}.z') for i in range(2)],StartFrame=0,NumberOfFrames=1,Precision=2,ColorSpace='RGB',ViewSynthesisMethod='Triangles',BlendingMethod='Multispectral',BlendingLowFreqFactor=1.,BlendingHighFreqFactor=4.)
        (self.work/'config.json').write_text(json.dumps(config,ensure_ascii=False),encoding='utf-8')

    def cancel(self):
        p=self.process
        if p is not None and p.poll() is None:
            try:p.kill()
            except OSError:pass

    def frames(self,cancel):
        h,w=self.scene.left.shape[:2];size=h*w*3*4
        flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
        with (self.work/'rvs.log').open('wb') as log:
            self.process=subprocess.Popen([str(self.executable),str(self.work/'config.json')],stdout=subprocess.PIPE,stderr=log,creationflags=flags)
            p=self.process
            try:
                for index in range(len(self.positions)):
                    check_cancelled(cancel);data=bytearray(size);view=memoryview(data);received=0
                    while received<size:
                        check_cancelled(cancel)
                        n=p.stdout.readinto(view[received:min(size,received+4*1024*1024)])
                        if not n:
                            check_cancelled(cancel)
                            raise RuntimeError('RVS: '+(self.work/'rvs.log').read_text(errors='replace')[-1500:])
                        received+=n
                    yield _srgb(np.frombuffer(data,dtype=np.float32).reshape(h,w,3))
                if p.wait():raise RuntimeError('RVS: '+(self.work/'rvs.log').read_text(errors='replace')[-1500:])
            finally:
                self.cancel();p.stdout.close();p.wait();self.process=None
