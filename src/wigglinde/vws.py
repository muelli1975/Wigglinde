"""Unchanged TMIV/VWS CPU: native 10-bit geometry and YUV420 transport."""
from pathlib import Path
from contextlib import ExitStack
import json
import subprocess
import time

import numpy as np

from .wiggle_export import check_cancelled
from .resources import vws_render_plan


# MPEG TMIV best-reference VWS parameters at the pinned revision. No tuning.
VWS_PARAMETERS = dict(angularScaling=1.5, blendingFactor=.03,
                      edgeBlurringBlockSize=5, edgeBlurringDepthThreshold=.04,
                      filterReprojectedPrunedDepthMaps=dict(dilateCount=5, erodeCount=5),
                      filteringPass=1, minimalWeight=2.5, overloadFactor=2., stretchFactor=100.)


def rgb_to_yuv420(rgb):
    values = rgb.astype(np.float32) / 255
    red, green, blue = np.moveaxis(values, -1, 0)
    y = .2126 * red + .7152 * green + .0722 * blue
    u = (blue - y) / 1.8556 + .5
    v = (red - y) / 1.5748 + .5
    planes = np.rint(np.clip(np.stack((y, u, v)), 0, 1) * 1023).astype(np.uint32)
    height, width = y.shape
    chroma = (planes[1:].reshape(2, height // 2, 2, width // 2, 2).sum(axis=(2, 4)) + 2) // 4
    return np.concatenate((planes[0].ravel(), chroma[0].ravel(), chroma[1].ravel())).astype('<u2')


def yuv420_to_rgb(data, height, width):
    values = np.frombuffer(data, dtype='<u2').astype(np.float32) / 1023
    pixels = height * width
    y = values[:pixels].reshape(height, width)
    u = values[pixels:pixels + pixels // 4].reshape(height // 2, width // 2).repeat(2, 0).repeat(2, 1)
    v = values[pixels + pixels // 4:].reshape(height // 2, width // 2).repeat(2, 0).repeat(2, 1)
    u = u - .5
    v = v - .5
    red = y + 1.5748 * v
    blue = y + 1.8556 * u
    green = (y - .2126 * red - .0722 * blue) / .7152
    return np.rint(np.clip(np.stack((red, green, blue), axis=-1), 0, 1) * 255).astype(np.uint8)


class VWSRenderer:
    def __init__(self, executable, scene, positions, work, matching_offset=64, *, worker_count=None):
        self.executable = Path(executable)
        self.scene, self.positions, self.work = scene, positions, Path(work).resolve()
        self.process, self.metrics, self.processes = None, {}, []
        if not self.executable.is_file():
            raise FileNotFoundError('Der VWS-Renderer fehlt / The VWS renderer is missing: ' + str(self.executable))
        self.work.mkdir(parents=True, exist_ok=True)
        height, width = scene.left.shape[:2]
        padded_height, padded_width = height + height % 2, width + width % 2
        self.storage_size = (padded_width, padded_height)
        self.schedule = vws_render_plan(padded_width, padded_height, len(positions))
        if worker_count is not None:
            if worker_count < 1:raise ValueError('Worker count must be positive.')
            self.schedule['workers'] = min(worker_count, len(positions))
            self.schedule['threads_per_view'] = max(1, self.schedule['cpu_capacity'] // self.schedule['workers'])
        self.bias = max(float(matching_offset),
                        1 - float(min(scene.left_disparity.min(), scene.right_disparity.min())))
        maps = (scene.left_disparity, scene.right_disparity)
        minimum = float(min(d.min() for d in maps)) + self.bias
        maximum = float(max(d.max() for d in maps)) + self.bias
        # Shared affine inverse-depth encoding. Never normalize each eye separately.
        low, high = minimum / width, maximum / width
        if high - low < 1e-6:
            high = low + 1e-6
        self.inverse_depth_range = [low, high]
        self.max_disparity_quantization_px = (high - low) * width / 2 * (1 / 65535 + 1 / 1023)
        for index, (rgb, disparity) in enumerate(zip((scene.left, scene.right), maps)):
            rgb = np.pad(rgb, ((0, height % 2), (0, width % 2), (0, 0)), mode='edge')
            disparity = np.pad(disparity, ((0, height % 2), (0, width % 2)), mode='edge')
            rgb_to_yuv420(rgb).tofile(self.work / f'input{index}.yuv')
            encoded = ((disparity.astype(np.float64) + self.bias) / width - low) / (high - low)
            depth = np.rint(np.clip(encoded, 0, 1) * 65535).astype('<u2')
            # The official loader reads YUV420 geometry and uses its luma plane.
            neutral = np.full((2, padded_height // 2, padded_width // 2), 32768, dtype='<u2')
            np.concatenate((depth.ravel(), neutral.ravel())).tofile(self.work / f'depth{index}.yuv')

        def camera(name, position):
            return dict(Name=name, Position=[0, -float(position), 0], Rotation=[0, 0, 0],
                        Depthmap=1, Background=0, Depth_range=[1 / high, 1 / low],
                        Resolution=[padded_width, padded_height], Projection='Perspective', Focal=[width, width],
                        Principle_point=[width / 2 + self.bias * float(position), height / 2],
                        BitDepthColor=10, BitDepthDepth=16, ColorSpace='YUV420',
                        DepthColorSpace='YUV420', HasInvalidDepth=False)

        cameras = [camera('input0', 0), camera('input1', 1)]
        cameras += [camera(f'view{i}', position) for i, position in enumerate(positions)]
        sequence = dict(Version='4.0', BoundingBox_center=[0, -.5, 1], Content_name='Wigglinde',
                        Fps=1, Frames_number=1, cameras=cameras,
                        sourceCameraNames=['input0', 'input1'], sourceCameraIds=[0, 1],
                        lengthsInMeters=True)
        (self.work / 'cameras.json').write_text(json.dumps(sequence), encoding='utf-8')
        config = dict(CullerMethod='NoCuller', NoCuller={}, RendererMethod='Renderer',
                      DepthQualityAssessorMethod='DepthQualityAssessor',
                      DepthQualityAssessor=dict(blendingFactor=.03, maxOutlierRatio=.001),
                      Renderer=dict(InpainterMethod='Inpainter', Inpainter={},
                                    SynthesizerMethod='ViewWeightingSynthesizer',
                                    ViewWeightingSynthesizer=VWS_PARAMETERS,
                                    ViewingSpaceControllerMethod='ViewingSpaceController',
                                    ViewingSpaceController={}),
                      configDirectory='.', inputDirectory='.',
                      outputDirectory='.', inputTexturePathFmt='{3}.yuv',
                      inputGeometryPathFmt='depth{3}.yuv', inputSequenceConfigPathFmt='cameras.json',
                      inputViewportParamsPathFmt='cameras.json', outputViewportTexturePathFmt='{4}.yuv')
        # Input names also identify files; geometry uses a distinct directory.
        config['inputGeometryPathFmt'] = 'geometry/{3}.yuv'
        (self.work / 'geometry').mkdir(exist_ok=True)
        for index in range(2):
            (self.work / f'depth{index}.yuv').replace(self.work / 'geometry' / f'input{index}.yuv')
        (self.work / 'config.json').write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')

    def cancel(self):
        for process in list(self.processes):
            if process.poll() is None:
                try:process.kill()
                except OSError:pass

    def frames(self, cancel):
        height, width = self.scene.left.shape[:2]
        padded_width, padded_height = self.storage_size
        expected = padded_height * padded_width * 3
        base_command = [str(self.executable.resolve()), '-c', 'config.json',
                        '-n', '1', '-N', '1', '-s', 'Wigglinde', '-r', 'RP0', '-f', '0',
                        '-j', str(self.schedule['threads_per_view'])]
        started = time.monotonic()
        workers = self.schedule['workers']
        log_paths = [self.work / f'vws-{i}.log' for i in range(workers)]
        with ExitStack() as stack:
            try:
                for worker in range(workers):
                    check_cancelled(cancel)
                    command = base_command.copy()
                    for index in range(worker, len(self.positions), workers):
                        command += ['-v', f'view{index}']
                    log = stack.enter_context(log_paths[worker].open('wb'))
                    self.processes.append(subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=self.work,
                                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)))
                    self.process = self.processes[0]
                for index in range(len(self.positions)):
                    path = self.work / f'view{index}.yuv'
                    process = self.processes[index % workers]
                    while True:
                        check_cancelled(cancel)
                        try:
                            if path.stat().st_size == expected:
                                data = path.read_bytes()
                                if len(data) == expected:
                                    break
                        except (FileNotFoundError, PermissionError):
                            pass
                        if process.poll() is not None:
                            raise RuntimeError('VWS: ' + log_paths[index % workers].read_text(errors='replace')[-1800:])
                        time.sleep(.02)
                    yield yuv420_to_rgb(data, padded_height, padded_width)[:height, :width].copy()
                    try:
                        path.unlink()
                    except PermissionError:
                        pass
                while any(p.poll() is None for p in self.processes):
                    check_cancelled(cancel)
                    time.sleep(.02)
                for worker,process in enumerate(self.processes):
                    if process.returncode:
                        raise RuntimeError('VWS: ' + log_paths[worker].read_text(errors='replace')[-1800:])
            finally:
                self.cancel()
                for process in self.processes:process.wait()
                self.processes = []
                self.process = None
                self.metrics = dict(backend='TMIV VWS', views=len(self.positions),
                                    wall_seconds=time.monotonic() - started,
                                    parallel_workers=workers,threads_per_view=self.schedule['threads_per_view'],
                                    geometry_bits=10, input_geometry_bits=16, texture_bits=10,
                                    chroma='4:2:0', color='BT.709 full-range YUV',
                                    temporary_edge_padding=[padded_width - width, padded_height - height],
                                    inverse_depth_range=self.inverse_depth_range, bias=self.bias,
                                    max_disparity_quantization_px=self.max_disparity_quantization_px,
                                    parameters=VWS_PARAMETERS)
