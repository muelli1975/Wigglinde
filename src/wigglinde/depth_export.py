"""Lossless, jointly normalized disparity maps for the corresponding RGB halves."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from .wiggle_export import check_cancelled


def save_depth_maps(left, right, source, output_stem, output_root, work, cancel):
    maps = (left, right)
    if left.shape != right.shape or not all(np.isfinite(d).all() for d in maps):
        raise ValueError('Ungültige Tiefenkarten / invalid depth maps')
    low = float(min(d.min() for d in maps))
    high = float(max(d.max() for d in maps))
    height, width = left.shape
    stem = f'{output_stem}_depth_{height}p'
    names = [f'{stem}_{side}.png' for side in ('left', 'right')]
    work = Path(work) / 'depth_export'
    work.mkdir()
    for name, disparity in zip(names, maps):
        check_cancelled(cancel)
        if high > low:
            values = np.rint((disparity.astype(np.float64) - low) * (65535.0 / (high - low))).clip(0, 65535).astype(np.uint16)
        else:
            values = np.zeros(disparity.shape, np.uint16)
        Image.fromarray(values).save(work / name)
    metadata = dict(schema=1, source=Path(source).name, maps=dict(zip(('left', 'right'), names)),
        size=[width, height], encoding='uint16_png', white='near', black='far',
        quantity='relative_disparity', units='processing_pixels', metric_depth=False,
        disparity_convention='x_left_minus_x_right_at_corresponding_half_coordinates',
        normalization='joint_linear_min_max', disparity_min=low, disparity_max=high,
        decode='disparity = disparity_min + png_value / 65535 * (disparity_max - disparity_min)',
        rgb_reference='Corresponding left/right half after EXIF orientation, ICC-to-sRGB conversion and output-size scaling; no alignment or crop.')
    metadata_name = stem + '.json'
    (work / metadata_name).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    check_cancelled(cancel)
    target = Path(output_root) / 'depth_maps'
    target.mkdir(parents=True, exist_ok=True)
    for name in names + [metadata_name]:
        (work / name).replace(target / name)
    return dict(metadata, files=[str(target / name) for name in names], metadata_file=str(target / metadata_name))
