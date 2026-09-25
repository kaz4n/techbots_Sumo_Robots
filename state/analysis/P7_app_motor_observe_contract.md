# D192 longer inhibited full-application observation

26 September 2026. Host software scope under D051. D190 completed four epochs
without reproducing D160/D161. This scope extends observation duration without
changing the existing diagnostic, native callback behavior or safety limits.

## Public interface and ownership

New bench/app_motor_observe has app_motor_observe.ino and src/app_motor_observe.h/.cpp.
Namespace app_motor_observe exposes Phase {NOT_STARTED, DISABLED, RUNNING,
FINALIZING, FROZEN} and Reason {NONE, SETUP_FAILED, CALLBACK_FAILURE, TRACE_INVALID,
APPLICATION_INVALID, RUNTIME_TERMINAL, EPOCH_LIMIT, POLL_LIMIT}, in that order.
Snapshot holds app::RuntimeReport runtime, app::TransactionReport transaction,
fsm::PreviousTick previous. Report defaults to NOT_STARTED/NONE and false flags:
begin_called, begin_finished, begin_ok, before_abort_valid, abort_called,
abort_returned, last_step_returned; uint32_t polls defaults0, plus Snapshot before_abort.

Runner has the same constructor and public methods as app_motor_fault::Runner:
Runner(const motors::Port&, const power::InputPort&, const app::SourcePort&,
const app::DumpPort& = {}); noncopyable; bool begin(const motor_fault::Grants&),
void poll(), bool active() const, const Report& report() const,
const motor_fault::TraceReport& trace() const, const app::Runtime& runtime() const.
It owns one unchanged motor_fault::Trace and one unchanged app::Runtime, passing
trace.port() to that Runtime. It must not use the short four-epoch Runner,
reset/reconstruct objects, duplicate callback forwarding or allocate dynamically.
Constructor/accessors do no I/O. Existing diagnostic/native sources stay unchanged.

Add only two development count bounds in src/config.h:
APP_MOTOR_OBSERVE_EPOCHS=10000U and APP_MOTOR_OBSERVE_MAX_POLLS=10000000U.
These count names are explicit R9 unit-suffix exceptions, like existing poll
bounds. Require both positive and <=10000000U and polls>=epochs with static_assert
in the new public header. They do not change any old config value. Ten thousand
epochs are roughly ten nominal seconds at1kHz, not an elapsed-time measurement.
No callback timeout/preemption, electrical acceptance or WCET is claimed.

## Lifecycle and retained evidence

Admission, empty app::SetupGrants{}, real Runtime::step ownership, port wiring,
single begin, inactive passivity, pre-abort copies and finalization ordering are
identical to D186's public contract. A denied first begin returns true/DISABLED
without native callbacks; subsequent begins return false/passive. Granted begin
sets RUNNING and begin_called before runtime.begin, records its exact result and
begin_finished, and freezes SETUP_FAILED if false. A successful begin checks the
ordered stop rules below. All peripheral/service grants remain empty.

Every active poll increments report.polls exactly once before setting Trace
APPLY context to prospective runtime.epochs+1 and calling runtime.step once.
Retain that return bool in last_step_returned. Do not synthesize epochs, advance
time, run catch-up applications or query a separate clock. Runtime owns release,
skip, wrap, reversal/stalled-clock and STOP-tail semantics.

After successful begin or each active poll, select first applicable reason:
1. trace.has_failure -> CALLBACK_FAILURE.
2. trace.timing_fault -> TRACE_INVALID.
3. If transaction.decision_made: require applied.consumed, feedback.applied_valid,
   feedback.token==robot.token, motors_enabled=false and both duties exactly0;
   otherwise APPLICATION_INVALID.
4. Runtime phase FAULT or STOPPED -> RUNTIME_TERMINAL.
5. Runtime epochs>=config::APP_MOTOR_OBSERVE_EPOCHS -> EPOCH_LIMIT.
6. report.polls>=config::APP_MOTOR_OBSERVE_MAX_POLLS -> POLL_LIMIT.

Unlike D186, overflow alone is expected prefix truncation and is not a stop
reason. Keep Trace and all its fields unchanged: count<=64 describes retained
prefix calls; rejected counts subsequent calls not stored in calls[] and
saturates by the original rule; overflow explicitly signals truncation. Current,
first_failure, timing_fault and clock_reads keep their original behavior.
Never relabel rejected calls as native rejections, conceal loss, or claim the
prefix contains every application. A failure after the prefix still freezes.

Freeze enters FINALIZING, saves the initiating reason and complete copies of the
three reports before diagnostic abort, sets before_abort_valid, selects HALT
context with current epochs, then sets abort_called before runtime.abort once.
Only after return set abort_returned and FROZEN. The chosen reason/pre-abort state
survive cleanup failures; such failures remain visible in Trace first_failure.
EPOCH_LIMIT/FROZEN alone is not a success verdict if final halt/abort failed.
The snapshot precedes this diagnostic's abort; Runtime may already have performed
its own failure cleanup, which must not be relabeled as an untouched prior state.
FINALIZING/FROZEN/DISABLED/NOT_STARTED polls and repeated begins perform no I/O.
At the exact epoch/poll tie, EPOCH_LIMIT wins; any real failure wins over bounds.
No active poll beyond the bound is allowed. Bounds cover returned polls, not a
native callback that blocks inside its existing implementation.

## Sketch and staging

Use main-app NativeSources/UnoQPort/FIFO8 UnoQDumpPort wiring and EMPTY macro
protection, matching D186. Only SUMOX_MOTOR_FAULT_PROBE==1 admits setup; its default
remains0. loop polls only while active. Existing Trace enforces MATCH0/MOTORS0.

Extend only the existing exact-name checks in tools/board_tool.py for this new
sketch: fresh attempt required; plain ancestry/source checks; exact canonical
motor_fault.h/.cpp copied with collision/missing/link refusal; generic flash
route rejected before transport or staging for all flags. Preserve every D186
guard and all other routes. Do not register a dynamic build/upload profile.
This host scope authorizes no native compile, upload, reset or capture. Those
require later fixed static artifact/source/identity bindings and new owners.

## Independent validation

Tests derive from this contract and public headers, not new implementation
bodies. Freeze before execution; preserve initial failures and established tests.
Use actual Runtime/Transaction/Robot/MotorGate with controlled callbacks/clocks.
Cover 10000 successful epochs with exact60017 callbacks after final halt:
64 retained,59953 rejected, overflowtrue, no failure/timing fault. Validate the
unchanged first64 prefix and latest call, four-epoch continuation, absent source
grants, receipt/pre-abort/abort ordering and passive terminal/repeated paths.
Inject failures before/after64 and on each native application operation beyond
the prefix, plus final cleanup failure and simultaneous bounds/failure priority.
Exercise clock reversal/wrap/stall, early polls, skipped releases, finite poll
limit under an advancing clock that stays before release, and missing callbacks.
Unsafe flags/probe values and invalid bounds must fail compilation. Verify new
sketch wiring/admission with controlled headers and new staging/refusal behavior.
Run focused normal and ASan/UBSan host builds serially in owned RAM, unchanged
D186 runtime/staging tests and relevant locked safety tests. No broad reruns are
needed without a changed dependency or failure.

Actual target layout, loadability, sustained runtime, first-fault reproduction,
RAM/stack/WCET, sensor/motor acceptance and human phase gates remain unproved.
