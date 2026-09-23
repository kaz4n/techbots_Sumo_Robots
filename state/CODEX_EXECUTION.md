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
| Integration/B7/P3-P7 | D092timing2081ca1/D093a15cffd/D095390005c transaction tested/target/review | SC-AL app transaction/resource schedule, full800us, physical acceptance |

D095 contractc17f6d6/implementation390005c: actual fixed Transaction, real S/D/A/C
and one Robot/Gate/recorder; terminal halt invalidates ordinary receipt, preserves
evidence, no fabricated tick/reset. FinalSTOP needs real tail. B14overrunlogonly.
Fullnormal/san1377main/25118683+139Gate/4467720 PASS; author28newcases617259/617260,
probe2/9eachmode,8newtools61oldtools; freshreview47703checks eachmode PASS/noopen.
Original new-test/worker/harness failures preserved; no establishedtests/core/config
change. New9lockedhaltcases established.80compiledsources113rawfiles indexexact.
Evidence: P2_app_transaction_validation.md/raw, reviews/P2_app_transaction_review.md.

Target9d6c0005:80files3ELFs;188imports/loader unchanged;40native42AEABI exports,
13initentries/passive startup including actualmain inspected.149120program238628
globals23516nominalremaining/lowRAMwarning; not fullapp/loadedRAM. Sevenexisting
inertkeys independentlyreviewed/refreshed; no newkey/upload/reset/MCU action.
LastknownMCUimage remains old D0911502e948 frozen synthetic recorder only.

Next: native source/resource scheduling contract then independent tests and actual
implementation using Transaction. Read P2_app_schedule_dependencies.md and D084/
D092/D093/D094/D095 contracts. Own actual setup, QTR sub-tick service, IMU600us
across callerwork, ADC grants, honest expiry, one decision and output/faultcleanup
inside S..C. app.ino remains inert. No scheduler/grants/new timing allowances yet.

SC-AL, SC-A circuit/windows, SC-AJ physicalclock, sensor/motor acceptance,
nativeUART/localreset, loadedRAM/full800us and human gates OPEN. No more hardware
requested; no motor authority/PINMAP/EXPLAINED/push/tag. Commit promptly after
validation; no artificial spacing. FullP0-P7 remains ACTIVE/incomplete.
