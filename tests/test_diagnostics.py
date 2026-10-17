from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import base64,json,unittest
import numpy as np
from PIL import Image
from wigglinde.diagnostics import LocalLogs,exception_details,error_message,memory_failure
from wigglinde.export_options import WiggleOptions
from wigglinde.memory import process_memory,system_memory
from wigglinde.models import DEFAULT_MODEL
from wigglinde.processor import Processor
from wigglinde.wiggle_export import ExportCancelled


class FakeModel:
    model_name=DEFAULT_MODEL
    session=type('Session',(),{'get_providers':lambda _:['CPUExecutionProvider']})()
    failure=None
    def predict_pair(self,left,right,offset,cancel,progress,stage):
        self.inputs=(left.copy(),right.copy(),offset)
        with stage('depth_left'):
            if self.failure:raise self.failure
        with stage('depth_right'):pass
        return np.ones(left.shape[:2],np.float32),np.ones(right.shape[:2],np.float32)


class DiagnosticsTests(unittest.TestCase):
    def test_runtime_error_bytes_survive_utf8_failure(self):
        raw='DirectML: Für diesen Vorgang ist nicht genügend Speicher verfügbar. 0x8007000E'.encode('cp1252')
        error=UnicodeDecodeError('utf-8',raw,13,14,'invalid start byte')
        item=exception_details(error)[0]
        self.assertEqual(base64.b64decode(item['bytes_base64']),raw)
        self.assertIn('Für diesen Vorgang',error_message(error))
        self.assertTrue(memory_failure(error))
        self.assertFalse(memory_failure(RuntimeError('GPU device removed')))

    def test_logs_rotate_and_preserve_other_files(self):
        with TemporaryDirectory() as folder:
            logs=LocalLogs(folder,max_bytes=500,backups=3)
            foreign=logs.folder/'keep.txt';foreign.write_text('keep')
            for i in range(40):logs.write('events',dict(index=i,message='Größe '+str(i)*40))
            logs.close()
            paths=list(logs.folder.glob('wigglinde.jsonl*'))
            self.assertEqual(len(paths),4)
            self.assertEqual(foreign.read_text(),'keep')
            for path in paths:
                for line in path.read_text(encoding='utf-8').splitlines():json.loads(line)
            self.assertEqual(json.loads((logs.folder/'wigglinde.jsonl').read_text().splitlines()[-1])['index'],39)

    def source(self,folder):
        path=Path(folder)/'Bild_Größe.png'
        pixels=np.arange(32*128*3,dtype=np.uint8).reshape(32,128,3)
        Image.fromarray(pixels).save(path);return path,pixels

    def test_depth_diagnostic_uses_full_sbs_and_never_starts_renderer(self):
        with TemporaryDirectory() as folder:
            path,pixels=self.source(folder);before=path.read_bytes()
            processor=Processor(folder);processor.model=FakeModel()
            try:
                with patch('wigglinde.processor.RVSRenderer',side_effect=AssertionError('Renderer must not start')):
                    report=processor.diagnose(path,WiggleOptions(video_height=2160))
                self.assertEqual(report['mode'],'depth_only');self.assertEqual(report['status'],'passed')
                self.assertEqual(report['processing_size'],(64,32));self.assertEqual(report['precision'],'float32')
                self.assertTrue(np.array_equal(processor.model.inputs[0],pixels[:,:64]))
                self.assertEqual(path.read_bytes(),before);self.assertNotIn('output',report)
                self.assertFalse((Path(folder)/'_temp').exists())
                self.assertIn('depth_left',report['stage_seconds']);self.assertIn('depth_right',report['stage_seconds'])
            finally:processor.close()

    def test_failed_inference_records_stage_context_and_original_message(self):
        with TemporaryDirectory() as folder:
            path,_=self.source(folder);processor=Processor(folder);processor.model=FakeModel()
            raw='Für diese Berechnung fehlt Speicher: 0x8007000E'.encode('cp1252')
            processor.model.failure=UnicodeDecodeError('utf-8',raw,1,2,'invalid start byte')
            try:
                with self.assertRaises(UnicodeDecodeError):processor.diagnose(path,WiggleOptions())
                report=json.loads((Path(folder)/'logs/latest_run.json').read_text(encoding='utf-8'))
                self.assertEqual(report['failed_stage'],'depth_left');self.assertEqual(report['status'],'failed')
                self.assertEqual(report['source'],str(path.resolve()));self.assertEqual(report['processing_size'],[64,32])
                self.assertEqual(base64.b64decode(report['exceptions'][0]['bytes_base64']),raw)
                self.assertEqual(report['model'],'LAS2-H')
                self.assertTrue((Path(folder)/'logs/errors.log').stat().st_size>0)
            finally:processor.close()

    def test_cancelled_diagnostic_is_recorded_without_error_report(self):
        with TemporaryDirectory() as folder:
            path,_=self.source(folder);processor=Processor(folder);processor.model=FakeModel();processor.model.failure=ExportCancelled()
            try:
                with self.assertRaises(ExportCancelled):processor.diagnose(path,WiggleOptions())
                self.assertEqual(processor.last_diagnostics['status'],'cancelled')
                self.assertEqual((Path(folder)/'logs/errors.log').stat().st_size,0)
            finally:processor.close()

    def test_native_memory_counters_are_plausible(self):
        process=process_memory();system=system_memory()
        self.assertGreater(process['rss_bytes'],0)
        self.assertGreater(system['system_ram_total_bytes'],0)
        self.assertLessEqual(system['system_ram_available_bytes'],system['system_ram_total_bytes'])
