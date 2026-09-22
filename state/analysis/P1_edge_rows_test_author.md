# P1 independent edge-row test author

Objective: protect the nine currently specified B4.2 escape rows, their B7
primitive boundaries, and D-020/D-021 guard and governor composition before
the wider escape controller is integrated.

Owned files: `tests/locked/test_edge_rows.cpp` and this report only. Existing
locked tests, configuration, implementation and shared build files were not
edited. No `src/core/*.cpp` source was read. This is an independent test-author
task using B4.2/B4.4, B6/B7, D-020 through D-023, and public headers. The initial
contract was 76e0360; c5e80b8 clarified phase-change pulses, terminal statuses,
fallback and meaningful profile scope before these new tests were established.

The new file contains 34 cases:

- All 256 selected-mask values: exactly the nine supported low-bit masks are
  accepted (144 values including ignored high bits). Unsupported masks are
  rejected before validating heading, without treating API rejection as an
  approved fault-recovery strategy.
- Literal defaults and exact/adjacent boundaries: one 1,000 us brake tick,
  120 ms reverse, 200 ms forward, 45/120 degree mirrored targets, strict
  five-degree tolerance using adjacent representable floats, and the 700 ms
  turn deadline. Completion one microsecond before timeout and a target at
  the timeout tie are distinguished.
- Heading capture at each segment entry, fixed captured turn targets,
  reverse and forward correction, fixed rear-wheel bias, late-observation
  segment starts, no backdating, correct moving profiles and terminal zero.
- Initial and mid-turn IMU loss, remaining-angle timing, latched fallback,
  recovery into the next segment, straight-reference recovery, and the
  unchanged original timeout. Healthy nonfinite readings invalidate every
  active phase; unavailable readings preserve the last healthy heading.
- Finite extreme headings, relative offsets after bounded normalization,
  invalid/unsupported/completed/pending restarts, reset, one-shot timeout
  pulses, exact unsigned-time wrap boundaries, and several cumulative wraps
  with every individual call gap below one complete uint32 wrap.
- A fixed-seed 10,000-stream mirror comparison with explicit coverage:
  every supported row appears at least 1,111 times; 5,000 streams use each
  IMU-availability mode; at least 5,000 cross timestamp wrap. All moving
  phases and DONE must be observed. Each paired sample checks phase/status,
  pulses, fallback, mirror demands, finiteness and bounds. These generated
  streams hold heading fixed; separate named cases test changing headings
  and IMU loss/recovery.
- Test-owned Guard/governor composition: completion while white cannot
  leave escape; early black does not end an unfinished script; all-white
  immediately inhibits a moving row and stays latched; revoked permission
  clears duty. Reverse correction is capped, sign reversal brakes before
  accelerating, and terminal braking is immediate.
- Nominal, low and high voltage composition preserves the exact forward
  deadline while applying compensation/caps to duty. The requested 70%
  inner ratio is not asserted as a final electrical or physical ratio.

Validation status: authoring/static review complete; no compiler, test runner
or shared build was invoked by this author. Parent will run the host suite and
record actual results before establishment. Only CHECK/CHECK_FALSE assertions
are used, compatible with DOCTEST_CONFIG_NO_EXCEPTIONS.

Limits: this proves neither full Robot arbitration nor MotorGate/EN writes,
sensor acquisition, physical trajectories, tick timing on the board, inward
heading storage at the real escape exit, B4.3 pushed-out selection, front-pair
selection, three-bit/exhausted-replan recovery, or replanning. Unsupported-row
coverage does not approve those policies. No hardware or phase gate is passed.

Next action: parent builds/reviews these new locked tests with the row
implementation, records evidence and commits the established tests. Once
established, AGENTS R1/R5 locked-test protection applies to later changes.
