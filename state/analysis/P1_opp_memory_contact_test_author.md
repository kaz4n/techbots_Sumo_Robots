# P1 B5 bearing memory/contact independent test authorship

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016; no gate acceptance.
Objective: independently specify accepted D-026 deterministic bearing memory and
D-027 contact lifetime before assessing the implementations.

Owned files:
- tests/test_opp_memory_contact.cpp: 30 new doctest cases.
- state/analysis/P1_opp_memory_contact_test_author.md: this report.

Sources read: current AGENTS.md, test-author role, BEHAVIOR.md B0/B5/B9,
DECISIONS.md D-026/D-027, opp_fusion.h contract committed as 290c13b, config.h,
types.h and governor.h. No src/core/*.cpp implementation was opened. No existing
locked test, header, configuration or another author's file was edited.

Bearing coverage: all 128 masks with/without previous detection; high-bit
ignoring; every table row; front/side/rear priority; bilateral conflicts and
missing history; reuse of previous relative bearing with current world heading;
newly lit front-bit recency, simultaneous ties, held bits and timestamp wrap;
empty current views with retained old memory; world angle wrap, finite extrema,
nonfinite headings and reset. Extreme headings are checked for finite canonical
range, without claiming sub-degree numerical accuracy at float maximum.

Contact coverage: 19/20/21 observations for 111 and 101; pattern changes and
every front-pattern interruption; all 128 masks; strict axis 1.5 g and adjacent
floats; Euclidean diagonals; huge/tiny finite accelerations; NaN/infinities per
axis and IMU availability; visual cues despite invalid IMU; cue visibility and
latch eligibility across all 256 state byte values; every state exit, target/
centering loss, re-entry, reset and CONTACT rising-event behavior.

Exact binary diagonal fixtures include (0.75,1.0) => 1.25 g and
(0.9375,1.25) => 1.5625 g. The inexact decimal (0.9f,1.2f) pair is deliberately
not treated as an exact 1.5 g tie. No threshold epsilon is added.

Integration coverage: real Contact results and current front centering feed the
real Governor at 9, 11.1 and 12.6 V. Full duty eligibility requires current
centered contact; clearing contact reduces the final cap immediately. These
tests do not implement or claim the separate FSM target-loss brake transition.
The 10,000 fixed-seed mirror cases assert 5,000 with and 5,000 without history,
finite canonical world angles and symmetric impact/contact results.

Validation at handoff: 30 cases counted; no whitespace issues; only CHECK and
CHECK_FALSE assertions. No shared compile/test was run by this author. The
coordinator owns normal/sanitizer runs and final result receipts.
Ambiguities: none requiring invented behavior within the committed contract.
Limits: debounce/polarity, stuck/phantom policy, whole FSM, physical contact,
IMU freshness, HAL/MotorGate writes and electrical/robot timing are not proved.
Next action: coordinator runs unchanged tests, resolves failures against the
specification and records final evidence in state/.
