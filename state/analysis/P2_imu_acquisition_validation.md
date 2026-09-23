# D081 qualified MPU6050 acquisition validation

2026-09-23 Asia/Dubai. Implementation7b46598, prerequisite contract/header/config f0031e8, following
D080 implementation63c7eaa/evidenceeb4ff3a. D051/D075 authorize this P2 software
work before physical acceptance. No hardware assumption has been promoted to
measured evidence.

## Implemented boundary

The native Bus now performs status, completed STOP/idle, then a15-byte status plus
motion transfer using one600us/8192poll Operation. Both diagnostic status bytes
are retained, but only the qualified pair grants an observation. NO_NEW and any
failed transfer contain no old motion payload. Old single-request methods retain
their behavior; cleanup has the existing separate50us/8192poll bound, once only.

Acquirer privately owns the actual Bus and checked Setup. It arms once at observed
profile readiness, returns explicit NOT_READY/NO_NEW/OBSERVATION/FAULT, validates
aggregate/phase timestamps, and rejects observed silence at exactly20000us, both
before requesting data and at final completion. Faults latch with preserved
diagnostics and accepted-observation sequence; later calls do no I/O.

Source hashes:

- Native CPP:1955d95c5e523e1538aaa44c1aa72bfc79398937245a0b573dc7285796a00603.
- Acquirer CPP:6dd161d0f4837ecb0c0b2874b1d7a7ddff6228c79c786ae69c2ff6890eabb4ed.

The freshness inference is conditional on the documented shadow/read-clear
behavior, exclusive D080 profile and no intervening sensor reset. It does not
prove silicon synchronization. Multiple internal samples can coalesce; sequence
counts accepted observations. Completion time is not a physical sample timestamp.
The198clock mathematical slow corner exceeds600us and must fault, not increase
the deadline. Healthy sample rate and complete-tick WCET remain unmeasured.

## Actual validation

- Independent spec-derived author:7/7 tooling methods PASS31.058s, including
  actual Acquirer15cases/36491assertions,14native cases/260parent assertions,
  nine configuration variants, two actual inert-probe macro modes and10000loops
  each, and eight upload refusals before any board/transport lookup. Native child
  assertions propagate through isolation;260 is not a total of child checks.
- Strict config14/14 PASS0.078s; the only changed expectation is the named
  pre-existing B14 silence limit. Existing config/locked assertions are retained.
- Root complete normal host2/2 PASS6.33s. The mounted filesystem emitted a0.31s
  future-Makefile warning. A complete clean rebuild then passed, followed by
  detailed host2/2 PASS8.44s, exit0, with1071/22581406 plus37/3796846 and no skips.
  This verifies the final frozen sources without relying on incremental timestamps.
- Root complete ASan/UBSan2/2 PASS35.84s, exit0:1071cases/22581406assertions and
  enabled MotorGate37cases/3796846assertions. No failed or skipped cases.
- Actual UNO Q Linux compile-only PASS, CLI1.5.1/core1.0.0, FQBNunoq,
  MATCH0/MOTORS_ALLOWED0/startupdefault. Source
  147e08b1c639e43094fce8c78094e5350d2e5852a8f8531df67948237ef9900f;
  86236B program/36172B compiler globals, exit0. This is not runtime RAM evidence.
  Root and reviewer independently match all46source files, three ELF identities
  and36nonzero native exports. The reviewer checks actual constructor relocations,
  setup and loop; the new startup path performs memory operations only.
- Exactly five existing P0 inert-source identities reviewed and reproduced, with
  no new key or upload permission. See raw/manifest_adoption.json.
- Separate same-model review PASS/no open findings. The reviewer independently
  runs15Acquirer cases in normal and ASan/UBSan, all10existing D079 methods,
  seven D081 methods and14config methods. The308-file snapshot is unchanged;
  129nested process receipts contain127exit0 and two expected negative sentinels.
  This context previously gave read-only fixture advice; it authored no contract,
  production implementation or tests. Its initial14-byte suggestion was corrected
  to the specified15-byte second read before implementation/review, as disclosed.
- Full existing tooling443/443 PASS678.339s, exit0. Together with the seven new
  acquisition methods,450distinct tooling methods pass across separate runs.
  Config14 is already included in443, not counted again. The shared native
  receipt folder (named existing_native_bus) also contains motor/power runner
  receipts:369exit0 plus four required assertion/signal sentinel exits1.
  Existing setup variants retain92exit0 receipts. No historical receipt was
  overwritten; existing_receipts_summary.json records the groups.

The first author/root/reviewer wrapper compiles failed because the new test
omitted <initializer_list>; the required header was added without changing
predicates. The first native test workload did not exhaust the shared poll budget.
Its corrected stimulus adds separate successful controls for each transaction,
then requires their combined workload to exhaust the unchanged shared budget.
Original drafts, failures, exact commands and explanations remain in author/ and
reviewer receipts. No production repair, relaxed assertion or altered old fixture
was needed. Final bounded additions cover all15forbidden NO_NEW payload bytes and
an actual completion crossing uint32 wrap. Sequence increment/preservation are
tested; exhaustive2^32sequence rollover was not executed.

## Evidence and remaining work

Exact commands, exits, timestamps and source hashes are under
P2_imu_acquisition_raw/; author/AUTHOR.md identifies final focused receipts.
The actual target collection is target_147e08b1_bench-default.json, independently
compared by root_target_integrity.json and reviewer source/ELF artifacts.
Read reviews/P2_imu_acquisition_review.md for reviewer scope and independence.

No upload/reset/MCU/I2C/pad or motor operation occurred. Last-known MCU image
remains inert QTR61d7a2d0. Physical identity/electrical setup, rate, axis mapping,
bias/drift/rotation and full-loop timing remain pending. SC-AJ clock qualification
and F091 inherited runtime limits remain deployment blockers. No PINMAP,
EXPLAINED, human phase gate or motor-run authorization follows.

Next real B3 task is the body-coordinate estimator, explicit observation presence,
bias and continuous-yaw/gap policy. The bounded read-only next_b3_audit.md explains
why merely adding calibration presence is insufficient: current imu_ok also
controls fallback and fresh yaw/acceleration evidence. Freeze those semantics
before actual HAL/core adapter changes; do not reuse cached samples as fresh.
