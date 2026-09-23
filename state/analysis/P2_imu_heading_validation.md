# D082 body-coordinate estimator validation

2026-09-23 Asia/Dubai. Contract `00f0cc2`; implementation `c1188b1`.
IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / separate same-model review PASS.
No physical mounting, accuracy, loader/runtime, WCET or phase acceptance follows.

The actual Estimator requires a confirmed proper signed axis map, separates new
gyro/acceleration from retained heading, integrates continuous unwrapped yaw with
double trapezoidal arithmetic, and applies bias only to future increments. No
physical mapping was selected. Observed completion times approximate sample time;
the explicit 2000 us continuity limit is a development policy, not measurement.

| Validation | Actual result / receipt |
|---|---|
| Independent spec-derived author | 22 cases / 64,370 assertions; six new tooling methods PASS 16.974 s; ten config variants, 10,000-observation allocation/I/O exercise, both inert probes, eight upload refusals; author/ |
| Independent fresh-context reviewer | Normal and ASan/UBSan each 22 / 64,370; six methods PASS 11.682 s; 28 nested subprocesses all exit0; 15 strict config checks; reviews/P2_imu_heading_review.md and raw/ |
| Root full host | tools/test_host.sh, 2/2 PASS 8.01 s, exit0; host.json/txt |
| Root full sanitizer | 2/2 PASS 22.61 s, exit0; 1093 main cases / 22,645,776 assertions plus 37 enabled MotorGate cases / 3,796,846 assertions; sanitize_build/tests.json/txt |
| Affected existing tooling | 287 selected methods PASS 186.964 s, exit0; tooling_selection.json and tooling_regression.json/txt |
| Actual UNO Q Linux compilation | --compile-only, CLI1.5.1/core1.0.0/arduino:zephyr:unoq, MATCH0/MOTORS_ALLOWED0/default startup; 79060 B program / 32208 B compiler globals, exit0; target_initial.json/txt |

There are 293 distinct methods across the selected287 and new6 runs; the15 config
methods are already within287. This is not a new complete all-tooling run. D081's
complete prior regression remains separately recorded. Existing core/app/locked
tests, MPU setup/acquisition/native transport and board wrapper were unchanged.

Actual target aggregate:
`a746b27b7628deaca5b809d0ecdf333b27d98b7c7d50d0a26e299ea5942779af`.
All48 staged source files and three ELF identities are retained. Offline symbol
checks cover36 native exports and42 math exports, including ten numerical helper
routes used by Estimator::publish. Root source/math comparison and reviewer
startup/binding audit pass. These prove offline binding consistency, not executed
loader success or numerical timing. Probe setup only stores a function pointer;
loop is empty, default mounting unconfirmed and Estimator remains NOT_STARTED.

Exactly five existing inert-source manifest identities were reviewed/adopted;
no upload key/permission was added. Root verified six reviewer command-output
hashes and the315-file snapshot: only the subsequent, separately approved manifest
adoption differs. root_review_integrity.json and manifest_adoption.json retain it.
All13 author final source hashes also match current bytes.

Preserved unsuccessful evidence: ten author configuration compiles initially
failed because its test-only -DVALID collided with Presence::VALID; renaming to
D082_EXPECT_VALID changed no assertion or compiler policy. The target collector
initially stripped __real_ from installed export names and falsely reported42
missing math bindings. Literal-name lookup and actual bare-wrapper disassembly
fixed that evidence collector; original/intermediate receipts remain. No production
fix or target rebuild followed the collector correction. No full2^32 sequence
rollover or forced float-maximum accumulator overflow was dynamically exercised;
the reviewed defensive arithmetic is not claimed as executed boundary coverage.

All raw paths above are under state/analysis/P2_imu_heading_raw unless indicated.
No upload/reset/MCU/register/pin/sensor/motor action occurred. Last-known MCU image
remains inertQTR61d7a2d0. SC-AJ/F091, actual mounting, B3 drift/rotation/time, P0/P1
human acceptance and all physical gates remain pending. Original schedule stands.

Next: explicit observation presence/source time through countdown calibration and
heading/control consumers, using next_adapter_audit.md. Do not wire retained
heading into the existing combined imu_ok path or turn absent data into readings.
