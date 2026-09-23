# D101 actual Runtime dump attachment

2026-09-23 selected under D051/D075 after D099/D100 acceptance f5f8f34. This is
the existing P2 B8/app integration task, not a new protocol or remote control.
No configuration value, native pin, recorder capacity, startup or motor authority
changes. Native UART ownership/framing grants stay absent unless explicitly supplied.

## Public interface and ownership

Add app::DumpPort in src/app/dump_port.h with context, setup begin callback,
readiness callback and existing recorder::dump::Port output. begin receives the
existing recorder::dump::SetupGrant and returns NativeStatus; ready returns bool.
app::unoQDumpPort(UnoQDumpPort&) creates direct bindings without hardware I/O.
Runtime accepts optional fourth constructor argument const DumpPort& = {}.
SetupGrants adds dump_enabled=false, dump grant and dump_origin=UNKNOWN.
RuntimeReport adds dump_setup=NOT_INITIALIZED and dump Report. Runtime owns one
Transfer by value; the native app owns one fixed UnoQDumpPort and supplies its
factory. app.ino retains completely unconfirmed SetupGrants{}.

Disabled dump performs no begin/ready/write/cancel callbacks and leaves existing
Runtime behavior unchanged. Enabled setup calls begin exactly once during setup,
after MotorGate and existing source initialization, with the exact supplied grant.
Missing begin/ready/output.write/output.cancel produces CONTEXT without calling
any dump callback. Failed setup is reported; it does not halt sensor/control work,
retry, reconstruct the native owner, wait for Linux or imply transport readiness.
Only NativeStatus::OK permits readiness sampling. No setup operation occurs in step.

## Actual transaction boundary

Within each due epoch, preserve actual sources -> Robot -> MotorGate -> recorder,
then existing calibration/display and dump service before final C. Feed the exact
Transaction RobotResult/decision_us and retained AttemptRecorder to Transfer.
Never fabricate a token, result, timestamp, origin claim, source or local intent.
Transfer remains the sole eligibility/source/serialization/CRC owner under D090.

Service reads the current clock before and after readiness and after Transfer.
The after-ready observation is Context.now_us; the original actual D is retained.
The work, callbacks, formatting, writes and cancellation belong inside actual S..C.
No between-tick pump, hidden second decision, unbounded loop or unmeasured service
side loop. Early calls and terminal STOP/FAULT retain existing passivity.

Readiness callback runs only after successful dump setup and a current fresh,
nonzero-token IDLE result with gate IDLE, zero duties/disabled outputs and a valid
actual consumed MotorGate receipt for that same token/decision with zero applied
duties and disabled enable. Other context goes directly to Transfer with false
readiness; Transfer's fuller D090 eligibility checks still apply. A current failed
motor receipt must cancel active transport immediately without sampling readiness
or offering further bytes; no source read or forged next Robot tick is needed.
Do not infer actual inhibition solely from core output intention.

Transfer receives every actual result while dump is enabled, including START,
COUNTDOWN, STOP and faults that invalidate IDLE authority. A genuine fresh LOG_DUMP
request on a retained SEALED/INTERRUPTED attempt remains required. Setup/readiness
failure or no evidence is reported through existing refusal semantics. Sent means
SENT_UNCONFIRMED, never a fabricated Linux capture. Exact source/loss fields remain.

## Terminal cancellation

Add Transfer::abort(): if ACTIVE, cancel once with existing Reason::CONTEXT;
otherwise remain passive and preserve its report. It neither resets identity/
clock history nor performs a Robot reset. This explicit owner-abort API avoids
mislabeling an app fault as a reset. Existing onRobotReset behavior is unchanged.

Runtime terminal failure first preserves/executes Transaction motor inhibition,
then aborts active Transfer before native sensor cleanup. Refresh dump report.
A bad clock after readiness/write follows this path. If the epoch cannot close,
retain interruption evidence instead of inventing a successful duration. Repeated
abort/terminal step does no new I/O. Normal STOP is delivered to Transfer before
the existing real tail and passive STOP; no active transport survives that boundary.
Native cancellation poison remains permanent; no lazy reinitialization/recovery.

## Verification and remaining project work

Independent tests derive from this contract and public headers before implementation.
Compose actual Runtime/Transaction/Robot/MotorGate/recorder with scripted source
and dump boundaries in both motor configurations. Cover disabled/invalid/setup-
failed ports, setup ordering, real menu intent, successful sealed countdown-cancel
attempt dump and receiver roundtrip, malformed/failed writes, readiness loss,
START/STOP preemption, actual inhibition failure, stale context, wrap/time reversal,
clock faults after I/O, cancellation exactly once and complete callback timing.
Retain existing tests unchanged; no locked-test amendment is authorized.

Native factory uses the existing D090 adapter; source and target binding checks
must prove one owner/no I/O in factory and startup safety. Run appropriate full
host suites, final-source inert/MATCH compile-only memory/dependency checks and
separate fresh-context review. A prior binary does not prove this larger app fits.

This attachment does not add post-STOP local reset/rearm. Its positive completed
attempt can use existing countdown cancellation -> real tail -> IDLE. Local
postmatch service reset/source lifetime is the next explicit task, followed by
calibration snippet delivery under a separately defined transport contract.
Do not claim full B8/physical UART, measured loadedRAM/800us or any human gate.
