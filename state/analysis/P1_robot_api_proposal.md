# Minimum production Robot API proposal - 2026-09-23

Status: **unadopted recommendations for one D-060 decision**, not implementation,
test evidence or a phase gate. Only this file is owned. Sources are the current
public component headers, BEHAVIOR, D-018 through D-058, the Robot interface/event
audits and P1_robot_heading_contract_audit.md. No implementation `.cpp` or test
source was read for this task; no build, hardware action or commit occurred.
D-059 HeadingReference is being defined separately: keep its raw-Fusion/local-
motion policy, including nominal fallback when IMU is missing at boot.

## 1. Public surface to publish

Put the Robot beside the existing FSM helpers in `fsm.h`; preserve legacy
core::Inputs/Outputs/component signatures. Add a dedicated input so conflicting
raw and preclassified line fields cannot both drive production decisions.
The following is a proposed declaration sketch, not an existing callable API.

```cpp
struct PreviousTick {
    bool applied_valid = false;
    std::uint64_t token = 0;       // Exact preceding RobotResult token.
    std::uint32_t applied_us = 0;
    bool motors_enabled = false;
    float duty_l = 0.0F, duty_r = 0.0F;
    bool duration_valid = false;
    std::uint32_t completed_us = 0;
    std::uint32_t execution_us = 0;
};
enum class ResetCause : std::uint8_t { UNKNOWN, WATCHDOG };
struct RobotInput {
    std::uint32_t t_us = 0;
    bool initialization_complete = false;
    bool observations_fresh = false; // NEW complete QTR + opponent observation.
    std::uint32_t line_raw_us[4] = {};
    std::uint8_t opp_raw_mask = 0;
    float raw_heading_deg = 0.0F; // Unreset continuous coordinate, D-059.
    float raw_gyro_z_dps = 0.0F;  // Before bias subtraction, D-024.
    float ax_g = 0.0F, ay_g = 0.0F;
    bool imu_ok = false;
    float previous_bias_dps = 0.0F; // Consumed ONLY on accepted match release.
    float vbat_v = 0.0F;
    bool vbat_valid = false;
    core::ButtonLevel button = core::ButtonLevel::NONE;
    bool stop_requested = false; // Qualified local safety stop, not remote motion.
    ResetCause reset_cause = ResetCause::UNKNOWN; // First boot observation only.
    PreviousTick previous;
};
struct EventBatch {
    logframe::EventInput entries[21] = {};
    std::uint8_t count = 0;
    bool overflowed = false;
    std::uint32_t rejected = 0; // Saturating, per returned batch.
};
struct RobotResult {
    std::uint64_t token = 0;
    bool fresh = false;
    core::Outputs outputs; // Final requested electrical duties + permission.
    core::Mode running_mode = static_cast<core::Mode>(config::MODE_DEFAULT);
    countdown::MenuResult menu;
    countdown::LifecycleResult lifecycle;
    std::uint16_t contract_faults = 0; // Sticky explicit reason bits below.
    edge::EscapeFault escape_fault = edge::EscapeFault::NONE;
    std::uint8_t opponent_fault_mask = 0, qtr_warning_mask = 0;
    bool low_battery = false, all_in = false;
    bool bias_update_requested = false;
    float accepted_bias_dps = 0.0F;
    // Include D-059's typed heading/reference diagnostics by value.
    EventBatch events;
    bool frame_ready = false;
    logframe::FrameBytes frame;
    logframe::PackStatus frame_status = logframe::PackStatus::OK;
    std::uint64_t frame_token = 0; // Identifies the prior completed observation.
    std::uint32_t skipped_frames = 0; // Saturating lifetime/attempt counter.
    logframe::TickStatistics ticks;
    bool timing_incomplete = false;
};
class Robot {
public:
    RobotResult step(const RobotInput& input);
    void reset();
};
```

No arbitrary state/mode setter, motor callback, clock, HAL handle, recorder ring,
transport queue, dynamic allocation or second speculative Robot pass is needed.
Representation capacity 21 belongs in one named public constant, not a ring-
tuned behavior value. Public bit constants/metadata enums should replace magic
numbers in the final header. D-059 supplies the precise heading diagnostic type.

