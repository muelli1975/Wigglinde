from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import numpy as np
from PIL import Image,ImageCms
from wigglinde.processor import read_pair,collect_files
from wigglinde.export_options import WiggleOptions
from wigglinde.rvs import RVSRenderer
from wigglinde.stereo import StereoScene

class ConverterInputTests(unittest.TestCase):
    def test_full_sbs_proportions_fixed_order_and_unchanged_source(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'sbs.png';a=np.zeros((40,120,3),np.uint8);a[:,:60,0]=255;a[:,60:,2]=255
            Image.fromarray(a).save(path);before=path.read_bytes()
            pair,original,size=read_pair(path,WiggleOptions())
            self.assertEqual(original,(60,40));self.assertEqual(size,(60,40));self.assertTrue((pair[0][:,:,0]==255).all())
            self.assertTrue(np.array_equal(pair[1],a[:,60:]));self.assertEqual(path.read_bytes(),before)

    def test_icc_profile_is_applied_before_stereo_split(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'icc.png';profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
            source=Image.new('RGB',(80,20),(12,80,210));source.save(path,icc_profile=profile)
            pair,_,_=read_pair(path,WiggleOptions())
            self.assertTrue(np.array_equal(pair[0],np.full((20,40,3),(12,80,210),np.uint8)))

    def test_folder_input_ignores_all_subfolders_and_keeps_only_direct_images(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            for sub in ['Tag1','output','_temp','foto_Wiggle_30fps_1080h_PNG']:
                (root/sub).mkdir();(root/sub/'image.png').touch()
            (root/'direct.jpg').touch();(root/'notes.txt').touch()
            files=collect_files(root,[root/'output'])
            self.assertEqual(files,[(root/'direct.jpg').resolve()])

    def test_high_bit_depth_is_not_silently_reduced(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'16bit.png';Image.fromarray(np.full((20,80),3000,np.uint16)).save(path)
            with self.assertRaises(ValueError):read_pair(path,WiggleOptions())

    def test_rvs_json_contains_utf8_paths_without_unsupported_escapes(self):
        import json
        with TemporaryDirectory() as folder:
            root=Path(folder)/'Größe';root.mkdir();exe=root/'renderer.exe';exe.touch()
            rgb=np.zeros((4,8,3),np.uint8);d=np.ones((4,8),np.float32)
            renderer=RVSRenderer(exe,StereoScene(rgb,rgb,d,d),[.5],root/'Arbeit')
            raw=(renderer.work/'config.json').read_text(encoding='utf-8')
            self.assertNotIn('\\',raw)
            config=json.loads(raw);self.assertIn('Größe',config['InputCameraParameterFile'])
            self.assertEqual(config['Precision'],1)
            self.assertEqual(config['BlendingMethod'],'Simple')
            self.assertEqual(config['BlendingFactor'],5.)
            self.assertNotIn('BlendingLowFreqFactor',config)
            self.assertNotIn('BlendingHighFreqFactor',config)

    def test_rvs_input_uses_encoded_rgb_without_gamma_linearization(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);exe=root/'renderer';exe.touch()
            rgb=np.full((4,8,3),128,np.uint8);d=np.ones((4,8),np.float32)
            renderer=RVSRenderer(exe,StereoScene(rgb,rgb,d,d),[.5],root/'work')
            stored=np.fromfile(renderer.work/'color0.rgb',dtype=np.float32)
            self.assertTrue(np.allclose(stored,128/255))

    def test_opengl_uses_one_context_and_keeps_geometry(self):
        import json
        with TemporaryDirectory() as folder:
            root=Path(folder);exe=root/'renderer';exe.touch()
            rgb=np.full((4,8,3),128,np.uint8);d=np.full((4,8),-3,np.float32)
            scene=StereoScene(rgb,rgb,d,d)
            cpu=RVSRenderer(exe,scene,[0,.5,1],root/'cpu')
            gl=RVSRenderer(exe,scene,[0,.5,1],root/'gl',backend='opengl')
            self.assertEqual(gl.schedule['workers'],1)
            self.assertEqual(cpu.bias,gl.bias)
            self.assertEqual((cpu.work/'color0.rgb').read_bytes(),(gl.work/'color0.rgb').read_bytes())
            self.assertEqual((cpu.work/'depth0.z').read_bytes(),(gl.work/'depth0.z').read_bytes())
            self.assertEqual(json.loads((cpu.work/'cameras.json').read_text()),json.loads((gl.work/'cameras.json').read_text()))
