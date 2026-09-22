# Execution checklist: measured P0 QTR/GPIO/ADC, verified P1 core, pending gates

Checkpoint:2026-09-23 Asia/Dubai. PROGRESS.md is authoritative. D-016 permits P1
host work while P0 acceptance is pending; it authorizes no P2 HAL work. No human
phase gate has passed. D-051 delegates engineering choices; D-052 permits bare
UNO Q diagnostics. No additional hardware connection is requested.

## Completed software checkpoint

- P0 0.4 QTR dcca300: current61d7a2d0/default inert upload03:00:13.327+04.
 100neutral+100pull-up acquisitions reached deadline/mask15. Total1530..1536us,
  charge11..12us, cleanup4 attempts. Actual full-image/frozen-RAM review PASS;
 306 tooling checks PASS. P0_qtr_validation.md retains failures/limits/raw receipts.
  Current source maps61d7a2d0/afa72adb/65d7e5a3/e30b5443/9ea79c80; older maps below
  are historical. No real QTR/freshness/physical-cleanup/R4 or human-gate proof.

- P0 0.4 GPIO a98bcf6:243 tooling checks and fresh source/binary/receipt reviews
  PASS. Current1dfbd571/default inert upload02:36:15.644+04;400 correct cycles,
  final HIGH/off. Pair2..3us/p993us, pinMode2..11us/p993us after first call.
  Full image/frozen RAM verified. See analysis/P0_gpio_validation.md. Empirical
  setup-only timing; debug overlap/native-error/optical/WCET limitations remain.
  Current source maps1dfbd571/18c4dfa8/5c5a72ac/0d5baec0 supersede older maps.

- P0 0.4 ADC9de8cd1:197 tooling checks and fresh source/binary/receipt reviews PASS.
  Actual sourcef5f637b2/default inert upload02:16:28+04;1000 complete calls,
  first276us,999 subsequent139..140us/p99140us. Full flash identity/frozen RAM
  verified. Setup-only; indefinite driver waits, floating input and possible debug
  overlap remain limits. analysis/P0_adc_validation.md and raw receipt directory.
  Current manifestsf5f637b2/aabfdebb/3ff0baba; prior maps below are historical.
- P0 D-062 fixed counter: packetdd4ed33 and adapter6b99a60;25 packet cases/
  156553assertions and39 actual-adapter substitute cases pass;40 sanitizer checks
  and156 full tooling checks pass. Fresh source/separate binary reviews PASS.
- Actual75ab5a22 default inert matrix/counter compiled and uploaded01:55:51+04.
  Project receive-only logger captured4..11 and56..63 in two8-second windows.
  This client's reconnect works; another client existed, Linux remained running.
  Current manifests75ab5a22/b4c61daf; analysis/P0_counter_validation.md has receipts.
- Following P1 results are the previously completed software checkpoint, not a
  repeated core run or the current UART workload's timing evidence.

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
| P0 0.2 scripts | SCRIPT-TESTED / TARGET-USED |306 full checks; actual ADB board builds/logger; SSH default retained |
| P0 0.2/0.4 inert demos | COUNTER-DELIVERY-OBSERVED / prior BARE-SCHEDULER-MEASURED |P0_counter_validation.md: actual4..11 and56..63; old timing image60000samples/max3us remains a separate workload |
| P0 0.3 host scaffold | HOST-TESTED |C++17/CMake/doctest2.4.12, now full895-case suite |
| P0 0.5 pin map | HARDWARE-PENDING |Electrical measurements and human PINMAP OK absent |
| P0 0.4 ADC | MEASURED / RUNTIME-API-BLOCKED |D-063/F-079; startup-only calls measured, stock runtime wait remains unbounded |
| P0 0.4 GPIO | MEASURED / REVIEWED |D-064/F-081;400 correct internal LED cycles, empirical timings |
| P0 0.4 QTR-style | MEASURED / REVIEWED |D-065/F-083; two100-sample timeout datasets, actual1.53ms path; SC-B still open |
| P0 G6 API compatibility | IN PROGRESS / COMPILE-ONLY |D-066 contract452502d;3 scoped host tests pass; installed Wire audit/source limits retained |
| P0 gate | GATE-PENDING |Fixed Monitor counter and ADC observed; optical/cold-start and physical electrical acceptance unfinished |
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

1. Complete D-066 MPU6050 compile-only API/link probe with exact pinned dependency
   provenance, installed exports and separate review. No I2C execution/upload.
   P0_imu_compile_contract.md and installed-contract audit define this scope.
   Keep all completed bare-board diagnostic evidence; no additional hardware request.
2. Preserve the completed P1 software evidence and current P1 gate packet. Do not
   restart completed modules or reinterpret a passing review as a human gate.
3. P0 fixed Monitor counter is now observed through D-062's adapter. Preserve its
   source/binary/host/physical distinctions; do not redo it or claim stock Bridge
   and production recorder semantics are resolved. Optical observation and true
   cold-start measurements remain absent; warm reset cannot replace cold power.
4. Electrical/pin-map and external sensor/driver/IMU measurements remain deferred
   while only UNO Q is connected. SC-A button decoding and SC-B QTR freshness/
   tick budget must be resolved with real hardware evidence before dependent HAL.
5. P2 and later implementation wait for genuine original gates or specific
   scheduling authorization. No STAND OK/RING OK exists. Full project/P7 is not done.

Last uploaded firmware is the inert QTR61d7a2d0/default image from
2026-09-23 03:00:13.327+04 under D-052. Compile-only never replaces it. Keep credentials outside
tracked files. No push/tag/release occurred.

Schedule: no cut is due on23September. Apply the Sep28 reactive-core scope cut,
Sep30 P6 eligibility and1October21:00 Dubai freeze at the actual deadlines.
