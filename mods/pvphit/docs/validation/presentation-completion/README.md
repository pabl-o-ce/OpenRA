# Presentation completion candidate — evidence

Implementation is ready for review. **Technical acceptance is incomplete**, final
listening/hardware acceptance is pending, and no human balance matches have been
performed. The environment congestion failure below is retained, not waived.
The original sample evidence remains in `../presentation/`.

## Review artifacts

- [Engine recording with audio](completion.mp4): real siege deployment/damage,
  paid production, held/resumed production, resource transfer/full-storage recovery,
  announcement collisions, mute/unmute, large cash counter and chat.
- [Held production](states-held.png), [ready production, large counter and chat](states-longtext.png).
- [Title/menu](shell-menu.png), [PvPHit account form](shell-settings-account.png),
  [connection error](shell-connection-error.png), [replay browser](shell-replay-browser.png).
- Settings: [display](shell-settings-display.png), [audio](shell-settings-audio.png),
  [hotkeys](shell-settings-hotkeys.png).
- UI samples: [1024×720 at 1×](completion-minimum-warning.png),
  [1600×1000 at 1.25×](completion-125-warning.png),
  [1920×1080 at 1.5×](completion-150-warning.png),
  [1920×1440 at 1.75×](completion-175-warning.png),
  [2560×1440 at 2×](completion-hidpi-warning.png).
- Replay views: [full world](replay-world-perspective.png),
  [selected player](replay-player-dropdown-perspective.png).

These are Xvfb/llvmpipe captures on one Linux host. Inspecting PNGs is not hardware
acceptance. Intermediate-scale runs used the completed audio/branding but preceded
the compact-counter change; final counter/held/chat captures use the final engine.
The title identity is new; the inherited RA shellmap and menu panel textures remain.

## Measured checks

| Check | Result and practical limit |
| --- | --- |
| Release solution build | Pass, zero errors; three existing .NET 6 end-of-support warnings. `build.log`. |
| Focused NUnit tests | 21 pass: notification ordering/expiry/coalescing/interruption/failure, Sound lifecycle clearing, resource sound throttling/defaults, compact integer formatting. `tests.log`. |
| YAML and missing sprites | Pass; four tilesets checked. `yaml.log`, `sprites.log`. |
| Reproduction/inventory | 56 clips including unchanged twelve; byte-identical generated WAV/SVG/PNG/YAML/manifest, no clipped source samples, 44.1-kHz mono PCM, new clip peaks below −3 dBFS. `checks.json`. |
| Preservation | 1,093 baseline files unchanged, including standalone RA, maps, original source art, sequences and existing rules/weapons; resolved scout/K6/siege simulation fields unchanged; player layout geometry identical. `checks.json`. |
| Resource sounds | Actual harvest and accepted-transfer callbacks; positive count/value required, one-second local cooldown. Scripted resource increases and recovery from full storage pass. `states-game.log`. Docking alone is not the success signal. |
| Visibility controls | Same-camera hidden and explored-but-fogged combat at backend dither floor (peak 1/32768); visible control audible. `audio-checks.json`. |
| Deployment control | Real F deployment followed by asserted damage. Hidden fixture removes own vision; its deploy window is at dither floor, visible control peak 1125. Earlier select-all UI speech excluded explicitly. This is not exhaustive enemy/allied deployment coverage. |
| Lose/regain vision and camera | Continuous combat goes to dither floor after vision loss, returns after reacquisition. Moving the camera away reduces RMS from about 125 to 23; return restores about 127. Camera distance is attenuation, not a guaranteed mute. |
| Mute/settings/lifecycle | Fully muted capture is at dither floor; real M mute/unmute exercised. Tests verify effects volume zero, mute, StopAudio, initialization and DisableAllSounds clear active/pending speech; music volume alone does not clear speech. Full interactive transitions remain a separate matrix. |
| Crowded mix | Twelve-K6 sample and completed-role scenario recorded without clipped samples in measured captures. An isolated visible destruction control peaks at −0.42 dBFS; this leaves little aggregate headroom and warrants crowded-battle listening. No universal no-clipping claim. |
| Multiplayer/replay | Two controlling automated Linux clients on private loopback, independent local mute, real deploy/withdraw input, harvesting and server replay. Both peers and replay report identical outcomes. No account identity or outcome submission. `final-network/checks.json` and logs. |
| Replay audio | Separate OpenAL captures in full-world and selected-player views complete with matching outcomes. Screenshots verify perspective selection; this is not a complete source-by-source audibility audit or a live-observer test. |
| Prior laboratories on changed engine | Vehicle, systems and core-building suites pass. Corresponding `foundry-*.log` files retained. They ran before the display-only compact-counter addition. |

