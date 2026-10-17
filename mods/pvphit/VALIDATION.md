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

## Core buildings — 2026-10-14

Verified on `pvphit-release-20250330`, based on `173f4792e7`, with a clean tree
before work. Local HEAD and the cached origin branch pointed to that commit;
no local or cached remote `main` existed. Live remote verification could not
complete: the default SSH configuration had a permission error, and bypassing
that include reached GitHub but failed public-key authentication. No branch,
commit or remote configuration was changed.

Blender MCP connected to the live Blender 5.2.2 LTS session before modeling.
The five supplied tank/factory/roster source files were inspected through MCP.
Three independent `FC4` building scenes were modeled and rendered through the
live bridge; the previous scenes and the default Cube/Camera/Light were retained.
Earlier source files and heavy tank/factory outputs are unchanged.

- All **39 sprite frames** and six model previews completed. Three editable
  `.blend` files, embedded PNG sheets, frame metadata, three build icons and
  scripts are retained. HQ remains preplaced, with no new build option.
- Loaded the three saved sources into separate scenes through Blender MCP and
  rerendered all 39 frames: **every frame was pixel-identical** to its procedural
  export. Source loading supports subsequent manual geometry edits.
- Packing validates dimensions, alpha bounds, complete frame sets, differing
  operating poses, differing damage states, and exact make-to-idle endpoints.
  An initial frozen-fan export was caught and corrected before final validation:
  timeline evaluation now agrees with the saved cooling-fan actions.
- Full mod `--check-yaml` passed. Missing-sprite checks passed for SNOW, INTERIOR,
  TEMPERAT and DESERT. Python compilation and `git diff --check` passed.
- Systems lab reached `FURNACE CHECK PASSED: systems suite complete`, including
  capture, income, harvesting/unloading and paid scout production/factory exit.
  Power remained 120 provided / 80 consumed.
- Expanded visual yard reached `CORE YARD PASSED: repeated unloading and
  departure; suite complete`. The tracked free hauler completed four dock
  departures during the final run; resource increases and paid factory output
  also passed. The processor's footprint, dock offset, facing and spawn remain
  unchanged, and the apron is visually open during approach and unloading.
- Native-zoom inspection shows red/blue/yellow/purple ownership panels without
  recoloring cyan induction collars or amber work lights. Generator and processor
  sidebar icons remap correctly. HQ's icon is supplied as an asset, not added to
  the sidebar. Damaged geometry is distinct for all three buildings.
- The recording shows the purple column taking damage and recovering, and new
  generator/processor construction progressing from foundation to intact form.
  Operating loops and the existing factory exit remain active.

The first independent visual-yard display closed before its final assertion.
A second run managed the display, game and recording together and completed
successfully. Both runs used isolated support directories, Xvfb and Mesa software
rendering; normal user settings/account files and the desktop were not changed.
The outcome emitter was disabled because no match ID was supplied.

Evidence: [model comparison](docs/core-building-models.png),
[native-size yard](docs/core-building-yard.png),
[construction capture](docs/core-building-construction.gif),
[operating capture](docs/core-building-operation.gif), and
[unloading capture](docs/core-building-unloading.gif).
The GIFs are enlarged crops from the in-game recording.
See [reproduction and rollback](docs/core-building-art-direction.md).

This is asset and local gameplay-regression verification, not a new multiplayer,
balance, hardware-display or backend-settlement acceptance run. Construction
uses five discrete stages; machinery animation is cosmetic. No engine code,
competitive map balance, gameplay statistics, account/result integration or
release configuration changed. No commit, push or release was performed.

## Support vehicles — 2026-10-14

This pass started from clean `pvphit-release-20250330` at `f8ad287652`. No
`.codegraph/` directory was present. Blender MCP connected to 5.2.2 LTS and
reported no running render before work. The roster source datablocks, completed
heavy/core references, rules, sequences and the fork's animation traits were
inspected first. The existing FC2/FC3/FC4 and default scenes remain present;
the active scene was restored after rendering. No existing source, heavy/core
asset or expanded core-yard file was changed.

Newly performed asset checks:

- Three independent editable sources contain one scene each. The initial
  silhouette preview was presented before the full batch; the mortar's capped
  appearance was corrected to an open rim and recessed bore before export.
- All **419 sprite frames** completed through Blender MCP. The packer checks
  every state's dimensions, RGBA alpha margin, frame completeness, directional
  wreck differences, actual five-stage movement, and exact travel/deployed
  endpoints for every facing. All passed.
