# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 incomplete; explicitly RESUMED; no human gate passed.
D051/D075 permit active P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core; full host suites PASS | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, physical qualification |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Native ADCe6b7060 +D093ownera15cffd tested/target/review PASS | Divider/reference/0.05V accuracy, physical qualification |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/Robot2c16023 | D094fab551f resume tested/target/review; physical mounting/B3, physical qualification |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1327c5db/gesturesb69fa12/matrix385c46c/D093fixedowner tested/target/review | Physical buttons/SC-A, optical acceptance, physical acceptance |
| P2 2.4 | QTR calibration311bf40 tested/target/review | Actual threshold printing/app/physical calibration |
| P2 B8 | Storage/D090dump febde53 tested/target/review; D09117bb38a actual200s synthetic MCU recorder PASS | Native UART, app lifetime/local reset UI, physical B8 |
| Integration/B7/P3-P7 | D092timing2081ca1/D093a15cffd/D095390005c transaction tested/target/review | D0973d84958 + D0981447ec8; default candidate fits; D099/D100 target adoption reviewed; full800us/physical pending |

D0973d84958 passive IMU accessor implemented/tested/reviewed; real696B saving.
Fullnormal/san1418main+173Gate PASS. D0981447ec8 isolated Bridge dependency
experiment/review PASS,27452B saving: actual default248308B with493projectfunction
identities/startup preserved. Conditional loader arithmetic is not loadedRAM.

D099/D100 build policy accepted: corrected default/Immediate/MATCH builds PASS
at248308/248684B. Exact source/ELF/object/startup/import audits, library fixture
rejection and fresh same-model review PASS.46new+78established tooling tests
previously passed unchanged; no unnecessary rerun. Original control failure saved.
Read P2_app_build_validation.md and acceptance_review.md.

Current next P2 task: actual app dump attachment/terminal cancellation with
independent tests. Post-STOP local service reset/source lifecycle and calibration
snippet delivery remain explicit subsequent dependencies. No physical gate passed.

Lastknown MCU remains D0911502e948 synthetic recorder, seveninertkeys unchanged.
Physical acceptance, loadedRAM/full800us, SC-A circuit, SC-AJ clock, nativeUART/
localreset/calibration-snippet integration and human gates remain outstanding.
No extra hardware requested or motor authority; no push/tag. Commit promptly
without artificial spacing. Continue eligible software with actual evidence; never assume target success.
