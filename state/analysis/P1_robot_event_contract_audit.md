# Robot event-result public-contract audit — 2026-09-23 Asia/Dubai

Status: recommendations for the future Robot, not accepted metadata policy,
implemented event collection or a gate verdict. Only this new audit is owned.
No implementation `.cpp`, build, hardware operation or commit was used.

Sources: BEHAVIOR B0/B2/B3/B4/B5/B9/B11/B14/B15, B7's required turn-timeout log;
types.h/logframe.h/countdown.h/edge.h/opp_fusion.h/stall.h/fsm.h/openers.h/motion.h;
D-028/D-056 and current D-057 START-routing public additions; existing
P1_robot_interface_audit.md items 10–12. Physical reporting remains caller-owned.

## 1. Established requirements and gaps

- B15 requires exact-tick START_RELEASE, GO, FIRST_NONZERO_DUTY, committed state
  changes, EDGE with mask, CONTACT, STALL, re-flank phases, PHANTOM_SET and faults.
  core::Event already contains these ten kinds; no new kind is needed below.
- EventInput is t_us/u32, type/u8, detail/u8, value/u16. packEvent checks only the
  event enum; it does not validate caller-defined metadata. The wire record is
  exactly eight bytes and uses explicit little-endian encoding.
- B15 frames already have a precise 25-byte codec; they do not have a scheduler,
  storage owner, time epoch, applied-duty source or invalid-data recovery policy.
- EventBuffer implements D-028: first 4096 successfully encoded events, append
  order retained, no overwrite, explicit overflow and saturating rejected count.
  A Robot batch can overflow before that buffer; its loss must be separate evidence.
- Component event support is uneven: Gate has pulses; Contact requires the final
  valid commit; Fusion exposes fresh/phantom/new-stuck pulses; Escape has entry,
  replacement/exit and latched fault; Detector.stalled is a level. Robot must
  convert decisions/level transitions to events without replaying them.
- Reflank's successful start requires caller-recorded BACK; its result explicitly
  permits both entered_swing and entered_turn_in, in that order, on one call.
- D-056 requires preceding actual applied electrical duties for stall/escape
  decisions. Governor output alone is not an application receipt. Actual duration
  of Robot::step cannot already be supplied as that same call's input.

## 2. Proposed per-tick envelope and lifecycle

Return a fixed array of EventInput plus count, overflowed and a saturating
rejected count, alongside decision state/mode, observation identity, diagnostic
values and a separate candidate frame. No allocation or internal unbounded queue.
Keep the existing long-lived EventBuffer with its recorder owner.

Recommended lifecycle invariants, required for the capacity proof below:

1. One genuinely fresh observation/Robot step per decision sequence. Repeated
   sequence/timestamp returns no new event/frame pulse and cannot restart modules.
2. Select candidate states freely, but commit at most one externally visible
   Robot state per tick. Log old committed state -> new final committed state;
   do not invent COUNTDOWN->OPENER->TRACK transitions when OPENER was only a
   provisional routing candidate. Actual accepted script phase entries remain
   separate events, even if they have zero residence time in that call.
3. Observe Fusion once, preview as needed, commit once to final state. Only valid
   commit.result.contact_started emits CONTACT. Preview can never emit an event.
4. Ask the limiter at most once for a selected stall decision; advance/step each
   relevant executor within its public bounded contract. A blocked or suppressed
   Detector level does not create repeated STALL events.
5. Aggregate same-tick sensor faults by mask and diagnostics by the fixed fault
   categories below. For retained levels, emit only new declarations/rises. Define
   reset/rearm explicitly; no per-tick event for a continually held fault.
6. The caller can complete the same logical tick's evidence after applying output
   and measuring execution, via matched bounded reports. These reports never
   rerun Robot arbitration, governor, debouncers or motion. A decision batch, one
   application extension and one timing extension together form the tick envelope.

The minimal proposed event capacity is **21 entries** by the conservative proof
in section 5. This is not a claim that all 21 can physically coincide. Record the
representation limit explicitly in the eventual public contract; adding sources
requires revisiting the proof, not relying on accidental spare space.