- Loaded all three saved `.blend` files into fresh owned scenes and rerendered
  all 419 frames: **419/419 pixel-identical**. PNG file hashes differ because of
  Blender metadata, so the comparison used decoded RGBA pixels.
- Every scout hull and turret direction is distinct and retains the shared
  untrimmed canvas. The union of either layer's validated bounds remains inside
  the frame for all 1,024 hull/turret direction combinations.
- Packed sheets have embedded `FrameSize` and `FrameAmount` metadata imported
  by this fork's utility. A deliberately incorrect deployment endpoint and an
  unembedded PNG were both rejected in isolated negative checks.
- Full mod `--check-yaml` passed; missing-sprite checks passed for SNOW,
  INTERIOR, TEMPERAT and DESERT. Python syntax and `git diff --check` passed.
  The new map generator reproduced its YAML exactly.

Newly performed in-game checks used isolated Xvfb displays, temporary support
settings and `Graphics.ViewportDistance=Native`, with the display, game and
recorder managed together. The initial sandbox launch could not create local
sockets; the permitted isolated rerun worked. No desktop settings/account files
were changed and no match ID was supplied.

- Native-zoom review covered all 32 body directions, all 32 deployed carrier
  directions, separate scout turret directions, shadows and all three wreck
  direction sets. Four player colors remapped ownership panels; induction
  cyan and work-light amber stayed separate. All three vehicle sidebar icons,
  including the hauler's explicitly overridden palette, showed red panels.
- The vehicle yard passed surviving scout capture, free-hauler spawn, repeated
  harvesting/unloading/departure, and paid production of all three vehicles.
  The tracked free hauler completed **11 dock departures** during the final
  visual-tour run. Paid hauler and scout factory-exit checks passed.
- Scripted checks passed for no undeployed firing, minimum/maximum mortar range
  and deployed firing within range. Real player input deployed the interactive
  mortar, force-fired (logged 13,750 damage per hit), then ordered movement.
  Captures show stabilizers withdrawing before travel and returning cleanly to
  the travel pose. Early hotkey attempts lacked Xvfb window focus; explicitly
  focusing the game corrected the input harness.
- The unchanged systems lab again logged `FURNACE CHECK PASSED: systems suite
  complete`, including capture, resource delivery and paid scout output.
- The unchanged core-building yard again logged `CORE YARD PASSED: repeated
  unloading and departure; suite complete`, with four dock departures, paid
  production, damage/recovery and construction events.

### Historical step-2 issue: produced siege carrier (fixed in step 3)

**At the end of step 2, the vehicle yard did not pass its complete suite.** A newly produced mortar
carrier stays at the factory. Source inspection identifies existing wiring in
`rules/furnace.yaml`: `WithMakeAnimation` grants `build-incomplete` during
`INotifyCreated`, when both conditional sprite bodies are still disabled. Its
`Forward` method returns without an animation callback to revoke the condition,
so `Mobile.PauseOnCondition` keeps the unit immobilized. Map-placed carriers skip
creation animation and correctly pass deployment/fire/withdrawal checks.

This predates the artwork changes: the relevant gameplay rules and engine code
are unchanged in this pass. Removing the creation-only grant and cleaning up its
now-unused condition references is a small YAML fix, but it changes explicitly
preserved condition wiring. At that milestone approval was requested and the fix was not applied.
The carrier's paid-production callback fired, but **factory exit remained failed**.
Do not treat a callback alone as a successful exit.

The test harness also initially tried to queue a build inside the preceding
production callback, before the queue released its lock; the next request is
now delayed one tick. Its failure handler now suppresses the final success
message after any assertion failure (an earlier failing run printed that message
after `FatalError` scheduled termination). These are laboratory-only changes.

Evidence: [models](docs/vehicle-models.png), [native yard](docs/vehicle-yard.png),
[before/after directions](docs/vehicle-facing-comparison.png),
[full native-size direction grids](docs/vehicle-directions-in-game.png),
[deployment](docs/vehicle-deployment.gif) and
[withdrawal before travel](docs/vehicle-withdrawal.gif).
The GIFs are enlarged crops of the native-zoom recording. The direction-grid
montage reads left-to-right: hauler/scout; traveling/deployed carrier;
independent scout turret/hauler wreck; scout wreck/carrier wreck.

