"""Capture a completed private network regression replay from a chosen audio perspective."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

MOD=Path(__file__).resolve().parents[1]
ROOT=MOD.parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--network-run',type=Path,required=True)
    p.add_argument('--tag',required=True)
    p.add_argument('--perspective',choices=('world','player'),required=True)
    p.add_argument('--display',default=':133')
    p.add_argument('--seconds',type=int,default=300)
    a=p.parse_args()
    if not a.tag.replace('-','').isalnum():p.error('Use an alphanumeric tag')
    original=a.network_run.resolve()
    expected=json.loads((original/'checks.json').read_text())
    work=MOD/'.work'/('presentation-replay-'+a.tag);work.mkdir()
    support=work/'support';support.mkdir()
    shutil.copytree(original/'replay/maps',support/'maps')
    (support/'Content').symlink_to(MOD/'.work/support/Content')
    shutil.copyfile(original/'replay/settings.yaml',support/'settings.yaml')
    config=work/'audio.conf'
    config.write_text('[general]\nchannels = stereo\nsample-type = int16\nfrequency = 44100\n[wave]\nfile = '+str(work/'engine.wav')+'\n')
    env=dict(os.environ,DISPLAY=a.display,LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='wave',ALSOFT_CONF=str(config),SDL_VIDEODRIVER='x11',LP_NUM_THREADS='2')
    env.pop('PVPHIT_MATCH_ID',None)
    processes=[];handles=[]
    def launch(command,name):
        handle=(work/(name+'.log')).open('w');handles.append(handle)
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT);processes.append(proc)
        return proc
    try:
        if Path('/tmp/.X11-unix/X'+a.display[1:]).exists():raise RuntimeError('Display occupied')
        launch(['Xvfb',a.display,'-screen','0','1280x1000x24','-nolisten','tcp'],'display')
        time.sleep(1)
        game=launch([str(MOD/'.work/dotnet/dotnet'),'bin/OpenRA.dll','Engine.EngineDir='+str(ROOT),'Engine.SupportDir='+str(support),
            'Game.Mod=pvphit','Game.FetchNews=False','Debug.CheckVersion=False','Debug.SendSystemInformation=False',
            'Launch.Replay='+str(original/expected['replay'])],'game')
        selected=False
        deadline=time.monotonic()+a.seconds
        while time.monotonic()<deadline:
            log=(work/'game.log').read_text()
            if game.poll() is not None or any(s in log for s in ('FAILED:', 'Fatal Lua Error', 'Out of sync','Exception of type')):
                raise RuntimeError(log[-2000:])
            if 'NETWORK INPUT deploy' in log and not selected:
                if a.perspective=='world':
                    commands=['down,equal','up,equal']
                else:
                    commands=['move,1248,284','click,1']
                subprocess.run(['python3',str(MOD/'tools/yard_input.py'),*commands],env=env,check=True,stdout=subprocess.DEVNULL)
                if a.perspective=='player':
                    time.sleep(.3)
                    subprocess.run(['magick','import','-window','root',str(work/'perspective-menu.png')],env=env,check=True)
                    subprocess.run(['python3',str(MOD/'tools/yard_input.py'),'move,1130,402','click,1'],env=env,check=True,stdout=subprocess.DEVNULL)
                time.sleep(.5)
                subprocess.run(['magick','import','-window','root',str(work/'perspective.png')],env=env,check=True)
                selected=True
            if 'NETWORK suite complete' in log:
                outcome=[line for line in log.splitlines() if 'NETWORK RESULT' in line][-1]
                assert selected and outcome==expected['replay_result'],outcome
                subprocess.run(['magick','import','-window','root',str(work/'complete.png')],env=env,check=True)
                (work/'checks.json').write_text(json.dumps({'perspective':a.perspective,'result':outcome},indent=2)+'\n')
                break
            time.sleep(.2)
        else:raise RuntimeError('Replay did not finish')
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
        for handle in handles:handle.close()
    subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(work/'engine.wav'),'-c:a','pcm_s16le',str(work/'review.wav')],check=True)
    print(work)


if __name__=='__main__':main()
