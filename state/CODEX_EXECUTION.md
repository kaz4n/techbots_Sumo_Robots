# Execution checklist: P1 host development; hardware acceptance pending

PROGRESS.md is the phase/gate authority. D-016 permits offline P1 development.
No human gate has passed. No board contact, target compile, upload/reset or motor
run has occurred. The active user goal defers hardware testing to the end; its
results remain pending, not assumed successful. Date:2026-09-22, Asia/Dubai.

| Existing task | Status | Evidence and remaining dependency |
|---|---|---|
| Kickoff role migration | IMPLEMENTED | D-015, AGENTS, CODEX_HANDOFF; baseline52b935e preserved |
| P0 0.1 G1-G6 | SOURCE-REVIEWED | P0_G*.md; FACTS throughF-061; installed/electrical checks pending |
| P0 0.2 scripts | SCRIPT-TESTED |48 controlled checks in latest *_tools.txt; no successful board build claimed |
| P0 0.2/0.4 inert demos/timing | PARTIAL / HARDWARE-PENDING | RAM timing/matrix host checks; round trip/startup/WCET/GPIO/QTR/ADC/I2C measurements absent |
| P0 0.3 host scaffold | HOST-TESTED | CMake/doctest2.4.12, all76 B16 defaults preserved |
| P0 0.5 pin map | BLOCKED | Physical electrical checks and PINMAP OK; no pins assigned in config |
| P0 gate | GATE-PENDING | P0_gate_request.md prepared; physical evidence and human gate absent |
| P1 1.1 interfaces | PARTIAL | types/countdown/edge/opp_fusion/governor/motion/logframe; stall/openers/fsm remain |
| P1 1.2 B3 | HOST-TESTED components | Gate/Buttons/Controller +Services;56 locked countdown cases; production service/bias/heading-reset wiring pending |
| P1 1.2 B4 | HOST-TESTED components | Classifier/Guard/forward demands;16 locked edge cases; scripts/replanning/acquisition pending |
| P1 1.2 B5 | HOST-TESTED components | Debouncer/front table +BearingMemory/Contact; phantom/stuck and full fusion composition pending |
| P1 1.2 B6 | HOST-TESTED | Governor final cap/slew/compensation; FSM target-loss brake/profile selection pending |
| P1 1.2 B7 | HOST-TESTED | Turn/Straight/Arc/Brake; bounded fallback and cumulative deadlines; scripts/FSM integration pending |
| P1 1.2 B15 | HOST-TESTED encoding |25-byte frames/8-byte exact-tick events; storage/cadence/dump not implemented |
| P1 1.2 remainder | UNFINISHED | Stall/re-flank, escape/openers, Robot FSM and B14 integration |
| P1 1.3 properties | PARTIAL | Three10000-stream countdown sets; two10000 motion sets;10000 fusion samples; full Robot R1/R5 and all-script symmetry pending |
| P1 1.4 architecture | PARTIAL | ARCHITECTURE describes actual components; full FSM diagram/explanation still pending |
| P1 1.5 target compile | HARDWARE-PENDING | No connected/verified UNO Q toolchain |
| P1 1.6 review/gate | SCOPED PASS / GATE-PENDING | Separate read-only component reviews; full fresh gate review, EXPLAINED OK and human GATE P1 PASS absent |

Latest host result:212 cases/6,089,047 assertions, normal and ASan/UBSan pass.
No failures/skips. Final current-source tooling run:48/48; rerun receipt
is P1_opp_memory_contact_tools.txt. Source/test receipts and reviews are linked
in P1_opp_memory_contact_validation.md; earlier182-case evidence is preserved.

Approvals: D-017 governor; D-018 ordering; D-019 release anchor; D-020 persistent/
all-white guard; D-021 forward0.80; D-022 heading correction; D-023 duty-only
compensation; D-024 services; D-025 ALL_IN safety; D-026 bearing memory; D-027
contact lifetime; D-028 explicit overflow. Do not re-request them. ALL_IN and
recorder overflow are approved policies awaiting their actual implementations.

Next eligible task: P1 B5.5/B5.6 phantom and stuck-sensor contracts/tests, then
remaining stall/escape/openers/FSM work. Resolve genuinely missing behavior via
spec_conflicts before dependent changes. Preserve all established locked tests.
SC-A physical button decoding, SC-B QTR cadence/freshness, SC-I bounded log demo,
SC-J both-held STOP/recovery, escape exhausted-replan direction and WAIT geometry
remain explicitly open. D-016 alone does not authorize P2 HAL work.

Hardware resumes through docs/P0_MANUAL_CHECKLIST.md when connected: obtain SSH
alias/user and isolation/part/instrument details, run read-only preflight, inspect
installed versions and F-061 loader ownership, then perform reviewed inert checks.
No passwords/private keys in tracked files; no motor-capable upload/run without
fresh specific STAND OK/RING OK. A source change invalidates inert snapshot hashes
until separate review. See CODEX_HANDOFF and CODEX_RESUME for full resume order.
