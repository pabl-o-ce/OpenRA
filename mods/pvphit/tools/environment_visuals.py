"""Owned environment scenes; run through Blender MCP's live or background tool.

build() refuses to replace saved sources. export() loads saved editable sources
without modifying them. Neither operation saves over the active Blender file.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import bpy

MOD = Path(__file__).resolve().parents[1]
SOURCE = MOD/'art/source/environment'
OUT = MOD/'art/environment/props'
ASSETS = ('wall-a', 'wall-b', 'wall-c', 'wall-d', 'pipe-ew', 'pipe-ns',
          'pipe-elbow', 'pipe-end', 'extraction-skid', 'broken-manifold')


def helper():
    spec = importlib.util.spec_from_file_location('fc_environment_helpers', MOD/'tools/refine_visuals.py')
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
    h.palette()
    return h


def build(assets=ASSETS):
    SOURCE.mkdir(parents=True, exist_ok=True)
    if any((SOURCE/(name+'.blend')).exists() for name in assets):
        raise RuntimeError('Existing environment sources: use export(), never rebuild over edits')
    old = bpy.context.window.scene
    h = helper()
    try:
        for name in assets:
            s = h.studio('Environment '+name)
            s['fc_environment'] = name
            s.cycles.seed = 0
            root = h.empty('Environment '+name+' ground anchor')
            if name.startswith('wall'):
                # 24 native pixels per occupied cell; low, grounded silhouettes.
                h.box('buried iron footing', (0,0,.08), (1.72,.72,.16), 'iron', root)
                i = ord(name[-1])-ord('a')
                for k in range(3):
                    height = (.49,.66,.42,.58)[(k+i)%4]
                    h.box('fractured refractory section', ((k-1)*.54,0,height/2+.12),
                          (.51,.55,height), 'ceramic', root, .035)
                h.box('oxide service band', (0,-.29,.24), (1.58,.035,.09), 'rust', root, .005)
                for x in (-.64,.64):
                    h.cyl('exposed fixing', (x,0,.69), .025,.28,'edge',root)
                if i % 2: root.rotation_euler.z = math.pi/2
            elif name.startswith('pipe'):
                for x in (-.58,.58):
                    h.box('flush support shoe',(x,0,.04),(.24,.52,.08),'concrete',root)
                h.cyl('low pressure pipe',(0,0,.19),.13,1.65,'rust',root,(0,math.pi/2,0))
                for x in (-.65,.65):
                    h.cyl('pressure collar',(x,0,.19),.18,.10,'iron',root,(0,math.pi/2,0))
                if name == 'pipe-ns': root.rotation_euler.z = math.pi/2
                if name == 'pipe-elbow':
                    h.cyl('branch',(0,.36,.19),.13,.72,'rust',root,(math.pi/2,0,0))
                    h.cyl('branch collar',(0,.66,.19),.18,.08,'iron',root,(math.pi/2,0,0))
                if name == 'pipe-end':
                    h.cyl('blank flange',(.83,0,.19),.22,.08,'edge',root,(0,math.pi/2,0))
            else:
                h.box('recessed machinery bed',(0,0,.08),(1.70,1.26,.16),'iron',root)
                for x in (-.48,.48):
                    h.cyl('insulated collector',(x,0,.44),.24,.66,'rust',root)
                    h.cyl('ceramic head',(x,0,.79),.27,.12,'ceramic',root)
                    h.cyl('dark aperture',(x,0,.86),.17,.02,'black',root)
                h.box('cross manifold',(0,.39,.36),(1.42,.24,.24),'edge',root)
                h.box('service enclosure',(0,-.42,.31),(.54,.24,.44),'ceramic',root)
                if name == 'broken-manifold':
                    for o in list(s.objects):
                        if o.parent == root and o.location.x > .3:
                            o.rotation_euler.y += .55
                            o.location.z -= .16
                else:
                    h.box('recessed amber gauge',(0,-.55,.36),(.07,.02,.05),'amber',root,.002)
            bpy.data.libraries.write(str(SOURCE/(name+'.blend')), {s}, fake_user=True)
    finally:
        bpy.context.window.scene = old
    return {'saved': list(assets)}


def export(assets=ASSETS):
    OUT.mkdir(parents=True, exist_ok=True)
    old = bpy.context.window.scene
    records = {}
    try:
        for name in assets:
            source = SOURCE/(name+'.blend')
            with bpy.data.libraries.load(str(source), link=False) as (src,dst):
                dst.scenes = src.scenes
            s = next(s for s in dst.scenes if s.get('fc_environment') == name)
            bpy.context.window.scene = s
            path = OUT/(name+'.png')
            s.render.filepath = str(path)
            bpy.ops.render.render(write_still=True, scene=s.name)
            records[name] = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                             'png_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            bpy.context.window.scene = old
            # Only this export's temporary scene; never the live user's scene.
            bpy.data.scenes.remove(s)
    finally:
        bpy.context.window.scene = old
    # Per-asset receipts cannot accidentally certify an unrendered batch.
    for name, record in records.items():
        (OUT/(name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
    return records
