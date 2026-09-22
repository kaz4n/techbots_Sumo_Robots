# P1 STOP-hold test author — 2026-09-22

Objective: independently encode B13/D-035 logical BOTH debounce, full hold,
reset-only STOP retention and Controller composition from public contract
`6a15674`. Read replacement AGENTS instructions, the test-author role, B13,
D-035's recorded user approval and `countdown.h`. No implementation `.cpp` was
opened. The local date was checked as 2026-09-22; work remains P1 host-only.

Only new files `tests/locked/test_stop_hold.cpp` and this report were authored.
No existing locked test, config, shared ledger or another author's file changed.

## Coverage

Twelve cases cover boot-held BOTH; exact/adjacent 20 ms debounce and full 1000 ms
hold thresholds; raw-edge-plus-hold rejection; delayed qualifying calls without
backdating; release priority before latching at either deadline and on the next
observed tick; every non-BOTH enum as an initiator/canceller; latched retention
through all 256 button values; reset; micros wrap and legal UINT32_MAX gaps.

Controller cases cover internal STOP from IDLE and READY, MODE cancellation of
COUNTDOWN while BOTH qualifies followed by STOP, immediate external STOP during
pending debounce and at the GO deadline, retained inhibition on release, and
reset into boot-held START followed by a fresh qualified 5.1-second start hold.

The seed `0xB013D035` generates 10,000 logical STOP episodes with boot-held versus
initially released input, raw bounce/invalid values, delayed qualification,
independently calculated 64-bit deadlines, optional pre-deadline cancellation,
later requalification, latching, long legal gaps and reset. Expected deadlines do
not derive from any output or internal state of StopHold.

## Evidence and limits

Authorship is ready for the coordinator's full host build and independent review.
No build was run by this author. No scoped ambiguity or contradiction was found.
Release-on-deadline behavior follows the explicit committed header requirement.

`rg -c 'TEST_CASE' tests/locked/test_stop_hold.cpp` reports 12 cases;
`git diff --check` returned exit 0 at author handoff.

These are pure logical safety tests. They do not establish that the physical A1
ladder distinguishes BOTH, prove ADC timing, drive the full Robot FSM, or verify
MotorGate EN/PWM writes, hardware reset, robot WCET or physical motor inhibition.
No board contact, motor run or phase-gate approval is claimed.

Next action: coordinator runs the complete host suite; independent reviewer
checks implementation and evidence without weakening any test predicate.
