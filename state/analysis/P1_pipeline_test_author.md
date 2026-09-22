# P1 B5 independent composed-perception tests

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.
Objective: specify Fusion and split Contact observation/commitment from header
30b16d5 and B5/D-026/D-027/D-029/D-030/D-031, without implementation access.

Owned files:
- tests/test_opp_pipeline.cpp: 25 independent doctest cases.
- state/analysis/P1_pipeline_test_author.md: this report.

Read public opp_fusion.h/governor.h, current B5 and relevant approved decisions,
PROGRESS.md, config constants and AGENTS handoff updates. The complete AGENTS.md,
test-author role, P1 and PLAN.md were read earlier in this continuous session.
No src/core/*.cpp implementation was opened. Existing component tests were read
only for assertion style; no existing Contact::step test or other file was edited.
No shared build or commit by this author.

Coverage: all 128 raw logical masks through the specified electrical polarity,
including unused high bits and two-fresh-sample assertion; exact clear hysteresis
and micros wrap; initial bilateral bearing uncertainty; relative/world validity;
20-confirmed-sample close cues with repeated cached observations; split Contact
commitments that cannot sample twice; example equivalence with legacy step;
same-tick ATTACK entry; all non-ATTACK exits and confirmed target/centering loss;
no stale latch on re-entry, double commit or missing commit; cached changed data
ignored without reopening the single commitment; pre-edge state for phantom
marking; current/prior contact blocking; effective-only bearing memory and expiry;
close-mask phantom override before contact qualification; newly stuck bits removed
before cues and bearing; stuck evidence surviving phantom suppression; reset of
all stages and protocol state; one-shot filter pulses; exact phantom boundaries
across wrap; explicit governor composition with valid current centered contact.

A 10,000-tick mirrored property stream checks masks, cues, bearing groups/angles,
phantom events and committed contact across a micros wrap. A deterministic odd
permutation visits all 128 raw masks; each coverage count is asserted at least 78
and the sum exactly 10,000. Wrapped world bearings are compared circularly so the
shared positive-180 convention is not mistaken for a mirror failure.

Validation at handoff: CHECK/CHECK_FALSE only; coordinator owns compilation and
normal/sanitizer evidence. No full Robot arbitration, actual motor permission,
hardware sample freshness, physical spectator/contact inference or MCU timing
is proved. Governor composition intentionally applies the ATTACK profile to show
its independent contact cap; it is not a test of the future FSM profile selection.
No protocol behavior is inferred beyond the committed header. Next action:
coordinator runs these tests and records actual validation findings in state/.
