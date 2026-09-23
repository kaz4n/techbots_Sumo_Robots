# P2 application transaction public-spec audit

2026-09-23 Asia/Dubai. Read-only audit of the published specifications and public
headers at the D094 checkpoint. The local date is Wednesday 23 September; PLAN
section 3 targets assembled P2 acceptance on Saturday 26 September. Active P2
software is permitted by D051/D075; no physical or human gate is inferred.

This audit read AGENTS.md, current PROGRESS/handoff/resume, PLAN section 3,
HARDWARE proposals, BEHAVIOR B13-B15, P2_hal_bench, the final D094 integration map,
D084/D085/D087/D089/D090/D092/D093/D094 and their relevant public contracts and
headers. It did not inspect implementation CPP bodies. Recommendations below
are prospective policy choices for the coordinator, not adopted decisions or
verified timing. No shared ledger, source, configuration, existing test or hardware
was changed by this audit.

## Smallest useful code boundary

Implement one fixed `app::Transaction` in `src/app/transaction.{h,cpp}` and one
thin native composition in `src/app/app.ino` (or a target-only companion). The
transaction owns the actual Robot, Estimator, InputOwner, Calibration and
AttemptRecorder lifetimes, previous receipt, source snapshots, schedule state
and fixed diagnostics. The native composition owns one instance of each actual
peripheral, binds the existing MotorGate Port and ADC InputPort, and supplies
typed calls to the existing opponent/QTR/Acquirer APIs. The concrete MotorGate
must remain inside the tested transaction path; a substitute final-duty callback
is insufficient. A single AttemptRecorder owns the large payload buffers.
Reference ownership of these fixed objects is equally suitable and avoids moving
their storage: their sole authorized caller must still be the transaction/native
scheduler composition. A begin/decision/close owner is sufficient when the actual
native scheduler cannot bypass its accounting or invoke a second decision/apply.

Recommended public owner surface:

- `Transaction(const Sources&, const power::InputPort&, const motors::Port&,
  const Outputs&)`: copy fixed callback tables/context references; no calls or I/O.
- `begin(const SetupProfile&)`: one setup attempt, actual Gate inhibition first;
  retain independent initialization results rather than a caller-supplied ready bit.
- `advance()`: obtain the actual clock and perform a finite bounded unit of setup,
  acquisition or one decision transaction. Return a typed phase/progress report.
  A call may produce at most one fresh Robot result and one corresponding Gate
  application; never run an unbounded catch-up loop.
- `report() const`, `lastResult() const`, `recorder() const`: read-only diagnostics.
  No motion setter, sample ingestion, remote command, clear-evidence, general job
  queue or runtime hardware-approval method.

`Sources` should expose only existing typed operations: clock; opponent begin/read;
QTR begin/start/advance/cancel/report; IMU start/advanceSetup/beginRead/advanceRead/
cancelRead/setupReport. Separate optional fixed matrix/dump callbacks may bind
their already-defined owners. Each production forwarding callback must invoke
its real corresponding HAL method, with no invented success or source metadata.
Use real InputOwner/Estimator/adapters/Robot/Gate/Recorder in host composition
tests; substitute only physical-call boundaries. One context/explicit lifetime
per peripheral, noncopyable owner, no allocation after setup.

Exact names are suggestions. The required boundary is this fixed composition,
not another bus/router framework or another disconnected metadata helper.

## Transaction and evidence oracle

For token k record actual acquisition start S, decision D, Gate application A and
completion C. The next real epoch has N and next decision E. Preserve D092:

`0 <= D-S <= A-S <= C-S <= N-S <= E-S < 2^31`.

Select explicit timing on the very first Robot call, including BOOT. Set D only
after all evidence used for that decision exists; S is not a replacement sensor
timestamp. A comes unchanged from MotorGate. Close C only after all acquisition,
cleanup, projections, Robot, Gate, bias application, calibration, recorder and
admitted output work assigned to that epoch. Attach `execution_us=C-S` to the
actual receipt and supply it exactly once as the following Robot input.

