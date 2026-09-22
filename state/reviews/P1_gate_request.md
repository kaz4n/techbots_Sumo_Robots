# Prepared P1 gate-review request — NOT READY / GATE-PENDING

Independent review of SumoX-26. Reviewer reads AGENTS.md first and edits no file.
This is a filled continuation request, not reviewer output or human approval.

Phase under review: **P1**, developed offline under D-016 while P0 acceptance is
still pending. Software range: **2c6e95d..5595b57**; include the subsequent checkpoint
documentation commit when reviewing the full submission. Recalculate the range
after additional implementation; do not use this partial snapshot as a complete gate.

Spec sections: BEHAVIOR B0–B16 with D-017 through D-021 amendments;
HARDWARE section 8; AGENTS R1–R11; P1_core_logic tasks/exit criteria.

Currently evidenced: B0 types, B3 hold/button qualifier and Controller, B4 classifier,
Guard and forward demands, B5 debounce/front rows and B6 governor. **106 host cases
pass**, with 5,220,784 assertions and separate ASan/UBSan success. Spec-only authors
and scoped separate reviews are documented, including fresh integration review.
Tool controls: 47/47 pass. See `analysis/P1_forward_validation.md` and both the
`P1_integration_codex.md` and `P1_forward_codex.md` review reports.

Exit criteria:
- [ ] 60+ tests **and every specified table row/locked invariant covered**: count
  threshold met, complete coverage and integrated R1/R5 still incomplete.
- [ ] Core compiled for the actual UNO Q toolchain: no target available.
- [ ] Full safety audit and genuinely fresh review with no open BLOCKER: pending;
  scoped component/integration review is not this gate.
- [ ] Team member explains complete state diagram; EXPLAINED OK: not supplied.
- [ ] Human GATE P1 PASS: not supplied; agent must not author it.

Before review can pass: complete remaining module contracts/implementations and
table coverage after specific protected decisions, full FSM/core-output R1/R5
proofs, target compile, and required human evidence. Actual MotorGate write-boundary
testing is required when HAL is implemented in the later phase; it does not
replace these P1 core-output proofs.
No P0 gate may be inferred from D-016 or these host results.

Review in the order prescribed by REVIEW_GATE.md: trace R1–R6 safety paths and
motor writes; check spec conformance; independent tests and locked-file history;
bounded tick work/wrap/finite duties; explainability; real measurement provenance.
Report BLOCKER/MAJOR/MINOR with file:line and suggested fixes, then PASS or FAIL.
Until that real review exists, its verdict remains **PENDING**, not simulated.
