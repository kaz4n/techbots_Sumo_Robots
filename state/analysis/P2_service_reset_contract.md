# D103 optional local service access after STOP

2026-09-23 under D051/D075, after D1029a8797d. This explicitly extends D096's
terminal STOP behavior only when SetupGrants.local_service_reset is true. The
new flag defaults false; app.ino retains SetupGrants{} and no physical grant.
It enables a local evidence-service transition once per boot, never native-owner
recovery or full control rearm. All established default-off and locked tests stay
unchanged. Read P2_service_reset_options.md and D095/D096/D101 contracts.

## Actual stopped observation

With the flag false, preserve the exact existing first STOP, real final tail,
then passive STOPPED lifetime. With it true and before a service reset, finish
that same real tail, verify the recorder is SEALED or EMPTY, then enter new
RuntimePhase::STOP_OBSERVING. This phase executes at most one actual transaction
per due original-grid release: same ADC/buttons/battery, actual opponents,
Robot, inhibited MotorGate, recorder, display/dump cancellation, actual C.
No between-epoch service/poll loop or invented decision/receipt/timestamp.
No QTR/IMU setup/start/advance resumes after their initial cancellation. Early
calls retain existing clock-only admission and stall guard. All work is in S..C.

Keep CONTROL+genuine absent/fault QTR before logical reset. Existing Robot may
latch LINE_CONTRACT as stopped samples expire; retain that fact rather than
feeding RAW into STOPPED or inventing healthy line data. Non-button source
faults do not by themselves forbid evidence-service reset. Runtime/Transaction
fault, ADC owner fault, BUTTON_CONTRACT, exhausted token or failed actual motor
receipt do forbid it. An invalid actual motor receipt during STOP_OBSERVING or
the service-only lifetime immediately terminally fails Runtime, after preserving
D101 transfer cancellation and MotorGate inhibition. No such fault is recoverable.

## Local gesture and pending intent

Only after the completed real tail, consume the current genuine fresh Robot
button observation and exact explicit A1 evidence. Require current admitted
button_available/button_updated, healthy ADC owner, bounded real source/decision
time, and matching consumed/valid/zero disabled MotorGate receipt with STOPPED
fault. No second ADC reader or second Robot/Menu step. Replayed/absent/stale/
invalid input cancels pending gesture history; never interpret it as NONE.

Qualification uses existing constants, no new timeout:

1. New NONE observations span BTN_DEBOUNCE_MS from first A1 completion.
2. Then MODE alone spans BTN_DEBOUNCE_MS from its first completion.
3. Begin the complete BTN_LONG_MS hold at the actual decision that qualifies
   MODE. Source completion before this anchor must not underflow into a full hold.
   Observe MODE on/after the deadline; an observed release on that deadline wins
   and cancels, never retrospectively completing the hold.
4. After the hold is observed complete, NONE alone spans BTN_DEBOUNCE_MS to
   qualify release. Any MODE/START/BOTH contamination during release cancels
   and requires a new neutral qualification. START/BOTH or early release during
   MODE/hold also cancels. Held MODE on entry cannot skip neutral qualification.

Generate one pending intent before C, retaining that release's real source start,
decision/token and old fault facts. Do not reset on that decision. At the next
actual S, after successful open and Runtime clock admission, require intent age
from its real source start <=BUTTON_SAMPLE_MAX_AGE_US and non-reversed chronology.
At5000us it is eligible;5001us expires without reset or refreshed timestamp.
The original C must have completed. Normal source-continuity checks still run.
A new press in the next acquisition is handled by the freshly reset real Robot;
it cannot grant motion or bypass post-reset neutral qualification.

## Guarded Transaction reset, inside the next epoch

Add public bool Transaction::resetStoppedRobotForService(), with no caller proof,
token, time or mutable-owner access. It returns false without owner mutation unless:

- Phase is ACQUIRING after a successful real open, before decide, and no prior
  accepted service reset in this Transaction lifetime.
- Internal proof records at least two consecutive successfully completed,
  timing-valid real STOPPED decisions (initial STOP plus genuine later tail),
  with gate STOPPED, no release/GO/motion, fresh nonzero non-max token, intended
  zero/disabled output, consumed matching valid actual zero/disabled receipt,
  fault exactly STOPPED, and ACCEPTED or OUTSIDE_ATTEMPT recorder outcome.
  A nonqualifying completion resets that streak; FAULT cannot recover. Capture
  eligibility before open clears the report, never from a caller-supplied result.
- Retained recorder phase is SEALED or EMPTY, not RECORDING/DRAINING/INTERRUPTED,
  with no terminal exhaustion. EMPTY remains no evidence, never a fabricated dump.

