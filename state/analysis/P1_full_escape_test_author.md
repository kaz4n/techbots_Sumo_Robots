# P1 independent full Escape test author

Date: 2026-09-23, Asia/Dubai. P1 host-only under D-016.

Objective: protect committed public contract 5360c80, B4/B6/B7/B8 and
D-047/D-048/D-049/D-050/D-054 independently of implementation. Owned files are
`tests/locked/test_edge_escape.cpp` and this report. Only specifications,
decisions and public headers were read; no implementation cpp was inspected.
All established locked tests, headers, config, ledgers and build files remain
unchanged. No build or commit was performed by this author.

Forty-two new cases cover all 16 line patterns and all 256 high-bit variants,
ordinary/head-on selection, default and captured shared side, pushed-out priority
over every eligible ordinary row and strict positivity of both prior final duties.
The tests distinguish consumed context from ignored payloads: both duties are
validated for a centered rear predicate, side only for head-on/qualified both-rear,
and current/initial heading according to healthy/unavailable IMU rules. Pattern
faults and closed permission retain their documented priority.

Lifecycle coverage includes persistent-white completion, initial zero budget,
three allowed replacements and the fourth-request fault, clears/reassertions,
multiple new bits, ignored high bits, new-bit/completion ties and successful-start
accounting. Explicit traces distinguish the phase at call entry from the phase
entered on that observation, and the captured intended pivot side from reversed
overshoot correction. A wrong-side bit can be ignored by the old pivot while
DONE-with-white still requests one replacement. Failed replacement context does
not increment budget, and ordinary context changes do not retarget an active row.

New RowExecutor::startPushedOut cases check mirrored 45-degree pivots, strict
five-degree tolerance, 90 ms timed fallback/recovery, the 700 ms timeout pulse,
200 ms forward duration, invalid capture and reset. The independent precision
regression requires RIGHT45 from raw origin -1e-6F to complete at healthy yaw40F;
its exact-zero/positive-origin boundaries and mirror remain distinct. Existing
locked row/head-on cases are not edited.

Fault and evidence cases check reset-only pattern/replan/permission/context
inhibition, existing fault retention with closed permission, no new fault while
inactive and gated, no budget reset or resumed motion after permission loss,
all-black-before-DONE continuation, and one-shot true exit. Only current healthy
finite raw yaw supplies inward evidence; fallback/cached yaw never refreshes it.
Timeout pulses survive same-call replacement/exit once. Delayed observations,
repeated uint32-wrap episodes and finite extreme headings are included.

Deterministic all-mask mirrored streams compare phases, replans, fault outcomes,
event pulses and swapped finite bounded demands across wrap. Actual Governor
composition at 9 V proves the final 0.80 escape cap, immediate braking from prior
full duty, and immediate zero/persistent inhibition for faults and permission
loss. These are component compositions, not a full Robot/MotorGate, QTR freshness,
physical inward-orientation, motor-run or phase-gate claim.

Static handoff: 42 cases; CHECK/CHECK_FALSE only, no throwing checks or trailing
whitespace. Tests are frozen for the coordinator's full host/sanitizer builds and
independent review. Runtime validation is pending; these expectations must not
be weakened to match an implementation failure.
