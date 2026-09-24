# D131/D132/D133 independent scoped review

## Findings
- [MAJOR, CLOSED] tools/board_tool.py:169,243: D132 validates the copied canonical raw literal in 0..100 before any board operation, closing native overflow admission. Source splices and code-level `%:` directives fail explicitly. All32 public admission methods and12 frozen private methods pass on production SHA bfa5ce00cc0ad72772eca48a3efcbb7af09a1e71a4d56ac5c300c377a63ad702.
- [MINOR, CLOSED] src/core/fsm_timing.cpp:80,135: both added white-only exclusions require positive duration, preserving default0 classification. Positive timing42 public/14 private and unchanged legacy30-case sanitizer suites pass per M0/M1.
- [MAJOR, CLOSED] tests/tooling/reviewed_source_fixture.py:30,58: the initial helper rejected Git's ancestor `bench` directory. Reviewed ff50369e now permits safe ancestor directories only, retains strict regular-file roots/hash checks and rejects repository destinations. The full D133 regression now passes.
- No open motor-safety BLOCKER or production MAJOR/MINOR found within this scope.

## Scope and evidence
- Fresh-context same-model reviewer; implementation/public tests read only after initial private contract/header probe freeze. This is not a cross-model review.
- Reviewed ef763104 baseline through adopted ac49d422 contract and final edge, FSM, timing, CMake and staging changes. R1-R6, union lifetime, source/heading provenance, raw FC, fault/STOP/edge/stall ordering, no renewal/rearm, final-state events and single contact/Governor pass inspected.
- Coordinator executed the equivalent configure/build/ctest commands from tools/test_host.sh in a RAM build; all16 default targets passed, including1519 main and187 existing Gate cases. The overall first runner exit1 was a private harness compile issue, retained separately.
- Public20ms and100ms M0/M1 runs pass34 cases each. Independent12-case probes pass each legal-positive M0/M1 configuration, including actual Transaction/Robot/MotorGate receipts.
- Configured0 ASan/UBSan passes36 public and12 private cases per M0/M1; private disabled-default assertions191 each. No sanitizer diagnostic reported.
- Configured100 ASan/UBSan passes36 public and12 private cases per M0/M1, including actual Runtime source-fault inhibition; no sanitizer diagnostic reported.
- Seven prior/current host layouts match; Escape208 and Sample28 bytes, added bool occupies offset27. All40 prior protected entries remain exact; final protected tree has42 entries including .gitkeep (41 source files). Shipped config SHA08470969 and native compiler/profile/upload approval policy remain unchanged; D132 adds admission only.
- No added allocation, loop, clock, network or I/O in changed production paths. A bounded second Escape/route call occurs only after deferral started no row; qualified unsuppressed stall revokes before limiter.request and executed-stall publication.
- Independent rehash confirms684 D131 inputs have only the six named D132/D133 changes in analysis/P4_push_literal_raw/final_binding.json; all106 D133 frozen inputs match. Production approval keys and consumed run records remain unchanged.
- D133 changes only historical fixture providers. P0 reads fixed commit1b1d77dc and checks both approved staged maps/aggregates; D118 reads the independently rehashed91-file e820c0e1 archive. All102/130/112 existing assertion calls in the three adapters are unchanged.
- Evidence: analysis/P4_push_through_validation.md and P4_push_literal_validation.md; corresponding raw command/LastTest receipts; review_raw/freeze.md, corrections.md, source_review.md, *_adjudication.md, historical_fixture_review.md and private receipts. Native status remains separate.
- Retained failures: initial private REQUIRE compile incompatibility; positive20 M1 fixture retained FC+SL, triggering the specified early TURN_IN exit. Only fixture stimulus/harness syntax were corrected; safety assertions and production source were unchanged.
- Optional timing first failure agreed with original D129's actual-preemption rule. Root explicitly adopted the D051 evidence-only extension excluding admitted white during deferral, including first arming; original meaning/failure and frozen oracle remain. Positive-only implementation and no-retry/precedence regression now pass.
- D132's first three failures were incorrect app-root header expectations, independently corrected to exact src/app header bytes plus absence of duplicates. Production stayed unchanged. Initial wider296-method run remains FAIL80 subcases: eight historical P0 pin failures reproduced with the pre-D132 tool, and72 D118 fixture failures before tool use. This motivated D133; it is not relabeled as a passing run.
- Final D133 regression_retry1.json/txt records the same296 methods PASS in224.289s, zero failures/errors/skips, bound to historical_fixture_freeze SHA0636e37d. All affected historical protocol cases now reach and pass their preserved assertions. No actual board operation occurred.

## Verdict
PASS within the reviewed D131 behavior, D132 raw-literal admission and D133 test-fixture software scope. No open BLOCKER, MAJOR or MINOR finding. This is fresh-context same-model review, not cross-model review or a human phase gate.
Native image/loader fit, loaded/free RAM, full-source800us WCET, real sensors/motors/ring behavior and positive-duration tuning remain unmeasured; no target action or physical/gate approval follows.
