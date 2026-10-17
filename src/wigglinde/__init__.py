"""Wigglinde's development prototype; no release-quality claim."""

import os

# Must precede ONNX Runtime initialization, including its minimal startup event.
os.environ['ORT_DISABLE_TELEMETRY'] = '1'

__version__ = "0.1-test5"
