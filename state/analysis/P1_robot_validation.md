# Production Robot validation — 2026-09-23 Asia/Dubai

Status: IMPLEMENTED / HOST-TESTED / TARGET-COMPILED. Final normal and ASan/UBSan
suites pass895 cases /13,765,968 assertions, no failures or skips. Final tooling
passes116 checks. The actual UNO Q compiles the inert P1 app with no upload.
P0 acceptance and all human gates remain pending; D-016 permits this P1 work.
No new hardware connection is requested under D-052.

## Change and independent responsibilities

D-060 public contracts ea4618c/4ae6d45 preceded implementation and independent
tests. Checkpoint da84b06 records work in progress. Normative semantics are in
P1_robot_contract.md; proposals remain provenance where the actual header differs.

- Source worker: fsm_robot.cpp and only Robot's private fsm.h members, no tests
  read. Complete bounded Robot composition; receipt P1_robot_implementation.md.
- Test author: new Robot fixture/scenarios/locked/event cases from specification
  and public headers only; receipt P1_robot_test_author.md. Synthetic application
  and timing receipts are explicitly mocks, never physical evidence.
- Coordinator: metadata validator/EventBatch append, inert app compile entry,
  architecture and state ledgers, builds and evidence.
- Reused separate reviewer: P1_robot_codex.md, scoped source/test/byte review.
- Fresh same-model reviewer: P1_fresh_gate_codex.md, full-core safety and P1
  readiness. Neither reviewer is cross-model or a human gate authority.

## Initial static evidence

- Worker strict C++17 syntax check exited0 with Wall/Wextra/Wpedantic/Werror,
  no exceptions/RTTI;862 lines,49 functions, longest38 lines. No runtime claim.
- Metadata strict syntax check exited0; separate static review found no material
  issue. Existing codec, statistics and EventBuffer bodies remain unchanged.
- Inert app static review passed: one default BOOT Robot call, volatile RAM
  inhibition marker, empty loop and MOTORS_ALLOWED==0 assertion. No motor API.
- Read-only ADB get-state on device2629958581 returned device, exit0 at this
  checkpoint. This says nothing about new target compilation or physical sensors.
- Prior807-case suite belongs to0dd643e and is not proof of this new source.

## Preserved failures and final validation

First whole runtime results and repair are preserved in
P1_robot_failure_analysis.md: a missing standard include was fixed literally;
then875/876 cases passed with seven assertions exposing the unknown-bearing
policy gap. D-061/34c48d0 selected bounded zero-demand waiting before replacement
code and independent regressions. No locked expectation changed. Validation
below ran against final source rather than the original source freeze.

| Check | Actual result | Raw receipt |
|---|---|---|
| Normal CMake/build/CTest and direct binary | exit0;895/13,765,968, no fail/skip | P1_robot_host_20260923_run4.txt |
| ASan/UBSan build and direct binary | exit0; identical895/13,765,968; no sanitizer diagnostics | P1_robot_sanitize_20260923.txt |
| Fresh reviewer direct reproduction | exit0; identical895/13,765,968 | P1_fresh_gate_runtime_20260923.txt |
| Scoped reviewer direct reproduction | exit0; identical895/13,765,968 | P1_robot_reviewer_host_20260923.txt |
| Controlled tooling substitutes | exit0;116 checks in39.167s | P1_robot_tooling_20260923_final.txt |
| Actual board-side app compile-only | exit0; MATCH0/MOTORS_ALLOWED0/default | P1_robot_target_app_20260923.txt |

Actual app uses125,508 bytes of786,432 program storage and61,004 bytes of262,144
global-memory capacity, leaving201,140 bytes for local variables per compiler
report. This is not runtime stack high-water or WCET evidence. Target is
arduino:zephyr:unoq using the installed board-side toolchain (CLI1.5.1/core1.0.0,
previous installed inventory in FACTS); ADB device2629958581 was live before
the operation. The script verified the pinned core before compiling.

App staged source SHA256:
ce90f09dff02447b6197097d0e9d074bc5a0c11813f40a3d4eaa40750b699b91.
All24 staged files and aggregates were independently reviewed against actual
source in P1_robot_inert_manifest_final.json. The two reviewed bench manifest
entries are matrix8107ec2d and timing333fe736. Earlier Robot proposal maps and
intermediate tooling results remain preserved but are superseded.

No upload, reset, firmware start or motor-capable build occurred. Last uploaded
image remains the September22 inert matrix; no earlier measurement was reused
as measurement of the new app. Compile-only copied sources and built artifacts
on board Linux without replacing the running MCU image.

Implementation commits:59376fe metadata and8692734 actual Robot plus independent
scenarios; public contracts ea4618c/4ae6d45/99bd3c8 and D-06134c48d0 precede their
dependent code.88 new independent cases augment the prior807. The original new
locked file SHA349bc3788eebe561b06207796b9b65234f568f38c5e304d2bac26ea0cd112c37
remained unchanged through failures and repairs; no established locked file or
B16 value changed. QTR's one added standard include changes no predicate.

Review corrections: sampled QTR warning coverage; accurate DEFEND terminal-zero
diagram; explicit D-061 legitimate-ambiguity policy; pending deadline anchored
before deferred escape-exit motion; CONTACT metadata rejects impossible centered/
close combinations. Each has independent cases and passing runtime evidence.
Reports: reviews/P1_robot_codex.md (reused scoped) and
reviews/P1_fresh_gate_codex.md (fresh full-core, same-model). No review is a human
EXPLAINED OK or GATE P1 PASS. Current gate packet is reviews/P1_gate_request.md.

## Limits

P1 app is an inert compile/link entry, not the P2 scheduler/HAL. Host tests and
target compilation do not prove fresh physical acquisition, real MotorGate,
whole-tick WCET, contact/escape performance or ring safety. Required A1 decoding,
QTR timing/freshness and bounded Bridge dependencies remain documented. No B16
value, wiring/pin, human gate or motor authorization is changed by this work.
