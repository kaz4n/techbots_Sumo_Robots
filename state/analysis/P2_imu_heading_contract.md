# D082 body coordinates and continuous heading

2026-09-23 Asia/Dubai. Baseline 2ab0f6e. D051/D075 authorize this actual P2 B3
software task. D024 calibration averaging and D059 logical GO origin remain
unchanged. This contract and imu_heading.h freeze before independent code/tests.

## Scope and coordinate evidence

Implement the concrete Estimator over D081 Sample. No clock, I/O, allocation,
callbacks, additional fusion library or bus ownership. It computes planar yaw;
no tilt compensation, gravity removal, position or magnetometer inference.

Body X is forward, Y right and Z down, so positive body-Z rotation is clockwise.
Mounting.body_axis uses +/-1, +/-2, +/-3 for signed sensor X/Y/Z. Require each
absolute axis exactly once and determinant +1 (24 proper signed permutations).
Require confirmed=true. No physical mapping is selected or verified here: the
default is zeros/false, and eventual robot assignments belong in config.h after
mounting evidence. Synthetic test mappings are explicitly not hardware facts.
Mapping is immutable after the first begin. Reconstructing only this estimator
cannot resume a running Acquirer: its first accepted sequence must be 1.

## One-shot lifecycle and faults

Construction/report/observe-before-begin do no work beyond returning the default
NOT_STARTED report. applyBias before begin returns false without mutation.

First begin validates in this order: config, confirmation, proper map, initial
bias. Config requires 0 < IMU_HEADING_MAX_GAP_US < IMU_SILENCE_US < 2^31. The new
gap default is 2000us (two control periods), selected as a conservative development
continuity policy, not measured sampling tolerance. It does not change B14's20ms
acquisition deadline or any existing B16 default. Invalid config/confirmation/map
or bias yields the corresponding terminal fault. A valid begin stores map/bias
and returns true with WAITING. Repeated begin returns whether the existing state
is nonfaulted and changes nothing, including ignored replacement arguments.

Any fault is reset-only for this instance. Subsequent observe/begin/applyBias
leave its report identical; begin/applyBias return false. No public reset or GO
entry exists. Fault report: state FAULT, specified fault/source cause; gyro and
accel Presence::INVALID; all sensor/heading values, observation time, age and
availability/update flags zero/false. Retain only current bias, accepted sequence
and last validated checked_us. This is loss of IMU heading availability, not a
new motor inhibit or a change to existing B14 timed fallback.

## Observation admission, in order

1. Before begin or after fault, return the unchanged report. Otherwise start a
   cleared WAITING report retaining bias, accepted sequence and checked time.
2. NOT_READY is benign ABSENT only before any NO_NEW/OBSERVATION has established
   profile_seen; it does not inspect or advance time. Later NOT_READY is INPUT.
   FAULT with a known non-NONE SampleFault becomes SOURCE, retaining that cause
   without trusting its timestamp. FAULT with NONE/unknown cause is INPUT.
   Unknown SampleState is INPUT.
3. NO_NEW/OBSERVATION require SampleFault::NONE, BusStatus::OK,
   cleanup NOT_ATTEMPTED and error_flags0, otherwise INPUT. Mark profile_seen.
4. checked_us must be equal/forward within unsigned half-range of the last
   validated time, else TIME_ORDER retaining the previous time. The first such
   sample accepts its time without a prior anchor. Accept the time before later
   sequence/payload checks. If a heading observation exists and its age is
   strictly greater than IMU_HEADING_MAX_GAP_US, fault GAP immediately. Equality
   is allowed. This check applies to NO_NEW as well as OBSERVATION; no extrapolation
   or late recovery can bridge an unobserved interval.
5. NO_NEW requires the unchanged accepted sequence, otherwise SEQUENCE. Its
   motion.coherent must be false, had_previous_observation false and
   observation_gap_us0, otherwise INPUT. Unused absent payload is ignored and
   never copied. If a previous observation exists, return READY with retained
   heading, its original observation_us, actual checked-minus-observation age,
   heading_available=true, heading_updated=false; both presences ABSENT and all
   gyro/acceleration values zero. With no observation, return WAITING, no heading.
