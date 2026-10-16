# Step 4 environment evidence

This folder separates executable checks, captured visual review and outstanding
human acceptance. No result here establishes competitive balance.

## Retained baseline and reproducibility

- `pressure-station-nine-baseline.oramap` contains the exact Step 3 map files
  from `b53989f9651fc0618e0f036b52f8db6c26601363`, before any edits or refresh.
- `before-sha256.json` records the pre-change mod and shared RA files. The
  static checker permits only the declared battlefield/manifest/docs/entrypoint
  changes. Existing labs, generators, slice rules, weapons and all earlier
  source/export assets are checked against these hashes.
- `static-checks.json` records effective resource quantities, geometric routes,
  footprint/adjacency/radius/apron checks, actor counts and fresh-root generation
  checks. Geometry is not engine timing; the candidate test supplies timing.
- `source-reproduction.json` records zero differing RGBA pixels for all ten
  props after freshly loading and rendering their saved Blender sources via MCP.
- `map-reproduction.json` verifies all three new/updated maps byte-for-byte
  after generation and current-engine refresh, including previews.
- `runtime-checks.json` and `candidate-checks.log` retain the final candidate
  run: all fifteen arrival pairs within 2.5%, three twelve-tank groups out/back,
  ten actual production arrivals and at least ten observed deliveries per side.
- `candidate-checks-map.oramap` preserves the exact test-map bytes loaded by that
  run, before YAML normalization. It is a test fixture, not a competitive map.
- `vehicle-yard.log`, `systems-lab.log` and `core-building-yard.log` retain passing
  unchanged regression suites. `yaml.log` and `sprites.log` retain current-engine
  checks, including all four tilesets.
- Ground/source/PNG receipts live alongside exports under `art/environment/`.
- `artifact-sha256.json` identifies the final changed/new files and the local
  engine binaries used for validation. It excludes itself and ignored raw captures.

The baseline is an archive, not a second new battlefield. To compare it in-game,
copy it into an isolated support map directory. For an unambiguous lobby label,
extract a temporary copy named `pressure-station-nine-baseline` and append
`[Step 3 baseline]` to its Title. Keep the original archive unchanged. Do not
replace the active candidate or overwrite the original laboratories.

## Automated coverage

The native sample checks capture without scout consumption, harvesting and actual
arrival of a produced siege carrier beyond the factory. The candidate laboratory
uses the real battlefield binary, stations and blocker cells. Access measurements
precede dynamic construction/traffic. It then creates reference opening buildings
and runs production, harvesting and routing checks. Direct actor creation does
not itself prove that a human's build cursor accepts a placement; static checks
separately account for the inherited two-cell adjacency and HQ range.
The additional `opening-west.log` / `opening-east.log` runs use real sidebar
clicks and placement orders, then assert all three resulting building locations.
They passed at unchanged prices/timing; matching PNGs show the completed openings.
These are independent local single-player tests, not a multiplayer match.

Candidate checks cover scout, tank and siege travel from each HQ's south staging
cell to home slag, both expansions and both station approaches; three independent
twelve-tank groups traverse the north, central and south routes both ways. A
produced hauler/scout/tank and two siege carriers per side must reach destination
cells. Both haulers must deliver, with at least ten aggregate dock departures per
side after observed resource increases. The lab clears storage periodically to
continue observing trips; the playable map does not.

The siege test injects real deploy/withdraw input, checks preserved damage and
withdrawal before translation, and sends a scout around the wall into minimum
range. Capture uses the unchanged station and scout traits. The existing vehicle
suite supplies the broader minimum/maximum range and animation-state regressions.

The harness measures the nearest home field edge before spawning economy
buildings. Comparisons are single controlled runs, not a guarantee over every
pathfinder tie or gameplay traffic mix. Dynamic hauling traffic is tested later.

`compact-rally-failure.log` and its matching map archive retain a failed return
test: one tank stopped at `(27,37)` while the adjacent-cell parking grid sealed
its exact destination `(27,39)` behind already parked tanks. The final harness
uses a cell of separation between rally destinations, retaining all 36 tanks,
the same route waypoints, exact arrival assertions and 100-second leg limits.
This is a test-fixture correction, not an engine or battlefield pathfinding fix.
Dense parking and player-created congestion remain human acceptance cases.

