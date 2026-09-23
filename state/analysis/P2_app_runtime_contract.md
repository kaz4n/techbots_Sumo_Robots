# D096 native application runtime

2026-09-23 Asia/Dubai, baseline38d71d3. Previous goal turn PROGRESS: D095 actual
transaction390005c passed real tests/target/review. D051/D075 select this next
P2 integration. This supplies a real native app scheduler, not another bus or
strategy layer. Physical grants, electrical acceptance, all-sensor800us and gates
remain unverified. Source guards cannot establish complete WCET by addition.

## Fixed ownership and setup

Runtime owns the actual D095 Transaction, ADC InputOwner, IMU Estimator and QTR
Calibration. One native binding owns existing power::Reader, line_qtr::Reader,
opp_sensors::Sensors, imu::Acquirer and optional UnoQMatrix. SourcePort directly
forwards their public operations with typed results. Its owners outlive Runtime.
No heap, default sensor measurement, constructor/destructor I/O, retry/reconstruction,
remote command or new hardware abstraction framework. Use existing callbacks and
installed native code. Inputs to Robot always use explicit line/IMU/buttons.

begin is one-shot and invokes Transaction.initialize before any other native
operation. Failure selects runtime TRANSACTION/FAULT and does not retry Gate.
Repeated begin is passive false. Validate all required callbacks for the granted
sources; an invalid required port terminally aborts after Gate initialization.
Ungranted sources perform no setup/read/cancel callbacks. Their absence is not
success. Default SetupGrants are all false, mounting unconfigured; app.ino must
not silently confirm pins, power, axis map, button windows or color thresholds.

After Gate: optional matrix setup; granted ADC pair setup; granted opponent
setup; granted QTR exclusive setup; requested IMU estimator/setup. Preserve every
real result. IMU estimator begin uses the explicit mounting and initial bias0;
acquisition start gets actual clock and the explicit power grant. A failed
estimator never becomes a configured map. On setup failure, propagate its real
fault evidence, without retry or fabricated source. Optional IMU absence is never
an initialization-complete prerequisite. All clocks use the MotorGate micros domain.

Native startup setup calls are setup work, before the release grid. IMU cooperative
setup continues at most once per due epoch until PROFILE_READY/FAULT. Its existing
1s/1024 advance/64 request limits remain; do not spin setup during waiting periods.
If setup faults after Estimator begin succeeded, obtain the Acquirer's real stored
fault with its legacy read only in this setup-fault state, once, and observe it.
Do not mistake a pulse-free beginRead FAULT snapshot for a completed acquisition.

## Decision-time projection seam

Add Transaction.decide(DecisionSource) alongside the established by-value API.
The same phase/clock/duplicate-D checks occur first. A missing projection callback
fails ORDER and inhibits without a Robot decision. Call the projection exactly
once with actual D, then overwrite t_us/timing/previous exactly as D095 before the
same Robot/Gate/recorder path. Projection may perform pure source validation and
bookkeeping only; no clock/backend/sensor or actuator call. Legacy decide behavior
and all established assertions remain unchanged. This closes the age boundary
race between an earlier caller time and Transaction's actual D.

Runtime retains the exact projected RobotInput and line snapshot used by that
decision for Calibration/display; no post-Gate timestamp substitutes for D.

## Actual release grid and clock failures

After begin, take an actual clock anchor; first step is due immediately at that
anchor. step performs at most one real epoch. Early calls only observe the clock;
no sensor/output/Robot/Gate work. Successive clock observations must advance by
less than half-range, equality allowed. On a due call, consume the latest released
grid slot, add earlier released slots to a saturating missed_releases counter,
and advance next_release on the original TICK_US grid. Never backdate S/D/sources.

After a completed epoch, skip any grid slots strictly before C; a slot exactly at
C remains eligible. This avoids a burst of decisions to replay work missed while
busy. Every executed epoch uses Transaction.open's actual S. No delay or busy wait
for the next release. Runtime report counters saturate, maximum_execution_us is
the actual complete C-S for every completed epoch including BOOT/STOP.

Consecutive identical idle clock observations increment a finite counter; an
actual advance resets it. At APP_CLOCK_STALL_MAX_POLLS=65536 equal observations,
terminal CLOCK abort, even if the next grid slot never arrives. Backward/half-range
clock fails immediately. This is a clock-integrity fault, not a runtime800/1000us
overrun policy. A frozen clock inside acquisition is bounded by existing native
limits and APP_SERVICE_MAX_PASSES=8192. No loop is unbounded.

