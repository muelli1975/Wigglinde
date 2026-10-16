"""First portable converter UI; shared Stereo-Tools palette and interaction rules."""
from pathlib import Path
import json,logging,queue,sys,threading,time,traceback
from tkinter import filedialog,messagebox
import customtkinter as ctk
from . import __version__
from . import theme as T
from .export_options import WiggleOptions
from .processor import Processor,collect_files
from .wiggle_export import ExportCancelled

def app_directory():
    return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]

class WigglindeApp(ctk.CTk):
    def __init__(self,app_dir=None):
        ctk.set_appearance_mode('dark');super().__init__()
        self.app_dir=Path(app_dir or app_directory());self.settings_path=self.app_dir/'settings.json'
        try:self.settings=json.loads(self.settings_path.read_text(encoding='utf-8'))
        except (OSError,ValueError):self.settings={}
        self.title(f'Wigglinde – {__version__} Testversion');self.geometry('820x680');self.minsize(780,650)
        self.configure(fg_color=T.BG_MAIN);self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.files=[];self.source_root=None;self.controls=[];self.running=False;self.processor=None
        self.events=queue.Queue();self.cancel_event=threading.Event();self.started=0
        self.layout=ctk.StringVar(value=self.settings.get('layout','Full-SBS'));self.swap=ctk.BooleanVar(value=False)
        self.standard=ctk.BooleanVar(value=self.settings.get('standard_output',True));self.own=ctk.StringVar(value=self.settings.get('own_output',''))
        self.kind=ctk.StringVar(value='MP4');self.size=ctk.StringVar(value='1080');self.fps=ctk.StringVar(value='30');self.duration=ctk.StringVar(value='2')
        self._build();self._dependencies();self.protocol('WM_DELETE_WINDOW',self._close);self.after(100,self._poll)

    def _label(self,parent,text,**kw):return ctk.CTkLabel(parent,text=text,text_color=T.TEXT,font=(T.FONT_FAMILY,13),**kw)
    def _button(self,parent,text,command,**kw):
        b=ctk.CTkButton(parent,text=text,command=command,fg_color=T.BUTTON_BG,hover_color=T.BUTTON_HOVER,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,border_width=1,border_color=T.BORDER,height=30,**kw);self.controls.append(b);return b
    def _menu(self,parent,variable,values,command=None,width=140):
        b=ctk.CTkOptionMenu(parent,variable=variable,values=values,command=command,width=width,height=30,fg_color=T.PANEL,button_color=T.PANEL_HOVER,button_hover_color=T.BORDER,dropdown_fg_color=T.BG_SOFT,dropdown_hover_color=T.PANEL_HOVER,text_color=T.TEXT,dropdown_text_color=T.TEXT);self.controls.append(b);return b
    def _check(self,parent,text,var,command=None):
        b=ctk.CTkCheckBox(parent,text=text,variable=var,command=command,fg_color=T.GOLD,hover_color=T.GOLD_LIGHT,border_color=T.BORDER,text_color=T.TEXT,text_color_disabled=T.TEXT_DISABLED,height=24);self.controls.append(b);return b
    def _entry(self,parent,var,width=140):
        b=ctk.CTkEntry(parent,textvariable=var,width=width,height=30,fg_color=T.BG_SOFT,border_color=T.BORDER,text_color=T.TEXT);self.controls.append(b);return b
    def _panel(self,row):
        f=ctk.CTkFrame(self,fg_color=T.PANEL,border_width=1,border_color=T.BORDER,corner_radius=12);f.grid(row=row,column=0,sticky='ew',padx=18,pady=(0,9));f.grid_columnconfigure(0,weight=1);return f
    def _build(self):
        head=ctk.CTkFrame(self,fg_color='transparent');head.grid(row=0,column=0,sticky='ew',padx=22,pady=(14,9));head.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(head,text='Wigglinde',font=(T.FONT_FAMILY,25,'bold'),text_color=T.GOLD_LIGHT).grid(row=0,column=0,sticky='w')
        self._label(head,f'{__version__} Testversion · LAS2-M / RVS · CPU').grid(row=0,column=1,sticky='e')
        f=self._panel(1);f.grid(sticky='nsew');f.grid_rowconfigure(1,weight=1);bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=0,column=0,sticky='ew',padx=12,pady=(8,4));bar.grid_columnconfigure(0,weight=1)
        self.input_label=self._label(bar,'Eingabe · Keine Bilder gewählt.');self.input_label.grid(row=0,column=0,sticky='w')
        self._button(bar,'Dateien auswählen',self._choose_files,width=145).grid(row=0,column=1,padx=(8,6))
        self._button(bar,'Ordner auswählen',self._choose_folder,width=145).grid(row=0,column=2)
        self.file_list=ctk.CTkTextbox(f,height=49,fg_color=T.BG_SOFT,text_color=T.TEXT,corner_radius=5,font=(T.FONT_FAMILY,12));self.file_list.grid(row=1,column=0,sticky='nsew',padx=12,pady=(0,8));self.file_list.configure(state='disabled')
        f=self._panel(2);self._check(f,'Unterordner im Eingabeordner verwenden',self.standard,self._dependencies).grid(row=0,column=0,sticky='w',padx=12,pady=(9,5))
        own=ctk.CTkFrame(f,fg_color='transparent');own.grid(row=1,column=0,sticky='ew',padx=12,pady=(0,5));own.grid_columnconfigure(1,weight=1)
        self.own_label=self._label(own,'Eigener Ausgabeordner');self.own_label.grid(row=0,column=0,padx=(0,12))
        self.own_entry=self._entry(own,self.own);self.own_entry.grid(row=0,column=1,sticky='ew',padx=(0,8))
        self._button(own,'Auswählen',self._choose_output,width=110).grid(row=0,column=2)
        self.output_label=self._label(f,'Ausgabeziel: Nach der Eingabeauswahl',anchor='w',wraplength=740,justify='left');self.output_label.grid(row=2,column=0,sticky='ew',padx=12,pady=(0,7))
        f=self._panel(3);bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=0,column=0,sticky='ew',padx=12,pady=(9,6));bar.grid_columnconfigure(5,weight=1)
        self._label(bar,'Format').grid(row=0,column=0,padx=(0,8));self._menu(bar,self.kind,['MP4','GIF','PNG-Bildfolge'],self._format_changed,150).grid(row=0,column=1,padx=(0,18))
        self._label(bar,'Größe').grid(row=0,column=2,padx=(0,8));self.size_menu=self._menu(bar,self.size,['720','1080','2160'],width=100);self.size_menu.grid(row=0,column=3)
        self.unit_label=self._label(bar,'px Höhe');self.unit_label.grid(row=0,column=4,padx=(6,18))
        self._label(bar,'fps').grid(row=0,column=6,padx=(0,8));self.fps_menu=self._menu(bar,self.fps,['30','60'],width=80);self.fps_menu.grid(row=0,column=7)
        bar=ctk.CTkFrame(f,fg_color='transparent');bar.grid(row=1,column=0,sticky='ew',padx=12,pady=(0,9));bar.grid_columnconfigure(2,weight=1)
        self._label(bar,'Zyklusdauer (s)').grid(row=0,column=0,padx=(0,10));self._entry(bar,self.duration,75).grid(row=0,column=1)
        self._menu(bar,self.layout,['Full-SBS','Half-SBS'],width=125).grid(row=0,column=3,padx=(12,16))
        self._check(bar,'L/R tauschen',self.swap).grid(row=0,column=4)
        f=self._panel(4);self.status=self._label(f,'Bereit.',anchor='w');self.status.grid(row=0,column=0,sticky='ew',padx=12,pady=(8,0))
        self.current=self._label(f,'',anchor='w');self.current.grid(row=1,column=0,sticky='ew',padx=12)
        self.progress=ctk.CTkProgressBar(f,fg_color=T.BORDER,progress_color=T.GOLD,height=8);self.progress.grid(row=2,column=0,sticky='ew',padx=12,pady=(4,4));self.progress.set(0)
        self.elapsed=self._label(f,'',anchor='w');self.elapsed.grid(row=3,column=0,sticky='ew',padx=12,pady=(0,5))
        footer=ctk.CTkFrame(self,fg_color='transparent');footer.grid(row=5,column=0,sticky='ew',padx=18,pady=(0,12));footer.grid_columnconfigure(0,weight=1)
        self.start=self._button(footer,'Start',self._start,width=150);self.start.grid(row=0,column=1,padx=(0,8))
        self.start.configure(fg_color=T.START_BG,hover_color=T.START_HOVER_BG,text_color=T.START_TEXT,border_color=T.START_BORDER)
        self.start.bind('<Enter>',lambda event:self.start.configure(text_color=T.START_HOVER_TEXT) if not self.running and self.files else None)
        self.start.bind('<Leave>',lambda event:self.start.configure(text_color=T.START_TEXT))
        self.stop=ctk.CTkButton(footer,text='Abbrechen',command=self._cancel,width=120,height=30,fg_color=T.BG_SOFT,hover_color=T.PANEL_HOVER,border_color=T.BORDER,border_width=1,text_color=T.TEXT,state='disabled');self.stop.grid(row=0,column=2)

    def _format_changed(self,*_):
        kind=self.kind.get();self.size_menu.configure(values={'MP4':['720','1080','2160'],'GIF':['640','800','1024'],'PNG-Bildfolge':['1080','2160']}[kind]);self.size.set('800' if kind=='GIF' else '1080')
        self.fps_menu.configure(values=['10','15','20','25'] if kind=='GIF' else ['30','60']);self.fps.set('15' if kind=='GIF' else '30');self.unit_label.configure(text='px lange Seite' if kind=='GIF' else 'px Höhe')
    def _set_files(self,files,root=None):
        self.files=[Path(p).resolve() for p in files];self.source_root=Path(root).resolve() if root else None
        self.input_label.configure(text=f'Eingabe · {len(self.files)} '+('Bild' if len(self.files)==1 else 'Bilder') if self.files else 'Eingabe · Keine Bilder gewählt.')
        self.file_list.configure(state='normal');self.file_list.delete('1.0','end');self.file_list.insert('1.0','\n'.join(str(p) for p in self.files));self.file_list.configure(state='disabled');self._dependencies()
    def _choose_files(self):
        files=filedialog.askopenfilenames(parent=self,title='SBS-Bilder auswählen',initialdir=self.settings.get('input_directory',str(Path.home())),filetypes=[('Bilder','*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp')])
        if files:self.settings['input_directory']=str(Path(files[0]).parent);self._set_files(files)
    def _choose_folder(self):
        folder=filedialog.askdirectory(parent=self,title='Eingabeordner auswählen',initialdir=self.settings.get('input_directory',str(Path.home())))
        if folder:
            root=Path(folder);excluded=[root/'output',self.app_dir/'_temp']
            if self.own.get():excluded.append(Path(self.own.get()))
            self.settings['input_directory']=folder;self._set_files(collect_files(root,excluded),root)
    def _choose_output(self):
        folder=filedialog.askdirectory(parent=self,title='Ausgabeordner auswählen',initialdir=self.own.get() or str(Path.home()))
        if folder:self.own.set(folder);self.standard.set(False);self._dependencies()
    def _dependencies(self):
        if self.running:return
        own=not self.standard.get();self.own_entry.configure(state='normal' if own else 'disabled',text_color=T.TEXT if own else T.TEXT_DISABLED);self.own_label.configure(text_color=T.TEXT if own else T.TEXT_DISABLED)
        self.start.configure(state='normal' if self.files else 'disabled',text_color=T.START_TEXT)
        if own:target=self.own.get() or 'Bitte eigenen Ausgabeordner auswählen'
        elif self.source_root:target=str(self.source_root/'output')
        elif self.files:target=str(self.files[0].parent/'output') if len({p.parent for p in self.files})==1 else 'Jeweils <Eingabeordner>/output'
        else:target='Nach der Eingabeauswahl'
        self.output_label.configure(text='Ausgabeziel: '+target)
    def _wiggle_options(self):
        kind={'MP4':'mp4','GIF':'gif','PNG-Bildfolge':'png'}[self.kind.get()]
        size=int(self.size.get());fps=int(self.fps.get());duration=float(self.duration.get().replace(',','.'))
        return WiggleOptions(format=kind,video_fps=fps if kind=='mp4' else 30,gif_fps=fps if kind=='gif' else 15,png_fps=fps if kind=='png' else 30,video_height=size if kind=='mp4' else 1080,gif_long_side=size if kind=='gif' else 800,png_height=size if kind=='png' else 1080,cycle_seconds=duration)
    def _save(self):
        self.settings.update(standard_output=self.standard.get(),own_output=self.own.get(),layout=self.layout.get())
        self.settings_path.write_text(json.dumps(self.settings,ensure_ascii=False,indent=2),encoding='utf-8')
    def _start(self):
        if self.running or not self.files:return
        try:
            options=self._wiggle_options();options.validate()
            if not self.standard.get() and not self.own.get():raise ValueError('Bitte einen Ausgabeordner auswählen.')
            self._save()
        except (ValueError,OSError) as e:messagebox.showerror('Wigglinde',str(e),parent=self);return
        self.running=True;self.cancel_event.clear();self.started=time.monotonic();self.progress.set(0)
        for c in self.controls:
            c.configure(state='disabled')
            if isinstance(c,ctk.CTkEntry):c.configure(text_color=T.TEXT_DISABLED)
        self.stop.configure(state='normal');self.status.configure(text='Verarbeitung startet …')
        files=list(self.files);root=self.source_root;standard=self.standard.get();own=Path(self.own.get());layout=self.layout.get();swap=self.swap.get()
        threading.Thread(target=self._work,args=(files,root,standard,own,layout,swap,options),daemon=True).start()
    def _work(self,files,root,standard,own,layout,swap,options):
        completed=0;errors=[];cancelled=False
        try:
            (self.app_dir/'logs').mkdir(exist_ok=True)
            self.processor=Processor(self.app_dir,self.cancel_event)
            for i,path in enumerate(files):
                if self.cancel_event.is_set():raise ExportCancelled()
                self.events.put(('file',f'{i+1}/{len(files)} · {path.name}'))
                base=(root/'output' if root else path.parent/'output') if standard else own
                target=base/path.parent.relative_to(root) if root else base
                def progress(text,p):self.events.put(('progress',(text,(i+p)/len(files))))
                try:
                    result=self.processor.convert(path,target,options,layout,swap,progress);completed+=1
                    with (self.app_dir/'logs/wigglinde.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
                except ExportCancelled:raise
                except Exception as e:
                    message=str(e)
                    if isinstance(e,MemoryError) or any(s in message.lower() for s in ['bad_alloc','out of memory','failed to allocate','not enough memory']):
                        message='Der Arbeitsspeicher reicht für diese Berechnungsgröße nicht aus. Bitte eine kleinere Größe wählen.'
                    errors.append(f'{path.name}: {message}')
                    with (self.app_dir/'logs/errors.log').open('a',encoding='utf-8') as f:f.write(traceback.format_exc()+'\n')
        except ExportCancelled:cancelled=True
        except Exception as e:errors.append(str(e))
        finally:self.processor=None;self.events.put(('done',(completed,errors,cancelled)))
    def _cancel(self):
        self.cancel_event.set();self.stop.configure(state='disabled');self.status.configure(text='Abbruch wird ausgeführt …')
        if self.processor:self.processor.cancel()
    def _poll(self):
        try:
            while True:
                kind,payload=self.events.get_nowait()
                if kind=='file':self.current.configure(text=payload[:105])
                elif kind=='progress':self.status.configure(text=payload[0]);self.progress.set(payload[1])
                elif kind=='done':
                    completed,errors,cancelled=payload;self.running=False
                    for c in self.controls:
                        c.configure(state='normal')
                        if isinstance(c,ctk.CTkEntry):c.configure(text_color=T.TEXT)
                    self.stop.configure(state='disabled');self._dependencies()
                    self.status.configure(text=f'{"Abgebrochen" if cancelled else "Fertig"}: {completed} Ausgaben'+(f' · {len(errors)} Fehler' if errors else ''))
                    if not cancelled:self.progress.set(1)
                    if errors:messagebox.showerror('Wigglinde','\n\n'.join(errors[:4])+'\n\nDetails: logs/errors.log',parent=self)
        except queue.Empty:pass
        if self.running:
            seconds=int(time.monotonic()-self.started);self.elapsed.configure(text=f'Verstrichen: {seconds//60:02d}:{seconds%60:02d}')
        self.after(100,self._poll)
    def _close(self):
        if self.running:self._cancel();self.after(150,self._close);return
        try:self._save()
        except OSError:pass
        self.destroy()

def main():
    root=app_directory()
    if len(sys.argv)>1 and sys.argv[1]=='--self-test':
        from .smoke import run
        run(root,Path(sys.argv[2]));return
    WigglindeApp(root).mainloop()
