# Vehicle refinement

The Slag Hauler, Relay Scout and Brace Mortar Carrier now use the completed
Kiln Directorate material language without sharing the K-6's silhouette.
See the [models](vehicle-models.png), [native-size samples](vehicle-native-samples.png),
[before/after directions](vehicle-facing-comparison.png) and [wrecks](vehicle-wrecks.png).
The model columns are hauler, scout, traveling carrier and deployed carrier.
The directional comparison has the original models above and refined models below;
each row groups four hauler, four scout and four carrier directions.

## Forms and states

- Hauler: protected forward cab, three-wheel track bogies, segmented shoulders,
  collector teeth and hydraulic rams, refractory hopper with an oxide lining,
  tipping cylinders, a hinged discharge gate and shielded service equipment.
  Residue in the hopper is fixed artwork, not a representation of resource capacity.
- Scout: narrow six-wheel chassis, visible running gear, separate fenders,
  low crew cell, protected communications mast and an independently aimed light
  gun/sensor turret. Hull and turret keep the same ground anchor.
- Carrier: fixed pressure-mortar cradle, open refractory muzzle, pressure
  accumulators, protected induction apertures and four telescoping stabilizers.
  The five deployment poses extend the beams and lower the ground shoes.
  Withdrawal uses the same sequence backward; no rotating gun or aiming trait
  has been added to the existing AttackOmni implementation.

Ceramic plates, structural iron and oxide heat shields match the core-building
pass. Amber work lights and cyan induction apertures are separate from green
ownership masks. Wrecks lose lit and ownership surfaces and change geometry:
hopper walls/gate/blade bend, scout turret/wheels/mast shift, and the mortar
cradle/crown collapse. Each wreck retains its vehicle's 32 directional views.

The original FC5 hauler used idle artwork for harvesting and docking.
WithHarvestAnimation reacts to harvested bales, while WithDockingAnimation gates
unloading on completion of its opening animation and reverses it before departure.
The later FC6 pass adds harvest/unload motion and validates economic timing while
retaining the original one-frame opening/closing callbacks. See
[movement art direction](movement-art-direction.md) for the current sources.

## Blender MCP workflow

Inspect the active Blender session and ensure no render or timer pass is running.
Import `tools/vehicle_visuals.py` through MCP and retain the module:

```python
import bpy, importlib.util
path = '/home/cye/Dev/OpenRA/mods/pvphit/tools/vehicle_visuals.py'
spec = importlib.util.spec_from_file_location('fc_vehicles', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
bpy.app.driver_namespace['fc_vehicles'] = m
result = m.load_sources()
```

`load_sources()` reads the three saved files under `art/source/vehicles/` without
resaving them. Use this path for subsequent hand edits. Each file contains one
scene with its own meshes/materials, `fc_asset` scene tag, `fc_root` anchors and
`fc_layer` body/turret tags. `fc_deploy_shift` and `fc_wreck_*` object properties
store pose deltas relative to the edited source pose. Save sources in their
travel pose. Do not apply object transform changes in a loaded export module;
edit/save the source, then load it into a fresh module to capture its new rest pose.

`build()` is only for generating new procedural sources. It refuses to overwrite
existing source files. To reproduce from code without touching hand edits, set
`m.SOURCE` to a separate directory before building. Both entry points accept
`assets=['hauler']`, `['scout']` or `['siege']` subsets.

```python
result = m.start_render('previews')
# Wait for previews-status.json success, then inspect all four silhouettes.
# Optional eight-direction, native-resolution checks:
result = m.start_render('samples')
# Wait for completion and review before beginning the full export:
result = m.start_render('sprites')
```

Use separate calls; do not start a second render or edit the scenes during a
batch. Success is `running: false`, no `error`, and `done == total` in the
mode-specific status file under `art/vehicles/`. A complete sprite batch has
**419 frames**: 65 hauler, 97 scout and 257 carrier frames, including icon sources.
Rendering restores source transforms, visibility, materials, timeline, output
settings and the previously active scene after completion or failure.

The fixed contract is 128×128 RGBA, Cycles CPU/24 samples/seed 0, orthographic
scale 4.9, sequence scale 0.5 and offset `(0,-7)`. Forward is −Y; source directions
advance 11.25° around +Z. Engine order is source `16–31,0–15`, with
`UseClassicFacings: false`. The carrier's `make` sheet is facing-major:
`source_facing * 5 + step`, `Length: 5`, `Tick: 400`. Both ends exactly match
travel/deployed pixels in all 32 directions.

## Packing and review

From the repository root, with ImageMagick and this fork's built utility:

```sh
XDG_CONFIG_HOME=/tmp/furnace-config ENGINE_DIR="$PWD" \
  python3 mods/pvphit/tools/pack_vehicles.py --dotnet /tmp/furnace-dotnet/dotnet
python3 mods/pvphit/tools/preview_vehicles.py
python3 mods/pvphit/tools/build_vehicle_yard.py
XDG_CONFIG_HOME=/tmp/furnace-config ENGINE_DIR="$PWD" \
  /tmp/furnace-dotnet/dotnet bin/OpenRA.Utility.dll pvphit --map refresh '^foundry-vehicle-yard$'
```

Temporary runtime/content paths must be checked before use. Substitute the
permanent runtime/configuration paths when appropriate. `--validate-only` runs
export checks without packing. The packer validates complete frame sets, RGBA
size and alpha margins, actual movement, wreck differences and exact deployment
endpoints. Both scout layers retain the whole shared canvas, so every combination
of their bounds fits within the frame. Sheets are staged, imported with
`--png-sheet-import`, and checked for embedded `FrameSize`/`FrameAmount` before
owned outputs are replaced. The export manifest records source/frame hashes and
rendering/facing parameters. Earlier asset sheets and sequences are not rewritten.

`foundry-vehicle-yard` is a separate laboratory. The first view includes heavy
references, four ownership colors, a working processor, capture scout, paid hauler/scout builds plus three successive
paid siege builds and an interactive mortar/target. The parked hauler color
samples are map-only display actors; the free hauler and produced hauler use
the real actor. Separate checks exercise minimum/maximum artillery range and
firing while undeployed. At 305 seconds the camera tours the complete facing,
deployed, turret and wreck grids; the final system assertion runs at 360 seconds.
The yard keeps its wrecks alive for this tour through a map-only override.

Use isolated support/settings and `Graphics.ViewportDistance=Native`. Keep Xvfb,
the game and any recorder under the same supervisor, stopping the recorder/game
before closing the display. Select the interactive mortar, deploy with F, then
force-fire at the blue target; a move order must withdraw the braces first.
The existing `foundry-visual-yard` and `foundry-systems-lab` remain independent
regression checks. Do not run the obsolete `build_visual_yard.py` generator.

## Rollback

For an FC5-only checkout, remove `rules/vehicles.yaml` and
`sequences/vehicles.yaml` from `mod.yaml` to restore the earlier artwork. In the
current checkout, the later motion rules/sequences/weapons also override those
assets; remove that presentation layer together before evaluating an art rollback. Heavy tank/factory and core-building
assets remain selected. The vehicle review map can be removed independently;
its generator never writes either existing laboratory. See `VALIDATION.md` for
newly performed checks and known limits.

**Step 3 update:** the creation-time condition leak is corrected while retaining
`WithMakeAnimation` for deployment. New motion sources, working sequences and
weapon/death effects are described in [movement art direction](movement-art-direction.md).
The original refined sources and exports remain available; the new sequence
overrides select the motion sheets. See `VALIDATION.md` for the current acceptance
results rather than the historical step-2 limitation.
