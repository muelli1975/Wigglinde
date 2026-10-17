"""Fixed LAS2-H model. No automatic model substitution."""
from pathlib import Path

MODELS=('LAS2-H',)
DEFAULT_MODEL='LAS2-H'

def model_path(app_dir,name):
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    return Path(app_dir)/'models/las2'/(name.replace('-','_')+'_dynamic.onnx')
