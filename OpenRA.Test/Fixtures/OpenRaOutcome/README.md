# OpenRA outcome event fixtures

Copies of `docs/openra/fixtures/outcome-event-{final,unresolved,desync}.json` from
[pabl-o-ce/pvphit](https://github.com/pabl-o-ce/pvphit/tree/main/docs/openra/fixtures),
**contract_version 1** (`docs/openra/results.md`). CI clones only this repository, so the
files are copied rather than referenced, and renamed without `-` so their embedded
resource names stay predictable.

`OutcomeEventTest` compares `OutcomeEventBuilder` output against these files field for
field, including property order. When the contract changes, update the pvphit fixtures
first, copy them here, and bump the version above.