## 2. Private ownership and compact retained state

| Members | Responsibility |
|---|---|
| countdown::Lifecycle, countdown::Menu | One logical button/STOP sample, hold/services, selection; running mode captured only on accepted match START. |
| edge::Classifier, edge::Escape | Robot exclusively classifies raw QTR observations; full existing escape owns its guard/rows/sticky faults. No second Guard/row executor. |
| opp_fusion::Fusion | One raw-domain observation, optional preview, one final commit. No second Debouncer/Contact/BearingMemory. |
| D-059 HeadingReference | Raw/local conversion and unavailable-IMU nominal/recovery policy; never resets Fusion. |
| NormalPerception, SearchSide, Search, DefendTurn, Reflank | Normal qualification, shared side, retained active state executor. |
| openers::Direct, Flank, Wait | Exactly one selected opener active; Flank covers four mirrored modes, Wait owns its own delegated Flank. |
| stall::Detector, ReflankLimiter, governor::Governor | One detector observation/limiter admission opportunity/governor update per fresh tick. |
| State/mode/boot and fault flags | One final committed public state per tick; no moving-state startup before real GO. |
| One previous-result receipt slot | Last token/time/output permission, attempt/GO identity, pending frame candidate/due flag and measured-match membership. |
| Bounded history | Previous confirmed line mask; world/front/inward/edge ages; last real swing side; first-applied-duty flag; warning episodes; frame clock; TickStatistics. |

Retained ages accumulate successive unsigned deltas and saturate at their largest
needed eligibility limit; preserve seen/valid flags. Do not repeatedly subtract
ancient wrapped timestamps. Refresh world/front recency only on the corresponding
new Fusion memory observation/front-bit rise. Preserve script-independent side,
limiter and previous actual swing history across executor reset/preemption.

## 3. Exact input, feedback and fault choices to adopt

- `observations_fresh` asserts one newly acquired complete four-QTR/seven-opponent
  observation at this admitted tick. Robot calls Classifier/Fusion once, including
  countdown/IDLE. No caller line_mask is accepted. False after initialization
  latches a contract fault and inhibits immediately; do not count stale data as
  black, a new contact or elapsed confirmed samples. BOOT may wait without fresh
  sensors. Still service logical STOP on these calls; no stale sensor resampling.
- Initialization completion is latched. The first completed-setup tick leaves
  BOOT for IDLE, unless STOP/fault wins; its BOOT-at-entry button release cannot
  start a match or invoke a menu action. IMU availability is **not** a prerequisite
  for initialization_complete. After it is latched, a false input cannot re-enter
  BOOT or clear state. Unknown reset cause produces no invented watchdog event.
- Each fresh accepted call receives a monotonically increasing uint64 token.
  `reset()` discards the pending receipt but preserves the next-token counter,
  preventing an old report attaching to a new attempt. Exhaustion is a contract
  fault, not token wrap. No pending predecessor means no feedback is required.
- Thereafter require one matching applied receipt for the exact previous result
  before using new stall/pushed-out predicates. Its duties must be finite [-1,1];
  disabled means both zero. An actual enable while previous permission was false,
  or actual nonzero for a requested zero/brake, is an application-contract fault.
  Log that violation; never call it a valid FIRST_NONZERO or evidence that R1 passed.
  A missing/stale/mismatched/invalid required applied receipt latches inhibition.
  Do not substitute the governor request as actual application. Quantization or
  external inhibition may reduce actual duty; exact request equality is not a
  claimed physical fact. Feedback reports output-stage settings, not wheel motion.
- Receipt timestamps must lie in the preceding decision-to-current-observation
  unsigned interval: application before completion if duration_valid. The caller
  supplies actual measured execution duration for the completed control tick,
  never time between scheduler calls. Missing duration only marks timing evidence
  incomplete; it must not stop motion. Valid duration is counted once for that
  receipt's recorded match membership (GO through final stopping tick, excluding
  countdown); it cannot attach to the current tick. Reset per accepted attempt.
