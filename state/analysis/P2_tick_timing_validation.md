# D092 complete-tick timing validation

2026-09-23 Asia/Dubai. Active P2 software under D051/D075. Baseline a57d3b7;
contract/public header commit33e6cba. The preceding goal turn made progress by
completing D091 actual bare-board recorder evidence. Full P0-P7 remains incomplete.

## Implemented change

Robot now accepts explicit actual acquisition-start metadata while retaining
post-acquisition decision timestamps for sensor age and behavior. It selects a
fixed timing mode until reset, saves start/validity with the pending token and
checks the complete start/decision/application/completion/next-start/next-decision
sequence from one unsigned half-range anchor. Legacy timing retains its original
equation. Missing or malformed duration remains incomplete evidence; unchanged
motor receipt validation independently protects permission and applied settings.

Frozen production implementation SHA256:
0e1ddb2057e0cc412529c2c8f1d77e1519edc5243847c0950fc6cda07e9f4e2d.
Scope: fsm.h/fsm_robot.cpp, new independent tests/fixture, enabled-test registration,
existing seven inert source hashes and state evidence. No established locked or
ordinary tests, config.h values, motor writers, sensor policy or pin changed.

## Validation status

Independent test-author reads only public headers/specifications and previous
tests, never implementation bodies. The source worker owns onlyfsm_robot.cpp.
A genuinely separate fresh same-model context reviews actual source/tests/evidence;
this is neither cross-model nor a human phase gate. Final validation is PASS with no open reviewer finding; exact results follow.

Standalone C++17 warnings/syntax PASS (impl/receipt.md). Current WSLUbuntu toolchain:
g++13.3.0 and CMake3.28.3. Full sanitizer build uses address+undefined sanitizers
and frame pointers, verified in build/host-sanitize/CMakeCache.txt.

Actual on-board compile-only PASS, no upload/reset/MCU action:
source5451e99d6e3542e5460683bde7dcbd6468a9a5aeb7153883906ca6d6b4b3ba38,
bench/p2_dump_compile, pinned arduino:zephyr:unoq/core1.0.0, default startup,
MOTORS_ALLOWED0/MATCH0. Compiler reports315764program/238812global bytes with
low-memory warning,23332 nominal remaining. This is not measured loaded free RAM.

72 physical/staged/board source files match exactly. Three real ELFs retain both
validTimingStart and validTimingReceipt and the strong empty loop hook. Loader
base hash and all undefined-import sets match reviewed D090;40native and42AEABI
exports are nonzero, preserving the previously audited fmod/sqrt bindings.
Raw target_compile, target_audit, target_5451e99d_bench-default andsource_integrity
receipts preserve exact commands, status and bytes. Existing target probe accepts
runtime RobotInput and retains actual recorder/dump code, not a header-only test.

Seven existing inert source keys were independently reconstructed/reviewed against
a57d3b7. Only fsm.h/fsm_robot.cpp differ. Root verified exact physical hashes and
merged those seven values, with no key or upload-policy change. This grants no
new hardware run. Current MCU remains the earlier frozen D091 source1502e948;
its pinned capture/layout artifacts still describe that old actual image only.

## Limits and next action

D092 proves software accounting, not MCU clock calibration, real sensors/motors,
resource scheduling, complete800us WCET, native UART transfer or any human gate.
No new board upload or runtime test was performed. D091 measurements remain scoped
to its earlier synthetic runner and cannot certify this changed source.

Next compose actual app owners and acquisition scheduling. The narrow battery-age
prerequisite audit is saved in P2_app_battery_audit.md; its10/20ms retention proposal
has not yet been selected or implemented. Explicitly amend D078 before holding
voltage rather than quietly marking cached data fresh. App.ino remains an inert
link scaffold, and complete P2 physical/gate acceptance is pending.

## Final software results

Full normal and ASan/UBSan suites each pass1303main cases/24481744assertions and
87enabled MotorGate cases/3848039assertions, zero fail/skip. CTest durations6.77s
and23.65s respectively; compile time is separate. Independent author22newcases/
487assertions pass each motor configuration, including actual finalSTOP acquisition
propagation into the sealed recorder. Source/fixture expectations were derived
without reading implementation bodies. Every prior test remains unchanged.

Fresh separate same-model review PASS/no BLOCKER,MAJOR or MINOR. Reviewer reproduced
24cases/16206assertions each motor setting, including its own2244 neighboring/wrap
chronology tuples. Exact report reviews/P2_tick_timing_review.md and review_raw/.
Its first reviewer-only harness compilation lacked initializer_list; the failed
receipt is retained and only that new harness include was corrected. No production
or established test failure/fix was needed.

61controlled tooling methods pass, covering SSH/ADB argument/compile/upload
separation, staging, matrix and recorder upload boundaries. These are substitutes,
not real board upload claims. Exact command arguments/status/stdout and CTest
logs are in P2_tick_timing_raw; validation_summary.json provides counts. Target
compilation and source/export checks above are actual on-board Linux evidence.

No config or locked tests changed; independent registry refresh alters only seven
existing reviewed hashes. Target source5451e99d is compile-only. D091 actual MCU
source1502e948 remains last deployed, frozen inert; no new runtime result claimed.
SC-AK is resolved and implemented in software. SC-AJ clock qualification, physical
B8/native UART, full app/HAL/resource scheduling, complete800us WCET and all human
gates remain open. No further testing needed for D092 absent a new source change.
