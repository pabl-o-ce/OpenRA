"""Furnace Covenant visual pass, executed inside Blender via MCP.

Load with importlib, call build(), then start_render('previews'|'sprites').
All models are built in separate scenes. The user's scenes and the earlier
source models are preserved. Frames render through a timer in the live Blender
instance; status is written to art/refined/render-status.json.
"""
from pathlib import Path
import json
import math
import traceback
import bpy
from mathutils import Vector

MOD = Path(__file__).resolve().parents[1]
OUT = MOD / 'art/refined'
SOURCE = MOD / 'art/source/refined'
ASSETS = {}
MATS = {}
JOBS = []
STATE = {}


def material(name, color, metal=0, rough=.65, wear=False, emission=0):
    m = bpy.data.materials.new('FC2 ' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n, links = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = emission
    if wear:
        noise = n.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 8
        noise.inputs['Detail'].default_value = 3
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .2
        ramp.color_ramp.elements[0].color = (*(v*.65 for v in color), 1)
        ramp.color_ramp.elements[1].position = .8
        ramp.color_ramp.elements[1].color = (*color, 1)
        links.new(noise.outputs['Fac'], ramp.inputs[0])
        links.new(ramp.outputs[0], p.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .12
        bump.inputs['Distance'].default_value = .015
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs[0], p.inputs['Normal'])
    return m


def palette():
    for key, args in {
        'ceramic': ((.42,.39,.31), .15,.68,True),
        'edge': ((.28,.30,.30), .65,.5,True),
        'iron': ((.10,.13,.14), .65,.64,True),
        'black': ((.025,.033,.038), .25,.82),
        'rust': ((.30,.065,.028), .3,.8,True),
        'team': ((.025,.8,.055), 0,.68),
        'review': ((.58,.055,.03), 0,.68),
        'cyan': ((.02,.48,.58), .2,.4,False,.7),
        'amber': ((1,.25,.025), .05,.55,False,.5),
        'concrete': ((.115,.125,.123), .0,.96,True),
        'soot': ((.036,.031,.027), .1,.96,True),
    }.items():
        MATS[key] = material(key, *args)


def studio(name, building=False, floor=False):
    s = bpy.data.scenes.new('FC2 ' + name)
    bpy.context.window.scene = s
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = 24
    s.cycles.use_denoising = True
    s.render.threads_mode, s.render.threads = 'FIXED', 4
    s.render.film_transparent = True
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGBA'
    size = 48 if floor else 256 if building else 128
    s.render.resolution_x = s.render.resolution_y = size
    s.render.resolution_percentage = 100
    s.view_settings.view_transform, s.view_settings.look = 'Standard','None'
    s.view_settings.exposure = -.7
    s.world = bpy.data.worlds.new('FC2 studio ' + name)
    s.world.use_nodes = True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.3,.3,.3,1)
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35
    scale = 2 if building else 1
    target = Vector((0,0,.75*scale))
    bpy.ops.object.camera_add(location=(0,-8*scale,8*scale) if not floor else (0,0,10))
    camera = bpy.context.object
    camera.name = 'FC2 sprite camera ' + name
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2 if floor else 4.9*scale
    if floor:
        camera.rotation_euler = (0,0,0)
    else:
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    s.camera = camera
    for loc,power,size in [((-3,-4,7),450,5),((4,-1,4),292.5,4),((0,4,6),540,3)]:
        bpy.ops.object.light_add(type='AREA', location=tuple(v*scale for v in loc))
        lamp=bpy.context.object
        lamp.data.energy, lamp.data.size = power*scale*scale,size*scale
        lamp.data.color=(1,.96,.90)
        lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
    return s


def finish(o, name, mat, root=None, layer='body'):
    o.name = 'FC2 ' + name
    o.data.materials.append(MATS[mat] if isinstance(mat,str) else mat)
    o['fc_layer'] = layer
    if root is not None:
        o.parent = root
    return o


