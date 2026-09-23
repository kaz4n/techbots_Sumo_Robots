# D081 MPU6050 qualified acquisition and observed silence

2026-09-23 Asia/Dubai. Baseline eb4ff3a, D051/D075 authority; P2 B3/B14.
Public headers imu_bus_unoq.h and imu_acquisition.h freeze before implementation
and independent tests. Existing D079 transport and D080 setup/decoder semantics,
all core/application/locked tests and previous config defaults remain unchanged.

## Adopted freshness inference and its limits

Adopt the explicitly conditional status/STOP/motion inference in
P2_mpu6050_sample_audit.md (manufacturer RM Rev4.0 pp27-32 sensor shadow
wording and interrupt read-clear rules; retained primary extracts/model receipts).
Require the D080 profile, sole owner, INT_RD_CLEAR0 and no intervening reset/mode
change. A successful status read of1, completed STOP/idle and subsequent15-byte
INT_STATUS+motion burst qualify one new observation under that model. The second
status read clears pending events that may already be represented in the shadow;
do not replace this with a14-byte motion-only read. Its own status bit0 grants
no additional observation. Numerical payload equality says nothing about freshness.

This is a source-based engineering inference, not measured silicon synchronization.
Multiple updates coalesce; accepted-observation sequence is not a sensor generation
counter. Bus timestamps are observation intervals, not physical sample times.
The198clock worst conditional corner659.340us exceeds the unchanged600us bound;
a slow transaction must fail. Healthy >=800Hz, timing/age, sensor settings and full
tick WCET remain physical/integration acceptance work. Do not increase the budget,
lower the source timeout, claim800us complete tick or combine two600us allowances.

## Native Bus::acquireMotion

One native Operation has one start, one600us exclusive deadline and one8192poll
budget across both complete transactions, including inter-transaction admission.
The existing50us/8192 cleanup allowance remains separate and occurs at most once
on failure. No retry, reset, reenable, GPIO recovery or new peripheral ownership.
Existing public read/write/readMotion wrappers preserve their D079 behavior.
Refactor only their private transaction body to accept an existing Operation.

1. Existing lifecycle admission: before begin return FAULT with NOT_INITIALIZED;
   after a terminal Bus fault return FAULT_LATCHED and retained cleanup. No I/O,
   time reads, new diagnostics or payload in these paths.
2. Read one byte from0x3A using the existing checked register transaction. It must
   complete STOP-clear/idle/final ownership/error/time checks before proceeding.
   On successful completion set readiness_observed, readiness_status and
   readiness_completed_us, even if the byte's semantics are subsequently rejected.
3. Any status bit except bit0 is a terminal PROTOCOL fault. Native error_flags
   retains D079 native hardware/transport-protocol flags, never MPU byte bits;
   readiness_status preserves the MPU status diagnosis.
   Status0 returns NO_NEW, complete=true,statusOK,count0,zero bytes, one aggregate
   start/end interval, no motion_attempted, motion_started_us0,
   motion_status_observed=false and motion_status0.
4. Status1 allows the second transaction. Record motion_attempted=true and a
   micros-domain motion_started_us immediately before its admission (not a physical
   START timestamp). Read15bytes from0x3A under the SAME Operation. Its repeated
   START, data, STOP/idle and final checks are unchanged. Partial bytes stay private.
5. After complete successful second transfer, set motion_status_observed=true
   and motion_status to its byte0. Reject any bits except bit0 as terminal PROTOCOL. Otherwise
   OBSERVATION contains the15bytes,complete=true,count15,statusOK,cleanupNONE and
   native error_flags0. transfer.started_us is the FIRST transaction's start;
   transfer.completed_us is the final successful observation after the second.
   readiness_completed_us and motion_started_us are ordered within that interval.

For a successful second transfer whose byte0 is invalid, retain that byte in
motion_status diagnostically; motion payload remains zero on failure. No
undocumented meaning is assigned to native error_flags.
Any failed stage returns FAULT and a failed BusTransfer with ALL bytes/count zero
and complete=false. Readiness/motion-attempt metadata already established may
remain for diagnosis. A consumed readiness event can never be retried after a
failed second transfer. Any later public Bus operation sees the existing latch.
STOP completion is not an explicit software STOP request; do not synthesize one.

## Acquirer: concrete owned setup and runtime input path

Acquirer privately owns one concrete Bus and Setup, preventing mismatched setup/
bus objects or public register writes between setup and acquisition. Constructors
and destruction perform no I/O. start/advanceSetup/setupReport preserve Setup's
D080 public semantics. The first observed PROFILE_READY arms acquisition once,
anchoring latest_us and last_observation_us to that setup completion. Repeated
start/advanceSetup must never reset runtime state or a terminal sample fault.

read(now_us) before PROFILE_READY returns default NOT_READY with no Bus calls.
A failed Setup yields terminal SampleFault::SETUP and its actual bus diagnostics;
no acquisition is attempted. A runtime fault is latched; subsequent reads return
that identical fault report without I/O/count/time changes until object/boot reset.
Only this Acquirer owns its Bus; constructing a new object cannot evade D079's
irreversible boot claim. No production test-reset hook is introduced.

