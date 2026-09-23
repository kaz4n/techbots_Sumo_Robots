# D084 estimator-to-Robot evidence routing

2026-09-23 Asia/Dubai; baselinec72921c. D051/D075 authorize implementation without
inventing physical tests/gates. Previous goal turn made concrete progress: D083
Services implemented5516bef and independently tested/reviewed. This task completes
the software estimator-to-Robot path, not merely an unused metadata helper.

## Explicit input admission

Append core::ImuEvidence to RobotInput; old fields/order/default callers remain.
ImuPresence codes1=ABSENT,2=VALID,3=INVALID; all other codes invalid. The first
admitted Robot tick chooses legacy or explicit_values mode until Robot reset.
Switching mode, contract_valid=false or malformed explicit data latches existing
HEADING_CONTRACT inhibition. Buttons/STOP/services still run; no remote authority.
Same decision timestamp remains ignored by Robot before any input/receipt change.

Legacy retains all old behavior, including current imu_ok meaning and recording.
Explicit input ignores legacy imu_ok and sets usable heading from metadata. It
requires known presences and one of these shapes:

- Unavailable, not updated: both ABSENT (waiting) or both INVALID (degraded).
  Ignore/zero sensor payload and source fields for consumers; preserve accepted
  internal heading history. This alone is B14 absence, not a contract fault.
- Available and updated: gyro VALID, accel VALID or INVALID; finite raw continuous
  heading and gyro within inclusive configured IMU_GYRO_RANGE_DPS; VALID accel
  finite within inclusive IMU_ACCEL_RANGE_G. INVALID accel payload ignored/zero.
  observation_us==checked_us. The first observed sequence may be any uint32.
- Available and not updated: both ABSENT; known prior heading required, same
  heading value, observation time and sequence as that accepted history. Ignore/
  zero gyro/accel payload; retain usable heading and actual source time.

Available reports require decision-minus-checked, checked-minus-observation and
decision-minus-observation to be forward within unsigned half-range, with the
last age <= IMU_HEADING_MAX_GAP_US. Checked time must not reverse relative to the
last admitted available report (equality allowed). No timestamp is backdated to
the start of a tick: the future app obtains its decision time after acquisition.
The current bound is2000us; no tunable changes or physical timing claim.

An updated report after history must advance both sequence and source time by
1..2^31-1 modulo uint32. Sequence gaps mean unconsumed distinct provider reports,
not fabricated readings; provider Estimator owns integration continuity. Exact
same identity and same used heading/gyro/accel presence/VALID values is replay:
normalize to retained heading/both ABSENT, never another measurement. Changed
payload at the same identity, partial identity, reversal or half-range rejects.
Rejected input never replaces history. Unavailable reports do not reset source
history or bypass ordering when availability returns. Reset clears input mode,
history and all existing Robot state, preserving existing transaction-token rule.
Accumulate retained history age from every admitted decision interval, saturating
at uint32 maximum; only a distinct fresh observation resets it to delivery age.
Retained availability additionally requires this accumulated age<=2000us. This
prevents old timestamps becoming fresh again after one or more clock wraps.

## HeadingReference

Add a typed HeadingSample overload; preserve the old bool overload exactly.
Typed available input requires finite yaw and decision-minus-source<=2000us.
Fresh sources must advance within unsigned half-range relative to known history;
retained sources must match known value/time. updated without available faults.
Unavailable payload ignored. Only fresh input changes raw history/time. No reset
at GO. Duplicate decision clears origin/update pulses and otherwise ignores input.

GO with fresh available yaw selects CURRENT_GO at actual source time; retained
available yaw selects LAST_KNOWN at its original source time. Unavailable GO uses
last genuine history or NOMINAL_PENDING at GO when none. Available retained yaw
remains usable for motion. First fresh recovery resolves a pending origin once
at source time. Preserve old finite-coordinate checks/faults/projection rules.
Expose observation_us/age when history exists; heading_updated is a pulse only
for a fresh usable match coordinate. Before GO it is false; imu_ok remains false.
Origin timestamps never refresh during projections or ordinary retained ticks.
HeadingReference also accumulates/saturates history age across unavailable ticks,
so an old retained source cannot regain eligibility after a clock wrap. Legacy
input still has no new age cutoff; each healthy legacy tick is a new observation.

## Consumers and event/source clocks

Robot calls admission once, then all existing arbitration services in their
original order. Explicit calibration feeds D083 presence/source sequence/time and
raw pre-bias gyro; mode and GO/STOP timing unchanged. Bias result is applied by the
future app after Robot::step to Estimator::applyBias for future increments only.

- Motion rows/openers/search/defend use qualified available heading, including
  bounded retained yaw. No false IMU-loss fallback on a normal NO_NEW tick.
- Fusion impact uses only current VALID acceleration after replay suppression;
  visual close counters and opponent debounce continue every actual sensor tick.
