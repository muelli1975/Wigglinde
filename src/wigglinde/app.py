"""Portable converter with the shared Stereo-Tools controls and path selection."""
from pathlib import Path
import json,queue,sys,threading,time
from tkinter import filedialog,messagebox
import customtkinter as ctk
from . import __version__,theme as T
from .devices import graphics_adapters
from .models import DEFAULT_MODEL
from .diagnostics import error_message,memory_failure
from .i18n import tr,message,TEXT
from .export_options import WiggleOptions
from .blending_options import BlendingOptions
from .processor import Processor,collect_files,EXTENSIONS
from .wiggle_export import ExportCancelled

def app_directory():
    if getattr(sys,'frozen',False):
        executable=Path(sys.executable).resolve()
        # Keep portable settings/models beside the .app, outside its signed contents.
        if sys.platform=='darwin' and executable.parent.name=='MacOS' and executable.parents[2].suffix=='.app':
            return executable.parents[3]
        return executable.parent
    return Path(__file__).resolve().parents[2]

def screen_work_area(window):
    if sys.platform=='win32':
        import ctypes
        from ctypes.wintypes import RECT
        area=RECT()
        if ctypes.windll.user32.SystemParametersInfoW(0x0030,0,ctypes.byref(area),0):
            return area.left,area.top,area.right,area.bottom
    return 0,0,window.winfo_screenwidth(),window.winfo_screenheight()

