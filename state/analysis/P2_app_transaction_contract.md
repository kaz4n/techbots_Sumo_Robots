# D095 actual application transaction ownership and terminal inhibition

2026-09-23 Asia/Dubai, baseline1b5bc3a. Previous goal turn PROGRESS: D094 actual
resumable source implementation fab551f with real tests/compile/review. D051/D075
select this necessary P2 app boundary. Read P2_app_transaction_spec_audit.md and
P2_app_schedule_dependencies.md. This is a concrete control/recording owner, not
a claim that native source scheduling or physical800us acceptance is complete.

## Scope and invariants

One fixed app::Transaction owns the actual Robot, MotorGate and AttemptRecorder.
The native port outlives it. Its copied MotorGate port clock is the same micros
domain used by all future source owners. No constructor/destructor I/O, heap,
strategy, background task or remote command. All later sensor/output work belongs
between open and finish; this boundary cannot certify work the caller performs
outside it. The actual native scheduler must exclusively use this owner later.

Do not change B14: duration>1000us is counted/logged by Robot, and physical<800us
remains an acceptance requirement. Neither800 nor1000 alone causes halt/STOP in
this change. Invalid clock/order/identity is different: ordinary one-token motion
cannot safely continue. A new MotorGate halt terminates output without inventing
a Robot command or clearing faults. R1-R11, existing governor/hold/edge logic,
source admission, recorder membership and every established assertion remain.

## MotorGate::halt

HaltResult is separate from Result/PreviousTick: fresh invocation pulse, attempted,
inhibition_confirmed, timing_valid, started_us, completed_us and actual Fault.
It never carries a token, source observation or valid application receipt.

First halt latches halted state and disarms the gate. If begin has never been
attempted, perform no clock/backend I/O; set NOT_INITIALIZED only when no earlier
fault exists. Return fresh=true, attempted=false, unconfirmed/invalid timing.
No later begin implicitly clears this fault. If begin was attempted (including a
failed setup), execute exactly one existing inhibit pass: EN LOW first, attempt
zero on every writable PWM channel despite an earlier failure, then settle once.
Do not configure, enable HIGH, retry, synthesize a command or renew a hold.

If no earlier fault exists, select STOPPED before inhibition. Preserve an earlier
cause except the existing inhibit IO upgrade. Capture clock immediately before
and after that pass when present. timing_valid requires both readings and a
forward unsigned interval<2^31; equal time and natural wrap are valid. Invalid
clock metadata never prevents the physical inhibit attempt or invents its timing.
inhibition_confirmed means callbacks acknowledged LOW/zero/settle only, not pin
or wheel measurements. Keep the first completed diagnostic report internally.
Later halt returns that report with fresh=false and no clock/backend I/O.

Subsequent apply obeys its existing fault/STOPPED rules and can never enable motors
until an explicit successful existing reset. A successful reset clears the added
halt cache along with the existing gate state; a failed reset keeps it. This does
not authorize application reset gestures, native fault recovery or hardware runs.
All old begin/apply/reset results and callback order stay unchanged for callers
that do not invoke halt.

## Transaction lifecycle

Public header freezes before implementation. Phase: NOT_INITIALIZED, IDLE,
ACQUIRING, DECIDED, FAULT. Fault: NONE, SETUP, ORDER, CLOCK, IDENTITY, RECEIPT,
ABORTED. Reports are passive retained diagnostics, not action pulses; method
success is the single operation acknowledgement. No public reset or mutable
Robot/Gate/recorder access. recording()/previous()/report() do no work.

initialize performs MotorGate.begin exactly once, as the first native operation.
Success selects IDLE; failure selects terminal SETUP without an extra inhibit
attempt (begin already handles its own cleanup). Repeated initialize returns true
while initialized/nonfaulted and false after fault; no state/clock/backend change.

open requires IDLE. Before initialization or in another nonfault phase, fail ORDER.
Terminal calls are passive false. Capture actual S with the copied port clock;
validate forward half-range from every prior accepted owner clock, equality valid.
The first sample has no prior chronology requirement. Reset only the current
cycle report, preserving the previous actual receipt and the owned objects.
Select ACQUIRING. Acquisition/services happen after S, never at invented release
timestamps. This owner is not the release-rate scheduler and never catches up.

