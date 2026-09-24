# D134 frozen source review

Private probes were frozen before these new implementation body reads. Reviewed
the four core files against adopted 27bc075a interfaces and tooling SHA
`500ce3c595803bd4c5395e390b6608b914dbf89dff5b18d0d4bcec3bd7cb12fd`.
No material source finding at this stage; execution remains pending.

- `types.h:18-33` uses exact enum cases, mandatory1..3 and optional ARC/WAIT;
  every other underlying value is unavailable. Typed flags and default-range/
  availability assertions reject invalid represented configuration. Raw overflow
  is separately checked before target compilation by staged admission.
- `countdown.cpp:369-383` retains the original all-six branch and service cycle;
  reduced mode scanning is bounded at six candidates. Construction/reset use
  the validated default. There is no input selector, new state or setter.
- `openers.cpp:65-74,220-225` resets before rejecting disabled public starts,
  retaining finite-heading and mode-kind admission. Existing terminal paths
  return INVALID/zero indefinitely; WAIT clears per-call cue/phase/timeout state.
- `fsm_robot.cpp:542-559` cancels all motion before availability dispatch. A
  rejection invokes no script and sets SCRIPT_START. Existing line815-828 final
  request logic changes the selected state to STOPPED and inhibits/zeros duty;
  contact commitment, governor and actual MotorGate authority remain unchanged.
  No new use of modeAvailable appears in recorder, display or historical ID
  validators. D034 routeNormal and D055 WAIT phase sequencing are unchanged.
- No runtime heap, I/O, clock, unbounded loop or extra object field is added.
  The six-iteration menu bound is source-inspected, not measured target WCET.
- `board_tool.py:219-245` rejects malformed source, splices and code-level
  digraphs before the both-absent return. It counts switches before stripping
  directives, refuses partial/conditional/macro definitions and requires one
  canonical single-digit declaration per switch/default before conversion.
  Disabled defaults fail. `stage:290` checks the actual copied config after the
  unchanged D132 admission. No compiler/profile/source-hash/upload policy changes.
- Shared lexical helper changes only parameterize error labels and names with
  the original D132 defaults retained. D132 accept/reject regression execution
  is still needed. Historical source pins still determine upload authority;
  both-absent compatibility does not manufacture new core definitions.

Coordinator runner audit: input freeze checked before build, copied variants
use exact one-occurrence substitutions, each unique /dev/shm TemporaryDirectory
is owned and released, and public LastTest plus private command receipts are
saved before cleanup. All command failures remain nonzero. The private runner
preserves actual compiler/defines/profile/sanitizer flags and excludes only the
two public test objects while retaining real production objects and test main.

First public-build failure adjudication: retained `default11.json/.txt` reports
build exit2 before any CTest/private C++ execution. At new fixture line109 the
compiler rejects `last = {};` and lists RobotResult's implicit copy/move
assignment candidates. `fsm.h:452-517` defines the aggregate's default member
values. The proposed sole replacement `last = fsm::RobotResult{};` creates the
typed default aggregate explicitly and preserves the reset-value intent,
including nonzero enum/configuration defaults. This is an acceptable fixture
syntax correction, with no stimulus/assertion/production change. Retain the
original failure and frozen source; validate syntax and refreeze before rerun.
At this adjudication no corrected compile result or C++ pass is claimed.

Focused behavioral failure adjudication: `default11_focused` completed20 cases
with19 passing and one failed new case for each M0/M1. The material defect is
the draft oracle at `tests/locked/test_mode_availability_safety.cc:41-44`, which
requires zero for every white mask. This conflicts with B4.2/D021. D134 has no
edge, governor or MotorGate production diff; only the opener-dispatch guard
changed in fsm_robot.cpp. This is a test-oracle correction, not a motion-policy
change or evidence that an established protected test should be weakened.

Independent literal first-row expectations, with nominal battery and unchanged
heading: masks1/2/3/6/9 brake; mask4 requests(+.80,+.56),8(+.56,+.80),12(+.80,+.80),
5(+.80,-.80),10(-.80,+.80); masks7/11/13/14/15 latch WHITE_PATTERN and inhibit
under D048/D020. Established protected `test_edge_rows.cpp:208-212` and
`test_edge_escape.cpp:219-223` contain the same moving-row expectations.