Reproduce from the repository root with the installed content/runtime:

```sh
python3 mods/pvphit/tools/check_environment.py \
  --output mods/pvphit/docs/validation/environment/static-checks.json
ENGINE_DIR="$PWD" XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  mods/pvphit/.work/dotnet/dotnet bin/OpenRA.Utility.dll pvphit --check-yaml
ENGINE_DIR="$PWD" XDG_CONFIG_HOME="$PWD/mods/pvphit/.work/config" \
  mods/pvphit/.work/dotnet/dotnet bin/OpenRA.Utility.dll pvphit --check-missing-sprites
python3 mods/pvphit/tools/run_visual_checks.py --map foundry-environment-sample \
  --tag environment --display :108 --seconds 180
python3 mods/pvphit/tools/run_visual_checks.py --map foundry-environment-checks \
  --tag environment-final --display :109 --seconds 1000
```

Use unused displays. The runner isolates settings/content, disables advertising
and removes `PVPHIT_MATCH_ID` from its environment. Raw videos and logs live under
ignored `.work/`. No authenticated settlement or account linking is exercised.

## Native review and performance

`native-sample.png` is an unscaled engine capture of the original ground kit with
the roster, resources, all ten prop variants and a station. The review tool creates
a private copy; it never alters the playable map:

```sh
python3 mods/pvphit/tools/review_environment.py --variant fog --display :113
python3 mods/pvphit/tools/review_environment.py --variant full --display :113
python3 mods/pvphit/tools/review_environment.py --variant no-props --display :113
python3 mods/pvphit/tools/review_environment.py --variant opening-west --display :113
python3 mods/pvphit/tools/review_environment.py --variant opening-east --display :114
```

For performance comparison run full/no-props serially with other game instances
closed. Each captures the same view at 20/30/40 seconds with the engine's timing
overlay and process RSS. This is a small Linux/Xvfb/llvmpipe comparison with a
30-FPS cap, not hardware-display or cross-platform performance certification.
There is no ambient animation to benchmark: optional steam was deferred.

The retained full-scene render snapshots were 12.6/12.9/25.0 ms, compared with
11.9/11.8/11.8 ms without props; simulation snapshots were 0.1–0.2 ms. The full
view had a 25 ms spike and briefly reported 29 FPS against the 30 FPS cap.
`performance.json`, the six full captures and `performance-counters.png` retain
all readings. Three snapshots are insufficient for a robust performance budget.
This comparison preceded the final three-cell inward adjustment of the contested
fields; its ground kit and 103 static prop actors are the same as the final map.

`native-north.png`, `native-south.png`, `native-east-base.png` and
`native-central.png` show the final candidate at native zoom.
`native-fog-selection.png` shows an actually selected K6 against the new ground
and unrevealed terrain. `siege-flank.gif` is an unscaled crop from the final run,
showing real deploy/fire/withdraw input and the nearby flank approach.

## Human acceptance — not performed by these scripts

Run at least six candidate games with two controlling humans, in three
side-swapped pairs, plus a side-swapped baseline pair. Keep starting cash,
game speed, handicaps and the chosen player pair fixed within each pair. Retain
the exact map and replay for every match. One controller plus an observer does
not satisfy this requirement.

Use `human-matches.csv` to record first contact and first capture, cumulative
north/south control time, deliveries, expansion timing, congestion incidents,
duration, winner and starting side. Use replay statistics for resource flow;
annotate the time range used. Do not turn intended 15–20-minute games into an
assertion that this duration has been established.

Before signing off, test alternative opening layouts, deliberately obstructed
rally/dock approaches, depleted resource transitions, fog/scouting denial,
selection through prop overlap, projectile contrast, and the usefulness and
counterplay of siege positions on a hardware display. Repeat paired matches
after layout changes. Repeated side advantage is grounds for revision even if
geometry and scripted tests pass. Cross-platform play and authenticated PvPHit
settlement remain unproven and outside this pass.
