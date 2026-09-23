# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D051/D075 permit P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core, full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, app integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADCe6b7060; tests/target/review PASS | Divider/reference/0.05V accuracy, integration |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/full Robot evidence2c16023; tests/target/review PASS | Physical mounting/B3, app scheduler |
| P2 B2/B6 | GPIO/ADC constraints established | Actual QTR/UI and freshness semantics |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, scheduler/HAL/WCET, physical acceptance |

D084: P2_imu_integration_validation.md/raw, F106, fresh separate review PASS.
All jobs complete. Fullhost2/2PASS6.39s/fullsan2/2PASS31.38s;
1151main+37enabledGate cases. Actual compile-onlyf3bc1f7f135536/66352B exit0.
51sources/3ELFs/native/math/startup checked. Selected27existing+5new tooling PASS.
No upload/MCU operation, old locked test or config value change.

Next: B2 native QTR acquisition contract/driver and explicit freshness policy.
Read P2_imu_integration_raw/next_hal_task.md and existing QTR/IRQ evidence. Preserve
10us/1500us; model release/read uncertainty and service gaps. A nonblocking driver
alone does not solve SC-B/Robot sample admission or600us IMU contention. No stale
line data as fresh; no app integration assumption. SC-AJ/F091, physical/human gates
remain pending. Do not ask for more connected hardware now.