## Per-epoch acquisition and phase admission

All source calls below occur after open and before finish. Preserve actual outer
clock observations; never derive the complete duration from sensor timestamps.

1. If QTR is CHARGING, service it exclusively until released or faulted before
   any atomic work. Normally no charging phase survives the previous epoch.
2. Read buttons once through InputOwner and read battery once only if due, using
   phase grants true only while QTR is not charging. Do not hide a second ADC
   conversion. Shared ADC faults invalidate both current projections. Preserve
   D09310ms period/20ms expiry and D0875ms button continuity.
3. Perform one useful IMU setup advance, or begin one runtime acquisition if
   configured/profile-ready and not terminal. One operation per epoch; NO_NEW
   does not cause another immediate request. Runtime operations retain the full
   original600us deadline and8192 native polls across all QTR work.
4. Preserve any completed QTR frame in an immutable mailbox before calling
   start once. Respect actual Reader BUSY/NOT_DUE, minimum2ms spacing, complete
   frame2500us and all native guards. Start is not a timer-derived measurement.
5. Pump bounded service passes. CHARGING always performs QTR advance alone;
   no IMU/ADC/Gate/output interleaving until release. Otherwise service active QTR
   then one active IMU advance per pass. Consume only a true IMU completed pulse.
   No new IMU operation starts within this pump.
6. The QTR service window ends600us after pump entry, not a new QTR frame deadline.
   CONTROL may end QTR pumping earlier when every pad is already LOW/timed-out,
   or its observed lower bound reaches that pad's current threshold. RAW preparation
   keeps polling until complete or that window ends. This is only a scheduling
   choice; no color is published from an incomplete frame. If IMU remains pending,
   continue its advances under its own original deadline, interleaving active QTR.
   Never close while CHARGING or IMU-pending. At8192 pump passes, terminally abort
   and cancel once; do not restart a budget. Keep pass counts in diagnostics.
7. Read all opponent pins once after acquisition, as the decision's actual
   snapshot. A fresh opponent input requires valid/all7 statuses, mask<=0x7f and
   S<=started<=completed<=D within half-range. Failed/partial/future snapshots are
   not fresh. No sensor service runs after finish or between C and the next S.

An active DISCHARGING QTR frame may span epochs. Preserve its elapsed interval,
native counters, source identity and actual service-gap diagnostic. No servicing
occurs in idle gaps. Some thresholds/transitions can remain ambiguous; retain the
adapter's failure rather than infer color. This software schedule is not physical
color qualification. Atomic ADC guards,600us IMU, two possible150us Gate settle
passes and cleanup can exceed800us in adverse cases. Measure and fix that before
physical acceptance; do not assert a guarantee, lower source timeouts, hide work
or stop merely because a completed epoch exceeds800/1000us.

## IMU publication and expiry

Feed each completed Acquirer result once into actual Estimator. PENDING is not
NOT_READY/NO_NEW. Preserve the latest genuine updated Estimate for publication;
an intervening real NO_NEW must not turn a never-admitted observation into retained
heading that Robot cannot identify. A real Estimator fault supersedes the mailbox.
Current bias is configuration and accompanies cached publication without changing
its original sensor payload/time/sequence. Robot normalizes exact observation
replay so it cannot increment calibration or contact twice.

At actual D, applyEstimate validates the original publication first. Never hide
a malformed report by treating it as ordinary expiry. A valid available heading
at age<=2000us remains usable; >2000us becomes explicit unavailable INVALID gyro
and acceleration, false heading flags, canonical zero sensor/source fields and
current accepted bias. Preserve the original Estimate separately. Accumulate age
from successive valid decision clocks and latch expiry for that source identity;
whole clock wrap or repeated projection cannot revive it. Only a genuinely new
Estimator observation can replace it. Do not invent NO_NEW/check time, call observe
for aging, reset yaw or recover a faulted estimator. Its own GAP policy remains.

After an actual Robot result requests a bias update, apply it once to Estimator
before any subsequent observation. Preserve a real failure as degraded evidence.
No app heading reset at GO: Robot already owns the match-coordinate origin.

## QTR preparation, handover and source expiry

