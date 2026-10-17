"""Full-SBS -> LAS2-H -> RVS. Diagnostics use the same depth calculation."""
from pathlib import Path
import io,tempfile,time,threading,os
import numpy as np
from PIL import Image,ImageCms,ImageOps
from .diagnostics import LocalLogs,RunTrace
from .export_options import camera_weight
from .stereo import StereoScene
from .las2 import LiteAnyStereo
from .models import DEFAULT_MODEL,model_path
from .rvs import RVSRenderer
from .wiggle_export import export_wiggle,check_cancelled

EXTENSIONS={'.jpg','.jpeg','.png','.tif','.tiff','.bmp','.webp'}

def read_pair(path,options):
    with Image.open(path) as source:
        bits=getattr(source,'tag_v2',{}).get(258,(8,));bits=(bits,) if isinstance(bits,int) else bits
        high_depth=any(value>8 for value in bits) or any('16' in str(tile.args) for tile in source.tile)
        if source.mode not in ('RGB','L','P','1') or 'transparency' in source.info or high_depth:
            raise ValueError('Diese Testversion benötigt deckende RGB-/Graustufenbilder mit 8 Bit pro Kanal.')
        image=ImageOps.exif_transpose(source).convert('RGB')
        profile=source.info.get('icc_profile')
        if profile:
            image=ImageCms.profileToProfile(image,ImageCms.ImageCmsProfile(io.BytesIO(profile)),ImageCms.createProfile('sRGB'),outputMode='RGB')
        w,h=image.size
        if w%2:raise ValueError('Das SBS-Bild muss zwei gleich breite Halbbilder enthalten.')
        eyes=[image.crop((0,0,w//2,h)),image.crop((w//2,0,w,h))]
        original=(w//2,h);size=options.output_size(*original)
        eyes=[e.resize(size,Image.Resampling.LANCZOS) if e.size!=size else e for e in eyes]
        pair=[np.asarray(e).copy() for e in eyes]
        return tuple(pair),original,size

def collect_files(folder,excluded=()):
    folder=Path(folder).resolve();excluded={Path(x).resolve() for x in excluded};result=[]
    for root,dirs,files in os.walk(folder):
        dirs[:]=sorted(d for d in dirs if d!='_temp' and not ('_wiggle_' in d.lower() and d.lower().endswith('_png')) and (Path(root)/d).resolve() not in excluded)
        result.extend(Path(root)/n for n in sorted(files) if Path(n).suffix.lower() in EXTENSIONS)
    return result

class Processor:
    def __init__(self,app_dir,cancel_event=None,device_id=None,model_name=DEFAULT_MODEL,device_name=None):
        if model_name!=DEFAULT_MODEL:raise ValueError('Diese Version verwendet LAS2-H / this version uses LAS2-H')
        self.model_name=model_name;self.device_id=device_id;self.device_name=device_name or ('CPU' if device_id is None else f'GPU {device_id}')
        self.app_dir=Path(app_dir);self.event=cancel_event or threading.Event();self.model=None;self.renderer=None
        self.logs=LocalLogs(app_dir);self.last_diagnostics=None

    def close(self):self.logs.close()
    def cancel(self):
        self.event.set()
        if self.model:self.model.cancel()
        if self.renderer:self.renderer.cancel()

    def convert(self,path,output_root,options,progress=lambda text,p:None):
        return self._run(path,options,progress,Path(output_root))

    def diagnose(self,path,options,progress=lambda text,p:None):
        return self._run(path,options,progress,None)

    def _run(self,path,options,progress,output_root):
        options.validate();check_cancelled(self.event.is_set)
        context=dict(source=str(Path(path).resolve()),model=self.model_name,iterations=4,precision='float32',layout='Full-SBS',input_order='left_then_right',
            device=self.device_name,depth_device_id=self.device_id,mode='depth_only' if output_root is None else 'wiggle',options=options.to_settings())
        trace=RunTrace(self.logs,context,self.device_id,child=lambda:self.renderer.process.pid if self.renderer and self.renderer.process else None)
        self.last_diagnostics=trace.data
        with trace:
            progress('Bild vorbereiten',0.)
            with trace.stage('prepare'):(left,right),original,size=read_pair(path,options)
            offset=min(128,max(1,round(64*size[0]/960)))
            trace.data.update(source_eye_size=original,processing_size=size,matching_offset=offset)
            trace.event('prepared',processing_size=size,matching_offset=offset)
            if self.model is None:
                progress(self.model_name+' laden',0.)
                with trace.stage('model_load'):self.model=LiteAnyStereo(model_path(self.app_dir,self.model_name),device_id=self.device_id)
            if self.model.model_name!=self.model_name:raise ValueError('Falsche Modelldatei / incorrect model file: '+str(self.model.model_name))
            trace.data['depth_provider']=self.model.session.get_providers()
            dl,dr=self.model.predict_pair(left,right,offset,self.event.is_set,progress,stage=trace.stage)
            trace.data['depth_seconds']=trace.timings['depth_left']+trace.timings['depth_right']
            if output_root is not None:
                output_root.mkdir(parents=True,exist_ok=True);temp_root=output_root/'_temp';temp_root.mkdir(exist_ok=True)
                scene=StereoScene(left,right,dl,dr);positions=[camera_weight(i,options.frame_count) for i in range(options.frame_count//2+1)]
                suffix=f'_wiggle_{options.fps}fps_{size[1]}p' if options.format!='gif' else f'_wiggle_{options.fps}fps_{max(size)}px'
                output=output_root/(Path(path).stem+suffix+('.'+options.format if options.format!='png' else '_png'))
                trace.data.update(output=str(output),renderer='RVS CPU Precision 2 Multispectral 1/4')
                with tempfile.TemporaryDirectory(prefix='rvs_',dir=temp_root) as directory:
                    work=Path(directory);exe=self.app_dir/'backend'/('wigglinde_rvs.exe' if os.name=='nt' else 'wigglinde_rvs')
                    with trace.stage('rvs_prepare'):self.renderer=RVSRenderer(exe,scene,positions,work/'rvs',offset)
                    renderer=self.renderer;frames=iter(renderer.frames(self.event.is_set));index=0;wait_seconds=0.;export_times={}
                    trace.data['rvs_schedule']=renderer.schedule
                    def render(position):
                        nonlocal index,wait_seconds
                        check_cancelled(self.event.is_set);begin=time.perf_counter();rgb=next(frames);index+=1
                        if index==len(positions):next(frames,None)
                        wait_seconds+=time.perf_counter()-begin
                        progress(f'Zwischenansicht {index}/{len(positions)}',.35+.5*index/len(positions));return rgb
                    def exporting(p):
                        if p>.7:progress(f'{options.format.upper()} speichern',.85+.15*(p-.7)/.3)
                    try:
                        with trace.stage('view_export'):export_wiggle(render,size,options,output,work,exporting,self.event.is_set,timings=export_times)
                    finally:
                        frames.close();trace.data.update(rvs=renderer.metrics,export_timings=export_times,render_stream_wait_seconds=wait_seconds);self.renderer=None
            progress('Fertig',1.)
        return trace.data
