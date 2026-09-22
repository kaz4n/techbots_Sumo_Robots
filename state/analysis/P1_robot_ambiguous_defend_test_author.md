# Independent D-061 Robot ambiguity tests — 2026-09-23

Objective: prove the newly selected bounded ambiguous DEFEND behavior through
the production `fsm::Robot::step`, while preserving the existing valid-bearing
turn API and all earlier tests.

Sources: committed public contract 34c48d0,
`P1_ambiguous_defend_contract.md`, BEHAVIOR B2/B5/B7/B10, D-026/D-060/D-061 and
public Robot/Fusion/DefendTurn declarations. The source-independent author did
not read any implementation `.cpp` or implementation-only header, run a build,
operate hardware or commit. Owned only the new test file and this report for
this task. Every earlier test, including the 10,000-stream locked property,
remains unchanged.

`tests/test_robot_ambiguous_defend.cpp` contains 16 CHECK-only cases using the
existing real-Robot scenario helper. Application and zero-duration receipts are
explicit synthetic settings fixtures, not physical MotorGate or timing proof.
The new file directly includes `<initializer_list>` for portable braced ranges.

## Independent expectations

- Initial both-side/both-rear ambiguity, both-side plus either/both lower rear
  bits and ignored high bits retain DEFEND_TURN, ordinary logical permission,
  exact governed zero and no invented contract fault/first-duty event.
- A single side plus both rear bits supplies a valid higher-priority bearing
  and retains the original mirrored turn behavior.
- Confirming the ambiguous pair while DIRECT was requesting 0.85 forward
  immediately brakes both governed duties, without inhibiting ordinary permission.
- A later usable side appears only after the actual 30 ms confirmed-clear interval;
  it captures the current 40 degree heading plus the real -90 degree side bearing.
  Arrival at -50 degrees proves capture was neither invented at the original
  zero heading nor retargeted from later memory observations.
- Both completed and still-active delayed turns retain the first ambiguous
  entry's 800 ms deadline. A newly usable side on that exact deadline loses to
  expiry, while confirmed current front or clear takes its normal priority.
- The front-priority case counts TRACK observations 1/2 before ATTACK on 3,
  rather than bypassing qualification at the expired wait boundary.
- Exact 799999/800000 us, repeated timeout/re-entry and a concrete uint32 wrap
  retain bounded waits. Forty altered duplicate observations cannot supply a new
  bearing, STOP, invalid heading, receipt or extended deadline.
- Edge preemption and real escape completion discard the old wait deadline;
  STOP preempts at expiry and remains latched; reset permits a new full interval.
- Valid bearing history still supports conflicted readings and the existing
  700 ms turn/800 ms defend timing. Missing IMU still permits a real relative
  bearing to use its 180 ms fallback after delayed capture, without extending
  the original wait or inventing a healthy yaw measurement.

No arbitrary Robot state or private timer mutation is used. Sparse observation
streams are intentional and do not fabricate missed sensor samples. Root
selected D-061 before these dependent expectations; the preserved original
runtime failure is evidence of the prior policy gap, not a passing run or an
unsafe-motion claim. This suite is not a replacement for physical validation.

Author checks: public names/types, literal timing arithmetic, no REQUIRE,
explicit include dependencies and no trailing whitespace. No test was executed
by this author; coordinator normal/sanitizer runs must provide execution evidence.

Narrow fresh-review addition: two new cases explicitly anchor the wait on the
actual escape-exit tick that first selects ambiguous DEFEND, even though that
tick forces braking and defers motion execution. They check 799999/800000 us
from that exit with wrap, and first later observations at 800000/800001/1500000 us
that must already select SEARCH. Only the following observation may start a new
bounded retry. This follows existing D-061 wording; it changes no contract and
retains every original 14-case predicate. No build or implementation read was
used to construct the new expectations.

Initial 14-case SHA-256:
`7FF5F948432775A971F70A0B316B3EAABE1AB10D3A63FD1EB490ABB88C43CE34`.
Re-frozen 16-case SHA-256:
`19B8308B551B5C70F1282C96A85D070EA05ADBA54CD70D94D0A8A815E498C184`.
Next action: coordinator/fresh reviewer checks the new contract alignment, then
runs the original locked property and complete host suites unchanged.
