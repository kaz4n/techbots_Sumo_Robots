# QTR cadence and controller freshness audit

2026-09-23 Asia/Dubai. Read-only audit, with this report as the only modification.
Prepared for the implementation owner to select policy under D-051/D-075. This
report is a proposal, not an adopted decision, native-driver implementation,
timing measurement, physical acceptance or phase pass. AGENTS.md, current
CODEX_EXECUTION/PROGRESS, relevant decisions, FACTS and source were inspected.
Today is Wednesday 23 September: PLAN section3 schedules P0/P1 work today;
D-075 expressly permits the current P2 software work before physical acceptance.

## Finding and smallest coherent path

Keep the controller at 1000us and preserve QTR_CHARGE_US=10 and
QTR_TIMEOUT_US=1500. Select a separate provisional **minimum** acquisition-start
period of2000us (equality permits start) and a2500us whole-frame cap including
charge/release/observation/cleanup (equality expires). Never restart until the
preceding acquisition and cleanup have ended.
Rearm at the same scheduler service opportunity after completion when the
minimum-start period is already due; otherwise wait for that period. No catch-up
charge or overlapping frame is allowed. The nominal400..500Hz candidate follows
from2000..2500us frame/start intervals, not from a measured scheduler guarantee;
additional rearm/service latency reduces that rate and must remain visible.
This explicitly replaces B4.1's impossible complete acquisition on the same four
pads every1000us. It does not establish a physically safe optical cadence.

The smallest useful software slice is a concrete native cooperative acquisition
owner, a pure line-evidence admission path in Robot, and a thin adapter joining
the two. Retaining the driver without the latter two leaves it incompatible with
the production controller. A final application scheduler is also required before
runtime integration can be claimed; the current app has an inert setup and empty
loop. Its eventual path is:

```
native QTR owner -> bounded result + sequence/source bounds -> line adapter
  -> Robot line admission -> Classifier once/new frame -> retained line state
  -> Escape on every controller tick -> Governor -> MotorGate
native opponent read -> Fusion once/new controller observation (independent)
```

One QTR advance must perform bounded work and return. Call it before and after
other bounded work and from the scheduler's service opportunities, not merely
once every 1000us. No 1500us busy-wait is permitted in the control transaction.
Define and test explicit operation/service deadlines; inability to service them
must become an invalid observation and motor inhibition, never a manufactured
black reading. The2500us frame cap does not increase the1500us RC observation
range: after the nominal RC deadline, readings are censored/late evidence with
the original uncertainty, never an exact longer discharge time. The B2 requirement
to finish within timeout+100us (1600us) is not met merely by this development
contract. Root must expressly document that conflict/scope when selecting the
asynchronous path; retain the original physical criterion as unproved unless an
explicit amendment replaces it. Do not report a2500us frame as a1600us pass.

Use a6000us source-age limit with expiry at equality. This conservatively budgets
two2500us frames plus one1000us delivery interval; it is an engineering allowance,
not evidence that old black remains safe for6ms at competition speed. A newer
frame cannot renew the lifetime of the old one, and no incomplete/uncertain frame
can extend the deadline. This is the exact recommended policy, replacing the
initial4000us-age/strict1600us-completion candidate considered during the audit.

## What the current controller actually requires

