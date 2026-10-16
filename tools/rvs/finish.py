"""Create the one-photo comparison and report; no product renderer changes."""
from pathlib import Path
import sys,json,re,subprocess,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from wigglinde.stereo import StereoScene
from wigglinde.render import _srgb,ViewRenderer
root=Path(sys.argv[1]).resolve();work=root/'rvs-check';out=work/'Ergebnis';out.mkdir(exist_ok=True)
scene=StereoScene.load(work/'scene.npz');h,w=scene.left.shape[:2]
old=[];new=[]
for i in range(31):
 old.append(np.array(Image.open(work/f'baseline/{i:03d}.png').convert('RGB')))
 new.append(_srgb(np.fromfile(work/f'animation/rvs_{i}.rgb',np.float32).reshape(h,w,3)))
 Image.fromarray(new[-1]).save(work/f'animation/{i:03d}.png')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
def pair(a,b):
 canvas=Image.new('RGB',(2*w,h+40),'#181818');canvas.paste(Image.fromarray(a),(0,40));canvas.paste(Image.fromarray(b),(w,40))
 d=ImageDraw.Draw(canvas);d.text((16,7),'Bisheriger Renderer',font=font,fill='white');d.text((w+16,7),'RVS CPU · 2-fache Abtastung · Multispectral',font=font,fill='white');return np.array(canvas)
seq=[min(i,60-i) for i in range(60)]*5
vf='format=gbrp,zscale=matrixin=gbr:primariesin=709:transferin=iec61966-2-1:rangein=full:matrix=709:primaries=709:transfer=709:range=limited,format=yuv420p'
def encode(name,width,height,getframe):
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r','30','-i','pipe:0','-vf',vf,'-c:v','libx264','-crf','18','-preset','slow','-movflags','+faststart',str(out/name)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in seq:p.stdin.write(getframe(i).tobytes())
 p.stdin.close();assert p.wait()==0
 subprocess.run(['ffmpeg','-v','error','-i',str(out/name),'-f','null','-'],check=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(out/name)]))['streams'][0]
 assert int(info['nb_read_frames'])==300 and int(info['width'])==width and int(info['height'])==height
 print('verified',name,info['nb_read_frames'],flush=True)
encode('Wigglinde-RVS-Vergleich.mp4',2*w,h+40,lambda i:pair(old[i],new[i]))
encode('bild032-RVS.mp4',w,h,lambda i:new[i])
Image.fromarray(pair(old[15],new[15])).save(out/'Vergleich-Mitte.png')
def stats(a,b):
 d=np.abs(a.astype('int16')-b.astype('int16'));return dict(max_rgb_channel_jump=int(d.max()),mean_absolute_rgb=float(d.mean()),fraction_pixels_over_16=float(np.mean(d.max(2)>16)))
r=ViewRenderer(scene);base_eps=r.render(1e-6).rgb
def probe(folder,i):return _srgb(np.fromfile(work/f'{folder}/rvs_{i}.rgb',np.float32).reshape(h,w,3))
log=(work/'animation/run.log').read_text();times=[float(x) for x in re.findall(r'view \d+ seconds ([\d.]+)',log)]
projection_check=re.search(r'projection_max_error_px ([\d.]+)',log)
report=dict(photo='bild032_cs.jpg',eye_size=[w,h],device='CPU',threads=8,las2_source='8c97bd4c4da3712c2ac60003a23201dfdb5935f4',rvs_source='d757a353c7f84d228ac30c179d6ff9de356c6101',las2_checkpoint_sha256='c41b61efce9b36e6b8b38b580421cd20cc9e84a47f0f45361767281938f69696',inference_note='Recomputed with pinned native LAS2-M FP32 after transient workspace reset. Both renderers use the SAME recovered maps. Versus saved previous ONNX midpoint: MAE 0.00006348/255; max 3/255; fraction >1: 0.0000032552.',rvs_precision=2,rvs_blending='Multispectral, low 1, high 4',rvs_inpaint='Unmodified upstream nearest-fill; raw missing masks retained in working data.',virtual_depth='Z=w/(d+64), C(t)=(0,-t,0), cx(t)=w/2+64*t; no source adjustment',rvs_projection_max_error_px=float(projection_check[1]) if projection_check else None,rvs_timing=dict(per_view_seconds=times,total_seconds=sum(times),median_seconds=float(np.median(times)),peak_rss_kib=int(re.search(r'peak_rss_kib (\d+)',log)[1]),includes='CPU projection, rasterization, blending, inpainting, downsampling, optional explicit adapter geometry verification, raw output writing; excludes model inference/build/MP4 encoding'),baseline_timing=json.loads((work/'baseline/timing.json').read_text()),epsilon_test=dict(delta_position=1e-6,max_physical_motion_px=float(max(np.max(abs(scene.left_disparity)),np.max(abs(scene.right_disparity)))*1e-6),baseline=stats(scene.left,base_eps),rvs_own_endpoint=stats(probe('probe',0),probe('probe',1)),rvs_vs_original_endpoint=stats(scene.left,probe('probe',1))),rvs_endpoint_difference=dict(left=stats(scene.left,new[0]),right=stats(scene.right,new[-1])),rvs_precision1_endpoint_difference=dict(left=stats(scene.left,probe('probe1',0)),right=stats(scene.right,probe('probe1',4))),clip='30 fps, 300 frames, five identical 2-second sinusoidal cycles. RVS own synthesized endpoints are used, NOT original endpoint substitution. Baseline keeps original endpoints.',adoption='Research comparison only; no product renderer switch, no Windows/portable validation.')
(out/'Messwerte.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
