# Step 7 — local controlled-build work

**No-go for tester handoff.** This is the final planned first-slice stage, not public
release acceptance. Implementation and automated evidence are available; the environment
fixture review, human/hardware acceptance and authenticated platform E2E gate remain open.
No push, public package, deployment, cloud provision or production migration occurred.

## Recorded scope

Engine source: `30fa940bbf0af679a151f8111409ba6dbd668153`, branch
`pvphit-release-20250330`. Platform base: `bba6f7f` on `main`. Orchestration base:
`a00a543` on `chore/openra-snapshot-437438971`. OpenRA Step 7 work is recorded on
`pvphit-release-20250330`; sibling changes remain uncommitted working-tree patches,
separately reviewable in each repository. Unrelated platform `assets/` and the
orchestrator's untracked `AGENTS.md` are preserved. Both sibling CodeGraph indexes were
consulted before source inspection; neither was initialized or rebuilt.

Local host: Linux x86_64, Arch, Xvfb/llvmpipe; SDK 8.0.425 building the fork's net6.0 target.
The repository SDK/version identifiers were not changed. No Windows or macOS acceptance
is claimed. Human testing/listening/hardware acceptance was explicitly confirmed absent.

## Gate ledger

| Area | Current evidence | Remaining acceptance |
|---|---|---|
| Implemented slice | Original assets/gameplay and shared C# are preserved; source at the recorded commit | No added faction/unit/map/mechanic |
| Technical | Local self-contained package, YAML/sprites, focused engine tests, vehicle/building/systems labs and automated two-client/replay checks; see evidence ledger | Reviewed environment assertion correction and complete later assertions; final authenticated launch |
| Congestion | Original seed fails on current and earlier engine; diagnostic confirms exact arrival then friendly nudge in the same tick | Proposed fixture patch is not applied without review; the old failed run remains failed |
| Presentation | Existing 56 clips, Foundry UI and retained visual evidence | Human listening, actual display/UI scaling/readability, observer/audio perspective transitions and hardware performance |
| Provisional balance | Human protocol and empty result sheets exist | Six candidate matches plus side-swapped baseline pair, two humans, feedback and any reviewed fixes |
| Platform integration | Structured result ingestion/verification/recovery and transactional platform completion tested in isolation | Real account linking → authenticated game → verified platform completion → cleanup in the agreed isolated environment |
| Distribution | Private local Linux tarball and matching image; manifest/checksums/provenance; no `.work` distribution | Two physical Linux installations, update/rollback and final go/no-go signatures |
| Deferred | Windows/macOS, public rollout, cloud snapshots/provisioning and public distribution | Separate scope/access/approval; no claim of balance certification or public readiness |

## What changed

OpenRA packaging stages an allowlist of runtime assets and only the playable Pressure
Station Nine map; developer laboratories, Blender sources, scripts, captures and support
settings are excluded. `packaging/build_furnace_candidate.py` exports a recorded commit,
publishes matching engine assemblies/runtime, stamps only the isolated package, requires
a private `.test` identity provider, and emits source, dependency inventory, file hashes
and archive checksums. `verify_furnace_candidate.py` checks the extracted files.
Shared package version stamping refreshes the runtime manifest on every packaging path.
The laboratory and two-client runners can exercise the package without putting fixtures
into the distribution; each run uses a fresh support directory.

Pvphit-game adds the contract-v1 `openra.outcome` event, immutable byte evidence and
conflict retention, two-participant identity verification, frozen release/map/image,
authoritative-file recovery before teardown and provenance in the result API/webhook.
The controlled watcher uses the engine's file and deterministic event ID, never its replay
footer as a fallback. The default-off exact local HTTPS webhook exception requires a
Local-only provider setup and retains DNS/IP pinning, TLS verification and redirect guards.
See sibling `docs/furnace-local.md` for exact environment and migration behavior.

Pvphit gates OpenRA completion on structured verified provenance, awaits completion
consumers before acknowledging delivery, reconciles archived completed results correctly,
and commits group settlement effects atomically under a row lock. The shared helper's
OpenRA statistics now use the group's game. Synthetic DB tests verify duplicate completion,
rollback/retry and completion followed by cancellation without a second effect. Existing
identity/key-linking contracts and cancellation policy are preserved.

## Verified boundary flow

