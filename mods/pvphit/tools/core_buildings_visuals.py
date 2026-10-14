"""Build and render the three core buildings through live Blender MCP.

Load with importlib, retain the module in bpy.app.driver_namespace, call build(),
then start_render('previews'|'sprites', assets=None). Earlier scenes are untouched.
Named meshes, stage/damage tags and fan actions are retained in standalone sources.
"""
from pathlib import Path
import importlib.util
import json
import math
import traceback
import bpy

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fc_core_geometry', HERE / 'heavy_visuals.py')
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
b = geometry.base  # Private helper module, never the running heavy pass.
b.OUT = b.MOD / 'art/core-buildings'
b.SOURCE = b.MOD / 'art/source/core-buildings'
NAMES = ('hq', 'generator', 'processor')
STATE = {}
ROOT = None
STAGE = 1


def box(name, loc, size, mat='ceramic', stage=None):
    o = b.box(name, loc, size, mat, ROOT)
    o['fc_stage'] = STAGE if stage is None else stage
    return o


def cyl(name, loc, radius, depth, mat='edge', rot=(0, 0, 0), stage=None):
    o = b.cyl(name, loc, radius, depth, mat, ROOT, rot)
    o['fc_stage'] = STAGE if stage is None else stage
    return o


def armor(name, x, y, width, depth, bottom, top, mat='ceramic', taper=.88):
    c = min(width, depth) * .15
    outline = [(x-width/2+c,y-depth/2),(x+width/2-c,y-depth/2),
               (x+width/2,y-depth/2+c),(x+width/2,y+depth/2-c),
               (x+width/2-c,y+depth/2),(x-width/2+c,y+depth/2),
               (x-width/2,y+depth/2-c),(x-width/2,y-depth/2+c)]
    o = geometry.armor(name, outline, bottom, top, mat, ROOT, taper=taper)
    o['fc_stage'] = STAGE
    return o


def panel(x, y, z, width=1, depth=.55):
    box('identification surround', (x,y,z), (width+.16,depth+.14,.10), 'iron')
    box('ownership enamel', (x,y,z+.06), (width,depth,.035), 'team')


def badge(x, y, z, size=1, collapse=False):
    # Equal upright bars above one crossbeam: the original Directorate device.
    for dx in (-.24, 0, .24):
        o = box('Directorate upright', (x+dx*size,y+.12*size,z), (.12*size,.46*size,.025), 'edge')
        if collapse:
            o['fc_damage'] = 'collapse'
    o = box('Directorate crossbeam', (x,y-.18*size,z), (.65*size,.10*size,.025), 'edge')
    if collapse:
        o['fc_damage'] = 'collapse'


def fan(x, y, z, radius=.46):
    cyl('fan armored rim', (x,y,z), radius+.11,.12,'edge')
    cyl('fan black well', (x,y,z+.067), radius,.018,'black')
    rotor = b.empty('cooling rotor', ROOT)
    rotor.location = (x,y,z+.09)
    rotor['fc_stage'] = STAGE
    rotor['fc_spin'] = math.pi/8
    for angle in (0, math.pi/2):
        blade = box('fan blade', (0,0,0), (radius*1.75,.13,.035), 'edge')
        blade.parent = rotor
        blade.rotation_euler.z = angle
    cyl('fan axle', (x,y,z+.14), .11,.08,'iron')
    # A loop is editable directly in the saved file as well as via export steps.
    for frame in (1,5):
        rotor.rotation_euler.z = (frame-1)*math.pi/8
        rotor.keyframe_insert(data_path='rotation_euler', frame=frame)
    for layer in rotor.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'
    rotor.rotation_euler.z = 0
    return rotor


def vents(x, y, z, width=.75, count=4):
    box('recessed louver well', (x,y,z), (width+.12,.07,.75), 'black')
    for i in range(count):
        box('louver blade', (x,y-.055,z-.25+i*.16), (width,.12,.07), 'edge')


