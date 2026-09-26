# D197 internal SETTLE observation: host validation

The probe records the native SETTLE exit reason without changing its decisions
or adding hardware/clock calls. All five independent test methods pass, including
21 fresh scenarios compared across the original driver, current probe0 and
current probe1. The existing locked disabled/enabled motor suites also pass:
76 cases, 217,020 assertions, no skips.

Source `src/hal/motor_port_unoq.cpp` is19,185 bytes / `f1ee755a`; new
`src/hal/motor_settle_probe.h` is2,366 bytes / `2eced554`. Contract3346b119 defines
a separate28-byte report with current and first_failure, explicit validity and
seven false reasons plus success. The report publishes through volatile RAM
references to an ordinary static aggregate; its const-reference accessor never
resets it. No config, UnoQPort fields, Trace, Runner, sketch or locked test changed.

## Verified behavior

The independent oracle was frozen before its author inspected the implementation.
It exercises null context, each incomplete write, EN readback, initial bank
failure, in-loop readiness/register failure, final149/150/151us, unsigned clock
wrap, loop deadline,4096-poll exhaustion with zero/partial freshness, first-failure
retention and actual MotorGate cleanup/HALT. Every complete original/probe0/probe1
return/native-call/forwarded-clock/hardware transcript is byte-identical. The
fixture verifies its trace did not truncate, including the long poll-limit cases.

Probe1 independently checks report values, validity, reserved bytes, exact
12/28-byte layouts, no allocations and first-failure persistence after later
failure and success. Probe0's preprocessed SETTLE body is whitespace-identical
to the original Git source, its defined symbols are unchanged, and no diagnostic
report/accessor is exposed. Existing MATCH/MOTORS_ALLOWED incompatibility checks
reject all tested motor-capable probe combinations. All builds used UBSan and
serial compilers; all140 final frozen inputs remained unchanged.

## Preserved fixture failures

First execution stopped while linking the original source: the new harness
omitted the unchanged opp_fusion.cpp dependency of MotorGate. No method or current
implementation ran. Commitc7fa1679 preserves oracle8d8f9e82 and the exact failure.
Independent author/reviewer approved only adding that translation unit and pin.

The next execution passed every differential scenario and four of five methods.
The negative accessor fixture failed earlier than intended because probe0's new
header declares no motors namespace. Commita0ccf86d preserves oracle451762cf and
that failure. Including the existing motor_port_unoq.h in only the accessor-use
snippet supplies its real namespace; every assertion and separate inert-guard
input remains unchanged. Final oracle29c6cac3 passes all five methods. Neither
fixture correction changed production source, contract or C++ cases0ad263b0.

## Evidence and limits

- [Final independent freeze](P7_motor_settle_probe_raw/independent_test_freeze03.json)
  and [coordinator freeze](P7_motor_settle_probe_raw/coordinator_freeze03.json).
- [Final probe result](P7_motor_settle_probe_raw/probe_corrected_linux02/result.json)
  and its exact stdout/stderr plus compact per-command receipts.
- [Locked regression result](P7_motor_settle_probe_raw/locked_first_linux01/result.json).
- [Closing observation](P7_motor_settle_probe_raw/closing01.json): all140 pins
  stable, no owned RAM or locked-suite temporary directories remain.
- [Separate same-model review](../reviews/P7_motor_settle_probe_review.md).

These are host fixtures, not native timing or electrical evidence. Extra RAM
publication can perturb timing. The actual target symbol,28-byte ABI, initialization
and store instructions must be observed after a fresh checked compile. The
currently flashed image remains D195 source3a08ddeb; its internal failure reason
is still unknown. Preserve150us/4096poll limits and all consumed native owners.
