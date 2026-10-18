"""Explicit local stereo models. No automatic substitution or download."""
from pathlib import Path

IGEV_MODEL='IGEV++ Middlebury'
LAS2_MODELS=('LAS2-S','LAS2-M','LAS2-L','LAS2-H')
MODELS=LAS2_MODELS+(IGEV_MODEL,)
DEFAULT_MODEL='LAS2-H'

def model_family(name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return 'igev' if name==IGEV_MODEL else 'las2'

def model_iterations(name):
    family=model_family(name)
    return 16 if family=='igev' else 4 if name=='LAS2-H' else None

def model_precision(name,device_id=None):
    model_family(name)
    return 'mixed_float16_float32' if device_id is not None else 'float32'

def model_path(app_dir,name,device_id=None):
    family=model_family(name)
    suffix='_mixed.onnx' if device_id is not None else '_dynamic.onnx'
    stem='IGEV_Middlebury' if family=='igev' else name.replace('-','_')
    return Path(app_dir)/'models'/family/(stem+suffix)
