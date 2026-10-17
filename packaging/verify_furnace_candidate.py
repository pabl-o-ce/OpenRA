#!/usr/bin/env python3
"""Verify an extracted candidate, including unexpected files; support data lives elsewhere."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(root):
    manifest = json.loads((root / 'candidate-manifest.json').read_text())
    expected = manifest['files']
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if actual != set(expected) | {'candidate-manifest.json'}:
        raise ValueError('Missing or unexpected package files')
    for name, digest in expected.items():
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Unsafe package path: ' + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Checksum mismatch: ' + name)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    manifest = verify(args.package)
    print(f"Verified {manifest['candidate']} / {manifest['map_uid']} (acceptance remains separate)")
