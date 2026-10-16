"""PyInstaller runtime hook: disable ORT telemetry before any application import."""
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
