"""Render the preserved prototype in an isolated background Blender process.

blender --background --python mods/pvphit/tools/render_tank.py -- [--preview]
The original scene is never saved over. Outputs use a common ground anchor.
"""
from pathlib import Path
import math
import sys
import bpy
from mathutils import Vector

MOD = Path(__file__).resolve().parents[1]
OUT = MOD / 'art' / 'tank'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(MOD / 'art/source/tank-prototype/ion-tank.blend'))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_percentage = 100
scene.render.resolution_x = scene.render.resolution_y = 128
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.7
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.3, .3, .3, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35

# Reserve green exclusively for player identification. Hue shifts preserve shading.
colors = {
    'Armor - Slate Blue': ((.32, .30, .25), .15, .65),
    'Armor - Titanium': ((.20, .23, .24), .5, .55),
    'Tracks - Graphite': ((.045, .05, .055), .3, .8),
    'Team Panels - Orange Prototype': ((.025, .8, .055), .0, .7),
    'Energy - Cyan': ((.015, .48, .62), .1, .35),
}
for name, (color, metal, rough) in colors.items():
    mat = bpy.data.materials[name]
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = rough
    if name == 'Energy - Cyan':
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = .7

for obj in scene.objects:
    if obj.type == 'LIGHT':
        obj.data.color = (1, .96, .90)
        obj.data.energy *= .45

body_root = next(o for o in scene.objects if o.name.startswith('Hull Pivot'))
turret_root = next(o for o in scene.objects if o.name.startswith('Turret Pivot'))
body, turret = list(body_root.children), list(turret_root.children)
camera = scene.camera
camera.location = (0, -8, 8)
camera.rotation_euler = (Vector((0, 0, .75)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 4.9

def render(layer, facing):
    for obj in body:
        obj.hide_render = layer == 'turret'
    for obj in turret:
        obj.hide_render = layer in ('body', 'wreck')
    body_root.rotation_euler.z = turret_root.rotation_euler.z = facing * math.tau / 32
    path = OUT / layer / f'{facing:02d}.png'
    path.parent.mkdir(exist_ok=True)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)

if '--preview' in sys.argv:
    render('assembled', 4)
else:
    for layer in ('body', 'turret'):
        for facing in range(32):
            render(layer, facing)
    for facing in range(0, 32, 4):
        render('assembled', facing)
    # A scorched hull is the first wreck state; retain recognizable track pods.
    for name in colors:
        shader = bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (.06, .045, .035, 1)
        shader.inputs['Emission Strength'].default_value = 0
    for facing in range(32):
        render('wreck', facing)
