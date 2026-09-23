# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 incomplete; explicitly RESUMED; no human gate passed.
D051/D075 permit active P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core; full host suites PASS | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9 and D107 named bench; host/checked default+Immediate target/review PASS | Live polarity/ranges/60s, physical qualification |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Native ADCe6b7060 +D093ownera15cffd tested/target/review PASS | Divider/reference/0.05V accuracy, physical qualification |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/Robot2c16023 | D094fab551f resume tested/target/review; physical mounting/B3, physical qualification |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1327c5db/gesturesb69fa12/matrix385c46c/D093fixedowner tested/target/review | Physical buttons/SC-A, optical acceptance, physical acceptance |
| P2 2.4 | QTR calibration311bf40 +D105 actual app delivery2eb97cc/receiver36ae9bc; D106 target fit6471204 | Physical calibration and actual UART receive |
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

D101 actual Runtime dump + D102 lossless frame/status packing tested/reviewed.
Fullnormal/san1434main+178Gate PASS; actualRuntime dump bytes unchanged. Source
3bf0da00 MATCH254156B, conditional loaderpeak258768B/largest3372B: D101-R1 modeled
capacity blocker CLOSED. All5001frames/4096events/25Hz retained. Same7inertkeys
reviewed/refreshed. Read P2_frame_packing_validation.md/targetaudit/review.
D103 optional local service-only reset tested/reviewed: fullnormal/san1443main+
187Gate,34 independent configured cases and4 strict Runtime dump roundtrips PASS.
Final1fbd7238 default/MATCH modeledpeaks261056/261448 fit with1088/696B remaining.
D1041fa2a01 actualbareprobePASS:200001epochs/0misses/maxS..C269us,allinhibited;
free28668B/largest25172B/sampledstack30952B. Exact2bd817c4 identities and stable
capture verified. Next: calibration snippet delivery, then namedP2bench software.
No physical gate passed. Read P2_service_reset_validation.md and next probe scope.

Lastknown MCU is frozen D1042bd817c4 actualRuntime absent-source probe.
Old7keys unchanged; one reviewed exactprobe key added.
Physical acceptance, full-app loadedRAM/full800us, SC-A circuit, SC-AJ clock, nativeUART/
physical localreset/calibration-snippet integration and human gates remain outstanding.
No extra hardware requested or motor authority; no push/tag. Commit promptly
without artificial spacing. Continue eligible software with actual evidence; never assume target success.

D105 actual calibration delivery2eb97cc and strict receiver36ae9bc are complete
in software: independent normal/sanitizer/active-Gate tests and source review PASS.
D106 deduplicates the installed native pin table; exactd72bff70 three-profile
compile/loader/import/startup review PASS closes D105-R2, with default/Immediate
remaining span456B and MATCH2088B. Native27+26methods PASS; unchanged old registry
assertions pass through the new additive D096 wrapper. No upload or physical claim.
Read P2_pin_table_validation.md and its final review for precise limitations.

D107 named opponent bench is implemented/host-tested/target-reviewed. Checked
332787f0 default/Immediate peak4496; generic artifacts rejected and retained.
All hardware grants false; no upload allowlist addition. D108 corrects geometric
front display ordering: fullnormal/san1446main+187Gate and exact618d3a96 app
default/MATCH target/review PASS (138e32e). D109contract/interfaces/config128
adoptedf786fa5. Bounded one-Reader capture implementation and independent tests
are in separate parallel contexts; exact policy7new+100old methods and separate
review PASS. Firmware tests/target/review remain active. No extra hardware requested.
