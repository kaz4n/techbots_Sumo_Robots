# P1 independent test-author evidence — 2026-09-22

## Objective and authority

Author host-only specification tests for the standalone P1 contracts under D-016,
and the final electrical governor envelope approved in D-017. D-018 permits later
gated-service ordering but is not treated as an implemented FSM. Today is the
PLAN section 3 P0 date; the D-016 development exception applies, and no physical
acceptance or phase gate is inferred.

## Independence and modified files

The test-author read AGENTS.md, `.claude/agents/test-author.md`, the relevant
BEHAVIOR sections, phase/decision records, config and public module headers.
**No implementation `.cpp` file was read.** Build output naming those files is
not source inspection. Implementation was concurrent and separately owned.

| New file | Cases | Evidence covered |
|---|---:|---|
| `tests/locked/test_countdown.cpp` | 19 | B0 defaults; B3 logical Gate; separate logical Buttons |
| `tests/locked/test_edge_classifier.cpp` | 6 | B4.1 classification only |
| `tests/test_opp_debounce.cpp` | 12 | B0/B5.1 polarity, sample assertion and timed clearing |
| `tests/test_front_view.cpp` | 10 | Seven unambiguous B5.2 front rows and front-only properties |
| `tests/test_governor.cpp` | 29 | D-017/B6 final electrical caps, slew, braking and filtering |
| `tests/support/countdown_runner.h` | helper | Deterministic randomness and an unwrapped host clock |

Total: **76 newly authored test cases**; with the existing scaffold, **77 cases**.
These locked files were initial creation; no established locked case was changed.
No implementation, configuration, shared ledger, pin or build-setting edits were
made by the test-author. No Git commit, upload or motor operation was performed.

## Test design

- Gate checks exact/adjacent hold boundaries, 1 kHz samples, duplicate releases,
  MODE cancellation at the deadline, STOP latch/precedence, reset and micros
  rollover. A separate literal **5,000,000 us** minimum test is independent of
  configured hold values: every 1 ms before five seconds plus 4,999,999 us must
  deny motion and GO. The configured 5,100,000 us boundary remains separately tested.
- Gate property: seed `0xB3005100`, **10,000 streams x 80 command steps** with
  random gaps/events, cancel/STOP/reset, zero/exact/adjacent intervals and rollover.
  Its oracle stores authorization windows on a 64-bit unwrapped clock, without
  using the implementation's returned phase or unsigned interval calculation.
- Buttons property: seed `0xB3000020`, **10,000 streams** varying origin, boot-held
  START, short press/release bounce and final stable transitions. Directed cases
  check 19,999/20,000/20,001 us boundaries, pulse uniqueness, both timestamps,
  reset, rollover and MODE/BOTH logical events. It does not connect to Gate.
- Edge tests exercise all 16 masks, all four thresholds at minus one/equal/plus
  one microsecond, zero/timeout/large readings, independent confirmation,
  persistent white, immediate black and reset. Default confirmation is one
  observation; loops also specify consecutive-count behavior for a future value.
- Opponent tests encode the seven named channels' electrical polarity directly,
  exercise all 128 detected masks, consecutive-set interruptions, exact clear
  deadlines, independent channels, reset, unused bit and timestamp rollover.
  Front-view tests use explicit table expectations and verify L/R symmetry.
- Governor tests cover all seven profiles at 9/11.1/12.6 V, all centered/contact
  combinations, eligibility loss, final duty acceleration at 999/1000/1001 us,
  immediate cap reductions/braking/inhibit, independent sides, reversal, reset,
  wrap, compensation floor, finite caps and nonfinite/unknown-profile rejection.
  The battery response has analytic backward-Euler checks plus a bounded,
  monotonic 1 kHz step response and voltage changes while output remains capped.

## Validation

Initial standalone suite command:
`wsl -d Ubuntu -- bash tools/test_host.sh` — **exit 0**, CTest **1/1 passed**.
The direct initial doctest run reported **47/47 cases**, **3,436,741 assertions**.
That initial result preceded governor tests and the independent five-second case.

The first build exposed test integration mistakes: REQUIRE is unavailable with
the existing `DOCTEST_CONFIG_NO_EXCEPTIONS`, and braced range iteration needed
`<initializer_list>`. They were corrected to CHECK with identical predicates and
an explicit include. No expected behavior or test threshold was relaxed.

Final complete-suite validation was run by the separate read-only reviewer after
the source-final notification: `tools/test_host.sh` **exit 0**, CTest **1/1**;
doctest **77/77 cases** and **3,457,564/3,457,564 assertions**, **0 failed, 0 skipped**.
The reviewer reported no findings in the test predicates; governor expectations
passed unchanged. The exact run summary is in
`build/host/Testing/Temporary/LastTest.log` (generated build evidence).
`git diff --check` returned exit 0 at source-final.

## Limits and unresolved interpretation

Passing this suite is **host evidence for these contracts**, not complete P1
acceptance despite exceeding the numerical 60-case minimum. No target compilation,
physical timing, hardware MotorGate write, motor enable/PWM observation, complete
Robot/Outputs timeline, R5 arbitration, escape behavior or physical ring result is
proved. The literal R1 test proves only the standalone logical permission floor.

SC-J button-to-Gate release anchoring remains unresolved: both edge and qualification
timestamps are tested without choosing one. SC-K countdown services and the B13
both-held STOP timer/recovery remain outside this implementation. Simultaneous
MODE plus START while idle is unspecified; randomized tests exclude that pair
instead of establishing an unapproved priority. Explicit STOP dominance is tested.

Classifier calls mean complete fresh observations; QTR acquisition cadence/staleness
and SC-B are outside this contract. SC-D2 escape decisions remain open. FrontView
does not resolve SC-L side/rear arbitration, target memory, contact or phantom
policy. Governor tests do not select FSM profiles or approve an ALL_IN exception.

Next action: coordinator records the final review/test result and commits the
initial tests with the owned implementation; preserve unresolved contracts and
pending target/human gate requirements in the continuation handoff.
