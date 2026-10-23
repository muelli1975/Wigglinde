"""Build the pinned, unchanged TMIV renderer for the VWS test.

The VWS synthesis algorithm and MPEG best-reference settings are unchanged.
No codecs are built. Inputs are explicit local checkouts; this script downloads
nothing. The upstream renderer and all its transport behavior remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

TMIV_REVISION = '8faacbe722f0e2fc1dc6f8247eb2da166a0297c6'
FMT_VERSION = '11.0.2'
FMT_REVISION = '0c9fce2ffefecfdce794e1859584e25877b7b592'
LIBRARIES = ['CommonLib', 'MivBitstreamLib', 'IOLib', 'ViewingSpaceLib',
             'RendererLib', 'RendererFrontLib', 'DepthQualityAssessorLib']


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--fmt', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=Path('build/vws'))
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    args.source, args.fmt, args.build = [p.resolve() for p in
                                        (args.source, args.fmt, args.build)]
    revision = subprocess.check_output(
        ['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != TMIV_REVISION:
        raise ValueError('Incorrect TMIV revision: ' + revision)
    if subprocess.check_output(['git', '-C', str(args.source), 'diff', '--name-only'], text=True).strip():
        raise ValueError('Use an unchanged pinned TMIV source checkout.')
    fmt_revision = subprocess.check_output(
        ['git', '-C', str(args.fmt), 'rev-parse', 'HEAD'], text=True).strip()
    if fmt_revision != FMT_REVISION:
        raise ValueError('Incorrect fmt revision: ' + fmt_revision)
    args.build.mkdir(parents=True, exist_ok=True)
    fmt_install = args.build / 'fmt-install'
    run('cmake', '-S', args.fmt, '-B', args.build / 'fmt', '-DFMT_TEST=OFF',
        '-DFMT_DOC=OFF', '-DBUILD_SHARED_LIBS=OFF', '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_INSTALL_PREFIX=' + str(fmt_install))
    run('cmake', '--build', args.build / 'fmt', '--config', 'Release', '--parallel', args.jobs)
    run('cmake', '--install', args.build / 'fmt', '--config', 'Release')
    native = args.build / 'native'
    run('cmake', '-S', args.source, '-B', native, '-DBUILD_TESTING=OFF',
        '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_STANDARD=17',
        '-DTMIV_BUILD_APP_LIST=Renderer', '-DTMIV_BUILD_LIB_LIST=' + ';'.join(LIBRARIES),
        '-DCMAKE_PREFIX_PATH=' + str(fmt_install))
    run('cmake', '--build', native, '--config', 'Release', '--target', 'TmivRenderer',
        '--parallel', args.jobs)
    executable = 'TmivRenderer.exe' if sys.platform == 'win32' else 'TmivRenderer'
    binaries = list(native.rglob(executable))
    if len(binaries) != 1:
        raise ValueError('Expected exactly one built TmivRenderer.')
    output = args.build / ('wigglinde_vws.exe' if sys.platform == 'win32' else 'wigglinde_vws')
    shutil.copy2(binaries[0], output)
    report = dict(tmiv_revision=revision, fmt_version=FMT_VERSION, fmt_revision=fmt_revision,
                  executable=output.name, sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  transport_patches=[], synthesis_algorithm_modified=False,
                  geometry_bits=10, chroma='4:2:0', codecs_built=False)
    (args.build / 'provenance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
