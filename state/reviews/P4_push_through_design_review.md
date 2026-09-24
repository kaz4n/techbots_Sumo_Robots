# D131 design review

Separate fresh-context Codex reviewer `/root/p4_push_contract_review`, 24 September
2026; read-only source/spec review before implementation. Same-model review,
not cross-model review, hardware acceptance or a phase gate.

Verdict: PASS, no BLOCKER/MAJOR. Three clarifications were incorporated before
implementation and independent oracle freeze:

- Any qualified unsuppressed stall during deferral revokes before limiter
  admission, including when capacity would deny REFLANK. The earlier phrase
  "would leave ATTACK" was narrower (`fsm_robot.cpp:751`).
- New-white invalidates an existing contact's stall qualification; a feasible
  short-window fixture starts contact after deferral, then supplies fresh
  deflection greater than25 degrees (`stall.cpp:36`). The1000ms timer cannot
  expire inside a20..100ms window.
- Every transition from DEFERRED to ESCAPING, including immediate pattern or
  context faults before successful row start, must initialize the union's
  replan counter0 (`edge.cpp:353`). No timestamp may be exposed as replans.

The reviewer found the no-renewal/rearm, normalized FC, source freshness,
default-false authority and bounded second Escape call consistent with the
referenced rules. File:line references describe the pre-implementation source.
This report records the reviewer's returned findings; no tests were executed
for this design-only review. Actual diff, tests and final scoped review follow.
