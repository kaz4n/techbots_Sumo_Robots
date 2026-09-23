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
| P2 B6 | A1 owner327c5db; decoder/gesture/event routingb69fa12 tested/target/review | Matrix rendering/native output, physical buttons/SC-A, service consumers |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, scheduler/HAL/WCET, physical acceptance |

D087 evidence P2_button_routing_validation.md/raw, F109, separate reused same-model
reviewPASS/no openfinding. Fullhost/san2/2PASS1209main+38Gate; independent36cases/
8newmethods,18config25tools2stagingPASS53distinctmethods. Final557e0target142288/
69864B59sources/3ELFs and59exactGitblobs verified.5existing inertkeys approved;
no new uploadkey. Initial failures/normalization correction preserved.

Next: actual104-byte matrix renderer and bounded native output per
P2_button_routing_raw/next_ui_task.md. Freeze precise display policies beforetests.
SC-A raw windows remain unconfigured; hardware testdeferral does not resolve
identical START/BOTH input. App timing must budget IMU600+motor150+twoADC100 and
allotherwork; no800us claim. SC-AJ/F091 and allphysical/humangates remainpending.