def damage(o, kind='scorch'):
    o['fc_damage'] = kind
    return o


def new_scene(name, title, width, depth):
    global ROOT, STAGE
    s = b.studio(title, building=True)
    s.name = 'FC4 ' + title
    s.cycles.seed = 19
    s.frame_start, s.frame_end = 1, 4
    ROOT = b.empty(name + ' ground anchor')
    ROOT['fc_asset'] = name
    ROOT['fc_front'] = '-Y; processor apron aligns with engine +Y docking offset'
    STAGE = 0
    box('foundation', (0,0,.17), (width,depth,.34), 'iron')
    for x in (-width/2+.12,width/2-.12):
        box('foundation rail', (x,0,.34), (.15,depth-.18,.12), 'edge')
    b.ASSETS[name] = {'scene':s,'roots':[ROOT],'size':256}
    STAGE = 1
    return s


def hq():
    global STAGE
    new_scene('hq', 'Headquarters command bastion', 5.4, 4.6)
    armor('lower command fortress',0,.05,4.6,3.9,.35,1.65,'iron',.94)
    for x in (-2.1,2.1):
        for y in (-1.45,.15,1.6):
            damage(armor('sloped perimeter buttress',x,y,.64,.85,.35,2.05), 'scorch')
            box('buttress replaceable shield',(x,y-.33,1.1),(.32,.12,.85),'rust')
            for z in (.65,1.6):
                cyl('buttress anchor',(x,y-.405,z),.06,.035,'edge',(math.pi/2,0,0))
    box('armored access recess',(0,-1.94,.85),(1.45,.08,1.05),'black')
    for x in (-.7,.7):
        box('door jamb',(x,-2,.88),(.17,.22,1.12),'edge')
        box('entry worklight',(x,-2.13,1.38),(.16,.04,.09),'amber')
    for z in (.6,.85,1.1):
        box('access door reinforcement',(0,-2,z),(1.12,.06,.065),'iron')
    STAGE = 2
    armor('command terrace',0,.1,4.15,3.35,1.63,1.96)
    armor('central command keep',0,.5,2.55,2.35,1.95,3.18)
    box('observation recess',(0,-.65,2.65),(2.1,.08,.24),'black')
    for x in (-.72,0,.72):
        box('armored observation glazing',(x,-.70,2.65),(.54,.045,.10),'edge')
    damage(armor('command roof cap',0,.5,2.8,2.5,3.16,3.4), 'scorch')
    panel(0,-1.12,2.0,1.45,.57)
    for x in (-1.62,1.62):
        box('heat exchanger cassette',(x,.5,2.1),(.48,1.7,.28),'rust')
        for y in (-.12,.18,.48,.78,1.08):
            box('radiator ridge',(x,y,2.28),(.52,.07,.09),'edge')
    STAGE = 3
    badge(0,.03,3.42,1.35)
    damage(armor('communications pedestal',0,1.15,1.32,.85,3.4,3.73,'iron'), 'collapse')
    rotor = b.empty('protected communications sweep',ROOT)
    rotor.location = (0,1.15,3.77)
    rotor['fc_stage'], rotor['fc_spin'], rotor['fc_damage'] = 3, math.pi/8, 'collapse'
    for angle in (0,math.pi/2):
        o = box('communications paddle',(0,0,0),(1.2,.17,.17),'edge')
        o.parent = rotor
        o.rotation_euler.z = angle
    for x in (-.85,.85):
        damage(box('crown guard',(x,1.18,3.7),(.22,.74,.7)), 'collapse')
    STAGE = 4
    fan(-1.55,-.45,2.0,.3)
    box('command service light',(0,-2.0,1.72),(.45,.06,.08),'amber')


