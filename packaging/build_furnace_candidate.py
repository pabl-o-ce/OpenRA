#!/usr/bin/env python3
"""Build a local Linux candidate from a recorded commit, without publishing it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
from urllib.parse import urlsplit

from pvphit_runtime import stage, write_manifest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd, log):
    with log.open('a') as output:
        subprocess.run(args, cwd=cwd, stdout=output, stderr=subprocess.STDOUT, check=True)


def build(args):
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ['git', 'rev-parse', '--verify', args.revision + '^{commit}'], cwd=root, text=True).strip()
    if not re.fullmatch(r'fc-local-[A-Za-z0-9._-]+', args.candidate):
        raise ValueError('Use an explicitly local fc-local-* candidate identifier')
    identity = urlsplit(args.identity_base_url)
    if (identity.scheme != 'https' or not identity.hostname or
            not identity.hostname.endswith('.test') or identity.username or
            identity.password or identity.query or identity.fragment or
            not identity.path.endswith('/api/openra/')):
        raise ValueError('Private candidates require an HTTPS .test identity URL ending /api/openra/')
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    source = destination / 'source'
    source.mkdir()
    archive = destination / 'source.tar'
    shutil.copyfile(__file__, destination / 'build_furnace_candidate.py')
    shutil.copyfile(Path(__file__).with_name('pvphit_runtime.py'), destination / 'pvphit_runtime.py')
    with archive.open('wb') as output:
        subprocess.run(['git', 'archive', revision], cwd=root, stdout=output, check=True)
    with tarfile.open(archive) as source_tar:
        source_tar.extractall(source, filter='data')
    build_dir = destination / 'build'
    build_dir.mkdir()
    # Select a recorded installed SDK without changing the source revision's pin.
    (build_dir / 'global.json').write_text(json.dumps({'sdk': {'version': args.sdk, 'rollForward': 'disable'}}))
    package = destination / args.candidate
    package.mkdir()
    log = destination / 'build.log'
    dotnet = str(args.dotnet.resolve())
    run([dotnet, '--info'], build_dir, log)
    run([dotnet, 'publish', str(source / 'OpenRA.sln'), '-c', 'Release', '-m:1',
         '-p:UseSharedCompilation=false', '-p:TargetPlatform=linux-x64', '-r', 'linux-x64',
         '--self-contained', 'true', '-p:CopyD2kDll=False', '-p:PublishDir=' + str(package) + '/'], build_dir, log)
    for name in ('VERSION', 'AUTHORS', 'COPYING', 'global mix database.dat'):
        shutil.copyfile(source / name, package / name)
    for name in ('glsl', 'mods/common', 'mods/common-content', 'mods/ra', 'mods/ra-content', 'mods/pvphit-content'):
        shutil.copytree(source / name, package / name)
    stage(source / 'mods/pvphit', package / 'mods/pvphit')
    (package / 'VERSION').write_text(args.candidate + '\n')
    for mod in ('pvphit', 'pvphit-content', 'ra', 'ra-content'):
        path = package / 'mods' / mod / 'mod.yaml'
        path.write_text(path.read_text().replace('{DEV_VERSION}', args.candidate))
    mod_yaml = package / 'mods/pvphit/mod.yaml'
    text = mod_yaml.read_text()
    for field, suffix in (('Profile', 'info/'), ('Link', 'link'), ('Unlink', 'unlink')):
        text, count = re.subn(r'^\t' + field + r': .*$', '\t' + field + ': ' + args.identity_base_url + suffix,
                             text, flags=re.MULTILINE)
        if count != 1:
            raise ValueError('Unexpected identity manifest: ' + field)
    text = re.sub(r'^\tForum: .*$', '\tForum: ' + identity.scheme + '://' + identity.netloc + '/', text, flags=re.MULTILINE)
    mod_yaml.write_text(text)
    write_manifest(package / 'mods/pvphit')
    launcher = package / 'furnace'
    launcher.write_text('''#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
program=OpenRA
if [ "${1:-}" = --server ]; then program=OpenRA.Server; shift
elif [ "${1:-}" = --utility ]; then program=OpenRA.Utility; shift
fi
if [ "$program" = OpenRA.Utility ]; then
  cd "$here"
  exec "$here/$program" pvphit "$@"
fi
exec "$here/$program" "Engine.EngineDir=$here" Game.Mod=pvphit "$@"
''')
    launcher.chmod(0o755)
    utility = package / 'OpenRA.Utility'
    map_uid = subprocess.check_output([str(utility), 'pvphit', '--map-hash',
        str(package / 'mods/pvphit/maps/pressure-station-nine')], cwd=package, text=True).strip()
    if not re.fullmatch('[0-9a-f]{40}', map_uid):
        raise ValueError('Unexpected map UID from fork utility: ' + map_uid)
    # Dependency metadata and corresponding source accompany the artifact, not player data.
    dependencies = {}
    for assets in sorted(source.glob('*/obj/project.assets.json')):
        dependencies[str(assets.relative_to(source))] = json.loads(assets.read_text())['libraries']
    (destination / 'dependencies.json').write_text(json.dumps(dependencies, indent=2) + '\n')
    manifest = {'schema': 1, 'candidate': args.candidate, 'status': 'acceptance-pending',
                'revision': revision, 'source_archive_sha256': sha(archive),
                'builder_sha256': sha(Path(__file__)), 'runtime_stager_sha256': sha(Path(__file__).with_name('pvphit_runtime.py')),
                'sdk': args.sdk, 'platform': 'linux-x64', 'self_contained': True,
                'identity_base_url': args.identity_base_url,
                'mod': 'pvphit', 'map_uid': map_uid, 'inherited_content': 'RA v2: basefiles, aftermath, cncdesert; installed separately',
                'files': {str(p.relative_to(package)): sha(p) for p in sorted(package.rglob('*')) if p.is_file()}}
    (package / 'candidate-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with tarfile.open(destination / (args.candidate + '.tar.gz'), 'w:gz') as output:
        output.add(package, arcname=args.candidate)
    artifacts = [destination / (args.candidate + '.tar.gz'), archive, destination / 'dependencies.json',
                 destination / 'build_furnace_candidate.py', destination / 'pvphit_runtime.py']
    (destination / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in artifacts))
    print(json.dumps({'artifact': str(artifacts[0]), 'map_uid': map_uid, 'status': 'acceptance-pending'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--dotnet', required=True, type=Path)
    parser.add_argument('--sdk', required=True)
    parser.add_argument('--identity-base-url', required=True)
    build(parser.parse_args())
