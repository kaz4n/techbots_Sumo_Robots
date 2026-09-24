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

Usage-guide source review: no material contradiction with D136; M0, timing bound
and physical/permission limits are correct. Nonblocking schema-detail suggestions
are recorded in `P5_abort_analysis_review_raw/usage_doc_review_first.json`.
Implementation body remains unread pending the coordinator's first source hash.

## User-requested pause checkpoint, 2026-09-24

Review stopped before completion. First implementation `c0afe321`, SHA256
`9891c3eaa8a283d918d1e253a691c55c3d7d8ad3b9574eefcc14452f1e8b7843`.
Retained first results: public 74/74 PASS; private 18/19 PASS, one failure.
No implementation, oracle, runner or first-receipt edit was made by this reviewer.

1. **Private injection mismatch, narrow correction not yet authorized/executed.**
   `private_probes.py:475` patches its conventional imported CSV module, while
   `analyze_opener_abort.py:16-20,549` loads and calls a distinct module object
   from the same unchanged validator file, following unchanged D130's pattern.
   The callback therefore never mutates the fixture; the zero call count does
   not demonstrate a binding defect. `_snapshot:340-345` checks bytes/hash/rows.
   Frozen public `validated_then:239-264` intercepts the actual dependency by
   source identity and its event/summary same-size restored-mtime tests pass.
   Preserve the original 19-case source and failure before any harness correction;
   retain mutation stimulus, exact call-count and INVALID/cleared-endpoint assertions.
2. **Potential MAJOR: unsupported duplicate config declaration admitted.**
   `_config_value:215-231` catches extra assignment, semicolon or array forms,
   but its extra-identifier check misses direct/list initialization. Appending
   `namespace duplicate { inline constexpr std::uint32_t TICK_US{2000U}; }`
   after the seven canonical declarations leaves one regex match and passes
   both extra-use rejection predicates. Ordinary reads are allowed by D136;
   duplicate/unsupported declarations are not. This is source-derived evidence,
   not an executed reproduction; independent adjudication remains pending.

Exact next step after user resume: preserve/adjudicate the duplicate-declaration
case with a bounded coordinator-owned probe, then decide any narrow production
fix and independently approved test-harness correction. Complete the remaining
source/contract review and rerun source-bound public/private and prior regressions.
No D136 acceptance verdict, further execution or permission follows this pause.
