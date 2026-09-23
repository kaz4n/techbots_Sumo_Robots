# Execution checklist -2026-09-23 Asia/Dubai

PROGRESS authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D051/D075 permit P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core, full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, app integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADCe6b7060; tests/target/review PASS | Divider/reference/0.05V accuracy, integration |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/full Robot2c16023 | Physical mounting/B3, app scheduler |
| P2 B2 | QTR/adapter/Robot47f4d9a tested/target/review | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | A1 owner327c5db; decoder/gestureb69fa12; matrix385c46c tested/target/review/inert-board-run | Physical buttons/SC-A, optical acceptance, service consumers |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, scheduler/HAL/WCET, physical acceptance |

D089 implementation311bf40: actual QTR_CAL owner/adapter/Robot handover,
atomic RAM bank/export and matrix progress IMPLEMENTED/HOST-TESTED/TARGET-COMPILED.
Full normal/san1255main+39GatePASS;31newcases1915assertions.4scoped tooling methods
(including18legacy config cases), alternate confirmation/batch profiles and
25existing scripts+5matrixupload+2staging PASS. Fresh same-model reviewPASS after
source-era MAJOR fixed. Finalcc4819aa67sources/3ELFs/40native42AEABI exact; six
existing inert hashes refreshed. No upload or physical calibration this turn.

Last-known MCU: D088 inert ui_matrixe50c6da3, prior measured counter+77/failures0.
All optical/independentclock/full800us/physical/button/human gates remain pending.
QTR_CAL still needs actual app lifetime/acquisition selection and print transport.

Next: P2 B8/B13/B15 actual bounded IDLE log-dump owner/transport. Read
P2_service_next_task.md, resolve STOPPED-to-IDLE RAM lifetime and native Bridge
boundedness before implementation. SC-A production windows stay unconfigured;
SC-AJ/F091/full RAM/tick budget and physical/human gates stay explicit.
