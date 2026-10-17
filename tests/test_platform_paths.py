from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from wigglinde.app import app_directory


class PlatformPathsTests(unittest.TestCase):
    def test_mac_bundle_keeps_portable_data_outside_signed_bundle(self):
        with patch.object(sys, 'platform', 'darwin'), patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'executable', '/tmp/Wigglinde/Wigglinde.app/Contents/MacOS/Wigglinde'):
            self.assertEqual(app_directory(), Path('/tmp/Wigglinde').resolve())

    def test_linux_directory_package_uses_executable_folder(self):
        with patch.object(sys, 'platform', 'linux'), patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'executable', '/tmp/Wigglinde/Wigglinde'):
            self.assertEqual(app_directory(), Path('/tmp/Wigglinde').resolve())
