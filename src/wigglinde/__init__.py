"""Portable Full-SBS to wiggle conversion."""

import os

# Must precede ONNX Runtime initialization, including its minimal startup event.
os.environ['ORT_DISABLE_TELEMETRY'] = '1'

__version__ = "1.2 Test 2"
SETTINGS_FILENAME = 'settings-test-1.2-defom.json'
