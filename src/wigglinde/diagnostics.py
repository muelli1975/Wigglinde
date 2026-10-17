"""Bounded local logs and stage timing. No geometry tests or network operations."""
from contextlib import contextmanager
from datetime import datetime,timezone
import base64
import ctypes
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import time
import traceback
import uuid
from . import __version__
from .memory import MemorySampler

MAX_LOG_BYTES=5*1024*1024
LOG_BACKUPS=3


def exception_details(error):
    chain=[];seen=set()
    while error is not None and id(error) not in seen and len(chain)<8:
        seen.add(id(error));item=dict(type=type(error).__name__,message=str(error)[:16000])
        if isinstance(error,UnicodeDecodeError):
            raw=bytes(error.object);part=raw[:32768]
            encoding='cp'+str(ctypes.windll.kernel32.GetACP()) if sys.platform=='win32' else 'cp1252'
            item.update(bytes_base64=base64.b64encode(part).decode('ascii'),byte_length=len(raw),bytes_truncated=len(part)!=len(raw),
                        failed_encoding=error.encoding,start=error.start,end=error.end,
                        candidate_encoding=encoding,candidate_text=part.decode(encoding,errors='backslashreplace'))
        chain.append(item);error=error.__cause__ or error.__context__
    return chain


def error_message(error):
    parts=[]
    for item in exception_details(error):
        text=item.get('candidate_text') or item['message']
        if text not in parts:parts.append(text)
    return '\n'.join(parts)


def memory_failure(error):
    if isinstance(error,MemoryError):return True
    text=error_message(error).lower()
    return any(token in text for token in ['bad_alloc','out of memory','outofmemory','failed to allocate',
        'not enough memory','0x8007000e','e_outofmemory','nicht genügend speicher','nicht genug speicher'])


class LocalLogs:
    def __init__(self,app_dir,max_bytes=MAX_LOG_BYTES,backups=LOG_BACKUPS):
        self.folder=Path(app_dir)/'logs';self.folder.mkdir(exist_ok=True,parents=True);self.handlers={}
        for key,name in [('events','wigglinde.jsonl'),('errors','errors.log')]:
            handler=RotatingFileHandler(self.folder/name,maxBytes=max_bytes,backupCount=backups,encoding='utf-8',errors='backslashreplace')
            handler.setFormatter(logging.Formatter('%(message)s'));self.handlers[key]=handler

    def write(self,key,data):
        text=json.dumps(data,ensure_ascii=False,default=str)
        self.handlers[key].emit(logging.LogRecord('wigglinde',logging.INFO,'',0,text,(),None))

    def close(self):
        for handler in self.handlers.values():handler.close()

    def latest(self,data):
        temporary=self.folder/'latest_run.partial.json'
        temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
        os.replace(temporary,self.folder/'latest_run.json')


class RunTrace:
    def __init__(self,logs,context,device_id=None,child=lambda:None):
        self.logs=logs;self.data=dict(schema_version=1,version=__version__,run_id=uuid.uuid4().hex,
            started_at=datetime.now(timezone.utc).isoformat(),**context)
        self.memory=MemorySampler(device_id,child);self.timings={};self.current='starting'

    def event(self,event,**fields):
        self.logs.write('events',dict(timestamp=datetime.now(timezone.utc).isoformat(),run_id=self.data['run_id'],event=event,**fields))

    def __enter__(self):
        self.started=time.perf_counter();self.memory.__enter__();self.event('started',context=self.data);self.logs.latest(dict(self.data,status='running'));return self

    @contextmanager
    def stage(self,name):
        self.current=name;self.memory.sample(name);begin=time.perf_counter();self.event('stage_started',stage=name)
        self.logs.latest(dict(self.data,status='running',current_stage=name,stage_seconds=dict(self.timings)))
        try:yield
        finally:
            self.timings[name]=time.perf_counter()-begin;self.memory.sample();self.event('stage_finished',stage=name,seconds=self.timings[name])

    def __exit__(self,kind,error,tb):
        self.memory.__exit__(kind,error,tb)
        from .wiggle_export import ExportCancelled
        self.data.update(status='cancelled' if isinstance(error,ExportCancelled) else 'failed' if error else 'passed',
            finished_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-self.started,
            stage_seconds=self.timings,memory=self.memory.report())
        if error:
            self.data.update(failed_stage=self.current,exceptions=exception_details(error))
            if not isinstance(error,ExportCancelled):
                self.logs.write('errors',dict(**self.data,traceback=''.join(traceback.format_exception(kind,error,tb))[:65536]))
        self.event('finished',result=self.data)
        self.logs.latest(self.data)
        return False
