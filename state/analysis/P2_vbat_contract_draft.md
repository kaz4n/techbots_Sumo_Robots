# D110 draft: finite battery-voltage capture bench

Proposal pending coordinator review/adoption. Implements software preparation
for P2 B5's missing `bench/vbat`; no physical accuracy, wiring, timing, upload or
phase approval follows. Sources: `P2_vbat_design.md`, D078/D086/D093 contracts,
`src/hal/power.h`, `power.cpp:423` and `src/config.h:38-50`. P2 B5 still requires
actual error within0.05V against a multimeter over9.5..12.6V.

## Fixed ownership and public surface

Own exactly one existing `power::Reader`; Native forwards only begin() and
read(), with micros() as the shared clock domain. Do not use InputOwner or
readerInputPort(), whose setup selects the A0/A1 pair. No beginWithButtons,
readButtons, arbitrary ADC channel, Robot, Runtime, MotorGate, QTR, IMU, matrix,
UART/Bridge, transport, reset or stop API. Construction/destruction/port creation
are passive. The sketch asserts MATCH=0/MOTORS_ALLOWED=0 and begins with Grants{}.

Draft public headers are `P2_vbat_headers/vbat.h` and `vbat_native.h`, to be moved
to bench/vbat/src only after adoption. The coordinator adds a uint32 count
`config::VBAT_BENCH_SAMPLES=128`; this is separate from QTR's capacity. Existing
ADC values/pins remain unchanged. Store the first configured number of accepted
Capture records, without overwrite, ring behavior, allocation, filtering,
rounding or clipping. A zero-capacity profile may have one inaccessible storage
placeholder solely for valid C++ array syntax; effective capacity remains zero.
Private implementation storage/helpers may be added after the public freeze.

captureCapacity() always returns the configured count; captureCount() equals
Report.captured_samples. capture(i) returns a const pointer iff i<count, otherwise
nullptr. A published record remains unchanged for the Runner's lifetime, including
after fault. All accessors are passive. No sequence is invented for power::Sample;
the array index identifies a retained record, not an ADC hardware generation.

## Begin and configuration

Begin is one attempt. Repeat begin returns false without changing any field or
calling anything. False exclusive_adc takes precedence over all checks and
returns true/DISABLED without callback, including clock. Enabled begin checks all
three callbacks, then configuration, before any callback. Null context is valid
for a stateless port. Missing callback is PORT. Invalid config is CONFIG.

Wrapper config requires positive capacity, 0<VBAT_ADC_CONVERSION_US<=
VBAT_SAMPLE_PERIOD_US<2^31, finite reference in(2.4,3.6], and finite divider>=1.
These are the used D078/D093 limits; the bench does not retain a current battery
value and therefore does not add VBAT_SAMPLE_MAX_AGE_US as a dependency. Other
native setup/ownership checks remain the Reader's responsibility. Invalid zero
period/capacity profiles must still compile under strict C++17 warnings; an
explicit compile-time guard must exclude division by zero, not substitute a
different period. No arithmetic or native bound is asserted to prove WCET.

Enabled begin observes S, invokes beginBattery exactly once, observes A
immediately after return, validates, then observes C. Save the complete actual
InitResult. Only known statusOK, ready=true, shutdownNOT_ATTEMPTED can succeed.
Unknown status or shutdown is CONTRACT. Any known non-OK status is SETUP,
including ALREADY_STARTED even if ready=true. OK with contradictory ready or
shutdown is CONTRACT. Result faults take precedence over bad A; clock_fault
independently records bad chronology. No source timestamp exists in InitResult.
Accept RUNNING/true only after valid C; first healthy poll is immediately due.

## Cadence and missed periods

Every poll clears fresh. Outside RUNNING it returns false without callbacks or
other report changes. A RUNNING poll increments poll_timing.calls, clears its
last_valid and observes S exactly once. A bad S faults with no native read and
no further clocks. Otherwise the first read is due. After any published sample,
due means accumulated age from its native started_us to S >= period P.

