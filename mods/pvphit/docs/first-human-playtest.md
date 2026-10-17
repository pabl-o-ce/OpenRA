# First two-human playtest — Pressure Station Nine

Status: **not performed**. Presentation direction is accepted; final listening,
hardware accessibility and human balance acceptance are separate open gates.
The intended 15–20-minute duration is a hypothesis. Automated controllers and
controller-plus-observer sessions do not count as human matches.

Technical hold: the current environment laboratory stranded tank 31 at (30,59)
on the return leg of the 36-tank congestion test. Preserve the failed log in
`docs/validation/presentation-completion/foundry-environment-checks.log` and
reproduce/classify this issue before calling the candidate technically accepted.
The kit is prepared for review; it does not waive this gate. Its cause has not
been established as either a fixture problem or a gameplay regression.

## Prepare and freeze

Run `python3 mods/pvphit/tools/prepare_playtest.py --tag <unique-tag>` from the
repository root after technical checks. The ignored kit contains both map copies,
a manifest of this checkout's content/binaries, a schedule, and empty result and
feedback CSVs. The archived baseline is preserved byte-for-byte in the repository;
only the private extracted copy receives a distinct lobby title.

Use two separate Linux computers/displays with the same validated engine/mod
content and installed RA dependencies. Record CPU/GPU, display resolution and UI
scale, audio device, headphone/speaker use, player experience and build manifest.
Give each player a separate support directory. Install the kit's map directories
there and provide installed RA content through the normal supported setup.

Launch each client from the repository root with its private support directory:

```sh
env -u PVPHIT_MATCH_ID ./launch-game.sh Game.Mod=pvphit \
  Engine.SupportDir=/absolute/path/to/private/support \
  Server.AdvertiseOnline=False Server.RequireAuthentication=False \
  Server.QueryMapRepository=False Server.RecordReplays=True Server.EnableSyncReports=True
```

Host a private LAN game and connect directly. Do not log in, advertise publicly,
use a production match ID, or submit results. Account linking and authenticated
settlement require a separately scoped environment. This kit is not a release.

## Unscored orientation and scenarios

Explain the generator → processor → armor works opening, free processor hauler,
scout capture, two pressure stations, siege deploy on **F**, minimum range, and
base-destruction victory. Show existing controls; do not change hotkeys or rules.
Allow an unscored familiarization round before measuring either map.

Exercise both starts with alternative building arrangements, deliberately blocked
factory exits and processor approaches, clearing the obstruction, depleted-field
transitions, expansion hauling, and dense armor traffic. Try siege positions and
scout flanks inside minimum range. Review fog denial, selection through props,
projectile contrast and station ownership. Keep these interventions out of scored games.

Use headphones and speakers for repeated selection/orders and crowded combat.
Ask whether role/weapon identities and important warnings remain distinguishable,
and record fatigue after a full game. Muting must leave text and power warnings
usable. Do not turn WAV peak checks into a listening or accessibility verdict.

## Eight scored matches

Follow `schedule.csv`: candidate pair C1, baseline pair B1, candidate pair C2,
candidate pair C3. Each pair swaps starting sides; C3 reverses the first-game
side order. Fix players, game speed, 5,000 starting cash and handicaps within each
pair. Use the same engine/presentation build for both maps. Do not patch mid-pair.
Schedule two sessions if needed, keeping each pair together and taking breaks.

Keep exact maps, replay, logs and settings for each match. Record in
`human-matches.csv`: starting side/winner, first contact, first north/south capture,
cumulative station control by side, completed deliveries, first expansion,
congestion incidents, duration and resource-flow notes with replay intervals.
First contact means the first hostile damage; first expansion means the first
successful delivery from a contested field. Count a delivery when transferred
resources are positive, not when docking starts. Record ambiguous observations
as unknown with a timestamp, never estimate them as measured facts.

After each game, each player independently records feedback before discussion:
missed/confused alerts, repetitive or harsh sounds, unclear text/states, terrain
or ownership confusion, congestion, siege counterplay and perceived side advantage.
Use timestamps, expected/observed behavior and screenshots/replays in `feedback.csv`.

## Acceptance and triage

Keep three verdicts: presentation accepted, technical validation passed, and
provisional human balance accepted. Require eight complete scored records for
this protocol; aborts/desyncs are incidents and must be replaced after fixing.

Prioritize: (1) crashes/desyncs/information leaks/broken controls or production;
(2) misleading or unreadable feedback and severe fatigue; (3) repeated side,
economy, congestion or counterplay problems; (4) cosmetic polish. Repeated side
advantage warrants investigation even if scripted route timings are similar.
Eight games establish initial evidence, not statistical balance certification.

Fix one supported issue at a time; rerun affected technical tests and complete
side-swapped pairs after gameplay/layout changes. Do not add units, factions,
mechanics or another map in response to vague feedback. After slice acceptance,
run a stabilization pass and repeat paired matches with another player pair.

Music, spoken voices, cross-platform acceptance and authenticated platform testing
remain separately scoped. Do not call this slice release-ready.
