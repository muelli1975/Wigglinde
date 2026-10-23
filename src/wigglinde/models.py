"""Explicit local stereo models. No automatic substitution or download."""
from pathlib import Path

IGEV_MODEL='IGEV++ Middlebury'
GREAT_MODEL='GREAT-IGEV Middlebury'
LAS2_MODELS=('LAS2-H',)
MODELS=LAS2_MODELS+(IGEV_MODEL,GREAT_MODEL)
DEFAULT_MODEL='LAS2-H'

def model_family(name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return 'igev' if name==IGEV_MODEL else 'great' if name==GREAT_MODEL else 'las2'

def model_iterations(name):
    family=model_family(name)
    return {'las2':4,'igev':16,'great':32}[family]

def model_precision(name,device_id=None):
    model_family(name)
    return 'mixed_float16_float32' if device_id is not None else 'float32'

def model_path(app_dir,name,device_id=None):
    family=model_family(name)
    suffix='_mixed.onnx' if device_id is not None else '_dynamic.onnx'
    stem='IGEV_Middlebury' if family=='igev' else 'GREAT_IGEV_Middlebury' if family=='great' else name.replace('-','_')
    return Path(app_dir)/'models'/family/(stem+suffix)

def model_suffix(name):
    model_family(name)
    return 'igev-middlebury' if name==IGEV_MODEL else 'great-igev-middlebury' if name==GREAT_MODEL else 'las2-h'

def estimator_class(name):
    from .las2 import LiteAnyStereo
    from .igev import IGEVMiddlebury
    from .great import GREATMiddlebury
    return {'las2':LiteAnyStereo,'igev':IGEVMiddlebury,'great':GREATMiddlebury}[model_family(name)]
