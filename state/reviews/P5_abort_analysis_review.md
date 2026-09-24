# D136 private companion-analysis review

Status: PENDING implementation review and authorized execution. No software PASS claimed.
Provenance: separate same-model reviewer reusing prior P4/D134/design context; not fresh gate review or cross-model. Only review/raw ownership; no production, public test, ledger, compiler or board changes.

Nineteen private spec-derived methods and a hash-bound runner are frozen in
`P5_abort_analysis_review_raw/private_freeze.json` before reading any future
companion implementation or new public test bodies. The adopted public
`decode_cue(value, mode)` seam is included. Coverage and generation provenance
are recorded in `P5_abort_analysis_review_raw/freeze.md`.

All generated evidence is temporary and synthetic, including deliberately
fabricated hardware-origin declarations. No probe/import or compiler/board
execution has occurred. Source identity, full token/EN producer guarantees,
physical ten-trial completeness, target fit and phase gates remain separate.

Next action: coordinator freezes the implementation/public expectations, then
authorizes private runner execution with the exact implementation hash. Preserve
first failures and unchanged original oracles before any justified correction.

## Independent metadata binding check, 2026-09-24

The separate D135 reviewer checked the original 19 methods against the D136
closure/loss clarification: no conflicting expectation; probes remain unchanged.
The first freeze is preserved as `private_freeze_first.json`; only its contract
dependency hash changed. See `contract_binding_update.json` for exact bindings.
These private methods do not directly cover every clarified closure/aggregate-only
loss case. Complementary public/source review remains required. No imports or
execution occurred; implementation acceptance and first execution remain pending.
