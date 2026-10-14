"""Original siege-industrial refinement, authored/rendered through Blender MCP.

Create a new module, call build(), then start_render('previews' or 'sprites').
Uses the established anchors and export helpers, with new independent scenes.
The previous pass, open user scenes, and archived tank remain untouched.
"""
from pathlib import Path
import importlib.util
import math
import bpy

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fc_heavy_base', HERE/'refine_visuals.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.OUT = base.MOD/'art/heavy'
base.SOURCE = base.MOD/'art/source/heavy'


def assign(o, mat):
    o.data.materials.clear()
    o.data.materials.append(base.MATS[mat])


def remove_matching(scene, fragments):
    # Only objects belonging to this fresh procedural scene are removed.
    for o in list(scene.objects):
        if any(fragment in o.name for fragment in fragments):
            bpy.data.objects.remove(o, do_unlink=True)


def armor(name, outline, bottom, top, mat, parent, layer='body', taper=.90):
    """A chamfered armor volume with sloped sides and a smaller top face."""
    n = len(outline)
    center = (sum(x for x,y in outline)/n, sum(y for x,y in outline)/n)
    vertices = [(x,y,bottom) for x,y in outline]
    vertices += [(center[0]+(x-center[0])*taper,center[1]+(y-center[1])*taper,top) for x,y in outline]
    faces = [tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh = bpy.data.meshes.new('FC3 '+name)
    mesh.from_pydata(vertices,[],faces);mesh.update()
    o = bpy.data.objects.new('FC3 '+name,mesh)
    bpy.context.scene.collection.objects.link(o)
    base.finish(o,name,mat,parent,layer)
    bevel=o.modifiers.new('Armor edge highlights','BEVEL');bevel.width=.012;bevel.segments=1
    o.modifiers.new('Armor normals','WEIGHTED_NORMAL')
    return o


def bolt(name,loc,radius,parent,layer='body',rot=(0,0,0)):
    return base.cyl(name,loc,radius,.025,'edge',parent,rot,layer)


def tank():
    s=base.tank();s.name='FC3 K6 siege-industrial tank'
    a=base.ASSETS['tank'];hull,turret=a['roots']
    box,cyl=base.box,base.cyl
    remove_matching(s,('Turret Main Armor','Turret Upper Plate','Turret Team Panel',
        'turret cheek','Cannon Muzzle','Cannon Aperture','marking 06','marking K6',
        'front ceramic cheek','oxide identification border','team stripe','Team Stripe',
        'foundry upright','foundry crossbeam'))
    for o in s.objects:
        if o.type!='MESH':continue
        for mod in o.modifiers:
            if mod.type=='BEVEL':mod.width=min(mod.width,.025);mod.segments=1
        if o.name.startswith(('Hull - Upper','Front Armor')):assign(o,'iron')
        if 'replaceable track crown' in o.name:
            assign(o,'ceramic' if abs(o.location.y)>.85 else 'rust')
        if 'Front Light' in o.name:
            assign(o,'amber');o.scale.x=.48
        if 'Ion Energy Strip' in o.name:o.scale.x=.62
        if 'Optical Sensor' in o.name or 'Sensor Lens' in o.name:o.location.z+=.21
        if 'capacitor' in o.name:o.location.y+=.18
    outline=[(-.60,-.66),(.60,-.66),(.84,-.38),(.84,.69),(.56,.94),(-.56,.94),(-.84,.69),(-.84,-.38)]
    armor('faceted turret citadel',outline,1.18,1.82,'ceramic',turret,'turret',.78)
    box('turret roof inset',(0,.24,1.836),(.96,.84,.035),'iron',turret,.012,'turret')
    box('turret ownership bar',(-.26,.20,1.865),(.20,.58,.023),'team',turret,.004,'turret')
    base.stamp((.21,.05,1.861),.56,turret,'turret')
    # A small armoured observation hatch, not another weapon.
    cyl('observation hatch',(.15,.65,1.85),.19,.075,'edge',turret,layer='turret')
    box('hatch lock',(.15,.65,1.902),(.23,.042,.028),'iron',turret,.004,'turret')
    for side in (-1,1):
        # Layered track skirts keep running gear visible below the armor.
        for y in (-.92,0,.92):
            box('side spaced armor',(side*1.36,y,.80),(.20,.79,.57),'iron',hull,.018)
            box('side sacrificial plate',(side*1.475,y,.86),(.045,.62,.36),'ceramic',hull,.008)
            for yy in (y-.22,y+.22):
                bolt('skirt fastener',(side*1.508,yy,.95),.037,hull,rot=(0,math.pi/2,0))
        box('shoulder iron rim',(side*1.04,-.62,1.126),(.43,.83,.06),'iron',hull,.016)
        box('shoulder identification',(side*1.04,-.63,1.161),(.25,.63,.025),'team',hull,.005)
        for y in (-1.08,.98):
            box('deck clamping bridge',(side*1.04,y,1.145),(.54,.07,.075),'edge',hull,.008)
        box('mantlet side shield',(side*.40,-.54,1.48),(.18,.41,.47),'iron',turret,.024,'turret')
        # Side cheeks are slanted, doubled armor with visible stud rows.
        cheek=box('turret bolted cheek',(side*.716,.10,1.50),(.11,.68,.34),'rust',turret,.015,'turret')
        cheek.rotation_euler.y=side*.20
        for y in (-.15,.12,.39):
            bolt('turret cheek stud',(side*.785,y,1.58),.030,turret,'turret',(0,math.pi/2,0))
        box('rear radiator cowl',(side*.72,1.10,1.38),(.36,.43,.36),'iron',hull,.025)
        for y in (.98,1.08,1.18):box('radiator ribs',(side*.72,y,1.568),(.28,.031,.012),'edge',hull,.001)
        # Towing eyes read as heavy industrial fittings.
        box('tow mount',(side*.60,-1.47,.61),(.20,.21,.23),'edge',hull,.012)
        cyl('tow eye dark center',(side*.60,-1.586,.61),.053,.018,'black',hull,(math.pi/2,0,0))
    armor('reinforced angled prow',[(-.82,-1.49),(.82,-1.49),(.77,-.99),(-.77,-.99)],.59,1.08,'ceramic',hull,taper=.83)
    box('prow inspection slit',(0,-1.505,.86),(.62,.025,.075),'black',hull,.003)
    for x in (-.59,.59):bolt('prow crown rivet',(x,-1.24,1.089),.043,hull)
    # An oversized shroud and deeply recessed aperture replace the luminous cap.
    box('muzzle reinforced shroud',(0,-1.88,1.46),(.64,.32,.40),'iron',turret,.035,'turret')
    box('muzzle sacrificial crown',(0,-1.88,1.673),(.54,.27,.042),'ceramic',turret,.008,'turret')
    box('muzzle deep aperture',(0,-2.051,1.46),(.43,.022,.21),'black',turret,.009,'turret')
    box('muzzle induction core',(0,-2.066,1.46),(.19,.010,.068),'cyan',turret,.004,'turret')
    for x in (-.25,.25):bolt('muzzle fastener',(x,-2.052,1.55),.027,turret,'turret',(math.pi/2,0,0))
    for y in (-.83,-1.18,-1.54):
        box('cannon armored bridge',(0,y,1.60),(.66,.11,.14),'edge',turret,.012,'turret')
    # A few broad scars and chipped corners, concentrated on exposed surfaces.
    # Do not scatter high-frequency noise over the ownership panels.
    for x,y,length in ((.36,-.02,.20),(.34,.05,.13),(-.37,.58,.12)):
        scar=box('roof abrasion',(x,y,1.86),(.013,length,.006),'black',turret,.001,'turret')
        scar.rotation_euler.z=.65
    for side in (-1,1):
        for y in (-.88,.90):
            box('skirt chipped corner',(side*1.503,y,.994),(.01,.13,.035),'edge',hull,.001)
    base.stencil('K-6',(0,-1.09,1.10),.16,'iron',hull)
    a['scene'].cycles.samples=32


def factory():
    s=base.factory();s.name='FC3 Armor Works fortified foundry'
    a=base.ASSETS['factory'];root=a['roots'][0]
    box,cyl=base.box,base.cyl
    remove_matching(s,('pressure stack','stack lip','stack bore','foundry upright','foundry crossbeam','marking 09'))
    for o in s.objects:
        if o.type!='MESH':continue
        if 'roof cassette' in o.name:assign(o,'iron')
        if 'wall cassette' in o.name:assign(o,'rust')
        if 'door pier' in o.name:assign(o,'iron')
        if 'bay header' in o.name:assign(o,'iron')
        if 'ownership' in o.name:o.location.x=-.94;o.location.y=.05
    # Leaning load-bearing ribs define the fortress silhouette without spires.
    for side in (-1,1):
        for y in (-1.20,.40,1.92):
            x=side*2.23
            outline=[(x-.32,y-.30),(x+.32,y-.30),(x+.32,y+.30),(x-.32,y+.30)]
            armor('fortress buttress',outline,.34,2.67,'ceramic',root,taper=.55)
            box('buttress dark collar',(x,y,1.01),(.63,.63,.12),'iron',root,.018)
            box('buttress crown',(x,y,2.71),(.46,.46,.15),'edge',root,.016)
            for z in (.67,1.77,2.27):bolt('buttress bolt',(x,y-.327,z),.055,root,rot=(math.pi/2,0,0))
        # Roof exhaust towers are shielded rectangular industrial structures.
        x=side*1.56
        box('vent tower foot',(x,1.43,2.47),(.77,.91,.42),'iron',root,.025)
        box('vent tower shaft',(x,1.43,3.03),(.61,.73,.86),'rust',root,.02)
        box('vent tower crown',(x,1.43,3.54),(.85,.94,.20),'ceramic',root,.027)
        box('vent tower top recess',(x,1.43,3.651),(.54,.64,.027),'black',root,.006)
        for z in (2.74,2.95,3.16):
            box('tower vent mouth',(x,1.049,z),(.43,.028,.11),'black',root,.004)
            box('tower vent lip',(x,1.021,z+.062),(.47,.065,.029),'edge',root,.004)
        # Deep entrance casing and a thick projecting portal brow.
        box('portal armor cheek',(side*1.57,-1.76,1.28),(.39,.42,1.63),'ceramic',root,.028)
        box('portal oxide insert',(side*1.57,-1.992,1.30),(.15,.022,1.22),'rust',root,.003)
        for z in (.64,1.20,1.77):bolt('portal anchor',(side*1.59,-2.016,z),.05,root,rot=(math.pi/2,0,0))
        box('entrance lamp frame',(side*1.58,-1.77,2.29),(.27,.30,.21),'iron',root,.015)
        box('entrance amber slit',(side*1.58,-1.935,2.29),(.14,.022,.065),'amber',root,.003)
    box('portal upper slab',(0,-1.55,2.52),(3.61,.75,.38),'ceramic',root,.035)
    box('portal top armor seam',(0,-1.57,2.727),(3.2,.55,.025),'iron',root,.005)
    for x in (-1.32,-.88,.88,1.32):bolt('portal upper fastener',(x,-1.74,2.755),.06,root)
    # Raised central pressure manifold, with original foundry stamp above the door.
    box('roof spine',(0,.62,2.48),(.72,2.1,.42),'rust',root,.025)
    box('roof spine cap',(0,.61,2.725),(.61,2.07,.12),'ceramic',root,.015)
    for y in (-.07,.45,.97,1.49):box('spine louvre',(0,y,2.797),(.48,.09,.025),'iron',root,.003)
    emblem=base.empty('portal foundry seal',root)
    emblem.location=(0,-1.961,2.38);emblem.rotation_euler.x=math.pi/2
    base.stamp((0,0,0),.58,emblem)
    base.stencil('09',(.92,-.72,2.301),.36,'ceramic',root)
    # Floor apron preserves the exit clearance and anchors the apparent mass.
    for x in (-1.14,1.14):
        box('apron steel guide',(x,-2.08,.37),(.15,.46,.035),'edge',root,.008)
    a['scene'].cycles.samples=32


def build():
    if base.ASSETS:raise RuntimeError('Reuse the already-built heavy pass instead of rebuilding it.')
    base.OUT.mkdir(parents=True,exist_ok=True)
    base.palette()
    base.MATS['ceramic']=base.material('FC3 ceramic',(.30,.29,.24),.15,.72,True)
    base.MATS['iron']=base.material('FC3 iron',(.065,.082,.09),.70,.60,True)
    base.MATS['rust']=base.material('FC3 oxide',(.23,.045,.025),.25,.77,True)
    base.MATS['edge']=base.material('FC3 edge',(.23,.255,.26),.75,.46,True)
    tank();factory()
    base.capture_rest();base.save_sources()
    bpy.context.window.scene=base.ASSETS['tank']['scene']
    return {name:{'scene':a['scene'].name,'objects':len(a['scene'].objects)} for name,a in base.ASSETS.items()}


_visibility=base.visibility
def visibility(a,layer='all',facing=0,step=0):
    _visibility(a,layer,facing,step)
    if layer.startswith('damaged-'):
        for o in a['scene'].objects:
            if o.type!='MESH':continue
            if any(n in o.name for n in ('fortress buttress','portal upper slab','portal armor cheek','roof spine cap')):
                assign(o,'soot')
            if o.location.x<0 and any(n in o.name for n in ('vent tower crown','vent tower top recess')):
                o.location.z-=.35
                o.rotation_euler.y=.30
                assign(o,'soot')
            if o.location.x<0 and 'vent tower shaft' in o.name:
                o.location.z-=.18;o.scale.z=.60
base.visibility=visibility

_render_jobs=base.render_jobs
def render_jobs(mode):
    if mode=='damage':
        return [j for j in _render_jobs('sprites') if j[0]=='factory' and j[1].startswith('damaged-')]
    return [j for j in _render_jobs(mode) if j[0] in base.ASSETS]
base.render_jobs=render_jobs


def start_render(mode):
    return base.start_render(mode)