## 3. Proposed metadata version 1

These byte codes are new recommendations. Publish the accepted mapping in one
shared public codec-facing header; do not depend on private enum ordinals.
All unspecified bits and reserved values are zero. Reject invalid semantic
metadata explicitly before calling packEvent; that codec cannot detect it.

| Event | Emit exactly when | detail | value |
|---|---|---|---|
| START_RELEASE | Gate accepts the match release; service-only D-057 releases excluded | Snapshotted match mode, 1–6 | 0 |
| GO | Gate.go; record even if a higher safety condition inhibits actual motion | Snapshotted match mode, 1–6 | 0 |
| FIRST_NONZERO_DUTY | First valid enabled actual applied nonzero duty after this attempt's accepted release/GO, per section 6 | Bit 0=left actually nonzero, bit 1=right actually nonzero | Low byte=signed left duty code; high byte=signed right code, each scale 127/two's complement, rounded as FrameInput |
| STATE_CHANGE | Old committed state differs from final committed state | Old public core::State value | New public core::State value in low byte; high byte 0 |
| EDGE | Any newly confirmed white bit OR Escape entered/replanned/exited on this observation | Bits 0=new-white, 1=entered, 2=replanned, 3=exited, 4=pushed-out selection on entry/replacement | Bits 0–3=current confirmed line mask; 4–7=newly-white mask; 8–15=replacement count after this observation |
| CONTACT | Valid final Fusion commit raises the contact latch | Bit 0=close_cue, bit 1=impact_cue | Current effective opponent mask in low seven bits |
| STALL | A non-suppressed qualified detector result is actually selected for limiter/re-flank routing this tick | Bits 0=timer route, 1=deflection route, 2=re-flank admitted, 3=ALL_IN started because denied | Attempts retained in limiter's rolling window after request |
| REFLANK_PHASE | Successful BACK start; entered_swing; entered_turn_in | Explicit phase code 1=BACK, 2=SWING, 3=TURN_IN | Explicit direction 1=RIGHT, 2=LEFT; not motion::Direction's ordinal |
| PHANTOM_SET | Fresh Fusion phantom_set pulse | 0 | Normalized world bearing in signed centidegrees/two's complement, nearest with exact halves away from zero; canonicalize a rounded -18000 to +18000, keeping (-18000,18000] |
| FAULT | New diagnostic according to the category table below | Explicit category code 1–10 | Category-specific payload below |

EDGE details deliberately distinguish an actual new white observation from a
persistent-white entry/replacement. Derive newly_white from successive admitted
confirmed masks, including gated observations; initial previous mask is zero.
Log those observations while inhibited if fresh acquisition is provided, without
granting motion. The component `edge_event` cue is newly-white evidence, not an
arbitrary replay of a packed EDGE entry/replacement event. A GO entry with white
already held has entered=true/newly_white=0. A successful replacement without a
new bit has replanned=true; an attempted replacement that faults is not replanned.
Exit uses current mask zero and the result's post-exit replacement count zero.
Bound encoded replacement count to <=255 and limiter count to <=65535 in the
representation contract; current defaults fit. Never silently truncate a future
configuration outside those bounds.

FIRST_NONZERO detail tests the actual finite duty, before quantization. A valid
small nonzero duty can quantize to byte zero; its wheel-mask bit still proves
which reported wheel was nonzero. The record does not prove wheel movement.

