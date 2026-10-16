"""Build only the step-5 review sample. No earlier asset generators are invoked.

Original deterministic synthesis and vector-like chrome; Python standard library only.
Use --output-root to reproduce into an empty staging directory before installation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import wave
import zlib

MOD = Path(__file__).resolve().parents[1]
RATE = 44100
COLORS = {'iron': '242C30', 'panel': '343E41', 'ceramic': '9B9B8A',
          'edge': '626E6E', 'cyan': '7FC9CA', 'amber': 'E2B76C'}


def audio(kind, variant=0):
    rng = random.Random(5100 + variant)
    duration = {'fire': .58, 'impact': .48, 'select': .23, 'move': .20,
                'attack': .24, 'action': .28, 'low-power': .70}[kind]
    samples = []
    low = 0.0
    for i in range(round(RATE * duration)):
        t = i / RATE
        n = rng.uniform(-1, 1)
        low += .035 * (n - low)
        # Separate transients, body and tail; never normalize a tail into a loud hiss.
        if kind == 'fire':
            v = (.34 * math.sin(2 * math.pi * ((105 + variant * 6) * t + 7 * (1 - math.exp(-t * 25)))) * math.exp(-t * 12)
                 + .20 * (n - low) * math.exp(-t * 65)
                 + .12 * math.sin(2 * math.pi * (1350 + variant * 80) * t) * math.exp(-t * 30))
        elif kind == 'impact':
            v = (.24 * n * math.exp(-t * 25) + .25 * low * math.exp(-t * 8)
                 + .18 * math.sin(2 * math.pi * (164 + variant * 17) * t) * math.exp(-t * 20))
        else:
            # One consistent command grammar; rhythm communicates the order.
            notes = {'select': [(0, 590 + variant * 70), (.09, 780 + variant * 55)],
                     'move': [(0, 530), (.075, 900)], 'attack': [(0, 940), (.075, 680)],
                     'action': [(0, 600), (.08, 600), (.16, 820)],
                     'low-power': [(0, 760), (.19, 570), (.38, 380)]}[kind]
            v = 0
            for start, frequency in notes:
                q = t - start
                if 0 <= q < .13:
                    env = min(1, q / .006) * math.exp(-q * 35) * min(1, (.13 - q) / .015)
                    v += .18 * env * (math.sin(2 * math.pi * frequency * q)
                                     + .2 * math.sin(2 * math.pi * frequency * 2 * q))
        v *= min(1, t / .002, (duration - t) / .025)
        samples.append(v)
    # Remove DC, retain mix headroom; reject instead of hard clipping.
    mean = sum(samples) / len(samples)
    samples = [s - mean for s in samples]
    peak = max(abs(s) for s in samples)
    assert peak < .71
    return samples


def png(path, scale, rects):
    width, height = 1024 * scale, 512 * scale
    pixels = bytearray(width * height * 4)
    for x, y, w, h, color in rects:
        rgba = bytes.fromhex(color) + b'\xff'
        row = rgba * (w * scale)
        for yy in range(y * scale, (y + h) * scale):
            offset = (yy * width + x * scale) * 4
            pixels[offset:offset + len(row)] = row
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    rows = b''.join(b'\0' + pixels[y * width * 4:(y + 1) * width * 4] for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def build(root):
    out = root / 'audio/presentation-sample'
    out.mkdir(parents=True, exist_ok=True)
    receipt = {'source': 'tools/build_presentation_sample.py', 'license': 'Repository licensing; no third-party inputs',
               'provenance': 'Original procedural synthesis and chrome; no samples, voices, or inherited artwork.',
               'rate': RATE, 'clips': {}}
    specs = [(f'k6-{kind}-{i+1}', kind, i) for kind in ('fire', 'impact') for i in range(3)]
    specs += [('k6-select-1', 'select', 0), ('k6-select-2', 'select', 1)]
    specs += [(f'k6-{kind}', kind, 0) for kind in ('move', 'attack', 'action')]
    specs += [('low-power', 'low-power', 0)]
    for name, kind, variant in specs:
        samples = audio(kind, variant)
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as stream:
            stream.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            stream.writeframes(struct.pack('<' + 'h' * len(samples), *(round(s * 32767) for s in samples)))
        receipt['clips'][name] = {'seconds': len(samples) / RATE,
                                  'peak_dbfs': round(20 * math.log10(max(abs(s) for s in samples)), 2),
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    rects = []
    def rect(x, y, w, h, color):
        rects.append((x, y, w, h, COLORS.get(color, color)))
    def panel(x, y, w, h, border='edge', fill='iron'):
        rect(x, y, w, h, border)
        rect(x + 1, y + 1, w - 2, h - 2, fill)
    # Regions are independently authored: they do not copy pixels from RA chrome.
    panel(0, 0, 238, 262, 'ceramic')
    rect(3, 3, 232, 33, 'panel')
    rect(4, 37, 230, 1, 'edge')
    rect(8, 3, 28, 2, 'cyan')
    panel(240, 0, 222, 222, 'edge', 'iron')
    panel(0, 264, 238, 28, 'ceramic', 'panel')
    rect(100, 270, 1, 16, 'edge')
    rect(145, 270, 1, 16, 'edge')
    panel(240, 224, 190, 47)
    # Transparent production overlay: borders must not obscure icons or progress.
    rect(0, 294, 3, 47, 'ceramic')
    rect(235, 294, 3, 47, 'ceramic')
    for x in (40, 103, 166, 229):
        rect(x, 294, 1, 47, 'edge')
    rect(40, 294, 190, 1, 'edge')
    rect(40, 340, 190, 1, 'edge')
    panel(0, 343, 238, 8, 'ceramic')
    panel(768, 0, 64, 48, 'edge')
    # Button 9-slice states, including visible press and disabled treatments.
    states = [('normal', 'edge', 'panel'), ('hover', 'cyan', '414E51'),
              ('pressed', 'cyan', '192124'), ('highlighted', 'amber', '4C4739'),
              ('highlighted-hover', 'amber', '605640'), ('highlighted-pressed', 'amber', '302C23'),
              ('disabled', '4A5355', '2B3234'), ('highlighted-disabled', '766B54', '2B3234')]
    for i, (_, border, fill) in enumerate(states):
        panel(480 + i * 32, 0, 28, 28, border, fill)
    panel(480, 40, 32, 32, 'ceramic')  # Tooltip 9-slice.
    rect(481, 41, 2, 30, 'cyan')
    panel(520, 40, 32, 32, 'amber')  # Notification 9-slice.
    panel(0, 355, 434, 44, 'ceramic')
    # Original 16px induction indicator; warning includes a contrasting frame.
    for x, color in ((560, 'cyan'), (580, 'amber')):
        for dy, left, width in ((1, 8, 4), (2, 7, 4), (3, 6, 4), (4, 5, 4), (5, 4, 8), (6, 3, 9), (7, 6, 6), (8, 6, 5), (9, 6, 4), (10, 5, 4), (11, 5, 3), (12, 4, 3), (13, 4, 2)):
            rect(x + left, 80 + dy, width, 1, color)
    rect(580, 80, 16, 1, 'amber')
    rect(580, 95, 16, 1, 'amber')
    art = root / 'art/ui/presentation-sample'
    art.mkdir(parents=True, exist_ok=True)
    for scale in (1, 2, 3):
        png(art / ('console' + (f'-{scale}x' if scale > 1 else '') + '.png'), scale, rects)
    header = ('^FurnaceConsole:\n\tImage: pvphit|art/ui/presentation-sample/console.png\n'
              '\tImage2x: pvphit|art/ui/presentation-sample/console-2x.png\n'
              '\tImage3x: pvphit|art/ui/presentation-sample/console-3x.png\n\n')
    chrome = header + 'sidebar-kiln:\n\tInherits: ^FurnaceConsole\n\tRegions:\n'
    for name, values in {'radar': (240, 0, 222, 222), 'background-top': (0, 0, 238, 262),
                         'background-moneybin': (0, 264, 238, 28), 'background-iconbg': (240, 224, 190, 47),
                         'background-supportoverlay': (768, 0, 64, 48),
                         'background-iconrow': (0, 294, 238, 47), 'background-bottom': (0, 343, 238, 8)}.items():
        chrome += f'\t\t{name}: ' + ', '.join(map(str, values)) + '\n'
    for prefix in ('sidebar-button', 'command-button'):
        for i, (state, _, _) in enumerate(states):
            suffix = '' if state == 'normal' else '-' + state
            chrome += f'\n{prefix}-kiln{suffix}:\n\tInherits: ^FurnaceConsole\n\tPanelRegion: {480+i*32}, 0, 3, 3, 22, 22, 3, 3\n'
    for name, x in (('furnace-tooltip', 480), ('furnace-notification', 520)):
        chrome += f'\n{name}:\n\tInherits: ^FurnaceConsole\n\tPanelRegion: {x}, 40, 4, 4, 24, 24, 4, 4\n'
    chrome += '\ncommandbar:\n\tImage: pvphit|art/ui/presentation-sample/console.png\n\tImage2x: pvphit|art/ui/presentation-sample/console-2x.png\n\tImage3x: pvphit|art/ui/presentation-sample/console-3x.png\n\tRegions:\n\t\tbackground: 0, 355, 434, 44\n'
    chrome += '\npower-icons:\n\tImage: pvphit|art/ui/presentation-sample/console.png\n\tImage2x: pvphit|art/ui/presentation-sample/console-2x.png\n\tImage3x: pvphit|art/ui/presentation-sample/console-3x.png\n\tRegions:\n\t\tpower-normal: 560, 80, 16, 16\n\t\tpower-critical: 580, 80, 16, 16\n'
    (root / 'chrome-presentation.yaml').write_text(chrome)
    receipt['palette'] = COLORS
    receipt['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (art / 'manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Built {len(specs)} sample clips and three chrome scales in {root}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=MOD)
    build(parser.parse_args().output_root)
