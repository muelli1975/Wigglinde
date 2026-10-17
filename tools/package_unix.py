"""Native CPU packages; test the extracted archive before publishing it."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'Linux_x64': ('Linux', 'x86_64'),
          'macOS_AppleSilicon': ('Darwin', 'arm64'),
          'macOS_Intel': ('Darwin', 'x86_64')}
MODEL_SHA = 'ba2260dcc0aaff33a9fc1c41f729f727eb58eb034dfaec022713b3848ff5af76'


def run(*command, **kwargs):
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True, **kwargs)


def download(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        destination.write_bytes(response.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', choices=LABELS, required=True)
    args = parser.parse_args()
    if LABELS[args.label] != (platform.system(), platform.machine()):
        raise SystemExit('Package label does not match native build architecture.')
    model = ROOT / 'models/las2/LAS2_H_dynamic.onnx'
    if hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA:
        raise SystemExit('Unexpected Float32 H model.')
    backend = ROOT / 'build/rvs/wigglinde_rvs'
    if not backend.is_file():
        raise SystemExit('Build the pinned RVS backend first.')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
               '--onedir', '--windowed', '--name', 'Wigglinde',
               '--runtime-hook', 'tools/pyi_offline.py',
               '--collect-all', 'customtkinter', '--collect-all', 'imageio_ffmpeg',
               '--collect-all', 'onnxruntime', '--hidden-import', 'PIL.ImageCms',
               '--hidden-import', 'PIL.ImageTk', '--hidden-import', 'PIL._tkinter_finder',
               '--add-binary', str(backend) + ':backend']
    if sys.platform == 'darwin':
        from PIL import Image
        icon = ROOT / 'build/Wigglinde.icns'
        with Image.open(ROOT / 'assets/wigglinde.ico') as image:
            image.convert('RGBA').save(icon)
        command += ['--icon', str(icon), '--osx-bundle-identifier', 'org.stereotools.wigglinde']
    run(*command, 'launch.py')
    if sys.platform == 'darwin':
        target = ROOT / 'release-stage/Wigglinde'
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        bundle = ROOT / 'dist/Wigglinde.app'
        run('codesign', '--force', '--deep', '--sign', '-', bundle)
        run('codesign', '--verify', '--deep', '--strict', bundle)
        run('ditto', bundle, target / 'Wigglinde.app')
    else:
        target = ROOT / 'dist/Wigglinde'
    shutil.copytree(ROOT / 'assets', target / 'assets')
    models = target / 'models/las2'
    models.mkdir(parents=True)
    for extension in ('onnx', 'json'):
        shutil.copy2(ROOT / ('models/las2/LAS2_H_dynamic.' + extension), models)
    notices = target / 'licenses'
    notices.mkdir()
    for source, name in [('LICENSE', 'Wigglinde-MIT.txt'),
                         ('rvs-reference/LICENSE', 'RVS-LICENSE.txt'),
                         ('las2-reference/LICENSE', 'LAS2-LICENSE.txt'),
                         ('opencv-reference/LICENSE', 'OpenCV-LICENSE.txt')]:
        shutil.copy2(ROOT / source, notices / name)
    # Preserve notices for the exact OpenCV third-party sources, including codecs.
    for file in (ROOT / 'opencv-reference/3rdparty').rglob('*'):
        if file.is_file() and any(term in file.name.lower() for term in ('license', 'copying', 'copyright', 'notice')):
            destination = notices / 'OpenCV-third-party' / file.relative_to(ROOT / 'opencv-reference/3rdparty')
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, destination)
    packages = ['numpy', 'pillow', 'onnxruntime', 'customtkinter', 'darkdetect',
                'imageio-ffmpeg', 'protobuf', 'flatbuffers', 'packaging', 'pyinstaller']
    if sys.platform == 'darwin':
        packages.append('psutil')
    # Include transitive runtime/build dependency notices as well (e.g. sympy,
    # mpmath and Intel ORT's coloredlogs/humanfriendly).
    for dist in metadata.distributions():
        name = dist.metadata['Name']
        for item in dist.files or []:
            if any(term in str(item).lower() for term in ('license', 'copying', 'copyright', 'notice')):
                file = Path(dist.locate_file(item))
                if file.is_file():
                    destination = notices / name / str(item).replace('../', '')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, destination)
    download('https://raw.githubusercontent.com/python/cpython/v3.12.10/LICENSE', notices / 'Python-LICENSE.txt')
    import tkinter
    interpreter = tkinter.Tcl()
    tcl_version = interpreter.call('info', 'patchlevel')
    for repo in ('tcl', 'tk'):
        tag = 'core-' + tcl_version.replace('.', '-')
        download(f'https://raw.githubusercontent.com/tcltk/{repo}/{tag}/license.terms', notices / f'{repo}-license.terms')
    # OpenMP runtime is collected as a native RVS dependency by PyInstaller.
    if sys.platform == 'darwin':
        formula = json.loads(subprocess.check_output(['brew', 'info', '--json=v2', 'libomp']))['formulae'][0]
        version = formula['versions']['stable']
        download(f'https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-{version}/openmp/LICENSE.TXT', notices / 'OpenMP-LICENSE.txt')
        (notices / 'OpenMP-build.json').write_text(json.dumps(formula, indent=2))
    else:
        shutil.copy2('/usr/share/doc/gcc-11-base/copyright', notices / 'GCC-runtime-copyright.txt')
    from imageio_ffmpeg import get_ffmpeg_exe
    (notices / 'FFmpeg-build.txt').write_bytes(subprocess.check_output([get_ffmpeg_exe(), '-version']))
    download('https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.0.2/COPYING.GPLv3', notices / 'FFmpeg-GPL-3.0.txt')
    for name in ('README.md', 'README_DE.md', 'BUILD.md'):
        text = (ROOT / name).read_text(encoding='utf-8')
        text = text.replace('](docs/', '](source/docs/').replace('](.github/', '](source/.github/')
        (target / name).write_text(text, encoding='utf-8')
    for name in ('LICENSE', 'THIRD_PARTY.md', 'CHANGELOG.md'):
        shutil.copy2(ROOT / name, target / name)
    source = target / 'source'
    for raw in subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0'):
        if raw:
            file = Path(raw.decode())
            destination = source / file
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / file, destination)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    info = dict(version='1.0', renderer='RVS CPU Precision 1 Simple 5', commit=commit, platform=args.label, python=sys.version,
                models=['LAS2-H'], model_sha256=MODEL_SHA, model_precision={'CPU': 'float32'},
                devices='CPU (LAS2 and RVS)', tcl_version=tcl_version,
                packages={name: metadata.version(name) for name in packages})
    (target / 'build-info.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    release = ROOT / 'release'
    release.mkdir(exist_ok=True)
    archive = release / ('Wigglinde_1.0_' + args.label + ('.zip' if sys.platform == 'darwin' else '.tar.gz'))
    if sys.platform == 'darwin':
        run('ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', target, archive)
    else:
        with tarfile.open(archive, 'w:gz') as handle:
            handle.add(target, arcname='Wigglinde')
    # Exercise the shipped archive, not the source interpreter or staging folder.
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='Wigglinde_Ä_') as temporary:
        unpacked = Path(temporary)
        if sys.platform == 'darwin':
            run('ditto', '-x', '-k', archive, unpacked)
            app = unpacked / 'Wigglinde/Wigglinde.app'
            run('codesign', '--verify', '--deep', '--strict', app)
            executable = app / 'Contents/MacOS/Wigglinde'
        else:
            with tarfile.open(archive) as handle:
                handle.extractall(unpacked, filter='data')
            executable = unpacked / 'Wigglinde/Wigglinde'
        run(executable, '--self-test', output / 'native-smoke.json', timeout=420)
        if sys.platform == 'darwin':
            run('codesign', '--verify', '--deep', '--strict', app)
    report = json.loads((output / 'native-smoke.json').read_text(encoding='utf-8'))
    assert report['status'] == 'passed' and not report['mixed_model_bundled']
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    verification = dict(status='passed', renderer='RVS CPU Precision 1 Simple 5', platform=args.label, commit=commit,
                        filename=archive.name, bytes=archive.stat().st_size, sha256=digest,
                        model_sha256=MODEL_SHA, actual_extracted_package_tested=True)
    (output / 'package-verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps(verification))


if __name__ == '__main__':
    main()
