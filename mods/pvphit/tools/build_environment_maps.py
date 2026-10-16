"""Generate only the selected environment map into an explicit mod-shaped root."""
from pathlib import Path
import argparse
import struct
from environment_ground import MOD, IDS

FIELDS = ((23,53,4),(74,53,4),(48,29,5),(49,68,5))
WALLS = [(x,y) for y in (36,61) for start in (37,55) for x in range(start,start+6)]


def rectangle(cells, x0,y0,x1,y1):
    cells.update((x,y) for x in range(x0,x1+1) for y in range(y0,y1+1))


def ground(size, paved, fields):
    data = bytearray(struct.pack('<BHHIII',2,size,size,17,0,17+size*size*3))
    for x in range(size):
        for y in range(size):
            kind = f'ash-{(x*7+y*11)%4}'
            if (x,y) in paved:
                outside = ''.join(d for d,dx,dy in [('n',0,-1),('e',1,0),('s',0,1),('w',-1,0)] if (x+dx,y+dy) not in paved)
                if len(outside) == 1: kind = 'edge-'+outside
                elif len(outside) == 2:
                    corner = next((c for c in ('ne','se','sw','nw') if set(c)==set(outside)),None)
                    if corner is None: raise ValueError(f'Paving too narrow at {x},{y}')
                    kind = 'outer-'+corner
                elif len(outside) > 2: raise ValueError(f'Isolated paving at {x},{y}')
                else:
                    corners = [c for c,dx,dy in [('ne',1,-1),('se',1,1),('sw',-1,1),('nw',-1,-1)] if (x+dx,y+dy) not in paved]
                    if len(corners)>1: raise ValueError(f'Ambiguous inner corner at {x},{y}')
                    kind = 'inner-'+corners[0] if corners else f'paving-{(x*3+y*7)%4}'
                    if not corners:
                        if x in (30,67): kind='drain-ns'
                        elif (x*13+y*31)%29 == 0: kind=f'damaged-{(x+y)%2}'
            data.extend(struct.pack('<HB',IDS[kind],0))
    for x in range(size):
        for y in range(size):
            data.extend((1,12) if any((x-cx)**2+(y-cy)**2<=r*r for cx,cy,r in fields) else (0,0))
    return data


def actor(name, kind, x,y, owner='Neutral', extra=''):
    return f'\t{name}: {kind}\n\t\tOwner: {owner}\n\t\tLocation: {x},{y}\n'+extra


def props():
    text = ''
    for i,(x,y) in enumerate(WALLS):
        # EW variants for horizontal wall chains; NS variants in the sample.
        text += actor(f'ServiceWall{i}', 'fc.env.wall-'+('a' if i%2==0 else 'c'),x,y)
    for i,x in enumerate(range(31,68)):
        text += actor(f'NorthPipe{i}','fc.env.pipe-ew',x,11)
        text += actor(f'SouthPipe{i}','fc.env.pipe-ew',97-x,86)
    for name,kind,x,y in [('NorthTerminal','pipe-end',68,11),('SouthTerminal','pipe-elbow',29,86),
                          ('NorthSkid','extraction-skid',41,22),('SouthSkid','extraction-skid',56,75),
                          ('Manifold','broken-manifold',66,81)]:
        text += actor(name,'fc.env.'+kind,x,y)
    return text


def battlefield(output):
    path=output/'maps/pressure-station-nine'; path.mkdir(parents=True,exist_ok=True)
    paved=set()
    for rect in [(5,36,29,65),(68,36,92,65),(5,42,92,55),
                 (29,18,36,78),(61,18,68,78),(29,14,68,32),(29,65,68,83)]:
        rectangle(paved,*rect)
    # The actual deposits remain readable over a quiet ash bed.
    for cx,cy,r in FIELDS:
        paved.difference_update((x,y) for x in range(cx-r-1,cx+r+2) for y in range(cy-r-1,cy+r+2))
    (path/'map.bin').write_bytes(ground(98,paved,FIELDS))
    original=(MOD/'docs/validation/environment/pressure-station-nine-baseline.oramap')
    import zipfile
    with zipfile.ZipFile(original) as z:
        header=z.read('map.yaml').decode().split('Actors:')[0]
    text=header+'Actors:\n'
    for name,kind,x,y in [('WestSpawn','mpspawn',14,48),('EastSpawn','mpspawn',83,48),
                         ('NorthFacility','fc.facility',48,18),('SouthFacility','fc.facility',48,78)]:
        text+=actor(name,kind,x,y)
    text+=props()
    text+='\nRules: pvphit|rules/slice.yaml, pvphit|rules/environment.yaml\n'
    text+='\nSequences: pvphit|sequences/environment.yaml\n\nFluentMessages: pvphit|fluent/slice.ftl\n'
    (path/'map.yaml').write_text(text)


