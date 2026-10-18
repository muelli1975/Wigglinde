"""Fixed LAS2-H model. No automatic model substitution."""
from pathlib import Path

MODELS=('LAS2-H',)
DEFAULT_MODEL='LAS2-H'

def model_path(app_dir,name,device_id=None,iterations=4):
    if iterations not in (4,8):raise ValueError('Iterationen: 4 oder 8 wählen. / Iterations: choose 4 or 8.')
    if name not in MODELS:raise ValueError('Unbekanntes Modell / unknown model: '+str(name))
    suffix='_dynamic.onnx' if device_id is None else '_mixed.onnx'
    return Path(app_dir)/'models/las2'/(name.replace('-','_')+('_iter8' if iterations==8 else '')+suffix)
