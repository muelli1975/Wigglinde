"""DEFOM mixed precision: FP16 convolutions/linears, FP32 sensitive islands."""

import argparse
import importlib.util
import json
from pathlib import Path


def connect_float32_island(model, node_names):
    """Bypass converter-inserted FP32->FP16->FP32 edges inside the island.

    Node blocking alone wraps each protected node independently. Rounding its
    output to half before the next protected node would still overflow. Keep
    those internal edges in FP32, retaining half casts for real FP16 consumers.
    """
    by_output = {out: node for node in model.graph.node for out in node.output}
    protected = set(node_names)
    bypassed = 0
    for cast in model.graph.node:
        if cast.op_type != 'Cast' or not any(a.name == 'to' and a.i == 1 for a in cast.attribute):
            continue
        previous = by_output.get(cast.input[0])
        if previous is None or previous.op_type != 'Cast' or not any(a.name == 'to' and a.i == 10 for a in previous.attribute):
            continue
        producer = by_output.get(previous.input[0])
        if producer is None or producer.name not in protected:
            continue
        for consumer in model.graph.node:
            if consumer.name in protected:
                for i, name in enumerate(consumer.input):
                    if name == cast.output[0]:
                        consumer.input[i] = previous.input[0]
                        bypassed += 1
    while True:
        used = {name for node in model.graph.node for name in node.input} | {v.name for v in model.graph.output}
        dead = [node for node in model.graph.node if node.op_type == 'Cast' and not any(o in used for o in node.output)]
        if not dead:
            break
        for node in dead:
            model.graph.node.remove(node)
    live = {name for node in model.graph.node for name in (*node.input, *node.output)}
    for value in list(model.graph.value_info):
        if value.name not in live:
            model.graph.value_info.remove(value)
    return bypassed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('conversion', Path(__file__).parents[1] / 'convert_las2_mixed.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Keep the all-pairs correspondence Einsum and normalization/probability/
    # resampling math in FP32. Transformer linears and attention MatMul may use
    # FP16, following the purpose of the model's native mixed-precision path.
    module.FP32_OPS |= {'Einsum', 'LayerNormalization', 'ReduceMean', 'ReduceMax', 'Sqrt', 'Pow'}
    original_converter = module.float16.convert_float_to_float16
    sensitive_nodes = []
    bypassed_casts = []
    source_meta = json.loads(args.source.with_suffix('.json').read_text())
    if source_meta['encoder'] == 'vitl':
        # Measured on the unchanged native/checkpoint graph: Large's feature
        # decoder exceeds FP16's finite range. Preserve that complete path,
        # including its slices, concatenation and convolution up to normalization.
        # This is a fixed build-time precision policy, never a runtime fallback.
        def convert_with_decoder_island(model, **kwargs):
            sensitive_nodes.extend(n.name for n in model.graph.node if
                '/defomencoder/depth_anything/depth_feat/' in n.name or
                n.name.startswith('/model/fnet/convd/') or n.name == '/model/fnet/Concat')
            kwargs['node_block_list'] = sensitive_nodes
            converted = original_converter(model, **kwargs)
            bypassed_casts.append(connect_float32_island(converted, sensitive_nodes))
            return converted
        module.float16.convert_float_to_float16 = convert_with_decoder_island
    metadata = module.convert(args.source, args.output)
    metadata['conversion']['policy'] = 'defom_onnx_mixed_v3' if sensitive_nodes else 'defom_onnx_mixed_v1'
    if sensitive_nodes:
        metadata['conversion']['fp32_nodes'] = sensitive_nodes
        metadata['conversion']['fp32_internal_half_roundtrips_bypassed'] = sum(bypassed_casts)
        metadata['conversion']['fp32_decoder_reason'] = 'Large feature decoder activations exceed finite Float16 range; retain decoder/transport/fusion until normalization in Float32.'
    args.output.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(dict(bytes=args.output.stat().st_size, conversion=metadata['conversion'])), flush=True)


if __name__ == '__main__':
    main()
