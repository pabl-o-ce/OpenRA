# Prototype validation

Verified on 2026-10-13 against this checkout on
`pvphit-release-20250330`. These are prototype acceptance checks, not a claim of
production readiness or competitive balance.

## Engine and static checks

- Rebuilt the current fork successfully: zero build errors; three warnings
  about the existing .NET 6 target being out of support. SDK 8.0.425 and runtime
  6.0.36 were installed under `/tmp/furnace-dotnet` for this session.
- Full `pvphit --check-yaml` passed, including inherited RA maps and all three
  prototype maps. Final targeted map checks passed after faction setup changes.
- `pvphit --check-missing-sprites` passed for SNOW, INTERIOR, TEMPERAT and DESERT.
- Python generation scripts compile; `git diff --check` passes.
- The copied original tank model, specification, and three source scripts match
  the supplied originals byte for byte.
- All tracked changes are inside `mods/pvphit/`. Shared RA source, platform
  services, orchestration configuration, release versions, and account/result
  integration code were not modified.

## In-game checks

Tests used isolated Xvfb displays and Mesa software rendering with separate
temporary support directories. The user's running desktop, Blender scene,
normal game settings, and account identity files were not used.

- Tank proving ground: 32 uniform hull directions, independent turret sample
  row, player-color panels in red/blue/yellow/purple, movement, aiming and firing.
  Cyan material remained outside the player-color remap range.
- Systems lab: original building and vehicle sprites, shadows, build icons,
  original resource art, basic weapon effects and directional layering loaded.
- Automated Lua assertions passed for station capture, surviving capture scout,
  income, hauler delivery, and paid scout production through the factory exit.
  Starting lab power was 120 supplied and 80 consumed. The final run used the
  Kiln faction and reached `FURNACE CHECK PASSED: systems suite complete`.
- Manual siege check: F extended the stabilizers; a move order withdrew them
  before travel; forced fire at a building within range reduced its health.
- Multiplayer smoke test: two separate clients connected to an unadvertised
  dedicated server, selected the Kiln faction, and started with headquarters
  and 5,000 credits. Generator and processor placement, prerequisite unlocking,
  free hauler harvesting, construction spending, and factory build completion
  worked. The longer test ran for about five minutes with both clients before
  the first Xvfb display closed and disconnected its client. No desync was
  reported before that interruption.
- A separate fresh two-client surrender test completed normally. Both clients
  displayed the same winner/loser, and the unchanged emitter wrote exactly one
  event with `state: final`, `reason: result`, `mod_id: pvphit`, and outcomes
  `Won` / `Lost`. Neither player had disconnected before that result. The test
  used anonymous local players: profile IDs and fingerprints were null.
- The completed server replay played back to the same winner/loser screen
  without a reported exception or desync. The emitted stdout event matched the
  JSON file, and the server logged only one outcome event for this test UUID.

The final result test used UUID `17de06e7-072f-44a0-984e-3108eab7febc` and map
UID `a9f2fbf4b1326baf2ee5a7234bcaaaa9d47654bf`. Its outcome and replay were
written only under `/tmp/furnace-support/`; no backend settlement was requested.

The multiplayer test exposed and corrected requirements not caught by YAML
lint: default-rule faction registration for the lobby, explicit starting-unit
faction membership, a sidebar suffix mapping, and power-of-two chrome textures.

## Remaining acceptance work

- A human mirror match to validate the 15–20 minute target, build orders,
  expansion timing, objective income, siege counterplay, and both starting sides.
- Crowded combat, pathfinding around factories and wrecks, larger armies,
  additional player colors, and prolonged multiplayer stability.
- Visual review on the user's actual display, zoom and graphics hardware;
  audible mixing review. Automated rendering used a null audio device.
- Final asset polish: terrain, construction/operating animations, tracks,
  loading/unloading motion, damaged forms, wrecks, spoken voices, and UI.
