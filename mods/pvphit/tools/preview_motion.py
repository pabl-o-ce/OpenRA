"""Reproduce native-size directional motion boards and working-state previews."""
from pathlib import Path
import subprocess,tempfile
MOD=Path(__file__).resolve().parents[1]
ART=MOD/'art/motion/frames'
DOCS=MOD/'docs'

def run(*args):subprocess.run(list(map(str,args)),check=True)

with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp);boards=[]
    for k in range(4):
        grids=[]
        for n in ('hauler','scout','tank','siege'):
            tiles=[]
            for f in range(32):
                body=ART/n/'move'/f'{f*4+k:03d}.png';tile=t/f'{n}-{f}-{k}.png'
                if n in ('scout','tank'):
                    turret=t/f'{n}-turret-{f}.png'
                    if n=='scout':
                        run('magick',MOD/'art/vehicles/scout/turret.png','-crop',f'128x128+{f%8*128}+{f//8*128}','+repage',turret)
                    else: turret=ART/'tank/turret'/f'{f:03d}.png'
                    run('magick',body,turret,'-compose','over','-composite',tile)
                else: run('magick',body,tile)
                tiles.append(tile)
            grid=t/f'{n}-{k}-grid.png'
            run('magick','montage',*tiles,'-background','#20272c','-tile','8x','-geometry','64x64+0+0',grid)
            grids.append(grid)
        board=t/f'board-{k}.png'
        run('magick','montage',*grids,'-tile','2x2','-geometry','+0+0',board);boards.append(board)
    run('magick','-delay','8',*boards,'-loop','0',DOCS/'vehicle-movement.gif')
    run('magick',boards[0],DOCS/'vehicle-motion-directions.png')
    frames=[]
    for k in range(20):
        paths=[ART/'hauler'/l/f'{f*4+(k%4):03d}.png' for l in ('harvest','unload') for f in (0,4,8,12,16,20,24,28)]
        paths += [ART/'siege/fire'/f'{f*5+(k%5):03d}.png' for f in (0,4,8,12,16,20,24,28)]
        frame=t/f'work-{k}.png'
        run('magick','montage',*paths,'-background','#20272c','-tile','8x','-geometry','64x64+0+0',frame);frames.append(frame)
    run('magick','-delay','8',*frames,'-loop','0',DOCS/'vehicle-working.gif')

    wrecks=[ART/'tank/wreck'/f'{f:03d}.png' for f in range(32)]
    run('magick','montage',*wrecks,'-background','#20272c','-tile','8x',
        '-geometry','64x64+0+0',DOCS/'tank-motion-wrecks.png')
    tiles=[]
    for hull in (0,8,16,24):
        for turret in range(0,32,4):
            tile=t/f'aim-{hull}-{turret}.png'
            run('magick',ART/'tank/body'/f'{hull:03d}.png',
                ART/'tank/turret'/f'{turret:03d}.png','-compose','over','-composite',tile)
            tiles.append(tile)
    run('magick','montage',*tiles,'-background','#20272c','-tile','8x',
        '-geometry','64x64+0+0',DOCS/'tank-independent-aim.png')