| FAULT code | Category and event lifetime | value |
|---|---|---|
| 1 | IMU_UNAVAILABLE: first valid availability report is unavailable, or available->unavailable; recovery rearms a future loss | 0; do not invent init-failure/stale-data cause from imu_ok alone |
| 2 | OPPONENT_STUCK: one event per nonempty new_fault_mask, not per sensor or retained fault | Low seven bits=newly declared sensor mask |
| 3 | QTR_STUCK_WARNING: newly qualified warning bits supplied by an explicit future detector; warning still obeys white | Low four bits=new warning sensor mask |
| 4 | LOW_BATTERY: new valid strict-under-VBAT_WARN_V episode in IDLE; validated non-low observation rearms | 0; measured voltage belongs to frame/diagnostic snapshot |
| 5 | CALIBRATION: new attempt rejection/start failure, once per attempt; cancellation/new accepted release resets attempt reporting | Bit 0=calibration_rejected, bit 1=service_start_failed; no invented rejection cause |
| 6 | ESCAPE_FAULT: NONE->latched Escape fault; reset-only | Explicit reason 1=WHITE_PATTERN, 2=REPLAN_LIMIT, 3=PERMISSION_LOST, 4=INVALID_CONTEXT |
| 7 | CORE_CONTRACT_FAULT: newly detected invalid required core context, aggregated once on first latch; disposition still needs Robot policy | Bits 0=invalid observation/context, 1=script start failure, 2=invalid active script result, 3=invalid governor request; known simultaneous causes ORed |
| 8 | TURN_TIMEOUT: public one-call B7 timeout pulse, aggregated across observed executors | Bits 0=Escape row, 1=Reflank, 2=Search, 3=DefendTurn, 4=Flank/WAIT delegate; ordinary timed arc/straight expiry is not a fault |
| 9 | TICK_STATISTICS: newly exceeded strict overrun-rate threshold or newly saturated retained statistics after one matched duration report | Bit 0=rate threshold rose, bit 1=statistics newly saturated; full max remains in diagnostics/frame |
| 10 | RESET_CAUSE: one first-boot observation of a supplied verified watchdog cause | 1=watchdog; unknown/unavailable cause emits nothing |

Warning code names do not add a motor veto. In particular calibration rejection,
low battery, timeouts and tick warning cannot weaken or invent B2 safety policy.
QTR warning detection, low-battery validity and hardware reset cause are currently
dependencies, not facts supplied by existing bools/default values. Code 7 also
does not silently choose the Robot's future invalid-context recovery policy.

## 4. Deterministic ordering and timestamp ownership

For a logical tick, publish decision events in this exact order:

1. START_RELEASE, GO.
2. The one combined EDGE, then PHANTOM_SET.
3. FAULT categories ascending 1–8, then 10; category 9 awaits duration evidence.
4. STALL, STATE_CHANGE, CONTACT.
5. REFLANK_PHASE entries BACK, SWING, TURN_IN.
6. Application extension: FIRST_NONZERO_DUTY, if qualified.
7. Measurement extension: FAULT category 9, if qualified.

This is deterministic observation/decision order, not fabricated causal physical
timing. A final re-flank/edge/STOP decision has no provisional CONTACT entry.
Log admitted re-flank phases even when same-call script advancement immediately
exits them; do not replace them with only the final phase. STOP/fault arbitration
suppresses decisions that never happened, while genuinely observed new sensor
faults/white can still be recorded with the final inhibited state change.

Decision events use the current admitted t_us. START uses the actual accepted
qualification tick, not the earlier raw release. Application event uses the
caller's matched actual apply timestamp; timing warning uses the matched measured
completion timestamp. Neither substitutes next-loop arrival time. A report that
arrives later retains its source identity/time and is not reassigned to a newer
tick. Never numerically sort uint32 timestamps across wrap; append in the above
source/sequence order and retain observation identities outside the 8-byte wire
format as needed for matching. Recorder must accept each extension before the
next logical tick's events, or explicitly report evidence order/incompleteness.

## 5. Conditional maximum-events proof and rejection behavior

