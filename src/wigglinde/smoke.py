"""Explicit build-time test only. Never called during normal conversion."""
from pathlib import Path
import json,hashlib,subprocess,sys,threading,time
import numpy as np
from PIL import Image
from . import theme as T,SETTINGS_FILENAME
from .processor import Processor
from .las2 import LiteAnyStereo
from .igev import IGEVMiddlebury
from .defom import DEFOMStereo
from .models import MODELS,DEFAULT_MODEL,DEFOM_LARGE,model_path,model_iterations,model_family,model_suffix
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
    for kind in ['mp4','gif','avif','png']:
        options=WiggleOptions(format=kind,png_fps=60,cycle_seconds=.8 if kind=='gif' else .5,save_depth=kind=='png')
        result=processor.convert(source,work/'Ausgabe_Größe',options)
        assert not (work/'Ausgabe_Größe'/'_temp').exists()
        if session is None:session=id(processor.model.session)
        assert id(processor.model.session)==session
        output=Path(result['output']);assert output.exists()
        assert output.parent==work/'Ausgabe_Größe'/'wiggle'
        if kind=='png':
            depth=result['depth_export']
            assert depth['normalization']=='joint_linear_min_max' and not depth['metric_depth']
            assert Path(depth['metadata_file']).is_file()
            for file in depth['files']:
                assert Path(file).parent==work/'Ausgabe_Größe'/'depth_maps'
                assert Path(file).name.startswith('Bild_Größe_depth_160p_las2-h_')
                with Image.open(file) as image:
                    assert image.size==(320,160) and np.asarray(image).dtype==np.uint16
        else:
            assert 'depth_export' not in result
            assert not (work/'Ausgabe_Größe'/'depth_maps').exists()
        if kind=='mp4':
            data=subprocess.check_output([ffmpeg_path(),'-v','error','-i',str(output),'-f','rawvideo','-pix_fmt','rgb24','-'])
            assert len(data)==320*160*3*options.frame_count*5
        elif kind=='gif':
            with Image.open(output) as image:
                assert image.size==(320,160) and image.info['loop']==0
                duration=0
                for i in range(image.n_frames):image.seek(i);duration+=image.info['duration']
                assert abs(duration-options.cycle_seconds*1000)<=10
        elif kind in ('avif',):
            from .animation_checks import check_animation
            check_animation(output,(320,160),options.cycle_seconds*1000)
        else:
            frames=sorted(output.glob('*.png'));assert len(frames)==options.frame_count
            with Image.open(frames[0]) as image:assert image.size==(320,160)
            assert frames[1].read_bytes()==frames[-1].read_bytes()
        results.append(result)
    assert results[0]['model']==DEFAULT_MODEL
    for result in results:
        assert result['status']=='passed' and result['model']=='LAS2-H'
        assert result['renderer']=='RVS CPU Precision 1 Simple 5'
        assert result['blending']==dict(BlendingMethod='Simple',BlendingFactor=5.)
        assert result['stage_seconds']['depth_left']>0 and result['stage_seconds']['depth_right']>0
        assert result['rvs']['render_work_seconds']>0 and result['rvs']['views']>1
        assert result['rvs']['parallel_workers']==result['rvs_schedule']['workers']
        if result['rvs']['parallel_workers']>1:assert result['rvs']['opencv_threads']==1
        else:assert result['rvs']['opencv_threads']>0
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
    # Every additional estimator runs through the actual packaged CPU/RVS path.
    png_result=next(r for r in results if "depth_export" in r)
    model_checks=[]
    for label in MODELS:
        if label==DEFAULT_MODEL:continue
        alternate=Processor(app_dir,model_name=label)
        try:
            result=alternate.convert(source,work/'Ausgabe_Größe',WiggleOptions(format='png',cycle_seconds=.5,save_depth=True))
            assert result['model']==label and result['iterations']==model_iterations(label)
            assert result['output']!=png_result['output'] and Path(png_result['output']).exists()
            assert model_suffix(label) in Path(result['output']).name
            metadata=json.loads(Path(result['depth_export']['metadata_file']).read_text(encoding='utf-8'))
            assert metadata['model']==label and metadata['iterations']==model_iterations(label)
            assert metadata['precision']=='float32' and metadata['device']=='CPU'
            assert set(metadata['maps'].values()).isdisjoint(Path(p).name for p in png_result['depth_export']['files'])
            assert result['renderer']=='RVS CPU Precision 1 Simple 5'
            frames=sorted(Path(result['output']).glob('*.png'))
            assert len(frames)==15
            with Image.open(frames[7]) as image:assert image.size==(320,160)
            alternate_session=id(alternate.model.session)
            repeated=alternate.diagnose(source,WiggleOptions())
            assert repeated['model']==label and id(alternate.model.session)==alternate_session
            model_checks.append(dict(model=label,status='passed',iterations=result['iterations'],depth_seconds=result['depth_seconds'],session_reused=True))
        finally:alternate.close()
    # GUI startup and selected controls, on the actual packaged Tk runtime.
    from .app import WigglindeApp,screen_work_area
    (Path(app_dir)/SETTINGS_FILENAME).write_text(json.dumps(dict(model='obsolete',layout='Half-SBS',iterations=8,renderer='opengl')),encoding='utf-8')
    gui=WigglindeApp(app_dir);gui.update()
    assert gui._wiggle_options().video_height==720 and gui.device.get()=='CPU'
    assert not gui.save_depth.get() and gui.depth_check.cget('text')==gui.tr('save_depth')
    icon=Path(app_dir)/'assets/wigglinde.ico'
    assert hashlib.sha256(icon.read_bytes()).hexdigest()=='0c8a3539748d834a6532b41ead10e886f802238793f8a625960b40606cad747f'
    if sys.platform=='win32':assert gui._iconbitmap_method_called
    assert not hasattr(gui,'file_list')
    assert not hasattr(gui,'blending_method') and not hasattr(gui,'blending_menu')
    assert not hasattr(gui,'layout') and 'layout' not in gui.settings
    assert not hasattr(gui,'swap')
    assert gui.model_name.get()==DEFAULT_MODEL and gui.model_menu.cget('values')==list(MODELS)
    assert not hasattr(gui,'iterations') and not hasattr(gui,'renderer')
    assert 'iterations' not in gui.settings and 'renderer' not in gui.settings
    assert gui.diagnose_button.cget('state')=='disabled'
    gui.input_file.set(str(source));gui.update()
    assert gui.diagnose_button.cget('state')=='normal'
    assert gui._collect_input()[0]==[source.resolve()]
    check_button_colors(gui)
    gui.input_folder.set(str(work));gui.update()
    assert not gui.input_file.get()
    assert gui._collect_input()[0]==[source.resolve()]
    assert gui.diagnose_button.cget('state')=='disabled'
    gui.own.set(str(work/'Custom output'));gui.standard.set(False);gui._dependencies()
    for language in ['English','Deutsch']:
        gui.kind.set(gui.tr('png'));gui._format_changed();gui.size.set('2160');gui.fps.set('60')
        gui.language.set(language);gui._language_changed();gui.update()
        assert gui._wiggle_options().png_height==2160 and gui._wiggle_options().png_fps==60
        assert gui.depth_check.cget('text')==gui.tr('save_depth')
        assert gui.model_menu.cget('values')==list(MODELS)
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
    assert gui.cycles_entry.cget('state')=='disabled'
    gui.save_depth.set(True);gui.kind.set('MP4');gui._format_changed()
    gui.cycles.set('1')
    assert gui.cycles_entry.cget('state')=='normal'
    gui.size.set('1080');gui.fps.set('60')
    gui.kind.set('GIF');gui._format_changed();gui.size.set('640');gui.fps.set('25')
    gui.kind.set('AVIF');gui._format_changed();gui.size.set('1080');gui.fps.set('60')
    gui.kind.set('MP4');gui._format_changed()
    assert (gui.size.get(),gui.fps.get(),gui.cycles.get())==('1080','60','1')
    gui.size.set('2160');gui.fps.set('60');gui.duration.set('3');gui.model_name.set('IGEV++ Middlebury');gui._save();gui.destroy()
    gui=WigglindeApp(app_dir);gui.update()
    assert gui.save_depth.get() and gui._wiggle_options().save_depth
    assert gui.model_name.get()=='IGEV++ Middlebury'
    assert gui._wiggle_options().video_height==2160 and gui._wiggle_options().video_fps==60
    assert gui._wiggle_options().cycle_seconds==3 and gui.input_folder.get()==str(work)
    assert gui._wiggle_options().video_cycles==1
    gui.kind.set('GIF');gui._format_changed()
    assert (gui.size.get(),gui.fps.get())==('640','25')
    assert gui.cycles_entry.cget('state')=='disabled'
    gui.kind.set('AVIF');gui._format_changed()
    assert (gui.size.get(),gui.fps.get())==('1080','60')
    gui.kind.set('MP4');gui._format_changed()
    gui.input_file.set(str(source));gui.update()
    adapters=list(gui.adapters)
    sound=Path(app_dir)/'assets/ready.wav'
    assert hashlib.sha1(b'blob '+str(sound.stat().st_size).encode()+b'\0'+sound.read_bytes()).hexdigest()=='260fb0d49982873a13dabd750b997448acb675ca'
    for language in ['English','Deutsch']:
        gui.language.set(language);gui._language_changed();gui.update()
        assert set(gui.format_menu.cget('values'))=={'MP4','GIF','AVIF',gui.tr('png')}
        def geometry_snapshot():
            return [(w.winfo_rootx(),w.winfo_rooty(),w.winfo_width(),w.winfo_height()) for w in gui.controls]
        baseline=geometry_snapshot();device_before=gui.device.get()
        for kind in ['GIF',gui.tr('png'),'AVIF','MP4']:
            gui.kind.set(kind);gui._format_changed();gui._wiggle_options().validate()
            # A long label exercises layout only; it does not probe a device.
            for device_label in [device_before,'GPU 0: '+('Long adapter name '*6)]:
                gui.device.set(device_label);gui.update()
                assert geometry_snapshot()==baseline
            # Restore the real selection before format changes persist settings.
            gui.device.set(device_before)
        for label in MODELS:
            gui.model_name.set(label);gui.update()
            assert geometry_snapshot()==baseline
        gui.device.set(device_before)
    for scaling in (1.,1.25,1.5):
        ctk.set_widget_scaling(scaling);ctk.set_window_scaling(scaling);gui.update()
        gui.geometry('780x600');gui.update()
        for control in gui.controls+[gui.stop]:
            assert control.winfo_rootx()>=gui.winfo_rootx()
            assert control.winfo_rootx()+control.winfo_width()<=gui.winfo_rootx()+gui.winfo_width()
            assert control.winfo_rooty()+control.winfo_height()<=gui.winfo_rooty()+gui.winfo_height()
        from tkinter.font import Font
        gui.model_name.set(DEFOM_LARGE);gui.update()
        label=gui.model_menu._text_label
        assert Font(font=label.cget('font')).measure(DEFOM_LARGE)<=label.winfo_width()
    ctk.set_widget_scaling(1.);ctk.set_window_scaling(1.)
    gui.update()
    # Run real packaged DEFOM initialization/inference while the Tk event loop
    # continues to service timers. Message boxes are suppressed only in this test.
    from unittest.mock import patch
    heartbeat=[]
    def beat():
        heartbeat.append(time.monotonic())
        if gui.running:gui.after(25,beat)
    gui.model_name.set(DEFOM_LARGE);gui.duration.set('.5');gui.size.set('720')
    gui.input_file.set(str(source));gui.update()
    with patch('wigglinde.app.messagebox.showinfo'),patch('wigglinde.app.messagebox.showerror') as errors:
        gui._start(True);gui.after(25,beat);deadline=time.monotonic()+240
        while gui.running and time.monotonic()<deadline:
            gui.update();time.sleep(.01)
        assert not gui.running and not errors.called
    assert len(heartbeat)>4 and max(b-a for a,b in zip(heartbeat,heartbeat[1:]))<1.5
    gui_responsiveness=dict(model=DEFOM_LARGE,timer_samples=len(heartbeat),max_timer_gap_seconds=max(b-a for a,b in zip(heartbeat,heartbeat[1:])))
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
    model_metadata=[]
    for label in MODELS:
        for device in ([None,0] if sys.platform=='win32' else [None]):
            path=model_path(app_dir,label,device)
            meta=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
            assert meta['model']==label and meta['iterations']==model_iterations(label)
            with path.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==meta['onnx_sha256']
            model_metadata.append(dict(model=label,device=device,sha256=meta['onnx_sha256']))
    assert not list((Path(app_dir)/'models/las2').glob('*iter8*'))
    assert not list((Path(app_dir)/'backend').glob('*_gl*'))
    mixed_path=model_path(app_dir,DEFAULT_MODEL,device_id=0)
    mixed_meta=None
    if sys.platform=='win32':
        mixed_meta=json.loads(mixed_path.with_suffix('.json').read_text(encoding='utf-8'))
        assert mixed_meta['precision']=='mixed_float16_float32'
        assert hashlib.sha256(mixed_path.read_bytes()).hexdigest()==mixed_meta['onnx_sha256']
    else:
        assert not mixed_path.exists() and adapters==['CPU']
    import onnxruntime as ort
    if 'DmlExecutionProvider' in ort.get_available_providers():
        for label in MODELS:
            estimator=DEFOMStereo if model_family(label)=='defom' else IGEVMiddlebury if model_family(label)=='igev' else LiteAnyStereo
            try:
                model=estimator(model_path(app_dir,label,device_id=0),device_id=0)
            except Exception as error:
                directml.append(dict(model=label,status='unavailable',reason=str(error),hardware_speed_not_validated=True))
                break
            else:
                left=texture[:,:320];right=texture[:,8:328]
                reference=estimator(model_path(app_dir,label))
                cpu=reference.predict(left,right,24,lambda:False)
                begin=time.monotonic();gpu=model.predict(left,right,24,lambda:False)
                diff=np.abs(cpu-gpu)
                assert np.isfinite(gpu).all()
                np.testing.assert_allclose(gpu,cpu,rtol=.01,atol=.1)
                directml.append(dict(model=label,status='passed',precision=model.precision,providers=model.session.get_providers(),max_difference_px=float(diff.max()),mean_difference_px=float(diff.mean()),within_h_numerical_tolerance=bool(np.all(diff<=.1+.01*np.abs(cpu))),seconds=time.monotonic()-begin,hardware_speed_not_validated=True))
                if hasattr(model,'close'):model.close();reference.close()
                del model,reference
    report_path.write_text(json.dumps(dict(status='passed',model_names_separate=True,depth_model_metadata=True,formats=results,model_checks=model_checks,model_metadata=model_metadata,depth_diagnosis=diagnosis,native_memory_probe=memory_probe,model_session_reused=True,source_unchanged=True,gui_started=True,bilingual_gui=True,defom_gui_responsiveness=gui_responsiveness,stable_control_geometry=True,button_colors=True,adapters=adapters,original_sound=True,original_icon=True,mixed_model_bundled=mixed_meta is not None,mixed_model_sha256=mixed_meta['onnx_sha256'] if mixed_meta else None,directml=directml),indent=2,ensure_ascii=False),encoding='utf-8')
