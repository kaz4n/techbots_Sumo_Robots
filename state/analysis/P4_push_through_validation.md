# P4 bounded push-through validation

2026-09-24, Asia/Dubai. D131 is implemented and host-tested; linked D132 admission
and D133 historical-fixture regressions also pass. The shipped `EDGE_PUSH_THROUGH_MS=0`
is unchanged. Positive durations below are copied-source test fixtures, not
physical tuning or permission to run motors.

## Implementation

Actual Escape and Robot arbitration implement the adopted B9.4 exception.
A fresh admitted front-white observation, prior ATTACK, current centered target
and confirmed plus raw FC can start one bounded interval. Repeated or retained
white cannot renew it. Eligibility loss, rear white, STOP/faults, deadline and a
qualified stall restore ordinary edge priority. A consumed interval cannot
restart until an actual escape completes on fresh black or reset occurs.
True line masks and edge history remain available to safety and recording.

Escape reuses mutually exclusive episode storage rather than adding a timer
alongside the replan counter. Every transition to real escape initializes the
counter, including fault transitions. Guard alone retains immediate white
behavior. All requests still pass through the governor and actual MotorGate.

For positive durations, timing evidence now excludes admitted white even when
escape is deferred, including the first eligible arming observation. It never
reopens after black. This explicit D131 evidence-policy extension preserves
motion, source-error precedence and completion of an earlier valid receipt.
The zero-duration configuration preserves its original event classification.

## Executed checks

Commands and exit statuses are retained under `P4_push_through_raw/`. Each host
run uses its `run_host.py` with the recorded name, duration and flags; Linux
scratch was under `/dev/shm`, with receipts captured before releasing it.

| Configuration | Result |
|---|---|
| Shipped0, normal full suite | All16 CTest targets pass;1519 main cases and187 existing MotorGate cases. New push targets34 cases each. The later private harness compile failure made the wrapper return1; it did not change the public result. |
| Copied20, normal retry |34 public and12 private cases pass per M0/M1. |
| Copied100, normal |34 public and12 private cases pass per M0/M1. |
| Shipped0, configured-button fixture, ASan/UBSan |36 public and12 private cases pass per M0/M1. |
| Copied100, configured-button fixture, ASan/UBSan |36 public and12 private cases pass per M0/M1. |
| Copied20, configured buttons and timing evidence, ASan/UBSan retry |42 public cases pass per M0/M1, with981358/981112 assertions;14 separate-review cases pass with25850/25985 assertions. |
| Shipped0, unchanged D129 timing suite, ASan/UBSan |30 cases pass per M0/M1, with21034/21059 assertions. |
| Controlled tooling and configuration registry before D132 |149 tooling methods and2 registry methods pass. These are script tests, not board builds. |
| Prior/current host layout comparison |All seven compared profiles match. Escape208 bytes; EscapeSample28 bytes, new bool at offset27. Default Robot2640/Runtime166624; timing Robot2712/Runtime166744. |

Locked fixed-seed checks include10,000 Escape streams and10,000 actual
Robot/MotorGate streams, alongside exact deadline, wraparound, mask, stale-source,
raw-polarity, no-renewal, STOP/fault and stall cases. The configured tests exercise
actual Runtime and MotorGate boundaries with synthetic hardware inputs.
No sanitizer diagnostic was reported in the completed successful runs.

Host syntax checks admit0/20/100 and reject101/large overflow fixtures. The host
uses `-Werror`; native `-w` makes that insufficient proof of raw-literal rejection.
That review finding is addressed separately by D132's copied-config validator.

## Failures and binding

`P4_push_through_first_failure.md` and separate review records preserve the
initial private REQUIRE/no-exceptions mismatch, the independently corrected
FC+side stimulus for later re-flank, and the timing-policy ambiguity. Original
oracles, exact failures and corrected hashes remain available. No prior locked
test was changed and no failing assertion was weakened to pass production.

`final_binding_before_D132.json` verifies684 frozen inputs and all40 prior
protected files before the linked tooling change. `freeze.json`, its timing
extension delta and `original_freeze.json` identify the successive source states.
New locked safety source SHA-256:
`2dffbfa45d565b2102d50190661a941650e938ef2c865813a0c5fa44f4d2abd0`.
Preserve it under the established locked-test rule.

The later `P4_push_literal_raw/final_binding.json` rechecks all684 inputs after
D132/D133. Only the six explicitly named tooling/fixture/attribute paths differ;
all firmware remains exact. All41 protected source files plus .gitkeep match.
D132's32 new admission methods,12 separate reviewer methods and the repeated296
tooling methods pass; original failures and narrow fixture corrections remain
recorded in `P4_push_literal_validation.md`.

Reviewer provenance and pending/final findings are in
`../reviews/P4_push_through_review.md`. This is separate-context same-model
review, not cross-model or human review.

## Remaining acceptance

No D131 board compilation, upload or motor run occurred. Target image/loader
fit, loaded RAM/stack and complete worst-case tick below800us remain pending;
host sizes or sanitizer success cannot establish them. Positive physical tuning
still needs original P4.4 trials with zero self-exits. All actual P4 metrics,
PINMAP/EXPLAINED and human phase gates retain their existing pending status.
