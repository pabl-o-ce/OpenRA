"""Original completion batch. Preserves the reviewed sample and every earlier generator.

Python standard-library synthesis; ImageMagick rasterizes original SVG branding
using the repository's FreeSans fonts. No recordings or external artwork.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import re
import struct
import subprocess
import wave

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]
RATE = 44100
PREFIX = 'pvphit|audio/presentation/'
ALERTS = {'BaseAttack': 'base-attack', 'InsufficientFunds': 'funds', 'SilosNeeded': 'storage',
          'ConstructionComplete': 'construction-complete', 'UnitReady': 'unit-ready'}


def inventory():
    entries = []
    def add(name, category, event, role='', kind='', variant=0):
        entries.append(dict(name=name, category=category, event=event, role=role, kind=kind, variant=variant))
    for role in ('scout', 'siege'):
        for kind in ('fire', 'impact'):
            for i in range(3):
                add(f'{role}-{kind}-{i+1}', 'weapon-impact', f'{role} {kind}', role, kind, i)
    for i, role in enumerate(('scout', 'tank', 'hauler', 'siege', 'building', 'building')):
        add(f'death-{role}' + (f'-{i-3}' if role == 'building' else ''), 'destruction',
            f'{role} death effect', role, 'death', i)
    for kind, count in (('deploy', 1), ('withdraw', 1), ('construction', 1), ('harvest', 2), ('transfer', 2)):
        for i in range(count):
            add(kind + (f'-{i+1}' if count > 1 else ''), 'machinery',
                {'construction': 'successful building placement', 'harvest': 'Harvested',
                 'transfer': 'own refinery accepted count > 0 and value > 0'}.get(kind, kind), '', kind, i)
    for role in ('scout', 'siege', 'hauler'):
        for kind in ('select', 'move', 'attack', 'action'):
            if role == 'hauler' and kind == 'attack':
                continue
            for i in range(2 if kind == 'select' else 1):
                add(f'{role}-{kind}' + (f'-{i+1}' if kind == 'select' else ''), 'command',
                    f'{role} {kind} order/selection', role, kind, i)
    for event, name in ALERTS.items():
        add(name, 'alert', event, '', name)
    assert len(entries) == 44
    return entries


def synth(entry):
    kind, role, variant = entry['kind'], entry['role'], entry['variant']
    seed = int.from_bytes(hashlib.sha256(entry['name'].encode()).digest()[:4], 'little')
    rng = random.Random(seed)
    tones = {
        'select': [(0, 590), (.09, 780)], 'move': [(0, 530), (.075, 900)],
        'attack': [(0, 940), (.075, 680)], 'action': [(0, 600), (.08, 600), (.16, 820)],
        'base-attack': [(0, 1040), (.12, 760), (.30, 1040), (.42, 760)],
        'funds': [(0, 520), (.18, 420)], 'storage': [(0, 430), (.11, 430), (.32, 620)],
        'construction-complete': [(0, 480), (.16, 640), (.32, 960)],
        'unit-ready': [(0, 640), (.14, 960)],
    }
    if kind in tones:
        duration = max(t for t, _ in tones[kind]) + .16
    else:
        duration = {'fire': .27 if role == 'scout' else .85,
                    'impact': .30 if role == 'scout' else .8, 'death': 1.15,
                    'deploy': .55, 'withdraw': .45, 'construction': .6,
                    'harvest': .19, 'transfer': .25}[kind]
    low = 0
    samples = []
    pitch = {'scout': 1.27, 'siege': .74, 'hauler': .88}.get(role, 1) * (1 + variant * .025)
    for i in range(round(duration * RATE)):
        t = i / RATE
        n = rng.uniform(-1, 1)
        low += .045 * (n - low)
        if kind in tones:
            v = 0
            for start, frequency in tones[kind]:
                q = t - start
                if 0 <= q < .13:
                    env = min(1, q / .006, (.13 - q) / .015) * math.exp(-q * 30)
                    v += .17 * env * (math.sin(2 * math.pi * frequency * pitch * q)
                                     + .14 * math.sin(2 * math.pi * frequency * pitch * 2 * q))
        elif kind in ('fire', 'impact', 'death'):
            freq = (180 if role == 'scout' else 65 if role in ('siege', 'building') else 95) + variant * 3
            decay = 23 if role == 'scout' else 6 if kind == 'death' else 10
            v = (.27 * math.sin(2 * math.pi * freq * t) * math.exp(-t * decay)
                 + .24 * n * math.exp(-t * (55 if kind == 'fire' else 25))
                 + .35 * low * math.exp(-t * 7))
            if kind == 'death':
                for delay in (.13, .29, .48):
                    if t >= delay:
                        v += .10 * n * math.exp(-(t-delay) * 32)
        else:
            freq = {'deploy': 210, 'withdraw': 290, 'construction': 155, 'harvest': 380, 'transfer': 260}[kind]
            v = (.12 * math.sin(2 * math.pi * (freq * t + 25 * t*t)) * math.exp(-t * 15)
                 + .18 * n * math.exp(-t * 40) + .15 * low * math.exp(-t * 12))
            if kind in ('deploy', 'withdraw', 'construction') and t > .23:
                v += .18 * n * math.exp(-(t-.23) * 45)
        samples.append(v * max(0, min(1, t/.002, (duration-t)/.025)))
    mean = sum(samples) / len(samples)
    samples = [s - mean for s in samples]
    assert max(map(abs, samples)) < .70
    return samples


def branding(root):
    art = root / 'art/ui/presentation'
    art.mkdir(parents=True, exist_ok=True)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="256" viewBox="0 0 512 256">
<rect width="512" height="256" fill="#242c30"/>
<rect width="512" height="2" fill="#9b9b8a"/><rect y="254" width="512" height="2" fill="#9b9b8a"/>
<rect x="258" y="34" width="254" height="1" fill="#626e6e"/><rect x="258" y="222" width="254" height="1" fill="#626e6e"/>
<rect x="24" y="34" width="208" height="1" fill="#626e6e"/><rect x="24" y="222" width="208" height="1" fill="#626e6e"/>
<rect x="86" y="55" width="11" height="49" fill="#9b9b8a"/><rect x="123" y="43" width="11" height="61" fill="#9b9b8a"/>
<rect x="160" y="55" width="11" height="49" fill="#9b9b8a"/><rect x="82" y="104" width="92" height="11" fill="#9b9b8a"/>
<rect x="122" y="41" width="12" height="4" fill="#7fc9ca"/>
<text x="128" y="151" text-anchor="middle" font-size="30" fill="#f2f1e7">FURNACE</text>
<text x="128" y="182" text-anchor="middle" font-size="27" fill="#f2f1e7">COVENANT</text>
<text x="128" y="207" text-anchor="middle" font-size="14" fill="#e2b76c">Prototype · PvPHit</text>
</svg>'''
    source = art / 'identity.svg'
    source.write_text(svg + '\n')
    for scale in (1, 2, 3):
        target = art / ('identity' + (f'-{scale}x' if scale > 1 else '') + '.png')
        subprocess.run(['magick', '-background', 'none', '-font', str(ROOT/'mods/common/FreeSansBold.ttf'),
                        '-density', str(96*scale), 'MSVG:'+str(source), '-resize', f'{512*scale}x{256*scale}!',
                        '-depth', '8', '-define', 'png:exclude-chunks=date,time', 'PNG32:'+str(target)], check=True)
    (root/'chrome-identity.yaml').write_text('''# Original title and loading atlas; existing logo rectangle and layout are retained.
logos:
\tImage: pvphit|art/ui/presentation/identity.png
\tImage2x: pvphit|art/ui/presentation/identity-2x.png
\tImage3x: pvphit|art/ui/presentation/identity-3x.png

loadscreen-stripe:
\tImage: pvphit|art/ui/presentation/identity.png
\tImage2x: pvphit|art/ui/presentation/identity-2x.png
\tImage3x: pvphit|art/ui/presentation/identity-3x.png
''')


def build(root):
    out = root/'audio/presentation'
    out.mkdir(parents=True, exist_ok=True)
    entries = inventory()
    for entry in entries:
        samples = synth(entry)
        path = out/(entry['name']+'.wav')
        with wave.open(str(path), 'wb') as stream:
            stream.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            stream.writeframes(struct.pack('<'+'h'*len(samples), *(round(s*32767) for s in samples)))
        entry.update(path=str(path.relative_to(root)), seconds=len(samples)/RATE,
                     peak_dbfs=round(20*math.log10(max(map(abs, samples))), 2),
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    voices = '# Generated original role commands. No hauler attack or invented tank action.\n'
    for role in ('scout', 'siege', 'hauler'):
        voices += f'Furnace{role.title()}:\n\tDefaultVariant: .wav\n\tDefaultPrefix: {PREFIX}\n\tVoices:\n'
        for kind in ('Select', 'Move', 'Attack', 'Action'):
            names = [e['name'] for e in entries if e['role'] == role and e['kind'] == kind.lower()]
            if names:
                voices += f'\t\t{kind}: ' + ', '.join(names) + '\n'
    (root/'audio/presentation.yaml').write_text(voices)
    # Freeze the explicit inherited definitions in the generated YAML, rather than changing engine defaults.
    inherited = (ROOT/'mods/ra/audio/notifications.yaml').read_text().split('\nSounds:')[0]
    names = re.findall(r'^\t\t(\w+):', inherited, re.M)
    notifications = '# Generated PvPHit-wide speech arbitration; standalone RA is unchanged.\nSpeech:\n\tNotifications:\n'
    for name in names:
        clip = ALERTS.get(name)
        path = PREFIX+clip+'.wav' if clip else 'pvphit|audio/presentation-sample/low-power.wav' if name == 'LowPower' else ''
        priority = 3 if name in ('Win', 'Lose', 'Leave', 'MissionAccomplished', 'MissionFailed') else 2 if name == 'BaseAttack' else 1 if name in ('LowPower', 'InsufficientFunds', 'SilosNeeded') else 0
        notifications += f'\t\t{name}:' + (' '+path if path else '') + '\n'
        if path:
            notifications += '\t\t\tUseFullPath: true\n'
        notifications += f'\t\t\tGroup: furnace-announcements\n\t\t\tPriority: {priority}\n'
        if priority >= 2:
            notifications += '\t\t\tInterruptLowerPriority: true\n'
    (root/'audio/notifications.yaml').write_text(notifications)
    branding(root)
    receipt = {'source': 'tools/build_presentation.py', 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'provenance': 'Original synthesis and procedural SVG; repository FreeSans font; no external samples or artwork.',
               'budget': 56, 'sample_clips_preserved': 12, 'new_clips': entries,
               'sample_only': 'k6-action is retained without a new gameplay action',
               'dependencies': {'font_sha256': hashlib.sha256((ROOT/'mods/common/FreeSansBold.ttf').read_bytes()).hexdigest(),
                                'inherited_notifications_sha256': hashlib.sha256((ROOT/'mods/ra/audio/notifications.yaml').read_bytes()).hexdigest()}}
    (out/'manifest.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(f'Built {len(entries)} completion clips, role/alert YAML and 1x/2x/3x identity in {root}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=MOD)
    build(parser.parse_args().output_root)
