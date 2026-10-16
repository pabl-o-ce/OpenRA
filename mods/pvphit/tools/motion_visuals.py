"""FC6 saved-source animation adapter. Import through Blender MCP.

load_sources() never rebuilds or saves a source. prepare() adds editable motion
properties to owned copies; save_sources() explicitly saves those copies.
start_render('samples', ['hauler']) precedes the full sprites export.
"""
from pathlib import Path
import importlib.util
import math
import json
import hashlib
import traceback
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fc_motion_base', HERE/'vehicle_visuals.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
MOD = v.b.MOD
OUT = MOD/'art/motion'
ASSETS = v.ASSETS
STATE = {}
LAYERS = {'hauler': {'body':1, 'move':4, 'harvest':4, 'unload':4},
          'scout': {'body':1, 'move':4},
          'siege': {'body':1, 'move':4, 'fire':5, 'make':5, 'deployed':1},
          'tank': {'body':1, 'move':4, 'turret':1, 'wreck':1}}


def source(name):
    animated = MOD/'art/source/motion'/(name+'.blend')
    return animated if animated.exists() else MOD/'art/source'/('heavy' if name=='tank' else 'vehicles')/(name+'.blend')


def load_sources(assets=None):
    names = list(LAYERS if assets is None else assets)
    if set(names)-set(LAYERS) or not names: raise ValueError(names)
    if ASSETS or v.busy(): raise RuntimeError('Busy or module already owns scenes')
    support = [n for n in names if n!='tank']
    for name in support:
        with bpy.data.libraries.load(str(source(name)),link=False) as (src,dst):
            if len(src.scenes)!=1: raise ValueError('Expected one saved scene')
            dst.scenes=src.scenes
        s=dst.scenes[0]
        v.b.palette();mats=dict(v.b.MATS)
        for o in s.objects:
            for slot in o.material_slots:
                if slot.material and slot.material.get('fc_material'):
                    mats[slot.material['fc_material']]=slot.material
        ASSETS[name]={'scene':s,'materials':mats};v.capture(ASSETS[name])
    if 'tank' in names:
        with bpy.data.libraries.load(str(source('tank')),link=False) as (src,dst):
            if len(src.scenes)!=1: raise ValueError('Expected one saved K6 scene')
            dst.scenes = src.scenes
        s = dst.scenes[0]
        s['fc_asset'] = 'tank'
        roots = [o for o in s.objects if o.type=='EMPTY' and not o.parent]
        if len(roots)!=2: raise ValueError('Expected K6 hull and turret anchors')
        for o in roots:
            o['fc_root'] = 'turret' if 'Turret' in o.name else 'body'
        v.b.palette()
        mats = dict(v.b.MATS)
        for o in s.objects:
            for slot in o.material_slots:
                mat = slot.material
                if not mat: continue
                if not mat.get('fc_material'):
                    for role in mats:
                        if role in mat.name.lower(): mat['fc_material'] = role; break
                if mat.get('fc_material'): mats[mat['fc_material']] = mat
        ASSETS['tank'] = {'scene':s,'materials':mats}
        v.capture(ASSETS['tank'])
    return {n:len(a['scene'].objects) for n,a in ASSETS.items()}


def prepare():
    """Idempotently tag existing geometry; add visible running-gear details only."""
    if v.busy(): raise RuntimeError('Render in progress')
    previous = bpy.context.window.scene
    try:
        for name,a in ASSETS.items():
            s = a['scene']
            if s.get('fc_motion_version') == 1: continue
            bpy.context.window.scene = s
            v.b.MATS = a['materials']
            hull = next(o for o in s.objects if o.get('fc_root')=='body')
            for o in list(s.objects):
                n = o.name.lower()
                if 'individual track shoe' in n or 'tread link' in n or 'outer tread rib' in n:
                    o['fc_motion'] = 'tread'
                    o['fc_tread_pitch'] = .20 if name=='tank' else (2.70 if name=='hauler' else 2.55)*.9/11
                if name=='hauler':
                    if any(t in n for t in ('collector','collection blade')): o['fc_motion']='collect'
                    if any(t in n for t in ('rear discharge gate','gate locking beam','gate latch')): o['fc_motion']='gate'
                if name=='siege' and any(t in n for t in ('pressure jacket','reinforcing collar','refractory muzzle crown','mortar bore','induction aperture')):
                    o['fc_motion']='recoil'
                if name=='tank' and 'side sacrificial plate' in n and o.location.x>0:
                    o['fc_wreck_rot']=(0,.42,.1)
                    o['fc_wreck_shift']=(.12,0,-.20)
            if name in ('hauler','siege'):
                # Side grousers make the belt motion readable below the guards.
                length = 2.70 if name=='hauler' else 2.55
                width = 1.94 if name=='hauler' else 1.91
                for side in (-1,1):
                    for j in range(11):
                        o = v.b.box('FC6 belt grouser',(side*(width/2+.225),-length*.43+j*length*.086,.30),
                                    (.025,.075,.26),'edge',hull,.006)
                        o['fc_motion']='tread'; o['fc_tread_pitch']=length*.086
            if name=='scout':
                for side in (-1,1):
                    for y in (-.68,.03,.72):
                        # A pair of broad spokes remains visible at native RTS size.
                        for theta in (0,math.pi/2):
                            o = v.b.box('FC6 wheel spoke',(side*.875,y,.30),(.025,.245,.035),'edge',hull,.003)
                            o.rotation_euler.x=theta
                            o['fc_motion']='wheel'
            s['fc_motion_version']=1
            s['fc_motion_notes']='move 4 poses; harvest/unload 4 poses; fire 5 poses. Export with motion_visuals.py.'
            v.capture(a)
    finally:
        bpy.context.window.scene=previous
    return {n:sum(bool(o.get('fc_motion')) for o in a['scene'].objects) for n,a in ASSETS.items()}