6. OBSERVATION requires sequence=previous+1 modulo2^32 (first=1). First has
   had_previous_observation=false/gap0; later ones have true and gap exactly equal
   to checked_us minus the prior accepted completion. A mismatch is SEQUENCE.
   Later observations at equal completion time fault TIME_ORDER. There is no
   duplicate-as-new path, no skipped accepted observation and no counter reset.
7. Require coherent motion, DecodeStatus::OK, motion.completed_us=checked_us,
   unsigned motion duration < IMU_I2C_TRANSFER_US and <2^31, status bits other
   than bit0 clear, and rail bit7 clear. Every scaled gyro/accel component must be
   finite and within inclusive configured +/-1000dps and +/-8g. Otherwise INPUT.
   The actual checked Acquirer/decoder remains the source; do not re-decode raw
   arrays or duplicate native phase validation in this numerical consumer.
8. A rail on the selected body-Z gyro channel faults SATURATION. Other gyro-axis
   and temperature rails do not qualify or invalidate planar yaw. Horizontal
   acceleration rails are handled separately below, so impact saturation does
   not erase a valid yaw history.

Sequence counts accepted Acquirer observations, not every coalesced physical
sensor generation. Time checks are based on observation completion, not sample
time. D081's conditional freshness model and SC-AJ remain prerequisites.

## Integration and publication

Map the selected body-Z rate and retain it before bias. First accepted observation
anchors yaw at 0 degrees; do not integrate a prehistory. Later observations use
double arithmetic:

    increment = (0.5 * (previous_raw + current_raw) - current_bias) * gap_us / 1e6
    yaw = previous_yaw + increment

This trapezoidal rule uses observed completion times as an explicit approximation.
No GO reset, wrap to360, integration on NO_NEW or extrapolation. Preserve the
double accumulator and publish a finite float heading; unrepresentable/nonfinite
intermediate/output values fault NUMERIC before committing sequence/history.

Successful observation publishes READY, VALID gyro, heading_available/updated=true,
raw and bias-corrected body-Z rate, current bias, sequence, checked/observation
time equal to the accepted completion and age0. Store the raw endpoint for later
integration. Map body X/Y acceleration. If either selected horizontal channel is
at a rail, publish accel INVALID and ax/ay0; otherwise VALID and mapped values.
An ignored vertical acceleration rail does not invalidate horizontal evidence.
No old acceleration is replayed; this result alone does not create a contact cue.

applyBias accepts a finite value within inclusive +/-IMU_GYRO_RANGE_DPS while
begun/nonfaulted. Update stored/report bias only, preserving the existing report's
other fields and yaw/history; the next published gyro/next integration increment
uses the new bias. Invalid active update faults BIAS without replacing old bias.
Calibration rejection means the caller does not request an update. D024 remains
the sole calibration averaging/acceptance contract; this class does not average.

## Validation and next integration

Use an independent author who reads this contract/public header, not production
CPP. Analytic constant/ramp/bias traces, all24 proper maps and rejected reflections,
NO_NEW time/age/payload behavior, exact gap bounds, clock wrap/reversal, first/later
sequence rules, rail separation, every finite/range/config boundary, fault latching,
no GO reset and finite bounded outputs must be exercised. Preserve old tests and
all locked assertions. Test actual constructors/setup/10000loops of the inert
compile probe in both macro modes and all eight upload refusals. Native target
compile/source/ELF/startup review and focused sanitizer/full host checks follow.

Core calibration/freshness routing is the next integration task: current imu_ok
still conflates new gyro, current impact evidence and usable retained heading.
Do not wire this class into Robot/app before separating those semantics. The class
is actual HAL computation needed by that path, not completed physical B3 or a
passed phase. Mounting, drift/rotation accuracy, healthy rate, complete tick WCET,
SC-AJ/F091 and all human/physical gates remain pending.
