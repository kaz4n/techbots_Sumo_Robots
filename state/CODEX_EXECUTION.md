# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D075 permits actual P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and actual inert diagnostics | Optical/cold-start/pin/electrical acceptance and human gate |
| P1 | Reviewed core;1030 current host cases pass | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live matrix, physical polarity/ranges/60s, app invalid-sample policy |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Stand/integration, physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADC e6b7060; independent tests/target/review PASS | Physical divider/reference/0.05V accuracy and integration |
| P2 B3 | Native bus a749816; independent tests/target/review PASS | Checked MPU setup/decode, aggregate freshness, bias/yaw, physical B3 |
| P2 B2/B6 | Unfinished; established GPIO/ADC constraints | Real QTR/UI drivers and explicit acquisition semantics |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ clock/F091 platform limits, full scheduler/HAL/WCET, physical acceptance/per-run permissions |

D079:431 distinct tooling methods PASS across existing421 and native10 separate
runs; normalhost2/2 and sanitizer2/2 PASS. Independent native reviewer10methods/
83positive cases PASS plus4boundary regressions. Final f3e9b546 compile-only
81992/33788B exit0. F100 and P2_imu_bus_validation.md/raw/review retain failed
attempts, exact source/ELF receipts and limits. No upload/reset/MCU/I2C/pad action.

Next: implement finite checked MPU6050 setup and sensor-coordinate decoder from
P2_mpu6050_sample_audit.md. Freshness needs an explicit aggregate deadline and
status/shadow handshake; heading/calibration integration follows separately.
SC-AJ remains global and no runtime frequency lock or physical gate is claimed.