Recommended narrow repair retains all modes/masks/GO-versus-after-GO stimuli
and initial EDGE_ESCAPE/line/contact assertions. Add exact NONE-versus-
WHITE_PATTERN fault checks, permitted ordinary rows versus disabled fault rows,
and exact immediate zeros for brake/fault rows. At GO the prior600ms governor
interval permits exact moving vectors. On the following tick after an opener,
B6 can require reversal-zero or acceleration slew, so immediate directions may
include zero; assert correct signs and .80 cap. A further unchanged observation
40000us later remains before the200ms forward/700ms pivot deadline and permits
the exact literal vector for all moving rows. Assert M1 active PWM channels and
quantized receipts; M0 callbacks remain zero. Do not replace row validation with
only a cap or final state check. Retain original oracle/failure and explicit
decision/refreeze provenance before rerun. Correction remains unexecuted here.

Corrected draft SHA901b735c69f13def646b033539121e55f289035e5a6ee206dbb9ffa1802d63b0
was then inspected before execution. It implements the narrow repair above,
including exact first-observation B6 budget/reversal checks and40ms literal-row
checks, rather than accepting arbitrary capped movement. M1 PWM uses each
fixture channel's independent literal period and floor quantization; inactive
channels stay zero and signed receipts match. M0 remains disabled/zero. Other
three new cases are unchanged. All41 prior protected source hashes match the
original425c8a97 core freeze. No remaining material source issue in this repair;
successful corrected frozen execution is required before closing the finding.

The corrected public case subsequently passed in
`default11_focused_retry1_LastTest.log`: all20 public cases passed separately
under M0/M1. This closes the erroneous blanket-brake draft finding for that
focused configuration; the rest of the matrix remains pending.

First private C++ execution then failed one of six M0 cases: the stale-snapshot
case at private_modes.cc:197/199/200 observed OPENER/.85 instead of SEARCH/<=.80.
M1 private execution did not run after the M0 failure. The original frozen
probe SHA7e976e23 and exact command/output receipts are retained. This is an
independently diagnosed private-probe stimulus error, not a production defect:
the helper observes release+1.500/1.501/4.500s, then the case jumps toGO5.100s.
B3/D024 and countdown.h:163-166 admit snapshots only in[4.800,5.100), excluding
GO. No observation in that window exists, so the presumed saved front is absent.
With current0, DIRECT therefore has no exit trigger and legitimately requests
OPENER_DUTY_MAX=.85. D034 routes current perception only after an opener exit;
the same probe's current2/8 variants trigger exits with their live targets and
pass. Services/Direct snapshot logic has no D134 production diff.

Proposed stimulus-only repair, not yet applied/executed: retain FC through the
calibration helper, admit fresh FC observations at4.900/4.901s, switch to each
current0/2/8 at5.060s and observe again5.061s, thenGO5.100s. B5's30ms clear
deadline then expires atGO while the snapshot retains a front bit from the
pre-GO window. Assert actual captured-front and final current-mask preconditions,
GO, and keep every original routing/noATTACK/no-contact/fault/cap assertion.
Archive the original probe and manifest, record correction provenance and
refreeze before any rerun. Do not merely change SEARCH to OPENER or raise caps.

After separate spec-only author agreement and root GO, the actual repair used
the simpler independently proposed timeline: no early target; fresh FC at5.000
and5.001s, one raw-current0/2/8 observation at5.060s, thenGO5.100s. Explicit
preconditions prove snapshot2 beforeGO andatGO, current2 beforeGO and requested
current0/2/8 atGO; an added physical hold check remains beforeGO. Every prior
assertion is retained, and the preceding five cases remain byte-equivalent.
The failed original source and manifest are saved as private_modes_first.cc and
private_freeze_first.json. New probe SHAe15baf36, with exact full hashes and
comparison receipt in private_correction.json. Reviewer edited no manifest;
root owns refreeze. Corrected execution is still pending at this entry.

D134's subsequent full default build stopped before CTest on a pre-existing
CMake integration defect: timing-only test_push_through_timing.cc was attached
to ordinary push targets with timing0. Retained default11_full_retry1 contains
the exact diagnostics. The minimal root fix moves the unchanged test source to
existing timing_evidence M0/M1 targets with timing1, preserving all18 targets.
Static review approves this reassociation; no test/assertion or production
change is present. Full ordinary rerun remains required. Positive20 configured
regression must separately run the whole push family under timing1 plus all five
D131 cases from the timing family, while all original D129 assertions run under
duration0. No passing test branch may substitute for the positive-only bodies.
My earlier P4 review is explicitly corrected: the old16-target full PASS predates
the timing-only test addition, so did not prove the final P4 CMake integration.
