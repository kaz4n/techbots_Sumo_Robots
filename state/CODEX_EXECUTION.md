# Execution checklist: P1 host development; hardware acceptance pending

**PAUSED by explicit human request, 2026-09-22.** No work continues in the background.
On resume: implement B8 SEARCH under newly accepted D-041/D-042, then re-flank
under D-040/D-043. D-044/45/46 approve head-on values and normal-arbitration details.
The prior next-task and pending-choice paragraphs below are superseded by this
checkpoint and the final resolution entry in analysis/spec_conflicts.md.

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
| P1 1.1 interfaces | PARTIAL | Existing core modules plus Flank/DefendTurn; remaining scripts/Robot contract pending |
| P1 1.2 B3/B13 | HOST-TESTED components | Gate/Buttons/StopHold/Controller +Services; production service/bias/heading-reset/menu wiring pending |
| P1 1.2 B4 | HOST-TESTED components | Classifier/Guard/forward demands plus nine selected RowExecutor rows; full selection/replanning/acquisition pending |
| P1 1.2 B5 | HOST-TESTED pipeline | Fusion orders filters/cues/memory and commits current-state contact once; Robot/physical sampling remain |
| P1 1.2 B6 | HOST-TESTED | Governor final cap/slew/compensation; FSM target-loss brake/profile selection pending |
| P1 1.2 B7 | HOST-TESTED | Turn/Straight/Arc/Brake/TimedArc; bounded fallback and cumulative deadlines; scripts/FSM integration pending |
| P1 1.2 B9 | HOST-TESTED request math/qualification | D-036 frontDemand and three-observation FrontQualification; actual state-entry/reset/loss routing still pending |
| P1 1.2 B10 | HOST-TESTED | DefendTurn captures one target and preserves700/800ms deadlines; Robot arbitration pending |
| P1 1.2 B11 | HOST-TESTED components | Qualified timer/deflection Detector and rolling limiter/ALL_IN; real re-flank script/FSM arbitration pending |
| P1 1.2 B12 | HOST-TESTED DIRECT/SIDESTEP/ARC | Shared mirrors and current-perception exit intents; WAIT/global arbitration pending |
| P1 1.2 B14 | HOST-TESTED tick statistics | Exact supplied-duration/rate/max/saturation arithmetic; actual measurements, IMU/QTR/warnings/fault dispatch pending |
| P1 1.2 B15 | HOST-TESTED encoding/event buffer |25-byte frames/8-byte events; first4096 retained with overflow/count; frame storage/cadence/dump not implemented |
| P1 1.2 remainder | UNFINISHED | Re-flank/escape/other openers, Robot FSM and B14 integration |
| P1 1.3 properties | PARTIAL | Countdown/motion/fusion/DIRECT/filter fixed-seed10000 sets; limiter/detector independent references; full Robot R1/R5 and all-script symmetry pending |
| P1 1.4 architecture | PARTIAL | ARCHITECTURE describes actual components; full FSM diagram/explanation still pending |
| P1 1.5 target compile | HARDWARE-PENDING | No connected/verified UNO Q toolchain |
| P1 1.6 review/gate | SCOPED PASS / GATE-PENDING | Separate read-only component reviews; full fresh gate review, EXPLAINED OK and human GATE P1 PASS absent |

Latest completed validation:509 cases/11,920,737 assertions pass normal and
ASan/UBSan;48/48 controlled script checks. Tick statistics add12 new unlocked cases
to920394e. Reused
separate read-only scoped review PASS/no open finding; exact23-file inert
manifests reviewed. See P1_tick_statistics_validation.md/review. Newly fresh
reviewer creation hit the tool's thread limit; no full phase-gate review claimed.
D-039's previous one-case locked amendment remains the sole authorized established
locked edit; no established locked test or B16 value changed in this latest batch.

Approvals: D-017 governor; D-018 ordering; D-019 release anchor; D-020 persistent/
all-white guard; D-021 forward0.80; D-022 heading correction; D-023 duty-only
compensation; D-024 services; D-025 ALL_IN safety; D-026 bearing memory; D-027
contact lifetime; D-028 explicit overflow; D-029/30 phantom episode/replacement;
D-031 stuck faults; D-032 qualified timer/deflection; D-033 SIDESTEP priority;
D-034 current-perception exits; D-035 qualified/reset-only STOP; D-036 steering;
D-037 timed re-flank arc/right-first tie; D-038 qualified re-flank reacquisition;
D-039 exactly one documented locked amendment. Do not re-request them.
Components implement these policies; complete scheduler/recorder integration remains.

RowExecutor complete at component scope (contract76e0360/c5e80b8, implementation
970e083). Existing45-degree side angle centralized without changing B16.
Front-centered qualification (c0b3ad6/1950635) and B14 tick statistics
(118f9cc/dc9daa4) are HOST-TESTED/reviewed. Full loss routing/Robot remain subject
to specification reconciliation. Next eligible task: production countdown
lifecycle contract, independent tests and implementation using existing Controller/
Services; read analysis/P1_countdown_lifecycle_audit.md. Do not change locked tests
or derive motion permission from service completion. Other unblocked B14 predicates
are described in analysis/P1_fault_contract_audit.md.
Leave unresolved row selection/replanning/head-on cases explicit. Then B8 SEARCH
and remaining Robot/escape/re-flank/WAIT after required specific decisions. Read
analysis/P1_search_reflank_contract_audit.md.
Pending protected choices: SC-Y re-flank completion, SC-Z SEARCH side mapping,
SC-AA scan fallback, SC-AB unseen-side recency; SC-R/S escape direction/priority,
SC-AC head-on brake/reverse values; SC-AD entry count and SC-AE loss routing;
SC-G WAIT geometry; SC-A physical button decoding, SC-B QTR freshness/timing,
SC-I bounded log demo. Preserve established locked tests. D-016 alone does not
authorize P2 HAL work. All original gates remain required.

Hardware resumes through docs/P0_MANUAL_CHECKLIST.md when connected: obtain SSH
alias/user and isolation/part/instrument details, run read-only preflight, inspect
installed versions and F-061 loader ownership, then perform reviewed inert checks.
No passwords/private keys in tracked files; no motor-capable upload/run without
fresh specific STAND OK/RING OK. A source change invalidates inert snapshot hashes
until separate review. See CODEX_HANDOFF and CODEX_RESUME for full resume order.
