"""Build a portable Windows archive from explicit local prerequisites."""
from pathlib import Path
import argparse,glob,importlib.metadata as metadata,json,shutil,subprocess,sys,zipfile,urllib.request

def main():
    p=argparse.ArgumentParser();p.add_argument('--opencv',type=Path,required=True);p.add_argument('--rvs',type=Path,required=True);p.add_argument('--las2',type=Path,required=True);p.add_argument('--igev',type=Path,required=True);a=p.parse_args()
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--windowed','--name','Wigglinde','--icon','assets/wigglinde.ico','--runtime-hook','tools/pyi_offline.py','--collect-all','customtkinter','--collect-all','imageio_ffmpeg','--collect-all','onnxruntime','--hidden-import','PIL.ImageCms','launch.py'],check=True)
    target=Path('dist/Wigglinde');backend=target/'backend';backend.mkdir()
    shutil.copy2('build/rvs/Release/wigglinde_rvs.exe',backend)
    shutil.copy2(a.opencv/'build/x64/vc16/bin/opencv_world4100.dll',backend)
    # Microsoft permits app-local deployment of its redistributable CRT/OpenMP DLLs.
    roots=glob.glob('C:/Program Files/Microsoft Visual Studio/*/*/VC/Redist/MSVC/*/x64/Microsoft.VC*.CRT')
    if not roots:raise RuntimeError('Microsoft C++ redistributable files not found')
    for folder in sorted(roots)[-1:]:
        for dll in Path(folder).glob('*.dll'):
            shutil.copy2(dll,backend)
            shutil.copy2(dll,target/'_internal')
    omps=glob.glob('C:/Program Files/Microsoft Visual Studio/*/*/VC/Redist/MSVC/*/x64/Microsoft.VC*.OpenMP/vcomp140.dll')
    if omps:shutil.copy2(sorted(omps)[-1],backend)
    shutil.copytree('assets',target/'assets')
    from wigglinde.models import MODELS,DEFAULT_MODEL,model_path
    from wigglinde import __version__
    for label in MODELS:
        for device in (None,0):
            source_model=model_path('.',label,device)
            destination=target/source_model
            destination.parent.mkdir(parents=True,exist_ok=True)
            for extension in ('.onnx','.json'):
                shutil.copy2(source_model.with_suffix(extension),destination.with_suffix(extension))
    notices=target/'licenses';notices.mkdir();shutil.copytree('runtime-wheel/licenses',notices/'DirectML-runtime');shutil.copy2('runtime-wheel/provenance.json',notices/'DirectML-build.json');shutil.copy2('LICENSE',notices/'Wigglinde-MIT.txt')
    for name in ['LICENSE.txt','tcl/tcl8.6/license.terms','tcl/tk8.6/license.terms']:
        file=Path(sys.base_prefix)/name
        if file.is_file():
            dest=notices/'Python-Tcl-Tk'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
    shutil.copy2(a.rvs/'LICENSE',notices/'RVS-LICENSE.txt');shutil.copy2(a.las2/'LICENSE',notices/'LAS2-LICENSE.txt');shutil.copy2(a.igev/'LICENSE',notices/'IGEV-LICENSE.txt')
    shutil.copy2('tools/igev/licenses/timm-LICENSE.txt',notices/'IGEV-timm-Apache-2.0.txt')
    for name in ['LICENSE','LICENSE.txt','LICENSE-3RD-PARTY.txt','LICENSE_FFMPEG.txt']:
        for f in a.opencv.rglob(name):
            if f.is_file() and f.stat().st_size<2_000_000:
                dest=notices/'OpenCV'/f.relative_to(a.opencv);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    for name in ['numpy','pillow','onnxruntime-directml','customtkinter','darkdetect','imageio-ffmpeg','protobuf','flatbuffers','packaging','pyinstaller']:
        dist=metadata.distribution(name)
        for item in dist.files or []:
            if any(x in str(item).lower() for x in ['license','copying','copyright','notice']):
                f=Path(dist.locate_file(item))
                if f.is_file():
                    dest=notices/name/str(item).replace('../','');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    for name in ['README.md','README_DE.md','BUILD.md']:
        text=Path(name).read_text(encoding='utf-8')
        text=text.replace('](docs/','](source/docs/').replace('](.github/','](source/.github/')
        (target/name).write_text(text,encoding='utf-8')
    for name in ['LICENSE','THIRD_PARTY.md','CHANGELOG.md']:
        shutil.copy2(name,target/name)
    shutil.copy2('THIRD_PARTY.md',notices/'THIRD_PARTY.md')
    from imageio_ffmpeg import get_ffmpeg_exe
    (notices/'FFmpeg-build.txt').write_bytes(subprocess.check_output([get_ffmpeg_exe(),'-version']))
    with urllib.request.urlopen('https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.0.2/COPYING.GPLv3',timeout=60) as response:
        (notices/'FFmpeg-GPL-3.0.txt').write_bytes(response.read())
    # Exact project source, without model files, external checkouts or local output.
    source=target/'source';source.mkdir()
    data=subprocess.check_output(['git','ls-files','-z']).split(b'\0')
    for raw in data:
        if not raw:continue
        f=Path(raw.decode())
        if f.is_file():dest=source/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    (target/'build-info.json').write_text(json.dumps(dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),version=__version__,renderer='RVS CPU Precision 1 Simple 5',models=list(MODELS),default_model=DEFAULT_MODEL,model_precision={'CPU':'float32','GPU':'mixed_float16_float32'},devices='CPU / DirectML (stereo), CPU (RVS)',packages={n:metadata.version(n) for n in ['numpy','pillow','onnxruntime-directml','customtkinter','imageio-ffmpeg']}),indent=2))
    # Explicit development smoke test, not an application startup operation.
    subprocess.run([str((target/'Wigglinde.exe').resolve()),'--self-test',str(Path('output/windows-smoke.json').resolve())],check=True,timeout=600)
    archive=Path(f'dist/Wigglinde_{__version__}_Windows_x64.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,6) as z:
        for f in target.rglob('*'):
            if f.is_file() and '_temp' not in f.parts and f.relative_to(target).parts[0]!='logs' and f.name!='settings.json':z.write(f,f.relative_to(target.parent))
    import hashlib
    verification=dict(status='passed',version=__version__,models=list(MODELS),platform='Windows_x64',commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),filename=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),actual_packaged_application_tested=True,renderer='RVS CPU Precision 1 Simple 5')
    Path('output/package-verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps(verification))
if __name__=='__main__':main()
