# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 ACTIVE/incomplete; no human gate passed.
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
| Integration/B7/P3-P7 | D092timing2081ca1/D093a15cffd/D095390005c transaction tested/target/review | D0963be9669 host-tested; target RAM BLOCKER14312B; full800us/physical pending |

D096 contract36c251f/implementation3be9669: actual Runtime/native bindings/app
composition, original release grid, actual source expiry, RAW calibration/handover,
and real STOP tail now implemented. All setup grants remain false by default.
Fullnormal/san1411main+173Gate pass; author37default/43configured cases eachmode,
6newtools61oldtools, reviewer131711checks eachmode PASS. Clock and QTR starvation
findings fixed; no old core/HAL/locked-test change. Exact82compiledsources250rawfiles
and5newtests verified in index; original failures retained.

TARGET BLOCKER: final actualapp4cb637f9 compileexit1,276456memory>262144/14312B
excess.82sources3linkedcacheELFs exact,188imports/loader unchanged,40native42AEABI
exports12initentries audited; this is not a successful target build. Sevenexisting
inertkeys reviewed/refreshed, no appkey/upload/reset/MCU action. Lastknown image
D0911502e948 old frozen synthetic recorder only.

Next: bounded passive Acquirer setup-fault accessor to remove accidental legacy
runtime retention; public contract/independent tests first, preserve legacy API.
Then sameapp compile-only/ELF comparison measures real saving (752B estimate only,
insufficient alone). Investigate inherited Bridge/Serial dependencies with isolated
source/ELF startup comparisons; no core/toolchain/startup/capacity change assumed.
Read P2_app_runtime_ram_audit.md. Do not claim a RAM remedy from symbol totals.

SC-AL full800us, SC-A circuit/windows, SC-AJ clock, physical acceptance, loadedRAM,
nativeUART/localreset/calibration-snippet transport and human gates remain pending.
No extra hardware requested, motor authority/PINMAP/EXPLAINED, push/tag. Commit
promptly after validation; no artificial spacing. FullP0-P7 remains ACTIVE.
