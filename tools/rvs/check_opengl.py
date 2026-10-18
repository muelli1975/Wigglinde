"""Development-only GL color/geometry/repeat/cancel checks on the real backend."""
import argparse,json,tempfile,threading,time
from pathlib import Path
import numpy as np
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene
from wigglinde.wiggle_export import ExportCancelled

def check(executable,output,allow_unavailable=False):
    reports=[]
    with tempfile.TemporaryDirectory(prefix='wigglinde_gl_') as folder:
        root=Path(folder)
        for width,height in [(320,160),(323,161)]:
            y,x=np.mgrid[:height,:width+8]
            texture=np.stack([.1+.5*x/(width+8),.2+.4*y/height,.3+.1*np.sin(x/20)],axis=-1)
            texture=np.rint(texture*255).astype(np.uint8)
            left=texture[:,:width];right=texture[:,8:width+8]
            disparity=np.full((height,width),8,np.float32)
            scene=StereoScene(left,right,disparity,disparity)
            positions=[0,.25,.5,.75,1]
            renderer=RVSRenderer(executable,scene,positions,root/str(width),backend='opengl')
            begin=time.perf_counter()
            try:frames=list(renderer.frames(lambda:False))
            except RuntimeError as error:
                if not allow_unavailable or 'OPENGL_INIT:' not in str(error):raise
                result=dict(status='unavailable',reason=str(error),physical_gpu_validated=False)
                Path(output).parent.mkdir(parents=True,exist_ok=True);Path(output).write_text(json.dumps(result,indent=2));print(json.dumps(result));return result
            seconds=time.perf_counter()-begin
            errors=[]
            for frame,t in zip(frames,positions):
                expected=texture[:,round(t*8):round(t*8)+width]
                error=np.abs(frame[8:-8,16:-16].astype(float)-expected[8:-8,16:-16])
                # Smooth analytic plane: catch blank frames, RGB swaps, flips and
                # wrong shift direction; allow upstream subpixel raster/filter differences.
                assert np.max(error)<6,(width,t,float(error.max()))
                errors.append(float(error.mean()))
            repeat=list(renderer.frames(lambda:False))
            assert all(np.array_equal(a,b) for a,b in zip(frames,repeat))
            assert renderer.metrics['backend']=='opengl' and renderer.metrics['parallel_workers']==1
            reports.append(dict(size=[width,height],seconds=seconds,mean_errors_8bit=errors,repeat_identical=True,metrics=renderer.metrics))
        event=threading.Event();renderer=RVSRenderer(executable,scene,np.linspace(0,1,101),root/'cancel',backend='opengl')
        frames=renderer.frames(event.is_set);next(frames);process=renderer.process;event.set();renderer.cancel()
        try:next(frames);raise AssertionError('Cancellation ignored')
        except ExportCancelled:pass
        finally:frames.close()
        assert process.poll() is not None
    result=dict(status='passed',cases=reports,cancellation=True,physical_gpu_validated=False)
    Path(output).parent.mkdir(parents=True,exist_ok=True);Path(output).write_text(json.dumps(result,indent=2));print(json.dumps(result));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--renderer',required=True);parser.add_argument('--output',required=True);parser.add_argument('--allow-unavailable',action='store_true');args=parser.parse_args()
    check(Path(args.renderer).resolve(),args.output,args.allow_unavailable)