- Authenticated PvPHit account/profile lookup, deployed match orchestration,
  and backend settlement. Local anonymous clients cannot verify those paths.
- Broader elimination/disconnect/desync scenario coverage. A short local test
  cannot establish balance, absence of desyncs, or release readiness.

## Blender MCP visual pass — 2026-10-13

The live Blender MCP bridge connected successfully to Blender 5.2.2. Procedural
modeling and all 135 sprite renders ran in that live instance through MCP.
Ten separate editable scenes were saved under `art/source/refined/`; six
presentation renders were also generated. The existing default scene still
contains its original Cube, Camera and Light at their original positions.
The archived tank source still matches the supplied `.blend` byte for byte.

This pass refines the K-6 tank, Armor Works and a small industrial art laboratory.
It adds ceramic panel seams, textured materials, oxide hardware, factory fans,
a production shutter, damage/construction frames, tank wreck directions, four
props and four paving modules. Original sources and earlier sprites remain.

Verified with this fork:

- Full mod YAML lint and missing-sprite checks passed for all four tilesets.
  Targeted yard lint passed again after the icon palette correction.
- Live yard at normal RTS zoom: four player colors, independent tank layering,
  movement, contrasting normal/damaged factories, ground sorting and prop scale.
  The controllable tank aimed and force-fired at the blue generator until it
  was destroyed; cyan shot/impact art remained separate from team colors.
- The Lua check logged `VISUAL YARD PASSED: refined factory produced a scout`.
  Recorded close-up frames show roof fans turning and the shutter retracting
  during exit and returning closed afterward. See [door capture](docs/factory-door.gif).
- The Armor Works build icon uses the player's color after switching its icon
  palette. The tank's icon and inherited vehicle icons use the same setting.
- Python compilation and whitespace checks passed. No engine, platform,
  orchestration, release metadata or account/result contract changes were made.

See the [yard screenshot](docs/industrial-yard.png) and
[Blender model previews](docs/refined-models.png). These are art/production
checks, not another multiplayer acceptance run. The new construction and wreck
frames were exported and validated for loading; their full transitions still
need manual review. The paving and props are decorative actors over inherited
terrain, without changed movement costs or collision. Other roster models,
terrain beyond this yard, UI and audio retain the earlier prototype treatment.

## Heavier silhouette pass — 2026-10-13

Blender MCP produced the next tank and factory revision in separate `FC3`
scenes. All 127 sprite frames completed. After live review, nine factory damage
frames were rerendered with scorched supports and a collapsed exhaust crown;
the earlier damage treatment was too similar to the darker intact building.
Two presentation views and independent editable sources are retained under
`art/heavy/` and `art/source/heavy/`.

- The visual-yard YAML check passed with warnings treated as errors.
- Missing-sprite checks passed for all four tilesets. One concurrent utility
  launch initially failed to create CoreCLR; the subsequent run completed.
- The live yard showed the new tank directions, four player colors, turret/body
  layering, and visibly distinct intact/damaged factories at normal zoom.
- The production assertion passed again with the heavier entrance geometry.
- Python compilation and whitespace checks passed. The original tank hash,
  previous refinement scenes and default Blender scene are preserved.

Review [heavy models](docs/heavy-models.png), the
[live yard](docs/heavy-yard.png), and
[sprite comparison](docs/heavy-facing-comparison.png) (earlier pass above,
heavier pass below; green panels are export remap masks).

This revision changes artwork and sequence paths, not gameplay statistics or
engine code. Construction and tank wrecks still use the earlier simple animation
approach. No new multiplayer or platform settlement test was performed.

## Repeating the checks

With the repository's supported runtime, a built utility, and required RA
content available:

```sh
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --check-yaml
ENGINE_DIR="$PWD" dotnet bin/OpenRA.Utility.dll pvphit --check-missing-sprites
git diff --check
```

See `README.md` for laboratory launch and asset-generation commands.
