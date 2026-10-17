#!/usr/bin/env python3
"""Stage only Furnace Covenant runtime data; never copy a developer support tree."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT_FILES = ('mod.yaml', 'chrome.yaml', 'chrome-identity.yaml',
              'chrome-presentation.yaml', 'metrics.yaml')
DIRECTORIES = {'art': {'.png', '.yaml'}, 'audio': {'.wav', '.yaml', '.json'},
               'chrome': {'.yaml'}, 'fluent': {'.ftl'}, 'rules': {'.yaml'},
               'sequences': {'.yaml'}, 'tilesets': {'.yaml'}, 'weapons': {'.yaml'}}


def inventory(source):
    for name in ROOT_FILES:
        yield source / name
    for name, extensions in DIRECTORIES.items():
        for path in sorted((source / name).rglob('*')):
            relative = path.relative_to(source)
            if 'source' in relative.parts or any(p.startswith('.') for p in relative.parts):
                continue
            if path.is_file() and path.suffix in extensions:
                if path.is_symlink():
                    raise ValueError(f'Symlink is not runtime data: {relative}')
                yield path
    for name in ('map.yaml', 'map.bin', 'map.png'):
        yield source / 'maps/pressure-station-nine' / name


def write_manifest(destination):
    hashes = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(destination.rglob('*'))
              if p.is_file() and p.name != 'runtime-files.json'}
    (destination / 'runtime-files.json').write_text(json.dumps(hashes, indent=2) + '\n')


def stage(source, destination):
    if destination.exists():
        raise ValueError('Destination must not exist; refusing to mix build contents')
    files = list(inventory(source))
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'Missing or linked runtime file: {path}')
    destination.mkdir(parents=True)
    for path in files:
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write_manifest(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--manifest-only', action='store_true', help='Rehash staged data after version stamping')
    args = parser.parse_args()
    if args.manifest_only:
        write_manifest(args.destination)
    else:
        stage(args.source, args.destination)
