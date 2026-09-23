# D104 actual Runtime on the bare UNO Q, without peripheral I/O

2026-09-23, selected under D051/D075 and the user's fresh confirmation that the
UNO Q alone is connected and may be tested. Follows D103 implementation1b1d77d.
Read P2_runtime_inert_options.md. This authorizes preparing one reviewed inert
probe, not loading the normal app, granting sensors/pins or running motors.

## Probe behavior

Create bench/runtime_inert with one actual app::Runtime, an independently tested
checked inert motors::Port and empty Source/ADC/Dump ports. All SetupGrants are
false, including local reset. No native motor or source owner is constructed.
MATCH and MOTORS_ALLOWED must both be0 at compile time. Core/config/Runtime and
existing benches remain unchanged. Unit periods are1 inert integer unit, never
a claim about physical PWM frequency. No GPIO/PWM/ADC/I2C/UART/Bridge operation,
remote command, heap, delay or second Robot/recorder occurs.

The pure public bench Runner owns this fixed lifetime. begin is one-shot; a
second begin fails permanently (unless already terminal, where no callbacks
occur). poll calls Runtime::step at most once; Runtime owns its original grid,
early-call admission and actual S/D/application/C clocks. Every clock observation
is real from the supplied callback; firmware supplies micros. No catch-up loop
or artificial sensor/time advancement. Terminal calls are fully passive.

Probe phases are NOT_STARTED/RUNNING/FROZEN/FAILED, distinct from RuntimePhase.
Run for LOG_FRAME_WINDOW_MS (200s) of actual MCU clock from begin. Require at
least ceil(window_us/TICK_US) completed epochs, zero missed releases and valid
chronology. Freeze success only after an actual completed epoch at/after the
window; retain its genuine Runtime RUNNING/Robot BOOT/recorder EMPTY state.
Do not call abort, invent STOP or reset an owner to freeze RAM. Failure also
freezes the actual observed state, with the first probe failure retained.

Bounded failure guards reuse existing constants: no first completed epoch by
BTN_LONG_MS; no successful finish by window+BTN_LONG_MS; at most
APP_CLOCK_STALL_MAX_POLLS consecutive equal supplied clock observations;
backward/half-range chronology fails. A first observed missed release or failed
receipt/invariant ends this exact zero-miss experiment; it is not silently ignored.
Counters saturate and saturation makes the experiment FAILED, never a wrapped
success. No new tunable or production threshold is introduced.

InertMotorPort validates one EN setup and each of four PWM setup channels,
acknowledges only disabled EN/zero PWM with period1, and validates settle after
complete setup. Count attempts; reject/latch enabled, nonzero, invalid channel,
wrong period or invalid setup order. After a latched port failure, callbacks
cannot fabricate successful receipts. It never calls a native I/O function.
Expose its fixed Port and immutable Counters for independent direct boundary
tests; the Runner's Runtime is exposed const-only. Missing clock fails before
setup. Clock observations are counted and chronological checks remain explicit.

For each completed epoch, verify the actual finished/timing-valid Transaction,
fresh strictly increasing nonzero token, matching consumed valid Gate receipt,
S<=D<=application<=C in half-range arithmetic, current BOOT, no Robot/Gate/
Runtime/Transaction fault, no release/GO/motion, intended and applied zero duties
and disabled motors. Source grants remain false: explicit line RAW/CALIBRATION
ABSENT, explicit IMU gyro/accel ABSENT, explicit buttons ABSENT, battery invalid,
opponents not fresh, initialization false. Recorder stays EMPTY with zero frames,
events and epoch; no accepted attempt is manufactured. Every guard is checked
against real public owner reports, not an independently advanced model.

The48-word Report records the first/last real epoch, last applied time/token,
actual elapsed, epoch/miss counts, maximum Runtime S..C and separately maximum
bracketed Runner poll duration, exact faults/receipt/input states and callback
counts. Runner duration includes its actual checks/report preparation but excludes
the final duration assignment and native diagnostic publication. Never label it
full-app WCET. Receipt flags: bit0 consumed, bit1 applied_valid, bit2 inhibited
intended, bit3 inhibited applied (successful value15). Input-absence mask: bit0
RAW absent line, bit1 canonical absent IMU, bit2 canonical absent buttons, bit3
invalid battery, bit4 unavailable opponents (successful value31). Six reserved
words remain zero. Public report ABI is192B, explicit uint32 words, no pointers.

Native wrapper reuses the reviewed D091 current-thread metadata/PSP method with
exact ABI assertions and no stack painting. StackSample is32B; diagnostic is232B:
front sequence, Report, StackSample, tail sequence. Publish initial RUNNING and
one final immutable diagnostic using barriers and matching nonzero even sequence;
do not publish every loop. Sample stack only at real clock callbacks; label the
minimum observed value sampled_headroom_bytes, not a watermark or D103 reset
stack measurement. Invalid stack metadata remains an explicit diagnostic failure.

