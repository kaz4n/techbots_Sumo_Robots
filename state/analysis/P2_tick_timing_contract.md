# D092 whole-tick acquisition and decision timing

2026-09-23 Asia/Dubai; baseline a57d3b7. D051/D075 authorize this P2 software
integration decision. The preceding goal turn made concrete progress: D091 actual
bare-board recorder runtime, independent review and evidence committed a57d3b7.
SC-AK conflicts P1_robot_contract.md's decision-as-start duration with D084's
post-acquisition decision time. This amendment resolves only that timing contract.

## Public input and fixed lifetime

Append fsm::TickTiming timing to RobotInput. TickTiming fields are
bool explicit_start=false, bool start_valid=false, uint32_t started_us=0.
Existing field order and default legacy callers remain unchanged. The first
admitted Robot tick selects timing.explicit_start for the Robot lifetime until
reset, even in BOOT. A duplicate decision timestamp is not an admitted tick.

Legacy selection preserves the existing receipt equation and unsigned ordering
exactly when explicit_start stays false; ignore start_valid/started_us entirely.
Legacy measures from the preceding decision timestamp and proves whole-tick
execution only if that really was the caller's start. Production app integration
must select explicit timing from its first tick. Any later selector mismatch
invalidates timing for that tick and the preceding receipt bounded by it, without
silently changing the selected mode. Returning to the selected mode may admit
later valid receipts; timing_incomplete remains latched for that attempt.

Explicit selection requires start_valid and unsigned decision-minus-start below
2^31. Equal start and decision is valid. Save the admitted tick's start, validity
and token with its pending request. Do not reread changed current metadata as the
previous tick's start. Invalid start is not a motor contract or sensor fault.

## Complete receipt chronology

For explicit timing, let S,D,A,C be the pending start, decision, actual application
and completion, and N,E the current start and decision. All offsets are uint32
subtraction from the common S anchor, and all must lie below 2^31:

    0 <= D-S <= A-S <= C-S <= N-S <= E-S < 2^31

Both pending and current timing metadata must be valid for the fixed selected
mode. Equal boundaries are permitted. Require the existing valid identity and
application-time receipt checks plus duration_valid and execution_us == C-S.
No extra maximum duration is invented: large but unambiguous durations remain
counted and may overrun/clamp existing record fields. Full modulo wrap is valid;
exact half-range and ambiguous/reversed/future/overlapping chronology is invalid.
A malformed current start invalidates the preceding member's duration, even if
completion would fit before its decision; do not replace unknown start with E.

Keep application admission independent and unchanged: actual application still
matches the previous token, lies between its decision and current decision, and
obeys permission/duty/sign/quantization constraints. Timing metadata cannot repair
invalid application or invalidate otherwise-valid application. Thus timing-only
errors mark timing evidence incomplete and do not manufacture APPLICATION_CONTRACT
or motion inhibition. Existing non-timing faults remain unchanged. Preserve the
existing distinction that timing admission uses identity/time, not duty validity.

## Membership, timestamps and evidence

Timing membership remains GO through the one final inhibited stopping tick.
Include the GO tick's acquisition before its GO decision. This never moves GO,
START release, the full countdown hold, source timestamps, application time or
any motion deadline. The preceding countdown receipt delivered at GO is excluded.
STOP at the GO deadline suppresses GO; canceled countdown has no match samples.
Nonmembers neither count nor mark timing incomplete even with malformed timing.

B14 overrun stays strictly greater than1000us; R4 physical acceptance remains
strictly below800us and is not established by this consistency check. Existing
statistics/rate thresholds/saturation and B15 frame clamping remain unchanged.
Warning detail9 uses completion time for counted durations, current detection
(decision) time for invalid timing, and aggregates transitions exactly as before.
Receipt events remain before current decision events, including across wrap.
Frame maxima use the newly counted complete duration through existing pending
frame finalization, status/loss fields and AttemptRecorder ownership.

Duplicate decisions ignore changed timing, receipt and sensor input and cannot
recount or replace pending start. Reset clears selected mode/pending timing with
other Robot state while preserving token monotonicity and external recorder data.
New accepted START resets per-attempt statistics/incompleteness, not fixed timing
mode. Explicit IMU/QTR/button age and freshness remain anchored to post-acquisition
RobotInput.t_us. No clock or I/O enters core; caller supplies real timestamps.

## Implementation and independent validation

Bounded implementation in fsm.h/fsm_robot.cpp; no heap, new motor writes, tunables,
B16 changes or established test edits. Public header first; independent tests from
this contract/public headers rather than implementation bodies. Use a new timing
fixture, since old Rig/timedReceipt deliberately derive duration from decision.

Test acquisition600+later401=1001, equality/adjacent boundaries,799/800/801 and
999/1000/1001, natural wrap and half-range minus1/exact/plus1, stale/wrong tokens,
invalid duty versus timing-only faults, fixed-mode mismatch/recovery, duplicate,
reset, GO/finalSTOP/cancellation, event timestamps/order and frame maxima65535/
65536. Include explicit fresh/retained IMU evidence between start and decision,
and actual Robot->MotorGate(fake callbacks)->AttemptRecorder with real feedback
and final deferred sealing. Preserve every old locked/ordinary assertion.

Full host/sanitizer, actual target compile-only, exact-source review and fresh
separate reviewer are required. Tests/compilation prove software accounting,
not calibrated clocks, sensors, motors, scheduler resource fit or full800us WCET.
No upload/reset/run or human phase gate is required or implied by this task.
