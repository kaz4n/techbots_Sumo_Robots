# Independent production Robot test author — 2026-09-23

Objective: test the actual `fsm::Robot::step` transaction against B0–B15,
R1/R5 and D-060, rather than reconstructing an arbiter in a test harness.
These are host software scenarios. They do not constitute a physical acquisition,
MotorGate, motor movement, WCET, recorder transport or phase-gate verdict.

## Independence and ownership

Read the public core headers, BEHAVIOR, D-060, the normative
`P1_robot_contract.md`, its adopted proposal sections2–5 and event metadata audit.
No implementation `.cpp` or implementation-only header was read. No build,
hardware operation, commit, configuration change, existing-test amendment or
shared state-ledger edit was performed by this author.

Owned new files only:

- `tests/robot_scenario.h`
- `tests/test_robot.cpp` —28 cases
- `tests/locked/test_robot_safety.cpp` —13 cases, including10000 streams
- `tests/test_robot_events.cpp` —24 cases
- this report

The framework uses CHECK/CHECK_FALSE, with no REQUIRE or exception dependency.
The new locked file becomes protected when established; existing locked files
remain unchanged. All expected values derive from the public contracts and
literal defaults, not observed implementation output.

## Receipt fixture and evidence assumptions

`Rig` sends electrical opponent polarity, four raw QTR timings, raw continuous
yaw, logical buttons, battery validity and explicit freshness to real Robot.
It supplies a receipt matching the preceding result token, never the new token.
The default mock applies the preceding permitted request instantaneously at its
source timestamp and reports a synthetic zero-microsecond completed duration.
Tests can inhibit or downscale that reported application and supply explicit
application/completion timestamps. This is a deliberately idealized output-stage
mock, not a claim that real firmware executes instantly or motors follow duty.
The helper does not select states, simulate a gate or duplicate Robot arbitration.
Only fresh results replace its pending receipt; duplicate calls are not reapplied.

The helper qualifies NONE/START/NONE and menu gestures through the real button
path. Normal GO scenarios supply two real logical calibration observations in
the approved window and check the full5100000us release-to-GO interval. Long
gaps are explicit test inputs; they do not fabricate missed observations.

## Covered boundaries

| Area | Independent production assertions |
|---|---|
| Initialization/selection | Inert BOOT, initialization latch, BOOT-entry START suppression/no replay, six modes captured only on accepted release, four typed service requests including unavailable DRIVE_TEST, invalid service-only bias ignored. |
| R1/STOP | Full5100000us hold with exact/adjacent endpoints and wrap; qualified MODE and immediate STOP win GO ties/delayed GO; BOTH full debounce-plus-long-hold; STOP remains inhibited. |
| R5 | All16 line masks, both already white before GO and newly white after GO; strict299/300us classification; three/four-white inhibition; raw mask precedence; persistent row replacements1–3 and fourth fault; no black-only early exit; exit brake; new-white replacement during reverse; head-on180ms reverse/right default; front-row mirrors. |
| Front/contact | DIRECT exit counts centered observations1/2/3; off-center front retains group priority without full-duty contact; same-tick ATTACK impact;20 confirmed close observations with25 duplicate calls; loss exact30ms debounce and one-call brake before residual SEARCH/DEFEND; edge/STOP clear contact without provisional CONTACT. |
| Scripts/history | SIDESTEP/ARC front ignored during initial pivot then current-perception exit qualification; complete WAIT ordered cue and right pivot; natural DIRECT/WAIT deadlines; absent-at-boot IMU timed pivot; mirrored opener outputs; DEFEND800ms SEARCH exit then next-tick side routing; raw yaw history survives GO and stuck faults survive clearing until reset. |
| Actual-duty predicates | Inhibited actual output cannot qualify a stall despite full requested ATTACK; exact1s actual-duty qualification; pushed-out rear predicate differs for actual forward versus inhibited receipt; two actual re-flank SWING entries alternate, third deflection admission is denied into ALL_IN, then all-white still inhibits. |
| Governor composition | Low-voltage approach remains0.60, centered contact reaches1.00, edge brake is immediate and reverse remains0.80; all generated demands finite and bounded. |
| Transaction defense | Immediate duplicate ignores changed STOP/stale/yaw/receipt and clears pulses; reset retains token monotonicity and rejects old feedback; missing/mismatched/nonfinite/disabled-nonzero/out-of-window application faults; inhibit/zero/downward settings accepted, reversal/increase rejected; stale input cancels calibration first; invalid battery/healthy yaw latch STOP; missing IMU and calibration failure do not invent a veto. |
| Events | Literal START/GO/source time/state metadata; persistent-white entry versus new-white; FIRST_NONZERO only from actual receipt, downward quantization and tiny nonzero with zero encoded bytes; receipt-before-current order across wrap; PHANTOM raw-to-match projection; one-shot warning/new-fault episodes; literal semantic metadata for all families;21-entry ordered prefix with separate capacity/semantic rejection counts. |
| Frames | START epoch0, actual delayed receipt identity, pre-GO raw yaw/post-GO local yaw, raw pre-bias gyro, actual downward duty,20ms exact cadence and explicit skipped slots, invalid/clamped emission with retained status/loss flag and no false skip, missing application loses candidate, one final canceled/stopped frame then no repeat. |
| Timing | GO receipt begins membership, one final stopped tick included,999/1000/1001us strict overrun and completion timestamps, missing/malformed member duration marks incomplete without motion fault, nonmember countdown duration neither counts nor warns. |

