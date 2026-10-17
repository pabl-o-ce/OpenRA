"""Private two-controller regression with per-client OpenAL recordings and replay verification.

Automated clients are not human balance matches. Each run owns a fresh directory,
displays and loopback server. No public advertisement, account or result identity.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tag', required=True)
    p.add_argument('--engine-dir', type=Path, help='Extracted self-contained candidate to verify')
    p.add_argument('--display', type=int, default=125)
    p.add_argument('--port', type=int, default=12439)
    p.add_argument('--seconds', type=int, default=400)
    args = p.parse_args()
    if not args.tag.replace('-', '').isalnum():
        p.error('Use an alphanumeric tag')
    work = MOD/'.work'/('presentation-network-'+args.tag)
    work.mkdir()
    engine_root = args.engine_dir.resolve() if args.engine_dir else ROOT
    version = (engine_root/'VERSION').read_text().strip()
    def engine(name):
        return [str(engine_root/name)] if args.engine_dir else [str(MOD/'.work/dotnet/dotnet'), 'bin/'+name+'.dll']
    env = dict(os.environ, ENGINE_DIR=str(engine_root), XDG_CONFIG_HOME=str(MOD/'.work/config'),
               LIBGL_ALWAYS_SOFTWARE='1', SDL_VIDEODRIVER='x11', LP_NUM_THREADS='2')
    env.pop('PVPHIT_MATCH_ID', None)
    processes, handles = [], []
    def launch(command, name, extra=None):
        handle = (work/(name+'.log')).open('w')
        handles.append(handle)
        process = subprocess.Popen(command, cwd=engine_root, env=dict(env, **(extra or {})), stdout=handle, stderr=subprocess.STDOUT)
        processes.append(process)
        return process
    def stop(process):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    def support(name):
        path = work/name
        target = path/('maps/pvphit/'+version+'/presentation-network')
        target.mkdir(parents=True)
        (path/'Content').symlink_to(MOD/'.work/support/Content')
        text = (MOD/'maps/foundry-environment-checks/map.yaml').read_text()
        text = text.replace('Visibility: MissionSelector', 'Visibility: Lobby').replace('checks.lua', 'network.lua')
        text = text.replace('Name: Blue\n\t\tNonCombatant: True', 'Name: Blue\n\t\tPlayable: True\n\t\tRequired: True\n\t\tAllowBots: False\n\t\tLockFaction: True')
        text = text.replace('FogCheckboxEnabled: false', 'FogCheckboxEnabled: true')
        (target/'map.yaml').write_text(text)
        shutil.copyfile(MOD/'maps/foundry-environment-checks/map.bin', target/'map.bin')
        shutil.copyfile(MOD/'tools/presentation_network.lua', target/'network.lua')
        (path/'settings.yaml').write_text('Player:\n\tName: '+name+'\nSound:\n\tMusicVolume: 0\n'
            'Graphics:\n\tMode: Windowed\n\tWindowedSize: 1280,1000\n\tViewportDistance: Native\n\tVSync: False\n'
            '\tCapFramerate: True\n\tMaxFramerate: 30\nGame:\n\tFetchNews: False\n\tViewportEdgeScroll: False\n\tMouseScroll: Disabled\n'
            'Debug:\n\tCheckVersion: False\n\tSendSystemInformation: False\n'
            'Server:\n\tAdvertiseOnline: False\n')
        return path
    def input_at(display, *commands):
        subprocess.run(['python3', str(MOD/'tools/yard_input.py'), *commands], env=dict(env, DISPLAY=display),
                       stdout=subprocess.DEVNULL, check=True)
    def screenshot(display, name):
        subprocess.run(['magick','import','-window','root',str(work/(name+'.png'))],env=dict(env,DISPLAY=display),check=True)
    result = {'engine_dir': str(engine_root), 'version': version, 'authentication': False, 'human_controllers': 0}
    try:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', args.port))
        server_support = support('server')
        uid = subprocess.check_output(engine('OpenRA.Utility')+['pvphit','--map-hash',
            str(server_support/('maps/pvphit/'+version+'/presentation-network'))],cwd=engine_root,env=env).decode().strip()
        result['map_uid'] = uid
        server = launch(engine('OpenRA.Server')+['Engine.EngineDir='+str(engine_root),'Engine.SupportDir='+str(server_support),
            'Game.Mod=pvphit','Server.ListenPort='+str(args.port),'Server.Map='+uid,'Server.AdvertiseOnline=False',
            'Server.QueryMapRepository=False','Server.RequireAuthentication=False','Server.RecordReplays=True',
            'Server.EnableSyncReports=True'], 'server', {'ALSOFT_DRIVERS':'null'})
        time.sleep(2)
        displays, clients = [], []
        for i in range(2):
            display = ':'+str(args.display+i)
            displays.append(display)
            if Path('/tmp/.X11-unix/X'+display[1:]).exists():
                raise RuntimeError('Display occupied')
            launch(['Xvfb',display,'-screen','0','1280x1000x24','-nolisten','tcp'],'display-'+str(i))
            time.sleep(1)
            path = support('client-'+str(i))
            conf = work/('audio-'+str(i)+'.conf')
            conf.write_text('[general]\nchannels = stereo\nsample-type = int16\nfrequency = 44100\n[wave]\nfile = '+str(work/('client-'+str(i)+'.wav'))+'\n')
            clients.append(launch(engine('OpenRA')+['Engine.EngineDir='+str(engine_root),'Engine.SupportDir='+str(path),
                'Game.Mod=pvphit','Launch.Connect=127.0.0.1:'+str(args.port)], 'client-'+str(i),
                {'DISPLAY':display,'ALSOFT_DRIVERS':'wave','ALSOFT_CONF':str(conf)}))
            time.sleep(6)
        deadline = time.monotonic()+60
        while 'client-1 has joined' not in (work/'server.log').read_text():
            if time.monotonic()>deadline:
                raise RuntimeError('Second client did not join')
            time.sleep(.2)
        for i,d in enumerate(displays):
            screenshot(d,'lobby-'+str(i))
        # Two playable slots: second player's ready checkbox, then host's start button.
        input_at(displays[1], 'move,842,315', 'click,1')
        input_at(displays[0], 'move,880,768', 'click,1')
        seen = set()
        start = time.monotonic()
        while time.monotonic()-start < args.seconds:
            logs = [(work/f'client-{i}.log').read_text() for i in range(2)]
            if any(c.poll() is not None for c in clients) or any(any(e in s for e in ('FAILED:', 'Fatal Lua Error', 'Out of sync', 'Sync mismatch', 'Exception of type')) for s in logs):
                raise RuntimeError('Peer failure; inspect retained logs')
            for line in logs[0].splitlines():
                if 'NETWORK' not in line or line in seen:
                    continue
                seen.add(line)
                print(line,flush=True)
                if 'INPUT deploy' in line:
                    for i,d in enumerate(displays):
                        input_at(d,f'move,{592+i*96},485','click,1','down,f','up,f')
                elif 'INPUT local mute' in line:
                    input_at(displays[1],'down,m','up,m')
                elif 'INPUT withdraw' in line:
                    for i,d in enumerate(displays):
                        input_at(d,f'move,{592+i*96},590','click,3')
            if all('NETWORK suite complete' in s for s in logs):
                outcomes = [[line for line in s.splitlines() if 'NETWORK RESULT' in line][-1] for s in logs]
                assert outcomes[0] == outcomes[1], outcomes
                result['peers'] = outcomes
                break
            time.sleep(.2)
        else:
            for i,d in enumerate(displays): screenshot(d,'timeout-'+str(i))
            raise RuntimeError('Peer scenario timeout')
        for i,d in enumerate(displays): screenshot(d,'complete-'+str(i))
        for client in clients: stop(client)
        time.sleep(3)
        stop(server)
        replay = sorted(server_support.rglob('*.orarep'))[-1]
        result['replay'] = str(replay.relative_to(work))
        # Replay commands come from the recording, never inject deployment/movement here.
        replay_support = support('replay')
        replay_process = launch(engine('OpenRA')+['Engine.EngineDir='+str(engine_root),'Engine.SupportDir='+str(replay_support),
            'Game.Mod=pvphit','Launch.Replay='+str(replay)],'replay',{'DISPLAY':displays[0],'ALSOFT_DRIVERS':'null'})
        deadline=time.monotonic()+args.seconds
        while time.monotonic()<deadline:
            log=(work/'replay.log').read_text()
            if replay_process.poll() is not None or any(e in log for e in ('FAILED:', 'Fatal Lua Error', 'Out of sync', 'Exception of type')):
                raise RuntimeError('Replay failed')
            if 'NETWORK suite complete' in log:
                outcome=[line for line in log.splitlines() if 'NETWORK RESULT' in line][-1]
                assert outcome == result['peers'][0], outcome
                result['replay_result']=outcome
                screenshot(displays[0],'replay-complete')
                break
            time.sleep(.2)
        else: raise RuntimeError('Replay timeout')
        (work/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
        print('Both controlling clients and replay completed with matching outcomes; not a human balance match.',flush=True)
    finally:
        for process in reversed(processes): stop(process)
        for handle in handles: handle.close()
    for i in range(2):
        subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(work/f'client-{i}.wav'),'-c:a','pcm_s16le',
                        str(work/f'client-{i}-final.wav')],check=True)
    print(work)


if __name__ == '__main__':
    main()
