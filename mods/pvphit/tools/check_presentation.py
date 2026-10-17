"""Check completion exports, inventory, frozen gameplay/source files and speech coverage.

Does not certify listening quality, hardware accessibility or human balance.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from check_presentation_sample import measure
from build_presentation import MOD, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    manifest = json.loads((MOD/'audio/presentation/manifest.json').read_text())
    result = {'baseline': '300a7643ec', 'clips': {}, 'limits': 'Technical checks only; human acceptance pending.'}
    counts = Counter(e['category'] for e in manifest['new_clips'])
    counts.update({'weapon-impact': 6, 'command': 5, 'alert': 1})
    assert dict(counts) == {'weapon-impact': 18, 'destruction': 6, 'machinery': 7, 'command': 19, 'alert': 6}
    result['inventory'] = dict(counts)
    for entry in manifest['new_clips']:
        path = MOD/entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
        stats = measure(path)
        assert stats['channels'] == 1 and stats['rate'] == 44100 and stats['peak_dbfs'] < -3
        assert stats['clipped_samples'] == 0
        result['clips'][entry['name']] = stats
    with tempfile.TemporaryDirectory(prefix='furnace-completion-') as tmp:
        subprocess.run(['python3', str(MOD/'tools/build_presentation.py'), '--output-root', tmp], check=True)
        for path in Path(tmp).rglob('*'):
            if path.is_file():
                assert path.read_bytes() == (MOD/path.relative_to(tmp)).read_bytes(), path
    result['reproduction'] = 'Byte-identical WAV, SVG, PNG, YAML and manifest'
    protected = ['mods/ra', 'mods/pvphit/art/source', 'mods/pvphit/art/environment',
                 'mods/pvphit/sequences', 'mods/pvphit/maps', 'mods/pvphit/rules', 'mods/pvphit/weapons',
                 'mods/pvphit/audio/presentation-sample', 'mods/pvphit/art/ui/presentation-sample']
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '300a7643ec', '--', *protected], cwd=ROOT).decode().splitlines()
    for name in names:
        before = subprocess.check_output(['git', 'show', '300a7643ec:'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes() == before, name
    result['preserved_baseline_files'] = len(names)
    inherited = (ROOT/'mods/ra/audio/notifications.yaml').read_text().split('\nSounds:')[0]
    names = re.findall(r'^\t\t(\w+):', inherited, re.M)
    overrides = (MOD/'audio/notifications.yaml').read_text()
    for name in names:
        block = re.search(r'^\t\t'+name+r':[^\n]*\n((?:\t\t\t[^\n]*\n)*)', overrides, re.M)
        assert block and '\t\t\tGroup: furnace-announcements\n' in block[1], name
    result['grouped_speech_definitions'] = len(names)
    layout = (MOD/'chrome/ingame-player.yaml').read_text().split('\n', 1)[1]
    layout = '\n'.join(line for line in layout.split('\n') if 'CompactDisplay:' not in line)
    assert layout == (ROOT/'mods/ra/chrome/ingame-player.yaml').read_text()
    result['player_layout'] = 'Control geometry identical; compact counters explicitly opt in'
    # Original three weapon baselines include simulation values, not just handpicked statistics.
    env = dict(os.environ, ENGINE_DIR=str(ROOT), XDG_CONFIG_HOME=str(MOD/'.work/config'))
    result['weapons'] = {}
    for weapon in ('FCInduction', 'FCScoutGun', 'FCMortar'):
        before = (MOD/'docs/validation/motion'/('before-'+weapon+'.yaml')).read_text()
        after = subprocess.check_output([str(MOD/'.work/dotnet/dotnet'), str(ROOT/'bin/OpenRA.Utility.dll'),
                                         'pvphit', '--resolved-weapons', weapon], cwd=ROOT, env=env).decode()
        normalize = lambda text: '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith(
            ('Image:', 'Report:', 'ImpactSounds:', 'ImpactSoundRequiresVisibility:'))).strip()
        assert normalize(before) == normalize(after), weapon
        result['weapons'][weapon] = 'Simulation fields unchanged'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'clips'}, indent=2))


if __name__ == '__main__':
    main()
