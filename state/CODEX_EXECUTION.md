# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D051/D075 permit active P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core, full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, app integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADCe6b7060; tests/target/review PASS | Divider/reference/0.05V accuracy, integration |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/Robot2c16023 | Physical mounting/B3, app scheduler |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1 owner327c5db; gesturesb69fa12; matrix385c46c tested/target/review/inert run | Physical buttons/SC-A, optical acceptance, service consumers |
| P2 2.4 | QTR calibration311bf40 tested/target/review | Actual threshold printing/app integration/physical calibration |
| P2 B8 | Storage and D090 bounded IDLE dump febde53 reviewed/tested/target-compiled; D09117bb38a synthetic200s actual MCU recorder PASS | Native UART transfer, app lifetime/local reset UI, physical B8 |
| Integration/B7/P3-P7 | Mapping saved; D090 strong hook verified | SC-AK timing, scheduler/HAL/full800us/runtime, SC-AJ, physical acceptance |

D090 fullnormal/sanitizer1281main+65enabledGate PASS;26owner/33receiver/11native
methods,56existingtooling and4Windows checks PASS. Actualb8bb9366target verified;
no D090 upload. D091 software17bb38a adds11Runner cases normal+san,28heap methods,
51capture methods and5controlled upload methods PASS;56existingtools PASS.

D091 exactsource1502e948/ELFeff3e050/ZSK0448e3ac uploaded once, source/artifacts
reviewed. Real MCU-clock200000998us from release toSTOP; full5100000us hold;
5001frames/8events/CRC900325728 independently extracted. No recorder loss or
active motor callbacks; absent-IMU calibration rejection is explicitly logged.
Runner maximum203us excludes fullHAL/wrapper. Loaded LLEXT free payload25116B,
largest21604B; sampled stack headroom31208B. Point-in-time/sampled limits apply.

Capture1 timeout preserved; smaller flash reads succeed with original ceilings:
47reads/934892B/51commands/281.633s. Firmware unchanged during readback. Board left
frozen in inert recorder1502e948. Evidence/review: P2_recorder_bench_validation.md,
P2_recorder_bench_review.md and raw runtime_retry1/. MEM-AP extraction, not UART.

Next: resolve SC-AK under D051 with additive public acquisition-start contract,
independent tests and timing implementation; see P2_app_integration_map.md.
Then app owner/native scheduling. No additional hardware requested now.
SC-A physical button circuit, SC-AJ time, fullRAM history/800us and human gates
remain open. No motor-run authority, push/tag, or phase approval inferred.
