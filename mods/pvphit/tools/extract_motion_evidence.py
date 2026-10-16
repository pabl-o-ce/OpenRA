"""Extract native-scale gameplay evidence from run_visual_checks recordings."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess

MOD = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tag', default='motion-replay-vehicle-yard')
args = parser.parse_args()
base = MOD / '.work' / args.tag
events = [json.loads(line) for line in base.with_suffix('.events.jsonl').read_text().splitlines()]
video = base.with_suffix('.mkv')
docs = MOD / 'docs'


def event(message):
    return next(e['seconds'] for e in events if e['message'].endswith(message))


def clip(name, start, duration, crop):
    # Crops retain the native game's pixels; no enlargement or zoom change.
    filters = (f'fps=12,crop={crop},split[a][b];'
               '[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start),
                    '-i', str(video), '-t', str(duration), '-filter_complex', filters,
                    '-loop', '0', str(docs / name)], check=True)


shutil.copyfile(Path(str(base) + '-20.png'), docs / 'vehicle-motion-yard.png')
clip('vehicle-fire-withdrawal.gif', event('VEHICLE INPUT: withdraw cycle 1') - 2,
     7, '448:352:432:320')
clip('vehicle-destruction-in-game.gif', event('VEHICLE INPUT: deploy cycle 7'),
     3, '448:448:432:300')
clip('hauler-docking-in-game.gif', event('VEHICLE INPUT: dock interruption'),
     6, '384:288:448:352')