def box(name, loc, size, mat='ceramic', root=None, bevel=.035, layer='body'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Fabricated edges','BEVEL')
        b.width,b.segments=bevel,2
        o.modifiers.new('Face normals','WEIGHTED_NORMAL')
    return finish(o,name,mat,root,layer)


def cyl(name, loc, radius, depth, mat='edge', root=None, rot=(0,0,0), layer='body'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=depth,location=loc,rotation=rot)
    return finish(bpy.context.object,name,mat,root,layer)


def empty(name, parent=None):
    o=bpy.data.objects.new('FC2 '+name,None)
    bpy.context.scene.collection.objects.link(o)
    o.parent=parent
    return o


def stencil(text,loc,size,mat='black',root=None,rot=(0,0,0),layer='body'):
    curve=bpy.data.curves.new('FC2 stencil','FONT')
    curve.body=text
    curve.size=size
    curve.align_x='CENTER'
    curve.extrude=.0005
    o=bpy.data.objects.new('FC2 marking '+text,curve)
    bpy.context.scene.collection.objects.link(o)
    o.location,o.rotation_euler=loc,rot
    return finish(o,'marking '+text,mat,root,layer)


def stamp(loc,scale,root=None,layer='body'):
    for x,h in ((-.24,.33),(0,.48),(.24,.33)):
        box('foundry upright',(loc[0]+x*scale,loc[1]+h*scale/2,loc[2]),
            (.12*scale,h*scale,.009),'iron',root,.003,layer)
    box('foundry crossbeam',(loc[0],loc[1]-.07*scale,loc[2]),
        (.60*scale,.09*scale,.01),'rust',root,.002,layer)


def tank():
    s=studio('K6 induction tank')
    with bpy.data.libraries.load(str(MOD/'art/source/tank-prototype/ion-tank.blend'),link=False) as (src,dst):
        dst.scenes=['PvPHit - Ion Tank.001']
    original=dst.scenes[0]
    # Independent geometry, parents and material bindings; no source-scene edits.
    mapping={}
    for old in original.objects:
        if old.type not in ('MESH','EMPTY'):continue
        o=old.copy()
        if old.data:o.data=old.data.copy()
        s.collection.objects.link(o)
        mapping[old]=o
    for old,o in mapping.items():
        o.parent=mapping.get(old.parent)
    hull=next(o for old,o in mapping.items() if old.name.startswith('Hull Pivot'))
    turret=next(o for old,o in mapping.items() if old.name.startswith('Turret Pivot'))
    hull.name,turret.name='FC2 Hull Pivot','FC2 Turret Pivot'
    hull.rotation_euler.z=turret.rotation_euler.z=0
    for old,o in mapping.items():
        if o.type!='MESH':continue
        name=old.name
        oldmat=o.data.materials[0].name
        key=next((v for k,v in [('Slate Blue','ceramic'),('Titanium','edge'),
            ('Graphite','black'),('Orange','team'),('Cyan','cyan')] if k in oldmat),'iron')
        if name.startswith(('Track Pod Armor','Track Shoulder Rail')):key='iron'
        if name.startswith(('Antenna Tip','Rear Energy Vent')):key='rust'
        o.data.materials.clear();o.data.materials.append(MATS[key])
        o['fc_layer']='turret' if o.parent==turret else 'body'
    # Larger panels and recessed seams survive reduction to RTS pixels.
    for side in (-1,1):
        for i in range(5):
            y=-1.08+i*.54
            box('replaceable track crown',(side*1.04,y,1.05),(.55,.47,.10),'ceramic',hull,.04)
            cyl('captive shoulder fastener',(side*1.25,y,1.105),.038,.024,'edge',hull)
        box('front ceramic cheek',(side*.51,-1.10,.98),(.55,.55,.14),'ceramic',hull,.04).rotation_euler.x=.22
        box('oxide identification border',(side*1.04,-.68,1.12),(.36,.61,.025),'rust',hull,.01)
        box('team stripe',(side*1.04,-.68,1.137),(.24,.48,.02),'team',hull,.006)
        cyl('exhaust heat shield',(side*.72,1.06,1.15),.14,.44,'rust',hull)
        cyl('exhaust opening',(side*.72,1.06,1.38),.09,.016,'black',hull)
        box('turret cheek',(side*.65,.12,1.4),(.17,.88,.32),'ceramic',turret,.05,'turret').rotation_euler.y=side*.18
        cyl('capacitor vessel',(side*.43,.74,1.4),.15,.47,'rust',turret,(math.pi/2,0,0),'turret')
        for y in (.54,.92):cyl('capacitor collar',(side*.43,y,1.4),.17,.06,'iron',turret,(math.pi/2,0,0),'turret')
    for y in (-.85,-1.27,-1.63):
        box('accelerator clamp',(0,y,1.46),(.62,.09,.13),'iron',turret,.018,'turret')
    stencil('K6',(0,-.75,1.105),.20,'black',hull)
    stencil('06',(-.31,.08,1.716),.15,'ceramic',turret,layer='turret')
    stamp((.55,.94,1.09),.46,hull)
    ASSETS['tank']={'scene':s,'roots':[hull,turret],'size':128,'frames':[]}
    return s


def factory():
    s=studio('Armor Works',True)
    root=empty('Armor Works anchor')
    box('foundation',(0,0,.16),(5.45,4.55,.32),'iron',root,.06)
    box('production core',(0,.48,1.14),(4.45,3.3,1.95),'iron',root,.08)
    # Side armor leaves the front door as an actual cavity.
    for side in (-1,1):
        for y in (-.55,.62,1.72):
            box('wall cassette',(side*2.24,y,1.16),(.24,1.02,1.78),'ceramic',root,.06)
        box('door pier',(side*1.62,-1.34,1.17),(.59,.71,1.85),'ceramic',root,.07)
        box('gantry foot',(side*1.49,-1.71,.53),(.28,.28,.65),'rust',root,.03)
        box('doorway runner',(side*1.38,-1.72,1.07),(.12,.16,1.54),'edge',root,.014)
        for y in (-1.7,-1.1):box('service apron',(side*1.85,y,.37),(.6,.54,.09),'concrete',root,.012)
    box('bay interior',(0,-1.186,.97),(2.5,.025,1.53),'black',root,.005)
    box('bay header',(0,-1.52,2.12),(3.70,.72,.34),'rust',root,.045)
    box('lintel plating',(0,-1.93,2.09),(2.74,.08,.22),'ceramic',root,.02)
    stencil('ARMOR WORKS',(0,-1.98,2.06),.16,'iron',root,(math.pi/2,0,0))
    for x in (-1.07,1.07):
        box('bay signal',(x,-1.94,1.90),(.18,.045,.075),'cyan',root,.012)
    doors=[]
    for i in range(5):
        o=box('shutter leaf',(0,-1.65,.49+i*.27),(2.60,.08,.25),'edge',root,.015,'door')
        doors.append(o)
        for x in (-.98,0,.98):box('shutter rib',(x,-1.704,.49+i*.27),(.04,.03,.17),'iron',root,.004,'door')
    box('delivery apron',(0,-1.95,.29),(2.78,.68,.11),'concrete',root,.01)
    for x in (-.65,.65):box('guide rail',(x,-1.97,.355),(.085,.7,.023),'edge',root,.004)
    for x in (-1.1,-.82,-.54,-.26,.02,.30,.58,.86,1.14):
        box('threshold warning',(x,-2.25,.36),(.14,.19,.012),'rust',root,.001).rotation_euler.z=.45
    for x in (-1.35,0,1.35):
        box('roof cassette',(x,.48,2.17),(1.23,2.85,.22),'ceramic',root,.045)
        for y in (-.35,.85):box('cassette joint',(x,y,2.289),(1.19,.035,.01),'iron',root,.002)
    box('ownership bed',(-1.36,-.45,2.30),(.85,.60,.032),'rust',root,.015)
    box('ownership plate',(-1.36,-.45,2.32),(.66,.43,.014),'team',root,.006)
    stamp((-.1,-.76,2.30),.95,root)
    stencil('09',(1.35,-.40,2.299),.32,'iron',root)
    fans=[]
    for x in (-1.15,1.15):
        cyl('fan well',(x,1.03,2.35),.49,.16,'iron',root)
        rotor=empty('vent rotor',root);rotor.location=(x,1.03,2.45)
        for angle in (0,math.pi/2):
            blade=box('fan blade',(0,0,0),(.67,.16,.025),'edge',rotor,.008)
            blade.rotation_euler.z=angle
        cyl('fan hub',(0,0,.04),.1,.10,'black',rotor)
        fans.append(rotor)
    cyl('pressure stack',(-1.9,1.55,2.74),.19,1.20,'rust',root)
    cyl('stack lip',(-1.9,1.55,3.34),.25,.10,'iron',root)
    cyl('stack bore',(-1.9,1.55,3.40),.16,.018,'black',root)
    for z in (.8,1.2,1.6):
        cyl('coolant header',(2.43,.38,z),.085,2.3,'rust',root,(math.pi/2,0,0))
    box('service cabinet',(-2.42,-.75,.84),(.45,.60,.9),'iron',root,.04)
    box('cabinet ceramic door',(-2.43,-1.06,.89),(.36,.035,.61),'ceramic',root,.01)
    all_doors=[o for o in s.objects if o.get('fc_layer')=='door']
    ASSETS['factory']={'scene':s,'roots':[root],'size':256,'doors':all_doors,
                       'door_z':{o.name:o.location.z for o in all_doors},'fans':fans}
    return s


def prop(name):
    s=studio(name)
    root=empty(name+' anchor')
    if name=='barrier':
        box('barrier foot',(0,0,.13),(2.75,.73,.26),'concrete',root,.09)
        box('barrier spine',(0,0,.40),(2.61,.38,.55),'ceramic',root,.08)
        for x in (-.85,.85):
            box('oxide band',(x,-.205,.48),(.29,.025,.24),'rust',root,.004)
            box('upper seam',(x,0,.675),(.038,.34,.012),'iron',root,.001)
        for x in (-1.18,1.18):cyl('lifting socket',(x,0,.689),.05,.02,'black',root)
    elif name=='pressure-skid':
        box('skid',(0,0,.13),(2.3,2.3,.26),'iron',root,.04)
        for x in (-.57,.57):
            cyl('pressure bottle',(x,.18,1.0),.41,1.50,'ceramic',root)
            cyl('bottle shoulder',(x,.18,1.8),.32,.15,'rust',root)
            cyl('pressure stem',(x,.18,2.03),.08,.32,'edge',root)
            for z in (.55,1.43):cyl('bottle strap',(x,.18,z),.435,.08,'iron',root)
        cyl('header',(0,-.65,.50),.12,1.6,'rust',root,(0,math.pi/2,0))
        cyl('handwheel',(0,-.81,.73),.22,.06,'edge',root,(math.pi/2,0,0))
        box('meter cabinet',(.80,-.79,.94),(.36,.23,.57),'iron',root,.03)
        box('meter glass',(.80,-.919,1.03),(.22,.022,.14),'cyan',root,.006)
    elif name=='pipe':
        cyl('main service pipe',(0,0,.65),.25,3.4,'rust',root,(0,math.pi/2,0))
        for x in (-1.32,1.32):
            cyl('flange',(x,0,.65),.37,.15,'iron',root,(0,math.pi/2,0))
            box('saddle',(x,0,.28),(.39,.72,.40),'concrete',root,.04)
            for a in range(6):
                t=a*math.tau/6
                cyl('flange bolt',(x-.085,math.sin(t)*.31,.65+math.cos(t)*.31),.045,.035,'edge',root,(0,math.pi/2,0))
        cyl('valve stem',(0,0,1.02),.085,.6,'iron',root)
        cyl('valve wheel',(0,0,1.3),.23,.035,'edge',root)
    else:
        box('pallet',(0,0,.12),(2,1.6,.24),'iron',root,.035)
        for x in (-.49,.49):
            box('replacement armor crate',(x,0,.58),(.87,1.35,.72),'ceramic',root,.07)
            for y in (-.35,.35):box('crate strap',(x,y,.96),(.86,.07,.023),'iron',root,.003)
            box('crate end band',(x,-.69,.65),(.38,.025,.20),'rust',root,.006)
    ASSETS[name]={'scene':s,'roots':[root],'size':128}


def floor(kind):
    s=studio(kind,floor=True)
    root=empty(kind+' anchor')
    box('slab',(0,0,0),(2.03,2.03,.05),'concrete',root,.008)
    if kind=='concrete':
        for x in (-.98,.98):box('expansion joint',(x,0,.028),(.025,2,.007),'black',root,0)
        for y in (-.98,.98):box('expansion joint',(0,y,.028),(2,.025,.007),'black',root,0)
        for x,y in [(-.7,.71),(.71,-.72)]:cyl('slab fastener',(x,y,.032),.027,.008,'edge',root)
    elif kind=='road':
        box('lane paint',(0,0,.031),(.12,.90,.01),'ceramic',root,0)
    elif kind=='drain':
        box('drain recess',(0,0,.03),(.6,2.02,.015),'black',root,.006)
        for y in [i*.17-.935 for i in range(12)]:box('grate',(0,y,.043),(.55,.045,.012),'edge',root,.002)
    elif kind=='hazard':
        for y in [-.7,-.2,.3,.8]:
            box('warning paint',(0,y,.038),(2.5,.17,.012),'rust',root,0).rotation_euler.z=.45
    ASSETS[kind]={'scene':s,'roots':[root],'size':48}


def save_sources():
    SOURCE.mkdir(parents=True,exist_ok=True)
    for name,a in ASSETS.items():
        # Blender writes the chosen scene and its dependencies only.
        bpy.data.libraries.write(str(SOURCE/f'{name}.blend'),{a['scene']},fake_user=True,compress=True)


def capture_rest():
    for a in ASSETS.values():
        a['rest']={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy(),
                    list(o.data.materials) if o.type in ('MESH','FONT') else [])
                   for o in a['scene'].objects}