Each armed read starts a cleared Sample with the retained accepted sequence.
Validate IMU_SILENCE_US is positive and <2^31 (otherwise INVALID_CONFIG before
runtime Bus I/O). The existing B14 limit is named config::IMU_SILENCE_US=20000.
now_us must follow/equal the last accepted time observation in the unsigned
half-range; otherwise TIME_ORDER. At >=20000us since setup completion or the
last accepted OBSERVATION completion, latch SILENCE before any new request.
This is a conservative observed-data deadline; reset-only recovery is selected
under D051. NO_NEW does not extend it or masquerade as an invalid sample before
expiry. The later calibration adapter must keep these states distinct.

Then call acquireMotion once. Retain its native status/cleanup/error_flags.
Validate in this order:

- NonOK Bus status => TRANSPORT. FAULT or unknown acquisition state with statusOK
  => RESPONSE. Successful shape requires complete,flags0,cleanupNOT_ATTEMPTED and
  count0 for NO_NEW or15 for OBSERVATION. NO_NEW bytes must all be zero.
- started_us must follow/equal caller now and completed_us follow/equal start
  in forward half-range, else TIME_ORDER. Aggregate duration >=600us => RESPONSE.
- readiness_observed must be true; readiness_status0 for NO_NEW or1 for OBSERVATION.
  readiness_completed_us lies within the aggregate interval. For NO_NEW it equals
  completed_us, motion_attempted=false,motion_started_us0,motion_status_observed
  false and motion_status0. For OBSERVATION,
  motion_attempted=true and readiness completion <= motion start <= final completion
  using offsets within the aggregate interval; motion_status_observed is true
  and motion_status equals payload byte0. Malformed phase metadata => RESPONSE.
- Accept the final completion time through the same forward-time/silence checks.
  Completion at or after the silence boundary faults even if the call began earlier.
- OBSERVATION must pass the existing coherent decoder, otherwise RESPONSE. Only
  then increment sequence modulo2^32, publish decoded motion, copy phase timestamps,
  and reset the silence anchor to completion. had_previous_observation and
  observation_gap_us describe previous accepted completion to current completion;
  first observation has false/0. They are NOT a heading-continuity approval.

NO_NEW returns an empty motion, unchanged sequence, checked_us=completion and
readiness_completed_us for diagnosis; no motion time/gap/previous-observation flag.
An accepted OBSERVATION has checked_us=completion and real bus interval in motion.
Faults clear motion, phase timestamps, gap and previous-observation flag; preserve
sequence and native diagnostics established during this call. checked_us is the
last validated time (caller now until final completion validates; a SILENCE fault
records that monotonic expired observation). A TIME_ORDER fault retains the prior
validated time. No old gyro/accel payload is replayed on any unsuccessful result.

This supplies sensor-coordinate samples only. Calibration observation-presence,
mounting transform, bias, numerical yaw integration and gap/recovery policy stay
explicit next integration tasks. No imu_ok, application change or behavior motion
is synthesized here. R1/R5/R6/MotorGate and the1kHz scheduler contract stay intact.

## Independent validation

Native new tests extend the existing source-derived fixture additively, without
changing established D079 assertions/model behavior. Check1+15byte ordering,
first STOP/idle before second START, status0/1/all unexpected bits, repeated distinct
and numerically equal observations, no stale bytes, errors/ownership at both
phases, aggregate deadline-minus1/equality/wrap, frozen shared poll exhaustion,
one cleanup allowance, terminal/no-I/O, and allocation-free behavior. Existing
D079 suites must still pass. Fixture models protocol progression, not silicon
shadow synchronization; the separate source inference remains conditional.

Independent Acquirer tests link actual implementation to direct Bus substitutes:
real D080 setup, no pre-ready read, setup failure, one-time arming, repeated
NO_NEW/new observations, unchanged/equal payloads, malformed result shapes/phases,
native failures, exact20ms call/completion boundaries, time wrap/reversal,
sequence/gap observations and latched identical failures. All failure data zero.
Config14 strict methods retain previous assertions. Add actual never-called
retained-method probe and startup counters in both host macro configurations,
all upload refusals, actual UNO Q compile-only/ELF/source review, full relevant
host/sanitizer/tooling checks and genuinely separate review. No MCU operation,
physical phase gate, PINMAP or per-run motor authorization follows.


## D094 additive runtime amendment,2026-09-23

P2_imu_resume_contract.md adds a separate pending envelope and bounded advances
on this same Acquirer/Bus. No pending value is a Sample, NO_NEW or source refresh.
Every active advance checks caller time/silence; semantic abort cancels native work
once. Legacy read while pending is terminal misuse with TRANSPORT/CANCELLED. Legal
idle legacy read and D081 final source/sequence/phase semantics remain unchanged.
