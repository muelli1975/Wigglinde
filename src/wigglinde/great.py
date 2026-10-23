"""Official classical GREAT-IGEV Middlebury, 32 fixed iterations, local ONNX."""
from .onnx_stereo import OnnxStereo


class GREATMiddlebury(OnnxStereo):
    family = 'great'