Do not perform sensor/output work after C and before N. Pure waiting until the
next release may occur outside an epoch; executing QTR/IMU work there requires
opening the next accounted epoch first. If that makes an epoch long, record the
whole duration; do not subtract waits or move C earlier to satisfy a target.
Every native fault cleanup, including a Gate's possible second settle, is inside
the outer interval. Native transfer completion is not necessarily cleanup end.

For each fresh Robot result: apply the actual Gate once, consume that exact result
once, and preserve the returned receipt for the next decision. A nonfresh result
must never cause another Gate write or recorder append. Bias-update intent applies
after the decision to future Estimator increments only. The input/result/snapshot
pair supplied to Calibration must be the same pair used in this decision.

## Setup readiness without invented facts

Gate.begin precedes all other native setup. Missing/failed inhibition is retained
as a failed application boundary, never converted to an acknowledged zero output.
Provide individual setup facts/grants: MPU power confirmation, signed mounting,
exclusive QTR pads, matrix normal-startup ownership and optional UART/framing.
Compilation and successful calls do not supply physical confirmation.

Current BUTTON_WINDOWS_CONFIGURED=0 and an unconfirmed mounting are deliberate
unavailable defaults. Do not fabricate windows, a BOTH distinction, a body map,
pad ownership or UART-clean grant to make the native app look ready. Missing IMU
is explicitly allowed by RobotInput and B14 and is not a prerequisite for boot
completion; it must follow the existing unavailable/degraded path.

At minimum, initialization must not become complete before actual Gate setup,
required acquisition owners, a first available battery, and usable explicit
button evidence. A control line frame must be qualified unless the app explicitly
requests D089 raw-only BOOT/IDLE preparation. Requiring classified lines before
all IDLE/menu access deadlocks the documented calibration workflow. Raw mode must
remain inhibited, use real raw frames, preserve STOP, and requalify with a later
source plus fresh neutral before match START. Freeze its native entry/exit policy.

MPU setup waits need a bounded useful advance cadence: polling every spin can
exhaust its 1024-call limit during mandatory waits. Its existing total deadline
and request/count limits cannot be silently enlarged. UART device_init contains
known unbounded acknowledgement waits and is setup-only; never lazy-initialize
it in a control transaction or claim its initialization establishes runtime WCET.

## Pending sources, age and admission

| Source | Required application behavior |
|---|---|
| Opponents | One actual full read for each actual initialized 1 kHz decision; accept only a complete valid snapshot. Partial/failed input is not a fresh zero or stale replay. No catch-up acquisitions for missed ticks. |
| QTR | Preserve CHARGING/DISCHARGING as pending. Adapter ABSENT allows Robot to retain its own qualified history; do not fabricate a completed frame. Actual complete source identity/intervals reach the adapter unchanged. Ambiguous color remains invalid. Age expires at >=6000 us. |
| IMU PENDING | Never pass the default pending Sample to Estimator, never call it NO_NEW, and never advance sequence, checked time, calibration or yaw from progress metadata. |
| IMU terminal pulse | Pass one actual completed Sample to Estimator once, including real NO_NEW and FAULT. Getter/repeated terminal snapshots do not replay an observation. |
| Bounded IMU history | Exact READY replay through applyEstimate is legal under D084 while decision-source age <=2000 us; Robot suppresses repeated observation identity. Keep original source, checked time, payload and sequence. |
| Expired IMU history | At age >2000 us project canonical explicit unavailable evidence with no fresh gyro/accel, retaining separate diagnostic history. Do not forge a later checked/source time or malformed WAITING Estimate; the adapter's WAITING shape excludes a prior source. Accumulate age so old evidence cannot revive after observed wrap. |
| Battery | Only InputOwner performs A0/A1 conversions. Request A0 when due and granted; no hidden second conversion. Actual source age <20000 us remains usable; A1 failure invalidates that same retained battery before projection. |
| Buttons | Pass only this epoch's actual ButtonRead or explicit absent. Absence is not NONE. Preserve source brackets/sequence; age >5000 us is a Robot fault. Unconfigured decoding remains invalid, never a release. |

