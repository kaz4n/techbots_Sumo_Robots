# P1 B12 O2 DIRECT independent test authorship

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016; no gate acceptance.
Objective: specify standalone DIRECT motion and exit requests independently of
implementation, using the committed public interface and accepted behavior.

Owned files:
- tests/test_opener_direct.cpp: 26 new doctest cases.
- state/analysis/P1_direct_test_author.md: this report.

Sources read: current AGENTS.md, .claude/agents/test-author.md, PROGRESS.md,
PLAN.md section 3, active P1 prompt, BEHAVIOR.md B0/B1/B2/B6/B7/B12 O2,
DECISIONS.md D-022/D-023, openers.h contract committed as 4acc9c1, motion.h,
governor.h, types.h and config.h. No src/core/*.cpp implementation was opened.
Existing test headers/helpers were read for local doctest style; no existing
test, locked file, header, configuration or another author's file was edited.
Local date matches the plan's Tuesday 22 September start; D-016 allows the
current host development before the pending P0 hardware gate.

Coverage: inert defaults, start/reset/restart, a complete 1 kHz straight
timeline, exact 400 ms termination, adjacent 1 us and 1 ms samples, delayed
first invocation, nearly full uint32 call gap and micros wrap. All 128 current
masks, all 128 snapshot masks and all 16,384 snapshot/current pairs enforce
front priority, side/rear current detection and ignored side/rear snapshots.
Unused mask bit 7 is ignored. Detections precede the deadline on its exact tick
and on a delayed first terminating tick. Every normal/invalid exit latches zero.

Heading coverage: captured reference, repeated error without drift of the
reference, opposite correction signs, angular wrap and accumulated yaw,
D-022 gain/cap/no reversal, finite extreme headings, rejected nonfinite starts,
invalid healthy samples, ignored nonfinite unavailable samples, IMU recovery
and unchanged fallback deadline. Extreme finite headings assert finite bounded
outputs without claiming small-angle numerical precision at float maximum.

Property coverage: 10,000 fixed-seed mirrored episodes, with current/snapshot
mask mirroring, heading mirroring, active/fallback/recovery samples, completion
or detection exits, finite nonnegative bounded requests and terminal zeros.

Composition coverage: explicitly feed DIRECT requests to the real Governor
under OPENER at 9, 11.1 and 12.6 V. Check first-tick zero, 1 ms slew, settled
compensation/final cap, immediate zero on detection exit and voltage-independent
400 ms completion. Even a composed request with centered contact retains the
OPENER cap. This fixture selects that profile explicitly; it does not prove
future FSM profile selection or MotorGate permission.

Contract distinction: FRONT_TARGET is a zero-duty exit intent. Tests do not
interpret it as an ATTACK state transition or full-duty authorization. The
committed header resolves snapshot priority and detection/deadline precedence.
It does not specify a motion status for a detection exit, so tests require its
exit enum and zero requests without inventing a status policy. No unresolved
ambiguity requires a new behavior decision for this bounded component.

Validation at handoff: 26 cases counted; only CHECK/CHECK_FALSE assertions;
no shared compilation or test run by this author. Coordinator owns the normal
and sanitizer suite and evidence of actual pass/failure.
Limits: no Robot/ScenarioRunner integration, global arbitration, debounce,
countdown release, edge handling, other openers, physical travel, board compile,
MotorGate writes or real-time MCU measurement is proved by these cases.
Next action: coordinator runs the unchanged cases, resolves failures against
the contract and records complete validation evidence in state/.
