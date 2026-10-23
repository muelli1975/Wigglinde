"""Build-time GREAT mixed conversion, with Float32 attention and overlap sums."""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location(
        'great_mixed_conversion', Path(__file__).parents[1] / 'convert_las2_mixed.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.FP32_OPS |= {'MatMul', 'Einsum', 'LayerNormalization', 'ConvTranspose',
                       'CumSum', 'Sin', 'Cos'}
    metadata = module.convert(args.source, args.output)
    metadata['conversion']['policy'] = 'great_igev_onnx_mixed_v1'
    args.output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    check = module.verify(args.source, args.output)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(dict(metadata=metadata, verification=check), indent=2))
    print(json.dumps(check), flush=True)


if __name__ == '__main__':
    main()
