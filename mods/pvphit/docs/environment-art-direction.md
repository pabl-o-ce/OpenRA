# Pressure Station Nine — ashbound transfer yard

The selected treatment uses muted ash, broad concrete transfer aprons, refractory
service walls and low pressure hardware. Pale roster armor and ownership panels
remain the strongest moving shapes. No global darkness, fog tint or post-process
grade is added. Ash is flat and dull; harvestable slag remains visibly piled.
The alternatives considered were monumental refractory plant ruins (more
occlusion and routing work) and an open extraction pipefield (cheaper but weaker
landmarks). This pass implements the transfer yard only.

## Layout and gameplay changes

The playable bounds remain `(1,1,96,96)` within a 98×98 rectangular map.
Headquarters spawn markers are `(14,48)` and `(83,48)`. Their actual 3×3 buildings
start at `(13,47)` and `(82,47)`. Matching north/south coordinates account for
the fixed south-facing production exits and processor docks.

Home fields are radius-four disks at `(23,53)` and `(74,53)`. The radius-five
contested disks are `(48,29)` and `(49,68)`. Moving these fields changes economic
access; their shapes, quantities, resource values and harvest timing remain
unchanged. Calculated effective deposits are 398/686 resource units per
home/expansion, respectively, before player modifiers: 54,200 nominal credits
across the map. ResourceLayer recalculates density from neighbors at load.
The contested centers moved three cells inward from the initial sketch to keep
four resource/obstacle-free cells around every side of each station footprint.

Both 2×2 stations have top-left x=48, at y=18 and y=78. Neither station footprint
was moved in this pass: those were already horizontally centered. The former
east spawn was one cell farther south; only its y position changed. Claims of
rotational station symmetry in early documentation were inaccurate.

```
                  NORTH METER / low pipe line
                     contested slag
           north branch             north branch
               broken service walls
 WEST PAD ======== TRANSFER APRON ======== EAST PAD
 home slag                               home slag
               broken service walls
           south branch             south branch
                     contested slag
             SOUTH METER / broken manifold
```

Paved base reserves are x=5–29 and x=68–92, y=36–65. The 14-cell-deep central
apron is y=42–55. Eight-cell-wide vertical branches join the broad north/south
station aprons. Ash shoulders remain fully traversable: visual routes are
navigation landmarks, not hidden movement restrictions. Four six-cell horizontal
wall clusters at y=36/61 leave a twelve-cell central opening, accessible ends and
outer flanks. The generator and static report specify exact cells.

Reference opening placements have been checked geometrically for footprints,
14-cell HQ build radius, two-cell adjacency and clear south aprons. West
generator/processor/factory anchors are `(17,45)/(20,42)/(13,51)`; east anchors
are `(79,45)/(75,42)/(82,51)`. These are examples, not forced player placements.
Both reference openings also passed actual paid sidebar production and placement
orders in independent local tests. Alternative layouts still need human review.

The existing mortar retains its 2–9.5-cell range. Ruins block movement only; they
are not cover, projectile blockers, destructible walls or resource sources.
The laboratory exercises an exposed siege position beside a wall and a scout
approach around it. No building, weapon, capture, victory or economic trait values
are changed. The main map has no test script or economy overrides.

## Kit and actual terrain pipeline

There are 24 original opaque 24×24 ground frames: four ash, four paving, two
damaged paving, four straight transitions, four outer corners, four inner corners
and two flush drains. Damage shares the paving boundary. Explicit adjacency in
the map generator selects transition frames; narrow/ambiguous paving raises an
error instead of silently selecting a broken seam. Ash/paving variations agree
at corresponding tile boundaries. Their small noise does not imply elevation.

`environment_ground.py` is the editable procedural ground source. It uses a
planar pixel grid, not the vehicle camera. It writes RGBA PNG with embedded
`FrameSize: 24,24` and `FrameAmount: 24`. New templates 60000–60023 use explicit
frame indices and Clear terrain. They are not PickAny, so regeneration retains
the selected variants. MinColor/MaxColor define minimap colors independently
of the texture. Resource overlays still supply Ore behavior on occupied cells.