def generator():
    global STAGE
    new_scene('generator', 'Pressure Generator shielded heat plant',3.55,3.4)
    for x in (-.82,.82):
        cyl('vessel lower collar',(x,.25,.59),.70,.40,'iron')
        cyl('pressure vessel',(x,.25,1.48),.58,1.6,'edge')
        for z in (.9,1.65):
            cyl('vessel oxide band',(x,.25,z),.61,.15,'rust')
        for dx in (-.53,.53):
            damage(armor('vessel armored rib',x+dx,.25,.20,.80,.5,2.13), 'scorch')
    box('service manifold',(0,-1.12,.8),(2.6,.65,.75),'iron')
    STAGE = 2
    for x in (-.82,.82):
        damage(armor('refractory vessel shield',x,-.14,1.18,1.05,.9,1.85), 'scorch')
        cyl('induction collar',(x,.25,2.05),.59,.13,'cyan')
        damage(cyl('pressure head',(x,.25,2.24),.70,.28,'rust'), 'collapse' if x<0 else 'scorch')
        damage(cyl('armored head cap',(x,.25,2.43),.62,.14), 'collapse' if x<0 else 'scorch')
        damage(cyl('relief stack',(x,.45,2.78),.21,.65,'iron'), 'collapse' if x<0 else 'scorch')
        cyl('stack rim',(x,.45,3.08),.25,.09,'edge')['fc_damage'] = 'collapse' if x<0 else 'scorch'
        cyl('stack dark aperture',(x,.45,3.13),.17,.012,'black')['fc_damage'] = 'collapse' if x<0 else 'scorch'
    panel(0,-1.15,1.21,1,.48)
    STAGE = 3
    for x in (-1.42,1.42):
        cyl('manifold supply',(x,-.2,.6),.13,2.15,'rust',(math.pi/2,0,0))
        for y in (-.8,.55):
            cyl('pipe coupling',(x,y,.6),.19,.13,'edge',(math.pi/2,0,0))
    box('cooling housing',(0,1.12,1.32),(1.2,.85,1.45),'iron')
    fan(0,1.13,2.1,.39)
    vents(0,-1.455,.78,.68,3)
    STAGE = 4
    for x in (-1.13,1.13):
        box('service worklight',(x,-1.465,1.0),(.18,.04,.09),'amber')
    badge(.82,.12,2.52,.68)
    fallen = box('ruptured pressure shield',(-1.12,-.48,.62),(.6,.7,.10),'soot')
    fallen.rotation_euler = (.28,.3,-.25)
    fallen['fc_damage_only'] = True