| Existing touch point | Current behavior | Required additive change |
|---|---|---|
| `src/core/fsm.h:405` RobotInput | `observations_fresh` means one new complete QTR **and** opponent sample | Keep legacy behavior for existing/locked callers; add explicit line presence, identity and source metadata and a separate opponent freshness meaning |
| `src/core/fsm_robot.cpp:210` prepareInputs | Every initialized call without that flag latches STALE_SENSORS | In explicit-line mode, distinguish permitted pending/retained data from invalid/expired data; still require fresh opponent reads |
| `src/core/fsm_robot.cpp:220` sampleSensors | Classifier and Fusion are coupled; new-white uses that same call | Admit/classify only a genuinely new valid line frame; Fusion still runs at the 1kHz opponent cadence; new-white is a one-tick pulse |
| `src/core/edge.h:23`, `edge.cpp:20` Classifier | Every call increments consecutive counters | Call once per admitted acquisition; never call on pending, duplicate, retained or invalid data |
| `src/core/fsm_robot.cpp:320` runEscape | Escape runs only if Fusion sampled | Run the escape timer/guard on each control tick using bounded-age line state and explicit `line_updated` |
| `src/core/edge.cpp:321,370` advanceRow/step | DONE+white can restart a row; mask baseline advances on each call | Retained white preserves priority, but only a new acquisition can request a replacement or consume the replan budget |
| `src/core/fsm_robot.cpp:275` runLifecycle; `countdown.cpp:254` | Countdown line warning sees the current mask at delivery time | Distinguish a new observation from retained state and apply source-window admission; do not move an old white measurement into the last1s warning window |
| `src/core/fsm_robot.cpp:707` updateQtrWarnings | Confirmed white plus applied pivot accumulates controller-time age | Explicitly define source-qualified consecutive observations and gap breaks; retained ticks cannot fabricate confirming observations |
| `src/core/fsm_robot.cpp:750,811` edge events/frame | EDGE is an exact decision-tick event; frame stores line state only | Keep one-shot event timing; do not call frame line_mask a new optical sample or silently encode age/uncertainty in unused bits |
| `src/hal/imu_adapter.*`, `src/core/fsm_imu.cpp` | Existing D084 example of HAL-to-Robot explicit admission | Reuse its architectural separation, not IMU-specific lifetime or presence meanings |
| `src/app/app.ino` | BOOT-only step, MOTORS_ALLOWED0 assertion, empty loop | Later wire the actual owner/adapter/admission path into bounded scheduling; preserve inert build/upload restrictions until integration is authorized and qualified |

`tick_.sampled` currently means the Fusion observation is fresh and also gates
contact commitment, stall preview and motor permission. It must continue to mean
opponent/Fusion freshness, not be changed to the slower QTR cadence. Otherwise
opponent debounce/contact and normal behavior silently change frequency too.

## Proposed explicit admission semantics

1. Add explicit mode while preserving the old default mode and every old locked
   test. Mode mixing after selection faults; a boolean flag alone must not let a
   caller move between legacy and explicit semantics to evade identity checks.
2. Evidence needs checked/delivery time, monotonically advancing acquisition
   identity, start/release source-time bounds, completion time, per-pad timing
   brackets and timeout/invalid masks. Native status and optical qualification
   are separate. Constructor/NOT_READY/PENDING provides no black observation.
3. A new complete qualified frame is admitted once. Identical replay contributes
   no observation and never refreshes age; same identity with changed payload,
   reverse identity/source time, future source time and inconsistent ordering
   invalidate the contract. Define finite identity exhaustion/reset behavior.
4. Age from the **earliest acquisition/release bound**, not latest cleanup,
   consumption or delivery. Store a bounded age accumulator after admission so
   repeated absent reports or a uint32 clock wrap cannot revive ancient data.
   Delivery age and retained-state age both require checks.
5. Select provisional `QTR_MAX_SOURCE_AGE_US=6000` with the2000us minimum start
   interval and2500us whole-frame cap. It is
   not a measured ring-safe limit. Equality expires. Select the value in
   config/DECISIONS, test the exact
   boundary, and validate stopping distance for that age before motor use.
6. PENDING/ABSENT with previously admitted nonexpired state retains that state
   without a new sample. Before the first frame, BOOT stays inhibited. Following
   initialization, malformed, invalid, uncertain or expired line evidence
   latches a reset-only inhibited fault; **an unresolved threshold bracket takes
   this same path, without a guessed escape direction**. The raw acquisition
   record remains available diagnostically even when line qualification fails.
   It must never clear white or allow
   ordinary motion. Known retained white remains an edge constraint until
   replaced by new qualified evidence or a stronger inhibit.
7. QTR_CONFIRM_TICKS becomes a count of consecutive **distinct acquisitions**
   in explicit mode, not controller calls. This changes its physical confirmation
   duration for values above1 and must be stated in B4/B16 even though the
   default numeric value remains1. Do not silently multiply counters between
   frames. An invalid/expired gap ends qualification rather than bridging it.
