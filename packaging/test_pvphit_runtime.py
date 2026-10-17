import importlib.util
import hashlib
import json
import subprocess
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('runtime', Path(__file__).with_name('pvphit_runtime.py'))
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RuntimePackageTest(unittest.TestCase):
    def test_developer_files_and_unapproved_maps_never_ship(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            for name in (*runtime.ROOT_FILES, 'art/ui/logo.png', 'audio/presentation/test.wav',
                         'maps/pressure-station-nine/map.yaml', 'maps/pressure-station-nine/map.bin',
                         'maps/pressure-station-nine/map.png', '.work/player.oraid',
                         'art/source/model.blend', 'maps/laboratory/map.yaml', 'docs/capture.mp4',
                         'audio/.private/key.json', 'tools/fixture.py'):
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name)
            target = root / 'target'
            runtime.stage(source, target)
            actual = {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()}
            self.assertEqual(actual, set(runtime.ROOT_FILES) | {
                'art/ui/logo.png', 'audio/presentation/test.wav', 'runtime-files.json',
                'maps/pressure-station-nine/map.yaml', 'maps/pressure-station-nine/map.bin',
                'maps/pressure-station-nine/map.png'})
            with self.assertRaises(ValueError):
                runtime.stage(source, target)

    def test_shared_version_stamping_updates_runtime_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'mod.yaml'
            path.write_text('Metadata:\n\tVersion: {DEV_VERSION}\n')
            runtime.write_manifest(root)
            subprocess.run(['sh', '-c', '. "$1"; set_mod_version fc-local-test "$2"',
                            'stamp-test', str(Path(__file__).with_name('functions.sh').resolve()),
                            str(path)], check=True)
            hashes = json.loads((root / 'runtime-files.json').read_text())
            self.assertEqual(hashes['mod.yaml'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertIn('fc-local-test', path.read_text())

    def test_symlinked_asset_is_rejected_before_copying(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            (source / 'art').mkdir(parents=True)
            (source / 'art/secret.png').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                list(runtime.inventory(source))


if __name__ == '__main__':
    unittest.main()
