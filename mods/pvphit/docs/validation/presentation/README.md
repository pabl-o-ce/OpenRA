# Step 5 sample — evidence and limits

Baseline: clean `833a83543e` on `pvphit-release-20250330`. Step 4 was already
committed when implementation began. This pass does not commit or publish work.

## Review artifacts

- `sample.mp4`: actual local engine audio and video, including real selection,
  move and force-attack input, verified target damage, actual low power, and a
  twelve-additional-tank crowded segment. The alert collision uses scripted
  calls to the existing notifications; it is not proof of paid production.
- `native-warning.png`: real low-power notification, deficit and amber icon at
  1280x1000 / 100%. `sample.log` and `sample-events.json` identify the sequence.
- `minimum.png`: 1024x720 / 100% snapshot with the deficit and power tooltip.
- `hidpi.png`: 2560x1440 / 200% snapshot with selected tank and power tooltip.
  These two early endpoint captures predate the runner's simulation-completion
  requirement. They establish rendering only, not a complete scenario pass.
- `checks.json`: source reproduction, PCM headroom, resolved weapon comparison,
  and captured audio measurements. `yaml.log` / `sprites.log` retain engine lint.
- Full capture WAVs, videos and private map copies remain under `.work/presentation-*`.
  The first run had an input-marker parsing error; early sample captures used a
  non-forced attack on a noncombatant target. Neither is accepted as real combat
  input evidence. The retained final sample uses force attack and asserts damage.

## Checks observed

The Release solution build passed with zero errors and the three pre-existing
.NET 6 end-of-support warnings. It used SDK 8.0.425, single-node MSBuild and
`UseSharedCompilation=false`; the initial parallel solution invocation failed
without a diagnostic in this sandbox. The project runtime remains unchanged.

Five `NotificationQueueTest` tests passed: coalescing/interruption, capacity and
priority/FIFO, expiry, clear on mute/world transition, source-start failure, and
opt-in parsing/legacy defaults (some scenarios share a test). NUnit/VSTest required
a local loopback socket outside the sandbox. These are fake-audio policy tests;
they do not certify the speakers or operating-system audio backend.

Full pvphit YAML lint and missing-sprite checks passed for SNOW, INTERIOR,
TEMPERAT and DESERT. All twelve WAVs, three PNG densities, chrome YAML and source
manifest reproduce byte-for-byte into an empty output root. PCM samples have
headroom with no clipped samples. Resolved induction/scout/mortar weapon fields
match the retained baseline apart from explicit image/audio presentation fields.
A baseline comparison also confirmed all 96 tracked files under maps, model
sources, sequences, rules and weapons were byte-identical to HEAD; presentation
is added through new override files.

The hidden and explored-but-fogged engine captures have peak magnitude 1 after
startup (OpenAL's 16-bit dither floor). The visible control at the same camera
position has peak magnitude 13232. All three include scripted firing and target
destruction. This is measured visibility evidence for those paths, not listening
approval or proof of every deployment/ownership/observer edge case.

The fully muted scenario completed real command/combat input and showed the
low-power text and indicator (`muted-warning.png`); recorded output stayed at
the backend dither floor. The unchanged systems laboratory also passed capture,
surviving scout, income, harvesting/refinery delivery and paid production/exit
(`systems-lab.log`). The unchanged core-building yard passed production,
construction/damage-state exercises and repeated unloading/departure
(`core-building-yard.log`). The complete vehicle yard passed paid production/actual
exit, three produced siege carriers firing/withdrawing twice each, interrupted
docking recovery and six animation-state destruction cases (`vehicle-yard.log`).
These are isolated local single-player regressions, not a new multiplayer run.

## Still required before expansion/sign-off

- Listen to the sample against the prototype on headphones and speakers. Judge
  induction weight, ballistic distinction after expansion, alert intelligibility,
  tonal fatigue, repeated orders, and the crowded mix. File analysis cannot do this.
- Exercise audio-only music settings, mute/unmute during queued announcements,
  camera distance, loss/recovery of vision, own/allied/enemy notifications,
  hidden deployment, and player-perspective versus full-world observers/replays.
- Review intermediate 125/150/175% scales, long Fluent strings/player names,
  edge tooltips, high cash/power values, disabled/held/ready production states,
  hotkeys, chat, replay/observer controls, lobby, settings and account/error flows.
  Hardware performance and accessibility remain unmeasured. No authenticated
  transaction or result settlement was performed.
- The six grouped alerts serialize; inherited ungrouped speech can still overlap.
  Confirm the bounded group's choice of coalescing, priority and three-second
  expiry in actual play before broadening it.

## Step 4 acceptance remains open

Retain six candidate games with two controlling humans in three side-swapped
pairs, plus a side-swapped baseline pair. Record first contact/capture, station
control, deliveries, expansion, congestion, winner/side and duration. The intended
15–20-minute duration is still a hypothesis.

Test alternative opening layouts, deliberately obstructed factory/dock approaches,
depleted resource transitions, fog/scouting denial, selection through props,
projectile contrast and siege counterplay on a hardware display. Existing static
and routing checks do not establish competitive balance. Step 3 multiplayer
remains one controller plus an observer on one Linux machine and replay checks;
there is no new cross-platform or competitive validation claim.

## Re-run engine policy tests

The isolated SDK selection lives in ignored `.work/build/global.json`; the root
SDK pin is unchanged. From `mods/pvphit/.work/build`:

```sh
../dotnet/dotnet build ../../../../OpenRA.sln -c Release --no-restore -m:1 -p:UseSharedCompilation=false -p:TargetPlatform=linux-x64
../dotnet/dotnet test ../../../../OpenRA.Test/OpenRA.Test.csproj -c Release --no-restore -m:1 -p:UseSharedCompilation=false -p:TargetPlatform=linux-x64 --filter FullyQualifiedName~NotificationQueueTest
```

Use the documented existing laboratory runners for gameplay regressions.
`artifact-sha256.json` records the final sample files, engine changes, tests and
validation binaries. It excludes itself and ignored raw capture files.
