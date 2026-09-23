# Draft: finite B3 IMU heading bench

Proposed2026-09-24; NOT ADOPTED. Public drafts are in
`P2_imu_heading_bench_headers/`. Source inventory:
`P2_imu_heading_bench_design.md`. Existing D080/D081/D082/D083/D094 semantics,
native guards, pins, mounting and calibration defaults remain unchanged.

## Ownership and permission

Native owns exactly one `imu::Acquirer`; direct callbacks are clockUs/startSetup/
advanceSetup/beginRead/advanceRead/cancelRead. No legacy read, second Bus, Wire,
Adafruit path, Runtime, Robot, Controller, MotorGate, ADC, buttons, QTR, matrix,
UART/Bridge, network, reset or stop interface. Runner owns the actual pure
Estimator and countdown::Services; do not duplicate integration or averaging.
Construction/destruction/port creation/accessors are passive.

This decision would explicitly permit a bench-only timer anchor in Services::start,
preserving D024/D083 windows and admission. It is not a Controller release, START,
GO, countdown permission or motor gate. Existing core/header behavior is unchanged.

Begin is one attempt; repeat returns false with no changes. `enabled=false`
returns true/DISABLED without any callback or other validation. With enabled=true,
missing exclusive_i2c, power_confirmed or at_rest_confirmed returns GRANT before
callbacks/config. Mounting remains the existing explicit Mounting, zeros/false by
default; the actual Estimator validates confirmation/proper map/initial bias.
Check every callback next (null context allowed), then bench configuration, then
Estimator.begin(mounting, initial_bias_dps). Estimator failure is HEADING and its
actual report is retained, with no clock/native call. Default sketch passes Grants{}
and asserts MATCH=0/MOTORS_ALLOWED=0. Permission values are caller evidence only.

## Proposed configuration and bounds

Add only uint32 duration/count constants: IMU_BENCH_TRIAL_US60000000,
IMU_BENCH_CHECKPOINT_US1000000, IMU_BENCH_CHECKPOINTS61,
IMU_BENCH_DEADLINE_US70000000 and IMU_BENCH_MAX_POLLS100000000.
These are proposed engineering bounds, not measured rate/WCET guarantees.
Use existing TICK_US for setup and new-read releases; do not change its default.

Require 0<TICK_US<=IMU_HEADING_MAX_GAP_US<2^31; positive checkpoint period >=
IMU_HEADING_MAX_GAP_US; trial a positive exact multiple of checkpoint period;
checkpoint count exactly1+trial/period; deadline<2^31 and greater than
IMU_SETUP_DEADLINE_US + CAL_END_MS*1000 + trial, evaluated without overflow;
0<MAX_POLLS<UINT32_MAX. Duration arithmetic/products use uint64 for validation.
Native/Estimator/Services retain their own config validation/static assertions.
Zero divisor profiles must compile with an explicit constexpr exclusion, never a
replacement period. Zero count may reserve one inaccessible array placeholder.

Each active poll consumes one budget slot; MAX_POLLS polls are admitted. The next
entry faults LIMIT before another clock/native progress, apart from required
pending cancellation. Timing.calls still counts that faulting active entry.
Elapsed deadline runs from begin's first S through every accepted later wrapper
clock; equality faults DEADLINE. Neither bound acts when the caller stops polling.

## Wrapper clocks, first faults and publication

An active operation observes S, makes at most one normal Port callback, observes A
immediately after its actual result is saved, validates/does pure work, then observes
C. Early not-due polls observe S only. No remaining normal callbacks/clocks follow
rejected chronology. All source/callback enum/shape failures are selected before
A chronology, preserving their first fault while independently latching clock_fault.
After accepted A, successful source brackets and pure consumers run. All nonclock
failures still take C unless a later clock also fails. C follows tentative checkpoint
copy and ordinary counters; final checkpoint C/poll span/count/flags publication is
explicitly outside S..C. A rejected C hides the tentative slot and changes no
previously published record. Actual provider/pure reports may already reflect work
done before C; they are diagnostics, not a successful checkpoint claim.