## Checked build and upload boundary

Extend D100 checked native-build policy only to exact bench/runtime_inert and
runtime_inert.ino: pinned tool/core/effective recipes, fixed no-library discovery,
source and artifacts must retain all previous checks. Bind the project filename
explicitly; never accept arbitrary filename or recipe substitutions. App defaults
and all other benches keep their existing behavior. Probe accepts only flags0
and default startup; reject MATCH/Immediate (including compile requests) before
target/transport calls. Reject sketch profiles/overrides as for the app.

Compile-only remains strictly upload/reset-free. Add no upload authorization key
until independent source/ELF/constructor/import/loader review passes. Then add
only the new inert key/default-only route; app and motor upload guards stay closed.
New guard tests use controlled transport, and preserve all established tests.

## Capture and physical acceptance

Prepare separate tools/runtime_capture.py and independent pure decoder tests.
Do not repin or weaken D091 recorder_capture.py. Pin exact reviewed ELF/ZSK/
loader/tool/config identity and runtimeDiagnostics offset/232B ABI. No arbitrary
address, size, command, artifact or output escape. Compare deployed flash bytes
before private RAM, require two identical terminal diagnostics and unchanged
heap descriptor, decode two pinned heap snapshots and compare metadata only.
Keep <=48 reads, <=2MiB total, <=16KiB RAM read, <=64commands, <=600s overall,
<=30s/command. Calculate read budget from actual package before running; no
automatic widening. MEM-AP only, no Cortex attach/halt/reset/write/background
daemon in capture. Existing old helpers and exact evidence remain unchanged.

Before upload create a run record binding bare serial2629958581, source/commit,
reviewed ELF/ZSK and scope to the user's current authorization. Upload via the
reviewed guard, then wait in short intervals while continuing evidence work.
Assess explicit FROZEN/NONE, valid stack sample, exact epoch/source/zero-write
invariants and deployment identity. A capture may succeed while experiment
acceptance fails; preserve both statuses, diagnose without inventing success.

Host tests cover actual Runtime lifetime, setup order/active/invalid-port refusal,
natural wrap/equality/regression/stall/deadline, absent inputs, first/last clocks,
miss/failure retention, terminal passivity, saturation bounds where reachable,
fixed ABI and malformed capture. Independent review must inspect final source,
actual target and capture commands before upload/read. This probe cannot prove
the different full-app ELF load, native sensors/UART, D103 active reset, historical
stack peak, calibrated clock, five-minute full800us, motor behavior or any gate.

## Boundary and tooling API clarification before independent test freeze

Before starting a new Runtime step, elapsed>=BTN_LONG_MS with no prior completed
epoch fails the first-epoch guard. Elapsed>=window+BTN_LONG_MS without an earlier
frozen success fails the overall guard. A completed epoch may qualify success
at C>=window if all invariants/counts pass and C is strictly before the overall
deadline. The first clock sample establishes a baseline; exactly
APP_CLOCK_STALL_MAX_POLLS consecutive equal deltas fails.

Checked policy public validators retain all old call forms. Optional project
selection defaults to app.ino and accepts only app.ino or runtime_inert.ino;
the latter additionally requires flags0/default FQBN. Every effective-command
template and artifact name is bound to that selected literal project. Unknown
names, mixed app/probe filenames, flags/startup mismatches and injected strings
fail. The probe upload must use the exact output directory returned by its
successful checked compile, never the old unverified generic bench directory.

Runner duration ends at its actual closing clock sample. Substantive invariant
checks/report preparation precede that sample; validation/bookkeeping of the
endpoint (clock count, elapsed and maximum assignment) necessarily follows and
is excluded, as is native publication. No recursively self-inclusive timing claim.

On FAILED, last_* and owner status preserve the latest actual Transaction, which
may be partial; epochs counts completed epochs separately. Only FROZEN success
asserts the complete final chronology. Native stack.valid0/faultN independently
fails physical acceptance even if the pure Runner reached FROZEN. Stack metadata
has no input into Runner: do not invent a clock fault or abort to conflate them.
The diagnostic gate_fault uses the current actual halt.fault when halt.fresh;
otherwise it uses applied.fault. An older application receipt must not hide a
later real terminal halt fault. Setup refusal is still the actual Transaction
SETUP fault; do not invent a native status that its public report does not expose.

The closing clock sample must also remain strictly before the overall deadline,
even when the completed C had qualified for success. A late endpoint produces
FAILED/DEADLINE, preserving the genuine C and first failure. D104-R1 verifies
the exact deadline and keeps the original failed regression receipt.
