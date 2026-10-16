"""Render the unchanged diagnostic baseline, in a separate measured process."""
from pathlib import Path
import sys,time,json,resource
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from wigglinde.stereo import StereoScene
from wigglinde.render import ViewRenderer
folder=Path(sys.argv[2]);folder.mkdir(parents=True,exist_ok=True)
scene=StereoScene.load(sys.argv[1]);renderer=ViewRenderer(scene)
positions=json.loads(Path(sys.argv[3]).read_text());times=[]
for i,t in enumerate(positions):
 start=time.perf_counter();v=renderer.render(t);times.append(time.perf_counter()-start)
 Image.fromarray(v.rgba()).save(folder/f'{i:03d}.png')
 print(i,t,times[-1],flush=True)
(folder/'timing.json').write_text(json.dumps(dict(seconds=times,total_seconds=sum(times),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),indent=2))
