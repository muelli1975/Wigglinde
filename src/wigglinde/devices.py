"""Enumerate Windows graphics adapters without loading a model or testing a frame."""
import sys

def graphics_adapters():
    if sys.platform != 'win32':return []
    import ctypes as c
    from ctypes import wintypes as w
    class GUID(c.Structure):
        _fields_=[('a',w.DWORD),('b',w.WORD),('c',w.WORD),('d',c.c_ubyte*8)]
    class DESC(c.Structure):
        _fields_=[('name',w.WCHAR*128),('vendor',w.UINT),('device',w.UINT),('subsystem',w.UINT),('revision',w.UINT),('vram',c.c_size_t),('system',c.c_size_t),('shared',c.c_size_t),('luid',c.c_int64),('flags',w.UINT)]
    def call(obj,index,result,*types):
        table=c.cast(obj,c.POINTER(c.POINTER(c.c_void_p))).contents
        return c.WINFUNCTYPE(result,c.c_void_p,*types)(table[index])
    factory=c.c_void_p();adapters=[]
    # IDXGIFactory1, for EnumAdapters1 in the same DXGI order DirectML uses.
    iid=GUID(0x770aae78,0xf26f,0x4dba,(c.c_ubyte*8)(0xa8,0x29,0x25,0x3c,0x83,0xd1,0xb3,0x87))
    try:
        create=c.WinDLL('dxgi').CreateDXGIFactory1
        create.argtypes=[c.POINTER(GUID),c.POINTER(c.c_void_p)];create.restype=c.c_long
        if create(c.byref(iid),c.byref(factory))<0:return []
        index=0
        while True:
            adapter=c.c_void_p()
            if call(factory,12,c.c_long,w.UINT,c.POINTER(c.c_void_p))(factory,index,c.byref(adapter))<0:break
            try:
                desc=DESC()
                if call(adapter,10,c.c_long,c.POINTER(DESC))(adapter,c.byref(desc))>=0 and not desc.flags&2:
                    adapters.append((index,desc.name))
            finally:call(adapter,2,w.ULONG)(adapter)
            index+=1
    except OSError:return []
    finally:
        if factory.value:call(factory,2,w.ULONG)(factory)
    return adapters
