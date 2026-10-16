"""Check sample reproduction, PCM headroom and preserved gameplay fields.

File/measurement checks do not certify audio quality or human accessibility.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import wave

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]


def measure(path, skip_seconds=0):
    with wave.open(str(path)) as stream:
        assert stream.getsampwidth() == 2, path
        rate, channels, frames = stream.getframerate(), stream.getnchannels(), stream.getnframes()
        stream.setpos(min(frames, round(skip_seconds * rate)))
        data = stream.readframes(frames)
    samples = struct.unpack('<' + 'h' * (len(data) // 2), data)
    assert samples, path
    peak = max(map(abs, samples))
    return {'rate': rate, 'channels': channels, 'seconds': frames / rate, 'peak_sample': peak,
            'peak_dbfs': round(20 * math.log10(peak / 32768), 2) if peak else None,
            'rms_sample': round(math.sqrt(sum(v*v for v in samples) / len(samples)), 3),
            'clipped_samples': sum(abs(v) >= 32767 for v in samples)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--captures', nargs='*', default=[])
    args = parser.parse_args()
    receipt = json.loads((MOD / 'art/ui/presentation-sample/manifest.json').read_text())
    result = {'clips': {}, 'weapons': {}, 'captures': {}}
    assert len(receipt['clips']) == 12
    for name, expected in receipt['clips'].items():
        path = MOD / 'audio/presentation-sample' / (name + '.wav')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], path
        stats = measure(path)
        assert stats['channels'] == 1 and stats['rate'] == 44100
        assert stats['peak_dbfs'] < -3 and stats['clipped_samples'] == 0
        result['clips'][name] = stats
    with tempfile.TemporaryDirectory(prefix='furnace-presentation-') as tmp:
        subprocess.run(['python3', str(MOD / 'tools/build_presentation_sample.py'), '--output-root', tmp], check=True, stdout=subprocess.DEVNULL)
        for generated in Path(tmp).rglob('*'):
            if generated.is_file():
                assert generated.read_bytes() == (MOD / generated.relative_to(tmp)).read_bytes(), generated
    result['reproduction'] = 'Byte-identical fresh-root WAV/PNG/YAML/manifest exports'
    env = dict(os.environ, ENGINE_DIR=str(ROOT), XDG_CONFIG_HOME=str(MOD / '.work/config'))
    for weapon in ('FCInduction', 'FCScoutGun', 'FCMortar'):
        before = (MOD / 'docs/validation/motion' / ('before-' + weapon + '.yaml')).read_text()
        after = subprocess.check_output([str(MOD / '.work/dotnet/dotnet'), str(ROOT / 'bin/OpenRA.Utility.dll'),
                                         'pvphit', '--resolved-weapons', weapon], env=env, cwd=ROOT).decode()
        ignored = ('Image:', 'Report:', 'ImpactSounds:', 'ImpactSoundRequiresVisibility:')
        normalize = lambda text: '\n'.join(x for x in text.splitlines() if not x.lstrip().startswith(ignored)).strip()
        assert normalize(before) == normalize(after), weapon
        result['weapons'][weapon] = 'Unchanged except explicit image/audio presentation fields'
    for tag in args.captures:
        path = MOD / '.work' / ('presentation-' + tag) / 'review.wav'
        stats = measure(path, skip_seconds=8)
        assert stats['clipped_samples'] == 0, tag
        result['captures'][tag] = dict(stats, measured_after_seconds=8)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
