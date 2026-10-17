import json,tempfile,unittest
from pathlib import Path
import numpy as np
from wigglinde.blending_options import BlendingOptions
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene

class BlendingTests(unittest.TestCase):
    def test_config_reaches_native_adapter(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);exe=root/'renderer';exe.touch()
            rgb=np.zeros((8,16,3),np.uint8);depth=np.full((8,16),2,np.float32)
            for blend in [BlendingOptions(high_factor=8),BlendingOptions(method='Simple',simple_factor=2.5)]:
                renderer=RVSRenderer(exe,StereoScene(rgb,rgb,depth,depth),[.5],root/'work',blending=blend)
                config=json.loads((renderer.work/'config.json').read_text())
                for key,value in blend.rvs_config().items():self.assertEqual(config[key],value)
                self.assertEqual(config['Precision'],1);self.assertEqual(config['ColorSpace'],'RGB')
                self.assertNotIn('BlendingFactor' if blend.method=='Multispectral' else 'BlendingLowFreqFactor',config)

    def test_invalid_and_restored_settings(self):
        for value in [0,-1,float('nan'),float('inf'),1e40,1e-50,1e-39]:
            with self.subTest(value=value),self.assertRaises(ValueError):BlendingOptions(method='Simple',simple_factor=value).validate()
        saved=BlendingOptions(method='Simple',low_factor=2.,high_factor=8.,simple_factor=2.5)
        self.assertEqual(BlendingOptions.from_settings(saved.to_settings()),saved)
        self.assertEqual(BlendingOptions.from_settings({'method':'unknown','low_factor':'bad','high_factor':0}),BlendingOptions())
        self.assertEqual(BlendingOptions.from_settings(None),BlendingOptions())
        # Positive fractional and larger factors are allowed; no invented preset range.
        for value in [.125,1,2,4,5,8,20]:BlendingOptions(method='Simple',simple_factor=value).validate()
