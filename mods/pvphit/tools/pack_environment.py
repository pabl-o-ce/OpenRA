"""Validate saved environment exports and emit map-scoped sequences and actors."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from environment_ground import MOD

ASSETS = ('wall-a','wall-b','wall-c','wall-d','pipe-ew','pipe-ns','pipe-elbow',
          'pipe-end','extraction-skid','broken-manifold')


def main():
    manifest={'frame_size':[128,128],'scale':0.5,'offset':[0,-7],
              'camera_scale':4.9,'samples':24,'seed':0,'assets':{},'scripts':{}}
    for name in ASSETS:
        image=MOD/'art/environment/props'/f'{name}.png'
        receipt=json.loads(image.with_suffix('.json').read_text())
        source=MOD/'art/source/environment'/f'{name}.blend'
        assert hashlib.sha256(image.read_bytes()).hexdigest()==receipt['png_sha256']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['source_sha256']
        assert subprocess.check_output(['magick','identify','-format','%wx%h',str(image)],text=True)=='128x128'
        bounds=subprocess.check_output(['magick',str(image),'-alpha','extract','-format','%@','info:'],text=True)
        w,h,x,y=map(int,re.fullmatch(r'(\d+)x(\d+)\+(\d+)\+(\d+)',bounds).groups())
        assert w and h and x>0 and y>0 and x+w<128 and y+h<128, (name,bounds)
        manifest['assets'][name]={**receipt,'alpha_bounds':[w,h,x,y]}
    for name in ('environment_visuals.py','refine_visuals.py','pack_environment.py'):
        manifest['scripts'][name]=hashlib.sha256((MOD/'tools'/name).read_bytes()).hexdigest()
    rules=['# Environment-only actors. No cover, projectile blocking or resource behavior.\n',
           '^FCENVPROP:\n\tInherits: ^SpriteActor\n\tImmobile:\n\t\tOccupiesSpace: false\n'
           '\tWithSpriteBody:\n\tHiddenUnderShroud:\n\t\tType: CenterPosition\n'
           '\tRenderSprites:\n\t\tPalette: player\n\tMapEditorData:\n\t\tCategories: Decoration\n']
    sequences=['# Single-frame RGBA props; ground belongs to the terrain layer.\n']
    for name in ASSETS:
        text=f'FC.ENV.{name.upper()}:\n\tInherits: ^FCENVPROP\n'
        if name.startswith('wall'):
            text+='\tImmobile:\n\t\tOccupiesSpace: true\n'
        text+=f'\tRenderSprites:\n\t\tImage: fc-env-{name}\n'
        rules.append(text)
        sequences.append(f'fc-env-{name}:\n\tidle:\n\t\tFilename: pvphit|art/environment/props/{name}.png\n'
                         '\t\tScale: 0.5\n\t\tOffset: 0,-7\n')
    (MOD/'rules/environment.yaml').write_text('\n'.join(rules))
    (MOD/'sequences/environment.yaml').write_text('\n'.join(sequences))
    (MOD/'art/environment/props/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__': main()
