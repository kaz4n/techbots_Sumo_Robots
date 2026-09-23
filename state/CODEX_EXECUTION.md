# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS.md is authoritative. Original goal ACTIVE after user resume. No human
phase gate passed. D-016 allowed P1 host work; D-068 now selects only offline B8
RAM storage under delegated D-051. No app/transport integration or phase pass.
D-052 bare-board authority remains separate; no new hardware connection request.

| Existing phase task | Status and evidence | Remaining dependency |
|---|---|---|
| P0 G1-G6/tooling/scaffold | SOURCE/INSTALLED-REVIEWED,317 controlled tool checks; FACTS and P0_*validation | Physical electrical acceptance, PINMAP OK |
| P0 matrix/counter/timing | Real counter4..11/56..63 and prior60000 scheduler samples; P0_counter_validation.md | Optical matrix and true cold default/Immediate checks |
| P0 ADC/GPIO/QTR timing | Measured setup-only diagnostics, reviewed; P0_adc/gpio/qtr_validation.md | Stock runtime wait hazards; real sensors/WCET absent |
| P0 G2/G6 compatibility | Actual never-called target compile probes660eb08/b7bd0df, reviewed | Runtime PWM/IRQ/I2C evidence remains separate |
| P0 gate | GATE-PENDING, reviews/P0_gate_request.md | Original physical evidence and human GATE P0 PASS |
| P1 core1.1-1.6 | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEWED;895corecases,10000Robot streams, actual inert target app; P1_robot_validation.md | EXPLAINED OK/human GATE P1 PASS |
| P2 B8 frame storage, D-069 | HOST-TESTED/REVIEWED f733c4e;25newcases;combined920/17033806 normal+ASanUBSan;317tools | No target RAM fit/app integration/transport claim |
| P2 B8 attempt owner, D-070 | HOST-TESTED/REVIEWED193bd33;49newcases;full969/17459867 normal+ASanUBSan,317tools PASS | SC-AH target-memory design; no runtime/transport integration |
| P2 remaining drivers/integration | NOT ACCEPTED/DEFERRED | Actual phase eligibility, API contracts, wiring/sensors and gates |
| P3-P7 | UNFINISHED | Original dependencies/measurements/human run and gate approvals |

First next task: resolve SC-AH with a scoped candidate memory design and
compile-only budget contract before a rate/representation/placement change.
25Hz is a specified conditional fallback, not yet selected or proven to fit.
F-089/P2_memory_budget_followup_20260923.md separates RAM estimates from upload
file size; include owner code, metadata, other HAL and peak/headroom evidence.
No workers or commands remain running. Preserve independent tests, original
locked tests and all failed receipts. No repeated completed diagnostics.

SC-A buttons,SC-B QTR timing/freshness,SC-I Bridge,SC-AG IMU runtime and ADC/PWM
API hazards remain explicit. SC-AH recorder default50Hz payload292794B exceeds
262144B installed extension pool; host292848B object size is not MCU fit. B15's
25Hz fallback is not yet adopted. B8 physical200s/free-RAM/dump acceptance absent.

Current MCU remains inert QTR source61d7a2d0/revisiondcca300/default/MOTOR0,
uploaded03:00:13.327+04. D-069/070 work has no board action. Latest five source guards were reviewed/refreshed in193bd33; this does not
mean the new source was uploaded. No STAND OK/RING OK, PINMAP OK or human phase pass.

No schedule cut due23September. Apply Sep28 reactive-core cut if P3 not passed,
Sep30 P6 eligibility,Oct1 21:00Dubai code freeze,Oct2 rehearsal/Oct3 competition.
Never manufacture evidence because a deadline arrives; no push/tag/release.
