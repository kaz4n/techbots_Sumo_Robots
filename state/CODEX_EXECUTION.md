# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D075 permits actual P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and actual inert diagnostics | Optical/cold-start/pin/electrical acceptance and human gate |
| P1 | Reviewed core; full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live matrix, polarity/ranges/60s, app invalid-sample policy |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Stand/integration, physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADC e6b7060; tests/target/review PASS | Divider/reference/0.05V physical accuracy and integration |
| P2 B3 | Bus/setup/acquisition7b46598; tests/target/review PASS | Observation presence, axes/bias/yaw, physical B3 |
| P2 B2/B6 | Unfinished; GPIO/ADC constraints established | Real QTR/UI drivers, explicit acquisition semantics |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, full scheduler/HAL/WCET, physical acceptance/per-run permissions |

D081 details: P2_imu_acquisition_validation.md/raw, F103, separate reviewer PASS.
Full cleanhost/sanitizer2/2 PASS;1071main cases plus37enabled MotorGate cases.
Actual compile-only147e08b1:86236/36172B exit0, no upload/MCU action.
Existing443tooling PASS678.339s,exit0;450distinct methods across separate runs.
All D081 jobs complete; no upload, reset or MCU operation.

Next: freeze/implement actual B3 body-axis
estimator plus explicit sample presence and continuous-yaw/bias/gap semantics.
Use next_b3_audit.md; changing calibration alone leaves stale heading/impact
reuse. No unknown mounting map becomes verified. SC-B requires independent QTR
cadence/freshness resolution; SC-AJ/F091 and human acceptance remain pending.
