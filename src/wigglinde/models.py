"""The explicit application model choices. No automatic model substitution."""
from pathlib import Path

MODELS=('LAS2-M','LAS2-L','LAS2-H')
DEFAULT_MODEL='LAS2-L'

def model_path(app_dir,name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return Path(app_dir)/'models/las2'/(name.replace('-','_')+'_dynamic.onnx')
