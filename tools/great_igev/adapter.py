"""Build/research-only GREAT-IGEV adapter; never imported by the application.

Uses the official GREAT-Stereo model and complete Middlebury checkpoint.
The streamed volume forward follows models/great_stereo/cost_volumes.py at the
pinned upstream revision, under that project's Apache License 2.0.
No reduced disparity search, image tiling, smoothing or altered weights.
"""

from pathlib import Path
from types import SimpleNamespace, MethodType
import sys
import hashlib
import torch
import timm
import torch.nn.functional as F

SOURCE_REVISION = "2a6b1efede8c3a9eec9540790c2700ea2f3dee7d"
WEIGHTS_SHA256 = "2f11060a718713df561cfb402494c11f05b157ce8a5da1b8364a0b9d53ef29cb"


def load(source, weights):
    import subprocess

    source = Path(source)
    weights = Path(weights)
    assert (
        subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        == SOURCE_REVISION
    )
    assert not subprocess.check_output(
        [
            "git",
            "-C",
            str(source),
            "status",
            "--porcelain",
            "--untracked-files=no",
            "--",
            "models",
            "utils",
        ],
        text=True,
    ).strip()
    sys.path.insert(0, str(source.resolve()))
    from models.great_stereo.great_igev_stereo import GREATStereo

    cfg = SimpleNamespace(
        name="great-igev-stereo",
        channels=[128] * 3,
        n_downsample=2,
        n_gru_layers=3,
        cv_levels=2,
        cv_radius=4,
        max_disp=768,
        mixed_precision=False,
        precision_dtype="float32",
        slow_fast_gru=False,
    )
    old = timm.create_model

    def offline(*a, **kw):
        kw["pretrained"] = False
        return old(*a, **kw)

    timm.create_model = offline
    try:
        model = GREATStereo(cfg).eval()
    finally:
        timm.create_model = old
    p = weights
    assert hashlib.sha256(p.read_bytes()).hexdigest() == WEIGHTS_SHA256
    state = torch.load(p, map_location="cpu", weights_only=True)
    model.load_state_dict(
        {k.removeprefix("module."): v for k, v in state.items()}, strict=True
    )
    return model


def streamed_stem(module, left, right, chunk=32):
    count = module.max_disp // 4
    w = left.shape[-1]
    padded = F.pad(right, (count - 1, 0))
    pieces = []
    # cc_stem has depth kernels 1,3,3: two disparity planes of halo suffice.
    for start in range(0, count, chunk):
        end = min(count, start + chunk)
        lo = max(0, start - 2)
        hi = min(count, end + 2)
        plane = torch.stack(
            [
                torch.cat((left, padded[:, :, :, count - 1 - d : count - 1 - d + w]), 1)
                for d in range(lo, hi)
            ],
            2,
        )
        filtered = module.cc_stem(plane)
        pieces.append(filtered[:, :, start - lo : end - lo])
    return torch.cat(pieces, 2)


def streamed_forward(self, left, right):
    from models.great_stereo.basic_modules import disparity_regression

    ml = self.global_spatial_refiner(left[0])
    mr = self.global_spatial_refiner(right[0])
    ml = ml + self.matching_pos(ml)
    mr = mr + self.matching_pos(mr)
    ml, mr = self.global_matching_refiner(ml.float(), mr.float())
    context = self.global_context_refiner(left)
    cc = streamed_stem(self, ml, mr)
    fv = self.feat_stem(context[0]).unsqueeze(2)
    fused = self.fuse_stem(fv * cc)
    volume, prob = self.eav_agg(fused, context)
    disp = disparity_regression(prob, self.max_disp // 4)
    return ml, mr, volume, disp


def use_streaming(model):
    model.excitive_attention_volume.forward = MethodType(
        streamed_forward, model.excitive_attention_volume
    )
    return model


class ConvUnfold(torch.nn.Module):
    def __init__(self, channels, kernel, padding, stride):
        super().__init__()
        self.channels = channels
        self.padding = padding
        self.stride = stride
        self.register_buffer(
            "weight",
            torch.eye(kernel * kernel)
            .reshape(kernel * kernel, 1, kernel, kernel)
            .repeat(channels, 1, 1, 1),
        )

    def forward(self, x):
        y = F.conv2d(
            x,
            self.weight,
            padding=self.padding,
            stride=self.stride,
            groups=self.channels,
        )
        return y.flatten(2)


def export_fold(input, output_size, kernel_size, dilation=1, padding=0, stride=1):
    # Only verified Outlook kernels 3/5/7, padding k//2, stride 1. Fold sums overlap.
    kh = kernel_size if isinstance(kernel_size, int) else kernel_size[0]
    kw = kernel_size if isinstance(kernel_size, int) else kernel_size[1]
    assert (
        kh == kw
        and kh in (3, 5, 7)
        and padding == kh // 2
        and stride == 1
        and dilation == 1
    )
    channels = int(input.shape[1]) // (kh * kw)
    weight = (
        torch.eye(kh * kw, dtype=input.dtype, device=input.device)
        .reshape(kh * kw, 1, kh, kw)
        .repeat(channels, 1, 1, 1)
    )
    x = input.reshape(
        input.shape[0], channels * kh * kw, output_size[0], output_size[1]
    )
    return F.conv_transpose2d(
        x, weight, padding=padding, stride=stride, groups=channels
    )


def export_upsample(disp_low, weights):
    kernel = torch.eye(9, dtype=disp_low.dtype, device=disp_low.device).reshape(
        9, 1, 3, 3
    )
    y = F.conv2d(disp_low, kernel, padding=1)
    y = F.interpolate(y, (disp_low.shape[2] * 4, disp_low.shape[3] * 4), mode="nearest")
    return (y * weights).sum(dim=1)


def dynamic_roll(x, shifts, dims):
    if isinstance(dims, int):
        dims = (dims,)
        shifts = (shifts,)
    for shift, dim in zip(shifts, dims):
        indices = (torch.arange(x.shape[dim], device=x.device) - shift) % x.shape[dim]
        x = torch.index_select(x, dim, indices)
    return x


class ExportTorch:
    roll = staticmethod(dynamic_roll)

    def __getattr__(self, key):
        return getattr(torch, key)


class ExportFunctions:
    fold = staticmethod(export_fold)

    def __getattr__(self, key):
        return getattr(F, key)


def use_export_ops(model):
    import inspect
    import textwrap
    from models.great_stereo import basic_modules, great_igev_stereo, transformers

    for module in model.modules():
        if isinstance(module, transformers.OutlookAttentionLayer):
            assert (
                module.kernel_size in (3, 5, 7)
                and module.padding == module.kernel_size // 2
                and module.stride == 1
            )
            module.unfold = ConvUnfold(
                module.to_v.out_channels,
                module.kernel_size,
                module.padding,
                module.stride,
            )
            original = module.forward.__func__
            source = textwrap.dedent(inspect.getsource(original))
            old = "hh, ww = math.ceil(h / self.stride), math.ceil(w / self.stride)"
            assert old in source
            source = source.replace(old, "hh, ww = h, w")
            namespace = dict(original.__globals__)
            namespace["F"] = ExportFunctions()
            exec(compile(source, "<great-outlook-export>", "exec"), namespace)
            module.forward = MethodType(namespace["forward"], module)
    # Restrict dynamic-roll adaptation to the upstream transformer module.
    transformers.torch = ExportTorch()
    basic_modules.context_upsample = export_upsample
    great_igev_stereo.context_upsample = export_upsample
    return model