Fixed-seed stream seed `0x36a891d5`:10000 independent real Robot instances, each
with a genuine qualified release, pre-GO hold observation, scheduled long-gap GO
or explicit STOP, and8 randomized fresh observations. Half the hold intervals
cross micros wrap. Assertions require8000 GO outcomes,2000 canceled outcomes,
5000 wrapped holds, all16 masks each sampled more than4000 times and explicit
STOP coverage. Randomized masks, target bits, finite yaw and finite low/normal
voltages exercise R1/R5, bounded output and valid bounded event metadata; this
does not claim exhaustive state-space exploration or physical safety proof.

## Limits and next action

Focused coverage is intentionally not every Cartesian product of all existing
component tests. The QTR pivot-warning timer is not independently driven through
its full continuous1500ms episode at Robot level here; its sensor/motion coupling
deserves a later dedicated scenario if needed. UINT64 token exhaustion and
uint64 statistic saturation are not reached by billions of Robot calls or unsafe
private-state mutation. Existing arithmetic/component tests retain their own
coverage, without being relabeled as full-Robot proof. Complete B11 limiter
window expiry, all SEARCH history TTL combinations and every script turn-in
mask/tolerance remain primarily in independent component suites.

Author validation: source/static checks only; no local compile or execution.
Coordinator must run normal and sanitizer host suites, inspect any failure
against the public source requirement, and record their separate receipts.
Do not change these independent expected predicates merely to match source.

Static pass found no REQUIRE/exception/allocation dependency, no trailing
whitespace and no test/helper function above60 lines. The deliberate receipt
time-wrap fixture uses the literal default-mode GO offset5163000us; no numeric
timestamp sorting is assumed. Public names and field types were checked against
the headers. Review handoff hashes:

| File | SHA-256 |
|---|---|
| `tests/robot_scenario.h` | `1B5E5524373902D21F4601C9BEF215359D977E11DDB9DF9C8FFC2E1AC10B9452` |
| `tests/test_robot.cpp` | `A52B2C152F972EE87AEE2F707C20104882A0310F525A41A1F3FB92D1C6BE7CE3` |
| `tests/locked/test_robot_safety.cpp` | `349BC3788EEBE561B06207796B9B65234F568F38C5E304D2BAC26EA0CD112C37` |
| `tests/test_robot_events.cpp` | `AC03C5144367C7CF7EDD62A9E026927D7DC56B3C374B97191FFE1EE004EDFFDD` |

No expected assertion was changed in response to an implementation run; none
has been run by this author. This report is not a passing test receipt. Final
freeze notification follows the coordinator's independent static review.