8. Do not fabricate one scalar time to conceal an unresolved bracket. The
   adapter may forward the recorded first-LOW upper duration only after that
   bracket proves the same threshold side, or the recorded censored timeout
   value only with valid black-side evidence. Preserve the original bracket and
   timeout status in the source result. A measured time and a censored lower
   bound remain different evidence even when both classify black.

## Retained-state Escape behavior

Keep timed row advancement at1kHz. Separate timed advancement/guarding from new
line evidence so no missing QTR frame delays STOP, countdown, braking or a script
deadline. In explicit mode:

- A new qualified white mask wins at its delivery tick, including at GO. A
  retained nonexpired white mask can establish the initial escape at GO, because
  a known edge constraint must not disappear merely when permission opens.
- Retained masks cannot create new-white pulses, rerun confirmation, clear the
  prior mask baseline or consume another replan. With a finished row and retained
  white, remain in EDGE_ESCAPE with zero/braking demand until the next new
  qualified frame decides replacement or exit.
- A retained black mask must not newly prove escape exit. Require a new qualified
  all-black frame together with DONE; specify source eligibility at that boundary
  in the integration contract. A conservative option requires its acquisition
  source to be no earlier than the observed DONE boundary; this adds a short
  braking wait and is an explicit behavior change, not existing D054 policy.
- Preserve the existing three-/four-white inhibited fault, replan budget,
  permission-loss handling, governor, countdown gate and zero push-through.
- The invariant becomes: an **admitted qualified white observation** takes edge
  priority in that controller tick/at most one tick. Do not imply that an optical
  transition is detected within1ms. Sampling phase, RC acquisition, service delay
  and delivery add latency which must be measured and enter stopping tests.

## Polling, interrupts and temporal threshold evidence

| Approach | Software benefit | Unresolved cost or risk |
|---|---|---|
| Cooperative full RC polling, with observation brackets | Smallest extension of established native GPIO paths; no new interrupt ownership | A600us IMU call can span the entire300us white threshold. Late LOW is not exact discharge time; missed service or straddling brackets must inhibit, so usable motion availability is not yet proved |
| Native falling-edge IRQ with fixed per-frame storage | Can observe during a main-loop IMU poll and reduce cooperative blind windows | Does not shorten1500us timeout or permit same-pad1kHz recharge. Callback timestamp is still delayed software evidence. Arming/release races, stale pending flags, callback lifetime, atomic publication, coalescing and bounded latency require a separate contract/source proof and physical qualification |
| Threshold-only/early temporal classification | A LOW observation strictly before the white threshold can prove white; an appropriately timed HIGH can prove black under the RC monotonic-discharge model, even while raw acquisition continues | Changes B4's raw-complete interface and evidence meaning. Unresolved threshold-straddling data cannot prove black. Early partial masks need per-acquisition update/replan rules and cannot be passed repeatedly through the current Classifier |

For the initial coherent slice, recommend cooperative full-record acquisition
with explicit invalid/uncertain fail-closed admission,2000us minimum starts,
2500us complete-frame cap and6000us source-age expiry. It is a valid software
architecture with conditional availability, not proof of a runnable high-duty
match scheduler. If the resulting whole-image schedule cannot maintain sufficient
observation resolution without starving other tasks, select the IRQ architecture
explicitly before claiming integration; do not hide that problem behind a helper.

For polling, preserve each pad's release interval and last-HIGH/first-LOW read
intervals. The transition duration is bounded by the last known HIGH and first
known LOW relative to release, with timer quantization and sequential-read skew
included. A bracket whose upper endpoint is strictly below300us proves white;
a bracket whose lower endpoint is at least300us proves black. A bracket spanning
300us is unresolved. An unobserved LOW at the1500us deadline is not proof that
the physical transition occurred at1500us. The native-source audit owns exact
register/read timestamp derivation; this report does not invent that guarantee.

