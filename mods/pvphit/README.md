# Furnace Covenant — playable prototype

Working title for an original industrial science-fiction RTS inside the `pvphit`
mod. This is a small gameplay and asset-pipeline prototype, not a finished total
conversion. Shared Red Alert files, release versions, account endpoints, and the
PvPHit outcome emitter are unchanged.

Review the [in-game roster](docs/roster-preview.png),
[tank facing samples](docs/tank-facing-preview.png), and [test results](VALIDATION.md).
The tank/factory Blender MCP pass is shown in the
[heavy model previews](docs/heavy-models.png) and
[industrial yard](docs/heavy-yard.png). See the
[art direction and reproduction notes](docs/heavy-art-direction.md).
The subsequent Headquarters, Generator and Processor pass has
[model comparisons](docs/core-building-models.png), a
[native-zoom yard](docs/core-building-yard.png), and
[reproduction instructions](docs/core-building-art-direction.md).
The [earlier model previews](docs/refined-models.png) remain for comparison.

## Direction

Veyr's settlements survive around immense heat and material-processing plants.
Their expeditions fight over the remaining extraction corridors and pressure
stations. A commander leads a mobile foundry detachment: build a viable base,
protect its haulers, and commit armor to routes that keep industry operating.

The **Kiln Directorate** is the first playable faction. Its practical design
language uses refractory ceramic armor, dark structural iron, oxide insulation,
exposed pressure hardware, and small cyan charge indicators. Broad tracked armor,
wheeled scouts, paired generator vessels, and a tall siege mortar distinguish
roles by shape. Three upright bars over a crossbar form the prototype foundry
symbol. Player identification panels have their own remappable hue range.

The **Severance Combine** remains a possible future rival, not an implemented
roster. Autonomous or biological factions, infantry, walkers, squads, cover,
morale, heroes, and melee remain future design decisions. The first balance pass
uses Directorate against Directorate.

## Play

Build this checkout with its normal engine build workflow and install the RA
content required by the inherited mod. From the repository root, launch:

```sh
./launch-game.sh Game.Mod=pvphit
```

Host **Furnace Covenant — Pressure Station Nine** in the multiplayer lobby.
Two human players are required; the inherited AI has no build plan for this
roster. Each starts with a headquarters and 5,000 credits. Build a generator,
processor, then armor works. A processor includes one hauler. Use scouts to
claim the northern and southern pressure stations. Destroy the opponent's
required base structures or force a surrender; station ownership is not a
separate victory condition. Surviving vehicles do not postpone elimination.

The intended match length is 15–20 minutes, **not yet a measured balance result**.
The 96×96 battlefield uses inherited terrain with original slag, pipe sections,
and ruined walls. Resource fields, starts, and blocking wall positions have
rotational symmetry. Pipe artwork is decorative; walls block one cell.

Validation uses ignored, isolated runtime/content/settings under `mods/pvphit/.work/`.
The repeatable commands and prerequisites are in
[the motion workflow](docs/movement-art-direction.md). These files are local test
fixtures, not a replacement for the repository's supported installation process.

| Structure | Cost | Power | Function |
| --- | ---: | ---: | --- |
| Foundry Headquarters | Preplaced | +20 | Construction, build radius, radar |
| Pressure Generator | 500 | +100 | Supplies power |
| Slag Processor | 1,500 | −30 | Unloading dock, 3,000 resource storage, free hauler |
| Armor Works | 2,000 | −50 | Vehicle production and rally point |
| Pressure Metering Station | Capture | 0 | 25 credits approximately every 5 seconds |

| Vehicle | Cost | Role |
| --- | ---: | --- |
| Slag Hauler | 1,000 | Unarmed resource collector |
| Relay Scout | 450 | Fast vision, light gun, five-second station capture |
| K-6 Induction Tank | 1,000 | Tracked direct-fire armor with independently aimed turret |
| Brace Mortar Carrier | 1,400 | Long-range siege; must deploy to fire |

Select a scout and right-click a station to capture it; the scout survives.
Select a mortar carrier and press **F** (default deploy binding). Stabilizers
extend over two seconds. A move order withdraws them before movement resumes.
The mortar has a minimum range of two cells; protect it with tanks and scouts.
Existing low-power and production behavior remains active. Resource storage is
limited: build additional processors or spend stockpiles when storage fills.

