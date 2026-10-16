"""FC6 transient weapon artwork. Execute build/load_source and render through MCP.

All particles are baked artwork, never actors. Saved sources are loaded for
subsequent exports; build refuses to overwrite a hand-edited source.
"""
from pathlib import Path
import importlib.util
import json
import math
import random
import traceback
import bpy

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fc_effect_helpers',HERE/'refine_visuals.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
OUT=b.MOD/'art/motion-effects'
SOURCE=b.MOD/'art/source/effects/weapon-effects.blend'
STATE={}
SCENE=None
SPECS={}
for weapon,color,size in [('scout',(1,.49,.12),.25),('tank',(.05,.65,1),.43),('siege',(1,.68,.30),.58)]:
    SPECS[weapon+'-muzzle']=(6,1,size,color,'muzzle')
    SPECS[weapon+'-impact']=(10,1,size*1.8,color,'impact')
    SPECS[weapon+'-shot']=(1,32,size*.33,color,'shot')
for vehicle,size in [('scout',.65),('hauler',.85),('tank',1),('siege',1)]:
    SPECS[vehicle+'-death']=(12,1,size,(1,.48,.12),'death')


def build():
    global SCENE
    if SOURCE.exists(): raise FileExistsError('Use load_source() to preserve edits')
    previous=bpy.context.window.scene
    try:
        b.palette();SCENE=b.studio('FC6 transient weapon effects')
        SCENE.cycles.seed=0
        for i in range(25):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(0,0,.75))
            o=bpy.context.object;o.name=f'FC6 effect particle {i:02d}';o['fc_particle']=i
            o.data.materials.append(b.material(f'FC6 effect particle {i:02d}',(.5,.5,.5),0,.95))
        SOURCE.parent.mkdir(parents=True,exist_ok=True)
        bpy.data.libraries.write(str(SOURCE),{SCENE},fake_user=True,compress=True)
    finally: bpy.context.window.scene=previous
    return SCENE.name


def load_source():
    global SCENE
    if SCENE: raise RuntimeError('Already loaded')
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst): dst.scenes=src.scenes
    if len(dst.scenes)!=1: raise ValueError('Expected one effects scene')
    SCENE=dst.scenes[0]
    return SCENE.name


def pose(name,step,facing):
    count,facings,size,color,kind=SPECS[name];phase=step/max(1,count-1)
    rng=random.Random(600)
    for o in SCENE.objects:
        if 'fc_particle' not in o: continue
        i=o['fc_particle'];o.hide_render=False
        angle=rng.random()*math.tau;radius=rng.uniform(.4,1);lift=rng.uniform(.4,1.4)
        o.rotation_euler=(0,0,facing*math.tau/32)
        if kind=='shot':
            o.hide_render=i>1;o.location=(0,0,.75)
            o.scale=(size*.55,size*2,size*.55) if i==0 else (size*.25,size*1.5,size*.25)
            c=color if name!='siege-shot' else ((.22,.24,.24) if i==0 else (1,.45,.1));alpha=1
        elif i==0:
            o.hide_render=step>2;o.location=(0,0,.75)
            r=size*(1-phase)*(.8 if kind=='muzzle' else .65);o.scale=(r,r,r*.75)
            c=tuple(min(1,v+.4) for v in color);alpha=1
        elif i<7:
            o.hide_render=phase>.55;r=size*(.08+.10*(1-phase));spread=size*(.3+phase*1.5)*radius
            o.location=(math.cos(angle)*spread,math.sin(angle)*spread,.75+phase*size*.4)
            o.scale=(r,r,r*2);c=color;alpha=max(0,1-phase*1.8)
        else:
            o.hide_render=step==0 or (kind=='muzzle' and i>12)
            spread=size*(.25+phase)*radius
            o.location=(math.cos(angle)*spread,math.sin(angle)*spread,.65+size*phase*lift)
            r=size*(.12+phase*.18);o.scale=(r,r,r*.8)
            c=(.18,.16,.13) if kind=='muzzle' else (.24,.21,.17);alpha=(1-phase)*.65
            if kind=='death' and i<11:
                # Small dark fragments settle into the same short effect lifetime.
                o.scale=(.045,.065,.035);c=(.08,.09,.09)
                o.location.z=.75+math.sin(phase*math.pi)*size*.8
        mat=o.data.materials[0];p=mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*c,1);p.inputs['Alpha'].default_value=alpha
        p.inputs['Emission Color'].default_value=(*c,1)
        p.inputs['Emission Strength'].default_value=1.5 if i<7 else 0
    bpy.context.view_layer.update()


def start_render():
    if SCENE is None or bpy.app.is_job_running('RENDER') or STATE.get('running'): raise RuntimeError('Load source; wait for renders')
    queue=[(name,k,f) for name,(count,facings,*_) in SPECS.items() for f in range(facings) for k in range(count)]
    previous=bpy.context.window.scene
    STATE.clear();STATE.update(running=True,done=0,total=len(queue))
    OUT.mkdir(parents=True,exist_ok=True)
    def status():
        p=OUT/'render-status.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(STATE,indent=2)+'\n');t.replace(p)
    def tick():
        try:
            name,k,f=queue.pop(0);bpy.context.window.scene=SCENE;pose(name,k,f)
            count=SPECS[name][0];p=OUT/'frames'/name/f'{f*count+k:03d}.png'
            p.parent.mkdir(parents=True,exist_ok=True);SCENE.render.filepath=str(p)
            bpy.ops.render.render(write_still=True,scene=SCENE.name)
            STATE.update(done=STATE['done']+1,last=str(p))
            if queue: status();return .05
            STATE['running']=False;bpy.context.window.scene=previous;status()
        except Exception:
            STATE.update(running=False,error=traceback.format_exc());bpy.context.window.scene=previous;status()
        return None
    status();bpy.app.timers.register(tick,first_interval=.5)
    return dict(STATE)