def processor():
    global STAGE
    new_scene('processor','Slag Processor open receiving apron',5.4,4.6)
    # Full front row remains visually open, including the centerline dock.
    box('flush receiving apron',(0,-1.48,.355),(4.85,1.45,.035),'edge',0)
    for x in (-1.4,1.4):
        box('flush apron guide',(x,-1.5,.38),(.12,1.35,.025),'rust',0)
    for x in (-2.24,2.24):
        box('apron corner marker',(x,-1.85,.40),(.18,.5,.08),'rust',0)
    armor('furnace structural housing',-1.12,.65,2.65,2.7,.35,2.0,'iron')
    cyl('separator support',(1.55,.8,.64),.77,.58,'iron')
    STAGE = 2
    damage(armor('furnace refractory hood',-1.12,.7,2.7,2.7,1.55,2.62), 'scorch')
    for x in (-2.16,-.08):
        armor('furnace front cheek',x,-.61,.37,.40,.38,1.75)
        box('furnace cheek shield',(x,-.84,1.0),(.20,.10,.78),'rust')
    box('receiving mouth',(0,-.72,.84),(2.75,.09,.78),'black')
    box('intake upper armor',(0,-.66,1.32),(2.95,.38,.28),'ceramic')
    for x in (-.9,0,.9):
        box('intake machinery guard',(x,-.8,.74),(.12,.12,.48),'edge')
    for z in (.49,.65):
        cyl('receiving roller',(0,-.84,z),.09,2.5,'edge',(0,math.pi/2,0))
    cyl('cyclone separator',(1.55,.85,1.7),.66,1.85,'rust')
    for z in (1.0,1.95,2.5):
        cyl('separator containment band',(1.55,.85,z),.72,.14,'edge')
    for x in (1.02,2.08):
        damage(armor('separator blast rib',x,.75,.23,1.12,.45,2.32), 'scorch')
    STAGE = 3
    damage(cyl('separator exhaust crown',(1.55,.85,2.78),.62,.42), 'collapse')
    damage(cyl('cyclone outlet',(1.55,.85,3.14),.32,.38,'iron'), 'collapse')
    damage(cyl('cyclone mouth',(1.55,.85,3.35),.23,.03,'black'), 'collapse')
    box('rear transfer duct',(.2,1.5,1.9),(1.9,.4,.4),'iron')
    fan(-1.6,1.1,2.66,.42)
    damage(armor('furnace exhaust shield',-.65,1.22,.65,.80,2.6,3.46,'iron'), 'scorch')
    vents(-.65,.80,3.04,.45,3)
    panel(-1.15,-.12,2.67,1.25,.55)
    badge(1.55,.72,3.37,.55,collapse=True)
    STAGE = 4
    for x in (-1.27,1.27):
        box('dock worklight',(x,-.88,1.30),(.20,.05,.1),'amber')
    for y in (.4,1.1):
        box('furnace service panel',(-2.38,y,1.32),(.12,.45,.65),'rust')
    broken = box('fallen cyclone plate',(1.7,.15,.7),(.6,.8,.14),'soot')
    broken.rotation_euler = (.4,.25,.3)
    broken['fc_damage_only'] = True


def busy():
    return bpy.app.is_job_running('RENDER') or any(
        getattr(m,'STATE',{}).get('running') or getattr(getattr(m,'base',None),'STATE',{}).get('running')
        for m in bpy.app.driver_namespace.values())


def build(assets=None):
    names = tuple(NAMES if assets is None else assets)
    if not names or set(names)-set(NAMES):
        raise ValueError('Select hq, generator, processor')
    if busy() or b.ASSETS:
        raise RuntimeError('Render busy or this module already owns scenes; reuse it.')
    previous = bpy.context.window.scene
    try:
        b.palette()
        for key,color,metal,rough in [('ceramic',(.30,.29,.24),.15,.72),
                ('iron',(.065,.082,.09),.70,.60),('rust',(.23,.045,.025),.25,.77),
                ('edge',(.23,.255,.26),.75,.46)]:
            b.MATS[key] = b.material('FC4 '+key,color,metal,rough,True)
        for key,mat in b.MATS.items():
            mat['fc_material'] = key
        for name in names:
            globals()[name]()
        for a in b.ASSETS.values():
            a['scene'].frame_set(1)
        b.capture_rest()
        for a in b.ASSETS.values():
            set_state(a)
        b.save_sources()
        return {n:len(a['scene'].objects) for n,a in b.ASSETS.items()}
    finally:
        bpy.context.window.scene = previous


def load_sources(assets=None):
    """Render hand-edited saved sources without regenerating their geometry."""
    names = tuple(NAMES if assets is None else assets)
    if not names or set(names)-set(NAMES):
        raise ValueError('Select hq, generator, processor')
    if busy() or b.ASSETS:
        raise RuntimeError('Render busy or this module already owns scenes')
    paths = [b.SOURCE/f'{name}.blend' for name in names]
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError('Build or supply the selected .blend sources first')
    previous = bpy.context.window.scene
    try:
        b.palette()  # Preview and soot materials may have no users in a source.
        for name,path in zip(names,paths):
            with bpy.data.libraries.load(str(path),link=False) as (source,target):
                target.scenes = source.scenes
            if len(target.scenes)!=1:
                raise ValueError(f'Expected one owned scene in {path}')
            scene = target.scenes[0]
            scene.frame_set(1)
            roots = [o for o in scene.objects if o.get('fc_asset')==name]
            if len(roots)!=1:
                raise ValueError(f'Missing unique ground anchor in {path}')
            mats = dict(b.MATS)
            for o in scene.objects:
                for slot in o.material_slots:
                    if slot.material and slot.material.get('fc_material'):
                        mats[slot.material['fc_material']] = slot.material
            b.ASSETS[name] = {'scene':scene,'roots':roots,'size':256,'materials':mats}
        b.capture_rest()
        for a in b.ASSETS.values():
            set_state(a)
        return {name:len(a['scene'].objects) for name,a in b.ASSETS.items()}
    finally:
        bpy.context.window.scene = previous