- Stuck candidate starts only with fresh heading; while available it ages with
  current opponent ticks, updates extrema only on fresh heading, and may declare
  on a retained tick once its already-observed span and timer qualify. Unavailable
  or cleared sensor resets undeclared candidates; latched faults stay reset-only.
- Phantom creation requires fresh heading; bounded retained heading may compare
  for masking. Edge consumption/expiry/chase/contact timers retain event time.
  Expose/store marker heading source time separately from marker event age.
- World bearing may combine a current opponent observation with bounded retained
  heading. Preserve heading source time in view/memory; Robot initializes world
  age from decision-minus-that-source, not zero. Relative/front recency keeps its
  current opponent timestamp. No detection retains memory and ages it normally.
- Escape motion uses available heading, but new inward evidence at exit requires
  fresh heading. Record its actual source age; no cached/fallback promotion.
- Stall contact anchor and deflection comparison require fresh match heading;
  missing fresh angle does not stop the qualified timer. No late anchor retrofit.
- IMU-unavailable warnings use raw heading availability; a retained tick is healthy.
  QTR/opponent observations_fresh stays independent and unchanged.

Existing direct filter APIs/default aggregates preserve legacy behavior. The
new Fusion explicit fields are already-qualified caller evidence; Robot owns the
stateful admission/replay guard, never sample an electrical sensor twice.

## Recording, without payload growth

Keep25bytes and every legacy vector/flag rejection. Append FrameInput.explicit_imu
defaultfalse. Explicit format uses bits4..5 gyro and6..7 accel, each code1..3 above;
both nonzero identify this extension. Mixed zero groups are invalid. The original
four low bits retain meanings; IMU_OK describes usable heading. Gyro/accel VALID
means a newly admitted observation; otherwise numeric fields must be canonical0.
Measured zero is distinguishable through VALID. Heading may retain a finite
fallback coordinate with IMU_OK clear. Fresh usable heading is inferable from
IMU_OK plus gyro VALID; no exact source timestamp is encoded in the25byte frame.
Capture values/presence together in Pending, never from the later receipt tick.
All other pack validation/status/clamping and stored byte offsets remain.
CSV schema1 continues to carry uninterpreted raw flags/bytes; document this
self-identifying presence extension and preserve its nonsemantic validator.
No old tests are edited; the explicit selector permits new exhaustive tests while
legacy tests still reject flags>15. No RAM-capacity/default logging-rate change.

## HAL map and acceptance

imu::applyEstimate is a thin pure mapping from actual Estimate into RobotInput's
IMU fields/current bias. It sets explicit_values=true even while waiting, preserves
decision time/all unrelated inputs, and validates report state/fault/presence
shape plus used finite values/time/age metadata against D082. Unknown/inconsistent
report returns false and contract_valid=false with no invented valid reading.
NOT_STARTED/WAITING map ABSENT; FAULT maps INVALID; READY maps exact payload and
provenance. Do not call Estimator, clock, bus, Robot or motor from this map.

Adapter validation is stateless, before publication. Known enum values required.
Bias is finite within +/-IMU_GYRO_RANGE_DPS. NOT_STARTED must equal the default
report. WAITING has NONE faults, both ABSENT, false availability/update, zero
sensor/heading/observation/age/sequence; checked_us may reflect prior NO_NEW.
FAULT requires a known non-NONE HeadingFault, both INVALID, false flags and zero
sensor/heading/observation/age; accepted sequence and checked_us may remain. SOURCE
requires a known non-NONE acquisition cause; other faults require NONE. READY has
NONE faults, availability true and checked-minus-observation==heading_age_us<=2000.
Updated READY has gyro VALID and accel VALID/INVALID, age0, raw gyro within range,
corrected gyro finite within twice that range; do not require corrected==raw-bias
because applyBias intentionally preserves the previous report's numeric fields.
Retained READY has both ABSENT, raw/corrected gyro and acceleration0. INVALID
acceleration is also canonical0; VALID acceleration finite within configured range.
All READY headings are finite. Mapping an invalid report sets explicit metadata
contract_valid=false and zero IMU payload/bias, preserves unrelated RobotInput.

Independent spec/header-derived tests: exact boundaries/replays/unknowns/wrap,
GO with delayed/new/retained/missing evidence, source-age preservation, calibration
and separate acceleration validity, target/contact/edge priorities, stuck/phantom/
world/inward/stall behavior, all256legacy/explicit flag combinations, delayed
recording, actual Estimator->adapter->Robot streams with valid transaction receipts,
no allocation and inert compile-probe startup/upload refusal. Preserve every old
locked/ordinary assertion. Full host/sanitizer, target compile-only with retained
Robot+adapter paths and fresh independent review precede completion claims.
Physical axes/accuracy/drift/WCET, SC-AJ/F091, QTR acquisition/app scheduler and all
human gates remain unverified; never upload/run or manufacture those results.