The recordings and hashes distinguish two builds in `engine-builds.json`. The
final two-client/replay regression uses the final normal-output build. Earlier
perspective recordings used the same sound implementation before compact counters.
The original `network.orarep` accompanies those perspective recordings;
`final-network/network.orarep` is the final-build regression, with its exact map
in `final-network/map/`. Final peer/replay result:
`2500,2500,81250,81250,46,52,50,52` (resources, target health, carrier positions).
No Step 3 multiplayer evidence is substituted for these new runs.

## Unresolved environment regression

`foundry-environment-checks.log` ends in:

```text
ENVIRONMENT YARD: stranded tank 31 at 30,59
ENVIRONMENT YARD FAILED: tank group timeout groups-back
```

All fifteen paired scout/tank/siege travel checks, the outbound three twelve-tank
groups, and five produced outputs on each side reached their destinations before
the failure. Return congestion did not pass. Later siege/flank/capture assertions
and the overall delivery threshold were not reached. A secondary exception occurs
while the fatal-script path opens its menu; retain it with the original failure.

The map and test script are unchanged. This run does not establish whether the
failure is a fixture/pathfinding sensitivity or a regression. Reproduce with a
fixed replay/seed and compare against the reviewed baseline before classifying it;
do not adjust movement, terrain or parking goals merely to make the check pass.
The raw capture, replay and events remain in ignored
`mods/pvphit/.work/completion20261016-environment-checks*`.

## Remaining acceptance

Keep these as open checks, not inferred passes:

- Resolve/classify the environment return-congestion failure and repeat the
  relevant regression before declaring the candidate technically accepted.
- Live observers and exhaustive own/allied/enemy event filtering, including
  hidden enemy deployment, replay seeking/speed changes and perspective transitions.
- Interactive world/menu/replay transitions with pending speech, effects slider
  changes, settings persistence and mute/unmute during dense overlapping alerts.
- Maximum supported names/text, every edge tooltip and production state at every
  supported endpoint/scale; inherited RA maps inside PvPHit and standalone RA
  runtime smoke checks. Defaults and untouched RA files are useful checks, not
  substitutes for running those screens.
- Headphones and speakers, role recognition, battle intelligibility, repetition,
  fatigue, color/contrast, non-audio cues, hardware UI scaling and performance.
- Six candidate human matches plus the baseline side-swapped pair, alternative
  layouts, blocked exits/docks, depletion, congestion and siege counterplay.

Authentication was not attempted. Account screenshots cover only the offline form;
the connection failure is loopback port 1. Authenticated platform testing,
cross-platform acceptance, music and spoken voices remain separately scoped.

## Reproduction

See [production notes](../../presentation-completion.md) for asset generation and
review commands, and [the human protocol](../../first-human-playtest.md) for the
isolated kit. From the ignored `mods/pvphit/.work/build` directory (local SDK 8
selection; repository SDK pin unchanged):

```sh
../dotnet/dotnet build ../../../../OpenRA.sln -c Release --no-restore -m:1 -p:UseSharedCompilation=false -p:TargetPlatform=linux-x64
../dotnet/dotnet test ../../../../OpenRA.Test/OpenRA.Test.csproj -c Release --no-restore -m:1 -p:UseSharedCompilation=false -p:TargetPlatform=linux-x64 --filter 'FullyQualifiedName~NotificationQueueTest|FullyQualifiedName~SoundNotificationLifecycleTest|FullyQualifiedName~ResourceSoundThrottleTest|FullyQualifiedName~CompactCounterTest'
```

Capture runners need Xvfb, software GL, OpenAL, ffmpeg, ImageMagick and local socket
access. Each new runner requires a fresh tag and refuses occupied displays; no
public server, backend or login is needed. Raw WAVs stay in ignored `.work`; measured
windows and event times are retained here. `artifact-sha256.json` records evidence
and changed implementation hashes, excluding itself and ignored raw captures.
