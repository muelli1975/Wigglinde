"""Build-time conversion only; runtime never edits or downloads a model."""
from pathlib import Path
import argparse
import hashlib
import json
import warnings
from collections import Counter

import numpy as np
import onnx
import onnxruntime as ort
from onnxruntime.transformers import float16
from onnxruntime.transformers.onnx_model import OnnxModel


# Keep numerically sensitive normalization/probability/reduction operations and
# correspondence sampling in FP32. Use ORT's standard compatibility block list
# as well. This is an ONNX policy, not a claim to reproduce CUDA autocast exactly.
FP32_OPS = {'BatchNormalization', 'InstanceNormalization', 'Softmax', 'ReduceSum',
            'GridSample', 'Resize'}


def convert(source, output):
    if ort.__version__ != '1.24.4':
        raise ValueError('Conversion requires the pinned ONNX Runtime 1.24.4.')
    original = onnx.load(source)
    metadata = json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != metadata['onnx_sha256']:
        raise ValueError('Source model hash differs from its export metadata.')
    blocks = sorted(set(float16.DEFAULT_OP_BLOCK_LIST) | FP32_OPS)
    with warnings.catch_warnings(record=True) as conversion_warnings:
        converted = float16.convert_float_to_float16(original, keep_io_types=True, op_block_list=blocks)
    OnnxModel(converted).topological_sort()
    onnx.checker.check_model(converted, full_check=True)
    if any(value.type.tensor_type.elem_type != onnx.TensorProto.FLOAT
           for value in list(converted.graph.input) + list(converted.graph.output)):
        raise ValueError('Mixed model must retain Float32 inputs and output.')
    # In particular, LAS2-H has a BatchNorm running variance above FP16's range.
    # ORT must retain that FP32 initializer, rather than clip it to a finite half.
    original = onnx.load(source)
    initializers = {t.name: t for t in converted.graph.initializer}
    for tensor in original.graph.initializer:
        if tensor.data_type == onnx.TensorProto.FLOAT:
            values = onnx.numpy_helper.to_array(tensor)
            if np.abs(values).max() > 65504:
                if initializers[tensor.name].SerializeToString() != tensor.SerializeToString():
                    raise ValueError('Out-of-range Float32 initializer was changed: ' + tensor.name)
    output.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(converted, output)
    counts = Counter(onnx.TensorProto.DataType.Name(t.data_type) for t in converted.graph.initializer)
    if not counts['FLOAT16'] or not counts['FLOAT']:
        raise ValueError('Expected both Float16 and Float32 initializers.')
    metadata['source_export_validation']={key:metadata.pop(key) for key in
        ('native_max_errors_px','comparison_tolerance') if key in metadata}
    metadata.update(precision='mixed_float16_float32', source_onnx_sha256=source_hash,
        onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        conversion=dict(tool='onnxruntime.transformers.float16', version=ort.__version__,
            keep_io_types=True, fp32_ops=blocks,
            initializer_types=dict(counts), warnings=[str(w.message) for w in conversion_warnings],
            policy='las2_h_onnx_mixed_v1', cuda_autocast_equivalence=False))
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


def verify(source, converted):
    # Explicit development check, not a runtime per-picture acceptance gate.
    # CPU execution checks the converted graph and records numerical differences;
    # it cannot establish physical DirectML behavior or GPU memory savings.
    options = ort.SessionOptions()
    options.intra_op_num_threads = 8
    sessions = [ort.InferenceSession(str(p), sess_options=options, providers=['CPUExecutionProvider'])
                for p in (source, converted)]
    results = []
    rng = np.random.default_rng(37)
    for width, height in ((416, 128), (448, 160)):
        texture = rng.integers(0, 256, (1, 3, height, width + 8)).astype(np.float32)
        feed = dict(left=texture[:, :, :, :width].copy(), right=texture[:, :, :, 8:].copy())
        ref, actual = [s.run(None, feed)[0] for s in sessions]
        if ref.shape != actual.shape or not np.isfinite(actual).all():
            raise ValueError('Invalid converted-model output.')
        error = np.abs(ref - actual)
        # Small-shape conversion sanity check, not a photographic quality claim.
        np.testing.assert_allclose(actual, ref, rtol=.01, atol=.1)
        results.append(dict(size=[width, height], max_difference_px=float(error.max()),
            mean_difference_px=float(error.mean()), p99_difference_px=float(np.quantile(error, .99))))
    return dict(status='passed', execution_provider='CPUExecutionProvider',
        physical_gpu_validated=False, photographic_quality_validated=False, cases=results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    metadata = convert(args.source, args.output)
    check = verify(args.source, args.output)
    report = dict(metadata=metadata, verification=check)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(status='passed', bytes=args.output.stat().st_size,
                         conversion=metadata['conversion'], verification=check)))


if __name__ == '__main__':
    main()
