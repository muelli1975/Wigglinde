"""Read-only local memory counters; sampled peaks are not allocation guarantees."""
import ctypes as c
import os
from pathlib import Path
import sys
import threading
import uuid


class VideoMemory:
    """DXGI adapter 3: this process' local/nonlocal usage and current budget."""
    def __init__(self, device_id):
        self.adapter = c.c_void_p()
        factory = c.c_void_p(); adapter = c.c_void_p()
        def guid(value):return (c.c_ubyte * 16).from_buffer_copy(uuid.UUID(value).bytes_le)
        create = c.WinDLL('dxgi').CreateDXGIFactory1
        create.argtypes = [c.c_void_p, c.POINTER(c.c_void_p)]; create.restype = c.c_long
        try:
            if create(c.byref(guid('770aae78-f26f-4dba-a829-253c83d1b387')), c.byref(factory)) < 0:
                raise OSError('CreateDXGIFactory1 failed')
            if self.call(factory,12,c.c_long,c.c_uint,c.POINTER(c.c_void_p))(factory,device_id,c.byref(adapter)) < 0:
                raise OSError('DXGI adapter not found')
            result = self.call(adapter,0,c.c_long,c.c_void_p,c.POINTER(c.c_void_p))(
                adapter,c.byref(guid('645967a4-1392-4310-a798-8053ce3e93fd')),c.byref(self.adapter))
            if result < 0:raise OSError('IDXGIAdapter3 unavailable: '+hex(result & 0xffffffff))
        finally:
            if adapter.value:self.call(adapter,2,c.c_ulong)(adapter)
            if factory.value:self.call(factory,2,c.c_ulong)(factory)

    @staticmethod
    def call(obj,index,result,*types):
        table=c.cast(obj,c.POINTER(c.POINTER(c.c_void_p))).contents
        return c.WINFUNCTYPE(result,c.c_void_p,*types)(table[index])

    def snapshot(self):
        class INFO(c.Structure):
            _fields_=[(name,c.c_uint64) for name in ['Budget','CurrentUsage','AvailableForReservation','CurrentReservation']]
        result={}
        for group,name in [(0,'local'),(1,'nonlocal')]:
            info=INFO()
            status=self.call(self.adapter,14,c.c_long,c.c_uint,c.c_uint,c.POINTER(INFO))(self.adapter,0,group,c.byref(info))
            if status < 0:raise OSError('QueryVideoMemoryInfo failed: '+hex(status & 0xffffffff))
            result[f'gpu_process_{name}_usage_bytes']=info.CurrentUsage
            result[f'gpu_process_{name}_budget_bytes']=info.Budget
        return result

    def close(self):
        if self.adapter.value:self.call(self.adapter,2,c.c_ulong)(self.adapter);self.adapter=c.c_void_p()


def process_memory(pid=None):
    process_id=pid or os.getpid()
    if sys.platform=='darwin':
        import psutil
        return dict(rss_bytes=psutil.Process(process_id).memory_info().rss)
    if sys.platform=='win32':
        class COUNTERS(c.Structure):
            _fields_=[('cb',c.c_ulong),('PageFaultCount',c.c_ulong)]+[(name,c.c_size_t) for name in
                ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
                 'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
        kernel=c.WinDLL('kernel32',use_last_error=True);psapi=c.WinDLL('psapi',use_last_error=True)
        kernel.OpenProcess.argtypes=[c.c_ulong,c.c_int,c.c_ulong];kernel.OpenProcess.restype=c.c_void_p
        kernel.CloseHandle.argtypes=[c.c_void_p]
        psapi.GetProcessMemoryInfo.argtypes=[c.c_void_p,c.POINTER(COUNTERS),c.c_ulong]
        handle=kernel.OpenProcess(0x1010,False,process_id)
        if not handle:raise c.WinError(c.get_last_error())
        try:
            info=COUNTERS();info.cb=c.sizeof(info)
            if not psapi.GetProcessMemoryInfo(handle,c.byref(info),info.cb):raise c.WinError(c.get_last_error())
            return dict(rss_bytes=info.WorkingSetSize,private_commit_bytes=info.PrivateUsage)
        finally:kernel.CloseHandle(handle)
    if sys.platform.startswith('linux'):
        fields={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path(f'/proc/{pid or "self"}/status').read_text().splitlines() if ':' in line}
        return dict(rss_bytes=int(fields['VmRSS'].split()[0])*1024)
    return {}


def system_memory():
    if sys.platform=='darwin':
        import psutil
        info=psutil.virtual_memory()
        return dict(system_ram_total_bytes=info.total,system_ram_available_bytes=info.available)
    if sys.platform=='win32':
        class STATUS(c.Structure):
            _fields_=[('length',c.c_ulong),('load',c.c_ulong)]+[(name,c.c_uint64) for name in
                ['total_phys','avail_phys','total_pagefile','avail_pagefile','total_virtual','avail_virtual','avail_extended']]
        info=STATUS();info.length=c.sizeof(info)
        if not c.windll.kernel32.GlobalMemoryStatusEx(c.byref(info)):raise OSError('GlobalMemoryStatusEx failed')
        return dict(system_ram_total_bytes=info.total_phys,system_ram_available_bytes=info.avail_phys,
                    system_commit_limit_bytes=info.total_pagefile,system_commit_available_bytes=info.avail_pagefile)
    if sys.platform.startswith('linux'):
        values={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if len(line.split())==3}
        return dict(system_ram_total_bytes=values['MemTotal'],system_ram_available_bytes=values['MemAvailable'])
    return {}


class MemorySampler:
    def __init__(self,device_id=None,child=lambda:None,interval=.25):
        self.device_id=device_id;self.child=child;self.interval=interval
        self.stop_event=threading.Event();self.lock=threading.Lock();self.phase='starting';self.stages={};self.notes={};self.gpu=None

    def __enter__(self):
        if self.device_id is not None:
            try:
                if sys.platform!='win32':raise OSError('DXGI counters require Windows')
                self.gpu=VideoMemory(self.device_id);self.notes['gpu_counter']='DXGI process usage/budget, not total adapter utilization'
            except Exception as error:self.notes['gpu_counter_unavailable']=str(error)
        self.sample();self.thread=threading.Thread(target=self._poll,daemon=True);self.thread.start();return self

    def _poll(self):
        while not self.stop_event.wait(self.interval):self.sample()

    def sample(self,phase=None):
        with self.lock:
            if phase is not None:self.phase=phase
            values={}
            for key,reader in [('main',lambda:{'main_'+k:v for k,v in process_memory().items()}),('system',system_memory),
                               ('rvs',lambda:{'rvs_'+k:v for k,v in process_memory(self.child()).items()} if self.child() else {}),
                               ('gpu',lambda:self.gpu.snapshot() if self.gpu else {})]:
                try:values.update(reader())
                except Exception as error:self.notes[key+'_counter_unavailable']=str(error)
            item=self.stages.setdefault(self.phase,dict(samples=0,peak={},minimum={},last={}))
            item['samples']+=1;item['last']=values
            for key,value in values.items():
                item['peak'][key]=max(item['peak'].get(key,value),value)
                item['minimum'][key]=min(item['minimum'].get(key,value),value)

    def __exit__(self,*_):
        self.stop_event.set();self.thread.join();self.sample()
        if self.gpu:self.gpu.close()

    def report(self):return dict(sample_interval_seconds=self.interval,stages=self.stages,notes=self.notes)
