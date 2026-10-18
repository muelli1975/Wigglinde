"""Local 16-iteration IGEV++ Middlebury ONNX; no torch/timm at runtime.

RGB values stay 0..255 here: the exported model includes its own -1..1
normalization. Padding and temporary matching offset exactly match the shared
stereo interface; the source geometry is restored after inference.
"""
from .onnx_stereo import OnnxStereo

class IGEVMiddlebury(OnnxStereo):
    family='igev'
