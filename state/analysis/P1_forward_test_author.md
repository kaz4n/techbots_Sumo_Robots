# P1 forward escape test author — 2026-09-22

Objective: independently test D-021's approved forward escape request and final
cap, retaining the existing B4 inner-side request bias and B6 governor rules.
The source contract is commit `79d2f6f`, its BEHAVIOR B4.2/B6 amendment, D-021,
and the public `edge.h`, `governor.h`, and `config.h` declarations. No core
implementation `.cpp` was opened. This remains P1 host-only under D-016.

## Owned new files

- `tests/test_edge_forward.cpp`: 9 specification-derived cases.
- `state/analysis/P1_forward_test_author.md`: this report.

No existing file, established locked test, implementation, or shared ledger was
modified by this author. Existing governor tests were read for doctest conventions.

## Coverage

The cases check inert demand defaults; literal approved 0.80 straight and
0.56/0.80 biased requests; left/right mirroring; all 253 invalid uint8 bias
values; the 0.80 final EDGE_FORWARD cap at 9.0, 11.1, and 12.6 V independent of
contact/centering; compensation before independent side caps; startup and
per-tick final electrical slew; immediate zero/brake/inhibit behavior; braking
before a reverse-to-forward transition; immediate reduction from full ATTACK;
and the existing guard veto with each forward demand, including an all-white
fault retained on later black samples.

The bias test uses independent literal expected requests and voltage equations.
At 9 V, a LEFT request yields 0.6906667/0.80 after compensation and caps, so its
final duty ratio is approximately 0.8633333. At nominal voltage, requested and
final ratios are 0.70 after slew settles. No constant final ratio is required
under independent saturation or transient slew.

## Validation status and limits

Authorship is ready for the coordinator's single complete host-suite run.
No build or host execution was run by this author for the new scope. No scoped
ambiguity or contradiction was found. Syntax/runtime status will be recorded by
the coordinator/reviewer after compilation, without changing test predicates to
fit failures.

`rg -c 'TEST_CASE' tests/test_edge_forward.cpp` reported 9 cases.
`git diff --check` returned exit 0; its unrelated existing manifest newline
warning did not report a whitespace error in these new files.

The guard/governor wiring in these tests is explicit test-owned composition.
It does not prove timed escape scripts, heading hold, complete FSM arbitration,
physical motion direction/curvature/speed, HAL MotorGate or PWM writes, target
compilation, board timing, or a human gate. No board or motor was contacted.

Next action: coordinator builds the full host suite and the independent reviewer
checks the approved implementation and these new tests.

Coordinator execution update: final host and separate ASan/UBSan suites each
passed 106/106 cases and 5,220,784 assertions, exit 0; tooling passed 47/47.
The separate reviewer inspected the raw evidence and returned scoped PASS in
reviews/P1_forward_codex.md. See P1_forward_validation.md for commands/limits.
