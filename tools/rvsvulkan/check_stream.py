"""Byte-level checks of the actual native frame packer and C/C++ log isolation."""
import argparse
import json
from pathlib import Path
import struct
import subprocess


def expected_rgb():
    return bytes(v for frame in range(2) for i in range(256)
                 for v in ((i+17*frame)%256,(37*i+29*frame)%256,(255-i+11*frame)%256))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--producer",type=Path,required=True)
    args=p.parse_args()
    expected=expected_rgb()
    rows=[]
    for w,h in ((1080,720),(1620,1080)):
        prefix=f"Real number of elements {6*(w-1)*(h-1)}\n".encode()
        for mode in ("float32","rgb24"):
            result=subprocess.run([str(args.producer),mode,str(w),str(h)],
                                  capture_output=True,check=True,timeout=10)
            if mode=="float32":
                assert len(result.stdout)==len(expected)*4
                values=struct.unpack("="+str(len(expected))+"f",result.stdout)
                actual=bytes(round(v*255) for v in values)
            else:
                assert len(result.stdout)==len(expected)
                actual=result.stdout
            assert actual==expected,(w,h,mode,"RGB changed or diagnostics entered pixels")
            lines=result.stderr.decode().splitlines()
            assert prefix.decode().strip() in lines
            assert "C++ renderer diagnostic" in lines
            assert "C diagnostic between frames" in lines
            rows.append(dict(size=[w,h],format=mode,bytes=len(result.stdout),rgb_identical=True))
        # Prove this regression detects the old implementation, including the
        # different float/channel alignment at the user's two exact sizes.
        old=subprocess.run([str(args.producer),"float32",str(w),str(h),"--legacy"],
                           capture_output=True,check=True,timeout=10)
        assert old.stdout.startswith(prefix)
        assert len(old.stdout)!=len(expected)*4
        assert len(prefix)==(32 if h==720 else 33)
    print(json.dumps(dict(status="passed",all_256_channel_values=True,
                          c_and_cpp_diagnostics_isolated=True,legacy_corruption_detected=True,
                          rgb24_transport_reduction=4,checks=rows),indent=2))


if __name__=="__main__":main()
