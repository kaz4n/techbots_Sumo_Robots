# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS authoritative. Full P0-P7 goal ACTIVE/incomplete; no human gate passed.
D051/D075 permit P2 software while physical acceptance remains pending.

| Existing task | Software/evidence | Remaining |
|---|---|---|
| P0 | Toolchain/source audits and inert diagnostics | Physical/pin/electrical acceptance and human gate |
| P1 | Reviewed core, full host validation passes | EXPLAINED OK and human GATE P1 PASS |
| P2 B1 | Native opponent588ceb9; tests/target/review PASS | Live polarity/ranges/60s, app integration |
| P2 B4 | Gate1c45f72/native99f8668; tests/target/review PASS | Physical EN/PWM/reversal/B4/B7/WCET |
| P2 B5 | Actual ADCe6b7060; tests/target/review PASS | Divider/reference/0.05V accuracy, integration |
| P2 B3 | Acquisition7b46598/estimatorc1188b1/calibration5516bef/full Robot2c16023; tests/target/review PASS | Physical mounting/B3, app scheduler |
| P2 B2 | Native QTR/adapter/Robotfreshness47f4d9a; host/san/target/review PASS | Physical color/cadence, pad ownership, full WCET |
| P2 B6 | Core logical UI; optional A1 owner327c5db tested/target/review | Decoder/evidence routing/display; SC-A |
| P2 B8 | Offline storage/CSV25Hz implemented/reviewed | Bounded IDLE transport, full RAM/200s/no-gap evidence |
| Integration/B7/P3-P7 | Unfinished | SC-AJ/F091, scheduler/HAL/WCET, physical acceptance |

D086 evidence: P2_adc_pair_validation.md/raw, F108, fresh separate review PASS.
Fullhost/san2/2PASS1173main+37Gate; independent native15methods150positivecases/
1329parentassertions PASS,17config/25tools/2stagingPASS59distinctmethods.
Finaltarget5f2c232983912/34700B exit0;56sources/3ELFs/36native42AEABI checked.
Exactly5existing inert keys approved/adopted; no new upload entry. Failures and
source-time correction retained. No locked test/B16value or physical claim.

Next: actual B6 button decoder/evidence adapter and existing service routing,
per P2_adc_pair_raw/next_button_task.md. Freeze ambiguity/source identity/age/
absence/expiry semantics before implementation and independent tests. SC-A
START/BOTH identity remains; failed input must not imply NONE. App scheduling
must budget IMU600+motor150+twoADC100 and other work. SC-AJ/F091, physical/human
gates and original schedule remain. No additional hardware request now.
