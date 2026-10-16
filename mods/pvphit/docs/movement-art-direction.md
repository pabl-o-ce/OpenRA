# Vehicle motion and weapon presentation

FC6 builds on the refined support vehicles and heavy K6, retaining the Kiln
Directorate silhouettes, three-bar marking, ceramic/iron/oxide materials and
separate cyan, amber and ownership colors. This pass adds artwork and existing
trait bindings; it does not add units, aiming mechanics, cargo states or sounds.

## Source ownership

The editable animation copies live in `art/source/motion/{hauler,scout,siege,tank}.blend`.
They were loaded from the refined `art/source/vehicles/` and `art/source/heavy/`
sources, never rebuilt from roster blockouts. Those original files are retained.
Each animation source contains one owned scene with editable geometry and
`fc_motion` properties. The export adapter evaluates these properties relative
to the saved rest pose. `fc_motion_version` prevents repeated rig additions.

Track grousers progress along the belt; the scout has broad rotating wheel
spokes. The hauler collector strokes on harvest notifications and its rear gate
reciprocates during unloading. Hopper residue remains fixed cosmetic artwork.
The siege pressure jacket and muzzle compress briefly on an actual shot; its
cradle, stabilizers and AttackOmni aim behavior remain fixed.

The source for baked flash, spark, dust, smoke and fragment effects is
`art/source/effects/weapon-effects.blend`. Its reproducible particle poses use a
fixed seed. The export has 192 frames: three muzzle/impact/projectile sets and
four death sequences. These are transient sprites, not physical debris actors.

## Blender MCP export

Inspect the live session, render jobs and unsaved work first. Load tools using
`importlib.util.spec_from_file_location` and retain the module in
`bpy.app.driver_namespace`; do not open a source over the user's live file.

For `tools/motion_visuals.py`:

```python
m.load_sources(['hauler'])
m.prepare()  # idempotent on already-rigged saved sources
m.start_render('samples', ['hauler'])
# Inspect all eight native-size directions before the full export.
m.start_render('sprites', ['hauler'])
```

Use separate calls and wait for `running: false`, no `error`, and `done == total`.
The four vehicles total **1,312 frames**: hauler 416, scout 160, siege 512 and K6
224. `save_sources()` writes only new animation source files and refuses to
replace existing ones. Save intentional manual edits explicitly in Blender,
then load them into a fresh module before exporting.

An interrupted export with a signature can use `resume=True` with the same
mode, asset selection, script and sources. A changed signature is rejected.
Per-asset sprite receipts prevent a partial selection from certifying a missing
export. Rendering restores transforms, materials, visibility, output settings,
timeline and active scene.

For `tools/weapon_visuals.py`, call `load_source()` then `start_render()`.
`build()` is only for first creation and refuses to overwrite the saved source.
Never run two render batches concurrently in the same Blender instance.

All vehicle sheets retain 128×128 RGBA frames, scale 0.5, offset `(0,-7)`, camera
scale 4.9, -Y forward and uniform +Z 11.25-degree directions. Engine ordering is
16–31 then 0–15. Hulls/turrets are not trimmed. Siege deployment remains five
facing-major frames at 400 ms/frame, with exact travel/deployed endpoints and
reverse withdrawal. Movement uses four frames at 80 ms/frame. These are cosmetic
loops, not distance-integrated track simulation or new steering mechanics.

## Engine interactions

- `WithMoveAnimation` controls the travel body on translation and turning. The
  siege binding requires `mobile`, protecting make/reverse-make animations.
- `WithHarvestAnimation` starts a short stroke on harvested resources; it does
  not delay resource acquisition. Movement can replace that custom body sequence.
- `WithDockingAnimation` still opens/closes using single-frame `idle`. Only its
  unloading loop changes. Opening/closing callbacks therefore retain their
  original duration; resource capacity, bale timing and dock positioning are unchanged.
- Scout and K6 use existing shot-driven muzzle overlays and turret recoil.
  Their hulls do not play competing attack animations. Siege `WithAttackAnimation`
  targets the `braced` body and uses `DelayRelativeTo: Attack` with zero delay.
- Vehicle death weapons contain only effects. Existing husk actors still spawn
  immediately with their existing lifetime, collision, pathing and visibility.
  Buildings retain the shared original death weapon.

The siege stall fix removes its creation-time `build-incomplete` grant and
references. `WithMakeAnimation` stays: deployment has separate completion
notifications and the `mobile`/`braced` conditions. This is a focused YAML fix;
no shared creation/deployment lifecycle behavior is changed.

The one engine correction is in `WithMoveAnimation.UpdateAnimation`: read the
current sequence name with a null check. A map-placed deployed carrier has never
enabled its travel body, so that body initially has no current sequence. The
old code crashed on its first movement notification even when the movement
animation trait was disabled. The existing pre-deployed yard grid exercises this
case; no new engine trait or public API was added.

