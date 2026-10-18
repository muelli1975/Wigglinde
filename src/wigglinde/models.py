"""Explicit local LAS2 model selection. No automatic model substitution."""
from pathlib import Path

MODELS=('LAS2-S','LAS2-M','LAS2-L','LAS2-H')
DEFAULT_MODEL='LAS2-H'

def model_iterations(name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return 4 if name=='LAS2-H' else None

def model_precision(name,device_id=None):
    model_iterations(name)
    return 'mixed_float16_float32' if device_id is not None else 'float32'

def model_path(app_dir,name,device_id=None):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    suffix='_mixed.onnx' if model_precision(name,device_id)=='mixed_float16_float32' else '_dynamic.onnx'
    return Path(app_dir)/'models/las2'/(name.replace('-','_')+suffix)
