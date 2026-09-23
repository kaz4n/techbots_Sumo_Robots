# D083 explicit gyro admission during countdown

2026-09-23 Asia/Dubai. Baseline06e7d0d. D051/D075 authorize software development;
D024 calibration and every established locked assertion remain intact. Freeze
this contract and countdown.h before independent implementation/tests.

## Scope

Implement the actual Services/Lifecycle consumption path for explicit new/absent/
invalid gyro observations. This is a bounded prerequisite to Robot's later unified
IMU adapter. Do not change Robot, HeadingReference, Fusion, B15, HAL or app yet:
their separate retained-heading/evidence routes remain enumerated in
P2_imu_heading_raw/next_adapter_audit.md. No physical fact or acceptance follows.

Append GyroPresence {LEGACY, ABSENT, VALID, INVALID}, gyro_observation_us and
gyro_sequence to ServiceSample. Preserve old field order, aggregate callers,
defaults and all existing public signatures. Use only C++17/time passed by caller.
No I/O, allocation, clocks, callback or new config value. LEGACY is compatibility,
not a permitted fallback for malformed explicit observations.

## Timing and mode

Keep current Services::step ordering: same decision timestamp is ignored wholly;
otherwise advance elapsed time, close calibration at/after CAL_END before looking
at that call's gyro, then run warning/snapshot/hold services. A delayed observation
delivered at CAL_END cannot reopen the window or delay GO. Preserve sparse calls,
wraparound and cancellation/STOP priority. Calls remain less than one uint32 wrap
apart as in the existing service contract.

Only decision calls inside [CAL_START,CAL_END) reach gyro admission. The first
such call with a known GyroPresence selects LEGACY or explicit mode for the attempt;
ABSENT/VALID/INVALID all select explicit. Mixing legacy and explicit later rejects
the attempt and contributes no reading on the mixed call. Unknown enums reject
without choosing a mode. A rejected attempt can still collect later valid readings
for diagnostics, but cannot accept a bias. Reset/start/cancel clear admission state.
No validation or identity update occurs outside this decision window.

LEGACY preserves the old behavior exactly: finite raw gyro and imu_ok=true adds
one reading per distinct decision timestamp; other readings reject. Added source
fields are ignored. Existing tests remain unchanged.

## Explicit admission, in order

ABSENT ignores imu_ok, all numeric/source fields, and contributes no reading or
invalid-reading flag. It still advances all services. INVALID rejects calibration
without using numeric/source fields. Unknown enums reject. VALID ignores imu_ok:
its explicit presence, not heading health, qualifies gyro evidence.

For VALID:
1. Require finite raw_gyro_z_dps. Require unsigned decision_time-source_time <=
   IMU_HEADING_MAX_GAP_US (2000us default). Thus equal age is accepted, one beyond,
   future times and half-range ambiguity reject. This explicitly reuses D082's
   bound as maximum calibration delivery age, without changing any config value.
2. First source identity may have any sequence including zero; the service may
   begin consuming well after Acquirer startup. With previous identity, compute
   uint32 deltas in source time and sequence. If both deltas are zero and finite
   raw value equals the prior raw value, ignore the duplicate. Either one alone
   zero, either delta >=2^31, or changed raw value for the identical pair rejects.
   Forward gaps in sequence are allowed: only actually delivered distinct
   observations are averaged; skipped observations are never fabricated.
3. Commit a valid distinct source identity/raw value even if its source precedes
   CAL_START. This prevents a pre-window sample from becoming new through replay.
   Rejected/duplicate calls never replace identity. All ordering is wrap-safe.
4. Compute source elapsed time as decision elapsed minus delivery age, only when
   decision elapsed >= age. Add a reading only if source elapsed is also in
   [CAL_START,CAL_END). A fresh pre-window source is excluded, not an invalid
   reading. Decisions after the window were already closed above.

Aggregation remains D024: mean of admitted finite raw pre-bias values, spread
max-min <= CAL_MAX_SPREAD_DPS, at least CAL_MIN_SAMPLES, and no rejected reading.
Acceptance/rejection occurs once; rejection keeps previous bias. ABSENT-only or
one-reading windows reject for too few samples. Do not use acceleration validity
or heading availability as gyro validity. Estimator.applyBias is a future-increment
consumer and remains separately owned by the future app adapter.

## Acceptance

Independent spec/header-derived tests must cover legacy compatibility; all four
presences and unknown enums; mode mixing; exact source/decision window boundaries;
2000/2001us age and future/wrapped source times; same/change/partial identities;
sequence/source forward jumps, reversal, half-range and wrap; duplicates delivered
on later ticks; no mutation after finish; cancel/reset/start identity reset; finite
and spread/minimum thresholds; absent data while line/snapshot/hold/STOP progress;
Lifecycle MODE cancellation and valid qualified START release through full hold.
Include an analytic fixed-seed stream with independently counted distinct readings.
Do not edit any established locked or ordinary test. Run full host and sanitizer
regressions, a compile-only target probe and separate fresh read-only review.

Later Robot integration must populate this explicit interface after acquisition
and before the decision timestamp, while separately routing usable heading and
new acceleration to their consumers. This change alone is not integrated physical
B3, complete P2, a passed gate or an authorization to upload/run firmware.
