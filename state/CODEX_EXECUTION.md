# Execution checklist: verified P1 core and pending P0/P1 gates

Checkpoint:2026-09-23 Asia/Dubai. PROGRESS.md is authoritative. D-016 permits P1
host work while P0 acceptance is pending; it authorizes no P2 HAL work. No human
phase gate has passed. D-051 delegates engineering choices; D-052 permits bare
UNO Q diagnostics. No additional hardware connection is requested.

## Completed software checkpoint

- Contracts ea4618c/4ae6d45/99bd3c8 and D-06134c48d0 precede dependent source.
- 59376fe: bounded metadata validation/EventBatch;8692734: production Robot plus
  independent scenarios;3e46ea4: inert app entry and complete architecture.
- HOST-TESTED:895 cases /13,765,968 assertions, normal and ASan/UBSan, no fail/skip.
  Both reviewers independently reproduced.88 new cases include10000 actual Robot
  streams. Locked expectations and original76 B16 values remain unchanged.
- SCRIPT-TESTED:116 checks,39.167s final. Exact24-file source maps reviewed before
  bench manifest8107ec2d/333fe736 refresh; older Robot maps are superseded.
- TARGET-COMPILED: actual UNO Q app, sourcece90f09d, MATCH0/MOTORS_ALLOWED0,
  default startup, exit0;125508B program/61004B globals/201140B remaining.
  No upload/reset/start. This proves compile/link, not full app runtime or WCET.
- REVIEWED: fresh full-core PASS/no open finding plus reused scoped PASS. These
  are distinct same-model Codex contexts, neither human acceptance nor cross-model.
- Evidence: analysis/P1_robot_validation.md and raw receipts; failures retained
  in P1_robot_failure_analysis.md. Reviews and current P1 packet are in reviews/.

## Existing phase tasks

| Task | Status | Evidence / remaining acceptance |
|---|---|---|
| P0 0.1 G1–G6 | SOURCE-REVIEWED / INSTALLED-INVENTORY | FACTS and P0_G*.md; physical electrical checks pending |
| P0 0.2 scripts | SCRIPT-TESTED / TARGET-USED |116 final checks; actual ADB board builds; SSH default retained |
| P0 0.2/0.4 inert demos | BARE-SCHEDULER-MEASURED / RAM-COUNTER-OBSERVED |60000 samples,max/p99 lateness3us,zero >=1ms late; matrix counter441→444; P0_bare_board_results_20260922.md |
| P0 0.3 host scaffold | HOST-TESTED |C++17/CMake/doctest2.4.12, now full895-case suite |
| P0 0.5 pin map | HARDWARE-PENDING |Electrical measurements and human PINMAP OK absent |
| P0 gate | GATE-PENDING |Optical/Monitor/cold-start and external microbenchmarks unfinished |
| P1 1.1 interfaces | IMPLEMENTED |Public contracts committed before independent tests/source |
| P1 1.2 B3/B13 | HOST-TESTED / TARGET-COMPILED |Production menu, mode capture, full hold, services and STOP; physical A1/consumers later |
| P1 1.2 B4 | HOST-TESTED / TARGET-COMPILED |Full Escape/global Robot priority and actual-duty input; physical fresh QTR and MotorGate later |
| P1 1.2 B5 | HOST-TESTED / TARGET-COMPILED |Raw Fusion, truthful history, preview and one final contact commit |
| P1 1.2 B6/B7 | HOST-TESTED / TARGET-COMPILED |One Governor pass, electrical caps/slew/braking and bounded motion |
| P1 1.2 B8–B12 | HOST-TESTED / TARGET-COMPILED |Actual SEARCH/front/DEFEND/re-flank, all six opener modes and integration |
| P1 1.2 B14 | HOST-TESTED / TARGET-COMPILED |Fault dispatch, freshness/receipt contracts, QTR warning and supplied-duration statistics |
| P1 1.2 B15 core | HOST-TESTED / TARGET-COMPILED |Event metadata/batch, cadence, actual-duty frame binding, loss policies; HAL storage/dump later |
| P1 1.3 properties | HOST-TESTED |10000 actual Robot streams plus existing component properties, specified mirrors/wrap/finite bounds |
| P1 1.4 architecture | IMPLEMENTED / REVIEWED |Complete module map, transaction, actual FSM graph and student explanation |
| P1 1.5 target | TARGET-COMPILED |Prescribed app compile-only via actual board-side ADB tool; inert app only |
| P1 1.6 safety/review | SOFTWARE-PASS / GATE-PENDING |Fresh full-core PASS; EXPLAINED OK and human GATE P1 PASS absent |

## Next actions and boundaries

1. Preserve the completed P1 software evidence and current P1 gate packet. Do not
   restart completed modules or reinterpret a passing review as a human gate.
2. Remaining P0 bare-board evidence includes bounded Monitor transport (SC-I),
   optical observation and real cold-start measurements. Use existing G3/G4/Facts
   findings first; only execute a new inert test after its actual API/timeout
   contract is verified. RAM debugger reads do not replace a Monitor round trip.
3. Electrical/pin-map and external sensor/driver/IMU measurements remain deferred
   while only UNO Q is connected. SC-A button decoding and SC-B QTR freshness/
   tick budget must be resolved with real hardware evidence before dependent HAL.
4. P2 and later implementation wait for genuine original gates or specific
   scheduling authorization. No STAND OK/RING OK exists. Full project/P7 is not done.

Last uploaded firmware remains the inert matrix/default image uploaded2026-09-22
23:34:33+04 under D-052. Compile-only never replaces it. Keep credentials outside
tracked files. No push/tag/release occurred.

Schedule: no cut is due on23September. Apply the Sep28 reactive-core scope cut,
Sep30 P6 eligibility and1October21:00 Dubai freeze at the actual deadlines.
