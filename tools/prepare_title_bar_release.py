"""Rebuild and check the title-bar update with each released portable runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / '.github/title-bar-update.json'
PORTABLE = ROOT / 'portable'
APPLICATION = PORTABLE / 'Wigglinde'
CANDIDATES = ROOT / 'title-bar-release'
BUNDLE = 'Wigglinde.app'
TARGETS = {
    'Windows_x64': ('Windows', 'AMD64', 'Wigglinde.exe'),
    'macOS_AppleSilicon': ('Darwin', 'arm64', BUNDLE + '/Contents/MacOS/Wigglinde'),
    'macOS_Intel': ('Darwin', 'x86_64', BUNDLE + '/Contents/MacOS/Wigglinde'),
}


def run(*args, **kwargs):
    return subprocess.run([str(item) for item in args], cwd=ROOT, check=True, **kwargs)


def digest(path):
    with path.open('rb') as source:
        return 'sha256:' + hashlib.file_digest(source, 'sha256').hexdigest()


def unpack(archive, directory, mac):
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and ':' not in name and '\\' not in name, name
        if not mac:
            package.extractall(directory)
    if mac:
        run('ditto', '-x', '-k', archive, directory)


def download(plan, name, mac):
    folder = ROOT / 'released-inputs'
    folder.mkdir(exist_ok=True)
    run('gh', 'release', 'download', plan['tag'], '--repo', plan['repository'],
        '--pattern', name, '--dir', folder)
    archive = folder / name
    assert digest(archive) == plan['assets'][name], name
    unpack(archive, PORTABLE, mac)
    if mac:
        run('codesign', '--verify', '--deep', '--strict', APPLICATION / BUNDLE)
    info = json.loads((APPLICATION / 'build-info.json').read_text(encoding='utf-8'))
    if 'GITHUB_OUTPUT' in os.environ:
        version = info.get('packages', {}).get('pyinstaller', '6.19.0')
        assert version.replace('.', '').isdecimal(), version
        with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
            output.write(f'pyinstaller={version}\n')


def repackage(name, executable, mac):
    from PyInstaller.archive.readers import CArchiveReader

    frozen = ROOT / 'frozen/Wigglinde' / Path(executable).name
    binary = APPLICATION / executable
    packaged = CArchiveReader(str(frozen)).open_embedded_archive('PYZ.pyz')
    assert 'wigglinde.titlebar' in packaged.toc
    shutil.copy2(frozen, binary)
    if mac:
        app = APPLICATION / BUNDLE
        run('codesign', '--force', '--sign', '-', app)
        run('codesign', '--verify', '--deep', '--strict', app)

    source = APPLICATION / 'source'
    for raw in subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0'):
        if raw:
            path = Path(raw.decode())
            destination = source / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)
    info_path = APPLICATION / 'build-info.json'
    info = json.loads(info_path.read_text(encoding='utf-8'))
    info['commit'] = os.environ['GITHUB_SHA']
    info_path.write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')

    CANDIDATES.mkdir(exist_ok=True)
    archive = CANDIDATES / name
    if mac:
        run('ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', APPLICATION, archive)
    else:
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
            for file in APPLICATION.rglob('*'):
                if file.is_file():
                    package.write(file, file.relative_to(PORTABLE))

    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='Wigglinde_Ä_') as temporary:
        extracted = Path(temporary)
        unpack(archive, extracted, mac)
        app = extracted / 'Wigglinde'
        if mac:
            run('codesign', '--verify', '--deep', '--strict', app / BUNDLE)
        originals = {p.relative_to(APPLICATION): digest(p) for p in (APPLICATION / 'models').rglob('*') if p.is_file()}
        assert originals and all(digest(app / path) == value for path, value in originals.items())
        smoke = output / ('native-smoke.json' if mac else 'windows-smoke.json')
        run(app / executable, '--self-test', smoke, timeout=600)
        if mac:
            run('codesign', '--verify', '--deep', '--strict', app / BUNDLE)

    report = json.loads(smoke.read_text(encoding='utf-8'))
    assert report['status'] == 'passed' and report['mixed_model_bundled'] == (not mac)
    assert report['gui_worker']['actual_start_button_and_export']
    assert report['model_names_separate'] and report['depth_model_metadata']
    checks = report['model_checks']
    assert len(checks) == 1 and checks[0]['model'] == 'IGEV++ Middlebury' and checks[0]['status'] == 'passed'
    assert all(item['status'] == 'passed' for item in report['formats'])
    print(f'Verified {name} {digest(archive)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'package'))
    parser.add_argument('platform', choices=TARGETS)
    args = parser.parse_args()
    system, arch, executable = TARGETS[args.platform]
    assert (platform.system(), platform.machine()) == (system, arch)
    name = f'Wigglinde_1.1_{args.platform}.zip'
    mac = system == 'Darwin'
    if args.stage == 'prepare':
        download(json.loads(PLAN.read_text(encoding='utf-8')), name, mac)
    else:
        repackage(name, executable, mac)
