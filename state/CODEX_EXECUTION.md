# Execution checklist: P1 host development and P0 acceptance

Current checkpoint: 2026-09-23 Asia/Dubai. PROGRESS.md is authoritative;
D-016 permits P1 host development while P0 acceptance remains pending. No human
phase gate has passed. D-051 delegates engineering choices without questions;
D-052 authorizes bare UNO Q diagnostics. No additional hardware is requested.

## Latest bounded delivery

- IN PROGRESS: D-060 production Robot contract ea4618c/4ae6d45 is published.
  fsm_robot.cpp, independent actual-Robot/locked/event scenarios, metadata batch
  validation and inert app compile entry are being implemented. These changed
  sources have no whole-suite or target validation yet;807 below is the baseline.
- Full Escape:66f76e4; WAIT:6938c63; contact preview:990f287. Interfaces preceded
  implementation; decisions D-054/D-055/D-056 record the exact added contracts.
- D-057 START-only routing:4d323bc, contract322ecce. Suppression cannot replay a
  release, restart calibration, cancel an existing hold or bypass STOP/MODE.
- D-058 Menu:9d9b858, contract3563a8f.25 new component and11 new locked cases.
- D-059 HeadingReference:4671c8b, public contracts first.31 new independent cases;
  raw Fusion versus logical match coordinates, honest missing-IMU fallback.
- HOST-TESTED:807 cases /12,233,461 assertions, normal and ASan/UBSan, no failures
  or skips; independent reviewer reproduced. Established locked tests unchanged.
  MODE_SHORT_MS centralizes existing B13 text; all76 B16 defaults unchanged.
- SCRIPT-TESTED:116 checks,40.767s latest. Separate reviewer approved exact23-file
  inert snapshots before manifest refresh. New sources require their own target
  evidence; historical uploaded image and measurements remain separate.
- TARGET-COMPILED:807-case revision4671c8b inside inert timing/default,
  sourcebbf6c22,exit0,MATCH0/MOTORS_ALLOWED0;74,008B program/33,964B globals.
  No upload/reset/start. This is not the complete app or a runtime measurement.
- Evidence: analysis/P1_escape_wait_validation.md and linked raw receipts;
  reviews/P1_escape_wait_codex.md. Read its final scoped verdict before reuse.
- Latest routing evidence: analysis/P1_start_routing_validation.md and
  reviews/P1_start_routing_codex.md, including independent runtime reproduction.
- Menu evidence: analysis/P1_menu_validation.md and reviews/P1_menu_codex.md;
  first tooling inventory failure preserved beside the reviewed literal correction.
- Heading evidence: analysis/P1_heading_validation.md and reviews/P1_heading_codex.md;
  near-antipode MAJOR corrected before test freeze and covered by independent tests.
- Physical evasion, sampling, real MotorGate and timing acceptance remain open.

## Existing phase tasks

