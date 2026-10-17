"""Explicit development test: serial/parallel float32 identity, order and cancellation."""
import argparse,json,subprocess,tempfile,time,threading
from pathlib import Path
import numpy as np
from wigglinde.rvs import RVSRenderer
from wigglinde.blending_options import BlendingOptions
from wigglinde.stereo import StereoScene
from wigglinde.wiggle_export import ExportCancelled

def check(executable,output):
    executable=Path(executable).resolve();reports=[]
    with tempfile.TemporaryDirectory(prefix='wigglinde_parallel_') as temporary:
        root=Path(temporary)
        for width,height in [(320,160),(323,161)]:
            rng=np.random.default_rng(81);left=rng.integers(0,256,(height,width,3),dtype=np.uint8)
            right=np.roll(left,-8,axis=1);depth=np.full((height,width),4,np.float32)
            depth[height//4:3*height//4,width//3:2*width//3]=16
            # Discontinuities, negative disparity and unequal/non-square sizes.
            depth[:height//4]=-2
            scene=StereoScene(left,right,depth,np.roll(depth,-8,axis=1))
            signatures=[]
            for blend in [BlendingOptions(),BlendingOptions(high_factor=2.),BlendingOptions(high_factor=8.),BlendingOptions(method='Simple'),BlendingOptions(method='Simple',simple_factor=2.)]:
                renderer=RVSRenderer(executable,scene,[0,.000001,.25,.5,.75,.999999,1],root/f'{width}_{blend.method}_{blend.high_factor}_{blend.simple_factor}',blending=blend)
                reference=None;times=[]
                for label,args in [('serial',[]),('two',['2','1']),('four',['4','1']),('repeat_four',['4','1'])]:
                    metrics=renderer.work/(label+'.json');begin=time.perf_counter()
                    p=subprocess.run([str(executable),str(renderer.work/'config.json'),str(metrics),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
                    if p.returncode:raise AssertionError(p.stderr.decode(errors='replace')[-2500:])
                    assert len(p.stdout)==width*height*3*4*7
                    if reference is None:reference=p.stdout
                    else:assert p.stdout==reference,(width,height,label,'float32 output/order differs')
                    assert np.isfinite(np.frombuffer(p.stdout,dtype=np.float32)).all()
                    times.append(dict(mode=label,seconds=time.perf_counter()-begin,metrics=json.loads(metrics.read_text())))
                reports.append(dict(size=[width,height],blending=blend.rvs_config(),bitwise_equal=True,runs=times))
                signatures.append(reference)
            assert len(set(signatures))==len(signatures),'Blending factors/modes did not reach native renderer'
        # Cancellation stops the single backend, including all native workers.
        renderer=RVSRenderer(executable,scene,np.linspace(0,1,101),root/'cancel')
        renderer.schedule.update(workers=4,threads_per_view=1)
        event=threading.Event();frames=renderer.frames(event.is_set)
        next(frames);process=renderer.process;begin=time.perf_counter();event.set();renderer.cancel()
        try:
            next(frames)
            raise AssertionError('Cancellation ignored')
        except ExportCancelled:pass
        finally:frames.close()
        assert process.poll() is not None and renderer.process is None
        cancel_seconds=time.perf_counter()-begin
        # An initialization error is reported without a hung pipe/process.
        bad=subprocess.run([str(executable),str(root/'missing.json'),str(root/'failed.json'),'4','1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
        assert bad.returncode!=0
    result=dict(status='passed',cases=reports,cancellation_seconds=cancel_seconds,error_exit=True)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='passed',bitwise_equal=True,cancellation_seconds=cancel_seconds)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--renderer',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();check(args.renderer,args.output)