```mermaid
sequenceDiagram
    participant C as Fork client
    participant P as pvphit API
    participant O as pvphit-game
    participant S as Fork dedicated server + watcher
    C->>P: Link account/device, signed challenge; profile lookup
    P->>P: Persistent numeric profile ID + revocable device key
    P->>O: API-key match creation and profile-ID roster
    O->>O: Freeze operator release/map/image; validate two opposing profiles
    O->>S: Local Docker-over-SSH; password, whitelist, identity URL, map pool
    O->>P: Signed server_ready: address, password, game_version
    C->>S: Matching mod/version, password and signed key authentication
    S->>P: Resolve authenticated fingerprint using same profile service
    S->>O: Durable match_start and verbatim immutable openra.outcome
    O->>P: Resolve BOTH outcome fingerprints and match roster
    O->>O: Validate build/map/outcome; store verified result and queue webhook
    O->>P: HMAC-signed completion with verification_source
    P->>P: Await consumer; atomic effects; mark delivery processed
    O->>S: Recover outcome/outbox/replay before remove; release slot/cleanup
```

This diagram follows implementation; it is not proof that this full path has run.
The handshake checks mod ID/version and order protocol, not a content checksum or engine
hash. Package SHA verification and unique candidate labels are therefore required. The
operator-selected map UID loads Furnace rules; generic `openra` support alone does not
select the new slice. Cash/starting units/faction come from existing map/rules. The private
coordinator must check opposing teams, zero handicap and normal speed before start; those
settings are not authenticated by the current outcome schema.

## Coupled references (unchanged outside local artifacts)

| Reference | Current responsibility / update boundary |
|---|---|
| OpenRA `VERSION`; pvphit/pvphit-content/ra/ra-content manifests | Source remains `{DEV_VERSION}`; local package alone stamped `fc-local-30fa940-step7.2` |
| Linux package / `candidate-manifest.json` / SHA256SUMS | Includes shared engine changes; map UID and identity endpoint recorded; checksum before install |
| Platform `MatchData.tsx`, socket server-ready guidance | Displays supplied `game_version`; removed misleading upstream fallback; no new hosted download metadata |
| Orchestrator public Dockerfile | Still tag `pvphit-20250330.1`, AppImage SHA256 `45c0c7c89cf8aa3345a8aa7fd6b9033fe44a2f5cd1fd3a01f1cab41fd3921016`; runtime now includes jq |
| Packer OpenRA inputs and deployment snapshot variables | Existing release/snapshot contract retained; branch snapshot 437438971 is not a Furnace acceptance artifact |
| `games.scoring_rules.release`, `map_uid`, `docker_image` | Operator configuration frozen per new controlled match; no production row updated |
| Local Dockerfile/image | Builds from exact candidate tar + recorded Debian digest; image ID belongs in the disposable game configuration |
| Map / required content | Pressure Station Nine UID above; inherited RA v2 basefiles/aftermath/cncdesert installer packages |

The Dockerfile tag/SHA, packer release and database release are a coordinated operational
contract, not an automatic equality check among those files. Before any external test
rollout, save the old tuple and update client metadata/checksums, image, snapshot inputs/ID
and scoring configuration together. That rollout is outside the local implementation.

## Ordered remaining work and acceptance

1. **Review congestion diagnosis/fix.** Inspect `validation/step7/congestion-excerpt.log`
   and the proposed patch. Original reproduction: current 30fa940 and environment baseline
   833a83543e, same replay/seed/map. Tank 31 (actor 180) reaches (29,60) at tick 9864;
   actor 184 requests a nudge while it is idle in that same tick; it reaches (30,59) at
   tick 9898. The later Lua `Location == goal and IsIdle` check misses the arrival.
   The proposed callback asserts completion at the exact goal, rather than relaxing
   distance, tank count, routing or timeout. Validate both recorded conditions and
   additional fixed seeds, then run through siege/capture/economy/end-of-suite. Keep the
   original evidence and distinguish original failed replay from corrected-fixture runs.
2. **Freeze reviewed candidate.** Record the three repository revisions plus patch hashes,
   SDK/runtime/dependency provenance, engine/mod versions, map UID, client archive SHA and
   server image ID. Any gameplay/engine/content change creates a new candidate; repeat
   affected checks and multiplayer/replay. No public version pins or pipelines yet.
3. **Complete isolated local platform flow.** Use two synthetic accounts, fresh databases,
   exact private identity/webhook origin with trusted test CA, and Docker-over-SSH confined
   to a disposable host. Fake pricing/email/Steam transports and deny external egress
   before starting the full platform. No production credentials or real funds. Run the
   success/failure matrix in sibling `docs/furnace-local.md`, proving winner identity,
   signed delivery, idempotency and cleanup. Component tests are not this gate.
4. **Finish final technical/presentation checks.** Run unchanged vehicle/building/systems
   labs on the frozen package; corrected environment lab after review; two controlling
   clients plus replay; separate live-observer lobby with audio visibility and perspective
   transitions. Do not weaken competitive authentication/whitelists to admit observers.
5. **Two physical Linux machines and humans.** Record CPU/GPU/driver, display/UI scale,
   audio devices, frame-time behavior and controls. Execute `first-human-playtest.md`.
   Record actual results, not an assumed 15–20-minute duration. Retest affected cases after
   reviewed fixes. Human balance acceptance remains provisional for this first slice.
