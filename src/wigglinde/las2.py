"""LAS2 adapter; preserves the shared RGB/padding/cancellation implementation."""
from .onnx_stereo import OnnxStereo

class LiteAnyStereo(OnnxStereo):
    family='las2'
