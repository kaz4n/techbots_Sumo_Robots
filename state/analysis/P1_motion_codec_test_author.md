# P1 B7 motion and B15 codec independent test authorship

Date: 2026-09-22, Asia/Dubai. Active scope: P1 host-only under D-016.
Objective: derive public-contract tests independently of implementation, retaining
the accepted D-022 heading correction and D-023 duty-only voltage compensation.

Sources read: AGENTS.md, .claude/agents/test-author.md, BEHAVIOR.md B0/B6/B7/B15,
DECISIONS.md D-022/D-023, committed motion.h/logframe.h contracts, governor.h,
types.h and config.h. No src/core/*.cpp implementation was opened. The schedule
date matches PLAN.md Tuesday 22 September; no gate acceptance is implied.

Modified files owned by this author:
- tests/test_motion.cpp: 30 doctest cases.
- tests/test_logframe.cpp: 19 doctest cases.
- state/analysis/P1_motion_codec_test_author.md: this report.

Motion evidence requested: signs/gain/caps; strict tolerance; immediate/terminal
zeros; exact and adjacent microsecond/millisecond deadlines; unsigned time wrap;
initial and mid-command fallback; last-valid remaining angle and direction;
recovery/no extension; invalid fields; reset/restart; continuous arc sweep;
maximum accepted durations whose final tick crosses a full start-time wrap.
Two fixed-seed suites sample 10,000 command pairs each and assert exactly 5,000
healthy and 5,000 unavailable-IMU cases per suite. Mirror properties exclude the
exact 180-degree tie, which has its separate clockwise convention test.
Governor integration feeds a 1 kHz timeline at 9, 11.1 and 12.6 V and checks
unchanged deadlines, final caps, single compensation and immediate zero at end.

Codec evidence requested: literal 25-byte/8-byte fixtures, little endian and
two's-complement signs, accumulated yaw, exact half-away rounding and adjacent
floats, saturation/status for every numeric field, all nonfinite fields, all
256 enum/mask/flag encodings, whole-output zeroing, and exact event ticks/wrap.
All assertions use CHECK/CHECK_FALSE, compatible with the no-exceptions build.

Validation at handoff: source inventory reports 49 new cases; git diff --check
reports no whitespace issue. No build/test pass is claimed by this author;
the coordinator owns shared normal/sanitizer builds and final evidence.
The first coordinated compile found an unsupported two-argument CAPTURE macro;
split it into two one-argument calls without changing any test expectation.
The original failed compile is preserved in P1_motion_codec_tests.txt; rerun
results belong to the coordinator's subsequent evidence receipt.

Ambiguities/limitations: none requiring invented assertions in this bounded
contract. Tests exercise request modules and codecs, not arbitration, motor
permission, physical travel, recorder cadence/storage/overflow or Bridge I/O.
The B15 never-drop-events capacity question remains outside this codec scope.
Next action: coordinator builds/runs unchanged tests, routes failures to the
responsible implementation owner and records final results in state/.