Every consecutive unsigned delta must be<2^31, including equality0 and natural
wrap. Accumulate accepted deltas over the whole bench lifetime (deadline<half),
each active S..C bracket and the current release-grid era; reject reaching half.
Do not reset a lifetime/grid age at arbitrary modulo wrap or a callback return.
An unobserved full wrap cannot be detected. CLOCK is primary only if no earlier
fault; clock_fault independently latches. First fault remains immutable.

When a wrapper failure may leave a read pending, cancel exactly once. Conservatively
mark possibly_pending before beginRead; clear it only after a structurally valid
terminal result. A well-formed native FAULT already owns cleanup and is not
cancelled again; a malformed apparent FAULT is not evidence of cleanup.
If A is accepted and failure is known before C, call cancelRead(A) before C and
save its actual result separately; C closes the cleanup-inclusive poll. Cancellation
shape never overwrites the first fault. If S/A/C chronology fails, or LIMIT prevents
S, pass the last accepted actual wrapper timestamp as a historical cleanup input,
never as a claim about current time, and make no additional clock call. A native
TIME_ORDER result from that conservative timestamp remains real evidence. If failure
is first detected at C, cancellation uses that C when chronologically accepted,
otherwise the last accepted clock, with no new closing observation. No fabricated
duration/cleanup success. Cancellation return is never fed to Estimator/Services.
No cancel exists for Setup; a completed semantic setup rejection is not a claim
that I2C was disabled. No implicit cleanup on successful COMPLETE.

## Begin, setup and read scheduling

After pure admission, begin observes S and calls startSetup(S,true), then A/C.
Retain the exact SetupReport. Known FAULT with a known non-NONE SetupFault is SETUP;
unknown state/fault/bus/cleanup or contradictory healthy state is CONTRACT.
Healthy start must return IN_PROGRESS, faultNONE, started=observed=S, zero advances/
requests, and default NOT_INITIALIZED/NOT_ATTEMPTED/flags0. Accepted C enters SETUP.

The setup release grid starts at begin S; first advance is due at S+TICK_US. A
not-due poll increments setup_not_due and returns after one S. At a due call,
slots=floor(age_at_S/TICK_US), missed=slots-1; add missed_setup_releases and advance
the grid by slots*TICK_US before exactly one advanceSetup(S). No catch-up burst.
Healthy setup reports retain original started, increment advances exactly1,
increase requests by0or1 within native caps, and have faultNONE. IN_PROGRESS and
PROFILE_READY are the only healthy states; observed lies in current S..A (a wait
sets it to S). Preserve native FAULT diagnostics without success-only timestamp
checks. Enum/counter/identity malformation is CONTRACT. Native fault takes priority
over counter/source checks; physical48-call profile verification remains native.

Healthy setup has cleanupNOT_ATTEMPTED/flags0, with busNOT_INITIALIZED before any
request and busOK after a request. PROFILE_READY also requires a nonzero request
count. Setup response checks do not recreate its register sequence.

On validated PROFILE_READY and accepted C, call
Services.start(C, current_estimator_bias) once and record calibration_started_us=C.
This pure timer initialization is closing publication outside S..C; it is not a
source observation, Controller event or invented START. A false return is
CALIBRATION. Otherwise enter CALIBRATION. The public ServiceResult remains its
default until an actual later Services.step returns a result; there is no getter
and no fabricated post-start snapshot. First beginRead is due on the next poll.

First beginRead S initializes a separate read grid. Later idle read starts use
the same slots/missed arithmetic as setup, counted in missed_read_releases at
actual invocation even if its result/A/C fails. Read-not-due polls increment
read_not_due and take only S. While PENDING, ignore release eligibility and call
advanceRead(S) once per poll, without a wait loop. Grid age still advances; missed
starts are counted only at the next actual begin. No new begin or legacy call is
made during pending work. Scheduling counts unserved release opportunities, not
missing sensor generations. Each native operation keeps its original600us budget.

