"""Explicit build-time test only. Never called during normal conversion."""
from pathlib import Path
import json,hashlib,subprocess,threading,time
import numpy as np
from PIL import Image
from .processor import Processor
from .export_options import WiggleOptions
from .wiggle_export import ffmpeg_path

def run(app_dir,report_path):
    report_path=Path(report_path);report_path.parent.mkdir(parents=True,exist_ok=True)
    work=report_path.parent/'Stereotest_ÄÖÜ';work.mkdir(exist_ok=True)
    rng=np.random.default_rng(21);texture=rng.integers(0,256,(160,352,3),dtype=np.uint8)
    texture=np.asarray(Image.fromarray(texture).resize((352,160)))
    source=work/'Bild_Größe.png';Image.fromarray(np.concatenate((texture[:,:320],texture[:,8:328]),axis=1)).save(source)
    before=hashlib.sha256(source.read_bytes()).hexdigest();processor=Processor(app_dir);results=[];session=None
    for kind in ['mp4','gif','png']:
        options=WiggleOptions(format=kind,png_fps=60,cycle_seconds=.8 if kind=='gif' else .5)
        result=processor.convert(source,work/'Ausgabe_Größe',options)
        if session is None:session=id(processor.model.session)
        assert id(processor.model.session)==session
        output=Path(result['output']);assert output.exists()
        if kind=='mp4':
            data=subprocess.check_output([ffmpeg_path(),'-v','error','-i',str(output),'-f','rawvideo','-pix_fmt','rgb24','-'])
            assert len(data)==320*160*3*options.frame_count*5
        elif kind=='gif':
            with Image.open(output) as image:
                assert image.size==(320,160) and image.info['loop']==0
                duration=0
                for i in range(image.n_frames):image.seek(i);duration+=image.info['duration']
                assert abs(duration-options.cycle_seconds*1000)<=10
        else:
            frames=sorted(output.glob('*.png'));assert len(frames)==options.frame_count
            with Image.open(frames[0]) as image:assert image.size==(320,160)
            assert frames[1].read_bytes()==frames[-1].read_bytes()
        results.append(result)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    for height in (720,1080,2160):assert WiggleOptions(video_height=height).output_size(3840,2160)==(round(height*16/9),height)
    for side in (640,800,1024):assert max(WiggleOptions(format='gif',gif_long_side=side).output_size(3840,2160))==side
    # GUI startup and selected controls, on the actual packaged Tk runtime.
    from .app import WigglindeApp
    gui=WigglindeApp(app_dir);gui.update()
    for kind in ['GIF','PNG-Bildfolge','MP4']:
        gui.kind.set(kind);gui._format_changed();gui._wiggle_options().validate()
    gui.update()
    assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=gui.winfo_rooty()+gui.winfo_height()
    try:
        from PIL import ImageGrab
        ImageGrab.grab().save(report_path.parent/'gui-build-check.png')
    except OSError:pass
    gui.destroy()
    report_path.write_text(json.dumps(dict(status='passed',formats=results,model_session_reused=True,source_unchanged=True,gui_started=True),indent=2,ensure_ascii=False),encoding='utf-8')
