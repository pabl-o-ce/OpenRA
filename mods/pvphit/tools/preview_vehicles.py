"""Compose vehicle review sheets from completed Blender exports (ImageMagick)."""
from pathlib import Path
import subprocess
import tempfile

MOD = Path(__file__).resolve().parents[1]
ART = MOD/'art/vehicles'


def run(*args):
    subprocess.run(list(map(str,args)),check=True)


def main():
    run('magick','montage',ART/'previews/hauler/all/004.png',ART/'previews/scout/all/004.png',
        ART/'previews/siege/all/004.png',ART/'previews/siege/deployed/004.png',
        '-background','#20272c','-tile','4x1','-geometry','400x400+8+8',MOD/'docs/vehicle-models.png')
    with tempfile.TemporaryDirectory(prefix='fc-vehicle-preview-') as temp:
        temp = Path(temp)
        samples = []
        for name,layer in (('hauler','body'),('scout','body'),('siege','body'),('siege','deployed')):
            for f in range(0,32,4):
                path = ART/'frames'/name/layer/f'{f:03d}.png'
                if name=='scout':
                    output = temp/f'scout-{f}.png'
                    run('magick',path,ART/'frames/scout/turret'/f'{f:03d}.png','-compose','over','-composite',output)
                    path = output
                samples.append(path)
        run('magick','montage',*samples,'-background','#20272c','-tile','8x','-geometry','64x64+4+4',
            MOD/'docs/vehicle-native-samples.png')
        # Before/after, preserving the established frame anchor and 0.5 scale.
        comparison = []
        for refined in (False,True):
            for name in ('hauler','scout','siege'):
                for f in (0,4,8,16):
                    output = temp/f'{refined}-{name}-{f}.png'
                    if refined:
                        run('magick',ART/'frames'/name/'body'/f'{f:03d}.png',output)
                    else:
                        run('magick',MOD/'art/roster'/name/'body.png','-crop',f'128x128+{(f%8)*128}+{(f//8)*128}','+repage',output)
                    if name=='scout':
                        turret = temp/'turret.png'
                        if refined:
                            run('magick',ART/'frames/scout/turret'/f'{f:03d}.png',turret)
                        else:
                            run('magick',MOD/'art/roster/scout/turret.png','-crop',f'128x128+{(f%8)*128}+{(f//8)*128}','+repage',turret)
                        run('magick',output,turret,'-compose','over','-composite',output)
                    comparison.append(output)
        run('magick','montage',*comparison,'-background','#20272c','-tile','12x2','-geometry','64x64+4+4',
            MOD/'docs/vehicle-facing-comparison.png')
        run('magick','montage',*[ART/'frames'/n/'wreck/004.png' for n in ('hauler','scout','siege')],
            '-background','#20272c','-tile','3x1','-geometry','128x128+8+8',MOD/'docs/vehicle-wrecks.png')


if __name__=='__main__': main()