| Producer per admitted logical tick | Maximum | Public basis / additional required Robot invariant |
|---|---:|---|
| Accepted START and GO | 2 | Gate bool pulses; conservative sum does not require them to coincide |
| Final state change | 1 | Proposed one committed final state per tick |
| Combined EDGE | 1 | One fresh line observation; Escape at most one replacement per call; OR flags |
| Final CONTACT | 1 | One valid Fusion commit, single rising flag |
| Selected STALL | 1 | Detector level consumed in at most one limiter decision |
| Re-flank phase entries | 3 | One successful BACK start plus two public ordered entry bools |
| PHANTOM_SET | 1 | One fresh Fusion observation/pulse |
| All FAULT categories | 10 | One per explicit category, sensor/component masks aggregate; timing report included |
| Actual FIRST_NONZERO_DUTY | 1 | One matched application report, per-attempt first latch |
| **Conservative total** | **21** | 19 decision + at most 1 application + at most 1 measurement event |

This is a proof for the proposed source/lifecycle contract, not an implementation
proof: Robot does not yet exist. Arbitrarily reporting per-sensor FAULT records,
multiple committed state transitions, duplicate application reports or new fault
categories invalidates it. Initial startup/STOP information is already accounted
for; startup must not add an unbounded list of historical faults.

Batch append failure must retain the first capacity entries, latch batch overflow
and increment its saturating rejected count. Do not attempt to enqueue an overflow
FAULT into an already full batch. Preserve batch loss, semantic-metadata failure,
packEvent INVALID, frame PackStatus and downstream EventBuffer overflow as distinct
out-of-band statuses/counts; summaries/dumps must show incomplete evidence. A
batch loss may still be followed by a successful recorder append and vice versa.
Recording failure never changes selected motion or claims a safety pass. Normal
valid production sources must prove zero batch rejection under the accepted bound.

## 6. Actual applied-duty evidence and FIRST_NONZERO

The application report needs decision identity, apply timestamp, enabled flag,
the two finite actual commanded electrical duties in [-1,1], and a validity
indicator. It reports what the output stage applied, not the earlier requested
or governor-limited demand, and does not claim measured motor voltage/motion.
If hardware is inhibited, the actual report is disabled/zero. Missing, stale,
unmatched, duplicate or invalid feedback cannot become a first-duty event.

After a new accepted match release, arm a new first-duty observation; require that
attempt's GO before accepting a first event. Record the first matched report
with enabled=true and either actual duty strictly nonzero. Do not fire on a
nonzero request with actual inhibit, or on merely enabled zero-duty braking.
Negative/pivot duties count. Once reported, continuing nonzero output cannot
retrigger until a new accepted attempt/reset. Reported nonzero before GO is an
explicit rule-violation diagnostic, never relabeled as a valid first-after-GO
event; how to expose that new violation must be selected before integration.

Use the same identified last applied report for the next tick's D-056 stall and
D-049 pushed-out predicates. A missing feedback policy must be defined separately
and conservatively; do not silently pretend an unknown report proves zero or
that previously returned Outputs necessarily reached hardware.

## 7. Scheduler measurement and frame-cadence interface gaps

- Provide a matched completed-tick measurement with measured execution_us and
  completion timestamp, exactly once. logframe::observeTick accepts supplied
  duration; it cannot know match membership, freshness or measurement scope.
  Specify whether the measured scope includes acquisition, Robot, application,
  recorder and scheduler overhead. If statistics are available only next tick,
  retain that lag/sequence explicitly. Never label a start-to-start interval as
  execution duration or claim that host time proves the robot's <800 us budget.
- B14 overrun is strict >1000 us; ratio warning is strict >1%, with saturation
  carried as incomplete retained-prefix evidence. Frame tick_max_us may clamp
  above 65535; preserve CLAMPED and the full u32 maximum outside the packed frame.
- Cadence needs a named recording epoch and membership/end policy. Recommend
  accepted START as the attempt epoch with one immediate snapshot, then 20 ms
  deadlines at LOG_HZ=50; recorder boot-fault retention/reset policy remains a
  separate required choice. Do not erase fault evidence implicitly at START.
- At most one frame per fresh observation. If a deadline is missed, emit the
  current snapshot and count skipped deadlines; never fabricate intervening
  sensor readings or catch up with repeated stale frames. Keep phase anchored to
  the epoch instead of drifting each deadline to a late observation's time.