- Duplicate `t_us` is checked before all processing: return the cached persistent
  outputs/state/diagnostics and same token with fresh=false, all action/event/frame
  pulses cleared. Ignore changed input/feedback; do not replace the pending slot.
  Callers must not apply a duplicate as another fresh output or report it twice.
  Consecutive distinct calls must be less than one uint32 wrap apart.
- Contract-fault bits: 0=invalid consumed observation/context, 1=script start
  failed, 2=invalid active script result, 3=invalid governor request/result,
  4=invalid/missing applied receipt or application violation, 5=stale required
  sensors, 6=invalid D-059 coordinate, 7=token exhaustion. OR reasons, latch to
  reset, select STOPPED, zero duties/disable immediately (the unexpected
  post-commit invariant failure in step 9 has an explicit reporting exception).
  These are not IMU-
  unavailable faults: ordinary B14 missing IMU still gets D-059/B7 fallback.
  Escape's own reset-only fault instead retains EDGE_ESCAPE with inhibition,
  unless explicit STOP or an independent contract fault wins. Never reset Escape
  or Fusion to recover either class. Declared stuck opponent bits only mask those
  bits; low battery/calibration rejection/timeout/tick warnings do not add a veto.
- A valid finite battery observation is required for an initialized fresh tick's
  compensation; missing/nonfinite required voltage is invalid context, not a fake
  nominal voltage. IDLE low-battery warning is strict vbat_v<VBAT_WARN_V on valid
  observations and rearms on a valid non-low observation. No new voltage cutoff.
  Before setup completes, absent voltage is allowed: the one inhibited Governor
  call receives an explicitly invalid nonfinite voltage, returns invalid/zero and
  cannot establish a fake nominal measurement; do not treat this expected BOOT
  result as a contract fault. Test the public invalid-input/filter recovery path.
- Implement the remaining QTR warning as four bounded timers: confirmed white
  AND previous actual enabled duties have strictly opposite nonzero signs for
  strictly more than QTR_STUCK_MS. Breaking either condition clears/rearms that
  bit. This is a warning from reported pivot commands, not measured body rotation;
  it never suppresses edge handling. Report newly warned bits once per episode.

## 4. One bounded fresh-tick sequence

1. Consume/validate the previous applied/duration receipt, complete its pending
   frame and first-duty/timing events, then admit the new token. Update truthful
   bounded ages and boot/fault state. A fault never skips logical STOP handling.
2. If fresh sensor data are admitted, classify QTRs once; compute new_white from
   the prior admitted confirmed mask; observe Fusion once using raw yaw and the
   state at entry. Supply new_white!=0 as its edge event. Preserve masks/pulses
   from this observation for the whole tick; prior cached masks are not fresh.
3. Derive allow_match_start from IDLE-at-entry, match view and no known inhibit.
   Step Lifecycle once with real buttons, raw gyro and the same confirmed masks;
   cancellation/STOP precedes pending service processing. Capture running mode
   only on accepted release. Emit an accepted-calibration bias-update pulse once;
   do not reapply a completed result every tick or reset integrated yaw.
4. Apply D-059's GO/recovery coordinate transaction before moving references.
   Advance the limiter's suppression time without admitting a maneuver. On closed
   permission, cancel transient moving executors/normal qualification; call
   Escape with closed permission so an interrupted active escape retains its
   required permission-loss fault. Existing sticky component state survives.
5. With permission, call Escape once before every other moving choice, using
   current confirmed lines/effective centering/shared SearchSide and the preceding
   actual applied duties. Its active/fault state preempts all scripts. Keep a
   zero-demand escape exit tick, retain genuine inward evidence, then route that
   current observation through normal perception; no second Escape call.
6. Otherwise continue the existing REFLANK executor, else active opener, else
   normal perception/Search/DefendTurn. At GO start only the selected opener once,
   unless Escape preempted it. Any script exit uses the current effective mask;
   reset NormalPerception before its first entry observation, count it once, and
   obey its D-046 loss-tick brake. A SEARCH intent from DefendTurn's timeout starts
   SEARCH even if its side target remains; normal priority resumes next tick.
