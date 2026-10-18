"""IGEV++ GPU mixed graph with Float32 correspondence and sampling islands."""
from pathlib import Path
import argparse,importlib.util,json

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    spec=importlib.util.spec_from_file_location('mixed_conversion',Path(__file__).parents[1]/'convert_las2_mixed.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # Feature convolutions can use FP16; large all-pairs correlation and its
    # coordinates, distributions, normalization and bilinear sampling retain FP32.
    module.FP32_OPS|={'MatMul','Einsum'}
    metadata=module.convert(a.source,a.output)
    metadata['conversion']['policy']='igev_onnx_mixed_v1'
    a.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2))
    check=module.verify(a.source,a.output)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(dict(metadata=metadata,verification=check),indent=2))
    print(json.dumps(dict(status='passed',bytes=a.output.stat().st_size,verification=check)),flush=True)
if __name__=='__main__':main()
