"""Check real generated map geometry, resources, scope and reproducibility.

Geometric paths are not engine timing or evidence of competitive balance.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import heapq
import json
import math
import re
import struct
import tempfile
import zipfile
from environment_ground import MOD, IDS, build
from build_environment_maps import battlefield, sample, checks


def read_map(data):
    version,w,h,to,ho,ro=struct.unpack_from('<BHHIII',data)
    assert version==2 and ho==0 and len(data)==ro+w*h*2
    tiles={(x,y):struct.unpack_from('<HB',data,to+(x*h+y)*3) for x in range(w) for y in range(h)}
    resources={(x,y) for x in range(w) for y in range(h) if data[ro+(x*h+y)*2]==1}
    return w,h,tiles,resources


def fields(resources):
    remaining=set(resources); result=[]
    while remaining:
        start=min(remaining); cells={start}; pending=[start];remaining.remove(start)
        while pending:
            x,y=pending.pop()
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                p=x+dx,y+dy
                if p in remaining:
                    remaining.remove(p);cells.add(p);pending.append(p)
        density=sum(max(12*sum((x+dx,y+dy) in cells for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)//9,1) for x,y in cells)
        result.append({'center':[sum(x for x,y in cells)/len(cells),sum(y for x,y in cells)/len(cells)],
                       'cells':len(cells),'recalculated_units':density,'credits':density*25})
    return result


def actors(text):
    return [(name,kind,int(x),int(y)) for name,kind,x,y in re.findall(
        r'^\t(\w+): ([\w.-]+)\n\t\tOwner: \w+\n\t\tLocation: (\d+),(\d+)',text,re.M)]


def paths(start, blocked, resources):
    # Octile geometry only: retain a separate engine locomotor measurement.
    distances={start:0}; queue=[(0,start)]
    while queue:
        cost,(x,y)=heapq.heappop(queue)
        if cost!=distances[(x,y)]:continue
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if not(dx or dy):continue
                p=x+dx,y+dy
                if not(1<=p[0]<=96 and 1<=p[1]<=96) or p in blocked:continue
                if dx and dy and ((x+dx,y) in blocked or (x,y+dy) in blocked):continue
                value=cost+math.hypot(dx,dy)
                if value<distances.get(p,math.inf):
                    distances[p]=value;heapq.heappush(queue,(value,p))
    return distances


def check():
    before=json.loads((MOD/'docs/validation/environment/before-sha256.json').read_text())
    data=(MOD/'maps/pressure-station-nine/map.bin').read_bytes()
    w,h,tiles,resources=read_map(data)
    assert (w,h)==(98,98) and all(t in IDS.values() and i==0 for t,i in tiles.values())
    with zipfile.ZipFile(MOD/'docs/validation/environment/pressure-station-nine-baseline.oramap') as z:
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest()==before['mods/pvphit/maps/pressure-station-nine/'+name],name
        old=read_map(z.read('map.bin'))[3]
    totals=fields(resources);baseline=fields(old)
    assert sorted((f['cells'],f['recalculated_units']) for f in totals)==sorted((f['cells'],f['recalculated_units']) for f in baseline)
    parsed=actors((MOD/'maps/pressure-station-nine/map.yaml').read_text())
    blocked=set(); decorative=[]
    for name,kind,x,y in parsed:
        if kind.startswith('fc.env.wall'): blocked.add((x,y))
        elif kind=='fc.facility': blocked.update((x+dx,y+dy) for dx in range(2) for dy in range(2))
        elif kind.startswith('fc.env.'): decorative.append((x,y))
    assert len(decorative)<=80
    assert len([a for a in parsed if a[1].startswith('fc.env.wall')])<=24
    assert not resources.intersection(blocked)
    for sy in (18,78):
        station={(x,y) for x in (48,49) for y in (sy,sy+1)}
        apron={(x,y) for x in range(44,54) for y in range(sy-4,sy+6)}-station
        assert not apron.intersection(resources|blocked|set(decorative)),('station apron',sy)
    for hx in (13,82):blocked.update((hx+dx,47+dy) for dx in range(3) for dy in range(3))
    pairs={}
    for side,start in [('west',(14,51)),('east',(83,51))]:
        d=paths(start,blocked,resources)
        groups={'home': {(x,y) for x,y in resources if (x<30 if side=='west' else x>67)},
                'north_expansion': {(x,y) for x,y in resources if 40<x<60 and y<40},
                'south_expansion': {(x,y) for x,y in resources if 40<x<60 and y>60}}
        for label,sy in [('north_station',18),('south_station',78)]:
            groups[label]={(x,y) for x in range(47,51) for y in range(sy-1,sy+3)}-blocked
        pairs[side]={name:round(min(d[p] for p in cells),4) for name,cells in groups.items()}
    for name in pairs['west']:
        assert abs(pairs['west'][name]-pairs['east'][name])<=1.001,(name,pairs)
    # Concrete feasible opening layouts, south aprons, and two extra generators.
    openings={}
    for side,buildings in [('west',[(17,45,2,2),(20,42,3,3),(13,51,3,3),(10,47,2,2),(10,51,2,2)]),
                          ('east',[(79,45,2,2),(75,42,3,3),(82,51,3,3),(86,47,2,2),(86,51,2,2)])]:
        occupied=set(blocked); hx=14 if side=='west' else 83
        buildable={(hx+dx,48+dy) for dx in (-1,0,1) for dy in (-1,0,1)}
        for x,y,bw,bh in buildings:
            footprint={(x+a,y+b) for a in range(bw) for b in range(bh)}
            assert not footprint.intersection(occupied|resources),(side,x,y)
            assert all(math.hypot(a-hx,b-48)<=14 for a,b in footprint),(side,'radius',x,y)
            assert any(abs(a-c)<=2 and abs(b-d)<=2 for a,b in footprint for c,d in buildable),(side,'adjacency',x,y)
            occupied.update(footprint)
            buildable.update(footprint)
        for x,y,bw,bh in buildings[1:3]:
            left = x-1 if side=='west' else x-2
            apron={(a,b) for a in range(left,left+6) for b in range(y+3,y+7)}
            assert not apron.intersection(occupied|resources),(side,'apron',x,y)
        openings[side]=buildings
    original=(MOD.parent/'ra/tilesets/temperat.yaml').read_bytes()
    derived=(MOD/'tilesets/temperat-industrial.yaml').read_bytes()
    assert derived.startswith(original), 'Inherited templates changed'
    # Build into two fresh destinations, never into unrelated maps.
    with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
        for destination in (Path(a),Path(b)):
            build(destination);sample(destination);battlefield(destination);checks(destination)
        for p in Path(a).rglob('*'):
            if p.is_file():assert p.read_bytes()==(Path(b)/p.relative_to(a)).read_bytes(),p
        for name in ('pressure-station-nine','foundry-environment-sample','foundry-environment-checks'):
            assert (Path(a)/'maps'/name/'map.bin').read_bytes()==(MOD/'maps'/name/'map.bin').read_bytes(),name
        assert (Path(a)/'maps/foundry-environment-checks/checks.lua').read_bytes()==(MOD/'maps/foundry-environment-checks/checks.lua').read_bytes()
    allowed={'mods/pvphit/mod.yaml','mods/pvphit/tools/build_maps.py','mods/pvphit/README.md','mods/pvphit/VALIDATION.md'}
    allowed.update('mods/pvphit/maps/pressure-station-nine/'+n for n in ('map.yaml','map.bin','map.png'))
    root=MOD.parents[1]
    unexpected=[p for p,digest in before.items() if p not in allowed and hashlib.sha256((root/p).read_bytes()).hexdigest()!=digest]
    assert not unexpected,unexpected
    return {'scope':'Static geometry; not locomotor timing or balance proof','resources':totals,
            'total_credits':sum(f['credits'] for f in totals),'geometric_paths':pairs,
            'opening_layouts':openings,'blocking_wall_cells':24,'decorative_actors':len(decorative),
            'station_apron_clearance_cells':4,'baseline_archive_preserved':True,
            'inherited_templates_preserved':True,'unrelated_files_preserved':True,'reproduction':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=check();text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text)
