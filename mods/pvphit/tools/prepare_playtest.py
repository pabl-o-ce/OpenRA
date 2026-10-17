"""Prepare an isolated local human-playtest kit, never publish or contact PvPHit.

Copies the candidate and archived baseline, labels the baseline clearly, records
current binary/content hashes, and creates empty result/feedback sheets.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    if not args.tag.replace('-', '').isalnum():
        parser.error('Use an alphanumeric tag')
    kit = MOD/'.work'/('human-playtest-'+args.tag)
    kit.mkdir()
    maps = kit/'support/maps/pvphit/{DEV_VERSION}'
    maps.mkdir(parents=True)
    shutil.copytree(MOD/'maps/pressure-station-nine', maps/'pressure-station-nine')
    baseline = maps/'pressure-station-nine-baseline'
    baseline.mkdir()
    archive = MOD/'docs/validation/environment/pressure-station-nine-baseline.oramap'
    with zipfile.ZipFile(archive) as source:
        for name in ('map.yaml', 'map.bin', 'map.png'):
            if name in source.namelist():
                (baseline/name).write_bytes(source.read(name))
    text = (baseline/'map.yaml').read_text()
    lines = [line+' [Step 3 baseline]' if line.startswith('Title:') else line for line in text.splitlines()]
    (baseline/'map.yaml').write_text('\n'.join(lines)+'\n')
    (kit/'support/settings.yaml').write_text('Server:\n\tAdvertiseOnline: False\n\tQueryMapRepository: False\n\tRequireAuthentication: False\n\tRecordReplays: True\n\tEnableSyncReports: True\n')
    header = (MOD/'docs/validation/environment/human-matches.csv').read_text().splitlines()[0]
    (kit/'human-matches.csv').write_text(header+'\n')
    with (kit/'feedback.csv').open('w') as stream:
        csv.writer(stream).writerow(['match_id','player','replay_time','category','severity','expected','observed','reproduction','artifact','fix_status'])
    with (kit/'schedule.csv').open('w') as stream:
        writer=csv.writer(stream)
        writer.writerow(['match_id','pair','map','west','east'])
        for i,(pair,map_name,west,east) in enumerate([
            ('C1','candidate','A','B'),('C1','candidate','B','A'),
            ('B1','baseline','A','B'),('B1','baseline','B','A'),
            ('C2','candidate','A','B'),('C2','candidate','B','A'),
            ('C3','candidate','B','A'),('C3','candidate','A','B')],1):
            writer.writerow([i,pair,map_name,west,east])
    files = list((ROOT/'bin').glob('OpenRA*.dll'))
    files += [p for p in MOD.rglob('*') if p.is_file() and '.work' not in p.parts and '__pycache__' not in p.parts
              and 'docs' not in p.relative_to(MOD).parts and 'art/source' not in str(p)]
    receipt = {'revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
               'working_tree': subprocess.check_output(['git','status','--short'],cwd=ROOT).decode(),
               'files': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},
               'maps': {str(p.relative_to(kit)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(maps.rglob('*')) if p.is_file()},
               'baseline_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
               'acceptance': {'technical_validation':'pending; review docs/validation/presentation-completion/README.md',
                              'presentation_listening':'pending','hardware':'pending','two_human_balance':'pending'}}
    (kit/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    shutil.copyfile(MOD/'docs/first-human-playtest.md',kit/'README.md')
    print(kit)


if __name__ == '__main__':
    main()
