"""Build-only DEFOM ONNX export; preserve the official model and reductions.

DEFOM-Stereo: MIT, copyright 2024 Insta360 Research Team; see UPSTREAM_LICENSE.txt.
Export adapters preserve dynamic sizes and the original bicubic scale offset.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from types import MethodType, SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F
from torch.onnx import symbolic_helper

SOURCE = "5b27591d83956e5d329ff66704271a9e68b1c75f"
WEIGHTS = {
    "vits": "aeb52a008f9c689ed23eaea562126ac1307d563fb8687002a657f06a6bf49da4",
    "vitl": "e8f17e18e8eb4455ddaf6130c6067b40063444acf7558c66d57963e60b539e25",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def configuration(encoder):
    return SimpleNamespace(
        dinov2_encoder=encoder, idepth_scale=0.5, hidden_dims=[128] * 3,
        corr_implementation="reg", corr_levels=2, corr_radius=4,
        scale_list=[0.125, 0.25, 0.5, 0.75, 1., 1.25, 1.5, 2.],
        scale_corr_radius=2, n_downsample=2, context_norm="batch",
        n_gru_layers=3, shared_backbone=False, mixed_precision=False,
    )


def load(source, weights, encoder):
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--", "core", "depth_anything_v2"], text=True)
    if revision != SOURCE or dirty or sha256(weights) != WEIGHTS[encoder]:
        raise ValueError("Unexpected source or weights")
    sys.path[:0] = [str(source.resolve()), str(source.resolve() / "core")]
    from core.defom_stereo import DEFOMStereo
    model = DEFOMStereo(configuration(encoder)).eval()
    state = torch.load(weights, map_location="cpu", weights_only=True, mmap=True)
    model.load_state_dict(state.get("model", state), strict=True)
    return model


def sizes(height, width, downsample, max_i_size=2688, multiple_of=14):
    """Tensor expression of upstream get_danv2_io_size, including its cap."""
    oh, ow = height // 2 ** downsample, width // 2 ** downsample
    ih = torch.ceil(oh.to(torch.float64) * 3.5 / multiple_of) * multiple_of
    iw = torch.ceil(ow.to(torch.float64) * 3.5 / multiple_of) * multiple_of
    limit = max_i_size // multiple_of * multiple_of
    capped_h = torch.where(ih >= iw, limit, torch.ceil(limit / iw * ih / multiple_of) * multiple_of)
    capped_w = torch.where(iw > ih, limit, torch.ceil(limit / ih * iw / multiple_of) * multiple_of)
    too_big = (ih > limit) | (iw > limit)
    ih = torch.where(too_big, capped_h, ih).to(torch.int64)
    iw = torch.where(too_big, capped_w, iw).to(torch.int64)
    return ih, iw, oh, ow


class PositionResize(torch.autograd.Function):
    @staticmethod
    def forward(ctx, values, height, width, offset, side):
        return F.interpolate(values, scale_factor=((float(height) + offset) / side,
                             (float(width) + offset) / side), mode="bicubic", antialias=False)

    @staticmethod
    @symbolic_helper.parse_args("v", "v", "v", "f", "i")
    def symbolic(g, values, height, width, offset, side):
        def constant(value, dtype):
            return g.op("Constant", value_t=torch.tensor(value, dtype=dtype))

        axes = constant([0], torch.int64)
        scales = []
        for value in (height, width):
            double = g.op("Cast", value, to_i=11)
            scale = g.op("Div", g.op("Add", double, constant(offset, torch.float64)), constant(side, torch.float64))
            scales.append(g.op("Unsqueeze", g.op("Cast", scale, to_i=1), axes))
        scales = g.op("Concat", constant([1., 1.], torch.float32), *scales, axis_i=0)
        return g.op("Resize", values, constant([], torch.float32), scales,
                    mode_s="cubic", coordinate_transformation_mode_s="half_pixel",
                    cubic_coeff_a_f=-0.75, exclude_outside_i=0)


def position_encoding(self, x, height, width):
    if self.interpolate_antialias:
        raise ValueError("Unexpected antialiased position interpolation")
    embedding = self.pos_embed.float()
    side = math.isqrt(embedding.shape[1] - 1)
    values = embedding[:, 1:].reshape(1, side, side, embedding.shape[-1]).permute(0, 3, 1, 2)
    values = PositionResize.apply(values, height // self.patch_size, width // self.patch_size,
                                  self.interpolate_offset, side)
    values = values.permute(0, 2, 3, 1).reshape(1, -1, embedding.shape[-1])
    return torch.cat((embedding[:, :1], values), dim=1).to(x.dtype)


@symbolic_helper.parse_args("v", "is", "is", "is", "is")
def unfold_symbolic(g, values, kernel, dilation, padding, stride):
    if (kernel, dilation, padding, stride) != ([3, 3], [1, 1], [1, 1], [1, 1]):
        raise ValueError("Unexpected unfold parameters")
    kernel = g.op("Constant", value_t=torch.eye(9).reshape(9, 1, 3, 3))
    patches = g.op("Conv", values, kernel, pads_i=[1, 1, 1, 1], strides_i=[1, 1])
    shape = g.op("Constant", value_t=torch.tensor([0, 9, -1], dtype=torch.int64))
    return g.op("Reshape", patches, shape)


def use_export_adapters(model):
    from core import defom_stereo
    original_sizes = defom_stereo.get_danv2_io_size

    def tensor_sizes(h, w, nds):
        if not torch.is_tensor(h):
            h = torch.tensor(h, dtype=torch.int64)
        if not torch.is_tensor(w):
            w = torch.tensor(w, dtype=torch.int64)
        return sizes(h, w, nds)

    for h, w in [(128, 416), (160, 448), (704, 1120), (3072, 3104), (3136, 4096), (4096, 3136)]:
        expected = original_sizes(h, w, 2)
        actual = tuple(int(v) for v in tensor_sizes(h, w, 2))
        if actual != expected:
            raise ValueError(f"Native size mismatch: {actual} vs {expected}")
    defom_stereo.get_danv2_io_size = tensor_sizes
    model.defomencoder.depth_anything.pretrained.interpolate_pos_encoding = MethodType(
        position_encoding, model.defomencoder.depth_anything.pretrained)
    torch.onnx.register_custom_op_symbolic("aten::im2col", unfold_symbolic, 18)
    return model


class Export(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, left, right):
        return self.model(left, right, iters=32, scale_iters=8, test_mode=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "weights", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--encoder", choices=list(WEIGHTS), required=True)
    args = parser.parse_args()
    torch.set_num_threads(8)
    torch.manual_seed(19)
    model = load(args.source, args.weights, args.encoder)
    cases = []
    print("Loaded official native model", flush=True)
    with torch.inference_mode():
        for width, height in [(416, 128), (448, 160)]:
            texture = torch.randint(0, 256, (1, 3, height, width + 8), dtype=torch.float32)
            left, right = texture[..., :width].contiguous(), texture[..., 8:].contiguous()
            value = model(left, right, iters=32, scale_iters=8, test_mode=True)
            cases.append((left.numpy(), right.numpy(), value.numpy()))
    model = use_export_adapters(model)
    errors = []
    with torch.inference_mode():
        for left, right, expected in cases:
            actual = model(torch.from_numpy(left), torch.from_numpy(right), iters=32, scale_iters=8, test_mode=True).numpy()
            np.testing.assert_allclose(actual, expected, atol=.001, rtol=.0001)
            errors.append(float(np.abs(actual - expected).max()))
        print("Native adapters verified; exporting all 32 updates", errors, flush=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        torch.onnx.export(Export(model).eval(), (torch.from_numpy(cases[0][0]), torch.from_numpy(cases[0][1])),
            str(args.output), opset_version=18, input_names=["left", "right"], output_names=["disparity"],
            dynamic_axes={"left": {2: "height", 3: "width"}, "right": {2: "height", 3: "width"}, "disparity": {2: "height", 3: "width"}},
            do_constant_folding=True, dynamo=False)
    np.savez_compressed(args.output.with_suffix(".validation.npz"), **{
        f"{i}_{name}": value for i, row in enumerate(cases) for name, value in zip(("left", "right", "disparity"), row)})
    metadata = dict(model="DEFOM-S/RVC" if args.encoder == "vits" else "DEFOM-L (CC-BY-NC-4.0)",
        source_revision=SOURCE, weights_sha256=WEIGHTS[args.encoder], onnx_sha256=sha256(args.output),
        precision="float32", iterations=32, scale_iterations=8, encoder=args.encoder,
        native_adapter_errors_px=errors, export_seconds=time.monotonic() - started,
        export_adapters=["dynamic upstream DA2 sizes including original 2688 cap", "dynamic bicubic position scales with original offset", "identity Conv for single-channel 3x3 unfold"],
        license="Apache-2.0 (underlying DA2 Small weights); DEFOM project MIT" if args.encoder == "vits" else "CC-BY-NC-4.0 (underlying DA2 Large weights); DEFOM project MIT")
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
