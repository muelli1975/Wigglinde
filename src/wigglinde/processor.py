"""Converter pipeline: chosen size, one model session, RVS, existing export core."""
from pathlib import Path
import io,json,tempfile,time,threading,os
import numpy as np
from PIL import Image,ImageCms,ImageOps
from .export_options import camera_weight
from .stereo import StereoScene
from .las2 import LiteAnyStereo
from .models import DEFAULT_MODEL,model_path
from .rvs import RVSRenderer
from .wiggle_export import export_wiggle,ExportCancelled,check_cancelled

EXTENSIONS={'.jpg','.jpeg','.png','.tif','.tiff','.bmp','.webp'}

def read_pair(path,layout,swap,options):
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
        original=(w//2 if layout=='Full-SBS' else w,h)
        size=options.output_size(*original)
        eyes=[e.resize(size,Image.Resampling.LANCZOS) if e.size!=size else e for e in eyes]
        pair=[np.asarray(e).copy() for e in eyes]
        return tuple(pair[::-1] if swap else pair),original,size

def collect_files(folder,excluded=()):
    folder=Path(folder).resolve();excluded={Path(x).resolve() for x in excluded}
    result=[]
    for root,dirs,files in os.walk(folder):
        dirs[:]=sorted(d for d in dirs if d!='_temp' and not ('_Wiggle_' in d and d.endswith('_PNG')) and (Path(root)/d).resolve() not in excluded)
        result.extend(Path(root)/n for n in sorted(files) if Path(n).suffix.lower() in EXTENSIONS)
    return result

class Processor:
    def __init__(self,app_dir,cancel_event=None,device_id=None,model_name=DEFAULT_MODEL):
        self.model_name=model_name;self.device_id=device_id;self.app_dir=Path(app_dir);self.event=cancel_event or threading.Event();self.model=None;self.renderer=None
    def cancel(self):
        self.event.set()
        if self.model:self.model.cancel()
        if self.renderer:self.renderer.cancel()
    def convert(self,path,output_root,options,layout='Full-SBS',swap=False,progress=lambda text,p:None):
        options.validate();check_cancelled(self.event.is_set)
        output_root=Path(output_root);output_root.mkdir(parents=True,exist_ok=True)
        # Stage beside the destination so final replacement also works on another drive.
        temp_root=output_root/'_temp';temp_root.mkdir(exist_ok=True)
        start=time.monotonic();progress('Bild vorbereiten',0.)
        (left,right),original,size=read_pair(path,layout,swap,options)
        if self.model is None:
            progress(self.model_name+' laden',0.)
            self.model=LiteAnyStereo(model_path(self.app_dir,self.model_name),device_id=self.device_id)
        if self.model.model_name!=self.model_name:raise ValueError('Falsche Modelldatei / incorrect model file: '+str(self.model.model_name))
        # Reversible search padding, scaled with the explicitly selected image size.
        # LAS2 has a fixed 192-pixel correspondence range; keep room on both sides.
        offset=min(128,max(1,round(64*size[0]/960)))
        depth_start=time.monotonic()
        dl,dr=self.model.predict_pair(left,right,offset,self.event.is_set,progress)
        depth_seconds=time.monotonic()-depth_start
        render_seconds=0.
        scene=StereoScene(left,right,dl,dr);positions=[camera_weight(i,options.frame_count) for i in range(options.frame_count//2+1)]
        suffix=f'_Wiggle_{options.fps}fps_{size[1]}h' if options.format!='gif' else f'_Wiggle_{options.fps}fps_{max(size)}px'
        output=output_root/(Path(path).stem+suffix+('.'+options.format if options.format!='png' else '_PNG'))
        with tempfile.TemporaryDirectory(prefix='rvs_',dir=temp_root) as directory:
            work=Path(directory);exe=self.app_dir/'backend'/('wigglinde_rvs.exe' if os.name=='nt' else 'wigglinde_rvs')
            self.renderer=RVSRenderer(exe,scene,positions,work/'rvs',offset)
            frames=iter(self.renderer.frames(self.event.is_set));index=0
            def render(position):
                nonlocal index,render_seconds
                check_cancelled(self.event.is_set)
                render_start=time.monotonic();rgb=next(frames);index+=1
                if index==len(positions):next(frames,None)
                render_seconds+=time.monotonic()-render_start
                progress(f'Zwischenansicht {index}/{len(positions)}',.35+.5*index/len(positions))
                return rgb
            def exporting(p):
                if p>.7:progress(f'{options.format.upper()} speichern',.85+.15*(p-.7)/.3)
            try:export_wiggle(render,size,options,output,work,exporting,self.event.is_set)
            finally:frames.close();self.renderer=None
        progress('Fertig',1.)
        return dict(output=str(output),source=str(path),source_eye_size=original,processing_size=size,model=self.model_name,depth_provider=self.model.session.get_providers(),depth_device_id=self.device_id,renderer='RVS CPU Precision 2 Multispectral 1/4',matching_offset=offset,elapsed_seconds=time.monotonic()-start,depth_seconds=depth_seconds,render_stream_wait_seconds=render_seconds,options=options.to_settings())
