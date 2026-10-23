"""Explicit local stereo models. No automatic substitution or download."""
from pathlib import Path

IGEV_MODEL='IGEV++ Middlebury'
DEFOM_SMALL='DEFOM-S/RVC'
DEFOM_LARGE='DEFOM-L (CC-BY-NC-4.0)'
LAS2_MODELS=('LAS2-H',)
MODELS=LAS2_MODELS+(IGEV_MODEL,DEFOM_SMALL,DEFOM_LARGE)
DEFAULT_MODEL='LAS2-H'

def model_family(name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return 'igev' if name==IGEV_MODEL else 'defom' if name in (DEFOM_SMALL,DEFOM_LARGE) else 'las2'

def model_iterations(name):
    family=model_family(name)
    return 32 if family=='defom' else 16 if family=='igev' else 4 if name=='LAS2-H' else None

def model_precision(name,device_id=None):
    model_family(name)
    return 'mixed_float16_float32' if device_id is not None else 'float32'

def model_path(app_dir,name,device_id=None):
    family=model_family(name)
    suffix='_mixed.onnx' if device_id is not None else '_dynamic.onnx'
    stem='DEFOM_S' if name==DEFOM_SMALL else 'DEFOM_L' if name==DEFOM_LARGE else 'IGEV_Middlebury' if family=='igev' else name.replace('-','_')
    return Path(app_dir)/'models'/family/(stem+suffix)

def model_suffix(name):
    model_family(name)
    return 'defom-s-rvc' if name==DEFOM_SMALL else 'defom-l-middlebury' if name==DEFOM_LARGE else 'igev-middlebury' if name==IGEV_MODEL else 'las2-h'
