# P1 independent SEARCH test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: test B8 SEARCH, D-041 retained side and D-042 full-sweep fallback from
the public contract, independently of implementation. Owned files are
`tests/test_search.cpp` and this report only.

Read AGENTS, B2/B7/B8 and SIDESTEP O1, D-041/D-042, config, and public fsm,
motion, governor and opponent-fusion headers. Contract daddb87 was clarified by
421a766 before test establishment: last_side is always validated, inactive hint
payload is ignored, and consumed recent world bearings must be finite and in
(-180,180]. These API defenses do not introduce a robot fault-response policy.
No src/core/*.cpp implementation was read. No existing tests, config, state
ledgers or shared build files were edited. No build or commit was performed.

The 31 cases cover:

- Literal 3,000 ms memory, 5,000 ms inward history, 360 degree scan, 300 ms
  advance, 0.45 scan/0.30 advance duty and 2 ms/degree fallback defaults.
- SearchSide default/right reset; valid positive/negative bounds; zero,
  unavailable, nonfinite and out-of-range retention; real BearingMemory
  composition showing front/side/rear selection before side retention.
- First scan precedence across hints, both retained sides and positive,
  negative, small nonzero and zero memory turns. The captured initial turn sign
  survives overshoot. Exact antipodal ties choose RIGHT. A public mathematical
  regression uses heading +180/world +0.000001 -> LEFT and the mirrored pair ->
  RIGHT, preserving tiny finite offsets before the exact tie.
- Memory TTL at 2,999,999/3,000,000/3,000,001 us, with no cancellation when
  memory expires during a captured turn; B7 strict tolerance, 700 ms timeout,
  one-call timeout pulse and initially missing-IMU memory turn.
- Directed continuous scan progress below/at 360 degrees, accumulated-heading
  crossings, both directions, opposite/oscillating movement, and healthy scans
  continuing beyond 700 ms. Net directed displacement, not absolute travel or
  shortest-angle wrapping, ends the scan.
- Missing IMU at scan entry requires exactly 720 ms. Mid-scan loss uses the
  last valid remaining sweep, including opposite progress clamped to 360.
  Unavailable yaw is ignored. Recovery neither shortens nor restarts fallback;
  recovered or last-known valid heading supplies the next primitive reference.
- Internally aged inward history immediately before/at/after five seconds,
  capture of the advance reference, exact 300 ms advance, one-shot first hint,
  alternating cycles and delayed transitions beginning at observation time.
- Every one of 256 masks in MEMORY_TURN, SCAN and ADVANCE. Any low-seven-bit
  target requests zero/PERCEPTION before invalid-yaw/deadline handling; high
  bit alone does not count. Terminal results stay zero and pulses do not replay.
- Initial/active nonfinite yaw, consumed versus unused context validation,
  extreme finite continuous yaw, reset/restart, exact deadlines over timestamp
  wrap and repeated cycles over several wraps without expired history revival.
  Every supplied consecutive time gap remains below one complete uint32 wrap.
- Ten compact mirrored streams spanning five initial headings and two IMU
  modes compare phase, pulses, fallback, direction and bounded wheel symmetry.
- Test-owned Search -> Governor composition demonstrates low-voltage scan
  compensation, advance correction limited by SEARCH_FORWARD, immediate zero
  under revoked permission, and zero at a target-driven executor exit.

Static handoff: 31 cases, CHECK/CHECK_FALSE only, no trailing whitespace, and
no compiler/test runner invoked by this author. Parent owns actual host and
sanitizer validation and any resulting evidence records.

Limits: this is an executor/retained-side test, not full Robot arbitration or a
hardware demonstration. Truthful world/inward ages, effective current targets,
real escape completion, fresh sensor acquisition and the caller's permission
are supplied assumptions. No target-state assignment, opener routing, edge/STOP
preemption, MotorGate/EN writes, physical sweep equivalence, scheduler timing or
phase gate is proved. The governor harness supplies permission explicitly and
does not infer it from a SEARCH phase.

Next action: parent reviews and builds the frozen files, records verified host
and sanitizer outcomes, and commits the completed batch.