def set_state(a, layer='idle', step=0, review=False):
    a['scene'].frame_set(step+1 if layer!='make' else 1)
    damaged = layer.startswith('damaged')
    materials = a.get('materials',b.MATS)
    for o in a['scene'].objects:
        loc,rot,scale,mats = a['rest'][o.name]
        o.location,o.rotation_euler,o.scale = loc.copy(),rot.copy(),scale.copy()
        o.hide_render = bool(o.get('fc_damage_only')) and not damaged
        if layer=='make' and o.get('fc_stage',0)>step:
            o.hide_render = True
        if o.get('fc_spin') and layer!='make':
            o.rotation_euler.z += step*o['fc_spin']
        if damaged and o.get('fc_damage')=='collapse':
            o.location.z -= .48
            o.rotation_euler.y += .38
            o.rotation_euler.x += .15
        if o.type not in ('MESH','FONT'):
            continue
        o.data.materials.clear()
        for mat in mats:
            o.data.materials.append(materials['review'] if review and mat==materials['team'] else mat)
        if damaged and o.get('fc_damage'):
            o.data.materials.clear()
            o.data.materials.append(materials['soot'])


def start_render(mode='sprites', assets=None):
    if mode not in ('sprites','previews'):
        raise ValueError(mode)
    names = tuple(b.ASSETS if assets is None else assets)
    if not names or set(names)-set(b.ASSETS):
        raise ValueError('Build selected assets before rendering')
    if STATE.get('running') or busy():
        raise RuntimeError('A Blender render or visual pass is running')
    jobs = [(n,layer,i) for n in names for layer,count in
            ([('idle',4),('damaged-idle',4),('make',5)] if mode=='sprites'
             else [('idle',1),('damaged-idle',1)]) for i in range(count)]
    previous = bpy.context.window.scene
    STATE.clear()
    STATE.update(running=True,mode=mode,total=len(jobs),done=0,assets=names)
    b.OUT.mkdir(parents=True,exist_ok=True)
    def status():
        path = b.OUT/'render-status.json'
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(STATE,indent=2)+'\n')
        temp.replace(path)
    def restore():
        for a in b.ASSETS.values():
            set_state(a)
            a['scene'].render.resolution_x = a['scene'].render.resolution_y = 256
        bpy.context.window.scene = previous
    def tick():
        try:
            name,layer,step = jobs.pop(0)
            a = b.ASSETS[name]
            s = a['scene']
            bpy.context.window.scene = s
            set_state(a,layer,step,mode=='previews')
            s.render.resolution_x = s.render.resolution_y = 640 if mode=='previews' else 256
            path = b.OUT/('previews' if mode=='previews' else 'frames')/name/layer/f'{step:02d}.png'
            path.parent.mkdir(parents=True,exist_ok=True)
            s.render.filepath = str(path)
            bpy.ops.render.render(write_still=True,scene=s.name)
            STATE.update(done=STATE['done']+1,last=str(path),running=bool(jobs))
            status()
            if jobs:
                return .15
            restore()
        except Exception:
            STATE.update(running=False,error=traceback.format_exc())
            status()
            restore()
        return None
    status()
    bpy.app.timers.register(tick,first_interval=.5)
    return dict(STATE)
