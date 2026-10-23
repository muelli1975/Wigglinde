"""Explicit development probe; not an application startup or fallback."""
from pathlib import Path
import argparse,json,tempfile
import numpy as np
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene

def main():
    p=argparse.ArgumentParser();p.add_argument('--renderer',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-unavailable',action='store_true');a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='Vulkan_Größe_') as folder:
        rgb=np.full((96,128,3),(37,113,201),np.uint8);d=np.full(rgb.shape[:2],4,np.float32)
        renderer=RVSRenderer(a.renderer.resolve(),StereoScene(rgb,rgb,d,d),[0,.5,1],Path(folder),stream_format="rgb24")
        try:
            frames=list(renderer.frames(lambda:False))
            assert len(frames)==3
            for frame in frames:
                assert frame.shape==rgb.shape
                assert np.max(np.abs(frame[8:-8,8:-8].astype(int)-rgb[8:-8,8:-8].astype(int)))<=1
            report=dict(status='passed',constant_plane_rgb_and_frame_transport=True,metrics=renderer.metrics)
        except RuntimeError as e:
            # A hosted software adapter is not evidence about the user's GPU.
            if not a.allow_unavailable or 'failed to find a suitable GPU' not in str(e):raise
            report=dict(status='unavailable',reason=str(e),gpu_render_test_passed=False)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
