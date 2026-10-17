"""Capture local menu/settings/account form/replay browser and loopback connection failure.

Never enters credentials or clicks account Link/Unlink/Retry. No news fetch.
"""
import argparse
import os
from pathlib import Path
import subprocess
import time

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tag',required=True)
    p.add_argument('--display',default=':129')
    args=p.parse_args()
    if not args.tag.replace('-','').isalnum(): p.error('Use an alphanumeric tag')
    work=MOD/'.work'/('presentation-shell-'+args.tag)
    work.mkdir()
    support=work/'support'; support.mkdir()
    (support/'Content').symlink_to(MOD/'.work/support/Content')
    (support/'settings.yaml').write_text('Game:\n\tFetchNews: False\n\tIntroductionPromptVersion: 1\n\tViewportEdgeScroll: False\n'
        'Debug:\n\tCheckVersion: False\n\tSendSystemInformation: False\n\tSystemInformationVersionPrompt: 6\n'
        'Sound:\n\tMusicVolume: 0\nGraphics:\n\tMode: Windowed\n\tWindowedSize: 1280,1000\n\tVSync: False\n'
        '\tCapFramerate: True\n\tMaxFramerate: 30\nServer:\n\tAdvertiseOnline: False\n')
    env=dict(os.environ,DISPLAY=args.display,LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='null',SDL_VIDEODRIVER='x11',LP_NUM_THREADS='2')
    env.pop('PVPHIT_MATCH_ID',None)
    processes=[]; handles=[]
    def launch(command,name):
        handle=(work/(name+'.log')).open('w');handles.append(handle)
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT);processes.append(process)
        return process
    def stop(process):
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill();process.wait()
    def capture(name):
        time.sleep(1)
        subprocess.run(['magick','import','-window','root',str(work/(name+'.png'))],env=env,check=True)
    def inputs(*commands):
        subprocess.run(['python3',str(MOD/'tools/yard_input.py'),*commands],env=env,stdout=subprocess.DEVNULL,check=True)
    command=[str(MOD/'.work/dotnet/dotnet'),'bin/OpenRA.dll','Engine.EngineDir='+str(ROOT),'Engine.SupportDir='+str(support),'Game.Mod=pvphit']
    try:
        if Path('/tmp/.X11-unix/X'+args.display[1:]).exists(): raise RuntimeError('Display occupied')
        launch(['Xvfb',args.display,'-screen','0','1280x1000x24','-nolisten','tcp'],'display')
        time.sleep(1)
        game=launch(command,'shell')
        time.sleep(15)
        capture('menu')
        inputs('move,203,495','click,1')
        capture('settings-display')
        for index,name in ((1,'audio'),(3,'hotkeys'),(5,'account')):
            inputs(f'move,290,{262+35*index}','click,1')
            capture('settings-'+name)
        inputs('down,Escape','up,Escape','move,203,535','click,1','move,203,415','click,1')
        capture('replay-browser')
        stop(game)
        # Port 1 is local and unused; this is a transport-error screen, not an authenticated platform test.
        game=launch(command+['Launch.Connect=127.0.0.1:1'],'connection')
        time.sleep(15)
        capture('connection-error')
        for name in ('shell','connection'):
            if 'Exception of type' in (work/(name+'.log')).read_text(): raise RuntimeError('Screen run failed')
    finally:
        for process in reversed(processes): stop(process)
        for handle in handles: handle.close()
    print(work)


if __name__ == '__main__': main()
