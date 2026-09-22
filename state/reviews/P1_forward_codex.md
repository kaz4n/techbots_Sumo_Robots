# P1 forward escape demand review - 2026-09-22

Read-only review in the separate context used for P1_integration_codex.md; not cross-model or a phase-gate review.
Objective: audit D-021's 0.80 forward request/cap and 70% inner-side request.
Scope: contract `79d2f6f`, source changes since `6ab4d2c`, nine new independent tests, exact config checks, architecture and complete P0 snapshots.

BLOCKER: none. MAJOR: none. MINOR: none in the reviewed scope.
- `src/core/edge.cpp:8`: straight and mirrored requests match the approved base/ratio; all invalid bias values return invalid zero demand.
- `src/core/governor.cpp:27`: EDGE_FORWARD selects the existing EDGE_BACK_DUTY cap and retains compensation, final caps, slew, reversal, brake and inhibit behavior.
- `src/config.h:97`: the only added tunable is the existing B4 ratio, 0.70; exact-value tooling checks preserve all 76 B16 defaults and reject unspecified extra constants.
- Requested left bias is (0.56, 0.80); settled 9 V final duty is approximately (0.690667, 0.80). Tests/documentation correctly avoid claiming a fixed final ratio or measured curvature.
- Added logic has bounded control flow and finite constant-derived requests, no allocation/clock/I/O/static execution path, and no route around actual motor hardware because that path remains absent.
- All established locked tests and board_tool.py are unchanged from `6ab4d2c`; no existing predicate was weakened. SC-M's D-021 resolution is recorded explicitly.

Coordinator ran the full host and separate sanitizer suites; reviewer inspected their raw logs and sanitizer compile/link flags.
Both CTest runs passed 1/1: **106 cases, 5,220,784 assertions, 0 failed and 0 skipped**; ASan/UBSan logs contain no diagnostics.
Tooling: **47/47 passed**, including exact 0.70/config values, inert staging hashes, changed-source rejection and upload restrictions; coordinator reported exit 0 for all suites.
Evidence: `state/analysis/P1_forward_core_tests.txt`, `P1_forward_sanitizer_tests.txt`, `P1_forward_tool_tests.txt`; `git diff --check` passed.

Independent reconstruction covered all 13 staged files per sketch; comparison with the prior reviewed set found only the five inspected config/edge/governor files changed.
Approved complete source SHA-256 values, now matching `tools/p0_inert_sources.json`:
- `bench/p0_matrix`: `3666582d873075f87bbbccdac685bf525d45752ca6b1141c600ff37e3b184869`
- `bench/p0_timing`: `62c6ba59a931ab55bf866b2a7e75a25eacf7ed69c029020855d17044fb7211b4`
These replace the prior integration hashes only for these exact bytes. No upload, motor-run or human-gate authorization is supplied; F-061 remains in force.

Limitations: helper and test-owned guard/governor composition do not implement timed/heading-held escape, replanning, full FSM/app, HAL/MotorGate or target/physical validation. No board was contacted by this reviewer.
Only this new review file was written; prior review preserved. No implementation/test/config/ledger edit, commit or phase approval was made.
Next: coordinator saves evidence and continues separately approved P1 work; motion contracts and hardware/human gates remain pending.

Verdict: **PASS - scoped D-021 host behavior and exact inert-source review only.**