An explicitly conservative "possible white" safety mask is another engineering
option, but it must remain distinct from confirmed white/raw evidence and its
escape behavior requires separate tests. The simpler initial policy is inhibited
invalidity, avoiding guessed motion on ambiguous corners. No shortened timeout,
synthetic exact time or silent threshold enlargement is recommended.

## Scheduling constraints that a driver alone cannot resolve

The IMU aggregate read has a600us acceptance budget plus separate50us cleanup;
MotorGate's native settling budget is150us and battery runtime conversion is100us.
These maxima already exceed800us when simply serialized, before Robot or QTR
work. Their independent per-operation limits are not a full-tick WCET proof.
Scheduling/batching must explicitly consider all of them, plus recorder, UI and
installed interrupts. Count faults/cleanup and background QTR service in whole
runtime evidence rather than moving work outside the measurement window.

Reserving a short fine-polling window after QTR release can make threshold
classification useful, while coarse polling follows for black/raw timeout data.
Its placement and operation reservations need a concrete scheduler design; the
existing600us blocking IMU call must not start across an unprotected critical
window when a successful optical classification is required. If it does, the
record must retain its resulting ambiguity and inhibition can be the correct
outcome. The2500us cap can tolerate a late service opportunity without falsely
claiming precise timing. The2ms minimum start interval does not by itself create
an early-window reservation or guarantee successful classification.

Reading IMU only on alternate1ms ticks is not an automatic solution: D082 permits
at most2000us between accepted IMU observations, and variable read completion
times can exceed that even when starts are exactly2000us apart. Either prove a
schedule with margin, make the IMU service incremental through a separately
specified change, or explicitly revise the selected continuity policy with
evidence. Do not silently relax it in QTR work.

SC-B's semantic contradiction can be resolved by the explicit acquisition/control
cadence split, but optical response, runnable schedule and under800us WCET remain
separate open qualification items. SC-AJ/F091 global runtime limitations and all
physical/pin/human gates remain unchanged.

## Minimum independent tests before claiming the path implemented

- Native real-driver tests for overlapping starts, full charge/release ordering,
  all16 pad combinations, status propagation, per-pad skew/brackets, equality,
  quantization, service gaps, timeout/censoring, cleanup and identity lifetime.
  Include an IMU-shaped600us gap straddling a white transition: never black.
- Actual-driver-result to adapter to **Robot** tests, with opponent samples at
  1000us and QTR at2000..2500us, including late completion/rearm. Prove progress
  on retained-black ticks; no false
  STALE_SENSORS; unchanged opponent confirmation/contact rate; real final duties
  stay governed and gated.
- Test QTR confirmation above1 using distinct acquisitions; immediate and later
  identical replay; changed-payload replay; missing first sample; absence;
  invalidity; stale source delivered recently; future/reversed/wrapped source;
  age equality/expiry and reset/mode mixing. Verify no counter or age refresh.
- GO with retained white; fresh white in every moving state; fresh additional
  white while pivoting; retained-white DONE without repeated replans; new-white
  replacement count; black-clear exit policy; three-/four-white faults; STOP on a
  pending tick. Keep all established locked tests unchanged.
- Countdown line-warning source-window boundaries; QTR stuck warning with valid
  source progression, applied pivot, retained ticks and a missing/expired gap.
  EDGE/FAULT events emit once; frames describe state without inventing raw source
  age or optical provenance.
- Scheduler simulation using actual orchestration, including worst admissible
  native-operation durations, missed release/deadline, no catch-up acquisition,
  micros wrap and timing receipts that account for every task. Failure must
  produce inhibition rather than falsely reporting healthy cadence.
- Actual compile-only target retains the real driver/adapter/Robot path; review
  exact source map, symbols/imports/startup and existing inert source guards.
  Then fresh independent review. Host/compile-only success does not replace
 black/white/brown tests, capture/service latency, ring stopping or whole-image
 5-minute WCET measurement.

No code/config/locked test/shared ledger/board action was performed by this audit.
Next action: root selects the explicit cadence/uncertainty/freshness policy and
records its exact scopes before implementation and independently authored tests.
