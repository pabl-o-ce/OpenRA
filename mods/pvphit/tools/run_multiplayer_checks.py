"""Local two-client determinism harness: one controller and one observing client.

No account, backend, public listing, or match ID. The same scripted yard runs on
both peers; only the controller receives XTest orders. Replays remain isolated.
"""
from pathlib import Path
import os,subprocess,time,shutil,socket
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'mods/pvphit/.work'
DOTNET=str(WORK/'dotnet/dotnet')
ENV=dict(os.environ,ENGINE_DIR=str(ROOT),XDG_CONFIG_HOME=str(WORK/'config'),LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='null',SDL_VIDEODRIVER='x11',LP_NUM_THREADS='2')
ENV.pop('PVPHIT_MATCH_ID',None)
processes=[]

def launch(args,tag,env=ENV):
    p=subprocess.Popen(args,cwd=ROOT,env=env,stdout=open(WORK/(tag+'.log'),'w'),stderr=subprocess.STDOUT)
    processes.append(p);return p


def support(tag):
    p=WORK/(tag+'-support');p.mkdir(exist_ok=True)
    if not (p/'Content').exists(): (p/'Content').symlink_to(WORK/'support/Content')
    (p/'settings.yaml').write_text('Player:\n\tName: '+tag+'\nGraphics:\n\tMode: Windowed\n\tWindowedSize: 1280,1000\n\tViewportDistance: Native\n\tVSync: False\n\tCapFramerate: True\n\tMaxFramerate: 30\nGame:\n\tViewportEdgeScroll: False\n\tMouseScroll: Disabled\nServer:\n\tAdvertiseOnline: False\n')
    target=p/'maps/pvphit/{DEV_VERSION}/fc6-local-yard'
    shutil.copytree(ROOT/'mods/pvphit/maps/foundry-vehicle-yard',target,dirs_exist_ok=True)
    yaml=target/'map.yaml'
    yaml.write_text(yaml.read_text().replace('Visibility: MissionSelector','Visibility: Lobby'))
    return str(p)


def inputs(display,*args):
    subprocess.run(['python3',str(Path(__file__).with_name('yard_input.py')),*args],env=dict(ENV,DISPLAY=display),check=True)


try:
    with socket.socket() as probe: probe.bind(('127.0.0.1',12437))
    server_support=support('multi-server')
    uid=subprocess.check_output([DOTNET,'bin/OpenRA.Utility.dll','pvphit','--map-hash',str(Path(server_support)/'maps/pvphit/{DEV_VERSION}/fc6-local-yard')],env=ENV,cwd=ROOT).decode().strip()
    launch([DOTNET,'bin/OpenRA.Server.dll','Engine.EngineDir='+str(ROOT),'Engine.SupportDir='+server_support,'Game.Mod=pvphit',
            'Server.Name=FC6 local verification','Server.ListenPort=12437','Server.Map='+uid,'Server.AdvertiseOnline=False',
            'Server.QueryMapRepository=False','Server.RequireAuthentication=False','Server.EnableSingleplayer=True',
            'Server.RecordReplays=True','Server.EnableSyncReports=True'],'multi-server')
    time.sleep(2)
    for i,d in enumerate((':103',':104')):
        if Path('/tmp/.X11-unix/X'+d[1:]).exists(): raise RuntimeError('Display in use')
        launch(['Xvfb',d,'-screen','0','1280x1000x24','-nolisten','tcp'],'multi-xvfb-'+str(i))
        time.sleep(1)
        launch([DOTNET,'bin/OpenRA.dll','Engine.EngineDir='+str(ROOT),'Engine.SupportDir='+support('multi-'+str(i)),
                'Game.Mod=pvphit','Launch.Connect=127.0.0.1:12437'], 'multi-'+str(i),dict(ENV,DISPLAY=d))
        time.sleep(5)
    deadline=time.monotonic()+60
    while 'multi-1 has joined' not in (WORK/'multi-server.log').read_text():
        if time.monotonic()>deadline: raise RuntimeError('Second client did not join')
        time.sleep(.2)
    time.sleep(2)
    print('Both clients joined the private yard; starting through lobby UI.',flush=True)
    for i,d in enumerate((':103',':104')):
        subprocess.run(['magick','import','-window','root',str(WORK/f'multi-lobby-{i}.png')],env=dict(ENV,DISPLAY=d),check=True)
    inputs(':104','move,842,315','click,1')
    inputs(':103','move,880,768','click,1')
    start=time.monotonic();seen=set()
    while time.monotonic()-start<900:
        texts=[(WORK/f'multi-{i}.log').read_text() for i in range(2)]
        for line in texts[0].splitlines():
            if line in seen: continue
            seen.add(line)
            if 'VEHICLE INPUT: deploy cycle' in line:
                time.sleep(.5);inputs(':103','move,640,485','click,1','down,f','up,f')
            if 'VEHICLE INPUT: withdraw cycle' in line:
                cycle=int(line.rsplit(' ',1)[1]);x=592 if cycle%2 else 688
                inputs(':103',f'move,{x},500','click,3')
            if 'VEHICLE INPUT: dock interruption' in line:
                inputs(':103','move,640,485','click,1','move,688,500','click,3')
            if 'PASSED:' in line: print(line,flush=True)
        if any(any(k in s for k in ('FAILED:', 'Fatal Lua Error:', 'Out of sync', 'Sync mismatch', 'OutOfSyncException', 'out-of-sync', 'Exception of type')) for s in texts):
            raise RuntimeError('Multiplayer validation failed; inspect peer logs')
        if all('systems suite complete' in s for s in texts):
            print('Both clients completed the yard without reported desync.',flush=True);break
        time.sleep(.2)
    else: raise RuntimeError('Multiplayer completion timeout')
finally:
    for p in reversed(processes):
        if p is processes[0] and p.poll() is None:
            # Let the server observe the last disconnect and finalize replay metadata.
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if 'Starting a new server instance' in (WORK/'multi-server.log').read_text(): break
                time.sleep(.2)
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
