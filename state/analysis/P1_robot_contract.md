# Production Robot contract (D-060, 2026-09-23)

Adopt sections2-5 of P1_robot_api_proposal.md and metadata/version1 in
P1_robot_event_contract_audit.md, with the explicit clarifications below.
These record D-051 choices for existing P1/B0-B15 integration, not new hardware
facts or phase authority. Public fsm.h/logframe.h define the actual callable API;
proposal declaration sketches are superseded by those headers. Scenario tests
derive from these sources, BEHAVIOR and existing component public contracts.

## Input and transaction

One distinct timestamp admits one tick/nonzero monotonically increasing token.
An immediate duplicate ignores changed observations/receipts, returns the cached
persistent state/output/token with fresh=false, clears event/frame/START/GO/menu/
bias/origin-change pulses, and does not advance any component. Successive distinct
call gaps must be less than one uint32 micros wrap. Reset clears state but keeps
the next-token counter; no old receipt can attach across reset. UINT64_MAX is the
last allocatable token; further admission latches TOKEN_EXHAUSTED and inhibits,
without reuse or a fresh token. No arbitrary state/mode setters.

BOOT may wait for initialization, with zero outputs and live buttons/STOP. First
completion latches setup and enters IDLE unless a safety inhibit wins. The tick's
entry state remains BOOT, so its qualified START cannot launch a match. Missing
IMU is permitted. After setup, genuinely fresh full QTR/opponent samples and a
valid finite battery sample are required. Missing/stale sensors or battery faults
immediately select STOPPED. OR known contract faults into Lifecycle STOP before
its services can sample stale data; still process real buttons/StopHold once.
Never call Classifier/Fusion/Escape with stale/cached observations. When fresh
lines resume, Escape may receive closed permission, preserving its own fault.

Classify raw QTR once; no alternate preclassified input. Fusion observes once in
continuous raw yaw using entry state/new-white evidence. Lifecycle uses the same
confirmed masks, raw pre-bias gyro, entry-state menu routing and real STOP; D-059
establishes match origin before any moving reference. Invalid previous bias or
calibration gyro samples retain their existing service-failure/rejection response,
not a new motor veto. Healthy nonfinite yaw follows D-059; unavailable IMU uses
fallback. High unused sensor mask bits retain the component ignore semantics.

Escape preempts; then ongoing re-flank/opener; then current normal perception.
Only one script exit -> normal selection -> new executor entry per tick, with
existing internal bounded phase advancement. Loss tick and actual escape exit
brake immediately; a deferred executor starts next tick using that tick's current
observation. Preserve all D-033/D-034/D-038/D-040/D-045/D-046 rules. A DefendTurn
SEARCH intent deliberately starts SEARCH for that exit tick even with a remaining
side target; normal arbitration resumes next tick. A scan hint survives until its
first actual scan or a preempting new behavior, never supplies target/contact.

Detector consumes one candidate contact preview and preceding actual applied
duties. Limiter admission occurs at most once. Actual SWING entry alone updates
alternating swing history. Prevalidate returned script status/finite request and
required voltage/known governor profile, select final fault state if invalid,
commit Fusion once to final state, then run Governor once. No provisional contact
event/permission. A contract-impossible invalid Governor result after valid inputs
forces disabled zero immediately and latches fault; preserve the already committed
state truthfully for that call, STOPPED before next commit. Never double-commit.
Expected invalid voltage on an already inhibited request needs no second action.

Contract faults latch until reset and select STOPPED. Explicit STOP outranks a
faulted Escape; otherwise Escape's own fault retains EDGE_ESCAPE with zero/disabled
output until reset. IMU absence, stuck-bit masking, calibration rejection, low
battery and timing/QTR warnings do not invent additional motion policies.

## Application and duration evidence

Each result after the first needs one valid receipt matching the exact preceding
token. No predecessor means receipt fields are ignored, never accepted as evidence.
Require finite duties in[-1,1]; disabled means both zero. Enabled requires preceding
permission. Each nonzero actual wheel must have the requested sign and magnitude
no greater than its requested magnitude. A zero/braking request permits only zero.
HAL must quantize toward zero (or inhibit); there is no upward allowance. Receipt
reports actual output-stage settings, not measured wheel movement. Missing or
invalid application evidence latches APPLICATION_CONTRACT, never assumed zero.

