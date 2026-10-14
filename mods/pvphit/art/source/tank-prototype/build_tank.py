"""Build an original sci-fi tank in a separate Blender scene. Run via Blender MCP."""
from pathlib import Path
import math
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.scene.new(type='NEW')
scene = bpy.context.scene
scene.name = 'PvPHit - Ion Tank'
engines = scene.render.bl_rna.properties['engine'].enum_items.keys()
scene.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in engines else 'BLENDER_EEVEE_NEXT'
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_percentage = 100
scene.render.resolution_x = scene.render.resolution_y = 768
scene.render.fps = 24
scene.view_settings.view_transform = 'Standard'
scene.world = bpy.data.worlds.new('Ion Tank Studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.15, .19, .25, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
body, turret = [], []

def material(name, color, metallic=0, roughness=.4, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat

armor = material('Armor - Slate Blue', (.12, .20, .28), .65)
edge = material('Armor - Titanium', (.34, .44, .51), .7)
dark = material('Tracks - Graphite', (.035, .055, .07), .25)
cyan = material('Energy - Cyan', (.03, .7, 1), .35, .25, 2)
team = material('Team Panels - Orange Prototype', (1, .31, .045), .25)

def finish(obj, name, mat, group):
    obj.name = name
    obj.data.materials.append(mat)
    group.append(obj)
    return obj

def box(name, loc, dims, mat, group, bevel=.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Armor bevels', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return finish(obj, name, mat, group)

def cylinder(name, loc, radius, depth, mat, group, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth,
                                      location=loc, rotation=rotation)
    return finish(bpy.context.object, name, mat, group)

# Forward is -Y. Broad track pods keep the silhouette readable at RTS scale.
box('Hull - Lower', (0, 0, .49), (1.65, 2.65, .48), dark, body, .12)
box('Hull - Upper', (0, -.06, .83), (1.65, 2.28, .49), armor, body, .18)
box('Front Armor', (0, -1.18, .78), (1.53, .25, .36), edge, body, .06)
for side in (-1, 1):
    x = side * 1.04
    box('Track Pod', (x, .05, .48), (.58, 2.93, .64), dark, body, .16)
    box('Track Pod Armor', (x, .02, .85), (.64, 2.7, .32), armor, body, .10)
    box('Track Shoulder Rail', (x, .04, 1.03), (.42, 2.49, .08), edge, body, .025)
    for i in range(13):
        y = -1.22 + i * .2
        box('Tread Link', (x, y, .21), (.6, .13, .13), edge, body, .018)
        box('Outer Tread Rib', (x + side * .3, y, .49), (.045, .10, .37), edge, body, .012)
    for y in (-1.04, -.52, 0, .52, 1.04):
        cylinder('Track Wheel', (x + side * .30, y, .50), .18, .05, dark, body,
                 (0, math.pi/2, 0))
    box('Team Stripe', (x, -.68, 1.078), (.29, .67, .025), team, body, .015)
    box('Front Light', (x, -1.365, .86), (.34, .035, .09), cyan, body, .015)
    box('Rear Energy Vent', (x, 1.37, .70), (.27, .045, .14), cyan, body, .02)
    for i in range(4):
        box('Engine Grille', (side * .53, .83+i*.09, 1.09), (.38, .035, .025), dark, body, .005)

cylinder('Turret Bearing', (0, .12, 1.10), .60, .16, dark, turret)
box('Turret Main Armor', (0, .16, 1.38), (1.23, 1.22, .46), armor, turret, .15)
box('Turret Upper Plate', (0, .26, 1.65), (1.02, .86, .10), edge, turret, .045)
box('Turret Team Panel', (0, .28, 1.713), (.63, .52, .025), team, turret, .025)
box('Cannon Mantlet', (0, -.48, 1.40), (.60, .37, .38), edge, turret, .07)
box('Cannon Core', (0, -1.20, 1.43), (.26, 1.24, .20), dark, turret, .025)
for side in (-1, 1):
    box('Ion Accelerator Rail', (side*.22, -1.22, 1.47), (.14, 1.30, .18), edge, turret, .025)
    box('Ion Energy Strip', (side*.22, -1.22, 1.57), (.065, 1.13, .02), cyan, turret, .006)
box('Cannon Muzzle', (0, -1.89, 1.44), (.57, .18, .31), armor, turret, .045)
box('Cannon Aperture', (0, -1.988, 1.44), (.32, .015, .12), cyan, turret, .015)
box('Optical Sensor', (.42, -.30, 1.69), (.19, .22, .09), dark, turret, .02)
box('Sensor Lens', (.42, -.417, 1.69), (.12, .018, .045), cyan, turret, .005)
cylinder('Antenna', (-.48, .61, 1.91), .016, .66, dark, turret)
cylinder('Antenna Tip', (-.48, .61, 2.25), .03, .05, cyan, turret)

# Separate rotation roots; turret render shares the hull's ground anchor.
def root(name, objects):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    for child in objects:
        child.parent = obj
    return obj

body_root = root('Hull Pivot', body)
turret_root = root('Turret Pivot', turret)

def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(5, -7, 6))
camera = bpy.context.object
camera.name = 'Orthographic Sprite Camera'
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.6
aim(camera, (0, -.10, .75))
scene.camera = camera
for name, loc, power, size, color in [
    ('Key', (-3,-4,7), 1000, 5, (1,.90,.79)),
    ('Fill', (4,-1,4), 650, 4, (.66,.83,1)),
    ('Rim', (0,4,6), 1200, 3, (.38,.70,1)),
]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy, light.data.shape, light.data.size = power, 'DISK', size
    light.data.color = color
    aim(light, (0,0,.6))

scene.render.filepath = str(OUT / 'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'ion-tank.blend'))