At the end of step 2, harvesting/docking still used idle artwork; no movement
or firing loops had been added. No new multiplayer, balance, backend-settlement or hardware-display
acceptance was performed. All changes are under `mods/pvphit/`; no commit, push,
release, deployment or `main` branch creation was performed.


## Movement, firing and destruction — 2026-10-15

The produced siege stall is fixed. The final standalone vehicle yard and both
clients of the local multiplayer yard passed their complete suites on the
rebuilt current engine. This supersedes the historical step-2 acceptance issue.

### Implementation and preserved behavior

- Removed only the siege's creation-time `build-incomplete` grant/references.
  `WithMakeAnimation`, both conditional bodies, deployment callbacks and reverse
  withdrawal remain. Actual production exit is asserted by arrival at a separate
  destination, not by the production callback.
- Four-frame travel loops cover hauler, scout, K6 and siege. Hauler harvest
  strokes and unloading gate motion use existing traits. Dock opening/closing
  still use one-frame idle, retaining callback duration. Cargo quantity is not
  represented by the cosmetic hopper residue.
- Scout ballistic, K6 induction and pressure-mortar flashes, projectile images,
  impacts and brief death effects are original Blender exports. Siege body recoil
  is shot-driven on its braced body; AttackOmni and existing turret/recoil behavior
  remain. No extra damage warheads, sounds or physical debris were added.
- Directional support wrecks remain; the K6 wreck now has a collapsed turret and
  displaced armor. Gameplay husk lifetime, collision, pathing and visibility
  rules are unchanged. The yard's existing persistent-husk override is test-only.
- One engine change outside the mod adds a null-safe current-sequence read to
  `WithMoveAnimation`. The old dereference crashed when the map's initially
  deployed carrier had never enabled its travel body. The rebuilt yard exercises
  this case. No new engine trait, aiming mechanic or platform change was needed.

### Observed checks

- Release build: zero errors; three existing SDK warnings about the net6 target.
  Full current-engine YAML lint, including the updated test map, and all four
  tilesets' missing-sprite checks passed.
- Vehicle yard: paid hauler, scout and three successive siege carriers all
  cleared the factory and reached their assigned cells. Each carrier deployed,
  hit for the unchanged 13,750 damage and withdrew/moved twice. Movement remained
  blocked during withdrawal. Undeployed fire and minimum/maximum range checks passed.
- Repeated hauler delivery/departure passed. A real move order interrupted docking,
  the hauler departed and resumed harvesting. Destruction passed during scout
  movement, K6 firing, siege deployment, siege withdrawal, hauler harvesting and
  hauler unloading. Six state checks completed before the 360-second final assertion. The final
  harvest check required five ticks at exactly the same world position, avoiding
  false positives while merely crossing a resource cell.
- The extended test initially exhausted its original ore patch before the late
  hauler checks. A second field was added only to the vehicle yard. An earlier
  before/after animation run matched **200 resource updates and ten dock departure
  ticks exactly** through tick 3,800. Opening/closing sequences and all economic
  trait values remain unchanged; see the retained economy comparison.
- Systems lab and current core-building yard passed again on the rebuilt engine.
  The latter completed four dock departures, paid scout production and building
  damage/recovery/construction checks. Regenerating both yards with their current
  generators produced byte-identical files.
- Two local clients (one controller, one observer) completed the vehicle suite
  through an unadvertised dedicated server with sync reports enabled. Their
  **358 Lua log lines were identical**, including economy ticks and assertions;
  neither reported a desync. The server recording and its exact map are retained.
- Replay verification passed with no live input: all 358 Lua lines matched both
  clients exactly, including the final suite-complete assertion. The final
  standalone yard additionally tightens the harvest-death trigger to compare
  exact world positions; the retained multiplayer/replay map predates that
  test-only refinement.
- All 1,312 vehicle frames and 192 effect frames passed export validation. Checks
  cover canvas/alpha bounds, animation differences, 32 directions, facing-major
  ordering, exact siege deployment/fire endpoints and engine PNG sheet metadata.
  Freshly loading all four saved animation sources reproduced **328 sampled
  frames with zero RGBA pixel differences**. The four original refined sources
  are byte-identical to reviewed commit `b51f61542c2012f5f1a37d9a4b74304182162ce9`.
- Resolved weapon comparisons matched every field except `Image` for FCInduction,
  FCScoutGun and FCMortar: damage, ranges, reload and projectile flight are unchanged.
  Native-size direction boards and the in-game directional tour cover silhouettes,
  four player colors, full-canvas anchors and independent turret aim.