def sample(output):
    path=output/'maps/foundry-environment-sample';path.mkdir(parents=True,exist_ok=True)
    paved=set()
    rectangle(paved,6,8,39,36)
    paved.difference_update((x,y) for x in range(6,16) for y in range(8,16))
    fields=((9,27,3),)
    (path/'map.bin').write_bytes(ground(48,paved,fields))
    base=(MOD/'maps/foundry-systems-lab/map.yaml').read_text()
    header=base.split('Actors:')[0].replace('Foundry Systems Lab','Environment Sample')
    text=header+'Actors:\n'
    for name,kind,x,y,owner in [('HQ','hq',17,10,'Tester'),('Generator','generator',24,10,'Tester'),
                              ('Processor','processor',13,23,'Tester'),('Factory','factory',33,11,'Tester'),
                              ('Tank','tank',22,19,'Tester'),('Scout','scout',19,26,'Tester'),
                              ('Siege','siege',26,31,'Tester'),('Facility','facility',25,24,'Neutral'),
                              ('Target','generator',33,30,'Blue')]:
        text+=actor(name,'fc.'+kind,x,y,owner)
    for i,name in enumerate(('wall-a','wall-b','wall-c','wall-d','pipe-ew','pipe-ns','pipe-elbow','pipe-end','extraction-skid','broken-manifold')):
        text+=actor(f'SampleProp{i}','fc.env.'+name,8+i*3,34)
    rules=base.split('Rules:',1)[1].replace('pvphit|rules/slice.yaml','pvphit|rules/slice.yaml, pvphit|rules/environment.yaml')
    rules=rules.replace('pvphit|maps/tank-proving-ground/systems.lua','sample.lua')
    briefing=next(line for line in rules.splitlines() if line.startswith('\t\t\tBriefing:'))
    rules=rules.replace(briefing,'\t\t\tBriefing: Inspect ash, paving transitions, slag and low props at native zoom. Capture, harvesting and paid siege production run automatically. This laboratory has no victory condition.')
    text+='\nRules:'+rules+'\nSequences: pvphit|sequences/environment.yaml\n'
    (path/'map.yaml').write_text(text)
    (path/'sample.lua').write_text('''-- Native terrain/prop inspection and smoke checks only.
local produced, departed = nil, false
WorldLoaded = function()
    Camera.Position = WPos.New(24*1024,23*1024,0)
    local p = Player.GetPlayer("Tester")
    Trigger.AfterDelay(DateTime.Seconds(3), function() Scout.Capture(Facility) end)
    Trigger.AfterDelay(DateTime.Seconds(5), function()
        p.Build({"fc.siege"}, function(units)
            produced = units[1]
            produced.Move(CPos.New(36,22))
        end)
    end)
    Trigger.AfterDelay(DateTime.Seconds(100), function()
        if not departed or Facility.Owner ~= p or Scout.IsDead or p.Resources == 0 then
            FatalError("ENVIRONMENT YARD FAILED: production/capture/harvest smoke check")
            return
        end
        print("ENVIRONMENT YARD PASSED: sample smoke suite complete")
    end)
end
Tick = function()
    if produced and produced.Location == CPos.New(36,22) then departed = true end
end
''')


def checks(output):
    """A separate laboratory using the candidate's exact terrain and blockers."""
    path=output/'maps/foundry-environment-checks';path.mkdir(parents=True,exist_ok=True)
    candidate=output/'maps/pressure-station-nine'
    if not candidate.exists():
        raise RuntimeError('Generate battlefield into this output root first')
    (path/'map.bin').write_bytes((candidate/'map.bin').read_bytes())
    base=(MOD/'maps/foundry-systems-lab/map.yaml').read_text()
    header=base.split('Actors:')[0].replace('Foundry Systems Lab','Environment Checks')
    header=header.replace('MapSize: 48,48','MapSize: 98,98').replace('Bounds: 1,1,46,46','Bounds: 1,1,96,96')
    text=header+'Actors:\n'
    text+=props()
    text+=actor('NorthFacility','fc.facility',48,18)+actor('SouthFacility','fc.facility',48,78)
    # Measure access before construction/hauling introduces dynamic traffic.
    for side,owner,hx in [('West','Tester',13),('East','Blue',82)]:
        text+=actor(side+'HQ','fc.hq',hx,47,owner)
    rules=base.split('Rules:',1)[1].replace('pvphit|rules/slice.yaml','pvphit|rules/slice.yaml, pvphit|rules/environment.yaml')
    rules=rules.replace('pvphit|maps/tank-proving-ground/systems.lua','checks.lua')
    briefing=next(line for line in rules.splitlines() if line.startswith('\t\t\tBriefing:'))
    rules=rules.replace(briefing,'\t\t\tBriefing: Candidate access, traffic and production laboratory. Launch through run_visual_checks.py for the required real deploy and withdrawal input. This is not a competitive match or balance test.')
    text+='\nRules:'+rules+'\nSequences: pvphit|sequences/environment.yaml\n'
    (path/'map.yaml').write_text(text)
    (path/'checks.lua').write_text((MOD/'tools/environment_checks.lua').read_text())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',required=True,choices=('sample','battlefield','checks'))
    parser.add_argument('--output-root',type=Path,default=MOD)
    args=parser.parse_args()
    {'sample':sample,'battlefield':battlefield,'checks':checks}[args.target](args.output_root)
