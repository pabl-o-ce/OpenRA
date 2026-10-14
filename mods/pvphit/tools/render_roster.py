"""Original Directorate blockout models and reproducible directional sprites.

blender -noaudio --background --python mods/pvphit/tools/render_roster.py
Uses an isolated scene; saves editable models under art/source/roster/.
"""
from pathlib import Path
import math
import sys
import bpy
from mathutils import Vector

MOD = Path(__file__).resolve().parents[1]
OUT = MOD / 'art/roster'
SOURCE = MOD / 'art/source/roster'
SOURCE.mkdir(parents=True, exist_ok=True)

def material(name, color, metal=0, emission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    s = mat.node_tree.nodes.get('Principled BSDF')
    s.inputs['Base Color'].default_value = (*color, 1)
    s.inputs['Metallic'].default_value = metal
    s.inputs['Roughness'].default_value = .65
    s.inputs['Emission Color'].default_value = (*color, 1)
    s.inputs['Emission Strength'].default_value = emission
    return mat

armor = material('Refractory ceramic', (.32, .30, .25), .15)
iron = material('Structural iron', (.20, .23, .24), .5)
dark = material('Graphite machinery', (.045, .05, .055), .3)
rust = material('Oxide insulation', (.25, .065, .035))
team = material('Identification green', (.025, .8, .055))
light = material('Capacitor cyan', (.015, .48, .62), .1, .7)
objects, turret, braces = [], [], []

def box(name, loc, size, mat=armor):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new('Machined edges', 'BEVEL')
    bevel.width, bevel.segments = .055, 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    obj.data.materials.append(mat)
    objects.append(obj)
    return obj

def cyl(name, loc, radius, depth, mat=iron, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    objects.append(obj)
    return obj

def studio(name, building=False):
    global objects, turret, braces
    objects, turret, braces = [], [], []
    bpy.ops.scene.new(type='NEW')
    s = bpy.context.scene
    s.name = 'Directorate - ' + name
    s.render.engine = 'CYCLES'
    s.cycles.device, s.cycles.samples, s.cycles.use_denoising = 'CPU', 16, True
    s.render.threads_mode, s.render.threads = 'FIXED', 4
    s.render.film_transparent = True
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGBA'
    s.render.resolution_x = s.render.resolution_y = 256 if building else 128
    s.render.resolution_percentage = 100
    s.view_settings.view_transform, s.view_settings.look = 'Standard', 'None'
    s.view_settings.exposure = -.7
    s.world = bpy.data.worlds.new(name + ' studio')
    s.world.use_nodes = True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.3,.3,.3,1)
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35
    target = Vector((0,0,1.5 if building else .75))
    bpy.ops.object.camera_add(location=(0,-16,16) if building else (0,-8,8))
    camera = bpy.context.object
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type, camera.data.ortho_scale = 'ORTHO', 9.8 if building else 4.9
    s.camera = camera
    scale = 2 if building else 1
    for loc, power, size in [((-3,-4,7),450,5),((4,-1,4),292.5,4),((0,4,6),540,3)]:
        bpy.ops.object.light_add(type='AREA', location=tuple(v*scale for v in loc))
        lamp = bpy.context.object
        lamp.data.energy, lamp.data.size = power*scale*scale, size*scale
        lamp.data.color = (1,.96,.90)
        lamp.rotation_euler = (target-lamp.location).to_track_quat('-Z','Y').to_euler()
    return s

def chassis(length=2.5, width=1.9, tracks=True):
    box('Hull', (0,0,.55), (width*.8,length,.55), iron)
    for side in (-1,1):
        x=side*width*.48
        if tracks:
            box('Track pod', (x,0,.35), (.5,length+.2,.55), dark)
            box('Track guard', (x,0,.65), (.55,length,.16))
            for i in range(9):
                box('Tread rib', (x+side*.25,-length*.43+i*length*.107,.36), (.06,.12,.4), iron)
        else:
            for y in (-.7,0,.7):
                cyl('Armored wheel', (x,y,.35), .31,.25,dark,(0,math.pi/2,0))
    box('Front identification', (0,-length*.32,.86), (.65,.42,.04), team)

def vehicle(name):
    if name == 'scout':
        chassis(1.8,1.45,False)
        box('Sloped cab', (0,.1,.91), (.95,.85,.35))
        start=len(objects)
        cyl('Sensor turret', (0,0,1.17), .3,.22)
        box('Light gun', (0,-.53,1.2), (.10,.85,.12), dark)
        box('Sensor face', (.2,-.18,1.28), (.15,.12,.09), light)
        turret.extend(objects[start:])
        cyl('Relay mast', (-.4,.45,1.4), .025,.8,dark)
    elif name == 'hauler':
        chassis(2.8,2.1)
        box('Sealed cab', (0,-.85,1.05), (1.35,.65,.7))
        box('Cab glass', (0,-1.19,1.14), (.9,.025,.16), light)
        box('Slag bed', (0,.45,.93), (1.6,1.6,.12), rust)
        for x in (-.8,.8): box('Bin wall', (x,.45,1.16), (.13,1.65,.55), iron)
        box('Bin back', (0,1.24,1.16), (1.6,.13,.55), iron)
        box('Collection blade', (0,-1.53,.45), (1.8,.2,.55), rust)
        for x in (-.55,0,.55): cyl('Slag block', (x,.4,1.13), .24,.27,rust)
    else:
        chassis(2.65,2.05)
        cyl('Mortar turntable', (0,.1,1), .68,.25,dark)
        cyl('Pressure mortar', (0,.1,1.55), .40,.95,iron)
        cyl('Muzzle rim', (0,.1,2.05), .45,.13,armor)
        cyl('Bore', (0,.1,2.12), .31,.025,dark)
        for side in (-1,1):
            for y in (-.85,.85):
                obj=box('Deployable stabilizer', (side*.9,y,.40), (.45,.3,.20), rust)
                braces.append((obj,side))
        box('Charge indicator', (0,-.8,1.01), (.6,.15,.05), light)

def structure(name):
    if name == 'pipe':
        cyl('Insulated pipe', (0,0,.5), .35,3.2,rust,(0,math.pi/2,0))
        for x in (-1.1,1.1):
            cyl('Pipe flange',(x,0,.5),.45,.15,iron,(0,math.pi/2,0))
            box('Support',(x,0,.18),(.35,.8,.3),dark)
        return
    elif name == 'ruin':
        box('Ruined slab',(0,0,.15),(3.8,2.9,.3),dark)
        for x,h in ((-1.5,1.8),(-.2,.6),(1.2,1.2)):
            box('Broken blast wall',(x,.65,h/2),(.7,1.3,h),iron)
        box('Fallen plate',(.3,-.7,.3),(1.9,.9,.25),rust).rotation_euler.z=.35
        return
    elif name == 'generator':
        box('Foundation', (0,0,.2), (3.4,3.1,.4), dark)
        for x in (-.8,.8):
            cyl('Pressure vessel', (x,0,1.2), .63,1.85,armor)
            cyl('Heat cap', (x,0,2.2), .72,.22,rust)
            cyl('Stack', (x,.2,2.65), .22,.75,dark)
        box('Service cabinet', (0,-1.1,.9), (1.1,.5,1.15), iron)
    elif name == 'hq':
        box('Fortress plinth', (0,0,.35), (5.2,4.5,.7), dark)
        box('Command bunker', (0,.2,1.2), (3.8,3.2,1.4))
        for side in (-1,1):
            box('Blast buttress', (side*2.15,.3,1), (.5,3.7,1.6), iron)
        box('Command tower', (.8,.7,2.35), (1.25,1.5,1.4))
        box('Observation slit', (0,-1.43,1.5), (2.2,.08,.18), light)
        cyl('Radio mast', (.8,.7,3.6), .07,1.6,dark)
    elif name == 'processor':
        box('Dock foundation', (0,0,.2), (5.2,4.5,.4), dark)
        box('Furnace', (-.9,.5,1.3), (2.6,2.6,2.1))
        cyl('Cyclone separator', (1.45,.65,1.35), .65,2.25,rust)
        cyl('Chimney', (-.9,.6,2.9), .35,1.25,dark)
        box('Delivery ramp', (0,-1.5,.34), (2.4,1.4,.22), iron)
        box('Intake glow', (0,-.89,.75), (1.4,.07,.35), light)
    elif name == 'factory':
        box('Factory foundation', (0,0,.25), (5.4,4.6,.5), dark)
        box('Production hall', (0,.5,1.3), (4.7,3.2,2.1))
        box('Armored shutter', (0,-1.13,1), (2.4,.1,1.5), dark)
        for x in (-1.5,1.5): box('Door reinforcement', (x,-1.22,1.1), (.28,.28,1.9), iron)
        box('Gantry crossbeam', (0,-1.2,2.2), (4.3,.4,.4), rust)
        for x in (-1.3,0,1.3): box('Roof heat exchanger', (x,.4,2.55), (.7,1.9,.35), iron)
    else:
        box('Relay foundation', (0,0,.2), (3.4,3.1,.4), dark)
        box('Relay housing', (0,.15,1.1), (2.3,2.1,1.7))
        cyl('Meter head', (0,.15,2.2), .55,.65,iron)
        cyl('Antenna', (0,.15,3.1), .06,1.3,dark)
        box('Service hatch', (0,-1,.65), (1.2,.1,.8), rust)
    roof = {'hq': (0,-.5,1.92), 'factory': (0,-.75,2.43),
            'processor': (-.9,-.25,2.38), 'facility': (0,-.5,1.98),
            'generator': (0,-1.1,1.51)}[name]
    box('Ownership panel', roof, (.85,.50,.045), team)
    # Repeated physical bands provide a common industrial construction language.
    for i in range(3): box('Directorate insignia', (-.38+i*.27,-1.18,1.91+i*.06), (.16,.06,.13), iron)

def render_asset(name, building=False):
    s=studio(name,building)
    structure(name) if building else vehicle(name)
    root=bpy.data.objects.new('Ground anchor',None)
    s.collection.objects.link(root)
    for o in objects:o.parent=root
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / f'{name}.blend'))
    dest=OUT/name
    dest.mkdir(parents=True,exist_ok=True)
    def frame(layer, i, facing=0):
        root.rotation_euler.z=facing*math.tau/32
        for o in objects:o.hide_render=(o in turret) if layer=='body' else (o not in turret) if layer=='turret' else False
        p=dest/layer
        p.mkdir(exist_ok=True)
        s.render.filepath=str(p/f'{i:03d}.png')
        bpy.ops.render.render(write_still=True)
    if building:
        frame('idle',0)
        for i in range(5):
            root.scale.z=(i+1)/5
            frame('make',i)
        root.scale.z=1
        for o in objects:
            if o.data.materials[0]==armor:o.data.materials[0]=rust
        frame('damaged',0)
    else:
        for i in range(32):frame('body',i,i)
        if turret:
            for i in range(32):frame('turret',i,i)
        frame('icon',0,4)
        if name=='siege':
            for facing in range(32):
                for step in range(5):
                    for o,side in braces:
                        o.location.x=side*(.9+step*.14)
                        o.location.z=.40-step*.04
                    frame('deploy',facing*5+step,facing)
            for i in range(32):frame('deployed',i,i)
        for o in objects:o.data.materials[0]=dark
        for i in range(32):frame('wreck',i,i)

names = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ('scout','generator','hauler','siege','hq','processor','factory','facility','pipe','ruin')
for name in names:
    render_asset(name,name not in ('scout','hauler','siege'))
