# D180 main-app setup binding review

25 September 2026, Asia/Dubai. Independent fresh-context same-model review by
`/root/setup_binding_review`; this is not a cross-model review or human gate.
The reviewer read source, specifications, tests and recorded evidence, and
verified local identities. The reviewer did not execute tests, builds, native
commands or cleanup, and changed only this review report.

## Scope

Contract e4aea29c, implementation70b9cea5, independent oracle ad9bd19c,
test receipts8d8f38d1 and validation/documentation89c784e1. Relevant requirements
are D051/D096/D180, P7.2 and AGENTS R1-R11. The local date is before the
1 October21:00 code freeze; the schedule does not establish acceptance.

Production changes are limited to `src/config.h`,
`src/app/configured_setup.h` and the ordinary `src/app/app.ino` entry.
The reviewed objective is an explicit configurable setup binding with shipped
permissions still disabled. It does not qualify an enabled release.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the bounded scope.

The17 boolean mappings match the contract independently, including nested
mounting, matrix and dump fields. All checked-in declarations remain0,
the three axes remain0, and origin remains UNKNOWN. Binary, signed-axis range
and origin assertions precede conversion; in-range malformed or unconfirmed
mounting remains unchanged for the existing Estimator to reject. No permission
is inferred from another field, MATCH or MOTORS_ALLOWED.

The builder is a C++17 constant expression using a local value and a fixed
three-iteration copy. It adds no I/O, allocation, clock access or owner. The
main entry includes it inside the existing EMPTY macro protection and passes
its result once to Runtime.begin; loop still only calls Runtime.step. Existing
Runtime/HAL/core consumers, MotorGate, countdown, governor and edge paths are
unchanged. The source diff against d8ff6b5a contains no bench, protected-test
or tools changes; config contains35 additions with no existing value changed.

## Evidence assessment

- The separate spec-only oracle was frozen before execution. Actual public
  SetupGrants types and constexpr assertions check all21 destination leaves,
  singleton/inverse/mixed permissions, all four build-flag combinations, axes
  and origins. Negative profiles require compile-time assertion failures.
- Real Estimator executions retain unconfirmed/malformed mounting rejection.
  Actual sketch text is executed with explicitly typed native/Runtime/builder
  substitutes to observe one setup forwarding and loop behavior, including
  EMPTY restoration. The real builder is tested separately against real types.
- `first_test_output.txt` records16 methods PASS in18.179s, no skips;
  `legacy_test_output.txt` records26 unchanged methods PASS in3.067s, no skips.
  Both result receipts record exit0. There were no source or fixture repairs.
  Method15 preserves the established registry assertions and requires the
  deliberate wrong-default profile to produce its exact expected failure.
- All ten freeze entries matched local byte counts and SHA256 during review.
  Recorded output hashes also matched. `integrity.json` records24 prior D179
  pins exact, the original PROGRESS prefix intact, no actual scope/owner and
  no owned RAM scratch. Historical diagnostic inputs were not repinned.
- The runbook, architecture, dated software-map follow-up and current handoff
  describe configurable but disabled software and keep changed-main-app target
  compilation pending. They do not populate physical acceptance fields.

## Verdict

PASS for the bounded D180 implementation and HOST-TESTED evidence. This review
does not establish target compilation, Arduino/native execution, hardware
origin, current UART preparation, pin/electrical acceptance, loaded RAM,
complete-tick timing, physical behavior, a phase gate or motor-run permission.
The sketch substitutions are host evidence and cannot establish those facts.

The shipped configuration remains unusable for robot operation. Later grant
enablement requires the actual acceptance/ownership evidence and approved
configuration scope. Preserve the reviewed historical diagnostic and D179
caller; fresh board admission and a separately identified native scope remain
the next hardware dependency. Do not infer a retry or deployment from this PASS.
