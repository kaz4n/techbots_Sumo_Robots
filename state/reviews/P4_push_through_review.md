# D131 bounded push-through independent scoped review

## Findings
- [MAJOR, OPEN] tools/board_tool.py:147: native staging accepts overflowing duration literals before uint32 conversion. D132 draft admission must also reject `%:if` conditional declarations and source splices before comment removal; private probes saved. Host -Werror is not native admission evidence; shipped0 remains intact.
- [MINOR, OPEN] src/core/fsm_timing.cpp:80: unconditional white-only exclusion changes default0 trace detail on simultaneous STOP+new-white from STOP_FAULT to EDGE. Gate added white-only checks on positive duration to preserve the stated default0 trace behavior, or explicitly adopt/document that tie change.
- No BLOCKER found in the reviewed Escape/Robot behavior; final evidence review remains in progress.

## Scope and evidence
- Fresh-context same-model reviewer; implementation/public tests read only after initial private contract/header probe freeze. This is not a cross-model review.
- Reviewed ef763104 baseline through adopted ac49d422 contract and current edge.cpp/edge.h/fsm_robot.cpp/fsm.h/CMake changes. R1-R6, union lifetime, source/heading provenance, raw FC, fault/STOP/edge/stall ordering, no renewal/rearm, final-state events and single contact/Governor pass inspected.
- Coordinator executed the equivalent configure/build/ctest commands from tools/test_host.sh in a RAM build; all16 default targets passed, including1519 main and187 existing Gate cases. The overall first runner exit1 was a private harness compile issue, retained separately.
- Public20ms and100ms M0/M1 runs pass34 cases each. Independent12-case probes pass each legal-positive M0/M1 configuration, including actual Transaction/Robot/MotorGate receipts.
- Configured0 ASan/UBSan passes36 public and12 private cases per M0/M1; private disabled-default assertions191 each. No sanitizer diagnostic reported.
- Configured100 ASan/UBSan passes36 public and12 private cases per M0/M1, including actual Runtime source-fault inhibition; no sanitizer diagnostic reported.
- Seven prior/current host layouts match; Escape208 and Sample28 bytes, added bool occupies offset27. All40 prior protected files hash-identical; config.h literal0 and native build/upload policy unchanged.
- No added allocation, loop, clock, network or I/O in changed production paths. A bounded second Escape/route call occurs only after deferral started no row; qualified unsuppressed stall revokes before limiter.request and executed-stall publication.
- Evidence: P4_push_through_review_raw/freeze.md, corrections.md, source_review.md, positive20_failure_adjudication.md; analysis/P4_push_through_raw/default0*, positive20_retry1*, positive100*, admission_layout.json; review_raw/*_private.{json,txt}.
- Retained failures: initial private REQUIRE compile incompatibility; positive20 M1 fixture retained FC+SL, triggering the specified early TURN_IN exit. Only fixture stimulus/harness syntax were corrected; safety assertions and production source were unchanged.
- Optional timing first failure agreed with original D129's actual-preemption rule. Root explicitly adopted a D051 evidence-only policy extension to exclude true white even during deferral, retaining the frozen oracle. Original meaning/failure remain recorded; new policy implementation/regression review pending.

## Verdict
PENDING final positive configured Runtime/sanitizer receipts and D132 closure. The open MAJOR prevents complete D131/software-packet acceptance; no phase gate is granted.
Native image/loader fit, loaded/free RAM, full-source800us WCET, real sensors/motors/ring behavior and positive-duration tuning remain unmeasured; no target action or physical/gate approval follows.