The manifest selects `tilesets/temperat-industrial.yaml` instead of RA's original
TEMPERAT entry. The generated file begins with the exact original bytes, then
appends templates; the inherited hash is recorded and verified. The loader does
not merge duplicate tileset IDs. Shared RA files, original IDs, palettes and
terrain types are preserved. Existing maps retain their original artwork.
The cache loads every template, so other TEMPERAT maps launched through PvPHit
also allocate the added ground atlas. The standalone RA mod is unaffected.

Verified engine path: DefaultTerrain reads Images/Frames; DefaultTileCache uses
FrameCache and registered sprite loaders, allocates the appropriate sheet type,
then TerrainRenderer draws through TerrainSpriteLayer. PngSheet supports RGBA
frames. The native engine sample confirms this path beyond source inspection.
Ground has scale 1 and offset zero. It does not use sprite sequences or the
vehicle `(0,-7)` offset. No TMP encoder or engine patch is required.

The ten modeled props are four low single-cell wall variants, four low pipe
variants, an extraction skid and a broken manifold. There are 24 blocking wall
actors and 79 decorative actors on the battlefield. Ground has zero actors.
Non-occupying machinery sits outside the central fighting/hauling paths. The
existing capturable station and resource sprites are retained. The station pads
reuse the ground kit. No smoke/steam actors are enabled in this pass.

## Reproduction and source ownership

The live MCP bridge at localhost:9876 was unavailable. Blender MCP's
`execute_blender_code_for_cli` was verified with Blender 5.2.2 and used for the new
sources and renders. It opens a background process; it does not alter a live
session. The common studio helper supplies established camera, lighting and
materials, with 128×128 prop exports at sequence scale 0.5 and offset `(0,-7)`.

Use a non-environment input file, such as the retained refined pipe source, for
the background MCP call. This avoids Blender's prohibition on appending a scene
from its currently open file. Run:

```python
import importlib.util
p = '/home/cye/Dev/OpenRA/mods/pvphit/tools/environment_visuals.py'
s = importlib.util.spec_from_file_location('fc_environment', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
result = m.export()  # loads saved environment scenes without resaving them
```

`build()` is first-creation only and refuses to replace existing sources. Sources
are under `art/source/environment/`; exports and per-asset source/image hashes
are under `art/environment/props/`. `pack_environment.py` validates hashes,
canvas dimensions and alpha margins before writing map-scoped rules/sequences.
Existing motion, vehicle, heavy and building sources are untouched.

From the repository root:

```sh
python3 mods/pvphit/tools/environment_ground.py
python3 mods/pvphit/tools/pack_environment.py
python3 mods/pvphit/tools/build_environment_maps.py --target sample
# Review the sample at Graphics.ViewportDistance=Native before battlefield work.
python3 mods/pvphit/tools/build_environment_maps.py --target battlefield
python3 mods/pvphit/tools/build_environment_maps.py --target checks
python3 mods/pvphit/tools/check_environment.py
ENGINE_DIR="$PWD" XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  mods/pvphit/.work/dotnet/dotnet bin/OpenRA.Utility.dll pvphit --map refresh \
  '^(pressure-station-nine|foundry-environment-sample|foundry-environment-checks)$'
```

Use `--output-root /tmp/environment-staging` with the ground/map generators to
review outputs before installation. `checks` requires `battlefield` in the same
output root. The new build_maps CLI requires `--target`; its battlefield target
delegates to the current generator. Existing lab generators and slice rules are
preserved; no multi-map generation is implicit.

## Performance and acceptance boundaries

The original inherited indexed terrain atlas is retained. Adding RGBA terrain
introduces a separate atlas (1024×1024×4 = 4 MiB texture payload at this sheet
size), plus renderer bookkeeping and prop sprites. This is not a measurement of
total GPU/CPU memory. Static actors still incur visibility/render work, but no
per-cell decorative actors or ambient animation ticks are introduced. The two
stations retain their original behavior. Optional steam remains deferred until
hardware-display performance review justifies it.

See [validation evidence](validation/environment/README.md) for what was actually
run and what remains human acceptance work. Basic native fog/selection and paid
opening-placement checks passed. Human matches, hardware performance and broader
visual accessibility must not be inferred from the automated suites.