## Progress/source and pure consumers

Save each actual progress before A. A healthy begin must be PENDING/started=true/
completed=false. A healthy pending advance is PENDING/false/false. Every PENDING
Sample equals a default Sample memberwise, including all motion arrays/metadata;
it is never delivered to a pure consumer. A begin may instead return a newly
completed native FAULT; a successful COMPLETE on begin is CONTRACT. Terminal
advance must be COMPLETE or FAULT with started=false/completed=true. IDLE,
replayed completion, unknown enum or contradictory pulses is CONTRACT.

For a terminal FAULT, require SampleStateFAULT and a known non-NONE SampleFault,
known BusStatus/Cleanup, default motion/phase/gap/previous-observation fields;
retain its sequence/checked time/error flags and actual native cause. Select SOURCE
before A chronology, with no success-only timestamp constraint. A well-formed fault
is consumed once by Estimator after accepted A for actual source-fault evidence;
its invalid estimate can be delivered to Services if calibration is still active.

For COMPLETE require SampleState NO_NEW or OBSERVATION, faultNONE, busOK,
cleanupNOT_ATTEMPTED and flags0. Successful checked_us lies in the current S..A.
NO_NEW requires default motion, readiness_completed=checked, motion_started0,
gap0 and previous=false. OBSERVATION requires motion.completed=checked and its
motion.started through readiness_completed through motion_started through checked
ordered within the original beginRead-S..current-A bracket, with motion duration
strictly below IMU_I2C_TRANSFER_US. Invalid brackets are SOURCE_ORDER. The actual
Estimator remains authoritative for remaining D082 payload/sequence/gap/rail
validation; do not duplicate the byte decoder. Any Estimator FAULT is HEADING
unless SOURCE already won. First accepted observation sequence is1, then+1;
NO_NEW retains identity, through the actual Estimator. Do not seed private state.

Deliver each well-formed completion to Estimator exactly once. In CALIBRATION,
step Services exactly once for each such completion at delivery A: raw pre-bias
body-Z plus VALID/ABSENT/INVALID mapped from actual Estimate; source time/sequence
from Estimate; explicit_line=true with no line/opp payload. No call on PENDING or
an early poll and no synthesized missing sample. Services' own close-before-sample
ordering applies at CAL_END, including delayed completion. This may close on the
first later actual completion; no window extension admits a late source.

Retain the actual ServiceResult. When calibration_finished first appears, rejection
is terminal CALIBRATION with prior bias retained. Otherwise applyBias exactly once;
false is HEADING. Record actual accepted bias/application flag and the actual
Estimator.report after application: applyBias updates only its bias field, retaining
the last raw/corrected observation values until a later observation. Never rewrite
that earlier evidence with a newly subtracted bias. After accepted C enter MEASURING.
The completion that closed calibration is never the measurement anchor. Stop
stepping Services after its calibration result is frozen; active/
finished remain its actual values, not an invented completed countdown. No yaw reset.

## Finite measurement and checkpoints

The first subsequent updated heading anchors measurement and stages checkpoint0.
Only updated observations contribute; NO_NEW does not move endpoints or extrema.
Retain actual source start/end, sequences, headings, relative delta and elapsed
source time. On every accepted-C observation, update min/max delta, max absolute
excursion and observation count. Compute delta as double(current published heading)
minus double(anchor published heading), without re-integrating or claiming access
to the Estimator's private double accumulator. Require finite derived differences; NUMERIC is
terminal before publication. The actual Estimator continues unwrapped integration.

