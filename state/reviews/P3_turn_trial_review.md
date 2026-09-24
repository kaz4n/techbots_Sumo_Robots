# D124 finite P3 turn-trial scoped review

Date: 2026-09-24. Reviewer: separate same-model, fresh-context agent, independent
of the implementation worker and public test author. This is a review of the
pure request helper, not a review or approval of a powered trial or phase gate.
The date remains before the 28 September P3 scope cutoff and 1 October freeze.

Reviewed AGENTS.md, P3_first_drive.md 3.4, B7, the relevant D022/D023/D051/D059/
D122/D124 decisions, adopted public contract and header, unchanged motion
primitive, new implementation, frozen independent tests and retained receipts.
The reviewer changed only this report and `P3_turn_trial_review_raw/`.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed software slice.

Before oracle freeze, review identified ambiguity about nonfinite yaw exactly at
the turn deadline. The contract now explicitly preserves the existing primitive's
timeout priority. It also explicitly distinguishes INVALID_START/IDLE,
INVALID_HEADING/INVALID, and the retained last primitive status on clock or
safety interruption. These were public clarifications before first execution;
the first implementation and frozen public oracle required no correction.

## Behavior and safety assessment

- Only exact signed -180, -90, +90 and +180 starts are accepted. Nonfinite initial
  yaw and all other angles consume the attempt, publish zero, and preserve finite
  unaccepted-start report fields. A repeated start is passive, including pulses.
- LEFT reflects the actual yaw and swaps wheel requests around the existing
  positive relative turn. This preserves the exact +180 tie in the primitive
  while obtaining a physical left request. It never changes actual `imu_ok`.
  Negating finite float yaw cannot overflow; the unchanged relative primitive
  reduces yaw before subtraction and retains the strict tolerance boundaries.
- All new work is bounded: no new loop, clock read, heap use, I/O or transport.
  A distinct active timestamp delta at or above half the micros range faults;
  ordinary wrap is accepted. CLOCK_ORDER precedes STOP, STOP precedes EDGE,
  and all precede stepping the motion primitive or completing the brake interval.
- Exact duplicates and terminal calls clear action pulses only, as specified.
  Because duplicates deliberately ignore changed safety input, future actual
  integration must retain owner-level safety arbitration. This helper cannot
  establish that integration or grant motor permission.
- The unchanged B7 Turn retains its proportional/minimum/maximum requests,
  overshoot correction, strict tolerance, original 700 ms timeout, latched
  remaining-angle fallback and non-extension on IMU recovery. Timeout wins the
  exact completion/nonfinite-yaw deadline tie. All examined duty outputs are
  finite and bounded by TURN_DUTY.
- DONE and TIMED_OUT enter BRAKE at the observed caller timestamp and retain
  distinct primitive outcomes. A delayed call cannot backdate completion or
  consume the new 500 ms interval. BRAKE ignores heading and retains zero duty;
  STOP/edge/clock still interrupt. Completion and termination flags distinguish
  valid timestamp zero from no observation. Invalid heading does not fabricate
  a valid turn completion.
- The config diff from D123 adds only TURN_TRIAL_BRAKE_MS=500 and its unlocked
  literal registry expectation. Existing motion, Robot, application, MotorGate,
  host build definitions, B16 values and prior locked tests remain unchanged.
  The helper has no caller in the actual application in this slice. Therefore
  R1/R5/R6 integration, native route and target footprint are not newly proved.

## Validation

The public test file was frozen before implementation execution. The reviewer's
private source was also authored before permission to execute was received.
No board connection, staging, upload, reset, MCU read or motor operation occurred
in this review.

| Evidence | Result |
|---|---|
| Independent public oracle, normal | 23 cases / 9,300 assertions PASS; zero skips |
| Same frozen public oracle, ASan/UBSan | 23 cases / 9,300 assertions PASS; zero skips |
| Unchanged full host regression, normal | All six targets PASS: main 1,519; Gate 187; B4 M0/M1 18 each; DRIVE_TEST M0/M1 27 each |
| Canonical config registry | 2 tests PASS |
| Reviewer private properties, normal and ASan/UBSan | 3 groups / 1,309,352 checks per profile PASS |
| Independent hash binding | All 10 frozen files and all 36 established locked files match; archived public oracle matches current file |

Private properties use an independent remainder-based angle oracle across
115,210 paired right/left observations, translated initial yaw, wrap, strict
tolerance and overshoot. They also exercise STOP/edge at each millisecond through
700 ms across three clock origins, terminal passivity, timeout at NaN, half-range
clock rejection, and a delayed timeout followed by the full observed brake
interval. Compilation and execution produced no diagnostics in either profile.

Bound source: `turn_trial.cpp`
`cc88727fa5a19117ceb88ad3c4b068ea4df815a8570f7d5c7b80c23ae4d3d62f`.
Bound public oracle:
`ab5547d2e0100b1aa501e2666c43068bc5bba9831f5a998c1beaed211ab5bbd1`.
Bound contract:
`ee5f22a3498e3a25422dbb6e87d4bd37ffbc2b6c194a100ee639deae186842b6`.

Receipts and exact commands are in `../analysis/P3_turn_trial_raw/`.
Reviewer source, compiler/run logs, command/source hashes and independent
bindings are in [P3_turn_trial_review_raw/](P3_turn_trial_review_raw/), especially
`private_validation.json` and `evidence_bindings.json`.

## Verdict

PASS for D124's pure finite turn-request helper and its host evidence.

This does not establish actual GO admission, PIVOT Governor/MotorGate routing,
edge escape behavior during a real trial, target RAM/WCET, physical settling,
measured turn accuracy, measured fallback calibration, or a human P3 gate.
COMPLETE with primitive TIMED_OUT remains a timeout; even primitive DONE is not
physical turn-accuracy evidence. Next work is actual isolated-trial integration
under the unchanged safety authorities, followed by target and independently
authorized physical validation.
