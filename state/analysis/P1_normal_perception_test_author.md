# P1 independent normal-perception test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: protect the NormalPerception public contract committed in b17696d,
B2/B5/B6/B9 and approved D-027/D-036/D-045/D-046. Owned files are
`tests/test_normal_perception.cpp` and this report. AGENTS, the active P1 prompt,
relevant specifications/decisions and public headers were read. No core
implementation cpp was read; no existing tests, headers, config or state ledgers
were edited. No build or commit was performed.

Sixteen focused cases cover all 256 masks with a literal eight-row centered
table, high-bit ignoring and current front priority over every lower-group
combination. Literal three-observation expectations cover first/second/third
entry, changing centered rows, pending/saturated interruptions, long retained
qualification, reset/preemption and reset of front-presence/loss history.
Every front-free residual mask is checked after one/two TRACK observations and
after ATTACK entry: loss brakes once, then current-perception routing remains
available without an extra brake. Both off-center front rows also require the
loss brake; side/rear changes or disappearance alone do not.

The test-owned composition uses production Fusion, NormalPerception, contact
commit, frontDemand, Governor, Search, DefendTurn and Guard. It checks electrical
polarity/debounce before qualification; duplicate Fusion observations skipped by
the caller; a prior impact cue not authorizing later ATTACK; a fresh cue on the
third observation authorizing contact; and stale contact cleared by script exit
or off-centering. At constant 9 V, TRACK remains capped at 0.30 and reacquired
ATTACK at 0.60 until fresh contact. All composed outputs are finite and bounded.

The loss scenario begins at full duty and checks immediately before and at the
literal 30 ms front-clear deadline. On that exact loss observation, actual
Search or DefendTurn nonzero requests are overridden to zero by the new brake
directive; the following observation permits the real request through normal
governor slew. An external-arbitration harness also applies the established
Guard veto, clears contact/qualification and preserves the all-white fault.

Static handoff: 16 cases; CHECK/CHECK_FALSE only (no REQUIRE or throwing checks),
no trailing whitespace and no shared builds. Parent owns runtime/sanitizer
evidence and review before commit. This harness demonstrates component contracts;
it is not production Robot arbitration, MotorGate behavior, physical sensor
freshness, motor permission or a passed phase gate. NormalPerception deliberately
has no clock or duplicate-observation detector; freshness remains its caller's
explicit responsibility. No additional strategy or recovery policy is assumed.