Boot RAW unless default_line_thresholds_confirmed is explicitly granted. RAW
permits sensor/service UI but inhibits match START. In CONTROL, previous actual
IDLE selection of QTR_CAL enters RAW for the next decision. A successful eight-stage
Calibration commit establishes a confirmed RAM bank. Stay RAW while actual menu
context remains QTR_CAL. On leaving that context, use CONTROL only with an already
confirmed default or committed bank; otherwise remain RAW preparation. This
explicit policy requires calibration before starting with unconfirmed defaults.
Do not derive RAW solely from IDLE or keep it in STOPPED/active motion states.

Use actual Calibration.thresholds for CONTROL. On every successful decision,
call Calibration.step(actual D, actual RobotResult, exact decision snapshot) once,
even with ABSENT input. Its real menu request,16 distinct samples/stage,8 stages,
deadline, atomic bank/version and subsequent new-frame/fresh-neutral handover
remain unchanged. No fabricated request/token or automatic calibration/reset.

QTR native FAULT supersedes cached success. Otherwise project the newest actual
completed mailbox while its accumulated source age<6000us. Expired/no mailbox
projects canonical ABSENT; it never restamps a source or revives on clock wrap.
Robot independently owns its retained classification, expiry and inhibited
handover. Raw pending can wait without falsely faulting an expired present frame.
Calibrate from the same snapshot that was projected, not a later mutable Reader.

Initialization complete requires successful granted opponent/QTR/ADC setup,
current valid battery, current VALID buttons and fresh complete opponent snapshot,
plus RAW preparation or a qualified CONTROL line frame. Never require classified
line availability for RAW entry. Once core initialization latches, later missing
required evidence follows existing core faults; lowering this flag cannot reset it.

## Post-decision services and terminal behavior

Normal post-Gate work: apply requested bias, Calibration step, then optional
display using exact current input/result/calibration. Native matrix submit uses
its actual post-work clock and existing40ms throttle. All rendering/submission
is inside C-S. Matrix failure is reported, never motion permission. No Bridge,
UART dump or remote control is added. Native dump/local reset UI and calibration
snippet transport remain explicit follow-on P2 work, not silently completed.

On first actual STOPPED decision, Gate has already inhibited. Cancel only active
QTR/IMU once before finish, retain cleanup reports, never restart them. Deliberate
STOP cancellation is diagnostic shutdown, not another color sample. Project
ABSENT line input on the next real tail; do not replace an earlier actual provider
fault with innocent absence. Continue real ADC/opponent observations for this one
tail. Do not manufacture freshness to seal logs. A real later due epoch performs
the final inhibited decision/application/recorder/finish; then Runtime STOPPED
is passive forever until actual reboot. Retain SEALED/incomplete diagnostics. If
the recorder is still ACTIVE/DRAINING after that real tail, abort to INTERRUPTED
rather than freeze pretending it completed. No software reset/rearm is introduced.

On terminal runtime/Transaction clock/order/service/port failure, first call
Transaction.abort (or retain its already-terminal result), then cancel active
sources once. Mark active calibration interrupted separately; keep its actual
report/bank because it has no token-free cancel API. Do not fake a Robot result.
If no valid open epoch can close, these cleanup diagnostics belong to the explicit
interruption, not a fabricated successful duration. Later methods are passive.

## Delivery and verification

Wire native Sources + UnoQPort + Runtime as fixed app globals; setup calls begin
with unconfirmed default grants, loop calls step. Remove the old P1 one-BOOT-step
scaffold only when this actual path builds/tests. DefaultMOTORS_ALLOWED0 remains;
--match is compilation configuration only. Tooling continues to refuse app upload.
All seven existing inert sketches retain passive common-source startup; review
their exact hashes before refresh, no new upload key.

Independent tests precede implementation: actual Runtime/Transaction/Robot/Gate/
InputOwner/Estimator/Calibration in both motor settings using typed callback
fixtures and explicit synthetic button-window config copies. Cover grant absence,
setup order/failures, finite frozen clocks, exact release/missed-slot/wrap, all
S/D/A/C timing, QTR exclusive charge/release/discharge interleaving/cancellation,
pending vs completed IMU, actual D expiry1999/2000/2001 and full-wrap nonrevival,
publication-before-NO_NEW, bias, no stale button release, RAW bootstrap/calibration/
handover, true5100ms hold/edge/STOP/tail, no heap, output inside receipts and
overrun log-only. Preserve every established/locked test. Build actual app on
target without upload, inspect source/ELF/native bindings, and obtain fresh
separate review. Native physical grants, full WCET, loaded RAM and gates remain.
