# Step 7 retained evidence — 2026-10-17 UTC

**Controlled handoff: NO-GO.** OpenRA Step 7 work is recorded on `pvphit-release-20250330`;
sibling changes remain uncommitted. Human tests remain unperformed. Authenticated end-to-end platform acceptance,
physical hardware/listening/accessibility and the reviewed environment fixture correction
remain open. See [status, flow, installation and gates](../../step7-controlled-build.md).

## Automated results

The local self-contained Linux candidate is `fc-local-30fa940-step7.2`, built from
OpenRA `30fa940bbf0af679a151f8111409ba6dbd668153`. Its only post-build data edits are
isolated version stamping and the explicit private identity endpoint. Source gameplay,
assets and C# are unchanged. [checks.json](checks.json) records artifact/image hashes,
map identity, counts and limits. Shared runtime hashes cover the engine as well as mod.

- Rust: 330 unit, 73 API, 8 evidence-recovery and 10 other integration tests passed;
  strict clippy passed. SQLx created disposable databases on local PostgreSQL 17.11.
- Platform: all 19 suites / 217 tests passed, including real-DB concurrent completion,
  rollback/retry and identity repository tests. HTTP pricing and socket output were mocked.
  Frontend/backend type checks passed. Prisma was generated in the isolated clone only.
- Engine: 21 notification/resource/formatting tests and 23 outcome-contract tests passed.
- Packaging: three allowlist/symlink/version-stamping checks passed; archive inventory verified.
- Candidate .2: full YAML lint and four-tileset sprite checks passed. Building, systems and
  vehicle laboratories completed. Systems uses byte-identical `systems.lua` copied into its
  private test map because the source fixture refers to another development map; none of
  those laboratory files ship in the candidate. No assertion was removed or relaxed.
- Candidate .2: two controlling automated clients and replay produced matching
  `2500,2500,95000,81250,46,52,50,52` scenario measurements. These are resource/target/position
  checks, not an authenticated competitive winner or a human match. Both clients ran on
  one Linux/Xvfb/llvmpipe host. The map is the retained presentation-network laboratory,
  not a claim that a full competitive game on Pressure Station Nine was accepted.
- Candidate .2 server image: matching engine/mod/map startup remained running with networking
  disabled; a wrong expected release exited 78. No authenticated connection was attempted.
- Fresh install on candidate .1 (same gameplay/runtime as .2): [empty-support installer](installer.png)
  → supported Quick Install downloaded 39 content files → [Furnace setup screen](download-final.png).
  Candidate .2 YAML/sprite checks then used that freshly installed content. Installer UI
  retains inherited RA attribution. The local update/rollback check is recorded separately;
  this does not establish account-linked update compatibility on physical hardware.

The build reports the existing net6.0 EOL warning and NuGet.CommandLine 6.12.1 advisory.
The candidate intentionally does not include dependency/version upgrades in the source.

## Congestion classification

Original evidence is unchanged in `../presentation-completion/foundry-environment-checks.log`.
[congestion-manifest.json](congestion-manifest.json) identifies the original replay, seed,
map and hashes. Current binaries reproduced `stranded tank 31 at 30,59` / `groups-back`.
A clean archived 833a83543e environment baseline reproduced the same failure using its
matching mod and engine. All 15 travel routes and ten production outputs preceded it;
later assertions were not reached. A current-mod/old-engine attempt failed on incompatible
presentation traits and is explicitly NOT comparative gameplay evidence.

The [diagnostic excerpt](congestion-excerpt.log) establishes the cause of this assertion:

1. Tank 31 is actor 180 (outbound destination 70,60, return destination 29,60).
2. At simulation tick 9864, Move reports `CompleteDestinationReached` at 29,60.
3. In that SAME tick, Mobile receives a friendly blocking notification from actor 184
   (tank 35), observes actor 180 idle and queues Nudge.
4. At tick 9898, the nudge completes at 30,59. The later Lua poll never recorded a frame
   with both the final location and idle state, so its remembered arrival remains false.
5. The unchanged timeout assertion consequently fails. This is not evidence that tank 31
   failed to find or traverse the route; it is an arrival-observation race in the lab.

[diagnostic-only.patch](diagnostic-only.patch) records instrumentation applied ONLY in the
archived `/tmp` checkout. First diagnostic playback used normal speed; the second added
only unsynced replay speed to accelerate the same command stream, and reproduced the same
arrival/nudge ticks and failure. No diagnostic C# changes are applied to the working engine.

[proposed-congestion-fixture.patch](proposed-congestion-fixture.patch) is a separate review
artifact, **not applied**. It asserts exact location when each queued Move completes, so
passing through a goal is not sufficient and a blocked/cancelled move still fails. All
36 tanks, waypoints, destinations and the 100-second timeout are unchanged. Review is pending;
no corrected-fixture pass or completion of the later environment checks is claimed.

## Private raw evidence and artifact locations

- `mods/pvphit/.work/step7-evidence/`: complete scoped build/test logs, failure reproductions,
  diagnostic logs and the exact applied sibling patches. `applied-patches.json` records
  hashes; applied repository files were byte-compared with the tested clones.
- `mods/pvphit/.work/step7-candidates/fc-local-30fa940-step7.2/`: candidate archive, full
  manifest, SHA256SUMS, corresponding source, dependency inventory and exact builder copies.
- `mods/pvphit/.work/presentation-network-step7package2/`: both peer logs/audio/captures,
  private fixture maps, replay, replay log and checks.json.
- `mods/pvphit/.work/step7package2-*`: building and vehicle recordings/settings/logs;
  `step7package2mounted-systems-lab*`: systems fixture with shared script mounted locally.
- Original environment replay/captures remain in the previously recorded `.work` paths.
  `/tmp/furnace-step7/baseline/sha256.json` inventories the initial copied baseline;
  the new congestion manifest retains the original replay hash in repository evidence.

The `.work` files are local private evidence, not a download channel. No upload or tester
contact took place. The disposable database was stopped after testing; smoke containers
were removed. Local candidate images are retained for further isolated checks. Raw replays
and support directories may contain identity/handshake material: share only through the
agreed private diagnostic path, and never copy them wholesale into distributions.

## Open acceptance

Full authenticated linking/join/result/webhook/platform/cleanup flow; failure injection on
that live local stack; hardware display/audio/observer coverage; six candidate human games
plus a side-swapped baseline pair; and a reviewed complete environment rerun. A private
local CA/origin, two physical Linux machines, test accounts and the human review owner must
be configured/recorded before those gates can close. No Windows/macOS or public-release
claim follows from the evidence here.
