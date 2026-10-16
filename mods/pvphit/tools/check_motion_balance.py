"""Compare resolved weapon simulation fields against a captured pre-polish baseline."""
from pathlib import Path
import argparse,os,subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--dotnet',default='dotnet');a=p.parse_args()
root=Path(__file__).resolve().parents[3]
env=dict(os.environ,ENGINE_DIR=str(root))
for weapon in ('FCInduction','FCScoutGun','FCMortar'):
    before=(a.baseline/('before-'+weapon+'.yaml')).read_text()
    after=subprocess.check_output([a.dotnet,str(root/'bin/OpenRA.Utility.dll'),'pvphit','--resolved-weapons',weapon],env=env,cwd=root).decode()
    def simulation(text):
        return '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('Image:')).rstrip('\n')
    if simulation(before)!=simulation(after): raise SystemExit('Non-artwork weapon change: '+weapon)
    print(weapon+': all resolved fields except artwork Image are identical')
