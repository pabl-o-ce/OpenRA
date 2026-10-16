# Retained FC6 validation evidence

`vehicle-yard.log` is the final standalone current-yard run. `systems-lab.log`
and `core-building-yard.log` are current-engine regression runs.
`multiplayer-controller.log`, `multiplayer-observer.log` and `replay.log` retain
the matching local two-client/replay traces. Their map predates the later
world-position tightening of the harvest-death test; the final standalone log
covers that refinement. `local-determinism.json` records the comparison and scope.

`local-two-client.orarep` and `local-replay-map.oramap` form a reproducible pair.
The archived map's UID is `8a037ddd987da9a24cda00ef012667639b263291`.
Commands, prerequisites and display isolation are documented in
[the motion workflow](../../movement-art-direction.md).

`before-FC*.yaml` are pre-polish resolved weapon baselines for
`tools/check_motion_balance.py`. `economy-comparison.txt` records the unchanged
resource-update and departure schedule before the late test-only ore extension.
`source-reproduction.json` compares fresh saved-source renders with packed inputs.
`preserved-sources.json` hashes the unchanged original refined Blender files.
`artifact-sha256.json` hashes current sources, sheets, metadata and sequence files;
per-frame hashes live in each exported asset's own manifest.

`rebuilt-yaml.log`, `rebuilt-sprites.log` and `build.txt` retain static/build output.
See [VALIDATION.md](../../../VALIDATION.md) for results and limits. Raw captures and
runtime dependencies remain in ignored `.work/`; selected native-size images and
GIFs are retained under `docs/`.