On success notify the existing recorder via onRobotReset, reset only Robot,
clear previous applied feedback, and consume the one-shot eligibility. Preserve
MotorGate object/fault/token/initialization, recorder arrays/summary/high-water,
Transaction ACQUIRING/current S, last actual clock/decision chronology and Robot
next-token. No Gate.reset/begin, native setup, pin operation or clock rebasing.

Runtime ordering: actual open/S and admission -> expiry/proof checks -> existing
Transfer.onRobotReset -> guarded Transaction reset -> actual clock observation
-> acquisition -> D/Robot/Gate/recorder -> outputs -> C. Unexpected refusal of a
qualified pending request is a terminal invariant failure. An active Transfer
is canceled by reset notification; native poison/ownership never clears.
Reset work and any failure cleanup remain inside S..C. A fault cannot invent a
successful C. Logical reset is not hardware reset-cause evidence (UNKNOWN only).

## Permanent service-only projection and lifecycle

After success, set RuntimeReport.service_only true permanently, record old
contract/escape faults and reset_from_token, and clear the old initialization
latch for honest service admission. service_reset_pending clears; the reset
action gets a one-step service_reset_fresh pulse even if later work faults.
No full RobotResult duplicate is retained. Runtime returns to RUNNING with an
explicit service-only state; source suspension remains separate from final-tail
tracking so clearing an old tail cannot restart QTR.

Before the first new BOOT input, force canonical explicit RAW/CALIBRATION ABSENT
QTR and canonical explicit unavailable IMU, with no fresh source/time/sequence,
no reused yaw/gyro and no bias reset. The same ADC/InputOwner and opponent owner
provide actual fresh evidence; service readiness requires their retained setup
success, current valid buttons, available valid battery and fresh opponents.
This is service readiness, not restored full-control sensor readiness. Preserve
all old native source/shutdown/expiry diagnostics and the committed QTR bank.
imuEvidence remains its retained diagnostic; decisionInput is explicitly absent.

RAW remains forced for service BOOT/IDLE even with a committed threshold bank;
every match START/menu exit remains inhibited, and Gate keeps STOPPED regardless.
For an actual subsequent STOPPED tail, use CONTROL+ABSENT rather than forbidden
RAW in STOPPED. A second STOP receives one real tail then permanent passive
STOPPED; there is never a second service reset. A service fault is terminal.

Skip Calibration.step/reset during service-only epochs. Preserve its actual
prior report/bank; do not report a fabricated rejection or start an unavailable
capture. Add app-owned ServiceActionReport {fresh, service, request_token,
status}, status NONE/UNAVAILABLE. A fresh genuine QTR_CAL or DRIVE_TEST request
in service-only IDLE sets UNAVAILABLE for that real token; it never modifies
RobotResult/menu intent. Other service requests leave no fabricated outcome.
Clear only action/reset fresh pulses on every Runtime::step, including passive
calls; retain last action identity/status. Existing genuine LOG_DUMP uses D101
actual inhibited authority and the same retained recorder, with no new protocol.

For display only add DisplaySample.service_unavailable defaultfalse. It changes
QTR_CAL selection to the existing C+cross glyph when service-only; DRIVE_TEST
already uses D+cross. All other glyphs, battery/fault strips and control inputs
are unchanged. Runtime applies this projection flag while selecting either
unavailable service; do not rewrite the saved calibration report or Robot result.
SENSOR_VIEW truthfully shows actual opponents and unavailable lines.

## Verification and limits

Independent tests use these public interfaces and actual Runtime/Transaction/
Robot/Gate/recorder, both motor configurations and synthetic configured buttons.
Cover defaults, genuine tail proof, every rejected Transaction phase/history,
EMPTY/SEALED/active/draining/interrupted/exhaustion, exact debounce/hold/release
boundaries/source-before-anchor/wrap, held/bounce/stale/replay, pending4999/5000/
5001us, original-C/new-S/post-reset clock failures, actual failed inhibition,
ADC/button faults, real QTR expiry while STOPPED, source cancellation once,
no reconstruction, preserved bank/native diagnostics, first RAW BOOT with real
service prerequisites, same source/token chronology, unavailable actions/pixels,
all attempted START/mode exits, second STOP/passivity and permanent UART poison.

Positive path: actual accepted attempt -> STOP -> real tail/SEALED -> genuine
local reset gesture -> actual BOOT/IDLE/menu/LOG_DUMP -> unchanged saved payload,
status/loss/summary plus strict independent receiver roundtrip. No fixture-reset
shortcut or fabricated source authority. Run full normal/sanitizer regressions,
target-source/ELF/startup/loader memory audits and fresh separate review. D102's
remaining capacity is not proof this larger image fits. Refresh the same inert
keys only after exact source review; no upload scope is added.

Physical A1/grants/UART, loadedRAM/stack/full800us and all human gates remain
pending. Physical reset/restart for a later match is separate from this inhibited
service lifetime. Calibration-snippet delivery and bench software remain next;
this task does not claim the full project or physical B8 is finished.