## Packing and verification

With the current engine utility, ImageMagick and installed RA content:

```sh
XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  python3 mods/pvphit/tools/pack_motion.py \
  --dotnet "$PWD/mods/pvphit/.work/dotnet/dotnet"
XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  python3 mods/pvphit/tools/pack_weapon_visuals.py \
  --dotnet "$PWD/mods/pvphit/.work/dotnet/dotnet"
python3 mods/pvphit/tools/run_visual_checks.py --tag motion-final --display :102
```

Substitute your isolated runtime/content paths when necessary. `.work/` is
ignored and isolated from normal settings; recordings, logs and temporary
content there survive restarts. No account identity or match ID is required.
The render directories are ignored; sources, sheets, metadata and export hash
manifests are retained. Packing stages files on the destination filesystem,
validates engine-imported PNG metadata, then replaces only owned outputs.

The vehicle harness requires real deploy/move input: this fork's Lua `Deploy()`
only supports Transforms and its Lua `Move()` bypasses deployment's movement
wrapper. The runner centers the camera, selects the produced carrier, presses F,
and issues a real move order after damage. Assertions verify actual exit and
arrival, repeated production, damage, withdrawal before translation, and repeat
cycles. Production callbacks alone do not pass the suite.

Use `build_core_building_yard.py` for the current core yard. Do not run the
obsolete `build_visual_yard.py`. See `VALIDATION.md` for results actually observed
and any outstanding acceptance work; this workflow is not itself proof of a pass.

## Runtime validation commands

The harnesses require Linux, Xvfb, X11/XTest, ImageMagick, FFmpeg, Python 3 and a
built current engine with its required RA content. They create their own settings,
content links, displays and logs under `.work/`. The local test environment used
.NET runtime 6.0.36 and SDK 8.0.425; the latter was selected by a `global.json`
inside the ignored `.work/build/` directory. The repository's SDK pin is unchanged.
`LP_NUM_THREADS=2` limits software-renderer worker oversubscription. Run the
following from the repository root (substitute a compatible dotnet executable):

```sh
ENGINE_DIR="$PWD" XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  mods/pvphit/.work/dotnet/dotnet bin/OpenRA.Utility.dll pvphit --check-yaml
ENGINE_DIR="$PWD" XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  mods/pvphit/.work/dotnet/dotnet bin/OpenRA.Utility.dll pvphit --check-missing-sprites
python3 mods/pvphit/tools/check_motion_balance.py \
  --baseline mods/pvphit/docs/validation/motion \
  --dotnet mods/pvphit/.work/dotnet/dotnet
python3 mods/pvphit/tools/run_visual_checks.py --tag motion --display :102 --seconds 900
python3 mods/pvphit/tools/run_visual_checks.py --tag motion --display :105 --map foundry-systems-lab
python3 mods/pvphit/tools/run_visual_checks.py --tag motion --display :106 --map foundry-visual-yard
python3 mods/pvphit/tools/run_multiplayer_checks.py
```

The multiplayer harness uses port 12437, displays :103/:104 and a private copy of
the yard with lobby visibility. One client controls Tester; the second observes.
It starts through the real lobby UI and injects orders only into the controller.
The server is unadvertised, authentication is disabled for this local test and
`PVPHIT_MATCH_ID` is removed from the child environment. It does not exercise
account linking or result submission. Existing occupied displays/port are refused.

Replay the resulting server recording without injecting any input:

```sh
python3 mods/pvphit/tools/run_visual_checks.py --tag motion-replay --display :107 \
  --replay /absolute/path/to/the/server.orarep \
  --extra-map 'mods/pvphit/.work/multi-server-support/maps/pvphit/{DEV_VERSION}/fc6-local-yard'
```

Preserve that private map copy with its replay: changing its Lua changes the map
hash. The runner writes timestamped event logs alongside recordings for extracting
real gameplay evidence. The additional late-stage ore field is test-map-only;
it prevents depletion from skipping the destruction and dock-interruption checks.

`preview_motion.py` regenerates the native 64-pixel direction/working boards.
`preview_weapon_visuals.py` generates labeled native-scale effect GIFs at the
sequence timings. Its projectile column shows one static facing; it does not
simulate projectile flight or claim to be an in-game recording.

The retained acceptance recording can be replayed directly from tracked evidence:

```sh
python3 mods/pvphit/tools/run_visual_checks.py --tag retained-replay --display :107 \
  --replay mods/pvphit/docs/validation/motion/local-two-client.orarep \
  --extra-map mods/pvphit/docs/validation/motion/local-replay-map.oramap
```

After a recorded run completes, generate the gameplay crops with:

```sh
python3 mods/pvphit/tools/extract_motion_evidence.py --tag motion-replay-vehicle-yard
```

These GIFs crop native game pixels without scaling. The full yard PNG preserves
its 1280×1000 capture. Effect preview GIFs are separate, labeled render boards.
