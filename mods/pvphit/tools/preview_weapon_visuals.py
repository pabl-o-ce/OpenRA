"""Native-scale effect strips with the engine sequence durations (no gameplay simulation)."""
from pathlib import Path
import subprocess
import tempfile

MOD = Path(__file__).resolve().parents[1]
ART = MOD / 'art/motion-effects/frames'
FONT = subprocess.check_output(['fc-match', 'sans', '-f', '%{file}']).decode()


def run(*args):
    subprocess.run(list(map(str, args)), check=True)


with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary)
    frames = []
    for tick in range(60):
        tiles = []
        for name in ('scout', 'tank', 'siege'):
            for effect, index in [('muzzle', min(tick // 2, 5)),
                                  ('shot', 16), ('impact', min(tick // 3, 9))]:
                source = ART / (name + '-' + effect) / f'{index:03d}.png'
                tile = work / f'{name}-{effect}.png'
                run('magick', source, '-resize', '64x64', '-background', '#20272c',
                    '-alpha', 'remove', '-alpha', 'off', '-gravity', 'south',
                    '-splice', '0x18', '-fill', '#dddddd', '-font', FONT,
                    '-pointsize', '10', '-annotate', '+0+2', name + ' ' + effect, tile)
                tiles.append(tile)
        frame = work / f'weapons-{tick:02d}.png'
        run('magick', 'montage', *tiles, '-tile', '3x', '-geometry', '+0+0', frame)
        frames.append(frame)
    run('magick', '-delay', '2', *frames, '-loop', '0', MOD / 'docs/vehicle-weapon-effects.gif')
    frames = []
    for tick in range(15):
        tiles = []
        for name in ('scout', 'hauler', 'tank', 'siege'):
            source = ART / (name + '-death') / f'{min(tick, 11):03d}.png'
            tile = work / (name + '.png')
            run('magick', source, '-resize', '64x64', '-background', '#20272c',
                '-alpha', 'remove', '-alpha', 'off', '-gravity', 'south',
                '-splice', '0x18', '-fill', '#dddddd', '-font', FONT,
                '-pointsize', '10', '-annotate', '+0+2', name, tile)
            tiles.append(tile)
        frame = work / f'deaths-{tick:02d}.png'
        run('magick', 'montage', *tiles, '-tile', '4x', '-geometry', '+0+0', frame)
        frames.append(frame)
    run('magick', '-delay', '8', *frames, '-loop', '0', MOD / 'docs/vehicle-death-effects.gif')
