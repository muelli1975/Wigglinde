"""Bound view concurrency by CPU capacity and available memory, never image quality."""
import math
import os
from pathlib import Path
from .memory import system_memory

GIB=1024**3

def cpu_capacity():
    count=getattr(os,'process_cpu_count',os.cpu_count)() or 1
    if hasattr(os,'sched_getaffinity'):
        count=min(count,len(os.sched_getaffinity(0)))
    try:
        quota,period=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota!='max':count=min(count,max(1,math.floor(int(quota)/int(period))))
    except (OSError,ValueError):pass
    return max(1,count)

def available_memory():
    try:values=system_memory()
    except OSError:values={}
    total=values.get('system_ram_total_bytes',0)
    limits=[values[k] for k in ('system_ram_available_bytes','system_commit_available_bytes') if k in values]
    try:
        limit=Path('/sys/fs/cgroup/memory.max').read_text().strip()
        if limit!='max':
            cap=int(limit);used=int(Path('/sys/fs/cgroup/memory.current').read_text())
            total=min(total or cap,cap);limits.append(max(0,cap-used))
    except (OSError,ValueError):pass
    return total,min(limits) if limits else None

def plan_views(width,height,count,cpus,total_memory,available):
    # Precision 1 has one quarter of Precision 2's working pixels. Scale the
    # existing per-pixel allowance accordingly, retaining fixed allocator/queue
    # overhead and the separate system reserve. Three 1620x1080 photo runs at P1
    # used 0.83-0.85 GiB native RSS with 3 workers; this budgets 1.44 GiB for them.
    # An estimate, not an allocation guarantee; keep one view possible as before.
    per_view=width*height*256+64*1024**2
    reserve=max(GIB,total_memory//10)
    budget=max(0,available-reserve) if available is not None else 0
    memory_workers=max(1,budget//per_view) if available is not None else 1
    workers=max(1,min(max(1,cpus),max(1,count),memory_workers))
    return dict(workers=workers,threads_per_view=max(1,cpus//workers),cpu_capacity=cpus,
                estimated_bytes_per_view=per_view,memory_available_bytes=available,
                memory_reserve_bytes=reserve,memory_budget_bytes=budget,
                policy='precision1_memory_bounded_v1')

def render_plan(width,height,count):
    total,available=available_memory()
    return plan_views(width,height,count,cpu_capacity(),total,available)
