"""Explicit photo A/B test; changes only RVS Precision, never application defaults.

Scene NPZ: left/right uint8 RGB, dl/dr float32 disparity, offset scalar.
Both variants use identical maps, positions, workers and inner threads.
Retains lossless views for inspection and exports normal five-cycle MP4s.
"""
import argparse,hashlib,io,json,os,sys,time
from pathlib import Path
import numpy as np
from PIL import Image
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene
from wigglinde.export_options import WiggleOptions,camera_weight,cycle_index
from wigglinde.wiggle_export import _run_ffmpeg

def encode_cached(frames_dir,variant,clip,options):
    sequence=variant/'sequence';sequence.mkdir(exist_ok=True)
    for i in range(options.frame_count):
        dest=sequence/f'{i:03d}.png'
        if not dest.exists():os.link(frames_dir/f'{cycle_index(i,options.frame_count):03d}.png',dest)
    video_filter=('pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black,format=gbrp,'
        'zscale=matrixin=gbr:primariesin=709:transferin=iec61966-2-1:rangein=full:'
        'matrix=709:primaries=709:transfer=709:range=limited,format=yuv420p')
    cycle=variant/'cycle.mp4';begin=time.perf_counter()
    _run_ffmpeg(['-framerate',str(options.fps),'-i',str(sequence/'%03d.png'),'-an','-vf',video_filter,
        '-c:v','libx264','-crf','18','-preset','slow','-pix_fmt','yuv420p',
        '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv',str(cycle)],variant/'encode.log',lambda:False)
    _run_ffmpeg(['-stream_loop','4','-i',str(cycle),'-map','0:v:0','-an','-c:v','copy','-movflags','+faststart',str(clip)],variant/'repeat.log',lambda:False)
    return dict(encode_or_copy_seconds=time.perf_counter()-begin)

def compare(args):
    root=Path(args.output).resolve();root.mkdir(parents=True,exist_ok=True)
    executable=Path(args.renderer).resolve();scene_path=Path(args.scene).resolve()
    data=np.load(scene_path)
    scene=StereoScene(data['left'],data['right'],data['dl'],data['dr'])
    options=WiggleOptions();positions=[camera_weight(i,options.frame_count) for i in range(options.frame_count//2+1)]
    # Linux-only independent native RSS measurement. The wrapper adds no pipe:
    # the native child's stdout is inherited unchanged by the adapter's reader.
    measured_executable=executable
    if sys.platform.startswith('linux'):
        measured_executable=root/'measure_native.py'
        measured_executable.write_text(f'''#!{sys.executable}
import json,pathlib,resource,subprocess,sys
p=subprocess.run([{str(executable)!r},*sys.argv[1:]])
pathlib.Path(sys.argv[2]).with_suffix('.rss.json').write_text(json.dumps(dict(peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)))
sys.exit(p.returncode)
''',encoding='utf-8')
        measured_executable.chmod(0o700)
    reports=[]
    for precision in map(int,args.order.split(',')):
        assert precision in (1,2)
        variant=root/f'precision{precision}';frames_dir=variant/'frames';frames_dir.mkdir(parents=True,exist_ok=True)
        renderer=RVSRenderer(measured_executable,scene,positions,variant/'rvs',float(data['offset']))
        renderer.schedule.update(workers=args.workers,threads_per_view=args.threads_per_view)
        config_path=renderer.work/'config.json';config=json.loads(config_path.read_text(encoding='utf-8'))
        config['Precision']=precision;config_path.write_text(json.dumps(config,ensure_ascii=False),encoding='utf-8')
        started=time.perf_counter();count=0
        if args.reuse_views and precision!=args.rerender and (frames_dir/f'{len(positions)-1:03d}.png').exists():
            count=len(list(frames_dir.glob('*.png')))
            renderer.metrics=json.loads((renderer.work/'metrics.json').read_text())
            materialize=None
        else:
            frames=renderer.frames(lambda:False)
            try:
                for i,rgb in enumerate(frames):
                    buffer=io.BytesIO();Image.fromarray(rgb).save(buffer,format='PNG',compress_level=6)
                    payload=buffer.getvalue();dest=frames_dir/f'{i:03d}.png'
                    assert dest.write_bytes(payload)==len(payload)
                    count+=1
            finally:frames.close()
            materialize=time.perf_counter()-started
        assert count==len(positions)
        clip=root/f'{scene_path.stem}_precision{precision}.mp4'
        export_times=encode_cached(frames_dir,variant,clip,options)
        rss_path=(renderer.work/'metrics.json').with_suffix('.rss.json')
        report=dict(precision=precision,materialize_seconds=materialize,metrics=renderer.metrics,
                    clip=clip.name,frames=count,export_from_cached_views=export_times,
                    peak_rss_kib=json.loads(rss_path.read_text())['peak_rss_kib'] if rss_path.exists() else None)
        reports.append(report);print(json.dumps(dict(scene=scene_path.stem,**report)),flush=True)
    assert sorted(r['precision'] for r in reports)==[1,2]
    # Difference to P2 is descriptive, not a quality score or ground truth.
    errors=[];previous=None;temporal=[]
    for i in range(len(positions)):
        with Image.open(io.BytesIO((root/'precision1/frames'/f'{i:03d}.png').read_bytes())) as image:a=np.array(image,dtype=np.int16)
        with Image.open(io.BytesIO((root/'precision2/frames'/f'{i:03d}.png').read_bytes())) as image:b=np.array(image,dtype=np.int16)
        delta=a-b;absolute=np.abs(delta)
        errors.append(dict(index=i,position=positions[i],mae=float(absolute.mean()),
                           p99=float(np.percentile(absolute,99)),fraction_pixels_max_channel_over8=float((absolute.max(axis=2)>8).mean())))
        if previous is not None:temporal.append(float(np.abs(delta-previous).mean()))
        previous=delta
    report=dict(scene=scene_path.stem,scene_sha256=hashlib.sha256(scene_path.read_bytes()).hexdigest(),
                eye_size=list(scene.left.shape[1::-1]),model='LAS2-H',iterations=4,model_precision='float32',
                workers=args.workers,threads_per_view=args.threads_per_view,order=args.order,
                output_options=options.to_settings(),runs=reports,differences=errors,
                temporal_difference_mae_mean=float(np.mean(temporal)),
                limitation='No intermediate-view ground truth. Differences do not establish which variant is better. Native Linux RSS; timings are not a Windows hardware forecast.')
    (root/'comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--renderer',required=True)
    p.add_argument('--output',required=True);p.add_argument('--workers',type=int,default=3)
    p.add_argument('--threads-per-view',type=int,default=2);p.add_argument('--order',default='2,1')
    p.add_argument('--reuse-views',action='store_true',help='Explicitly reuse completed views from this same test scene')
    p.add_argument('--rerender',type=int,choices=(1,2),help='Repeat this variant while reusing the other variant')
    args=p.parse_args();assert args.workers>0 and args.threads_per_view>0;compare(args)
