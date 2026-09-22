# P1 countdown and edge integration review - 2026-09-22

Fresh separate-context Codex read-only reviewer; not cross-model or a phase-gate review.
Objective: audit D-019 Controller composition and D-020 Guard against B0/B2/B3/B4.
Scope: diff since `dd81fd3`, contracts committed in `fb82971`, actual implementation,
20 new independent locked cases, architecture changes, and both complete P0 staged source sets.

BLOCKER: none. MAJOR: none. MINOR: none in the reviewed scope.
- `src/core/countdown.cpp:77`: Buttons runs before Gate; the current qualification tick anchors the complete hold, including delayed calls; STOP wins and reset clears both components.
- `src/core/edge.cpp:32`: permission is checked before new edge/fault processing; persistent white requests escape; black AND script completion are required to exit.
- `src/core/edge.cpp:40`: all-white inhibition stays latched through black readings, completion and permission loss until explicit reset; unsupported positive push-through fails compilation.
- Fixed storage, bounded branches/loops, wrap-safe unsigned timing; no new allocation, clock read, static I/O, remote-command surface or motor-write path.
- Existing `test_countdown.cpp` and `test_edge_classifier.cpp` are unchanged from `dd81fd3`; config and board tooling are also unchanged. No locked predicate was weakened.
- New tests cover 10,000 seeded Controller streams, deadline/debounce/wrap/cancel/reset/STOP cases, all 16 masks at GO, persistent/re-entry/clear ordering and sticky fault inhibition.

Reviewer execution: `wsl -d Ubuntu -- bash tools/test_host.sh` exited 0; CTest 1/1 passed.
doctest: **97 cases, 5,214,158 assertions, all passed; 0 failed, 0 skipped**.
Raw output was read from `build/host/Testing/Temporary/LastTest.log`; `git diff --check` passed.

All 13 staged files per sketch were inspected, including empty core/hal placeholders.
Independent filename+NUL+bytes SHA-256 reconstruction first reproduced both `dd81fd3` manifest values, then approved these exact refreshed snapshots:
- `bench/p0_matrix`: `6f97c7466d8a01766d4640552aafd6bf897314bbc3a77c7c6028aac92e251a8a`
- `bench/p0_timing`: `088009162cc2a4bcc60c1bc7d92097751ef32bd71ae7b49958be8e59eeca64b2`
This authorizes manifest refresh for these bytes only, not upload, motor operation or a human gate. F-061's Immediate matrix restriction remains.

Limitations: the test-owned Controller -> Guard -> Governor pipeline is not actual app/HAL integration. Acquisition, full B3 services, motion scripts/replanning, full Robot FSM and MotorGate remain absent; no target compile, timing or physical R1/R5 proof is claimed.
No board command, upload, reset, motor run, commit or phase approval occurred in this review.
Next: coordinator records host evidence and exact hash refresh, then resumes only separately approved P1 work; all hardware and human gates remain pending.

Verdict: **PASS - scoped host integration and exact inert-source review only.**
