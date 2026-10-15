"""Furnace Covenant vehicles: build/load and render through the live Blender MCP.

Import without side effects, then build() OR load_sources(), followed by
start_render('previews'), inspect, and start_render('sprites'). Never regenerate
hand-edited sources: load_sources reads the saved scenes without saving them.
"""
from pathlib import Path
import importlib.util
import math
import json
import traceback
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fc_vehicle_helpers', HERE/'refine_visuals.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = b.MOD/'art/vehicles'
SOURCE = b.MOD/'art/source/vehicles'
NAMES = ('hauler', 'scout', 'siege')
ASSETS = {}
STATE = {}
ROOT = None
LAYER = 'body'


def box(name, loc, size, mat='ceramic', bevel=.025):
    o = b.box(name, loc, size, mat, ROOT, bevel, LAYER)
    o.name = 'FC5 ' + name
    return o


def cyl(name, loc, radius, depth, mat='edge', rot=(0,0,0)):
    o = b.cyl(name, loc, radius, depth, mat, ROOT, rot, LAYER)
    o.name = 'FC5 ' + name
    return o


def armor(name, x, y, width, depth, bottom, top, mat='ceramic', taper=.88):
    cut = min(width, depth)*.16
    points = [(-width/2+cut,-depth/2),(width/2-cut,-depth/2),
              (width/2,-depth/2+cut),(width/2,depth/2-cut),
              (width/2-cut,depth/2),(-width/2+cut,depth/2),
              (-width/2,depth/2-cut),(-width/2,-depth/2+cut)]
    vertices = [(x+px,y+py,bottom) for px,py in points]
    vertices += [(x+px*taper,y+py*taper,top) for px,py in points]
    faces = [tuple(reversed(range(8))),tuple(range(8,16))]
    faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    mesh = bpy.data.meshes.new('FC5 '+name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    o = bpy.data.objects.new('FC5 '+name,mesh)
    bpy.context.scene.collection.objects.link(o)
    b.finish(o,name,mat,ROOT,LAYER)
    o.name = 'FC5 '+name
    bevel = o.modifiers.new('Forged edge','BEVEL')
    bevel.width,bevel.segments = .018,2
    o.modifiers.new('Plate normals','WEIGHTED_NORMAL')
    return o


def link(name, start, end, radius=.045, mat='edge'):
    mid = (Vector(start)+Vector(end))/2
    delta = Vector(end)-Vector(start)
    o = cyl(name, mid, radius, delta.length, mat)
    o.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
    return o


def muzzle_ring():
    vertices = []
    for radius,z in ((.46,1.99),(.46,2.21),(.32,2.21),(.32,1.99)):
        vertices.extend((radius*math.cos(i*math.tau/32),.20+radius*math.sin(i*math.tau/32),z) for i in range(32))
    faces = [(row*32+i,row*32+(i+1)%32,((row+1)%4)*32+(i+1)%32,((row+1)%4)*32+i)
             for row in range(4) for i in range(32)]
    mesh = bpy.data.meshes.new('FC5 open refractory muzzle')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    o = bpy.data.objects.new('FC5 refractory muzzle crown',mesh)
    bpy.context.scene.collection.objects.link(o)
    b.finish(o,'refractory muzzle crown','ceramic',ROOT)
    o.name = 'FC5 refractory muzzle crown'
    return o


def team_panel(x,y,z,w=.55,d=.34):
    box('ownership frame',(x,y,z),(w+.10,d+.10,.06),'iron',.012)
    box('ownership enamel',(x,y,z+.036),(w,d,.018),'team',.004)


def vents(x,y,z,w=.45):
    box('cooler housing',(x,y,z),(w+.12,.45,.10),'iron',.018)
    for j in range(4):
        box('recessed radiator fin',(x,y-.15+j*.10,z+.057),(w,.035,.018),'edge',.003)


def damage(o, shift=(0,0,0), rot=(0,0,0), hide=False):
    o['fc_wreck_shift'] = shift
    o['fc_wreck_rot'] = rot
    o['fc_wreck_hide'] = hide
    return o


def tracks(length, width):
    box('load bearing chassis',(0,0,.52),(width-.35,length-.2,.43),'iron')
    for side in (-1,1):
        x = side*width/2
        box('continuous track belt',(x,0,.32),(.42,length,.45),'black',.10)
        for y in (-length*.36,0,length*.36):
            cyl('recessed road wheel',(x+side*.22,y,.34),.205,.025,'iron',(0,math.pi/2,0))
            cyl('road wheel hub',(x+side*.238,y,.34),.075,.03,'edge',(0,math.pi/2,0))
        for j in range(12):
            y = -length*.45+j*length*.9/11
            box('individual track shoe',(x,y,.108),(.47,.09,.075),'edge',.008)
        for j,y in enumerate((-length*.33,0,length*.33)):
            box('segmented track shoulder',(x,y,.68),(.53,length*.29,.17),'ceramic' if j!=1 else 'rust')
            p = box('hanging track guard',(x+side*.22,y,.58),(.10,length*.25,.23),'iron',.014)
            if side==1 and j==0: damage(p,(.12,0,-.16),(0,.35,.12))
            for yy in (y-length*.08,y+length*.08):
                cyl('guard bolt',(x+side*.28,yy,.61),.034,.018,'edge',(0,math.pi/2,0))
        box('rear tow lug',(side*.55,length/2+.04,.43),(.17,.17,.16),'edge',.014)
        box('worklight surround',(x,-length/2,.72),(.27,.13,.18),'iron',.014)
        damage(box('amber worklight',(x,-length/2-.072,.73),(.16,.018,.065),'amber',.003),hide=True)


def hauler():
    tracks(2.70,1.94)
    armor('cab protected plinth',0,-.88,1.42,.90,.65,1.32)
    armor('raised driver cell',-.14,-.84,1.12,.70,1.30,1.55,taper=.82)
    damage(box('recessed cab glazing',(-.12,-1.225,1.36),(.71,.022,.115),'black',.008))
    for x in (-.51,.25):
        box('cab window pillar',(x,-1.25,1.38),(.07,.06,.22),'edge',.008)
    team_panel(-.16,-.86,1.565,.65,.30)
    # A deep, open refractory hopper, surrounded by replaceable heat shields.
    box('hopper dark interior',(0,.43,.81),(1.47,1.65,.12),'black')
    for side in (-1,1):
        damage(box('hopper side ceramic',(side*.73,.43,1.12),(.16,1.68,.65),'ceramic'),
               (side*.09,0,-.10),(0,side*.24,0))
        box('hopper oxide lining',(side*.635,.43,1.14),(.03,1.48,.48),'rust',.005)
        for y in (-.17,.40,.97):
            box('hopper iron rib',(side*.824,y,1.12),(.065,.10,.61),'iron',.01)
        box('hopper top rail',(side*.73,.43,1.47),(.21,1.76,.08),'edge',.012)
        link('cargo tipping cylinder',(side*.62,.28,.63),(side*.62,1.0,1.0),.065,'iron')
        cyl('rear hopper hinge',(side*.65,1.23,.90),.11,.20,'edge',(0,math.pi/2,0))
    damage(box('rear discharge gate',(0,1.25,1.14),(1.46,.16,.60),'rust'),(0,.12,-.13),(.28,0,0))
    box('gate locking beam',(0,1.35,1.08),(1.50,.09,.10),'edge')
    for x in (-.4,.4): box('gate latch',(x,1.40,1.12),(.10,.09,.28),'iron',.01)
    # Modest permanent residue is not a cargo-capacity animation.
    for x,y,r in ((-.35,.2,.18),(.22,.45,.23),(-.12,.80,.19)):
        cyl('slag residue',(x,y,.95),r,.20,'rust')
    box('collector backing',(0,-1.45,.48),(1.78,.19,.46),'iron')
    damage(box('collection blade',(0,-1.57,.35),(1.90,.16,.25),'rust'),(0,-.05,-.09),(0,.06,.08))
    for x in (-.65,-.32,0,.32,.65):
        box('collector tooth',(x,-1.66,.25),(.12,.18,.08),'edge',.008)
    for side in (-1,1):
        link('collector ram',(side*.6,-.87,.71),(side*.6,-1.43,.51),.055)
    box('service cabinet',(.54,-.13,1.13),(.32,.38,.48),'iron')
    vents(.54,-.13,1.40,.22)
    cyl('shielded service exhaust',(-.55,-.20,1.42),.10,.60,'iron')
    damage(cyl('exhaust cap',(-.55,-.20,1.75),.14,.09,'edge'),(-.05,0,-.2),(0,.35,0))
    b.stamp((0,-.43,1.331),.55,ROOT)


def scout():
    armor('narrow reconnaissance chassis',0,0,1.13,1.92,.38,.75,'iron')
    for side in (-1,1):
        for y in (-.68,.03,.72):
            x = side*.70
            link('suspension arm',(side*.40,y-.13,.48),(x,y,.31),.055,'edge')
            damage(cyl('exposed all terrain wheel',(x,y,.30),.29,.25,'black',(0,math.pi/2,0)),
                   (side*.09,0,-.04),(0,0,side*.16) if y==.72 else (0,0,0))
            cyl('wheel armored hub',(x+side*.139,y,.30),.16,.032,'iron',(0,math.pi/2,0))
            cyl('wheel center',(x+side*.160,y,.30),.065,.04,'edge',(0,math.pi/2,0))
            box('individual wheel fender',(x,y,.63),(.34,.44,.09),'ceramic',.02)
        box('side rail',(side*.55,.15,.83),(.10,1.12,.12),'rust',.014)
        damage(box('front amber lamp',(side*.40,-.968,.65),(.14,.025,.065),'amber',.004),hide=True)
    armor('sloping forward glacis',0,-.63,1.02,.63,.65,.93,taper=.65)
    team_panel(0,-.62,.94,.48,.24)
    armor('protected crew pod',0,.30,.97,1.0,.71,1.02,taper=.84)
    vents(0,.64,1.03,.50)
    box('front bumper',(0,-1.01,.45),(1.03,.12,.12),'edge',.015)
    # Mast stays with hull and behind the turret sweep.
    box('communications armored foot',(-.37,.65,1.15),(.25,.26,.30),'iron')
    damage(cyl('relay mast',(-.37,.65,1.59),.028,.65,'edge'),(0,0,-.24),(0,.65,0))
    damage(box('protected relay head',(-.37,.65,1.94),(.18,.08,.14),'rust',.01),(-.20,0,-.3),(0,.65,0))
    global ROOT, LAYER
    hull = ROOT
    ROOT = b.empty('FC5 turret ground anchor')
    ROOT['fc_root'] = 'turret'
    LAYER = 'turret'
    cyl('turret bearing',(0,0,1.06),.32,.13,'black')
    damage(armor('light gun sensor turret',0,0,.67,.69,1.10,1.36,'ceramic',.72),(.10,.03,-.12),(.10,.16,.15))
    box('gun mantlet',(0,-.30,1.22),(.28,.23,.22),'iron')
    damage(cyl('light gun barrel',(0,-.63,1.22),.055,.55,'iron',(math.pi/2,0,0)),(.10,0,-.05),(0,.2,0))
    cyl('recessed muzzle',(0,-.915,1.22),.035,.018,'black',(math.pi/2,0,0))
    box('protected sensor',(.22,-.18,1.35),(.19,.23,.16),'iron',.018)
    damage(box('sensor glass',(.22,-.303,1.35),(.09,.014,.045),'black',.003),hide=True)
    team_panel(-.10,.05,1.37,.24,.23)
    ROOT = hull
    LAYER = 'body'


def siege():
    tracks(2.55,1.91)
    armor('mortar armored deck',0,0,1.55,2.18,.65,.91,'iron')
    armor('forward crew shield',0,-.90,1.42,.62,.85,1.20)
    team_panel(0,-.91,1.22,.65,.27)
    cyl('fixed mortar foundation',(0,.20,.99),.63,.24,'black')
    cyl('mortar pressure jacket',(0,.20,1.49),.35,.85,'iron')
    for z in (1.15,1.65,1.92): cyl('mortar reinforcing collar',(0,.20,z),.42,.13,'rust')
    damage(muzzle_ring(),(.10,0,-.20),(0,.28,0))
    damage(cyl('deep mortar bore',(0,.20,1.995),.32,.018,'black'),(.10,0,-.20),(0,.28,0))
    for side in (-1,1):
        x = side*.50
        damage(armor('load bearing cradle',x,.20,.23,.89,.89,1.74,'ceramic',.70),
               (side*.08,0,-.1),(0,side*.18,0))
        cyl('cradle trunnion',(side*.55,.20,1.39),.14,.14,'edge',(0,math.pi/2,0))
        cyl('pressure accumulator',(side*.50,.86,1.24),.15,.60,'rust')
        link('pressure line',(side*.50,.86,1.50),(side*.33,.39,1.63),.035,'edge')
        damage(box('induction aperture',(side*.365,-.04,1.77),(.055,.26,.055),'cyan',.004),hide=True)
        for y in (-.78,.82):
            box('stabilizer socket',(side*.85,y,.54),(.32,.38,.28),'iron')
            # Three nested carriage pieces extend while the load foot lowers.
            for j in range(2):
                o = box('telescoping stabilizer',(side*(.93+j*.06),y,.43-j*.04),(.38,.23-j*.045,.16),'edge' if j else 'rust',.012)
                o['fc_deploy_shift'] = (side*(.18+j*.22),0,-j*.08)
            foot = box('stabilizer ground shoe',(side*1.02,y,.27),(.36,.40,.14),'iron',.02)
            foot['fc_deploy_shift'] = (side*.55,0,-.16)
            cap = box('ground shoe ceramic cap',(side*1.02,y,.35),(.29,.32,.06),'ceramic',.01)
            cap['fc_deploy_shift'] = (side*.55,0,-.16)
    vents(0,1.02,1.02,.52)
    b.stamp((0,-.36,.933),.60,ROOT)


def busy():
    return bpy.app.is_job_running('RENDER') or any(
        getattr(m,'STATE',{}).get('running') or getattr(getattr(m,'base',None),'STATE',{}).get('running')
        for m in bpy.app.driver_namespace.values())


def selected(assets):
    names = tuple(NAMES if assets is None else assets)
    if not names or set(names)-set(NAMES):
        raise ValueError('Select hauler, scout, siege')
    return names


def capture(a):
    a['rest'] = {o: (o.location.copy(),o.rotation_euler.copy(),o.scale.copy(),o.hide_render,
                    list(o.data.materials) if o.type in ('MESH','FONT') else []) for o in a['scene'].objects}


def build(assets=None):
    global ROOT, LAYER
    names = selected(assets)
    if busy() or ASSETS:
        raise RuntimeError('Busy or module already owns scenes; reuse or load in a fresh module')
    paths = [SOURCE/f'{n}.blend' for n in names]
    if any(p.exists() for p in paths):
        raise FileExistsError('Sources exist. Use load_sources() to retain edits.')
    previous = bpy.context.window.scene
    try:
        for name in names:
            b.palette()
            for key,color,metal,rough in [('ceramic',(.30,.29,.24),.15,.72),
                    ('iron',(.065,.082,.09),.70,.60),('rust',(.23,.045,.025),.25,.77),
                    ('edge',(.23,.255,.26),.75,.46)]:
                b.MATS[key] = b.material('FC5 '+key,color,metal,rough,True)
            for key,mat in b.MATS.items():
                mat.name = f'FC5 {name} {key}'
                mat['fc_material'] = key
            s = b.studio(name)
            s.name = 'FC5 '+name
            s['fc_asset'] = name
            s.cycles.seed = 0
            ROOT = b.empty('FC5 hull ground anchor')
            ROOT['fc_root'] = 'body'
            LAYER = 'body'
            globals()[name]()
            a = {'scene':s,'materials':dict(b.MATS)}
            ASSETS[name] = a
            capture(a)
        SOURCE.mkdir(parents=True,exist_ok=True)
        for name,a in ASSETS.items():
            # Explicit scene roots exclude every unrelated scene in the session.
            bpy.data.libraries.write(str(SOURCE/f'{name}.blend'),{a['scene']},fake_user=True,compress=True)
        return {n:len(a['scene'].objects) for n,a in ASSETS.items()}
    finally:
        bpy.context.window.scene = previous


def load_sources(assets=None):
    names = selected(assets)
    if busy() or ASSETS:
        raise RuntimeError('Busy or module already owns scenes')
    previous = bpy.context.window.scene
    try:
        for name in names:
            with bpy.data.libraries.load(str(SOURCE/f'{name}.blend'),link=False) as (src,dst):
                if len(src.scenes)!=1:
                    raise ValueError(f'{name}: expected exactly one scene')
                dst.scenes = src.scenes
            s = dst.scenes[0]
            roots = [o.get('fc_root') for o in s.objects if o.get('fc_root')]
            if s.get('fc_asset')!=name or sorted(roots)!=(['body','turret'] if name=='scout' else ['body']):
                raise ValueError(f'{name}: missing scene/anchor tags')
            b.palette()
            mats = dict(b.MATS)
            for o in s.objects:
                for slot in o.material_slots:
                    if slot.material and slot.material.get('fc_material'):
                        mats[slot.material['fc_material']] = slot.material
            a = {'scene':s,'materials':mats}
            ASSETS[name] = a
            capture(a)
        return {n:len(a['scene'].objects) for n,a in ASSETS.items()}
    finally:
        bpy.context.window.scene = previous


def pose(a, layer, facing, step=0, review=False):
    s = a['scene']
    s.frame_set(1)
    deploy = step/4 if layer=='make' else 1 if layer=='deployed' else 0
    for o,(loc,rot,scale,hidden,mats) in a['rest'].items():
        o.location,o.rotation_euler,o.scale,o.hide_render = loc.copy(),rot.copy(),scale.copy(),hidden
        if o.get('fc_root'):
            o.rotation_euler.z += facing*math.tau/32
        if layer in ('body','turret') and o.type in ('MESH','FONT'):
            o.hide_render |= o.get('fc_layer','body') != layer
        if o.get('fc_deploy_shift'):
            o.location += Vector(o['fc_deploy_shift'])*deploy
        if layer=='wreck':
            o.location += Vector(o.get('fc_wreck_shift',(0,0,0)))
            for i,v in enumerate(o.get('fc_wreck_rot',(0,0,0))): o.rotation_euler[i] += v
            o.hide_render |= bool(o.get('fc_wreck_hide'))
        if o.type in ('MESH','FONT'):
            o.data.materials.clear()
            for mat in mats:
                role = mat.get('fc_material')
                if layer=='wreck' and role in ('team','cyan','amber','rust'):
                    mat = a['materials']['soot']
                elif review and role=='team':
                    mat = a['materials']['review']
                o.data.materials.append(mat)
    bpy.context.view_layer.update()


def jobs(mode, names):
    for name in names:
        if mode=='previews':
            for layer in (('all','deployed') if name=='siege' else ('all',)):
                yield name,layer,4,0
        elif mode=='samples':
            for layer in (('all','deployed') if name=='siege' else ('all',)):
                for facing in (0,4,8,12,16,20,24,28): yield name,layer,facing,0
        else:
            layers = [('body',1),('wreck',1)]
            if name=='scout': layers += [('turret',1)]
            if name=='siege': layers += [('make',5),('deployed',1)]
            for layer,count in layers:
                for facing in range(32):
                    for step in range(count): yield name,layer,facing,step
            yield name,'icon',4,0


def start_render(mode='sprites', assets=None):
    if mode not in ('sprites','previews','samples'): raise ValueError(mode)
    names = selected(assets)
    if set(names)-set(ASSETS): raise ValueError('Load/build assets first')
    if busy(): raise RuntimeError('A render or timer pass is already running')
    queue = list(jobs(mode,names))
    previous = bpy.context.window.scene
    saved = {}
    for n in names:
        a = ASSETS[n]
        s = a['scene']
        saved[n] = (s.frame_current,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
    STATE.clear()
    STATE.update(running=True,mode=mode,total=len(queue),done=0,assets=names)
    OUT.mkdir(parents=True,exist_ok=True)
    def status():
        path = OUT/f'{mode}-status.json'
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(STATE,indent=2)+'\n')
        temp.replace(path)
    def restore():
        for n in names:
            a = ASSETS[n]
            s = a['scene']
            frame,rx,ry,path = saved[n]
            s.frame_set(frame)
            for o,(loc,rot,scale,hidden,mats) in a['rest'].items():
                o.location,o.rotation_euler,o.scale,o.hide_render = loc.copy(),rot.copy(),scale.copy(),hidden
                if o.type in ('MESH','FONT'):
                    o.data.materials.clear()
                    for mat in mats: o.data.materials.append(mat)
            s.render.resolution_x,s.render.resolution_y,s.render.filepath = rx,ry,path
        bpy.context.window.scene = previous
    def tick():
        try:
            name,layer,facing,step = queue.pop(0)
            a = ASSETS[name]
            s = a['scene']
            bpy.context.window.scene = s
            pose(a,'all' if layer=='icon' else layer,facing,step,mode=='previews')
            s.render.resolution_x = s.render.resolution_y = 640 if mode=='previews' else 128
            folder = 'frames' if mode=='sprites' else mode
            index = facing*5+step if layer=='make' else 0 if layer=='icon' else facing
            path = OUT/folder/name/layer/f'{index:03d}.png'
            path.parent.mkdir(parents=True,exist_ok=True)
            s.render.filepath = str(path)
            bpy.ops.render.render(write_still=True,scene=s.name)
            STATE.update(done=STATE['done']+1,last=str(path))
            if queue:
                status()
                return .05
            restore()
            STATE['running'] = False
            status()
        except Exception:
            STATE.update(running=False,error=traceback.format_exc())
            try: restore()
            finally: status()
        return None
    status()
    bpy.app.timers.register(tick,first_interval=.5)
    return dict(STATE)
