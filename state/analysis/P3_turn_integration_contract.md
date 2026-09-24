# D125 isolated P3 3.4 turn-trial integration

D051/D122 permit this software task before physical acceptance. Integrate the
D124 helper through actual Robot, Runtime, Governor and MotorGate. No pin/source
grant, original B16 value, established locked test or motor-run approval changes.

## Immutable build and admission

`SUMOX_P3_TURN_TRIAL` defaults 0, accepts only 0/1, and rejects MATCH, B4 stand,
or P3 DRIVE_TEST simultaneously. The config-only `TURN_TRIAL_DEG` development
default is +90; exactly -180, -90, +90, +180 are allowed. No transport/menu angle
command is added. Build/source identity must accompany future trial evidence.
Default app and D123/B4 behavior remain unchanged; trial storage exists only in
this new profile. RobotResult exposes immutable TURN_TRIAL_PROFILE and, only in
profile1, `turn_trial`, `turn_trial_stopping`, `turn_trial_edge_interrupted`.

Use D123's local DRIVE_TEST service selection/release admission, availability
indicator and full actual countdown. Match modes/other services cannot start.
Existing RAW-to-CONTROL classified-line/neutral rearm, button/source freshness,
MODE cancellation, boot-held rejection and physical receipt boundaries apply.
Selection alone confers no motion authority. No opponent can select combat.

## One trial and termination

Actual runEscape precedes trial routing. Only a GO with permission and no escape
starts Trial with current match heading, unchanged real imu_ok, and config angle.
The heading reference resets at GO as before. Later distinct eligible observations
step the actual helper. State is DRIVE_TEST in TURN and BRAKE. Every request goes
through existing PIVOT Governor (including final electrical cap/slew) and the real
MotorGate. BRAKE requests zero immediately and may retain enable only while all
existing permission checks succeed. Full duty is never requested or authorized.

COMPLETE inhibits EN/PWM on its observation and sets turn_trial_stopping. The next
distinct tick feeds STOP into the existing Lifecycle. No automatic repeat, SEARCH,
opener, ATTACK, DEFEND, re-flank or stall execution occurs. FAULT/NOT_STARTED after
an expected GO faults SCRIPT_RESULT/SCRIPT_START respectively and immediately
inhibits; the following tick establishes Lifecycle STOP. TIMED_OUT remains a
distinct outcome, enters the same full observed brake interval, and emits one
FAULT event with detail=FaultCode::TURN_TIMEOUT and value=16 (new bench origin,
not a core fault).
No timeout is described as a successful accuracy measurement.

STOP/source/receipt faults win before routing and cancel an active helper using
its actual-time STOP sample. Edge preemption instead latches the owner edge flag
and cancels an active helper with EDGE, before executing the unchanged full B4
escape. Edge at GO does not start the helper: report remains NOT_STARTED and the
edge flag is true. Escape may move through its existing governed safe script;
trial motion never resumes. Successful escape exit immediately inhibits and
sets stopping, then Lifecycle STOP next distinct tick. All-white/recovery faults
inhibit under the unchanged escape-fault rules. Terminal reports are retained.

Report pulses clear on duplicate owner observations. Cancellation after a
same-timestamp helper observation may be deferred by the helper's duplicate
contract until the next distinct observation; immediate motor inhibition is
owned by Robot/Gate, never by a report pulse. Publication records current owner
stopping/edge flags; a late core/Governor fault latches stopping and makes a STOP
sample, preserving the helper's honest last-observed status if duplicate. Token
exhaustion also inhibits and performs bounded cancellation/publication. All old
receipt, source, clock and event-loss handling stays intact.

The existing D103 local post-STOP service gesture may reconstruct Robot for an
inhibited service-only session. Trial report then resets with Robot; retained
recording remains frame/event evidence but does not serialize the trial report.
Capture any needed trial report before this reset; no new wire fields are added.
Native MotorGate stays STOPPED, source projection
cannot start countdown, and DRIVE_TEST service remains explicitly unavailable.
Only an actual new physical setup/run authorization could permit another run.

## Staging and checks

`bench/turn_accuracy/turn_accuracy.ino` uses real NativeSources/UnoQPort/Runtime
and empty SetupGrants, with profile1/MATCH0/M0 static assertions. Checked tooling
admits only default-startup compile-only and exact C/C++ flags
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_TURN_TRIAL=1`; no upload key or MCU action.
This wrapper cannot energize motors even on an assumed connected board.

Independent public-header/spec .cc tests freeze before first execution: selected
local admission/full hold/wrap, all signed config angles via isolated source
overlays, DONE/tolerance/overshoot/timeout/fallback, full brake duration and final
inhibition/STOP, all128 opponent masks/no combat, edge before GO/during TURN/BRAKE,
escape completion and persistent faults, physical Gate writes M0/M1, real applied
receipt FIRST_NONZERO, source/receipt failures, duplicate pulses and permanent
post-STOP service-only inhibition. New locked R1/R5 checks, old36 byte identities,
normal/sanitizers/full regression, tooling refusal cases, target compile/loader
accounting when connected and a separate reviewer precede software completion.
No simulated test establishes measured accuracy, fallback timing, settling or WCET.
