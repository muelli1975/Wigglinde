"""Offline DEFOM ONNX inference in a cancellable, isolated native worker."""

import multiprocessing
from pathlib import Path
import threading
import traceback

from .diagnostics import error_message, exception_details
from .memory import MemorySampler
from .onnx_stereo import OnnxStereo
from .resources import cpu_capacity
from .wiggle_export import ExportCancelled, check_cancelled


class _Runtime(OnnxStereo):
    family = 'defom'


def _worker(connection, path, threads, device_id):
    try:
        with MemorySampler(device_id) as memory:
            memory.sample('model_load')
            model = _Runtime(path, threads=threads or cpu_capacity(), device_id=device_id)
            connection.send(('ready', dict(model_name=model.model_name, precision=model.precision,
                providers=model.session.get_providers(), memory=memory.report())))
            while True:
                request = connection.recv()
                if request[0] == 'close':
                    break
                if request[0] != 'predict':
                    raise ValueError('Unknown stereo worker request')
                memory.sample('inference')
                left, right, offset = request[1]
                result = model.predict(left, right, offset, lambda: False)
                memory.sample()
                connection.send(('result', (result, memory.report())))
    except (EOFError, BrokenPipeError):
        pass
    except Exception as error:
        try:
            connection.send(('error', dict(message=error_message(error), details=exception_details(error),
                                          traceback=traceback.format_exc())))
        except (EOFError, BrokenPipeError, OSError):
            pass
    finally:
        connection.close()


class _SessionInfo:
    def __init__(self, providers):
        self.providers = tuple(providers)

    def get_providers(self):
        return list(self.providers)


class WorkerError(RuntimeError):
    def __init__(self, payload):
        super().__init__(payload['message'])
        self.remote_details = payload['details']
        self.remote_traceback = payload['traceback']


class DEFOMStereo(OnnxStereo):
    """Retain the shared transport math and reuse one worker per batch."""

    family = 'defom'

    def __init__(self, model_path, threads=None, device_id=None, cancel=lambda: False):
        self._cancelled = threading.Event()
        self._closed = False
        self.device_id = device_id
        context = multiprocessing.get_context('spawn')
        self.connection, child = context.Pipe()
        self.process = context.Process(target=_worker, args=(child, str(Path(model_path).resolve()), threads, device_id), daemon=True)
        try:
            check_cancelled(cancel)
            self.process.start()
            child.close()
            kind, details = self._receive(cancel)
            if kind != 'ready':
                raise RuntimeError('Invalid stereo worker startup')
            self.model_name, self.precision = details['model_name'], details['precision']
            self.session = _SessionInfo(details['providers'])
            self.worker_lifetime_memory = details['memory']
        except BaseException:
            child.close()
            self.close()
            raise

    def _receive(self, cancel):
        while True:
            if self._cancelled.is_set() or cancel():
                self.close()
                raise ExportCancelled()
            try:
                if self.connection.poll(.05):
                    result = self.connection.recv()
                    if result[0] == 'error':
                        self.close()
                        raise WorkerError(result[1])
                    return result
                if not self.process.is_alive():
                    self.process.join()
                    code = self.process.exitcode
                    self.close()
                    raise RuntimeError(f'DEFOM-Prozess beendet / DEFOM worker stopped (exit {code}, 0x{code & 0xffffffff:08X}).')
            except (EOFError, BrokenPipeError, OSError) as error:
                self.process.join(timeout=.1)
                code = self.process.exitcode
                self.close()
                raise RuntimeError(f'DEFOM-Prozess beendet / DEFOM worker stopped (exit {code}).') from error

    def predict(self, left, right, offset, cancel):
        check_cancelled(cancel)
        if self._closed:
            raise RuntimeError('DEFOM-Prozess nicht verfügbar / DEFOM worker is unavailable.')
        try:
            self.connection.send(('predict', (left, right, offset)))
            kind, result = self._receive(cancel)
        except (EOFError, BrokenPipeError, OSError) as error:
            self.close()
            raise RuntimeError('DEFOM-Prozess beendet / DEFOM worker stopped.') from error
        if kind != 'result':
            self.close()
            raise RuntimeError('Invalid stereo worker response')
        disparity, self.worker_lifetime_memory = result
        return disparity

    def cancel(self):
        self._cancelled.set()

    def close(self):
        if self._closed:
            return
        self._closed = True
        # Never block the UI's Cancel callback; this runs in its job thread.
        if self.process.pid is not None:
            if self.process.is_alive():
                self.process.terminate()
            self.process.join(timeout=2)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=2)
        self.connection.close()