Evidence and reproduction: [native in-game yard](docs/vehicle-motion-yard.png),
[firing and withdrawal](docs/vehicle-fire-withdrawal.gif),
[destruction in game](docs/vehicle-destruction-in-game.gif),
[dock interruption](docs/hauler-docking-in-game.gif),
[workflow](docs/movement-art-direction.md), [retained logs, baseline weapons, hashes and replay](docs/validation/motion/),
[movement](docs/vehicle-movement.gif), [working sequences](docs/vehicle-working.gif),
[weapon effect timings](docs/vehicle-weapon-effects.gif),
[death effect timings](docs/vehicle-death-effects.gif),
[K6 wreck directions](docs/tank-motion-wrecks.png), and
[independent K6 aim samples](docs/tank-independent-aim.png).
The gameplay GIFs are crops of native pixels from the verified replay, without
resizing. The effect/direction previews show rendered assets at native scale;
they are not recordings of simulated projectile flight. Source/frame hashes accompany the
packed sheets under `art/motion/` and `art/motion-effects/`.

### Limits and scope

These are Linux/Xvfb/llvmpipe tests on one machine, including one controlling
player plus an observer. They do not establish cross-platform determinism,
latency tolerance, competitive balance or hardware-display performance. The state
checks cover the listed scenarios, not every possible order/death combination.
Movement is a fixed-speed cosmetic loop rather than distance-integrated running
gear. Major sound work, voices, music, cargo-state visuals and UI work remain for
later as requested. No account, match-result, website, backend, release/version or
platform behavior was changed. No commit, push, release or deployment was made.

## Ashbound transfer yard — 2026-10-15

Pressure Station Nine now has original ash/paving ground, damaged concrete,
flush drains, low pressure hardware and four short blocking wall clusters.
The playable bounds remain 96×96. Starts share the same y coordinate; home
deposits move south/inboard and larger deposits become northern/southern contested
fields. Both station anchors remain unchanged and horizontally centered.
The exact Step 3 battlefield is preserved as an archive for comparison.

### Observed checks

- Current-engine YAML lint and missing-sprite checks passed, including all four
  tilesets. The mod-local TEMPERAT definition preserves the complete original
  definition byte-for-byte before its 24 added templates. RA files and existing
  maps' original terrain artwork are preserved.
- The native environment sample passed actual produced-siege arrival, surviving
  capture and harvesting. The PNG terrain path was reviewed in-game, including
  transitions, minimap colors and sorting beneath the roster.
- Static checks preserve two 49-cell and two 81-cell deposits. Applying the
  engine's neighbor-density formula gives 398/686 units per home/expansion:
  54,200 nominal credits, unchanged from baseline. All added ground uses Clear
  semantics; no road-speed or buildability change was introduced.
- Geometric home access matches exactly; corresponding expansion distances
  differ by at most one cell. Fifteen controlled engine arrival comparisons
  (scout/tank/siege to five destinations) passed with a maximum difference of
  **2.5%** in the retained final run. This does not characterize every pathfinder
  tie, player layout or traffic condition.
- The candidate lab passed three twelve-tank groups over north/central/south
  routes and back using separated rally cells. An earlier compact parking grid
  boxed one tank out of its exact destination; that failed fixture/log is retained.
  Both sides produced a hauler, scout, tank and two siege
  carriers; all ten outputs reached separate destination cells.
- Two haulers on each side completed **at least ten aggregate deliveries**.
  Counts require resource increases followed
  by departure. Storage is periodically cleared only in this laboratory.
- Real deploy/withdraw input exercised a candidate siege position. Damage stayed
  13,750 against the test target; withdrawal finished before translation. A scout
  reached minimum-range proximity around the wall. Station capture preserved
  the scout. The walls have no projectile-blocking or cover traits.
- Actual paid sidebar production and placement orders accepted the reference
  generator/processor/factory opening on both starts. This supplements static
  footprint, two-cell adjacency, HQ-radius and south-apron checks.
- Existing vehicle, systems and core-building laboratories passed again unchanged,
  including repeated siege production and six deploy/fire/withdraw cycles. Resolved
  weapon comparisons matched the Step 3 baselines except the existing artwork
  Image fields. Earlier source/export and test-map hashes are preserved.
- All ten modeled props reproduced with **zero RGBA differences** from saved
  Blender sources through Blender MCP's background tool. The live localhost:9876
  bridge was unavailable; no live scene or existing motion source was overwritten.
