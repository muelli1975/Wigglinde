"""One spawned processing process per GUI batch; no Tk or model changes.

ORT model loading can hold Python's GIL for seconds. A thread cannot keep Tk
responsive then. Keep the existing Processor, session reuse, logs and native
renderers together in a process; send only small status/result messages to Tk.
"""
from pathlib import Path
import multiprocessing
import queue
import threading
from .diagnostics import error_message,memory_failure
from .processor import Processor
from .wiggle_export import ExportCancelled


def run_batch(request,cancel,events,processor_factory=Processor):
    completed=0;errors=[];cancelled=False;diagnosis=None;processor=None
    finished=threading.Event()
    try:
        processor=processor_factory(request['app_dir'],cancel,device_id=request['device_id'],
            device_name=request['device_name'],model_name=request['model_name'],render_backend=request['render_backend'])
        def watch_cancel():
            while not finished.is_set():
                if cancel.wait(.1):
                    processor.cancel();return
        threading.Thread(target=watch_cancel,daemon=True).start()
        files=request['files'];root=request['root']
        for i,filename in enumerate(files):
            if cancel.is_set():raise ExportCancelled()
            path=Path(filename);events.put(('file',f'{i+1}/{len(files)} · {path.name}'))
            base=(Path(root)/'output' if root else path.parent/'output') if request['standard'] else Path(request['own'])
            def progress(text,p):events.put(('progress',(text,(i+p)/len(files))))
            try:
                if request['depth_only']:diagnosis=processor.diagnose(path,request['options'],progress=progress)
                else:processor.convert(path,base,request['options'],progress=progress)
                completed+=1
            except ExportCancelled:raise
            except Exception as error:
                errors.append(dict(file=path.name,detail=error_message(error),memory=memory_failure(error)))
                if str(error).startswith('GPU_INIT: '):break
    except ExportCancelled:cancelled=True
    except Exception as error:errors.append(dict(file=None,detail=error_message(error),memory=memory_failure(error)))
    finally:
        finished.set()
        if processor:
            try:processor.close()
            except Exception as error:errors.append(dict(file=None,detail=error_message(error),memory=memory_failure(error)))
        events.put(('done',(completed,errors,cancelled,diagnosis)))


class BatchProcess:
    def __init__(self,**request):
        context=multiprocessing.get_context('spawn')
        self.events=context.Queue();self.event=context.Event()
        self.process=context.Process(target=run_batch,args=(request,self.event,self.events),name='Wigglinde processing')
        self.started=False

    def start(self):
        self.process.start();self.started=True

    def cancel(self):self.event.set()

    def messages(self):
        while True:
            try:message=self.events.get(timeout=.1)
            except queue.Empty:
                if self.process.is_alive():continue
                # The final flush may have happened just after the timed-out read.
                try:message=self.events.get(timeout=.2)
                except queue.Empty:raise RuntimeError('WORKER_EXIT: '+str(self.process.exitcode)) from None
            yield message
            if message[0]=='done':return

    def close(self):
        if self.started:self.process.join()
        self.process.close();self.events.close();self.events.join_thread()