Checkpoint k>0 is the first accepted updated observation with source elapsed >=
k*CHECKPOINT_US; store its actual Sample/Estimate plus delivery A and closing C,
never an interpolated time/value. At most one checkpoint may be staged per poll.
An observation reaching a second unfilled boundary is CONTRACT rather than
duplicating the same sample into skipped slots; normal D082 gap<=checkpoint period
precludes it. First observation at/after TRIAL_US publishes final checkpoint and
enters COMPLETE, returning true with both fresh flags. Its actual elapsed may
exceed60s slightly; retain that value. Checkpoint count is exactly configured count
on success. Previously published records remain immutable through faults/lifetime.
Access returns const pointer only for index<count; capacity always reports config.

poll returns true only for a newly published checkpoint. Each entry clears
checkpoint_fresh and observation_fresh; terminal/disabled entries change nothing
else and perform no callback. observation_fresh is true for any accepted-C updated
observation, including calibration observations; it does not mean checkpoint or
physical freshness. Report diagnostics retain actual most recent setup/progress/
estimate/calibration/cancellation. completions counts actual well-formed terminal
replies before A validation, including native FAULT and later closing failures;
pending_results likewise counts actual well-formed pending replies even if A/C
later fails. observations/no_new count successful Estimator categories committed
after accepted C with no wrapper fault. missed releases count invocations.
Measurement.observations covers only accepted-C measurement observations, anchor
included. maximum_observation_gap_us covers accepted updated samples across phases.

All wrapper diagnostic uint32 additions saturate; flag only attempted overflow,
not exact arrival at max. admitted_polls caps at its configured limit; checkpoint
count is capacity bounded. Copy Services' actual diagnostics unchanged.
Timing.calls counts actual callbacks, and active poll entries for poll_timing.
Clear last_valid when attempted, preserve old numeric history after rejected time.
Normal callback timing is S..A; poll timing S..C includes validation/pure work/
tentative copying and any pre-C cancellation. Accepted A measures even semantic
failure. Early polls have no measured poll duration. Cancellation timing is the
accepted trigger A..C bracket, which includes intervening validation; late/invalid-
clock cleanup has no measured duration. These are observations, not physical WCET.

## Checks, scope and adoption items

Freeze this contract/header before independent execution; author may work in parallel
from public declarations and must not read implementation bodies. Test permission/
passivity, setup cadence and truthful faults, every progress pulse/default payload,
cancel-once/clock-fault paths, D024/D083 window/absence/rejection/bias behavior,
analytic heading and source-gap boundaries, delayed/failing C,60s endpoint and
all61 immutable checkpoints/extrema, wrap/half-range/deadline/limits/counters, strict
zero/invalid profiles, native single-owner forwarding and default10000-loop silence.
Existing core/HAL/locked assertions remain unchanged. No impossible first1-to-wrap
sequence trace is required within a finite60s test; natural time wrap is required.
Default successful calibration needs dense source observations to satisfy the
existing2ms heading-gap limit through the3s window. Exactly-two/too-few admission
cases may use explicitly labelled, mutually valid temporary timing/config profiles;
do not fake private state or weaken native/Estimator defaults to make them reachable.

Compile only via new literal checked imu_heading.ino policy: inert default/Immediate,
MATCH/upload/profile and symlink refusal before transport, no upload key. Audit
actual staged source/objects/ELFs, native paths, startup/imports and conditional
loader fit; declaration or syntax success alone is insufficient.

Adoption must confirm the proposed five constants and timer-anchor permission.
No other software requirement is intentionally deferred. Later physical work must
verify supply/bus/mounting/stillness/clock and capture provenance. STILL uses actual
duration, endpoint drift AND maximum observed excursion against2deg; a separately
labelled hand-rotation run compares actual signed delta with externally confirmed
+/-360deg within3deg. The bench does not know that the hand turned exactly360deg.
One trial per boot; no physical accuracy, healthy cadence,800us app WCET or gate
follows from synthetic tests, guards or nominal60s clock arithmetic.