If age<P, increment not_due and return false after that one clock. There is no
read, A, C, accepted poll duration or update to the retained sample diagnostics.
At equality P a read is due. Each due poll makes exactly one read; no catch-up,
delay, retry, wait or burst. At each actual due read invocation, before calling
the Reader, add `floor(age_at_S/P)-1` to missed_releases; the first read adds0.
The value is nonnegative because the later call is admitted only when age>=P.
Count these missed releases even if the native result, A or C then fails: they
were already unserved at S. Capture.missed_before stores this local value for a
published record. Counters saturate; neither saturation nor lateness adds reads.

Examples relative to the preceding accepted source start: ageP and2P-1 skip0;
age2P skips1; age3P+1 skips2. These are cadence observations, not inferred missing
ADC conversions. Additional time after S does not change this call's skip count.
On accepted C, reanchor age to C-new_sample.started_us, rather than to S/A/C alone.
Future polls add all later accepted clock deltas. There is no second C-based
grid-skip calculation. A delayed C can make the next poll immediately due, with
misses evaluated then against the newly accepted source. An unsuccessful read
does not reanchor and is terminal. A frozen clock can leave later polls not due;
finite storage does not promise an independent wall-time watchdog.

## Read result admission and immutable publication

Before the callback, increment read_timing.calls, clear its last_valid and set
last_read_accepted=false. Save the actual returned Sample unchanged and set
sample_seen=true. Observe A immediately after return, then apply this precedence:

1. Unknown Status or Shutdown, or a known non-OK result with valid=true: CONTRACT.
2. Known non-OK with valid=false: ADC; preserve all actual fields and shutdown.
   Do not apply success-only voltage/timestamp/deadline rules to native failure.
3. For OK, require valid=true, shutdownNOT_ATTEMPTED, raw<=16383, finite voltage
   and ordinary float equality with `float(raw)/16383.0F *
   VBAT_ADC_REFERENCE_V * VBAT_DIVIDER_RATIO`. Failure is CONTRACT. Raw0 and the
   upper endpoint are valid software values, with no healthy-voltage clamp.
4. Evaluate A chronology, latching clock_fault even if an earlier result fault
   is primary. Only after accepted A evaluate successful source brackets:
   `0 <= start-S <= completed-S <= A-S < 2^31`, with native completed-start
   strictly below VBAT_ADC_CONVERSION_US. Equality at the100us default fails.
   Reversal, future/old source, or excessive span is SOURCE_ORDER.

Numerically repeated readings are permitted when produced by another bracketed
call. Neither equal data nor valid timestamps prove an honest hardware conversion
against a dishonest port; the real native Reader supplies freshness. All known
Status enumerators through NOT_ENABLED and all three Shutdown values are
recognized; none is converted to an invented result or silently narrowed.

For a semantically and chronologically admitted sample, copy the unchanged
Sample, S/A, qualified source span, read span and missed_before into the next
unpublished slot before C. C follows validation, tentative copying and ordinary
counter work. Only after valid C write that slot's C/poll span, then increment
count, set last_read_accepted=true/fresh=true and return true. These final fields
are closing publication, explicitly outside S..C. A bad C hides the tentative
slot and leaves the previous count unchanged. At capacity enter COMPLETE before
returning; this final poll is true/fresh. No read, clock, implicit shutdown or
extra record follows. Subsequent passive polls clear only fresh.

## Clock and timing reports

Every consecutive wrapper delta is unsigned and<2^31; equality and natural wrap
are allowed. Accumulate deltas within an active setup/due-poll S..C bracket and
from the last committed source start, including early polls and all inter-poll
gaps. Reject reaching half-range, even when individual deltas are smaller. Until
C accepts a new source, keep the previous source-era accumulator; then initialize
it to C-new_source_start. Before the first accepted sample only the wrapper
clock/bracket constraints apply. An entirely unobserved full wrap is unknowable.

