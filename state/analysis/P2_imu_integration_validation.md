# D084 estimator-to-Robot validation

2026-09-23 Asia/Dubai. Contract/interface aef3be2; implementation/tests 2c16023.
IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / fresh separate review PASS.

The actual Estimator now maps through applyEstimate to Robot admission, countdown
calibration, HeadingReference, Fusion, motion, stall, escape and delayed recording.
Bounded retained yaw remains useful for steering without becoming a fresh gyro or
acceleration observation. Replay suppression, actual source times and saturating
history age prevent repeated impact/calibration evidence or clock-wrap revival.
The existing 25-byte frame carries explicit presence codes without changing its
offsets; legacy callers and flag validation remain compatible. No old test or
config value was changed. The application scheduler remains unfinished.

| Check | Actual result and receipt |
|---|---|
| Independent spec/header-derived author | 27 cases / 165477 assertions each normal and ASan/UBSan; 5 tooling methods PASS29.197s; raw/author/HANDOFF.md and final_receipt_summary.json |
| Fresh separate same-model reviewer | 118 new/established cases /1727511 assertions each normal and ASan/UBSan;5 tooling and15 config methods PASS; reviews/P2_imu_integration_review.md and raw |
| Full root host | tools/test_host.sh, 2/2 PASS6.39s, exit0; raw/root_host_final.json/txt |
| Full root sanitizer | 2/2 PASS31.38s, exit0; 1151 main cases / 22813536 assertions plus37 enabled MotorGate / 3796846; raw/root_sanitize_build_final and root_sanitize_tests_final.json/txt |
| Staged public headers/core | 2 methods PASS2.722s, exit0; raw/root_staged_core.json/txt |
| Script safety/staging |25 existing tooling methods PASS14.709s after exact reviewed manifest adoption; raw/root_tools_final.json/txt |
| Actual UNO Q Linux compile-only | CLI1.5.1/core1.0.0, arduino:zephyr:unoq, MATCH0/MOTORS_ALLOWED0/default startup; 135536B program,66352B compiler globals, exit0; raw/target_initial.json/txt |
| Offline target identity | All51 source files and3ELFs match;36 native exports and42 AEABI math exports bind to installed base; additional fmod/sqrt bindings checked; raw/root_target_integrity.json, target_f3bc1f7f_bench-default.json and target_additional_math.json |

The existing27 staging/tooling methods plus5new are32distinct scoped methods.
This is not a complete rerun of every historical native/tooling suite.

Raw paths above mean state/analysis/P2_imu_integration_raw. Commands preserve exact
arguments, timestamps, outputs and return codes. Compiler memory is not measured
free RAM or proof that the final integrated recorder fits.

Independent tests use the actual estimator/adapter/Robot with matched synthetic
application receipts. The seeded5400-tick stream covers bias, horizontal rails,
retained observations, full hold, edge and STOP. Both inert probe macro modes
execute constructors/setup/10000 empty loops with allocation guarding active
before static initialization. Another10000 actual estimator/adapter/Robot
transactions show no allocation or I/O within that harness. Eight upload requests
are refused before transport lookup. These are host/software checks, not physical
measurements, successful upload or proof of complete tick WCET.

Actual target aggregate:
`f3bc1f7f7fac3f027d5daa2cdcadc9981acfc14d9d3c3f130946ed6c4e2fcb55`.
Setup0x6c stores an unused entry pointer; loop0x7c returns; initializer0x2490 has
stores and no computation call. The probe retains actual Robot/adapter/consumer
and codec paths. Inherited Bridge/Serial/loop-hook behavior remains F091.
The reviewer independently checked329 frozen source/test files, all51 staged
sources/3ELFs,20 retained AEABI wrappers and supplemental fmod/sqrt routes. No open
findings remain in this software scope. Exactly five existing inert identities
were approved and independently reproduced/adopted; no new upload key was added.
This is a separate same-model review, not cross-model or human gate acceptance.

Preserved findings and corrections:

- Early reviewer found contract_valid=false was checked only in explicit mode.
  Enforce the frozen contract in both modes; add a new independent legacy-false
  regression. Existing defaults and established tests remain unchanged.
- The initial independent real-estimator stream and allocation fixture omitted
  D082's NO_NEW BusStatus::OK and unchanged sequence. Both focused executables
  compiled;26/27 cases passed before the fixture correction. Three failed command
  receipts remain. Correct the fixture, preserving its assertions; final runs pass.
- Reviewer found the probe allocation guard initially began in main. Constant
  initialization now enables it before global constructors, with a pre-setup zero
  assertion. This strengthens the new test; no old test is changed.
- Target review requested additional fmod/sqrt bindings beyond the42 AEABI exports.
  Collect them from the same installed base/upload ELF without recompilation.
  The first outer command receipt name collided with the detailed JSON filename;
  preserve that command receipt as target_math_initial_command.json and repeat the
  read-only collection under distinct target_math_final_command receipt names.
- The reviewer's initial binding parser assumed every imported AEABI helper had a
  retained wrapper. Preserve its failed receipt; distinguish unused imports from
  the20 retained wrappers and verify their actual relocations. No production or
  test expectation changed to repair that evidence-tool assumption.
- A final root snapshot check initially expected all329 review files unchanged
  after intentional resume and approved-manifest updates. Preserve that failed
  assumption receipt. Final check confirms327 identical files, only those two
  metadata changes, exact approved manifest values and all production/tests intact.

No upload, reset, MCU/pad/sensor/motor action occurred. Last-known MCU image remains
inertQTR61d7a2d0. Physical mounting, drift/accuracy/read time, SC-AJ clock qualification,
F091 runtime paths, PINMAP/EXPLAINED and all human gates remain pending. No schedule
or acceptance threshold changed. Full P0-P7 objective remains active/incomplete.

Next concrete software work: B2 QTR acquisition and freshness contract, then the
actual bounded native driver and independent tests. Read raw/next_hal_task.md and
the existing P0 QTR/IRQ audits. Preserve10us charge and1500us timeout; no blocking
full-timeout read inside a1ms tick. A cooperative acquisition owner alone does not
resolve service cadence, observation uncertainty or Robot freshness admission.
The600us IMU budget must enter that analysis; do not promote pending/old line data
to a new complete sensor snapshot. UI A1 also needs a single ADC owner and a real
resolution of START/BOTH electrical ambiguity. No hardware request is needed now.