- Fresh generation plus current-engine map refresh reproduced all three
  new/updated maps byte-identically, including previews. Generators now require
  explicit targets; the prior multi-map build entry point is no longer implicit.
- Native captures cover both station compounds, the central apron, base access
  and a selected K6 at a shroud edge. The static-prop comparison retained all
  six timing snapshots: full-scene render 12.6/12.9/25.0 ms versus
  11.9/11.8/11.8 ms without props on llvmpipe, with a 30 FPS cap. The spike is
  retained; these few snapshots are not a hardware performance guarantee.

Evidence: [layout](docs/environment-layout.svg),
[native sample](docs/validation/environment/native-sample.png),
[siege and flank crop](docs/validation/environment/siege-flank.gif),
[workflow](docs/environment-art-direction.md), and
[logs, measurements, baseline and human-match protocol](docs/validation/environment/README.md).

### Remaining acceptance

No two-human competitive matches were performed. Match duration, positional
advantage, station control and resource-flow balance remain unproven; the
15–20-minute target is still a hypothesis. The retained CSV is intentionally
empty. Human paired matches, alternative construction layouts, congested/depleted
resource scenarios and hardware-display accessibility/performance review remain.
No new multiplayer/replay determinism claim is made by this pass; Step 3's local
controller-plus-observer/replay evidence retains its original limited scope.
Cross-platform behavior and authenticated PvPHit settlement remain unproven.

There are no new ambient animation actors, terrain mechanics, unit/economic/weapon
values or victory rules. Shared RA content, engine code, account/result integration,
website/backend and release configuration were not changed. No commit, push,
release or deployment was performed.

## Sound and interface sample — 2026-10-16

The first step-5 review milestone is implemented; the full asset batch remains
pending sample review. The Release build, five announcement-policy tests, full
YAML lint, four-tileset missing-sprite checks, deterministic sample reproduction
and resolved weapon comparison passed. Actual OpenAL captures distinguish visible
firing/destruction from shrouded and explored-but-fogged activity at the same
camera position. These measurements do not establish subjective sound quality.

The sample recording asserts real force-attack damage and captures an actual
low-power event with visible text and indicator. Native and UI-scale endpoint
screenshots are retained. See [the evidence and explicit limits](docs/validation/presentation/README.md).
No competitive, cross-platform, hardware-accessibility or authenticated-platform
acceptance is claimed. Step 4's human match/layout/congestion/depletion review
remains open and the 15–20-minute duration remains a hypothesis.

The unchanged systems, core-building and complete vehicle laboratories passed
on the changed engine. Vehicle evidence includes actual paid factory exit, all
three produced carriers' repeated fire/withdraw cycles, docking interruption
recovery and destruction in six animation states. The fully muted sample also
completed and preserved the low-power visual warning while output remained at
the backend dither floor. These are local single-player checks; no new
multiplayer/replay or environment-routing acceptance run is claimed.

## Presentation completion candidate — 2026-10-16

The original twelve exports are preserved; 44 new original clips complete the
56-clip inventory. Role commands, harvesting and accepted-transfer feedback,
remaining core alerts, explicit grouping of inherited speech, title/loading
identity, PvPHit connection wording and opt-in compact counters are implemented.
Shared C# changes are part of this milestone. Gameplay/source preservation and
deterministic reproduction checks pass; there is no listening approval implied.

The Release build and 21 focused tests pass, as do YAML and sprite checks.
Private two-controller multiplayer and replay runs produced matching outcomes.
These are automated Linux clients, not humans. Player-perspective and full-world
replay captures, sound visibility controls, intermediate UI scales and representative
shell/production/chat screens are retained in the
[completion evidence](docs/validation/presentation-completion/README.md).

The vehicle, systems and core-building laboratories passed again. The current
environment run **failed**: tank 31 remained at (30,59) during `groups-back`.
All 15 paired travel trials and ten production exits passed before that failure;
the subsequent siege/capture/end-of-suite assertions were not reached. This is
an unresolved congestion acceptance issue, not a successful environment rerun.
No gameplay or fixture changes were made to hide it.

The [human protocol](docs/first-human-playtest.md) provides six candidate games
and a side-swapped baseline pair, with empty result sheets. Hardware listening,
accessibility, full observer/filter/transition coverage, human balance and
authenticated platform acceptance remain open. No commit, deployment or release
readiness is claimed.