## Laboratories

These maps can be launched directly from the repository root:

```sh
./launch-game.sh Game.Mod=pvphit Launch.Map=tank-proving-ground
./launch-game.sh Game.Mod=pvphit Launch.Map=foundry-systems-lab
./launch-game.sh Game.Mod=pvphit Launch.Map=foundry-visual-yard
```

The tank proving ground shows 32 hull directions in four player colors and a
row of independent turret directions. Red units are controllable. Move and
force-fire with Ctrl + right-click to inspect alignment and muzzle placement.

The systems laboratory places the complete roster, resources, a neutral
station, and a target building. Its Lua checks capture without consuming the
scout, income, harvesting/refinery delivery, and paid scout production through
the factory exit. Check the engine's `lua.log` or stdout for `FURNACE CHECK`.
Keep the laboratory running for about two minutes without spending or destroying
test actors until `systems suite complete` appears. It has no victory condition.
Use the mortar manually to test deployment, withdrawal, and forced attacks.

The industrial visual yard shows the refined HQ, generator and processor in
four player colors plus a damaged column, with the heavy K-6 and Armor Works
below. The purple column takes damage at 30 seconds and recovers at 45 seconds;
additional buildings assemble at 50 seconds. An automatic scout order exercises
the factory exit and shutter. Keep it running for two minutes to check repeated
processor dock departures and production. Paving is decorative; this is an art
laboratory, not a balanced map. Reproduce the expanded layout with
`tools/build_core_building_yard.py` (the older yard script restores its old layout).

## Asset pipeline

Editable sources and reproducible scripts live with the mod:

- `art/source/tank-prototype/`: preserved copy of the supplied tank and its
  original generation scripts. Those archived scripts contain legacy paths;
  use the new wrappers below for this mod.
- `art/source/roster/`: editable procedural Blender models.
- `tools/render_tank.py`: loads the preserved tank without saving over it,
  changes the material treatment, and renders separate hull, turret, and wreck.
- `tools/render_roster.py`: builds the remaining original blockout models and
  renders their sprites, construction frames, deployment frames, and wrecks.
- `tools/pack_assets.py`: assembles sheets, embeds PNG metadata using this fork's
  utility, generates icons, synthesizes WAV effects, and builds the flag atlas.
- `tools/build_maps.py`: reproduces the maps and map-scoped roster restrictions.

Run from the repository root after building `OpenRA.Utility`:

```sh
ALSOFT_DRIVERS=null blender -noaudio --background --python mods/pvphit/tools/render_tank.py
ALSOFT_DRIVERS=null blender -noaudio --background --python mods/pvphit/tools/render_roster.py
ENGINE_DIR="$PWD" python3 mods/pvphit/tools/pack_assets.py --dotnet dotnet
python3 mods/pvphit/tools/build_maps.py
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --map refresh '^(tank-proving-ground|foundry-systems-lab|pressure-station-nine)$'
```

The verified render environment was Blender 5.2.2 using Cycles CPU. The initial
blockout scripts used isolated background scenes when the MCP bridge was
unavailable. The subsequent refinement below was modeled and rendered through
the connected live Blender MCP bridge.
Pass a subset after `--` to `render_roster.py` to regenerate selected models,
for example `-- hq generator`. Intermediate frame directories are ignored by
git. Complete sheets, metadata, models, and scripts are retained.

Vehicles use 128×128 frames at sequence scale 0.5; buildings use 256×256 at
0.5. Orthographic scales are 4.9 and 9.8 respectively. The camera points from
south toward a shared ground anchor at roughly 42 degrees; fixed warm studio
lights and a neutral background illuminate pale armor against darker ground.
Body and turret share the anchor. Sequence offsets are `(0,-7)` for vehicles
and `(0,-14)` for buildings. These are visual offsets, not footprint sizes.

The model's forward direction is −Y. Source frames rotate around +Z in uniform
11.25-degree steps. Engine facing zero maps to source frame 16, followed by
17–31 and 0–15. Both `UseClassicFacings: false` and a normal `BodyOrientation`
replace the inherited classic facing treatment. Do not copy RA tank facings.