def build():
    if ASSETS:raise RuntimeError('This module already owns a visual pass; reuse its scenes.')
    OUT.mkdir(parents=True,exist_ok=True)
    palette();tank();factory()
    for name in ('barrier','pressure-skid','pipe','pallet'):prop(name)
    for name in ('concrete','road','drain','hazard'):floor(name)
    capture_rest();save_sources()
    bpy.context.window.scene=ASSETS['tank']['scene']
    return {name:{'scene':a['scene'].name,'objects':len(a['scene'].objects)} for name,a in ASSETS.items()}


def visibility(a,layer='all',facing=0,step=0):
    s=a['scene']
    for o in s.objects:
        loc,rot,scale,mats=a['rest'][o.name]
        o.location,o.rotation_euler,o.scale=loc,rot,scale
        if o.type in ('MESH','FONT'):
            o.data.materials.clear()
            for mat in mats:o.data.materials.append(mat)
    for root in a['roots']:root.rotation_euler.z=facing*math.tau/32
    display_layer=layer.removeprefix('damaged-')
    for o in s.objects:
        if o.type in ('MESH','FONT'):
            group=o.get('fc_layer','body')
            o.hide_render=(group!=display_layer) if display_layer in ('body','turret','door') else False
            if layer=='wreck' or (layer.startswith('damaged-') and
                    any(x in o.name for x in ('roof cassette','wall cassette','shutter leaf','bay header'))):
                o.data.materials.clear();o.data.materials.append(MATS['soot'])
    if layer=='wreck':
        a['roots'][0].scale.z=.72
        a['roots'][1].location.z=-.42
        a['roots'][1].rotation_euler.x=.16
    if layer=='make':
        a['roots'][0].scale.z=.18+.205*step
    if 'doors' in a:
        # A segmented shutter retracts within the opening, never above the roof.
        door_step=step if display_layer=='door' else 0
        for o in a['doors']:
            factor=1-door_step*.24
            o.location.z=1.76+(a['door_z'][o.name]-1.76)*factor
            o.scale.z=factor
        for rotor in a['fans']:rotor.rotation_euler.z=step*math.pi/8


