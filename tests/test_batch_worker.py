from pathlib import Path
import queue,threading,unittest
from wigglinde.batch_worker import run_batch
from wigglinde.export_options import WiggleOptions
from wigglinde.wiggle_export import ExportCancelled


class BatchWorkerTests(unittest.TestCase):
    def request(self,**changes):
        request=dict(app_dir=Path('/app'),files=[Path('/input/Größe.png'),Path('/input/Bild2.png')],root=Path('/input'),
            standard=True,own=Path('/own'),options=WiggleOptions(),device_id=2,device_name='GPU 2: chosen',
            depth_only=False,model_name='IGEV++ Middlebury',render_backend='vulkan')
        request.update(changes);return request

    def drain(self,events):
        messages=[]
        while not events.empty():messages.append(events.get_nowait())
        return messages

    def test_batch_reuses_processor_and_preserves_explicit_choices_and_paths(self):
        instances=[];calls=[]
        class FakeProcessor:
            def __init__(self,*args,**kwargs):instances.append((self,args,kwargs));self.closed=False
            def convert(self,path,base,options,progress):calls.append((self,path,base,options));progress('test',.5)
            def close(self):self.closed=True
        events=queue.Queue();request=self.request()
        run_batch(request,threading.Event(),events,FakeProcessor)
        self.assertEqual(len(instances),1)
        self.assertTrue(instances[0][0].closed)
        self.assertEqual(instances[0][2],dict(device_id=2,device_name='GPU 2: chosen',model_name='IGEV++ Middlebury',render_backend='vulkan'))
        self.assertTrue(all(call[0] is instances[0][0] and call[2]==Path('/input/output') and call[3] is request['options'] for call in calls))
        messages=self.drain(events)
        self.assertEqual([m[1][1] for m in messages if m[0]=='progress'],[.25,.75])
        self.assertEqual(messages[-1],('done',(2,[],False,None)))

    def test_cancel_reaches_active_processor_and_closes_without_second_file(self):
        entered=threading.Event();interrupted=threading.Event();closed=threading.Event()
        class FakeProcessor:
            def __init__(self,*args,**kwargs):pass
            def convert(self,*args,**kwargs):
                entered.set()
                if not interrupted.wait(2):raise RuntimeError('cancel did not reach the active inference')
                raise ExportCancelled()
            def cancel(self):interrupted.set()
            def close(self):closed.set()
        cancel=threading.Event();events=queue.Queue()
        worker=threading.Thread(target=run_batch,args=(self.request(),cancel,events,FakeProcessor))
        worker.start();self.assertTrue(entered.wait(2));cancel.set();worker.join(3)
        self.assertFalse(worker.is_alive());self.assertTrue(closed.is_set())
        messages=self.drain(events)
        self.assertEqual(sum(m[0]=='file' for m in messages),1)
        self.assertEqual(messages[-1],('done',(0,[],True,None)))

    def test_gpu_initialization_failure_stops_batch_without_fallback(self):
        calls=[]
        class FakeProcessor:
            def __init__(self,*args,**kwargs):pass
            def convert(self,path,*args,**kwargs):calls.append(path);raise RuntimeError('GPU_INIT: chosen GPU failed')
            def close(self):pass
        events=queue.Queue();run_batch(self.request(),threading.Event(),events,FakeProcessor)
        self.assertEqual(len(calls),1)
        result=self.drain(events)[-1][1]
        self.assertEqual(result[:1],(0,));self.assertFalse(result[2])
        self.assertEqual(result[1],[dict(file='Größe.png',detail='GPU_INIT: chosen GPU failed',memory=False)])

    def test_depth_diagnosis_and_memory_errors_retain_their_meaning(self):
        class FakeProcessor:
            def __init__(self,*args,**kwargs):pass
            def diagnose(self,path,*args,**kwargs):
                if path.name=='Größe.png':raise MemoryError('not enough memory')
                return dict(status='passed',model='IGEV++ Middlebury')
            def close(self):pass
        events=queue.Queue();run_batch(self.request(depth_only=True),threading.Event(),events,FakeProcessor)
        completed,errors,cancelled,diagnosis=self.drain(events)[-1][1]
        self.assertEqual(completed,1);self.assertTrue(errors[0]['memory']);self.assertFalse(cancelled)
        self.assertEqual(diagnosis,dict(status='passed',model='IGEV++ Middlebury'))
