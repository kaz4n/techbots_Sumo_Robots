# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D075 permits P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core, full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live matrix, polarity/ranges/60s, integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADCe6b7060; tests/target/review PASS | Divider/reference/0.05V accuracy, integration |
| P2 B3 | Bus/setup/acquisition7b46598/estimatorc1188b1; tests/target/review PASS | Explicit core presence/time routing; physical B3 |
| P2 B2/B6 | GPIO/ADC constraints established | Real QTR/UI drivers and acquisition semantics |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, scheduler/HAL/WCET, physical acceptance |

D082: P2_imu_heading_validation.md/raw, F104, separate review PASS. All jobs done.
Fullhost/sanitizer2/2 PASS;1093main+37enabledGate cases. Actual compile-onlya746b27b
79060/32208B exit0. Selected287tooling+new6 methods PASS (293distinct; scoped run).
No upload/MCU action; old core/app/locked tests unchanged.

Next: countdown presence/source-time admission, then heading/control/recording
routing from next_adapter_audit.md. Preserve all legacy locked assertions. SC-B
QTR cadence and SC-AJ/F091 deployment limits remain. Physical/human gates pending.