7. Start a newly selected normal executor at this tick and evaluate its first
   step once, except when a loss/escape-exit brake defers moving evaluation. Bound
   routing to one script exit -> one normal selection -> one new executor entry;
   do not loop around terminal script intents. Newly entered normal executors
   are not immediately rerouted again in this tick. Internal executor phase loops
   retain their existing public bounds. Never backdate entry to a missed deadline.
8. Preview final candidate ATTACK contact read-only for Detector; feed Detector
   once with current cue/centering/local heading, preceding actual duties and
   new-white evidence. Non-ATTACK/edge/gated candidates get an ineligible sample
   so old contact/qualification cannot linger. ALL_IN suppresses stall only. A
   selected stall asks limiter once; an admitted start chooses SwingContext,
   starts REFLANK BACK, records admission and steps it once (charger skip remains
   live). Denial keeps ATTACK under its ordinary cap and starts ALL_IN. Reset
   Detector on a selected exit from its provisional ATTACK into REFLANK; do not
   feed a second sampled observation to accomplish that reset.
9. Finalize the candidate state and requested motion. Validate script status and
   consumed context first, including finite requested duties, finite required
   battery voltage and a known internally selected governor profile. These are
   exactly the rejection inputs named by Governor's public contract; do not
   duplicate its compensation/filter/cap/slew math. Invalid input selects the
   final STOPPED/fault state now. Commit Fusion exactly once to that final state,
   then run Governor exactly once using the committed contact/centering and final
   inhibit. Known invalid voltage may still yield valid=false on this inhibited
   call, with zero output; that is expected and does not need another commit.
   If no fresh Fusion observation exists, do not invoke a fake commit; the stale-
   input fault gates output. Only the valid final commit grants contact authority.
   An unexpected invalid/nonfinite governor result despite successful prechecks
   violates the relied-on component contract: force disabled/zero immediately,
   latch bit 3 and report it, preserve this call's already committed state rather
   than falsely claiming a different contact commit, and enter STOPPED before the
   next fresh tick's commit. Never call either component twice to hide that fault.
10. Commit at most one public Robot state transition, then step Menu once with
    entry state, current genuine qualified START snapshot and final inhibition.
    Services remain typed intents; DRIVE_TEST is unavailable and cannot transition
    into moving DRIVE_TEST. New menu selection does not change running mode.
    Emit ordered events, save one pending frame/receipt slot and return outputs.

Step 9 preserves D-056's final commit then one governor pass. Prevalidating the
finite/profile conditions is smaller than running Governor against a speculative
preview: it needs no extra preview or filter simulation. Normal bad input/script
results are resolved before commit. The narrow unexpected-result defense inhibits
immediately while honestly retaining the already committed state for that call.

## 5. History, event and frame choices

- Adopt the metadata table/order in P1_robot_event_contract_audit.md as version 1;
  expand CORE_CONTRACT_FAULT's payload to the reason bits above. Add category 9
  bit 2 for newly incomplete timing evidence. Treat warning categories as events,
  not permission. Publish explicit shared codes; do not depend on private enums.
- Return prior receipt extensions first (FIRST_NONZERO, then timing warning with
  their original application/completion timestamps), followed by current decision
  events in the audited order. Capacity remains 21: at most 2 prior extensions
  plus 19 current decision events. One final STATE_CHANGE, one combined EDGE,
  one new-stuck mask and one event per fault category keep this bound. Never
  sort raw uint32 timestamps. Preserve prefix/overflow/rejected status if violated;
  logging overflow alone cannot change motion or recursively enqueue a fault.
- The first actual enabled nonzero receipt after that attempt's GO emits FIRST
  once; negative/pivot duty counts, enabled zero brake does not. Snapshot-only or
  service START never arms it. Preserve prequantization nonzero wheel bits.