def render_jobs(mode):
    jobs=[]
    def job(asset,layer,index,facing=0,step=0,size=None):
        jobs.append((asset,layer,index,facing,step,size))
    if mode=='previews':
        job('tank','all',0,4,size=768)
        job('factory','all',0,size=768)
        for name in ('barrier','pressure-skid','pipe','pallet'):job(name,'all',0,size=384)
    elif mode=='sprites':
        for layer in ('body','turret','wreck'):
            for f in range(32):job('tank',layer,f,f)
        for f in range(0,32,4):job('tank','all',f,f)
        for layer in ('body','damaged-body'):
            for i in range(4):job('factory',layer,i,step=i)
        for layer in ('door','damaged-door','make'):
            for i in range(5):job('factory',layer,i,step=i)
        for name in ASSETS:
            if name not in ('tank','factory'):job(name,'all',0)
    else:raise ValueError(mode)
    return jobs


def start_render(mode):
    if STATE.get('running'):raise RuntimeError('A visual-pass render is already running')
    JOBS[:]=render_jobs(mode)
    STATE.clear();STATE.update(running=True,mode=mode,total=len(JOBS),done=0)
    def tick():
        try:
            asset,layer,index,facing,step,size=JOBS.pop(0)
            a=ASSETS[asset];s=a['scene']
            bpy.context.window.scene=s
            visibility(a,layer,facing,step)
            if mode=='previews':
                for o in s.objects:
                    if o.type in ('MESH','FONT'):
                        for slot in o.material_slots:
                            if slot.material==MATS['team']:slot.material=MATS['review']
            s.render.resolution_x=s.render.resolution_y=size or a['size']
            path=OUT/('previews' if mode=='previews' else 'frames')/asset/layer/f'{index:02d}.png'
            path.parent.mkdir(parents=True,exist_ok=True)
            s.render.filepath=str(path)
            bpy.ops.render.render(write_still=True,scene=s.name)
            STATE['done']+=1
            STATE['last']=str(path)
            STATE['running']=bool(JOBS)
            (OUT/'render-status.json').write_text(json.dumps(STATE,indent=2)+'\n')
            if JOBS:return .15
            for a in ASSETS.values():
                visibility(a)
                a['scene'].render.resolution_x=a['scene'].render.resolution_y=a['size']
            bpy.context.window.scene=ASSETS['tank']['scene']
        except Exception:
            STATE.update(running=False,error=traceback.format_exc())
            (OUT/'render-status.json').write_text(json.dumps(STATE,indent=2)+'\n')
        return None
    bpy.app.timers.register(tick,first_interval=.5)
    return dict(STATE)
