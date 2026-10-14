"""Assemble rendered sprites, synthesize effects/audio, embed engine metadata.

Run from any directory: python3 mods/pvphit/tools/pack_assets.py [--dotnet PATH]
Requires ImageMagick and a built OpenRA.Utility. Never edits prototype sources.
"""
from pathlib import Path
import argparse
import math
import random
import struct
import subprocess
import wave
import zlib

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]

def png(path, width, height, pixels):
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    rows = b''.join(b'\0' + pixels[y * width * 4:(y + 1) * width * 4] for y in range(height))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
                    + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))

def effects():
    for name, size, count in [('bolt', 12, 1), ('muzzle', 24, 4), ('impact', 48, 8)]:
        pixels = bytearray()
        for y in range(size):
            for sx in range(size * count):
                frame, x = divmod(sx, size)
                t = frame / count
                radius = size * (.16 + .3 * t)
                d = math.hypot(x + .5 - size / 2, y + .5 - size / 2)
                core = max(0, 1 - d / radius)
                ring = max(0, 1 - abs(d - radius) / 2) if name == 'impact' else 0
                alpha = int(255 * min(1, core + ring * .65) * (1 - t))
                pixels.extend((int(80 + 175 * core), int(190 + 65 * core), 255, alpha))
        path = MOD / 'art/effects' / f'{name}.png'
        png(path, size * count, size, bytes(pixels))
        path.with_suffix('.yaml').write_text(f'FrameSize: {size},{size}\nFrameAmount: {count}\n')
    # Density frames for a tile of mineral slag. Deterministic original pixel art.
    pixels = bytearray(24 * 24 * 12 * 4)
    rng = random.Random(41)
    rocks = [(rng.randrange(3,21),rng.randrange(3,21),rng.randrange(2,4)) for _ in range(24)]
    for frame in range(12):
        for cx,cy,r in rocks[:2*(frame+1)]:
            for y in range(max(0,cy-r),min(24,cy+r+1)):
                for x in range(max(0,cx-r),min(24,cx+r+1)):
                    if abs(x-cx)+abs(y-cy)>r+1:continue
                    bright=135 if y<cy else 70
                    pos=(y*288+frame*24+x)*4
                    pixels[pos:pos+4]=bytes((bright+20,bright,bright-12,255))
    path=MOD/'art/effects/slag.png'
    png(path,288,24,bytes(pixels))
    path.with_suffix('.yaml').write_text('FrameSize: 24,24\nFrameAmount: 12\n')

def sound(name, duration, frequency):
    rate = 22050
    rng = random.Random(17)
    samples = bytearray()
    for i in range(int(rate * duration)):
        t = i / rate
        envelope = min(1, t / .004) * math.exp(-t * 8 / duration)
        phase = 2 * math.pi * frequency * (.16 * t + .84 * .09 * (1 - math.exp(-t / .09)))
        v = envelope * (.58 * math.sin(phase) + .22 * rng.uniform(-1, 1))
        samples.extend(struct.pack('<h', int(max(-1, min(1, v)) * 26000)))
    with wave.open(str(MOD / 'audio' / name), 'wb') as out:
        out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        out.writeframes(samples)

def flags():
    # Preserve inherited flags in their original locations; add our symbol in
    # an unused strip of a separate atlas, leaving shared RA assets untouched.
    dest = MOD / 'art/ui'
    dest.mkdir(parents=True, exist_ok=True)
    for scale, suffix in ((1, ''), (2, '-2x'), (3, '-3x')):
        source = ROOT / 'mods/ra/uibits' / f'glyphs{suffix}.png'
        path = dest / f'flags{suffix}.png'
        def rect(x1,y1,x2,y2):
            return f'rectangle {x1*scale},{y1*scale} {x2*scale},{y2*scale}'
        width, height = 1 << (256*scale-1).bit_length(), 1 << (280*scale-1).bit_length()
        subprocess.run(['magick', str(source), '-background', 'none', '-gravity', 'northwest',
                        '-extent', f'{width}x{height}', '-fill', '#30383b',
                        '-draw', rect(0,260,29,274), '-fill', '#c1b8a0',
                        '-draw', rect(5,264,8,271), '-draw', rect(12,262,15,271),
                        '-draw', rect(19,264,22,271), '-fill', '#9d4637',
                        '-draw', rect(5,272,22,273), 'PNG32:' + str(path)], check=True)

