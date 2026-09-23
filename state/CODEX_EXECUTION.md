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
| P2 B8 | Storage/CSV25Hz and D090 bounded IDLE dump febde53 reviewed/tested/target-compiled | Actual loaded RAM/200s/no-gap/transport, app lifetime and local reset UI |
| Integration/B7/P3-P7 | Unfinished; D090 strong hook verified in target | SC-AJ, full scheduler/HAL/WCET/runtime, physical acceptance |

D090 febde53:1281main+65enabledGate normal/sanitizer PASS;26owner cases,
33receiver methods/18legacyconfig,11native methods/154normal+san scenarios,
56existingtools and4Windows publication/outcome PASS. Fresh separate same-model
review PASS. Actualb8bb9366target72exactsourcefiles/3ELFs;315332program/
238596compilerRAM(lowmemorywarning),40native42AEABI+fmod/sqrt, strongemptyhook
and actual main/startup inspected.6existinginertkeys reapproved. No upload.

D089 calibration311bf40 remains tested/reviewed; D088 last-known runtimeimage is
ui_matrixe50c6da3, prior counter+77/failures0. No currentruntimechange followsD090.
Next: review/freeze inert recorderbench contract using P2_recorder_bench_native_audit.
First prove actual elapsed200s synthetic recording/retention and bounded memory
facts; later native transport requires knownclean decoder. Nevercall zero stack
watermark export, inventheapstats, or silentlyrelax p0_capture16-read guard.
All SC-A buttonwindows/physical/humangates, SC-AJ/fullRAM/800us and fullapp remain.
