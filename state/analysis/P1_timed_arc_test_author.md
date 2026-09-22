# P1 B7 D-037 independent duration-only arc tests

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016; no gate inferred.
Objective: specify TimedArc independently from the motion.h contract committed
as d6bdff3, B7 duration-bounded arcs and approved B11/D-037 request defaults.

Owned files:
- tests/test_motion_timed_arc.cpp: 19 independent doctest cases.
- state/analysis/P1_timed_arc_test_author.md: this report.

Read BEHAVIOR.md B7/B11, DECISIONS.md D-037, current public motion.h/governor.h,
config constants, current PROGRESS.md and AGENTS handoff updates. AGENTS.md,
.claude/agents/test-author.md, active P1 and PLAN.md section 3 were read earlier
in this continuous session. Date remains the Tuesday 22 September plan start.
No src/core/*.cpp file was opened. No existing test, locked file, configuration,
implementation or another author's file was edited. No commit or shared build.

Coverage: inert defaults; all 256 direction encodings; each nonfinite argument;
finite invalid extremes and adjacent unit-interval limits; accepted signed zero,
subnormal/normal minima and values adjacent to one; zero-duration validation and
immediate completion; literal maximum duration 4,294,967 ms and conversion overflow;
mirrored requests and ratio endpoints; zero duty remaining ACTIVE until expiry;
400 ms adjacent microsecond/millisecond deadlines; 1 kHz timeline with no heading
or IMU parameter; duplicate times; delayed calls; micros wrap; cumulative elapsed
time crossing a complete start-relative wrap at the longest legal duration;
terminal status across later wraps; reset/restart and invalid-restart recovery.

The 10,000 fixed-seed mirrored property cases explicitly count five duration
classes and five observation-time classes (2,000 each), left/right originals
(5,000 each), ACTIVE/DONE outcomes (3,200/6,800), and exact zero/full duty and
ratio endpoints (1,000 each). Each case checks finite nonnegative unit-bounded
requests, the specified product ratio and mirrored wheel exchange. Counter
assertions prevent random-generator correlations from silently removing a class.

Explicit governor composition runs both directions at 9, 11.1 and 12.6 V for
a 1 kHz timeline, using REFLANK_TURN. It verifies initial inhibition by zero
elapsed slew budget, final caps, settled voltage compensation and immediate
zero at the same 400 ms deadline. It does not assume the final electrical ratio
stays 0.40 when outer-side saturation changes it.

No extra yaw cutoff, IMU qualification or voltage duration multiplier is invented.
No ambiguities requiring a new decision were found in this bounded contract.
Validation at handoff: CHECK/CHECK_FALSE only; coordinator owns compilation,
normal/sanitizer results and separate source review. No re-flank side choice,
charger skip, Robot arbitration, real MotorGate, physical trajectory, hardware
sample or MCU timing is proved by these primitive tests. Next action: coordinator
runs the cases and records actual validation results in state/.