IMU unavailability due only to scheduling expiry need not create a new hardware
fault; subsequent genuine source evidence still passes existing Estimator gap and
Robot identity rules. The application cannot reset either component to disguise
a missed source. Decide whether terminal cancellation reports are forwarded once
before/after STOP; do not leave that edge implicit.

## Fixed scheduling and safety priorities

QTR charge release must complete in [11,100) us after drive_completed_us. Native
call guards alone do not guarantee that window. Do not start charge and admit a
100 us ADC call or 150 us motor settle before release. IMU advances are resumable,
but keep their original 600 us wall-clock deadline across every QTR/ADC/job and
the one original poll budget. Pending is not permission to park a transaction
until a later tick with a new budget.

QTR discharge needs threshold-relevant observations, not merely eventual frame
completion. Use the currently selected per-pad thresholds, including RAM bank
updates; fixed 300 us service assumptions are insufficient. Preserve observed
intervals and max service gaps. No chosen polling interval proves physical color
separation. A scheduling budget/early cutoff may be selected as a development
policy only, with actual failures reported and full800us qualification still open.

Recommended priority order within bounded admission: already-active QTR release/
critical discharge service; real button/STOP opportunity; remaining required
acquisition; actual Robot and Gate; cleanup required by terminal control; recorder
and bias/calibration; optional display/dump only with remaining admitted slack.
Once STOP is known, the actual inhibited Gate application precedes slow optional
work. It is not acceptable to poll indefinitely for an IMU sample before deciding.
Do not begin optional work with a reservation that omits its failure cleanup.

Overruns do not create synthetic ticks. At most one actual decision occurs per
eligible invocation; next releases remain on the original 1 kHz grid and skipped
slots are counted separately. Use real current timestamps/sensor calls. Freeze
whether an overdue invocation executes one late current epoch before skipping to
the next grid boundary; do not infer this from modulo arithmetic. B14 durations
strictly >1000 us count overruns; a duration of800 us already fails the separate
strict <800 us physical target. No existing contract adopts a new overrun STOP
policy, so changing motor behavior here requires an explicit D051 decision.

## Stop, final receipt and reset

Terminal STOPPED or inhibited escape fault must stop new acquisitions and cancel
any already-pending QTR/IMU operation exactly once through their actual APIs;
cancellation is terminal/reset-only, not a pause. Include cleanup before closing
the stopping epoch. Do not reset a shared ADC owner, turn a failed Gate receipt
into success, discard errors, or acquire new measurements solely to seal logs.

The stopping result enters AttemptRecorder DRAINING. It is not complete evidence.
Execute a later real inhibited Robot tick with the actual stopping receipt, apply
its fresh zero command once, and consume its result so the final frame/timing
can seal. Preserve exact token association, final-frame loss fields, and all
events. Do not synthesize a flush result or erase buffers. This tail's own Gate
receipt is still real even though its duration is not a match member.

A same-epoch post-Gate failure must not cause a second Robot step or double Gate
application under the same token. Freeze its next-tick fail-closed routing and
truthful diagnostics. Genuine reset notification must reach AttemptRecorder and
dump owner before Robot reset; unfinished evidence becomes interrupted, not
sealed. The native app can initially require a real reboot for reset; adding a
software/local-reset UI is a separate explicit policy and cannot be a remote
motion path. STOPPED is not IDLE dump authority.

### Minimal emergency inhibition gap

This is distinct from B14 timing overruns. If the application clock freezes or
reverses after an enabled application, Robot may be unable to produce a fresh
valid STOP result. A repeated timestamp must not be used to manufacture a new
token. The existing public MotorGate offers only apply and reset; reset is
unsuitable for this terminal failure because its documented purpose clears a
fault/rearms after acknowledged inhibition.

Recommend a narrow `MotorGate::halt()` before complete owner integration. It
performs the existing finite LOW/all-zero/settle inhibition through the sole
writer, retains a terminal latch until genuine reset, and returns a typed
non-token inhibition report (acknowledgement, actual completion time, first
fault). Preserve a pre-existing cause, except actual callback failure upgrades
to IO. It must not invent a Robot command, consume a token, return PreviousTick,
or claim physical stopping. Freeze repeat-call semantics explicitly.