`PngSheet` is enabled in the manifest. Sidecars alone are insufficient: the pack
step calls `--png-sheet-import` to embed frame metadata. Team panels are rendered
green and shifted by `PlayerColorShift` through the separate `furnace-player`
palette. Cyan charge details remain cyan. Shadows are engine-generated sprite
shadows; wrecks are simple scorched forms. The refined tank and factory have
material wear; the factory also has operating fans and a retracting shutter.
Articulated tracks, more convincing wreck geometry, animations for the remaining
blockouts, voice acting, and final sound mixing remain future asset work.
The core HQ, generator and processor now also have operating, construction and
physical damage states; see the core-building workflow below.

### Blender MCP refinement

`tools/refine_visuals.py` creates independent scenes and copies the archived tank
geometry before editing it. It preserves the open default scene and original
source file. Ten editable scenes are saved under `art/source/refined/`.
The tank retains its shared body/turret anchors and uniform angular ordering.
The refined camera, lighting, scale and offsets match the existing pipeline.

Execute this Python through Blender MCP in a fresh session:

```python
import bpy, importlib.util
path = '/home/cye/Dev/OpenRA/mods/pvphit/tools/refine_visuals.py'
spec = importlib.util.spec_from_file_location('fc_visual_pass', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
bpy.app.driver_namespace['fc_visual_pass'] = m
m.build()
result = m.start_render('sprites')
```

Rendering runs through Blender timers; inspect `art/refined/render-status.json`
until `running` is false and `done` equals `total` (135). Do not start another
render or edit these generated scenes while the timer is running. The preserved
user scene is separate. To render presentation views afterward, call
`bpy.app.driver_namespace['fc_visual_pass'].start_render('previews')` through MCP.
Presentation views use red identification panels; sprite exports use green
remapping masks. Saved models retain the export materials.

```sh
ENGINE_DIR="$PWD" python3 mods/pvphit/tools/pack_refined_assets.py --dotnet dotnet
python3 mods/pvphit/tools/build_visual_yard.py
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --map refresh '^foundry-visual-yard$'
```

`sequences/refined.yaml` and `rules/refined.yaml` load after the earlier assets.
They use the fork's existing `WithProductionDoorOverlay` and player palette
support; no C# changes are needed. Construction remains a simple five-frame
assembly placeholder, and damage is a scorched material treatment. The source
meshes, preview renders, sheets, metadata and generation scripts are retained;
intermediate frame directories are ignored.

The subsequent `tools/heavy_visuals.py` pass replaces the tank and factory with
more imposing armor and fortified industrial silhouettes. It exports 127 frames
through Blender MCP, preserving the same scale, anchors, facing order and
gameplay. `sequences/heavy.yaml` loads last; removing this one manifest entry
restores the previous visuals. Editable sources are in `art/source/heavy/`.
See [heavy refinement notes](docs/heavy-art-direction.md) for its workflow.

### Core buildings

`tools/core_buildings_visuals.py` builds only the HQ, generator and processor in
independent Blender MCP scenes. It also loads hand-edited sources for export.
`tools/pack_core_buildings.py` validates and packs 39 frames, three player-color
icons and embedded PNG metadata without rewriting other roster assets.
Editable sources live in `art/source/core-buildings/`; sequence and icon palette
overrides load last. See [the complete workflow](docs/core-building-art-direction.md)
for source editing, rendering, the expanded yard and rollback.

## Implementation boundaries

All gameplay uses existing traits in this fork; no new C# traits were required.

| Feature | Implementation | Remaining work |
| --- | --- | --- |
| Harvesting and construction | `Harvester`, `DockHost`, `Refinery`, `Production`, classic queues; YAML | Economy and traffic balance |
| Territory income | `Captures`, `Capturable`, `CashTrickler`; YAML | Capture timing, denial and snowball playtests |
| Siege bracing | `GrantConditionOnDeploy`, `WithMakeAnimation`, conditional attack/mobile traits | Readability and counterplay testing |
| Separate hull and turret | `Turreted`, `WithSpriteTurret`, uniform PNG sequences | Wider directional muzzle review |
| Player colors | `PlayerColorPalette`, `PlayerColorShift` | More player colors and accessibility review |
| Victory and results | Inherited conquest/surrender plus existing `PvpHitOutcomeEmitter` | Authenticated platform end-to-end test |

