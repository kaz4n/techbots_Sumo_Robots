# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 ACTIVE/incomplete; no human gate passed.
D051/D075 permit active P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core; full host suites PASS | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, app integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Native ADCe6b7060 +D093ownera15cffd tested/target/review PASS | Divider/reference/0.05V accuracy, app scheduler |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/Robot2c16023 | D094fab551f resume tested/target/review; physical mounting/B3, app scheduler |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1327c5db/gesturesb69fa12/matrix385c46c/D093fixedowner tested/target/review | Physical buttons/SC-A, optical acceptance, service consumers |
| P2 2.4 | QTR calibration311bf40 tested/target/review | Actual threshold printing/app/physical calibration |
| P2 B8 | Storage/D090dump febde53 tested/target/review; D09117bb38a actual200s synthetic MCU recorder PASS | Native UART, app lifetime/local reset UI, physical B8 |
| Integration/B7/P3-P7 | D092timing2081ca1/D093a15cffd tested/target/review; strong hook verified | SC-AL app transaction/resource schedule, full800us, physical acceptance |

D094 contracte507c42/implementationfab551f: bounded native Bus/Acquirer progress,
original600us/8192 across caller work, separate pending and terminal-once. D093
ADC owner remains a15cffd. Fullnormal/san1349main/24501424+111Gate/3850460 PASS;
independent22/17259eachmode,21native/728parent,44legacy/932parent,probe/refusals and
61tools PASS. Freshsame-model review4/48native +2/156Acquirer PASS/no open findings;
one MAJOR fixed. All failures and new-test clarification preserved. Evidence:
P2_imu_resume_validation.md/raw and reviews/P2_imu_resume_review.md/raw.

Targetb495f085:78current/staged/target/indexsources/3ELFs;108rawfiles indexexact.
330844program247564globals14580nominalremaining/lowRAMwarning.188imports/loader
unchanged;40native42AEABI nonzero.13init-array entries/passive startup inspected.
Sevenexisting inertkeys reviewed/refreshed; no newkey/upload/reset/MCU operation.
LastknownD0911502e948 remains the old frozen synthetic recorder image only.

Next: fixed app transaction/resource-admission public contract under D051; read
P2_app_schedule_dependencies.md D094 map. Then independent tests/implementation.
Own truthful setup, QTR sub-tick service, IMU progress, ADC grants, bounded retained/
expired evidence, one Gate application/recorder and all fault cleanup inside D092
complete intervals. No D095/scheduler policy/timing allowance selected yet.

SC-AL schedule, SC-A circuit/windows, SC-AJ clock, physicalsensor/motor, nativeUART,
loadedRAM/full800us and human gates remain OPEN. No more hardware requested now;
no motor authority/PINMAP/EXPLAINED, push/tag or phase approval.