If halt occurs after apply within an open epoch, that token's ordinary application
receipt should be invalidated: the extra output change is not represented by its
single application record. Preserve actual timing and separate halt diagnostics.
A later real decision can receive the invalid receipt and follow existing core
inhibition. If valid decisions cannot resume, notify the recorder of end-of-stream
interruption; do not synthesize a tail or SEALED evidence. This halt is for an
unrepresentable/unsafe transaction or clock failure, never for800/1000us elapsed
alone. Exact API/tests are a small prerequisite, not a replacement application
framework or a reason to defer the native composition indefinitely.

## Independent prospective test matrix

| Group | Required oracle and discriminating cases |
|---|---|
| Lifetime/setup | Constructor/destructor no I/O; setup once; Gate LOW first; every prerequisite failure; unconfirmed defaults; missing IMU allowed; raw calibration reachable without qualified color; no silent retry/recovery. |
| Real transaction | Script clock across acquisition/decision/Gate/recorder/output; exactly one Robot/Gate/consume per token; exact S,D,A,C and next N; final duration includes source failure cleanup and second Gate settle. |
| Timing boundaries | Natural wrap; half-range/reversal rejection; 799/800/801 and999/1000/1001 us; late start versus long execution; no pre-S or post-C work; no duplicate apply on equal clock/result. |
| Scheduler | Normal grid, one/multiple missed releases, frozen clock finite call quota, pending operation finite budget, true missed-slot counter, no fabricated sensor timestamps or fast-forwarded countdown. |
| IMU | Deferred begin; pending over decisions; one terminal pulse; NO_NEW distinct from pending; bounded replay age1999/2000/2001; observed full-wrap nonrevival; future bias only; terminal fault/cancel once; no silent gap reset. |
| QTR | Charge release at lower bound and100 rejection; atomic-job refusal while charging; discharge interval straddles each current threshold; incomplete/pending/ambiguous report; source start spacing; frame/source expiry; RAM thresholds respected. |
| ADC/buttons | Battery due9999/10000; age19999/20000; one grant/one conversion; A1 faults invalidate battery same decision; button absence not release, age5000/5001, no cached hold/release freshness. |
| Priority | White at GO, persistent white, all-white inhibited fault; STOP concurrent with IMU/QTR progress/output request; countdown full5100ms; actual enabled-host Gate honors governor/contact caps. |
| Final evidence | START, GO, STOP, one later tail; counted GO-through-final-stop durations; stopping cleanup included; SEALED after actual tail only; missing receipt/frame visible; faulted Gate receipt stays invalid. |
| Services | QTR_CAL raw preparation,8 genuine requests, later-source handover/fresh neutral; no match start from service; display cannot outrank Gate; no active-match dump; STOPPED refuses dump; reset preserves bytes. |
| End-to-end | Actual InputOwner->adapters->Estimator/Robot->MotorGate->AttemptRecorder in both host motor configurations, plus target compile retaining the actual native app path. Add tests; preserve every existing/locked assertion. |

## Decisions still needed before implementation

1. Freeze one finite application service-work quota and phase/time admission
   policy, including concrete acquisition cutoff and atomic-call reservations.
   Distinguish development choices from measured WCET. Existing upper guards do
   not supply a proof that adverse native work fits800us.
2. Freeze the actual setup profile and readiness matrix, including unconfigured
   defaults, raw calibration entry/exit and optional matrix/UART participation.
   Do not convert unknown physical grants into selected engineering facts.
3. Freeze accumulated-age pending-IMU projection and the precise expiry shape.
4. Freeze original-grid missed-slot handling, clock fault response, terminal
   acquisition cancellation and post-Gate failure routing.
5. Freeze the tail/reset/output policy and account all actual service work inside
   receipts. Any optional output may be deferred, but cannot execute invisibly.

The next concrete action is a D051 decision plus frozen public application header,
then independent additive tests from that contract while another agent implements
the owner/native composition. Native target compilation, full tests and fresh
separate review verify software only. Actual loaded RAM, physical sensors/buttons/
mounting/pads, calibrated clock, complete worst-case/p99 timing, assembled B1-B8,
native UART acceptance and every human phase gate remain unproved.