def save_sources():
    if v.busy(): raise RuntimeError('Render in progress')
    for name,a in ASSETS.items():
        # One owned scene only; never save the live session or procedural rebuild.
        destination=MOD/'art/source/motion'/(name+'.blend')
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): raise FileExistsError('Save edited animation sources explicitly; never overwrite implicitly')
        bpy.data.libraries.write(str(destination),{a['scene']},fake_user=True,compress=True)
    return [str(source(n)) for n in ASSETS]


def pose(a, layer, facing, step):
    base = 'deployed' if layer=='fire' else 'body' if layer in ('move','harvest','unload') else layer
    v.pose(a,base,facing,step)
    name = a['scene']['fc_asset']
    for o,(loc,rot,scale,hidden,mats) in a['rest'].items():
        motion = o.get('fc_motion')
        if layer=='move':
            if motion=='tread': o.location.y += o['fc_tread_pitch']*step/4
            if motion=='wheel': o.rotation_euler.x += step*math.pi/8
        elif layer=='harvest' and motion=='collect':
            stroke=(0,.10,.17,.08)[step]
            o.location.z-=stroke*.5; o.location.y-=stroke
        elif layer=='unload' and motion=='gate':
            # Reciprocating discharge gate, not an opening callback or cargo level.
            angle=(0,.22,.38,.22)[step]
            pivot=Vector((0,1.25,1.44))
            o.location=pivot+Matrix.Rotation(-angle,3,'X')@(loc-pivot)
            o.rotation_euler.x-=angle
        elif layer=='fire' and motion=='recoil':
            o.location.z-=(0,.18,.11,.04,0)[step]
        if layer=='wreck' and name=='tank':
            if o.get('fc_root')=='turret':
                o.location.z-=.35; o.rotation_euler.x+=.19; o.rotation_euler.y+=.13
                o.scale*=.90  # Collapsed turret stays within the shared canvas at every facing.
            elif o.get('fc_root')=='body': o.scale.z*=.78
            if o.type in ('MESH','FONT'):
                o.data.materials.clear(); o.data.materials.append(a['materials']['soot'])
    bpy.context.view_layer.update()


def start_render(mode='samples', assets=None, resume=False):
    if mode not in ('samples','sprites'): raise ValueError(mode)
    names = list(ASSETS if assets is None else assets)
    if not names or set(names)-set(ASSETS): raise ValueError('Load selected sources first')
    if v.busy(): raise RuntimeError('A render is already running')
    directions = range(32) if mode=='sprites' else range(0,32,4)
    queue = [(n,l,f,k) for n in names for l,count in LAYERS[n].items()
             for f in directions for k in range(count)]
    signature = hashlib.sha256(Path(__file__).read_bytes() + b''.join(source(n).read_bytes() for n in names)).hexdigest()
    completed = 0
    status_path = OUT/(mode+'-status.json')
    if resume:
        previous_status = json.loads(status_path.read_text())
        if previous_status.get('signature') != signature or previous_status.get('assets') != names:
            raise ValueError('Cannot resume changed sources, script, or selection')
        completed = previous_status['done']
        if completed == len(queue): return previous_status
    total = len(queue)
    queue = queue[completed:]
    previous = bpy.context.window.scene
    settings = {n:(a['scene'].frame_current,a['scene'].render.filepath,
                   a['scene'].render.resolution_x,a['scene'].render.resolution_y)
                for n,a in ASSETS.items()}
    STATE.clear(); STATE.update(running=True,mode=mode,assets=names,done=completed,total=total,signature=signature)
    OUT.mkdir(parents=True,exist_ok=True)
    def status():
        p=OUT/(mode+'-status.json'); t=p.with_suffix('.tmp')
        t.write_text(json.dumps(STATE,indent=2)+'\n'); t.replace(p)
    def restore():
        for n,a in ASSETS.items():
            s=a['scene']; frame,path,rx,ry=settings[n]
            s.frame_set(frame)
            for o,(loc,rot,scale,hidden,mats) in a['rest'].items():
                o.location,o.rotation_euler,o.scale,o.hide_render=loc.copy(),rot.copy(),scale.copy(),hidden
                if o.type in ('MESH','FONT'):
                    o.data.materials.clear()
                    for mat in mats: o.data.materials.append(mat)
            s.render.filepath,s.render.resolution_x,s.render.resolution_y=path,rx,ry
        bpy.context.window.scene=previous
    def tick():
        try:
            n,l,f,k=queue.pop(0); a=ASSETS[n]; s=a['scene']
            bpy.context.window.scene=s
            pose(a,l,f,k)
            s.render.resolution_x=s.render.resolution_y=128
            p=OUT/('frames' if mode=='sprites' else 'samples')/n/l/f'{f*LAYERS[n][l]+k:03d}.png'
            p.parent.mkdir(parents=True,exist_ok=True); s.render.filepath=str(p)
            bpy.ops.render.render(write_still=True,scene=s.name)
            STATE.update(done=STATE['done']+1,last=str(p))
            if queue: status(); return .05
            restore(); STATE['running']=False; status()
            # Per-asset receipts prevent a partial export from certifying stale frames.
            for name in names: (OUT/f'{mode}-{name}.json').write_text(json.dumps(STATE,indent=2)+'\n')
        except Exception:
            STATE.update(running=False,error=traceback.format_exc())
            try: restore()
            finally: status()
        return None
    status(); bpy.app.timers.register(tick,first_interval=.5)
    return dict(STATE)