def branding():
    dest = MOD / 'art/ui'
    # A foundry stamp: three refractory uprights carried by an oxide crossbeam.
    # Draw at 3x for smooth edges, then pad each chrome image to power-of-two.
    source = dest / 'mark-source.png'
    subprocess.run(['magick', '-size', '768x768', 'xc:none',
                    '-fill', '#242c30', '-stroke', '#655f51', '-strokewidth', '9',
                    '-draw', 'polygon 108,114 660,114 660,534 576,618 192,618 108,534',
                    '-stroke', 'none', '-fill', '#c1b8a0',
                    '-draw', 'rectangle 195,246 270,492',
                    '-draw', 'rectangle 345,174 420,492',
                    '-draw', 'rectangle 495,246 570,492',
                    '-fill', '#a14936', '-draw', 'rectangle 195,516 570,558',
                    '-fill', '#68aeb4', '-draw', 'rectangle 345,198 420,210',
                    'PNG32:' + str(source)], check=True)
    for scale, suffix in ((1,''),(2,'-2x'),(3,'-3x')):
        size = 256*scale
        padded = 1 << (size-1).bit_length()
        subprocess.run(['magick', str(source), '-resize', f'{size}x{size}',
                        '-gravity', 'northwest', '-background', 'none',
                        '-extent', f'{padded}x{padded}',
                        'PNG32:' + str(dest/f'mark{suffix}.png')], check=True)
    source.unlink()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dotnet', default='dotnet')
    args = parser.parse_args()
    tank = MOD / 'art/tank'
    for layer in ('body', 'turret', 'wreck'):
        frames = [tank / layer / f'{i:02d}.png' for i in range(32)]
        if not all(p.is_file() for p in frames):
            raise SystemExit(f'Missing {layer} frames; run render_tank.py first')
        sheet = tank / f'{layer}-sheet.png'
        subprocess.run(['magick', 'montage', *map(str, frames), '-background', 'none', '-tile', '8x4',
                        '-geometry', '128x128+0+0', 'PNG32:' + str(sheet)], check=True)
        sheet.with_suffix('.yaml').write_text('FrameSize: 128,128\nFrameAmount: 32\n')
    subprocess.run(['magick', str(tank / 'assembled/04.png'), '-trim', '+repage', '-resize', '60x44',
                    '-gravity', 'center', '-background', '#20272c', '-extent', '64x48',
                    'PNG32:' + str(tank / 'icon.png')], check=True)
    effects()
    flags()
    branding()
    sound('induction.wav', .6, 700)
    sound('impact.wav', .8, 130)
    sound('scout.wav', .12, 1700)
    sound('mortar.wav', 1.1, 85)
    sound('mechanism.wav', .45, 220)
    sound('acknowledge.wav', .16, 900)
    roster_sequences = []
    for asset in sorted((MOD / 'art/roster').glob('*')):
        if not asset.is_dir():
            continue
        building = asset.name not in ('scout','hauler','siege')
        size = 256 if building else 128
        sequences = [f'fc-{asset.name}:']
        for layer in sorted(asset.iterdir()):
            if not layer.is_dir():
                continue
            if layer.name == 'icon':
                continue
            frames = sorted(layer.glob('*.png'))
            if not frames:
                continue
            expected = (5 if layer.name == 'make' else 1) if building else (160 if layer.name == 'deploy' else 32)
            if len(frames) != expected:
                raise SystemExit(f'{asset.name}/{layer.name}: expected {expected} frames, got {len(frames)}')
            sheet = asset / f'{layer.name}.png'
            subprocess.run(['magick', 'montage', *map(str, frames), '-background', 'none', '-tile', '8x',
                            '-geometry', f'{size}x{size}+0+0', 'PNG32:' + str(sheet)], check=True)
            sheet.with_suffix('.yaml').write_text(f'FrameSize: {size},{size}\nFrameAmount: {len(frames)}\n')
            seq_name = {'body':'idle', 'deploy':'make'}.get(layer.name, layer.name)
            if seq_name == 'icon':
                continue
            sequences += [f'\t{seq_name}:', f'\t\tFilename: pvphit|art/roster/{asset.name}/{layer.name}.png',
                          '\t\tScale: 0.5', '\t\tOffset: 0,' + ('-14' if building else '-7')]
            if not building:
                length = 5 if layer.name == 'deploy' else 1
                remap = [((i+16)%32)*length+j for i in range(32) for j in range(length)]
                sequences += ['\t\tFacings: 32', '\t\tUseClassicFacings: false',
                              '\t\tFrames: '+','.join(map(str,remap))]
            else:
                length = len(frames)
            if length > 1:
                sequences += [f'\t\tLength: {length}', '\t\tTick: 400']
        preview = asset / ('idle/000.png' if building else 'icon/000.png')
        # Icons use the loader's single-frame default, not sprite-sheet metadata.
        (asset / 'icon.yaml').unlink(missing_ok=True)
        subprocess.run(['magick', str(preview), '-trim', '+repage', '-resize', '60x44',
                        '-gravity', 'center', '-background', '#20272c', '-extent', '64x48',
                        'PNG32:' + str(asset / 'icon.png')], check=True)
        sequences += ['\ticon:', f'\t\tFilename: pvphit|art/roster/{asset.name}/icon.png']
        if not building and asset.name != 'hauler':
            sequences += ['\tmuzzle:', '\t\tFilename: pvphit|art/effects/muzzle.png', '\t\tLength: 4', '\t\tTick: 40']
        roster_sequences.append('\n'.join(sequences))
    (MOD / 'sequences/roster.yaml').write_text('# Generated by tools/pack_assets.py\n' + '\n\n'.join(roster_sequences) + '\n')
    for path in sorted((MOD / 'art').rglob('*.png')):
        if path.with_suffix('.yaml').exists():
            subprocess.run([args.dotnet, str(ROOT / 'bin/OpenRA.Utility.dll'), 'pvphit',
                            '--png-sheet-import', str(path)], cwd=ROOT, check=True)

if __name__ == '__main__':
    main()
