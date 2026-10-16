from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import numpy as np
from PIL import Image,ImageCms
from wigglinde.processor import read_pair,collect_files
from wigglinde.export_options import WiggleOptions

class ConverterInputTests(unittest.TestCase):
    def test_explicit_size_full_half_swap_and_unchanged_source(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'sbs.png';a=np.zeros((40,120,3),np.uint8);a[:,:60,0]=255;a[:,60:,2]=255
            Image.fromarray(a).save(path);before=path.read_bytes()
            pair,original,size=read_pair(path,'Full-SBS',False,WiggleOptions())
            self.assertEqual(original,(60,40));self.assertEqual(size,(60,40));self.assertTrue((pair[0][:,:,0]==255).all())
            pair,original,size=read_pair(path,'Half-SBS',True,WiggleOptions())
            self.assertEqual(original,(120,40));self.assertEqual(size,(120,40));self.assertTrue((pair[0][:,:,2]==255).all());self.assertEqual(path.read_bytes(),before)

    def test_icc_profile_is_applied_before_stereo_split(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'icc.png';profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
            source=Image.new('RGB',(80,20),(12,80,210));source.save(path,icc_profile=profile)
            pair,_,_=read_pair(path,'Full-SBS',False,WiggleOptions())
            self.assertTrue(np.array_equal(pair[0],np.full((20,40,3),(12,80,210),np.uint8)))

    def test_folder_snapshot_excludes_output_temp_and_generated_png_sequences(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            for sub in ['Tag1','output','_temp','foto_Wiggle_30fps_1080h_PNG']:
                (root/sub).mkdir();(root/sub/'image.png').touch()
            files=collect_files(root,[root/'output'])
            self.assertEqual(files,[(root/'Tag1/image.png').resolve()])

    def test_high_bit_depth_is_not_silently_reduced(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'16bit.png';Image.fromarray(np.full((20,80),3000,np.uint16)).save(path)
            with self.assertRaises(ValueError):read_pair(path,'Full-SBS',False,WiggleOptions())
