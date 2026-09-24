# D138 independent test author workspace

Owner: `/root/p7_ready_tests`, 2026-09-24, Asia/Dubai.

Scope is new draft tests and their freeze record. Production implementation,
established tests, shared fixtures, configuration, build files and ledgers are
not this author's editing responsibility. Root integrates and executes tests.

## Independence

The author has read AGENTS.md, the public D138 proposal, the relevant public
headers, prior public contracts and existing tests/helpers. No production
`.cpp`, `.cc` or `.ino` implementation has been read. Existing test sources are
read as fixture/interface examples, not as companion implementation behavior.
The author does not execute the companion implementation before test freeze.
Same-model source independence is claimed; different-model independence is not.

## Existing seams

- `tests/robot_scenario.h`: actual Robot with synthetic observations and actual
  intended-output receipts for pure core tests.
- `tests/fixtures/qtr_cal_fixture.h`: actual adapter/Robot/Gate/calibration
  pipeline with explicit button option and raw/classified handover stimuli.
- `tests/fixtures/app_runtime_fixture.h`: actual Runtime, Transaction, Robot,
  MotorGate and ADC owners with typed bounded source callbacks. Configured
  button builds use `APP_TEST_CONFIGURED_BUTTONS`.
- `tests/fixtures/app_service_reset/fixture.h`: documented local STOP/reset
  gesture timelines; reuse its public sequence without editing the helper.
- `tests/test_ui_display.cpp`: existing complete 104-byte literal frame pattern.

A local callback wrapper can retain the submitted frame and supply valid battery
ADC codes. It must retain the existing source timing and conversion formula.
Exact warning-threshold equality belongs to pure renderer cases; Runtime cases
use real accepted integer ADC codes straddling the configured threshold.

## Integration plan

Root can add the pure renderer/core draft to ordinary M0/M1 host targets and add
the Runtime draft to configured-button M0/M1 Runtime targets. Profile exclusions
need separate builds with the actual profile macros; a source assertion alone
is not execution evidence. No native hardware, network or target run is part of
this author's work. Test freeze and exact source hashes will be recorded here
before the first implementation execution.

## First-source test freeze

The adopted contract is D138 at `36a96bd2`; its SHA-256 and the two test source
identities are recorded in `freeze.json`. Nineteen pure/core cases include
literal full-frame R/battery/fault expectations, all-state/view compatibility,
exact float thresholds, nonfinite values, blink/wrap, readonly neutral getters,
explicit-source timing/replay/reset/menu/cancel and raw/classified handover.
Ten Runtime cases include actual M0/M1 receipt binding, real captured frames,
valid ADC codes, conservative diagnostics, full hold, service views, source and
application faults, and the local service-only lifetime. The configured cases
are compiled only when the established synthetic window macro is supplied.

No test or companion implementation was compiled or executed by this author.
The root owns first execution and preservation/adjudication of failures. The
existing fixtures and tests were not changed. Token exhaustion is not reachable
in a bounded test through the public Robot API; this draft does not claim that
case. Faulted Runtime may leave an old physical frame: the fault case inspects
new submissions only and does not claim optical clearing. Source grants, physical
pins/buttons/sensors, matrix optics, motor motion and target timing are unproved.
