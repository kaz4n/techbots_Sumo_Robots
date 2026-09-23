# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS is authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D075 permits actual P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and actual inert diagnostics | Optical/cold-start/pin/electrical acceptance and human gate |
| P1 | Reviewed core; 1030 current host cases pass | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent driver588ceb9, independent tests/target/review PASS | Live matrix, physical polarity/ranges/60s, app invalid-sample policy |
| P2 B4 | Gate1c45f72 + native backend99f8668; tests/target/fresh review PASS | Stand sketch/integration and physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Next: source prerequisites for concrete native ADC1/A0 | Complete targeted audit, freeze contract, implement/test/compile/review |
| P2 B2/B3/B6 | Unfinished; established GPIO/I2C/ADC constraints | Real bounded drivers and explicit QTR/UI acquisition semantics |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | Full scheduler/HAL/WCET, physical acceptance and per-run permissions |

Final D077: 410 tooling tests PASS432.397s; normal host2/2 PASS; sanitized
1030/20982541 plus37/3796846 PASS. Fresh native replay152/217368 PASS across
78 executables. Final c35726f4 default85052/35160B and enabled85588/35552B compile.
Evidence25a0858, P2_motor_native_validation.md/raw/review, F096/SC-AI.
No upload/reset/GPIO/MCU/motor action. Old locked/core/app unchanged; new native
safety tests now locked. All five inert hash replacements independently approved.

Next: read P2_next_hal_audit.md and P2_adc_native_audit.md/raw. Complete the narrow
ADC source/errata gap before actual B5 contract/code. No V_NOM fallback, stale-as-
fresh reading, extra governor filter or guessed initialization. Hardware pending
is not software success and does not require a new human question for source work.