| Task | Status | Evidence / remaining acceptance |
|---|---|---|
| P0 0.1 G1-G6 | SOURCE-REVIEWED / INSTALLED-INVENTORY | P0_G*.md; FACTS F-001..F-072; electrical checks pending |
| P0 0.2 scripts | SCRIPT-TESTED / TARGET-USED |116 tests; actual board-side ADB compile/upload receipts; SSH default retained; missing rsync reported |
| P0 0.2/0.4 inert demos | BARE-SCHEDULER-MEASURED / MATRIX-COUNTER-OBSERVED |60000 samples,max/p99 lateness3us,zero >=1ms late;counter441->444; P0_bare_board_results_20260922.md |
| P0 0.3 host scaffold | HOST-TESTED | CMake/C++17/doctest2.4.12; original B16 defaults preserved |
| P0 0.5 pin map | HARDWARE-PENDING | Electrical measurements and human PINMAP OK absent; config has no proposed pin assignments |
| P0 gate | GATE-PENDING | Optical/Monitor/cold-start and hardware microbenchmarks unfinished; P0_gate_request.md |
| P1 1.1 interfaces | PARTIAL | Component headers committed first; Robot integration contract pending |
| P1 1.2 B3/B13 | HOST-TESTED logical menu/lifecycle/routing | Production running-mode capture and actual service consumers pending |
| P1 1.2 B4 | HOST-TESTED Escape | Full policy/rows/replans/faults; fresh physical QTR and global Robot/MotorGate integration pending |
| P1 1.2 B5 | HOST-TESTED fusion/preview | Ordered filters/cues/memory; pure preview and one final commit; Robot wiring pending |
| P1 1.2 B6/B7 | HOST-TESTED | Electrical cap/slew/compensation and bounded primitives; one Governor invocation in future Robot |
| P1 1.2 B8/B9/B10 | HOST-TESTED components | SEARCH/front demand/qualification/normal arbitration/DefendTurn; global histories/state lifecycle pending |
| P1 1.2 B11 | HOST-TESTED components | Detector/limiter/ALL_IN predicate/Reflank; actual final-duty feedback and admission/arbitration pending |
| P1 1.2 B12 | HOST-TESTED all opener components | DIRECT/SIDESTEP/ARC/WAIT; Robot dispatch and physical opener evidence pending |
| P1 1.2 B14 | PARTIAL | Supplied-duration tick statistics; warning/freshness/fault dispatch incomplete |
| P1 1.2 B15 | PARTIAL | Encoding and first4096 event retention; per-tick events/frame cadence/HAL storage/dump unfinished |
| P1 1.3 properties | PARTIAL | Existing fixed-seed10000-stream component sets, symmetry/wrap/finite tests; full Robot R1/R5 scenarios still required |
| P1 1.4 architecture | PARTIAL | ARCHITECTURE matches components; complete FSM graph awaits Robot |
| P1 1.5 target | PARTIAL | Core compiled inside inert sketches; complete app/Robot and prescribed app compile remain unfinished |
| P1 1.6 gate | GATE-PENDING | Scoped component reviews; complete fresh gate review, EXPLAINED OK and human GATE P1 PASS absent |

## Next eligible work

1. Finish D-060 Robot source and independent scenario/event/locked tests, then
   freeze for separate review and normal/sanitized host validation. The adopted
   contract is analysis/P1_robot_contract.md and the actual public headers;
   ea4618c/4ae6d45 preceded source/tests. Proposals are superseded where clarified.
2. Verify actual Robot from that API and analysis/P1_robot_interface_audit.md:
   fresh input ownership, same-tick GO coordinate rebase, truthful histories,
   previous applied duties, one contact commit/Governor call, bounded events,
   STOP/edge priority and inhibited faults. Add real production scenario tests.
   D-060 adopts the event metadata/batch table with explicit clarifications;
   its21-event bound still needs production tests/review. Complete inert app
   compile-only on UNO Q after host validation; app uploads remain forbidden.
3. Complete P1 source/table/property coverage and architecture, target compile,
   then prepare fresh phase review. No P2 HAL implementation without gate/specific
   scheduling authorization; D-016 authorizes P1 only.

SC-A physical button decoding, SC-B QTR timing/freshness and SC-I bounded Bridge
remain real dependencies, not assumed successes. MPU6050 is human-reported;
installed/physical IMU evidence is absent. Other hardware-dependent acceptance
is deferred; no additional connection request is needed for these host tasks.

Bare board currently retains the inert matrix/default image uploaded2026-09-22
23:34:33+04 under D-052. No motor authorization exists. A compile-only action is
not an upload/run or full control-WCET measurement. Do not reuse old measurement
helpers with changed firmware identity. Credentials stay outside tracked files.

Schedule: no cut is due on23September. Apply PLAN's Sep28 scope cut and Sep30 P6
eligibility at their actual deadlines; code freeze remains1October21:00 Dubai.
C: has about290MB free; avoid large downloads and unnecessary build copies.
