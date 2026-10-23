"""Compile the unchanged pinned upstream shaders and record their identity."""
from pathlib import Path
import argparse,hashlib,json,subprocess

UPSTREAM='e0f00f9c67dfd868d2b1489051e9118158b6de03'

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--glslc',default='glslc');a=p.parse_args()
    revision=subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()
    if revision!=UPSTREAM:raise ValueError('Unexpected HoviTron revision')
    changed=subprocess.check_output(['git','-C',str(a.source),'status','--porcelain','--untracked-files=no'],text=True)
    if changed:raise ValueError('Upstream source has local changes')
    a.output.mkdir(parents=True,exist_ok=True);rows=[]
    for source in sorted((a.source/'RVSVulkan/RVSVulkan/shaders').rglob('*')):
        if source.suffix not in ('.vert','.geom','.frag'):continue
        target=a.output/(source.name+'.spv')
        subprocess.run([a.glslc,str(source),'-o',str(target)],check=True)
        rows.append(dict(path=source.relative_to(a.source).as_posix(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),spirv_sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (a.output.parent/'shader-provenance.json').write_text(json.dumps(dict(upstream=UPSTREAM,compiler=subprocess.check_output([a.glslc,'--version'],text=True),shaders=rows),indent=2),encoding='utf-8')
    print(f'{len(rows)} unchanged upstream shaders compiled')
if __name__=='__main__':main()
