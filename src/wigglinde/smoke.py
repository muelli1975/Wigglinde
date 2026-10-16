"""Explicit build-time test only. Never called during normal conversion."""
from pathlib import Path
import json,hashlib,subprocess,threading,time
import numpy as np
from PIL import Image
from .processor import Processor
from .las2 import LiteAnyStereo
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
    from .app import WigglindeApp,screen_work_area
    gui=WigglindeApp(app_dir);gui.update()
    assert not hasattr(gui,'file_list')
    gui.input_file.set(str(source));gui.update()
    assert gui._collect_input()[0]==[source.resolve()]
    gui.input_folder.set(str(work));gui.update()
    assert not gui.input_file.get()
    gui.own.set(str(work/'Custom output'));gui.standard.set(False);gui._dependencies()
    for language in ['English','Deutsch']:
        gui.kind.set(gui.tr('png'));gui._format_changed();gui.size.set('2160');gui.fps.set('60')
        gui.language.set(language);gui._language_changed();gui.update()
        assert gui._wiggle_options().png_height==2160 and gui._wiggle_options().png_fps==60
        assert gui.input_folder.get()==str(work) and gui.own.get()==str(work/'Custom output')
        assert gui.output_label.cget('text').endswith(str(work/'Custom output'))
        assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=screen_work_area(gui)[3]
    gui.running=True;gui._set_busy(True);gui.update()
    assert all(c.cget('state')=='disabled' for c in gui.controls)
    assert gui.stop.cget('state')=='normal' and gui.start.cget('border_color')=='#333333'
    gui.running=False;gui._set_busy(False);gui.standard.set(True);gui._dependencies()
    assert gui.own_entry.cget('state')=='disabled'
    adapters=list(gui.adapters)
    sound=Path(app_dir)/'assets/ready.wav'
    assert hashlib.sha1(b'blob '+str(sound.stat().st_size).encode()+b'\0'+sound.read_bytes()).hexdigest()=='260fb0d49982873a13dabd750b997448acb675ca'
    for kind in ['GIF',gui.tr('png'),'MP4']:
        gui.kind.set(kind);gui._format_changed();gui._wiggle_options().validate()
    gui.update()
    assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=gui.winfo_rooty()+gui.winfo_height()
    assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=screen_work_area(gui)[3]
    try:
        from PIL import ImageGrab
        ImageGrab.grab().save(report_path.parent/'gui-build-check.png')
    except OSError:pass
    gui.destroy()
    # Explicit development probe, including WARP on a hosted runner if available.
    # A software adapter does not establish performance on a physical GPU.
    directml=dict(status='not-tested')
    import onnxruntime as ort
    if 'DmlExecutionProvider' in ort.get_available_providers():
        try:
            model=LiteAnyStereo(Path(app_dir)/'models/las2/LAS2_M_dynamic.onnx',device_id=0)
        except Exception as error:
            directml=dict(status='unavailable',reason=str(error),hardware_speed_not_validated=True)
        else:
            left=texture[:,:320];right=texture[:,8:328]
            cpu=processor.model.predict(left,right,24,lambda:False)
            begin=time.monotonic();gpu=model.predict(left,right,24,lambda:False)
            diff=np.abs(cpu-gpu)
            assert float(diff.max())<.05, float(diff.max())
            directml=dict(status='passed',providers=model.session.get_providers(),max_difference_px=float(diff.max()),seconds=time.monotonic()-begin,hardware_speed_not_validated=True)
    report_path.write_text(json.dumps(dict(status='passed',formats=results,model_session_reused=True,source_unchanged=True,gui_started=True,bilingual_gui=True,adapters=adapters,original_sound=True,directml=directml),indent=2,ensure_ascii=False),encoding='utf-8')
