"""Capture a private native-scale review map, with optional fog/performance views.

Never changes the candidate or existing laboratories. Uses isolated support,
no account/match identity, no advertised server and a fresh Xvfb display.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from environment_ground import MOD


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=('full','no-props','fog','opening-west','opening-east'),default='full')
    p.add_argument('--display',default=':113')
    p.add_argument('--seconds',type=int,default=45)
    a=p.parse_args()
    opening=a.variant.startswith('opening-')
    if opening and a.seconds==45:a.seconds=220
    root=MOD.parents[1];work=MOD/'.work'/('environment-review-'+a.variant)
    support=work/'support';maps=support/'maps/pvphit/{DEV_VERSION}'
    path=maps/'environment-review';path.mkdir(parents=True,exist_ok=True)
    content=MOD/'.work/support/Content'
    if not (support/'Content').exists():(support/'Content').symlink_to(content)
    shutil.copyfile(MOD/'maps/foundry-environment-checks/map.bin',path/'map.bin')
    text=(MOD/'maps/foundry-environment-checks/map.yaml').read_text()
    if a.variant=='no-props':
        text=re.sub(r'\t\w+: fc\.env\.[\w-]+\n\t\tOwner: \w+\n\t\tLocation: \d+,\d+\n','',text)
    text=text.replace('checks.lua','review.lua')
    if a.variant=='opening-east':
        text=text.replace('Owner: Tester','Owner: Temporary').replace('Owner: Blue','Owner: Tester').replace('Owner: Temporary','Owner: Blue')
    if a.variant=='fog':
        text=text.replace('FogCheckboxEnabled: false','FogCheckboxEnabled: true')
        text=text.replace('ExploredMapCheckboxEnabled: true','ExploredMapCheckboxEnabled: false')
    (path/'map.yaml').write_text(text)
    (path/'review.lua').write_text('''WorldLoaded = function()
    local p=Player.GetPlayer("Tester")
    Camera.Position=WPos.New(48*1024,29*1024,0)
    local scout=Actor.Create("fc.scout",true,{Owner=p,Location=CPos.New(43,28)})
    local tank=Actor.Create("fc.tank",true,{Owner=p,Location=CPos.New(47,31)})
    local siege=Actor.Create("fc.siege",true,{Owner=p,Location=CPos.New(53,31)})
    Trigger.AfterDelay(1,function()
        for _,owner in ipairs({p,Player.GetPlayer("Blue")}) do
            for _,u in ipairs(owner.GetActorsByType("fc.hauler")) do u.Stop() end
        end
        print("ENVIRONMENT REVIEW READY")
    end)
end
''')
    if opening:
        east=a.variant.endswith('east')
        (path/'review.lua').write_text('''local p
local specs = {
    {"fc.generator", GX,45,16}, {"fc.processor", PX,42,40}, {"fc.factory", FX,51,52}
}
local function build(i)
    if i>3 then print("ENVIRONMENT OPENING PASSED: suite complete"); return end
    local s=specs[i]
    print("ENVIRONMENT OPENING QUEUE " .. i)
    Trigger.AfterDelay(DateTime.Seconds(s[4]),function()
        print("ENVIRONMENT OPENING PLACE " .. i)
        Trigger.AfterDelay(DateTime.Seconds(4),function()
            local units=p.GetActorsByType(s[1])
            if #units~=1 or units[1].Location~=CPos.New(s[2],s[3]) then
                FatalError("ENVIRONMENT OPENING FAILED: placement " .. s[1]);return
            end
            print("ENVIRONMENT OPENING PASSED: paid UI placement " .. s[1] .. " at " .. tostring(units[1].Location))
            build(i+1)
        end)
    end)
end
WorldLoaded=function()
    p=Player.GetPlayer("Tester")
    Camera.Position=Map.CenterOfCell(CPos.New(HX,48))
    print("ENVIRONMENT REVIEW READY")
    Trigger.AfterDelay(DateTime.Seconds(3),function() build(1) end)
end
'''.replace('GX',str(79 if east else 17)).replace('PX',str(75 if east else 20)).replace('FX',str(82 if east else 13)).replace('HX',str(83 if east else 14)))
    (support/'settings.yaml').write_text('Player:\n\tName: Environment-Review\nGame:\n\tViewportEdgeScroll: False\n'
        'Sound:\n\tMusicVolume: 0\nGraphics:\n\tMode: Windowed\n\tVSync: False\n\tWindowedSize: 1280,1000\n'
        '\tViewportDistance: Native\nServer:\n\tAdvertiseOnline: False\nDebug:\n\tPerfText: True\n')
    env=dict(os.environ,DISPLAY=a.display,LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='null',SDL_VIDEODRIVER='x11',LP_NUM_THREADS='2')
    env.pop('PVPHIT_MATCH_ID',None)
    processes=[]
    handles=[]
    try:
        socket=Path('/tmp/.X11-unix/X'+a.display[1:])
        if socket.exists():raise RuntimeError('Display occupied')
        handles.append(open(work/'xvfb.log','w'))
        display=subprocess.Popen(['Xvfb',a.display,'-screen','0','1280x1000x24','-nolisten','tcp'],stdout=handles[-1],stderr=subprocess.STDOUT)
        processes.append(display)
        for _ in range(50):
            if display.poll() is not None:raise RuntimeError('Display failed')
            if socket.exists():break
            time.sleep(.1)
        handles.append(open(work/'game.log','w'))
        game=subprocess.Popen([str(MOD/'.work/dotnet/dotnet'),'bin/OpenRA.dll','Engine.EngineDir='+str(root),
            'Engine.SupportDir='+str(support),'Game.Mod=pvphit','Launch.Map=environment-review',
            'Graphics.ViewportDistance=Native','Graphics.CapFramerate=True','Graphics.MaxFramerate=30'],
            cwd=root,env=env,stdout=handles[-1],stderr=subprocess.STDOUT)
        processes.append(game)
        start=time.monotonic();captured=set();records=[];seen=set()
        while time.monotonic()-start<a.seconds:
            if game.poll() is not None:raise RuntimeError((work/'game.log').read_text()[-3000:])
            elapsed=int(time.monotonic()-start)
            if opening:
                log=(work/'game.log').read_text()
                if 'FAILED' in log or 'Fatal Lua Error' in log:raise RuntimeError(log[-3000:])
                for action,index in re.findall(r'ENVIRONMENT OPENING (QUEUE|PLACE) (\d)',log):
                    if (action,index) in seen:continue
                    seen.add((action,index));i=int(index)-1
                    commands=[f'move,{1100+i*60},320','click,1']
                    if action=='PLACE':
                        x=([556,472,640] if a.variant.endswith('east') else [724,808,640])[i]
                        commands+=['wait,0.2',f'move,{x},{[440,380,596][i]}','wait,0.2','click,1','move,950,700']
                    subprocess.run(['python3',str(MOD/'tools/yard_input.py'),*commands],env=env,check=True,stdout=subprocess.DEVNULL)
                if 'suite complete' in log:
                    subprocess.run(['magick','import','-window','root',str(work/'complete.png')],env=env,check=True)
                    break
            if elapsed in (20,30,40) and elapsed not in captured:
                if a.variant=='fog' and elapsed==20:
                    subprocess.run(['python3',str(MOD/'tools/yard_input.py'),'move,630,550','click,1','move,950,700'],env=env,check=True,stdout=subprocess.DEVNULL)
                subprocess.run(['magick','import','-window','root',str(work/f'{elapsed}.png')],env=env,check=True)
                rss=re.search(r'VmRSS:\s+(\d+)',Path(f'/proc/{game.pid}/status').read_text())
                records.append({'seconds':elapsed,'rss_kib':int(rss[1]),'capture':f'{elapsed}.png'})
                captured.add(elapsed)
            time.sleep(.2)
        text=(work/'game.log').read_text()
        if 'ENVIRONMENT REVIEW READY' not in text or 'Fatal Lua Error' in text:raise RuntimeError(text[-3000:])
        if opening and 'suite complete' not in text:raise RuntimeError('Opening UI check timed out')
        (work/'capture.json').write_text(json.dumps({'variant':a.variant,'renderer':'Linux Xvfb llvmpipe; 30 FPS cap',
                                                    'captures':records},indent=2)+'\n')
        print(work,flush=True)
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait()
        for h in handles:h.close()


if __name__=='__main__':main()
