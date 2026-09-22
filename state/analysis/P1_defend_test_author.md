# P1 B10 independent defensive-turn tests

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016.
Objective: specify DefendTurn target capture, B2 target exits and separate B7/B10
deadlines from the public fsm.h interface committed as f2a6099.

Owned files:
- tests/test_defend_turn.cpp: 23 independent doctest cases.
- state/analysis/P1_defend_test_author.md: this report.

Read current AGENTS.md, .claude/agents/test-author.md, PROGRESS.md, BEHAVIOR.md
B0/B2/B7/B10 and the public fsm.h, motion.h and governor.h contracts. PLAN.md
section 3 and the active P1 prompt were already read during this session. Local
date remains Tuesday 22 September. Existing tests were read for doctest style.
No src/core/*.cpp file was opened; no implementation, existing test, locked test,
configuration or another author's file was edited. No build or commit by author.

Coverage includes default inert state; invalid heading/bearing and missing bearing
validity; strict (-180,180] capture interval; all four B5 side/rear directions;
fixed target across changing masks; accumulated and extreme finite headings;
five-degree completion boundary from both sides; gain and duty bounds; all 128
masks with/without high bit, before/at both deadlines and across micros wrap;
literal 700/800 ms separation, adjacent microseconds and one-shot pulses;
healthy completion remaining zero without retarget/restart; latched front/no-target
intents; unavailable IMU fallback at angle*2 ms; loss/recovery and original turn
deadline; invalid healthy readings; complete 1 kHz wrap timeline; delayed/nearly
full legal micros gaps; reset/restart; 10,000 fixed-seed mirrored captures; and
explicit PIVOT governor composition at 9, 11.1 and 12.6 V.

Contract boundaries: if the first observed call is already past both deadlines,
tests require the specified defend timeout/SEARCH but do not invent a retrospective
primitive timeout pulse. Invalid healthy samples must preserve B7 INVALID/zero;
the header does not prescribe their particular wrapper intent, so those tests do
not choose it. No 720 ms search-scan fallback is imported into a defensive turn:
its accepted relative angle is at most 180 degrees and B7 keeps its 700 ms cap.
The finite-heading tests require relative-direction preservation through normalized
yaw; they do not require physically meaningful precision for huge absolute yaw.

Validation at handoff: authored using CHECK/CHECK_FALSE only; coordinator owns
compilation and normal/sanitizer result evidence. These tests address the new
component only; they do not modify or waive any independent locked-test approval.
No Robot arbitration, real MotorGate, hardware acquisition, board compile,
physical turn or target worst-case timing is proved. Next action: coordinator
runs these cases, resolves failures against the committed contract and records
the actual validation outcome in state/.