Any rejected S/A/C is CLOCK unless another fault is already primary, independently
sets clock_fault, and suppresses all remaining callbacks/clocks for the operation.
No successful closure is fabricated. Result/shape faults are evaluated before A
chronology; successful source checks follow admitted A. An accepted A measures
read S..A even for a native/semantic failure. With no clock failure, still observe
C and measure a nonclock failed setup/read path. No wrapper cleanup is added.

Timing.calls counts actual beginBattery/readBattery callbacks for setup_timing/
read_timing, and RUNNING entries for poll_timing. Setup timing is S..C; read is
S..A; measured due-poll timing is S..C. Native source_us is completed-start and
appears only in published captures. last_valid clears when its category is
attempted; specifically a poll's bad S or not-due return changes poll timing only, never
read timing. A valid measurement increments measured_calls and updates last_us/
maximum_us. Bad timing preserves old numeric history with last_valid=false.
All diagnostic counters use saturating uint32 addition; attempted overflow sets
counter_saturated. Captured count is capacity-bounded and never wraps or overruns.

Report.sample_seen and last_read_accepted describe the latest actual read,
not the current poll and not battery availability. An early/no-read fault leaves
that historical sample and its acceptance flag unchanged. Report.fresh alone is
the new-record pulse. Captured records and the report preserve exact nominal
voltages; no B6 filter, source-age projection or averaging is introduced.

## Terminal ownership and evidence

First fault is terminal and immutable; independent clock_fault may still be set
by the remaining required post-call observation. Report.setup/sample retain the
actual first failing operation's result, or the prior actual sample if a clock
failed before another read. Future calls cannot replace it with FAULT_LATCHED or
clear fault/capture history. Only passive fresh clearing remains after terminal.

Reader has no public stop/disable API. On COMPLETE or wrapper fault, cease all
callbacks and retain the actual Shutdown, normally NOT_ATTEMPTED for success.
Never synthesize DISABLED, force a failing read, reconstruct/destruct the Reader
to reset it, manipulate registers, or claim that stopping callbacks disabled ADC1.
Known native faults already own D078's bounded cleanup; do not repeat it. The
boot-lifetime ADC claim persists. Cleanup-inclusive failure durations are not
subject to the success-only conversion span. Neither callback brackets nor
finite software guards abort a blocked callback or establish physical WCET.

## Required checks and deferred physical work

Independent tests derive from this adopted contract/header before execution and
without implementation-body reads. Cover passive grants/repeat begin/missing
ports; capacity0/1/128 and zero/half-range period; setup enum/shape/native priority;
first/equal/early/late cadence and the exact skip arithmetic; no bursts; raw0/
16383/repeated fresh values; scaling/nonfinite/unknown statuses; source brackets
and100us equality; natural time wrap, cumulative half-range and bad S/A/C; native
failure shutdown; immutable captures and final fresh; failed C hidden slot;
measurement category independence and terminal silence. Inspect saturation
branches without private seeding or claims of executing billions of polls.

Counted native-binding tests execute direct Reader begin/read and prove no
beginWithButtons/readButtons call or other owner; actual default sketch setup
plus10000 loops must perform no callback. Keep old D078/D086/native-pins tests
and assertions unchanged. Coordinator owns a new literal registry expectation,
normal/sanitizer regression and target build policy. Compile only via the checked
literal vbat.ino route, inert default/Immediate flags; MATCH/uploads/sketch.yaml/
sketch.yml including symlinks must refuse before transport. No inert upload key.
Audit actual staged sources/objects/ELFs, native paths, startup/imports and
conditional loader fit. A syntax check or compiler exit0 is insufficient.

Stable RAM is the software deliverable here. A later physical plan must associate
frozen captures with verified source/config/deployed identity, actual divider/
reference/supply checks and time-correlated multimeter readings across9.5..12.6V.
Retain each signed/absolute error and worst observed error; no average hides a
failing sample. Physical points/settling protocol and a frozen-bank readout tool
need separate review. F097/F098/F108/F115 do not establish actual0.05V accuracy,
SC-AJ clock behavior, pad permission, app WCET or any human phase gate.
