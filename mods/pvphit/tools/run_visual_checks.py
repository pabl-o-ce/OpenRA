"""Run local visual laboratories with isolated settings, display and real deploy input."""
import os, subprocess, time, shutil, argparse, json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
work=root/'mods/pvphit/.work'
work.mkdir(exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--map',default='foundry-vehicle-yard')
parser.add_argument('--seconds',type=int,default=600)
parser.add_argument('--tag',default='step3')
parser.add_argument('--replay',type=Path)
parser.add_argument('--extra-map',type=Path)
parser.add_argument('--dotnet',default=str(work/'dotnet/dotnet'))
parser.add_argument('--content',default=str(work/'support/Content'))
parser.add_argument('--display',default=':98')
parser.add_argument('--engine-dir',type=Path,help='Extracted self-contained candidate; laboratories are copied only into test support')
parser.add_argument('--binaries',type=Path,default=root/'bin',help='Recorded build directory for baseline comparisons')
a=parser.parse_args()
root=Path(__file__).resolve().parents[3]
engine_root=a.engine_dir.resolve() if a.engine_dir else root
version=(engine_root/'VERSION').read_text().strip()
tag=a.tag+'-'+a.map.removeprefix('foundry-')
support=work/(tag+'-support')
support.mkdir(exist_ok=False)
if a.engine_dir or a.extra_map:
    maps=support/'maps/pvphit'/version;maps.mkdir(parents=True,exist_ok=True)
if a.engine_dir:
    shutil.copytree(root/'mods/pvphit/maps'/a.map,maps/a.map)
    if a.map == 'foundry-systems-lab':
        # This laboratory references another development map's script. Keep
        # those fixtures out of distribution; mount the identical bytes locally.
        yaml=maps/a.map/'map.yaml'
        reference='pvphit|maps/tank-proving-ground/systems.lua'
        text=yaml.read_text()
        if text.count(reference)!=1: raise RuntimeError('Unexpected systems fixture script reference')
        yaml.write_text(text.replace(reference,'systems.lua'))
        shutil.copyfile(root/'mods/pvphit/maps/tank-proving-ground/systems.lua',maps/a.map/'systems.lua')
if a.extra_map:
    if a.extra_map.is_dir(): shutil.copytree(a.extra_map,maps/a.extra_map.name,dirs_exist_ok=True)
    else: shutil.copyfile(a.extra_map,maps/a.extra_map.name)
if not (support/'Content').exists(): (support/'Content').symlink_to(a.content)
(support/'settings.yaml').write_text('Player:\n\tName: Vehicle-Review\nGame:\n\tViewportEdgeScroll: False\n\tMouseScroll: Disabled\nSound:\n\tMusicVolume: 0\nGraphics:\n\tMode: Windowed\n\tVSync: False\n\tWindowedSize: 1280,1000\n\tViewportDistance: Native\nServer:\n\tAdvertiseOnline: False\n')
log=work/(tag+'.log')
env=dict(os.environ,DISPLAY=a.display,LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='null',SDL_VIDEODRIVER='x11',LP_NUM_THREADS='2')
env.pop('PVPHIT_MATCH_ID',None)
processes=[]
try:
    if Path('/tmp/.X11-unix/X'+a.display[1:]).exists(): raise RuntimeError('Display already exists; refusing to use it')
    processes.append(subprocess.Popen(['Xvfb',a.display,'-screen','0','1280x1000x24','-nolisten','tcp'],stdout=open(work/(tag+'-xvfb.log'),'w'),stderr=subprocess.STDOUT))
    for _ in range(50):
        if processes[0].poll() is not None: raise RuntimeError('Xvfb failed; use an unused isolated display')
        if Path('/tmp/.X11-unix/X'+a.display[1:]).exists():break
        time.sleep(.1)
    executable=[str(engine_root/'OpenRA')] if a.engine_dir else [a.dotnet,str(a.binaries.resolve()/'OpenRA.dll')]
    processes.append(subprocess.Popen(executable+[
        'Engine.EngineDir='+str(engine_root),'Engine.SupportDir='+str(support),
        'Game.Mod=pvphit',('Launch.Replay='+str(a.replay.resolve()) if a.replay else 'Launch.Map='+a.map),'Graphics.WindowedSize=1280,1000',
        'Graphics.ViewportDistance=Native','Graphics.CapFramerate=True','Graphics.MaxFramerate=30'],cwd=root,env=env,stdout=open(log,'w'),stderr=subprocess.STDOUT))
    processes.append(subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','x11grab','-framerate','15',
        '-video_size','1280x1000','-i',a.display,'-t',str(a.seconds),'-c:v','libx264','-preset','ultrafast','-crf','20',
        str(work/(tag+'.mkv'))],env=env,stdout=subprocess.DEVNULL,stderr=open(work/(tag+'-record.log'),'w')))
    print('Started '+a.map+' on '+a.display,flush=True)
    start=time.monotonic();seen=set();snapshots=set()
    events=work/(tag+'.events.jsonl');events.write_text('')
    while time.monotonic()-start<a.seconds:
        text=log.read_text()
        for line in text.splitlines():
            if any(s in line for s in ('YARD','FURNACE CHECK','VEHICLE','Exception')) and line not in seen:
                seen.add(line)
                if 'VEHICLE ECONOMY:' not in line:
                    with events.open('a') as out: out.write(json.dumps({'seconds':round(time.monotonic()-start,3),'message':line})+'\n')
                if 'VEHICLE ECONOMY:' not in line: print(line,flush=True)
                if not a.replay and 'VEHICLE INPUT: deploy cycle' in line:
                    # The script centers the camera on the produced carrier.
                    time.sleep(.5)
                    subprocess.run(['python3',str(Path(__file__).with_name('yard_input.py')),
                        'move,640,485','click,1','down,f','up,f'],env=env,check=True)
                if not a.replay and 'VEHICLE INPUT: withdraw cycle' in line:
                    cycle=int(line.rsplit(' ',1)[1])
                    x=592 if cycle%2 else 688
                    subprocess.run(['python3',str(Path(__file__).with_name('yard_input.py')),
                        f'move,{x},500','click,3'],env=env,check=True)
                if not a.replay and 'VEHICLE INPUT: dock interruption' in line:
                    subprocess.run(['python3',str(Path(__file__).with_name('yard_input.py')),
                        'move,640,485','click,1','move,688,500','click,3'],env=env,check=True)
        elapsed=time.monotonic()-start
        for second in (20,40,60,120,155,160,165,170,175,180,185,190,200,310,315,320,325,330,335,340,345,350):
            if elapsed>=second and second not in snapshots:
                subprocess.run(['magick','import','-window','root',str(work/f'{tag}-{second}.png')],env=env,check=True)
                snapshots.add(second)
        if any(s in text for s in ('FAILED:', 'Fatal Lua Error:', 'Exception of type')) or processes[1].poll() is not None:
            raise RuntimeError('Game failed: '+text[-4000:])
        if 'suite complete' in text: break
        time.sleep(.2)
    if 'suite complete' not in log.read_text(): raise RuntimeError('No suite completion before timeout')
finally:
    for p in reversed(processes):
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
