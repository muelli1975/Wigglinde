"""Explicit build-time test only. Never called during normal conversion."""
from pathlib import Path
import json,hashlib,subprocess,sys,threading,time
import numpy as np
from PIL import Image
from . import theme as T
from .processor import Processor
from .las2 import LiteAnyStereo
from .models import MODELS,DEFAULT_MODEL,model_path
from .memory import MemorySampler
from .export_options import WiggleOptions
from .wiggle_export import ffmpeg_path

def check_button_colors(gui):
    """Development regression: test drawn colors after real Tk hover callbacks."""
    def drawn(button,background,border,text):
        for tag,color in [('inner_parts',background),('border_parts',border)]:
            items=button._canvas.find_withtag(tag)
            assert items,tag
            assert {button._canvas.itemcget(item,'fill').lower() for item in items}=={color}
        assert button._text_label.cget('fg').lower()==text
    def event(surface,sequence):
        surface.event_generate(sequence);gui.update()
    start=gui.start
    gui._dependencies();gui.update()
    geometry=(start.winfo_width(),start.winfo_height())
    drawn(start,T.START_BG,T.START_BORDER,T.START_TEXT)
    for surface in [start._canvas,start._text_label]:
        event(surface,'<Enter>')
        drawn(start,T.START_HOVER_BG,T.START_HOVER_BORDER,T.START_HOVER_TEXT)
        assert (start.winfo_width(),start.winfo_height())==geometry
        event(surface,'<Leave>')
        drawn(start,T.START_BG,T.START_BORDER,T.START_TEXT)
    # A queued Enter must not restore gold after processing disables the button.
    start._canvas.event_generate('<Enter>')
    gui.running=True;gui._set_busy(True);gui.update()
    drawn(start,T.START_DISABLED_BG,T.START_DISABLED_BORDER,T.START_DISABLED_TEXT)
    event(start._text_label,'<Leave>');event(start._canvas,'<Enter>')
    drawn(start,T.START_DISABLED_BG,T.START_DISABLED_BORDER,T.START_DISABLED_TEXT)
    event(gui.stop._canvas,'<Enter>');drawn(gui.stop,T.BUTTON_HOVER,T.BORDER,T.TEXT)
    event(gui.stop._canvas,'<Leave>');drawn(gui.stop,T.BUTTON_BG,T.BORDER,T.TEXT)
    gui.running=False;gui._set_busy(False);gui.update()
    drawn(start,T.START_BG,T.START_BORDER,T.START_TEXT)
    # Secondary actions retain the neutral palette, including Cancel while busy.
    for button in [c for c in gui.controls if isinstance(c,type(start)) and c is not start]+[gui.stop]:
        assert button.cget('fg_color')==T.BUTTON_BG and button.cget('border_color')==T.BORDER
        assert button.cget('hover_color')==T.BUTTON_HOVER
        if button.cget('state')=='normal':
            event(button._canvas,'<Enter>');drawn(button,T.BUTTON_HOVER,T.BORDER,T.TEXT)
            event(button._canvas,'<Leave>');drawn(button,T.BUTTON_BG,T.BORDER,T.TEXT)

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
    assert results[0]['model']==DEFAULT_MODEL
    for result in results:
        assert result['status']=='passed' and result['model']=='LAS2-H'
        assert result['stage_seconds']['depth_left']>0 and result['stage_seconds']['depth_right']>0
        assert result['rvs']['render_seconds']>0 and result['rvs']['views']>1
        assert result['export_timings']['encode_or_copy_seconds']>0
        assert '_wiggle_' in result['output'] and 'Wiggle' not in Path(result['output']).name
        assert max(s['peak'].get('main_rss_bytes',0) for s in result['memory']['stages'].values())>0
    existing={p.relative_to(work) for p in work.rglob('*')}
    diagnosis=processor.diagnose(source,WiggleOptions())
    assert diagnosis['status']=='passed' and diagnosis['mode']=='depth_only'
    assert 'output' not in diagnosis and 'rvs' not in diagnosis
    assert existing=={p.relative_to(work) for p in work.rglob('*')}
    assert id(processor.model.session)==session
    latest=json.loads((Path(app_dir)/'logs/latest_run.json').read_text(encoding='utf-8'))
    assert latest['run_id']==diagnosis['run_id'] and latest['status']=='passed'
    processor.close()
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    for height in (720,1080,2160):assert WiggleOptions(video_height=height).output_size(3840,2160)==(round(height*16/9),height)
    for side in (640,800,1024):assert max(WiggleOptions(format='gif',gif_long_side=side).output_size(3840,2160))==side
    # GUI startup and selected controls, on the actual packaged Tk runtime.
    from .app import WigglindeApp,screen_work_area
    (Path(app_dir)/'settings.json').write_text(json.dumps(dict(model='LAS2-L',layout='Half-SBS')),encoding='utf-8')
    gui=WigglindeApp(app_dir);gui.update()
    icon=Path(app_dir)/'assets/wigglinde.ico'
    assert hashlib.sha256(icon.read_bytes()).hexdigest()=='0c8a3539748d834a6532b41ead10e886f802238793f8a625960b40606cad747f'
    if sys.platform=='win32':assert gui._iconbitmap_method_called
    assert not hasattr(gui,'file_list')
    assert not hasattr(gui,'layout') and 'layout' not in gui.settings
    assert not hasattr(gui,'model_name') and 'model' not in gui.settings
    assert gui.diagnose_button.cget('state')=='disabled'
    gui.input_file.set(str(source));gui.update()
    assert gui.diagnose_button.cget('state')=='normal'
    assert gui._collect_input()[0]==[source.resolve()]
    check_button_colors(gui)
    gui.input_folder.set(str(work));gui.update()
    assert not gui.input_file.get()
    assert gui.diagnose_button.cget('state')=='disabled'
    gui.own.set(str(work/'Custom output'));gui.standard.set(False);gui._dependencies()
    for language in ['English','Deutsch']:
        gui.kind.set(gui.tr('png'));gui._format_changed();gui.size.set('2160');gui.fps.set('60')
        gui.language.set(language);gui._language_changed();gui.update()
        assert gui._wiggle_options().png_height==2160 and gui._wiggle_options().png_fps==60
        assert not hasattr(gui,'model_name')
        assert gui.input_folder.get()==str(work) and gui.own.get()==str(work/'Custom output')
        assert gui.output_label.cget('text').endswith(str(work/'Custom output'))
        assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=screen_work_area(gui)[3]
    import customtkinter as ctk
    ctk.set_widget_scaling(1.0);gui.update()
    gui.running=True;gui._set_busy(True);gui.update()
    assert all(c.cget('state')=='disabled' for c in gui.controls)
    assert gui.stop.cget('state')=='normal' and gui.start.cget('border_color')=='#333333'
    gui.running=False;gui._set_busy(False);gui.standard.set(True);gui._dependencies()
    assert gui.own_entry.cget('state')=='disabled'
    adapters=list(gui.adapters)
    sound=Path(app_dir)/'assets/ready.wav'
    assert hashlib.sha1(b'blob '+str(sound.stat().st_size).encode()+b'\0'+sound.read_bytes()).hexdigest()=='260fb0d49982873a13dabd750b997448acb675ca'
    for language in ['English','Deutsch']:
        gui.language.set(language);gui._language_changed();gui.update()
        def geometry_snapshot():
            return [(w.winfo_rootx(),w.winfo_rooty(),w.winfo_width(),w.winfo_height()) for w in gui.controls]
        baseline=geometry_snapshot();device_before=gui.device.get()
        for kind in ['GIF',gui.tr('png'),'MP4']:
            gui.kind.set(kind);gui._format_changed();gui._wiggle_options().validate()
            # A long label exercises layout only; it does not probe a device.
            for device_label in [device_before,'GPU 0: '+('Long adapter name '*6)]:
                gui.device.set(device_label);gui.update()
                assert geometry_snapshot()==baseline
        gui.device.set(device_before)
    for scaling in (1.,1.25,1.5):
        ctk.set_widget_scaling(scaling);ctk.set_window_scaling(scaling);gui.update()
        for control in gui.controls+[gui.stop]:
            assert control.winfo_rootx()>=gui.winfo_rootx()
            assert control.winfo_rootx()+control.winfo_width()<=gui.winfo_rootx()+gui.winfo_width()
            assert control.winfo_rooty()+control.winfo_height()<=gui.winfo_rooty()+gui.winfo_height()
    ctk.set_widget_scaling(1.);ctk.set_window_scaling(1.)
    gui.update()
    assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=gui.winfo_rooty()+gui.winfo_height()
    assert gui.stop.winfo_rooty()+gui.stop.winfo_height()<=screen_work_area(gui)[3]
    try:
        from PIL import ImageGrab
        ImageGrab.grab().save(report_path.parent/'gui-build-check.png')
    except OSError:pass
    gui.destroy()
    with MemorySampler(0) as counters:counters.sample('native_counter_probe')
    memory_probe=counters.report()
    # Explicit development probe, including WARP on a hosted runner if available.
    # A software adapter does not establish performance on a physical GPU.
    directml=[]
    import onnxruntime as ort
    if 'DmlExecutionProvider' in ort.get_available_providers():
        for label in MODELS:
            try:
                model=LiteAnyStereo(model_path(app_dir,label),device_id=0)
            except Exception as error:
                directml.append(dict(model=label,status='unavailable',reason=str(error),hardware_speed_not_validated=True))
                break
            else:
                left=texture[:,:320];right=texture[:,8:328]
                reference=LiteAnyStereo(model_path(app_dir,label))
                cpu=reference.predict(left,right,24,lambda:False)
                begin=time.monotonic();gpu=model.predict(left,right,24,lambda:False)
                diff=np.abs(cpu-gpu)
                assert float(diff.max())<.05,(label,float(diff.max()))
                directml.append(dict(model=label,status='passed',providers=model.session.get_providers(),max_difference_px=float(diff.max()),seconds=time.monotonic()-begin,hardware_speed_not_validated=True))
                del model,reference
    report_path.write_text(json.dumps(dict(status='passed',formats=results,depth_diagnosis=diagnosis,native_memory_probe=memory_probe,model_session_reused=True,source_unchanged=True,gui_started=True,bilingual_gui=True,stable_control_geometry=True,button_colors=True,adapters=adapters,original_sound=True,original_icon=True,directml=directml),indent=2,ensure_ascii=False),encoding='utf-8')