- Start recording/frame cadence at accepted START, with an immediate t_ms=0
  candidate; every 1,000,000/LOG_HZ us thereafter prepare at most one current
  snapshot. On gaps, advance by whole periods, count skipped slots, never invent
  catch-up frames. Use accumulated elapsed time for t_ms, natural uint32 encoding.
  Force one final stopping-state candidate and then stop cadence until next
  accepted attempt; coalesce it with an already-due frame. Complete/pack the
  pending candidate on its matching next-call actual receipt, using **that tick's
  actual duties**. Preserve frame token and PackStatus. Caller retains the last
  completed match through Robot reset; only a new accepted attempt clears its
  recorder storage. Robot owns no 200-second buffer or 4096-event EventBuffer.
- Freeze one pending candidate per tick; missing duration marks its timing
  evidence incomplete but does not prevent a frame with valid actual output.
  Missing application cannot become an apparently valid applied-duty frame.
  An unflushed final pending receipt at shutdown is incomplete evidence, not an
  implicit zero/measurement. A final fresh STOPPED step can flush it normally.
- Re-flank edge-side history is captured only from a completed escape whose
  participating confirmed white masks were exclusively left (FL/RL) or exclusively
  right (FR/RR). Any bilateral/front-pair/rear-pair/diagonal participation makes
  that episode's side unknown. Do not infer side from pivot direction. Record
  its completion age only on actual exit. Store inward raw yaw only with valid
  exit evidence and project through D-059. Previous swing changes only when the
  executor actually reports SWING entry, not on a denied request or aborted BACK.

## 6. Essential real-Robot scenarios before implementation is called done

1. BOOT/defaults, held START, missing-at-boot IMU, setup-to-IDLE transition,
   service START and all six running-mode snapshots; same-tick countdown MODE
   cancellation cannot become an IDLE menu gesture.
2. Real Buttons/Lifecycle -> full 5.1-second gate -> Robot outputs: exact and
   adjacent boundaries, bounce, sparse/wrapped calls, duplicate GO, STOP on GO,
   zero/disabled before GO and no service calibration/motion start.
3. Every confirmed line mask at GO and during every moving state; persistent
   white, all-black completion, three/all-white fault, bounded replan exhaustion,
   STOP during escape; all final duties/governor caps and fault lifetimes checked.
4. Every opener actual entry/abort/natural exit including DIRECT stale snapshot,
   WAIT ordered cue, SIDESTEP pivot priority and ARC; current perception gets one
   centering count and no direct ATTACK bypass. Verify every state transition row.
5. TRACK/ATTACK centering/contact/target loss with residual side target; immediate
   zero loss tick, one final contact commit, SEARCH/DEFEND delayed movement, no
   stale contact permission after edge/opener/re-flank exits.
6. Actual-duty stall/deflection boundaries and pushed-out precedence: requested
   high duty with actual inhibition must not qualify; limiter limits, denied
   ALL_IN, charger skip and BACK/SWING/TURN_IN event order; real swing alternation.
7. Raw-yaw GO candidate/phantom/stuck continuity, D-059 absent/history/recovery
   branches, world/inward expiry, large finite values, invalid healthy coordinates,
   no stale motor reference after same-tick GO; preserve B14 fallback.
8. Duplicate/invalid/missing receipt, illegal pre-GO actual EN/duty, timestamp
   identity/wrap, missing measured duration versus missing application, no first-
   duty event from requests; ordinary timing warnings do not stop the robot.
9. Bounded event metadata/order/capacity and deliberate overflow, actual frame
   duty binding/cadence/skipped frames/codec statuses, QTR/voltage/IMU warning
   episodes, true-reset-only faults, seeded safety/finiteness properties using
   the actual Robot API rather than another test-only arbiter.

This is a directly implementable proposal. D-060 needs to adopt/revise the listed
input/receipt/fault/order/history/recording choices in one coherent contract;
it does not need another audit-only dependency. Hardware acquisition, actual
MotorGate feedback, complete recorder storage/transport and measured robot WCET
remain HAL/app work and are not proved by the proposed host scenarios.
