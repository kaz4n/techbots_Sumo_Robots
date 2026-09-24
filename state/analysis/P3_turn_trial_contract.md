# D124 finite P3 3.4 turn trial

This pure request helper prepares one isolated P3 turn-accuracy trial. It adds no
motor authority, Robot routing, native wrapper, upload route or physical evidence.
The owner must establish actual GO and apply every request through PIVOT Governor
and MotorGate. Actual integration is a following task; D123 SEARCH stays intact.

`turn_trial::Trial` accepts one start attempt in its lifetime. Exactly four signed
angles are accepted: -180, -90, +90, +180 degrees. Reject nonfinite initial yaw or
any other angle, consuming the first attempt into FAULT/INVALID_START, zero output.
Repeated start is passive false, including retained report and pulses. On a valid
start capture raw time/signed angle and start the actual motion::Turn at TURN_DUTY.
Start computes the initial request and publishes TURN/fresh/phase_changed.

RIGHT trials use actual yaw and positive target. LEFT trials negate actual yaw
and use the same positive target, then swap left/right wheel requests. This is an
explicit coordinate reflection, not a fabricated IMU observation. Real imu_ok is
passed unchanged. In particular +180 RIGHT in that reflected frame is physical
LEFT180. Default Turn API, exact tie, tolerance, timeout and fallback stay unchanged;
no 179.999 substitute and no extra field/code in the existing Turn are needed.

Step receives caller time, actual yaw, actual imu_ok, edge_required and local STOP.
NOT_STARTED, terminal and duplicate timestamp calls do no work except clearing
fresh/phase_changed. For active distinct calls: a delta>=2^31 faults CLOCK_ORDER;
otherwise STOP wins EDGE, both permanently interrupt before any motion step.
Successive valid calls must be less than half a micros wrap apart. An ordinary
forward delayed call advances the existing Turn once; it never skips a brake
phase or invents historical completion time. All calls use bounded work.

TURN uses the actual primitive. Healthy nonfinite yaw gives FAULT/INVALID_HEADING
and zero. Invalid heading is ignored while unavailable exactly as Turn specifies.
Mirror actual duties back for LEFT; preserve the primitive status and fallback
flag. DONE or TIMED_OUT enters BRAKE at that actual observation, marks
turn_finished=true and turn_finished_us, zero requests. TIMED_OUT is not success.

BRAKE remains zero for the full TURN_TRIAL_BRAKE_MS=500 development interval from
its observed entry; this is a requested brake observation period, not measured
physical settling. STOP/edge/clock still preempt. Heading is not consumed during
BRAKE. At elapsed>=500000us publish COMPLETE, zero, finished=true/finished_us.
COMPLETE retains the primitive DONE/TIMED_OUT distinction. Terminal calls cannot
resume. An interruption/fault records finished time on that actual observation.
Invalid initial start records its attempted time as finished, but no accepted
angle/start fields or valid turn completion. All report duty/angle fields stay finite.

`turn_finished` distinguishes an actual terminal primitive observation even at
timestamp0; `finished` similarly distinguishes trial termination. Ordinary initial
and active TURN have neither. BRAKE has only turn_finished. Fresh/phase_changed
are action pulses, not motor permission. Pure helper BRAKE itself writes no EN.

No existing test or B16 default changes. Add one new config value and literal
unlocked registry expectation. Independent public-header/spec tests freeze before
implementation execution: all signed angles/ties, L/R reflection, strict tolerance
and adjacent floats, overshoot, wrapped/large finite yaw, actual fallback/loss/
recovery, timeout priority, full observed brake interval, clock wrap/order, STOP/
edge priority, duplicates, invalid starts, terminal passivity and finite bounds.
Run focused normal/sanitizer tests, unchanged host regression and separate review.
Target/actual Runtime integration and ring acceptance remain separate unfinished work.
