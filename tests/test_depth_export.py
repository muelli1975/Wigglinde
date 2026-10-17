from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
import numpy as np
from PIL import Image
from wigglinde.depth_export import save_depth_maps
from wigglinde.wiggle_export import ExportCancelled


class DepthExportTests(unittest.TestCase):
    def test_joint_scale_and_negative_disparity(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);work=root/'work';work.mkdir()
            left=np.array([[-40,-30],[-20,0]],np.float32)
            right=np.array([[-30,-20],[0,20]],np.float32)
            result=save_depth_maps(left,right,'Bild.jpg','Bild',root/'output',work,lambda:False)
            decoded=[]
            for path in result['files']:
                self.assertEqual(Path(path).parent,root/'output/depth_maps')
                self.assertTrue(Path(path).name.startswith('Bild_depth_2p_'))
                with Image.open(path) as image:
                    self.assertEqual(image.size,(2,2));values=np.asarray(image)
                    self.assertEqual(values.dtype,np.uint16);decoded.append(values)
            self.assertEqual(decoded[0][0,0],0);self.assertEqual(decoded[1][-1,-1],65535)
            self.assertEqual(decoded[0][0,1],decoded[1][0,0])
            metadata=json.loads(Path(result['metadata_file']).read_text())
            for original,values in zip((left,right),decoded):
                recovered=metadata['disparity_min']+values.astype(float)/65535*(metadata['disparity_max']-metadata['disparity_min'])
                self.assertLess(float(np.abs(original-recovered).max()),60/65535)
            self.assertFalse(metadata['metric_depth'])

    def test_constant_map_and_cancellation_preserve_existing_outputs(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);work=root/'work';work.mkdir();d=np.full((2,3),-5,np.float32)
            result=save_depth_maps(d,d,'Bild.jpg','Bild',root/'out',work,lambda:False)
            path=Path(result['files'][0]);before=path.read_bytes()
            with Image.open(path) as image:self.assertFalse(np.asarray(image).any())
            other=root/'other';other.mkdir()
            with self.assertRaises(ExportCancelled):save_depth_maps(d,d,'Bild.jpg','Bild',root/'out',other,lambda:True)
            self.assertEqual(path.read_bytes(),before)
