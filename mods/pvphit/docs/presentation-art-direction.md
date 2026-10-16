# Step 5 — Foundry console review sample

This is the first review milestone, not completion of the whole sound/UI pass.
The agreed plan requires comparing a representative sample in context before
expanding the asset batch. Review [the engine recording](validation/presentation/sample.mp4)
and [the native warning view](validation/presentation/native-warning.png).
Compare the earlier [step-4 interface](validation/environment/native-fog-selection.png)
and prototype `audio/induction.wav` / `audio/acknowledge.wav`. Those are historical
comparisons, not a matched before/after performance experiment.

## Direction and implemented scope

The selected **Foundry console** uses ceramic-gray framing (`#9B9B8A`), structural
iron (`#242C30`), instrument surfaces (`#343E41`), quiet seams (`#626E6E`), cyan
induction indicators (`#7FC9CA`) and amber attention markers (`#E2B76C`). Existing
FreeSans fonts, player colors, build icons and familiar command glyphs remain.
The crewed-radio and predominantly electronic instrument-panel alternatives are
not part of this sample.

Twelve original 44.1-kHz, mono, 16-bit PCM WAV exports cover three K6 reports,
three K6 impacts, two selection cues, move/attack/action cues and low power.
Reports combine a short electrical onset with a pitched mechanical body;
commands use a consistent short radio-tone grammar. The action clip is provided
in the voice pool, not a new K6 gameplay action. Scout, siege and hauler retain
their prototype command audio. Source envelopes have headroom and short tails;
listening approval is still required.

The sidebar, production cell frames, button states, minimap frame, command-bar
frame, power indicator, tooltip panels and transient notification panel use
original procedural artwork. Chrome is authored at 1x/2x/3x. Controls, hit areas,
hotkeys, production logic, selection decorations and resource/power values are
unchanged. The power counter's red deficit text remains the existing C# behavior;
its new amber warning icon and explicit low-power text provide additional cues.

Only the Kiln faction uses the new faction-suffixed sidebar/buttons. The command
bar, power icons, tooltip and notification panels are shared across the **pvphit
mod**, including inherited RA maps launched through it. The standalone RA mod is
unchanged. Mod-local copies replace two manifest layout references; duplicate
widget definitions are not appended. No UI C# or Fluent wording changes were
needed for the sample. Menu/loading branding remains for the post-review stage.

## Audio implementation and compatibility

Three default-off trait fields are enabled through focused Furnace overrides:

- `Armament.SoundsRequireVisibility`: report, start-burst and delayed after-fire
  sounds require both current actor visibility and visible actor position.
- `GrantConditionOnDeploy.SoundsRequireVisibility` and
  `SoundOnDamageTransition.SoundsRequireVisibility`: the same actor/position
  gate at the existing event, without changing animation or damage callbacks.
- `CreateEffect.ImpactSoundRequiresVisibility`: the impact position must currently
  be visible. This also gates the existing Furnace death-effect weapons.

Checks use `World.RenderPlayer`: full-world observers retain all-world audibility;
a player perspective follows its visibility. Explored terrain alone is
insufficient. Gates suppress new playback; they do not cut a short already-playing
tail when vision changes. Build sounds retain their existing local-owner filter.
No attenuation distances, backend source limits, simulation random draws or
weapon statistics changed.

Notification pools now optionally accept:

| Field | Default | Behavior |
| --- | --- | --- |
| `Group` | unset | Serializes this group; ungrouped definitions keep legacy behavior |
| `Priority` | 0 | Higher values precede lower pending values; equal priority is FIFO |
| `InterruptLowerPriority` | false | Interrupts active lower-priority audio; does not resume it |
| `UseFullPath` | false | Uses the clip's exact package path, bypassing prefix/suffix expansion |

Grouped playback coalesces definition keys, keeps at most three pending events,
and expires pending events after 3,000 wall-clock milliseconds. Group policy
supersedes the legacy per-file interruption setting. Accepted, coalesced and
dropped requests return success so production callers do not repeatedly retry
an already-handled notification. Failure to start a source returns failure.
Mute, effects volume zero, audio shutdown and sound reinitialization clear queues.
Owner filtering occurs before admission. Text notifications stay immediate.

Six existing Speech events opt into `furnace-announcements`: base attack has
priority 2 and can interrupt; power/funds/storage have priority 1; construction
and unit completion have priority 0. Only low power receives a new clip. Other
five clips remain inherited RA speech. These definitions apply throughout pvphit,
not the standalone RA mod. Other inherited announcements can still overlap this
channel; the sample does not promise a global speech mixer or music ducking.

## Reproduction and review

`tools/build_presentation_sample.py` is the editable source for all sample audio
and chrome. It uses deterministic synthesis/seeds and geometric drawing with
Python's standard library; there are no recordings, AI voices or third-party
samples. Repository licensing applies. The manifest beside the PNGs records
source and WAV hashes, palette, durations and peaks. Do not run `pack_assets.py`
or older model/terrain generators for this pass.

From the repository root:

```sh
python3 mods/pvphit/tools/build_presentation_sample.py --output-root /tmp/furnace-sample-review
# Omitting --output-root intentionally replaces only this sample's owned exports.
python3 mods/pvphit/tools/check_presentation_sample.py
python3 mods/pvphit/tools/review_presentation_sample.py --tag my-review --display :117
```

Choose a fresh tag and unused display. The runner creates a private map/settings
folder under ignored `.work/`, removes `PVPHIT_MATCH_ID`, disables advertising,
and captures **actual OpenAL wave-backend output**. It does not use a microphone,
connect an account, submit results or change the battlefield. It requires Xvfb,
XTest, FFmpeg, ImageMagick, the isolated runtime and installed RA content. No
new software installation or external generator is required. FFmpeg finalizes
the raw WAV header after shutdown and muxes a review MP4; stream start times may
differ slightly, so this recording is not a sample-accurate latency measurement.

Use `--scenario hidden`, `fog`, `visible` or `muted` for the other review fixtures.
`--size 1024,720` and `--size 2560,1440 --scale 2` exercise the UI endpoints.
`--seconds` is a wall-clock timeout; the final runner requires simulation
completion markers and real attack damage, rather than treating elapsed time as
a pass. High-resolution software rendering may require a longer timeout.

## Next stages after sample review

Keep the essential budget at **56 clips total**, including these twelve: 18
weapon/impact, six destruction, seven machinery/construction, 19 role-command,
and six core-alert exports. Confirm the sample's timbre, command grammar and
panel treatment before expanding it. Add event-driven hauler cues only after the
review: harvest notifications plus a successful-resource-transfer notification,
with a one-second actor cooldown and no idle loops. Do not infer working sounds
from docking alone or alter economic timing.

Complete the remaining UI state/long-text/scale and player/observer/replay/menu/
lobby/account reviews. Then implement the focused title/loading treatment:
**Furnace Covenant** prominent, **Prototype · PvPHit** secondary; PvPHit remains
explicit in account, authentication and connection messages. Keep the shellmap,
other inherited layouts, useful glyphs/cursors and release metadata for this
milestone. No account/result/backend changes or releases are authorized here.

Speech/music remain separate optional work. No voice or music generator was
verified; local recording commands exist but microphone availability and a
performer have not been established. A later six-line announcer needs original
dry recordings, consent/provenance and reproducible processing. Optional music
starts with one muteable menu bed, followed by separately scoped battlefield
tracks/stems. No adaptive music or always-playing machinery is included.

See [validation and outstanding acceptance](validation/presentation/README.md).