Use unsigned offsets from preceding t_us: applied_us must be no later than current
t_us; valid completion is between application and current observation. execution_us
must equal completed_us minus that preceding t_us: the supplied timestamp is the
start of the measured whole tick, including acquisition/decision/application/
recorder/scheduler work. This consistency check is not proof of physical timing.
Malformed claimed duration marks timing evidence incomplete and is not counted;
it alone does not change motion. Missing duration similarly does not inhibit.
Duration counting/incomplete/category9 reporting apply only to the explicitly
included GO-through-final-stop receipts, not BOOT/COUNTDOWN/nonmember receipts.
One category9 event aggregates any prior report's rate/saturation/incomplete rise;
valid duration uses completion time, missing/invalid duration uses current detection
time (never a fabricated completed_us). FIRST_NONZERO uses actual application time.
Prior receipt events precede current decision events; never sort wrapped times.

## Histories, warnings and recording

Preserve raw Fusion histories across GO. Age eligible world/front/inward/edge
evidence with bounded accumulators, never repeatedly subtract ancient timestamps.
Only actual new valid memory/front rises/escape exit refresh corresponding ages.
Completed escape side is known only if all participating masks were exclusively
left or exclusively right; any bilateral participation makes it unknown. Retain
actual raw inward yaw/time only with healthy exit evidence, then project via D-059.

QTR warnings require a confirmed white bit AND previous actual enabled duties of
strictly opposite nonzero signs continuously for strictly more than QTR_STUCK_MS.
Any break clears/rearms that bit. This is evidence of commanded pivot, not measured
body rotation; it never suppresses edge logic. IMU-availability warning starts with
the first initialized availability report, then on recovery/loss episodes. Low
battery warning starts on strict under-threshold valid IDLE samples; valid non-low
samples rearm it. Watchdog cause is consumed only on first boot tick if provided;
unknown cause produces no invented event.

Adopt the explicit metadata table/order, CORE_CONTRACT bits0..7 and category9
bits0=rate-rise,1=saturation-rise,2=incomplete-rise. PHANTOM_SET angle is the
MATCH-world projection of the actual new raw Fusion marker through D-059. If that
projection is unavailable/invalid, record semantic evidence loss, not a false zero
angle or a motion change. Fault masks aggregate; code7 reports newly latched reason
bits. No per-sensor/per-tick repeated fault flood.21-entry bound is2 prior receipt
extensions plus19 current decision events. Invalid metadata and capacity rejection
are separately saturating; logging loss cannot affect motion or recurse.

Snapshot running mode only on accepted START. Start frame epoch/counters then,
immediate candidate t_ms0; LOG_HZ cadence is phase-anchored with at most one current
candidate per tick and explicit skipped slots. Finish only from the next matching
actual application receipt; unreported final frames remain incomplete. Retain
packFrame status, never synthesize valid zeros for unknown application/voltage.
With valid matched application, emit frame_ready even for CLAMPED/INVALID, retain
that status (INVALID has codec-zero bytes), and mark recording_incomplete. Such
an emitted frame does not increment skipped_frames. Missing/invalid application
emits no frame, increments skipped_frames for its candidate and marks incomplete.
Before GO frame yaw is the actual raw continuous input; after GO it is match yaw.
Frame gyro_z_dps is the supplied raw_gyro_z_dps (pre-bias), the only live rate in
RobotInput. Do not subtract previous_bias_dps outside its accepted-release service
use or invent a corrected-rate sample. Dump field documentation must retain this
meaning; a later corrected-rate channel requires an explicit public contract.
IMU_OK describes current actual availability with valid coordinate; nominal/retained
fallback yaw is never marked healthy. Nonfinite fields retain codec INVALID status.
RobotResult contains no raw nonfinite measurement outputs.

Timing membership starts at GO and includes the one final inhibited stopping tick.
Stop recording/timing after STOPPED, latched inhibited Escape fault or countdown
cancellation; force one final candidate (coalesced with a due frame). A canceled
countdown has no match-duration samples. A later STOPPED call may flush the final
receipt but cannot create another final frame. Reset/new accepted START resets
local attempt counters; external recorder storage remains separately owned and
must preserve last-match evidence through Robot reset. Service intents do not
execute hardware or grant permission; DRIVE_TEST stays unavailable in P1.

No pins, B16 values, established locked tests, physical acceptance or human gate
are changed. Complete app, real MotorGate/feedback, acquisition and WCET remain
separate requirements. The implementation and actual Robot scenario tests must
now prove this contract; a proposal or component test is not that proof.