decide requires ACQUIRING. Capture D after source work; require forward chronology,
D-S<2^31 and D different from the previous actual admitted Robot decision. A frozen
duplicate decision is CLOCK; do not invoke Robot or Gate.apply in that case.
Override caller t_us, timing={true,true,S}, previous with the owner's exact last
closed receipt. All source/initialization/local-stop/reset-cause fields otherwise
pass to actual Robot unchanged; it remains their validation/strategy authority.
Call Robot.step once; require fresh and nonzero strictly increasing token, otherwise
IDENTITY fault. Call MotorGate.apply once with that exact D/result; require consumed
and returned feedback token equal to that result, otherwise IDENTITY fault.

Ordinary Gate faults are retained in applied; they already inhibit through the
existing boundary and do not justify fabricating acknowledged output. An invalid
application receipt goes to the next real Robot tick unchanged. Ordinary recorder
rejection/loss remains evidence and does not change motion. Call recorder.consume
once after Gate, preserve its status, mark decision_made and select DECIDED.
Caller may now apply accepted bias to future estimator increments, calibrate, or
perform other explicitly admitted jobs. All such work still belongs to this S..C.

finish requires DECIDED. Capture actual C after that work; validate clock and one
common S anchor:0<=D-S<=A-S<=C-S<2^31, where A is Gate's actual feedback timestamp.
Check A even if applied_valid=false: a failed Gate call still has an actual return
clock, not a fabricated time. Invalid A chronology is RECEIPT; no duration is
declared valid. For ordered C, retain actual execution=C-S, timing_valid=true,
finished=true, and copy Gate feedback into previous with duration_valid=true,
completed_us=C and execution_us. Do not turn false applied_valid into true.
Select IDLE. A later open additionally checks C<=nextS; a later decide supplies
that actual nextS/D to Robot's existing D092 receipt validator.

The final stopped tick still needs a later real opened/decided/finished epoch so
Robot emits its deferred final frame/timing and AttemptRecorder seals naturally.
This tail consumes actual time, inputs and an inhibited Gate transaction; never
forge it by incrementing timestamps or reusing an old result. No automatic
software reset, evidence erasure or dump is performed by this owner.

## Terminal ownership failure

Wrong phase, invalid clock, invalid identity/receipt or explicit abort selects the
first app fault and FAULT permanently. Halt the actual MotorGate exactly once and
retain its report. Never use Gate.reset or duplicate-token apply as inhibition.
If a current/previous ordinary receipt may describe an output changed by halt,
invalidate applied_valid and duration_valid in saved previous and current applied
feedback. Do not rewrite its token/application time/duty to a fictional disabled
application. Preserve any already verified cycle diagnostics; no later call may
manufacture a valid completion after fault. Halt owns its own diagnostic bracket.

Notify recorder.onRobotReset once as the existing end-of-stream interruption
operation; this preserves frames/events and marks any active/draining attempt
INTERRUPTED. It does not call Robot.reset, erase storage or claim SEALED. If no
attempt is active, retain the existing recorder semantics. No synthetic next tick
is created when a clock cannot support one. Subsequent owner methods return
false/passive cached evidence, with no clock/backend/Robot/recorder invocation.

Native source cancellation remains the future scheduler's responsibility. Its
IMU/QTR cleanup must be inside an accounted epoch or an explicitly invalidated
interruption, never a fabricated successful complete tick. This task does not
claim active source owners can resume after their terminal cancellation.

## Staging and verification

Place transaction.h/.cpp in src/app. Required app support sources must be staged
under build/stage/<sketch>/src/app for both app and retained-method bench builds;
the .ino stays at staging root. Exclude app.ino from shared support. Reserve the
sketch-local src/app name against shadowing, and preserve exact error propagation.
Established source behavior and controlled tooling assertions remain unchanged;
new tests cover app support/header include paths and shadow refusal.

Independently author tests from public headers/contracts: no-I/O construction,
halt every fault position/clock boundary/repeat/reset, both motor macros, R1 hold,
all transaction phases and failure priorities, exact S/D/A/C/nextS wrap/half-range,
caller forged receipts/timing ignored, genuine enabled Gate path, source-age after
acquisition, actual200s simulated recorder lifecycle, GO/finalSTOP/tail, malformed
clock/receipt interruption, no catch-up/duplicate application, no allocation and
799/800/1000/1001 durations retaining B14. Existing locked tests stay unchanged.
Full normal/sanitizer, relevant native/tool regressions, exact inert target
compile-only source/ELF startup inspection and fresh independent review required.
No upload key, physical measurement, new config value, motor authority or gate.