- Frame payload must combine one identified admitted sensor snapshot, final
  committed state/mode, and its matching actual applied duties. Finalize the
  candidate frame only after application evidence; nonfinite/unknown data must
  remain explicit INVALID/unavailable status, not invented zeros. A field's zero
  value cannot by itself encode missing evidence under the current codec.
- Define a wrap-safe extended recording clock for t_ms. Repeatedly using raw
  `t_us/1000` jumps backward at the 71.6-minute micros wrap. The u32 t_ms wire
  representation can wrap naturally after its own longer period; preserve epoch.
- At least 200 s storage, frame ring policy, target RAM capacity, Bridge/IDLE
  dumping and physical timing are outside this per-tick P1 contract. No HAL/P2
  design or unknown transport capability is inferred here.

## 8. Required acceptance scenarios before implementation approval

| Scenario | Contract evidence required |
|---|---|
| Qualified START / service START / STOP tie | Accepted match release only; correct qualification timestamp; service pulse or STOP-suppressed release never logs START_RELEASE/GO. |
| GO with persistent white / immediate pattern fault | GO retained, correct combined EDGE entry with zero new mask where appropriate, one newly latched FAULT, one final state change, no false first duty. |
| White clears/reasserts/replans/exits | One combined event per observation, exact masks/flags/count; no per-tick event for unchanged white alone; replacement fault never claims successful replacement. |
| Simultaneous stuck bits / phantom | All seven stuck declarations in one mask event; single phantom replacement with signed bearing boundary fixtures; cached Fusion produces no repeated pulse. |
| Contact candidate / re-flank decision | Preview does not emit CONTACT; final centered ATTACK rise does; final REFLANK/EDGE/STOP clears permission without a provisional event. |
| Stall level / limiter deny / ALL_IN | One selected decision with explicit route/outcome; repeated stalled level while suppressed does not flood events; new post-suppression decision is distinct. |
| BACK->SWING->TURN_IN same call | Three phase events retained and ordered, even if final routing exits the script; no synthetic intermediate state-change records. |
| B7 timeout and other faults | Pulse maps once to correct source mask; timed straight/arc normal completion is not a timeout FAULT; persistent levels do not replay. |
| Batch bound / forced overflow | Construct every source permitted by the interface, prove count<=21; bounded append 20/21/22 retains exact prefix and reports rejection/saturation without recursive logging. |
| Recorder overflow | 4095/4096/4097 successful encodings keep first events; batch overflow and recorder overflow remain distinguishable; later frame recording continues. |
| Actual output differs from request | Nonzero request but disabled/zero application gives no first event; enabled zero brake gives none; first negative/pivot application does; sub-LSB nonzero preserves wheel-mask evidence. |
| Feedback identity/timing | Invalid/missing/stale/duplicate/cross-attempt report never fabricates FIRST_NONZERO or next-tick applied feedback; exact source apply timestamp retained across wrap. |
| Illegal pre-GO feedback | Detect reported nonzero as an explicit contract/rule violation; never claim a normal post-GO event or passing R1 evidence. |
| Timing boundaries | 999/1000/1001 us; ratios just below/equal/above 1%; count saturation and max>65535; exactly one observation per matched measurement. |
| Frame cadence/gaps/wrap | Initial/20 ms boundary +/-1 us and +/-1 ms, sparse multi-period gap, no stale catch-up frames, explicit skipped count, micros and t_ms wrap. |
| Encoding/statuses | Literal eight-byte metadata fixtures, signed angles/duties, invalid semantic metadata, INVALID event enum, CLAMPED/INVALID frame, no silently valid zero record. |
| Reset/attempt lifetime | Old pending reports cannot attach to new attempt; selected fault/first-duty lifetimes reset exactly once; unknown hardware reset cause is never invented. |

Next action: coordinator chooses metadata, lifecycle and required evidence APIs
under D-051, including the unresolved pre-GO application-violation diagnostic and
recording epoch/lifetime. Commit the public contract before independent tests and
Robot implementation. This audit supplies no event-batch runtime pass or physical
countdown/WCET verification.
