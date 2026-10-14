"""Render 32 hull/turret facings and eight assembled views without blocking MCP."""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
scene = bpy.context.scene
body_root = next(o for o in scene.objects if o.name.startswith('Hull Pivot'))
turret_root = next(o for o in scene.objects if o.name.startswith('Turret Pivot'))
body, turret = list(body_root.children), list(turret_root.children)
camera = scene.camera
original_camera = camera.matrix_world.copy()
original_scale = camera.data.ortho_scale
camera.location = (0, -8, 8)
camera.rotation_euler = (Vector((0, 0, 0.75))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.ortho_scale = 4.9
scene.render.resolution_x = scene.render.resolution_y = 128
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = 16
jobs = [(layer, i) for layer in ('body', 'turret') for i in range(32)]
jobs += [('assembled', i) for i in range(0, 32, 4)]
for layer in ('body', 'turret', 'assembled'):
    (OUT / layer).mkdir(exist_ok=True)
state = {'completed': 0, 'total': len(jobs), 'status': 'rendering'}

def render_next():
    try:
        while state['completed'] < len(jobs):
            layer, facing = jobs[state['completed']]
            if not (OUT / layer / f'{facing:02d}.png').exists():
                break
            state['completed'] += 1
        if state['completed'] == len(jobs):
            for obj in body + turret:
                obj.hide_render = False
            body_root.rotation_euler.z = turret_root.rotation_euler.z = 0
            camera.matrix_world = original_camera
            camera.data.ortho_scale = original_scale
            scene.render.resolution_x = scene.render.resolution_y = 768
            scene.render.filepath = str(OUT / 'preview.png')
            state['status'] = 'complete'
            (OUT / 'render-status.json').write_text(json.dumps(state, indent=2))
            return None
        layer, facing = jobs[state['completed']]
        for obj in body:
            obj.hide_render = layer == 'turret'
        for obj in turret:
            obj.hide_render = layer == 'body'
        body_root.rotation_euler.z = turret_root.rotation_euler.z = facing * math.tau / 32
        scene.render.filepath = str(OUT / layer / f'{facing:02d}.png')
        bpy.ops.render.render(write_still=True)
        state['completed'] += 1
        (OUT / 'render-status.json').write_text(json.dumps(state, indent=2))
        return .1
    except Exception as exc:
        state.update(status='error', error=str(exc))
        (OUT / 'render-status.json').write_text(json.dumps(state, indent=2))
        return None

(OUT / 'render-status.json').write_text(json.dumps(state, indent=2))
bpy.app.timers.register(render_next, first_interval=.5)
