"""Explicit native VWS geometry/transport checks; no model inference or tuning."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from wigglinde.stereo import StereoScene
from wigglinde.vws import VWSRenderer
from wigglinde.wiggle_export import ExportCancelled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = []
    with tempfile.TemporaryDirectory(prefix='VWS_Größe_') as folder:
        for index, (width, height, disparity) in enumerate([(96, 32, 8), (97, 33, -6)]):
            y, x = np.mgrid[:height, :width]
            def image(position):
                gray = np.rint(32 + x + y + position * disparity).astype(np.uint8)
                return np.repeat(gray[:, :, None], 3, axis=2)
            left, right = image(0), image(1)
            depth = np.full((height, width), disparity, np.float32)
            scene = StereoScene(left, right, depth, depth.copy())
            originals = [a.copy() for a in (left, right, scene.left_disparity, scene.right_disparity)]
            renderer = VWSRenderer(args.renderer.resolve(), scene, [.25, .5, .75],
                                   Path(folder) / str(index), 24)
            cases = []
            for position, frame in zip([.25, .5, .75], renderer.frames(lambda: False)):
                assert frame.shape == left.shape
                # Check registration away from disoccluded borders. Wrong sign,
                # focal scaling or an unremoved offset exceeds this tolerance.
                error = np.abs(frame[:, 16:-16].astype(float) - image(position)[:, 16:-16])
                cases.append(dict(position=position, max_error=float(error.max()), mean_error=float(error.mean())))
                assert error.max() <= 2 and error.mean() < 1, cases[-1]
            for original, array in zip(originals, (left, right, scene.left_disparity, scene.right_disparity)):
                np.testing.assert_array_equal(original, array)
            serial = VWSRenderer(args.renderer.resolve(), scene, [.25, .5, .75],
                                 Path(folder) / f'{index}-serial', 24, worker_count=1)
            parallel = VWSRenderer(args.renderer.resolve(), scene, [.25, .5, .75],
                                   Path(folder) / f'{index}-parallel', 24, worker_count=3)
            reference = list(serial.frames(lambda: False))
            actual = list(parallel.frames(lambda: False))
            for a, b in zip(reference, actual):np.testing.assert_array_equal(a, b)
            rows.append(dict(size=[width, height], disparity=disparity, cases=cases,
                             metrics=renderer.metrics, originals_unchanged=True,serial_parallel_bit_equal=True))
        renderer = VWSRenderer(args.renderer.resolve(), scene, [.5]*12, Path(folder) / 'cancel', 24,worker_count=3)
        cancelled=False
        iterator = renderer.frames(lambda: cancelled)
        next(iterator)
        processes=list(renderer.processes)
        cancelled=True
        try:
            next(iterator)
        except ExportCancelled:
            pass
        else:
            raise AssertionError('Cancellation was not honored.')
        assert renderer.process is None
        assert not renderer.processes and all(p.poll() is not None for p in processes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='passed', checks=rows, cancellation=True), indent=2))
    print(args.output.read_text())


if __name__ == '__main__':
    main()