6. **Private handoff.** Two to four named testers, one coordinator, one candidate at a time.
   Supply the artifacts/instructions below only after go/no-go review. Do not contact
   testers or upload builds as part of this work.

## Package, installation and joining

Local diagnostic artifact: `fc-local-30fa940-step7.2`, Linux x86_64; map UID
`2d3cd89c011e7c747871d8ac52927b40ddee1afb`. Account provider:
`https://furnace.local.test:18443/api/openra/`. This reserved test name must resolve to the
agreed isolated host and have a trusted test certificate before any linking attempt.
The package contains GPL COPYING/AUTHORS; corresponding source and dependency inventory
are sidecars. Original audio/art export manifests remain in runtime/source provenance.
The build reports .NET 6 end-of-support and a low-severity NuGet.CommandLine advisory;
record their disposition before handoff. No dependency upgrade was smuggled into this stage.

Build (a new destination is required; source checkout is never version-stamped):

```sh
python3 packaging/build_furnace_candidate.py   --revision <reviewed-engine-commit> --candidate fc-local-<unique-id>   --destination <new-private-build-directory> --dotnet <absolute-sdk-dotnet>   --sdk 8.0.425 --identity-base-url https://furnace.local.test:18443/api/openra/
```

Check `SHA256SUMS` before extracting into a new directory, then run
`python3 packaging/verify_furnace_candidate.py <extracted-directory>`. Keep support data
outside the extracted tree. Create a separate private support directory per tester and
launch `./furnace Engine.SupportDir=/absolute/private/support Server.AdvertiseOnline=False`.
With no RA data, use the included **Quick Install** (basefiles, aftermath, cncdesert), or
its Advanced Install supported original-media sources. Music/video are optional. Do not
redistribute an arbitrary developer Content directory. The initial installer still uses
inherited RA wording, correctly identifying the required original-game content.

For an authenticated run, obtain the server address, per-match password and version through
the private platform, link only a synthetic test account, and join through Direct Connect.
Check both manifests, endpoint, roster and lobby settings before ready/start. Keep join
passwords and tokens out of commands shared in reports. Save the exact candidate for replay;
replay behavior on a different engine/mod is not promised.

Install updates side by side. Back up the private support directory with restrictive
permissions before first launch; it contains account/device data. Never overwrite the old
binary tree or delete settings/keys to fix compatibility. Roll back by selecting the old
client and the matching old image/release/map tuple for NEW matches; drain existing matches
first. Restore a support backup only if needed, preserving identity files privately. The
source database enum addition is additive; leave it in place on application rollback.

## Test reports and evidence

Use `validation/step7/issue-template.md`. Each run records candidate/manifest hashes,
map UID, match ID (private), test case, two platform participant IDs (private), operating
system/hardware, expected/observed result and reproduction steps. Attach timestamps, relevant
logs and exact replay/map privately. Publicly share only redacted extracts: no passwords,
Authorization/X-API-Key headers, signatures, account tokens, private keys, `.oraid`, complete
settings or environment dumps. Replays can contain handshake/account identifiers: never
assume they are safe to publish or redact their binary contents in place. Keep the original
private and a hash in the report. Preserve outcome/conflict/outbox evidence before teardown.

Handoff deliverables: manifest + SHA256SUMS + corresponding source/dependency provenance;
installation/join instructions; supported-platform/limitation list; protocol + empty human
sheets; issue template; private diagnostics/replay instructions; coordinated rollback; named
owner and signed gate ledger. `.work` contains local evidence only and is not a distribution
mechanism; the produced checksummed archive is the packaging output.

## Go/no-go: ready for a controlled test build

All must be true for the SAME frozen candidate:

- [ ] Congestion classification/fix reviewed; full environment lab completes without waived assertions.
- [ ] Build, focused engine checks, YAML/sprites, all laboratories, two-controller network and replay pass.
- [ ] Real authenticated platform path and documented failure/retry/cleanup cases pass with synthetic data.
- [ ] Client/server engine/mod/map/provider match; manual competitive lobby rules verified.
- [ ] Two physical supported Linux machines pass fresh install, launch, join, replay, update and rollback.
- [ ] Required human matches, final listening/accessibility and observer transitions are recorded and reviewed.
- [ ] Presentation accepted; technical acceptance passed; human balance explicitly provisional; integration accepted.
- [ ] Manifest/checksums/provenance, instructions, limitations, issue collection and rollback are reviewed.
- [ ] Coordinator authorizes the small private group and diagnostic retention/access.

“Ready” means permission to hand this exact candidate to that controlled group. It does
not mean public distribution, broad hardware support, competitive balance certification,
production settlement readiness, or completion of deferred scope.
