# Foundry console — completion candidate

The sample's sound character, nonverbal command grammar and console appearance
were accepted in design review. This implementation extends that direction;
it does not substitute for final listening, hardware or two-human acceptance.

## Production inventory

The twelve reviewed exports remain unchanged. `tools/build_presentation.py`
adds 44 original synthesized PCM clips, making **56 retained clips** under the
agreed ceiling. `audio/presentation/manifest.json` records each clip's category,
event, duration, headroom and hash. All sounds are mono 44.1-kHz/16-bit PCM.

| Category | Total | Event mapping |
| --- | ---: | --- |
| Weapon/impact | 18 | Three reports and impacts for scout, K6 and siege |
| Destruction | 6 | Four vehicle identities; two building-collapse variants |
| Machinery/construction | 7 | Deploy, withdraw, placement; two harvest and two transfer variants |
| Role commands | 19 | Five K6, five scout, five siege, four hauler |
| Core alerts | 6 | Base attack, power, funds, storage, construction complete, unit ready |

K6 `Action` remains a preserved sample export without an invented gameplay action.
Scout Action acknowledges capture, siege Action deploy, and hauler Action harvest.
The hauler has no attack clip. Existing command suppression and shuffled sound
pools control repetition; orders are never queued or delayed by sound playback.

`ResourceActivitySounds` listens to actual `Harvested` events and refinery
`INotifyResourceAccepted`. The refinery broadcasts to same-owner listeners, so
only the receiving refinery's own positive-count, positive-value event qualifies.
An empty dock, full storage or rejected transfer does not create success audio.
One-second per-actor cooldowns use local presentation time; visibility is checked
before admission. There are no idle loops, replay backlogs, economic changes,
new transfer callbacks or synchronized random draws.

Buildings use only their death-effect weapon for collapse sound. The duplicate
destroyed-state clip is cleared; heavy-damage transitions retain a short impact.

## Announcements and compatibility

All 113 inherited `Speech` definitions explicitly join the bounded announcement
group inside PvPHit. Ordinary retained speech has priority 0, power/funds/storage
priority 1, base attack priority 2, and match-ending announcements priority 3.
Priorities 2/3 may interrupt lower active audio. Capacity remains three pending,
expiry three wall-clock seconds, equal priority FIFO and duplicate coalescing.
Text stays immediate. Commands, UI sounds and music are separate.

The new sound trait is opt-in with empty sound arrays by default. Existing
visibility fields remain false by default. PvPHit enables visibility for the new
resource sounds; full-world observers can hear world events, while player views
follow current vision. Private notifications retain local-owner filtering.

Original SVG identity artwork uses the repository FreeSans Bold font, the foundry
mark, **Furnace Covenant** and **Prototype · PvPHit**, at 1x/2x/3x. Existing loading
and main-menu logo rectangles are retained. The shellmap and inherited menu
layouts remain. Authentication and connection wording explicitly names PvPHit;
account endpoints, authentication and result submission code are unchanged.

PvPHit's local player layout opts into compact cash/power display at large values;
tooltips retain exact values. The `CompactDisplay` logic argument defaults off.
Control geometry, hotkeys and panel sizes are unchanged.

Kiln sidebar/buttons remain faction-specific. Command-bar/power/tooltip/transient
panels, counter display, identity artwork and speech arbitration affect inherited
RA maps inside PvPHit. Standalone RA files and default behavior remain unchanged.

## Reproduction and review

```sh
python3 mods/pvphit/tools/build_presentation.py --output-root /tmp/furnace-completion-review
python3 mods/pvphit/tools/check_presentation.py
python3 mods/pvphit/tools/review_presentation_sample.py --tag unique-review --display :121 \
  --script mods/pvphit/tools/presentation_complete.lua --seconds 240
python3 mods/pvphit/tools/run_presentation_network.py --tag unique-network
python3 mods/pvphit/tools/review_presentation_shell.py --tag unique-screens
```

Use unused display/port numbers and unique tags. Default generator output writes
only this batch's owned files. The sample and all earlier sources/generators are
preserved. The generator needs Python and ImageMagick's MSVG reader; it records
the repository font hash. No voice/music generator is required or promised.

Current evidence and explicit untested cases are in
[completion validation](validation/presentation-completion/README.md).
Use the [human playtest protocol](first-human-playtest.md) after technical review.
Music/spoken voices remain separately scoped. No publishing, versioning, account
transactions, backend changes or release-readiness claim is included.
