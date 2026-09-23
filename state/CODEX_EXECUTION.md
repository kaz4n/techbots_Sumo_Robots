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
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/Robot2c16023 | Resumable runtime service, physical mounting/B3, app scheduler |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1327c5db/gesturesb69fa12/matrix385c46c/D093fixedowner tested/target/review | Physical buttons/SC-A, optical acceptance, service consumers |
| P2 2.4 | QTR calibration311bf40 tested/target/review | Actual threshold printing/app/physical calibration |
| P2 B8 | Storage/D090dump febde53 tested/target/review; D09117bb38a actual200s synthetic MCU recorder PASS | Native UART, app lifetime/local reset UI, physical B8 |
| Integration/B7/P3-P7 | D092timing2081ca1/D093a15cffd tested/target/review; strong hook verified | SC-AL resumable IMU, app transaction/resource schedule, full800us, physical acceptance |

D093 contractd248782/implementationa15cffd: one A0/A1 owner,10ms battery period,
strict<20ms retained source age, shared reset-only faults. Native fresh-only API,
original B16 values/governor and established tests unchanged. Fullnormal/san each
1327main/24484165assertions +111Gate/3850460 PASS. Independent24/2421eachmode,
actualnative/config/probe/limits/registry/refusal PASS;61existingtools PASS; fresh
review6/20059normal+san PASS/no findings. Evidence P2_power_inputs_validation.md
and reviews/P2_power_inputs_review.md. Newharnessfailures preserved/corrected.

Actualtarget4d5e21cc76current/staged/target/indexfiles and3ELFs exact,40native42AEABI
exports/loader/188imports unchanged. Compiler321652program/241524globals,20620
nominalremaining/lowRAMwarning.56rawblobs indexverified. Sevenexistinginertkeys
reviewed/refreshed, no newkey or upload. Last deployed D0911502e948 remainsfrozen;
its5001frames/8events/CRC900325728,200000998us and25116Bfreepayload apply onlyto
that prior synthetic MCUrun. No D093MCU/sensor/motor/UART action or physicalgate.

Next: SC-AL audit bounded resumable native IMU and freeze public contract under
D051 before app scheduler. P2_app_schedule_dependencies.md records synchronous
read, QTR sub-tick service, extra MotorGate settle on failure and IMU cleanup
outside source timestamp. Preserve600us aggregate deadline/polls, cleanup and
freshness across all advances; no pending-as-new sample. No D094/new API/timing
allowance selected yet. Count every executed service inside D092 complete timing.

SC-A circuit/windows, SC-AJ clock, physicalsensor/motor, loadedRAM/full800us,
physical B8/nativeUART and human gates remain OPEN. No more hardware requested
now; no motor authority/PINMAP/EXPLAINED, push/tag or phase approval.