class WigglindeApp(ctk.CTk):
    def __init__(self,app_dir=None):
        ctk.set_appearance_mode('dark');super().__init__()
        self.app_dir=Path(app_dir or app_directory());self.settings_path=self.app_dir/'settings.json'
        icon=self.app_dir/'assets/wigglinde.ico'
        if sys.platform=='win32' and icon.is_file():self.iconbitmap(default=str(icon))
        elif icon.is_file():
            from PIL import Image,ImageTk
            with Image.open(icon) as image:self._window_icon=ImageTk.PhotoImage(image.convert('RGBA'),master=self)
            self.iconphoto(True,self._window_icon)
        try:self.settings=json.loads(self.settings_path.read_text(encoding='utf-8'))
        except (OSError,ValueError):self.settings={}
        self.locale=self.settings.get('language','de');self.locale='en' if self.locale=='en' else 'de'
        left,top,right,bottom=screen_work_area(self);scale=self._get_window_scaling()
        width=min(820,max(780,int((right-left-32)/scale)))
        height=min(690,max(640,int((bottom-top-72)/scale)))
        x=left+max(0,(right-left-round(width*scale))//2)
        y=top+max(0,(bottom-top-round(height*scale)-40)//2)
        self.minsize(780,640);self.geometry(f'{width}x{height}+{x}+{y}')
        self.configure(fg_color=T.BG_MAIN);self.grid_columnconfigure(0,weight=1);self.grid_rowconfigure(4,weight=1)
        self.files=[];self.source_root=None;self.controls=[];self.running=False;self.processor=None
        self.events=queue.Queue();self.cancel_event=threading.Event();self.started=0
        self.settings.pop('layout',None)
        self.standard=ctk.BooleanVar(value=self.settings.get('standard_output',True));self.own=ctk.StringVar(value=self.settings.get('own_output',''))
        self.input_file=ctk.StringVar(value=self.settings.get('last_input_file',''))
        self.input_folder=ctk.StringVar(value='' if self.input_file.get() else self.settings.get('last_input_folder',''));self.changing_input=False
        saved_options=WiggleOptions.from_settings(self.settings.get('wiggle',{}))
        self.kind=ctk.StringVar(value=self.tr('png') if saved_options.format=='png' else saved_options.format.upper())
        saved_size={'mp4':saved_options.video_height,'gif':saved_options.gif_long_side,'png':saved_options.png_height}[saved_options.format]
        self.size=ctk.StringVar(value=str(saved_size));self.fps=ctk.StringVar(value=str(saved_options.fps));self.duration=ctk.StringVar(value=f'{saved_options.cycle_seconds:g}')
        blend=BlendingOptions.from_settings(self.settings.get('blending',{}))
        self.blending_method=ctk.StringVar(value=blend.method)
        self.blending_low=ctk.StringVar(value=f'{blend.low_factor:g}')
        self.blending_high=ctk.StringVar(value=f'{blend.high_factor:g}')
        self.blending_simple=ctk.StringVar(value=f'{blend.simple_factor:g}')
        self.save_depth=ctk.BooleanVar(value=self.settings.get('save_depth',False) is True)
        self.settings.pop('model',None)
        self.language=ctk.StringVar(value='English' if self.locale=='en' else 'Deutsch')
        self.adapters={'CPU':None,**{f'GPU {i}: {name}':i for i,name in graphics_adapters()}}
        saved=self.settings.get('device_id')
        if saved is not None and saved not in self.adapters.values():self.adapters[f'GPU {saved} ({self.tr("unavailable")})']=saved
        label=next(label for label,ident in self.adapters.items() if ident==saved)
        self.device=ctk.StringVar(value=label);self.status_value=('ready',{});self.last_file='';self.elapsed_seconds=None;self.error_count=0
        self.localized=[];self._build();self._dependencies()
        self.input_file.trace_add('write',lambda *_:self._input_changed(self.input_file,self.input_folder))
        self.input_folder.trace_add('write',lambda *_:self._input_changed(self.input_folder,self.input_file))
        self.own.trace_add('write',lambda *_:self._dependencies())
        self.protocol('WM_DELETE_WINDOW',self._close);self.after(100,self._poll)

    def tr(self,key,**values):return tr(self.locale,key,**values)
    def _localize(self,widget,key):
        if key in TEXT:self.localized.append((widget,key))
        return widget
    def _label(self,parent,text,**kw):
        return self._localize(ctk.CTkLabel(parent,text=self.tr(text) if text in TEXT else text,text_color=T.TEXT,font=(T.FONT_FAMILY,13),**kw),text)
    def _button(self,parent,text,command,**kw):
        b=ctk.CTkButton(parent,text=self.tr(text) if text in TEXT else text,command=command,fg_color=T.BUTTON_BG,hover_color=T.BUTTON_HOVER,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,border_width=T.BORDER_WIDTH,border_color=T.BORDER,corner_radius=T.RADIUS_CONTROL,height=30,**kw);b.grid_propagate(False);self.controls.append(b);return self._localize(b,text)
    def _menu(self,parent,variable,values,command=None,width=140):
        b=ctk.CTkOptionMenu(parent,variable=variable,values=values,command=command,width=width,height=30,dynamic_resizing=False,fg_color=T.PANEL,button_color=T.PANEL_HOVER,button_hover_color=T.BORDER,dropdown_fg_color=T.BG_SOFT,dropdown_hover_color=T.PANEL_HOVER,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,dropdown_text_color=T.TEXT);self.controls.append(b);return b
    def _check(self,parent,text,var,command=None):
        b=ctk.CTkCheckBox(parent,text=self.tr(text) if text in TEXT else text,variable=var,command=command,fg_color=T.GOLD,hover_color=T.GOLD_LIGHT,border_color=T.BORDER,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,height=24);self.controls.append(b);return self._localize(b,text)
    def _entry(self,parent,var,width=140):
        b=ctk.CTkEntry(parent,textvariable=var,width=width,height=30,fg_color=T.BG_SOFT,border_color=T.BORDER,text_color=T.TEXT);self.controls.append(b);return b
    def _panel(self,row):
        f=ctk.CTkFrame(self,fg_color=T.PANEL,border_width=1,border_color=T.BORDER,corner_radius=12);f.grid(row=row,column=0,sticky='ew',padx=18,pady=(0,9));f.grid_columnconfigure(0,weight=1);return f
    def _path_row(self,parent,row,key,var,command):
        bar=ctk.CTkFrame(parent,fg_color='transparent');bar.grid(row=row,column=0,sticky='ew',padx=12,pady=(8 if row==0 else 0,8));bar.grid_columnconfigure(1,weight=1)
        self._label(bar,key,width=158,anchor='w').grid(row=0,column=0,sticky='w',padx=(0,8))
        entry=self._entry(bar,var);entry.grid(row=0,column=1,sticky='ew',padx=(0,8))
        self._button(bar,'choose',command,width=110).grid(row=0,column=2)
        return entry
    def _build(self):
        self.title(f'Wigglinde – {__version__}')
        head=ctk.CTkFrame(self,fg_color='transparent');head.grid(row=0,column=0,sticky='ew',padx=22,pady=(12,9));head.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(head,text='Wigglinde',font=(T.FONT_FAMILY,25,'bold'),text_color=T.GOLD_LIGHT).grid(row=0,column=0,sticky='w')
        self._label(head,'version').grid(row=0,column=1,padx=(8,20))
        self._menu(head,self.language,['Deutsch','English'],self._language_changed,120).grid(row=0,column=2)
        f=self._panel(1)
        self.file_entry=self._path_row(f,0,'single',self.input_file,self._choose_file)
        self.folder_entry=self._path_row(f,1,'folder',self.input_folder,self._choose_folder)
        f=self._panel(2);self._check(f,'standard',self.standard,self._dependencies).grid(row=0,column=0,sticky='w',padx=12,pady=(9,5))
        own=ctk.CTkFrame(f,fg_color='transparent');own.grid(row=1,column=0,sticky='ew',padx=12,pady=(0,5));own.grid_columnconfigure(1,weight=1)
        self.own_label=self._label(own,'own',width=158,anchor='w');self.own_label.grid(row=0,column=0,padx=(0,8))
        self.own_entry=self._entry(own,self.own);self.own_entry.grid(row=0,column=1,sticky='ew',padx=(0,8))
        self._button(own,'choose',self._choose_output,width=110).grid(row=0,column=2)
        self.output_label=self._label(f,'',anchor='w',wraplength=740,justify='left');self.output_label.grid(row=2,column=0,sticky='ew',padx=12,pady=(0,7))
        f=self._panel(3);bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=0,column=0,sticky='ew',padx=12,pady=(9,6));bar.grid_columnconfigure(5,weight=1)
        self._label(bar,'format').grid(row=0,column=0,padx=(0,8));self.format_menu=self._menu(bar,self.kind,['MP4','GIF',self.tr('png')],self._format_changed,150);self.format_menu.grid(row=0,column=1,padx=(0,18))
        self._label(bar,'size').grid(row=0,column=2,padx=(0,8));self.size_menu=self._menu(bar,self.size,self._sizes(),width=100);self.size_menu.grid(row=0,column=3)
        self.unit_label=self._label(bar,self.tr('long_side' if self.kind.get()=='GIF' else 'height'));self.unit_label.grid(row=0,column=4,padx=(6,18))
        self._label(bar,'fps').grid(row=0,column=6,padx=(0,8));self.fps_menu=self._menu(bar,self.fps,self._rates(),width=80);self.fps_menu.grid(row=0,column=7)
        bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=1,column=0,sticky='ew',padx=12,pady=(0,6));bar.grid_columnconfigure(2,weight=1)
        self._label(bar,'duration').grid(row=0,column=0,padx=(0,10));self._entry(bar,self.duration,75).grid(row=0,column=1)
        bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=2,column=0,sticky='ew',padx=12,pady=(0,9));bar.grid_columnconfigure(3,weight=1)
        self._label(bar,'model').grid(row=0,column=0,padx=(0,8))
        self._label(bar,DEFAULT_MODEL,width=112,anchor='w').grid(row=0,column=1,sticky='w')
        self._label(bar,'device').grid(row=0,column=2,padx=(16,8))
        self._menu(bar,self.device,list(self.adapters),width=245).grid(row=0,column=3,sticky='w')
        self._label(bar,'renderer').grid(row=0,column=4,padx=(12,0))
        bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=3,column=0,sticky='ew',padx=12,pady=(0,9))
        self._label(bar,'blending',width=140,anchor='w').grid(row=0,column=0,padx=(0,8))
        self.blending_menu=self._menu(bar,self.blending_method,['Multispectral','Simple'],self._blending_changed,140);self.blending_menu.grid(row=0,column=1,padx=(0,12))
        self.blending_first_label=self._label(bar,'',width=85,anchor='w');self.blending_first_label.grid(row=0,column=2,padx=(0,6))
        self.blending_first_entry=self._entry(bar,self.blending_low,70);self.blending_first_entry.grid(row=0,column=3,padx=(0,12))
        self.blending_high_label=self._label(bar,'blend_high',width=50,anchor='w');self.blending_high_label.grid(row=0,column=4,padx=(0,6))
        self.blending_high_entry=self._entry(bar,self.blending_high,70);self.blending_high_entry.grid(row=0,column=5)
        for entry in (self.blending_first_entry,self.blending_high_entry):entry.bind('<FocusOut>',lambda event:self._save_quietly())
        bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=4,column=0,sticky='ew',padx=12,pady=(0,9));bar.grid_columnconfigure(0,weight=1)
        self.depth_check=self._check(bar,'save_depth',self.save_depth,self._save_quietly)
        self.depth_check.grid(row=0,column=0,sticky='w')
        self.blending_reset=self._button(bar,'reset_blending',self._reset_blending,width=170);self.blending_reset.grid(row=0,column=1)
        f=self._panel(4);f.grid(sticky='nsew');f.grid_rowconfigure(0,weight=1)
        self.status=self._label(f,'',anchor='w');self.status.grid(row=0,column=0,sticky='ew',padx=12,pady=(6,0))
        self.current=self._label(f,self.last_file,anchor='w');self.current.grid(row=1,column=0,sticky='ew',padx=12)
        self.progress=ctk.CTkProgressBar(f,fg_color=T.BORDER,progress_color=T.GOLD,height=8);self.progress.grid(row=2,column=0,sticky='ew',padx=12,pady=(4,4));self.progress.set(0)
        self.elapsed=self._label(f,'',anchor='w');self.elapsed.grid(row=3,column=0,sticky='ew',padx=12,pady=(0,5))
        self._show_status();self._show_elapsed()
        footer=ctk.CTkFrame(self,fg_color='transparent');footer.grid(row=5,column=0,sticky='ew',padx=18,pady=(0,12));footer.grid_columnconfigure(0,weight=1)
        self.diagnose_button=self._button(footer,'diagnose',lambda:self._start(True),width=220);self.diagnose_button.grid(row=0,column=0,sticky='w',padx=(0,12))
        self.start=self._button(footer,'start',self._start,width=150);self.start.grid(row=0,column=1,padx=(0,8))
        self.start.bind('<Enter>',lambda event:self.after_idle(lambda:self._style_start(hover=True)),add='+')
        self.start.bind('<Leave>',lambda event:self.after_idle(self._style_start),add='+')
        self.stop=ctk.CTkButton(footer,text=self.tr('cancel'),command=self._cancel,width=120,height=30,fg_color=T.BUTTON_BG,hover_color=T.BUTTON_HOVER,border_color=T.BORDER,border_width=T.BORDER_WIDTH,corner_radius=T.RADIUS_CONTROL,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,state='disabled');self.stop.grid_propagate(False);self.stop.grid(row=0,column=2)

    def _style_start(self,hover=False):
        if not self.start.winfo_exists():return
        enabled=self.start.cget('state')=='normal';hovered=enabled and hover
        self.start.configure(
            fg_color=T.START_HOVER_BG if hovered else T.START_BG if enabled else T.START_DISABLED_BG,
            hover_color=T.START_HOVER_BG if enabled else T.START_DISABLED_BG,
            text_color=T.START_HOVER_TEXT if hovered else T.START_TEXT if enabled else T.START_DISABLED_TEXT,
            border_color=T.START_HOVER_BORDER if hovered else T.START_BORDER if enabled else T.START_DISABLED_BORDER,
        )

    def _kind(self):return self.kind.get() if self.kind.get() in ('MP4','GIF') else 'PNG'
    def _sizes(self):return {'MP4':['720','1080','2160'],'GIF':['640','800','1024'],'PNG':['1080','2160']}[self._kind()]
    def _rates(self):return ['10','15','20','25'] if self._kind()=='GIF' else ['30','60']
    def _format_changed(self,*_):
        self.size_menu.configure(values=self._sizes());self.size.set({'GIF':'800','MP4':'720','PNG':'1080'}[self._kind()])
        self.fps_menu.configure(values=self._rates());self.fps.set('15' if self._kind()=='GIF' else '30');self.unit_label.configure(text=self.tr('long_side' if self._kind()=='GIF' else 'height'))
    def _language_changed(self,*_):
        kind=self._kind();self.locale='en' if self.language.get()=='English' else 'de'
        for widget,key in self.localized:widget.configure(text=self.tr(key))
        self.format_menu.configure(values=['MP4','GIF',self.tr('png')])
        if kind=='PNG':self.kind.set(self.tr('png'))
        self.unit_label.configure(text=self.tr('long_side' if kind=='GIF' else 'height'))
        self.stop.configure(text=self.tr('cancel'))
        self.title(f'Wigglinde – {__version__}')
        self._show_status();self._show_elapsed();self._dependencies();self._save_quietly()
    def _blending_dependencies(self):
        simple=self.blending_method.get()=='Simple'
        self.blending_first_label.configure(text=self.tr('blend_weight' if simple else 'blend_low'),text_color=T.TEXT_DISABLED if self.running else T.TEXT)
        self.blending_first_entry.configure(textvariable=self.blending_simple if simple else self.blending_low)
        enabled=not simple and not self.running
        self.blending_high_entry.configure(state='normal' if enabled else 'disabled',text_color=T.TEXT if enabled else T.TEXT_DISABLED)
        self.blending_high_label.configure(text_color=T.TEXT if enabled else T.TEXT_DISABLED)
    def _blending_changed(self,*_):
        self._blending_dependencies();self._save_quietly()
    def _reset_blending(self):
        self.blending_low.set('1');self.blending_high.set('4');self.blending_simple.set('5');self._save_quietly()
    def _blending_options(self):
        values=BlendingOptions.from_settings(self.settings.get('blending',{})).to_settings()
        method=self.blending_method.get();values['method']=method
        for key,var in [('low_factor',self.blending_low),('high_factor',self.blending_high),('simple_factor',self.blending_simple)]:
            active=(key=='simple_factor')==(method=='Simple')
            try:
                value=float(var.get().replace(',','.'))
                BlendingOptions(method='Simple',simple_factor=value).validate();values[key]=value
            except (ValueError,OverflowError):
                if active:raise ValueError(self.tr('blend_numbers')) from None
        result=BlendingOptions(**values);result.validate();return result
    def _has_input(self):return bool(self.input_file.get().strip() or self.input_folder.get().strip())
    def _input_changed(self,active,other):
        if self.changing_input:return
        self.changing_input=True
        try:
            if active.get().strip():other.set('')
        finally:self.changing_input=False
        self.files=[];self._set_status('ready');self._dependencies()
    def _choose_file(self):
        path=filedialog.askopenfilename(parent=self,title=self.tr('file_dialog'),initialdir=self.settings.get('input_directory',str(Path.home())),filetypes=[(self.tr('images'),'*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp')])
        if path:self.settings['input_directory']=str(Path(path).parent);self.input_file.set(path);self._save_quietly()
    def _choose_folder(self):
        folder=filedialog.askdirectory(parent=self,title=self.tr('folder_dialog'),initialdir=self.settings.get('input_directory',str(Path.home())))
        if folder:self.settings['input_directory']=folder;self.input_folder.set(folder);self._save_quietly()
    def _choose_output(self):
        folder=filedialog.askdirectory(parent=self,title=self.tr('output_dialog'),initialdir=self.own.get() or str(Path.home()))
        if folder:self.own.set(folder);self.standard.set(False);self._dependencies();self._save_quietly()
    def _dependencies(self):
        self._blending_dependencies()
        if self.running:return
        own=not self.standard.get();self.own_entry.configure(state='normal' if own else 'disabled',text_color=T.TEXT if own else T.TEXT_DISABLED);self.own_label.configure(text_color=T.TEXT if own else T.TEXT_DISABLED)
        self.start.configure(state='normal' if self._has_input() else 'disabled');self._style_start()
        self.diagnose_button.configure(state='normal' if self.input_file.get().strip() else 'disabled')
        if own:target=self.own.get() or self.tr('choose_output')
        elif self.input_folder.get().strip():target=str(Path(self.input_folder.get().strip())/'output')
        elif self.input_file.get().strip():target=str(Path(self.input_file.get().strip()).parent/'output')
        else:target=self.tr('after_input')
        self.output_label.configure(text=self.tr('target',path=target))
    def _wiggle_options(self):
        kind=self._kind().lower()
        try:size=int(self.size.get());fps=int(self.fps.get());duration=float(self.duration.get().replace(',','.'))
        except ValueError:raise ValueError(self.tr('numbers')) from None
        return WiggleOptions(format=kind,video_fps=fps if kind=='mp4' else 30,gif_fps=fps if kind=='gif' else 15,png_fps=fps if kind=='png' else 30,video_height=size if kind=='mp4' else 720,gif_long_side=size if kind=='gif' else 800,png_height=size if kind=='png' else 1080,cycle_seconds=duration,save_depth=self.save_depth.get())
    def _save(self):
        self.settings.update(standard_output=self.standard.get(),own_output=self.own.get(),language=self.locale,device_id=self.adapters[self.device.get()],save_depth=self.save_depth.get(),
            last_input_file=self.input_file.get(),last_input_folder=self.input_folder.get())
        # A partly typed invalid number must not discard the last valid options.
        try:
            options=self._wiggle_options();options.validate();self.settings['wiggle']=options.to_settings()
        except ValueError:pass
        try:self.settings['blending']=self._blending_options().to_settings()
        except ValueError:pass
        temporary=self.settings_path.with_name(self.settings_path.name+'.partial')
        temporary.write_text(json.dumps(self.settings,ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(self.settings_path)
    def _save_quietly(self):
        try:self._save()
        except OSError:pass
    def _collect_input(self):
        file=self.input_file.get().strip();folder=self.input_folder.get().strip()
        if file:
            path=Path(file)
            if not path.is_file() or path.suffix.lower() not in EXTENSIONS:raise ValueError(self.tr('bad_file'))
            return [path.resolve()],None
        if folder:
            root=Path(folder).resolve()
            if not root.is_dir():raise ValueError(self.tr('bad_folder'))
            excluded=[root/'output',self.app_dir/'_temp']
            if self.own.get():excluded.append(Path(self.own.get()))
            files=collect_files(root,excluded)
            if not files:raise ValueError(self.tr('empty'))
            return files,root
        raise ValueError(self.tr('choose_input'))
    def _start(self,depth_only=False):
        if self.running or not self._has_input():return
        if depth_only and not self.input_file.get().strip():return
        try:
            options=self._wiggle_options();options.validate()
            blending=None if depth_only else self._blending_options()
            if not depth_only and not self.standard.get() and not self.own.get().strip():raise ValueError(self.tr('choose_output'))
            self.files,self.source_root=self._collect_input();self._save()
        except (ValueError,OSError) as e:messagebox.showerror('Wigglinde',message(self.locale,str(e)),parent=self);return
        self.running=True;self.cancel_event.clear();self.started=time.monotonic();self.progress.set(0)
        self.diagnosing=depth_only;self.error_count=0;self.last_file='';self.current.configure(text='');self.elapsed_seconds=0;self._show_elapsed()
        self._set_busy(True);self._set_status('starting')
        threading.Thread(target=self._work,args=(list(self.files),self.source_root,self.standard.get(),Path(self.own.get()),options,self.adapters[self.device.get()],self.device.get(),depth_only,blending),daemon=True).start()
    def _set_busy(self,busy):
        for control in self.controls:
            control.configure(state='disabled' if busy else 'normal')
            if isinstance(control,ctk.CTkEntry):control.configure(text_color=T.TEXT_DISABLED if busy else T.TEXT)
            if isinstance(control,ctk.CTkCheckBox):control.configure(fg_color=T.CHECKBOX_DISABLED if busy else T.GOLD,hover_color=T.CHECKBOX_DISABLED if busy else T.GOLD_LIGHT)
        self.stop.configure(state='normal' if busy else 'disabled')
        self._blending_dependencies()
        if busy:self._style_start()
        else:self._dependencies()
    def _set_status(self,key,**values):self.status_value=(key,values);self._show_status()
    def _show_status(self):
        key,values=self.status_value
        text=message(self.locale,values['text']) if key=='pipeline' else self.tr(key,**values)
        if key in ('finished','cancelled') and self.error_count:text+=self.tr('errors',count=self.error_count)
        self.status.configure(text=text)
    def _show_elapsed(self):
        self.elapsed.configure(text='' if self.elapsed_seconds is None else self.tr('elapsed',minutes=self.elapsed_seconds//60,seconds=self.elapsed_seconds%60))
    def _work(self,files,root,standard,own,options,device_id,device_name,depth_only=False,blending=None):
        completed=0;errors=[];cancelled=False;diagnosis=None
        try:
            self.processor=Processor(self.app_dir,self.cancel_event,device_id=device_id,device_name=device_name)
            for i,path in enumerate(files):
                if self.cancel_event.is_set():raise ExportCancelled()
                self.events.put(('file',f'{i+1}/{len(files)} · {path.name}'))
                base=(root/'output' if root else path.parent/'output') if standard else own
                def progress(text,p):self.events.put(('progress',(text,(i+p)/len(files))))
                try:
                    if depth_only:diagnosis=self.processor.diagnose(path,options,progress=progress)
                    else:self.processor.convert(path,base,options,progress=progress,blending=blending)
                    completed+=1
                except ExportCancelled:raise
                except Exception as e:
                    details=error_message(e)
                    if memory_failure(e):details=self.tr('memory')+'\n'+details
                    errors.append(f'{path.name}: {self._error_message(details[:1800])}')
                    if str(e).startswith('GPU_INIT: '):break
        except ExportCancelled:cancelled=True
        except Exception as e:errors.append(self._error_message(str(e)))
        finally:
            if self.processor:self.processor.close()
            self.processor=None;self.events.put(('done',(completed,errors,cancelled,diagnosis)))
    def _error_message(self,text):
        if text.startswith('GPU_INIT: '):return self.tr('gpu_failed',error=text[10:])
        return message(self.locale,text)
    def _cancel(self):
        self.cancel_event.set();self.stop.configure(state='disabled');self._set_status('cancelling')
        if self.processor:self.processor.cancel()
    def _play_ready_sound(self):
        path=self.app_dir/'assets/ready.wav'
        if not path.is_file():return
        try:
            if sys.platform=='win32':
                import winsound
                winsound.PlaySound(str(path),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
            else:
                import shutil,subprocess
                player=shutil.which('afplay') if sys.platform=='darwin' else (shutil.which('paplay') or shutil.which('aplay'))
                if player:subprocess.Popen([player,str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except OSError:pass
    def _poll(self):
        try:
            while True:
                kind,payload=self.events.get_nowait()
                if kind=='file':self.last_file=payload[:105];self.current.configure(text=self.last_file)
                elif kind=='progress':self._set_status('pipeline',text=payload[0]);self.progress.set(payload[1])
                elif kind=='done':
                    completed,errors,cancelled,diagnosis=payload;self.running=False;self.error_count=len(errors);self._set_busy(False)
                    self._set_status('cancelled' if cancelled else 'diagnosed' if diagnosis else 'finished',count=completed)
                    if not cancelled:self.progress.set(1)
                    if completed and not cancelled:self._play_ready_sound()
                    if errors:messagebox.showerror('Wigglinde','\n\n'.join(errors[:4])+'\n\n'+self.tr('details'),parent=self)
                    elif diagnosis:
                        peaks=[s['peak'] for s in diagnosis['memory']['stages'].values()]
                        def peak(name):
                            values=[p[name] for p in peaks if name in p]
                            return f'{max(values)/1024**2:.0f} MiB' if values else '—'
                        messagebox.showinfo('Wigglinde',self.tr('diagnosis_result',size=' × '.join(map(str,diagnosis['processing_size'])),
                            device=diagnosis['device'],depth=f"{diagnosis['depth_seconds']:.2f}",
                            load=f"{diagnosis['stage_seconds'].get('model_load',0):.2f}",
                            ram=peak('main_rss_bytes'),gpu=peak('gpu_process_local_usage_bytes')),parent=self)
        except queue.Empty:pass
        if self.running:self.elapsed_seconds=int(time.monotonic()-self.started);self._show_elapsed()
        self.after(100,self._poll)
    def _close(self):
        if self.running:self._cancel();self.after(150,self._close);return
        self._save_quietly();self.destroy()

def main():
    root=app_directory()
    if len(sys.argv)>1 and sys.argv[1]=='--self-test':
        from .smoke import run
        run(root,Path(sys.argv[2]));return
    WigglindeApp(root).mainloop()
