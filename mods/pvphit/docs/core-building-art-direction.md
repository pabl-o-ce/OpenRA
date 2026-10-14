# Core building refinement

The Headquarters, Pressure Generator and Slag Processor now share the heavy
K-6 / Armor Works material and construction language. These are original Kiln
Directorate designs: pale refractory armor, structural iron, oxide heat shields,
protected machinery, amber work lights and separate ownership enamel. Cyan is
reserved for the generator's induction collars.

Review [intact and damaged models](core-building-models.png) and the
[native-zoom visual yard](core-building-yard.png). Model comparison columns are
HQ, generator, processor; intact above, damaged below. Presentation panels are
red; game exports use green masks shifted by `furnace-player`.

## Shapes and states

- HQ: stepped command keep, six perimeter buttresses, recessed observation band,
  protected communications sweep, roof cooling and the three-bar Directorate mark.
- Generator: paired pressure vessels, ceramic shields, exposed service manifold,
  oxide head bands and a rear cooling fan. A damaged head collapses asymmetrically.
- Processor: refractory furnace and cyclone separator connected behind the
  receiving area. The apron and central dock stay clear; a damaged cyclone crown
  collapses behind the apron. Cooling motion does not imply a docking event.

All three have four-frame intact and damaged operating loops (80 ms/frame),
and five-stage construction (400 ms/frame): foundation, structure, armor,
upper machinery, then final equipment. The final stage exactly matches idle
frame zero. Damage changes both geometry and materials; these are damage states,
not persistent wreck actors. Machinery loops are cosmetic and do not introduce
new power, resource or production conditions.

Existing gameplay is unchanged. HQ remains preplaced and unbuildable. Generator
and processor icons use the player palette; the HQ icon is supplied for asset
use without adding it to the construction menu. The processor keeps its 3×3
`xxx xxx ===` footprint, `DockOffset: 0,1c0,0`, facing and free-hauler spawn.
The camera, ground anchors, scale and offsets are the established building setup:
256×256 RGBA frames, 9.8 orthographic scale, sequence scale 0.5, offset `(0,-14)`.

## Reproduce through Blender MCP

Use Blender 5.2.2 with the connected MCP addon. Inspect the connection and check
that no other render is running first. Run this through `execute_blender_code`:

```python
import bpy, importlib.util
path = '/home/cye/Dev/OpenRA/mods/pvphit/tools/core_buildings_visuals.py'
spec = importlib.util.spec_from_file_location('fc_core_buildings', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
bpy.app.driver_namespace['fc_core_buildings'] = m
result = m.build()
```

`build()` creates independent scenes and saves one scene and its dependencies
per file in `art/source/core-buildings/{hq,generator,processor}.blend`. Earlier
sources and open scenes are preserved. Mesh names, ground anchors, material roles,
construction/damage tags and cooling-fan actions remain editable. A module owns
one pass: reuse it instead of calling `build()` twice. In a fresh module, use
`m.load_sources()` **instead of** `m.build()` to export manual `.blend` edits.
Do not call `build()` when those manual edits should be retained.

Render using separate MCP calls:

```python
import bpy
result = bpy.app.driver_namespace['fc_core_buildings'].start_render('sprites')
```

Wait until `art/core-buildings/render-status.json` reports `running: false`,
`done: 39`, `total: 39`, and no error. Only then request `start_render('previews')`
for six presentation images. `build`, `load_sources` and `start_render` accept
`assets=['generator']` (or another subset). Partial rendering refreshes only
those frames; a first complete pack still requires all three assets.

The timer restores the previous scene and intact export materials on completion
or failure. Do not edit pass-owned scenes during a render. Cycles uses CPU,
24 samples, denoising and a fixed seed. The loader reads saved sources without
resaving them. Construction/damage variants are controlled by mesh properties
`fc_stage`, `fc_damage` and `fc_damage_only`; `fc_spin` drives operating poses.

From the repository root, with ImageMagick, Python 3, the built utility and RA
content installed:

```sh
ENGINE_DIR="$PWD" python3 mods/pvphit/tools/pack_core_buildings.py --dotnet dotnet
python3 mods/pvphit/tools/build_core_building_yard.py
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --map refresh '^foundry-visual-yard$'
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --check-yaml
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --check-missing-sprites
```

The current temporary setup substitutes `/tmp/furnace-dotnet/dotnet` and sets
`XDG_CONFIG_HOME=/tmp/furnace-config` for content lookup. No Pillow dependency
is required. The packer checks completeness, dimensions, alpha bounds, actual
operating motion, damage differences and the construction endpoint **before**
writing. It embeds PNG metadata with this fork's utility, writes three 64×48
icons and records frame hashes in `art/core-buildings/export-manifest.json`.
Only core-building outputs and their sequence file are packed.

`build_core_building_yard.py` is the current expanded yard generator. The older
`build_visual_yard.py` intentionally recreates the earlier tank/factory layout;
run the core-building generator last when reproducing multiple passes.
Intermediate frames and render status are ignored; sources, packed sheets,
metadata, previews and scripts are retained.

## In-game review

```sh
/tmp/furnace-dotnet/dotnet bin/OpenRA.dll \
  Engine.EngineDir=/home/cye/Dev/OpenRA \
  Engine.SupportDir=/tmp/furnace-core-yard-support \
  Game.Mod=pvphit Launch.Map=foundry-visual-yard \
  Graphics.ViewportDistance=Native
```

Use an isolated support directory with the required RA content. The yard's
three rows show red, blue, yellow, purple and damaged red buildings. Tank and
factory references sit below. At 30 seconds the purple column takes damage;
at 45 seconds it recovers. At 50 seconds additional generator/processor actors
assemble. These scripted events are laboratory-only, not changes to gameplay.
The two-minute assertion checks paid factory production, resource income and
at least two departures from the original processor dock. Avoid intervening
until `CORE YARD PASSED: repeated unloading and departure; suite complete`.

Also run `foundry-systems-lab` until `FURNACE CHECK PASSED: systems suite complete`.
Review [construction in-game](core-building-construction.gif) and
[operating machinery in-game](core-building-operation.gif), and
[harvester unloading](core-building-unloading.gif); these are enlarged
crops from the native-zoom capture. The screenshot above preserves native size.

## Rollback

Remove `rules/core-buildings.yaml` and `sequences/core-buildings.yaml` from the
manifest to restore the original three buildings. The heavy tank and factory
remain selected. Run the older yard generator and refresh the map to restore
its earlier layout. No engine, gameplay-statistic, platform or account files
are changed by this pass.