`rules/furnace.yaml` adds actors without replacing the inherited RA roster.
`rules/slice.yaml` is loaded only by the prototype battlefield and systems lab;
it hides inherited production choices, sets the starting HQ and cash, and
selects the new faction. Existing RA maps remain available. Basic title and
faction-symbol branding is included; most chrome, loading artwork, announcements,
music, and terrain remain inherited. The flag atlas preserves inherited RA artwork and
adds the original Directorate symbol; it is not wholly new artwork.

## Next review

1. Play a human mirror match and record match duration, first contact, income,
   station control, and the effectiveness of scout/tank/siege counters.
2. Review the tank and roster at normal zoom before refining or adding units.
3. Refine the battlefield's industrial terrain and operating animations.
4. Run an authenticated PvPHit match through the deployed orchestration contract
   in an explicitly approved test environment before distributing a new build.

See `VALIDATION.md` for checks performed and remaining limits. No release was
published and no platform or orchestration configuration was changed.

### Refined support vehicles

The Slag Hauler, Relay Scout and Brace Mortar Carrier now have independent
editable Blender sources under `art/source/vehicles/`, directional wrecks,
matching icons and focused `vehicles.yaml` overrides. The scout retains its
separate turret; the mortar has five deployment stages with exact travel and
deployed endpoints. The subsequent motion pass adds harvesting and unloading
loops while keeping docking opening/closing callbacks at their original duration. See [vehicle models](docs/vehicle-models.png),
[native-zoom yard](docs/vehicle-yard.png),
[before/after directions](docs/vehicle-facing-comparison.png), and
[workflow and art direction](docs/vehicle-art-direction.md).

Use `tools/vehicle_visuals.py` through Blender MCP: `load_sources()` for existing
hand-edited models, `start_render('previews')` before `start_render('sprites')`.
The complete batch has 419 frames. `tools/pack_vehicles.py` validates the exports
and embeds PNG metadata without touching earlier assets.
`tools/preview_vehicles.py` reproduces the comparison images.

`tools/build_vehicle_yard.py` builds only `foundry-vehicle-yard`; its tracked
`yard.lua` supplies the checks. Launch with `Launch.Map=foundry-vehicle-yard`
and `Graphics.ViewportDistance=Native`. The separate map checks capture,
resource deliveries, artillery range restrictions and all three factory builds,
then tours full directional and wreck grids. The expanded core-building yard
is preserved. Consult `VALIDATION.md` for the acceptance results and limitations.

### Movement, weapons and destruction

The hauler, scout, K6 and siege carrier have four-frame movement loops. The
hauler collector and unloading gate animate; its hopper residue remains cosmetic.
Ballistic, induction and pressure weapons have distinct shot-driven flashes,
projectiles and impacts. Short death effects lead into the directional wrecks,
including a revised K6 wreck. Weapon statistics and husk behavior are unchanged.

The factory-produced siege stall is corrected without removing deployment's
`WithMakeAnimation`. One engine null guard also protects `WithMoveAnimation`
when a conditional body has never played a sequence.

Use the saved animation copies in `art/source/motion/` for this pass. Original
refined sources remain preserved. See [native directions](docs/vehicle-motion-directions.png),
[movement](docs/vehicle-movement.gif), [working loops](docs/vehicle-working.gif),
[weapon effects](docs/vehicle-weapon-effects.gif), and [source/export instructions](docs/movement-art-direction.md).
[Gameplay footage](docs/vehicle-fire-withdrawal.gif) shows firing and withdrawal
at native zoom; [the final yard](docs/vehicle-motion-yard.png) retains four colors.
The vehicle yard now produces three siege carriers, verifies actual exit and
six firing/withdrawal cycles, and exercises docking interruption and destruction
in animation states. Its directional tour begins at 305 seconds; final assertions
run at 360 seconds. See [validation results](VALIDATION.md) for measured coverage.
