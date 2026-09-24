# DECISIONS (append only, ADR style)

Format: ID, date, status (accepted / superseded by D-xxx / pending), context, decision, consequence.

## D-001 (2026-09-22, accepted) Two IBT-2 drivers, motors paralleled per side
Context: each BTS7960 double module drives one motor channel with two PWM inputs; the UNO Q has 6 PWM pins; 4 drivers need 8.
Decision: one IBT-2 per side; front and rear motor of a side in parallel.
Consequence: 4 PWM pins used; left/right pair on each side cannot be controlled separately; two spare boards for match day.

## D-002 (2026-09-22, accepted) Real-time control on the MCU only
Context: edge crossing takes 12 ms at 2.5 m/s; Linux boot about 35 s; brownout exposure; rule on remote control.
Decision: sensing, decisions, and motor control run on the STM32U585 at 1 kHz. Linux builds, flashes, stores logs.
Consequence: no dependency on Linux during a match; judges get a clear rationale.

## D-003 (2026-09-22, accepted) Add an IMU on Qwiic
Context: timed turns drift with battery and tire state; stall and impact cues need acceleration.
Decision: 3.3 V IMU on the Qwiic connector (Wire1), bias calibrated during the 5-second hold.
Consequence: one purchase; timed-turn fallback required if the IMU fails.

## D-004 (2026-09-22, accepted) Sensor layout
Decision: JS200XF at 0, -15, +15 degrees (front); MZ80 at -90, +90, -135, +135 degrees; QTR-1RC at the four corners.
Consequence: flank and rear coverage during arcs; no dedicated straight-back sensor.

## D-005 (2026-09-22, accepted) JS200XF range pads bridged (120 cm)
Context: 200 cm range reaches well beyond a 150 cm ring.
Consequence: fewer spectator detections; phantom mask still required.

## D-006 (2026-09-22, accepted) Power isolation
Decision: Schottky diode + 1000 uF hold-up feeding UNO Q VIN; separate 5 V buck for sensors; 30 A fuse and main switch.
Consequence: brownout test B7 must pass.

## D-007 (2026-09-22, accepted) Hybrid flanking strategy
Decision: flank opener, head-on when well placed, re-flank on a stalled push. Openers in priority: SIDESTEP (default SIDESTEP_R), DIRECT, ARC, WAIT.
Consequence: stall detection and re-flank are core features (B11).

## D-008 (2026-09-22, accepted) Matches first
Decision: award polish (P6) only if GATE P4 passes by 30 September.

## D-009 (2026-09-22, accepted) Agent workflow
Decision: Claude Code builds and orchestrates with sub-agents; Codex reviews at every gate; firmware compiled and uploaded on the board over SSH (adb fallback).

## D-010 (2026-09-22, accepted) Stall detection by inference
Context: no encoders; an IMU cannot measure constant speed.
Decision: contact timer + deflection cue; IMU displacement refinement behind a flag, enabled only if P4 logs support it.

## D-011 (2026-09-22, accepted) Buttons on one ADC pin
Decision: START and MODE on A1 through a resistor ladder, freeing D10 for MOTOR_EN with a pull-down.
Consequence: motors held off by hardware during boot and reset.

## D-012 (2026-09-22, accepted) Speed governor from measured data
Decision: SEARCH_DUTY_MAX from the P3 stopping table (worst stop under 70 % of R_room); full duty only after contact.

## D-013 (2026-09-22, pending) IBT-2 logic supply
Options: VCC from 3.3 V (default) or 5 V. Decided by bench test B4.

## D-014 (2026-09-22, pending) Organizer answers
Placeholder for replies to docs/PLAN.md section 5 (orientation, mode changes, radios, arena height, activation timing, scale, blade color).

## D-015 (2026-09-22, accepted) User-authorized Codex role migration
Context: the user explicitly invoked docs/prompts/CODEX_KICKOFF.md and authorized Codex takeover in this session.
Decision: Codex implements and orchestrates; a separate fresh-context reviewer reviews without editing implementation. Supersedes ONLY the agent-role portion of D-009 and corresponding legacy role restrictions. A separate Codex context is not cross-model review.
Consequence: preserve D-009's on-board compilation/upload over SSH and verified adb fallback, all original documents, R1-R11, phase dependencies, and human gates. No wiring, behavior, purchase, locked-test, motor-run, or phase approval is implied. Coordinator alone merges shared state/configuration; delegated fact checks own separate analysis files.

## D-016 (2026-09-22, accepted) User-directed offline P1 development
Context: after the P0 hardware checkpoint, the user explicitly instructed:
"continue working and assume these things are tested and working, i don't have
hardware connected currently, but commence working".
Decision: proceed with P1 host development using the intended setup as a development
assumption. This is a narrow scheduling exception to the P0-before-P1 development
dependency, not a claim that any physical check passed. The active implementation
phase is P1 (host only); P0 acceptance remains HARDWARE-PENDING / GATE-PENDING.
Consequence: preserve the required P0/P1 exit evidence and human gate rights. No
GATE P0 PASS, PINMAP OK, electrical verification, behavior-conflict resolution,
locked-test change, P2 HAL work, target upload or motor run is authorized by this
assumption. Begin independent spec-derived tests and unambiguous pure modules;
defer dependent behavior until its specific protected decision is resolved.

## D-017 (2026-09-22, accepted) Final electrical governor envelope
Context: SC-C showed that B6 compensation after cap/slew could violate R6 and the
measured search cap at low battery voltage. The user explicitly replied
"Approve A for the governor" to the presented option.
Decision: apply voltage compensation first, then enforce the state cap and
acceleration slew on final electrical duty. Braking and safety-cap reductions
remain immediate. Full duty still requires centered contact.
Consequence: update B6's pipeline; retain all B16 values. Test 9.0/11.1/12.6 V,
changing battery voltage, centered/contact loss, cap reductions, reversal and
exact slew limits. This does not authorize ALL_IN exceptions, wiring or motor runs.

## D-018 (2026-09-22, accepted) Gated-state services precede output inhibition
Context: SC-D1 identified B2's early return suppressing the countdown and other
inhibited-state services. The user explicitly replied "Approve A for tick ordering".
Decision: update button/countdown/gated-state services before the motor-output
gate. BOOT, IDLE, COUNTDOWN and STOPPED still return zero duties and disabled motors.
Consequence: service updates are possible while inhibited. This resolves only
ordering; it does not choose ADC/button semantics, calibration/sample eligibility,
snapshot aggregation, edge policy, or STOP recovery. Those conflicts remain open.

## D-019 (2026-09-22, accepted) Full hold starts after release debounce
Context: SC-J left the hold timestamp ambiguous. The user explicitly replied
"Approve A: after debounce" to the presented timestamp choice.
Decision: start COUNTDOWN_MS + COUNTDOWN_MARGIN_MS at the tick when START-release
debounce completes. With unchanged defaults, this is a full 5.1-second hold after
at least 20 ms of stable release; a delayed qualifying tick starts the hold then.
Consequence: connect Buttons to Gate using qualification time, never the earlier
raw edge. Test bounce, delayed ticks, exact deadlines, reset/boot-held START,
cancel/STOP and wraparound through the composed controller. Existing locked tests
remain unchanged; add new integration tests. This resolves the START time-anchor
portion of SC-J only, not ADC decoding or both-held STOP/recovery semantics.

## D-020 (2026-09-22, accepted) Persistent edge and inhibited all-white fault
Context: SC-D2 left all-four-white without a black direction and rising-only
edge handling could miss white already present at GO. The user explicitly replied
"Approve A: inhibited all-white fault" to the presented policy.
Decision: after the countdown gate permits motion, enter or remain in EDGE_ESCAPE
on persistent white. All-four-white latches a fault with zero duties and motors
disabled until reset. Otherwise leave escape only when all sensors are black and
its script is finished. Preserve the configured push-through exception, disabled
by default; no positive window is enabled by this decision.
Consequence: implement a pure edge guard for the default zero-window configuration;
test every mask, white at GO, persistent white, re-entry, completion/clear ordering
and a fault that cannot clear on black readings alone. Motion directions, forward
escape duty (SC-M), replan-limit direction and actual HAL safety remain separate.
No sensor acquisition change, pin approval, physical test or motor run is implied.

## D-021 (2026-09-22, accepted) Forward escape uses the existing 0.80 limit
Context: SC-M identified missing forward escape duty/cap. The user explicitly
replied "Approve A: reuse 0.80" to the proposed reuse of EDGE_BACK_DUTY as the
requested base and final cap, retaining the specified 70% inner-wheel bias and
approved governor rules.
Decision: forward escape requests use EDGE_BACK_DUTY (currently 0.80) as base and
final cap. Where B4 specifies a biased forward segment, request 70% of that base
on the inner side. Apply the same D-017 compensation, per-side caps and slew.
Consequence: add a named forward governor profile and pure straight/biased demand
builder. Centralize the existing B4 70% ratio in config without changing B16
defaults. This specifies requests and caps, not measured speed/trajectory: voltage
compensation and per-side saturation may alter the final side ratio. Timed motion,
heading hold, escape scripts and physical validation remain pending.

## D-022 (2026-09-22, accepted) Bounded straight-line heading correction
Context: SC-N identified a missing gain and limit for B7 straight motion. The
user explicitly replied "Approve A: bounded heading correction".
Decision: use existing K_TURN_PER_DEG (0.02 duty/degree) for straight heading
correction; limit correction magnitude to min(TURN_MIN_DUTY, abs(base duty)).
This prevents correction from reversing a wheel. All requests retain governor
caps; no B16 value changes or new tunables are introduced.
Consequence: implement/test signed heading correction, forward/reverse requests,
zero duty, saturation, symmetry and IMU availability. Defaults need physical
validation; this does not approve wiring, a motor run or a phase gate.

## D-023 (2026-09-22, accepted) Apply voltage compensation once through duty
Context: SC-N identified undefined extra duration compensation alongside B6's
duty compensation. The user explicitly replied "Approve A: compensate duty only".
Decision: configured segment durations and angle * TURN_MS_PER_DEG fallback
timing remain unchanged across voltages. Apply compensation once through the
approved B6 governor, with its final caps and slew.
Consequence: visibly amend B4/B7; implement exact duration/timeout boundaries,
wraparound and voltage-independent timing tests. Caps and slew can still alter
physical travel, so no measured equivalence is claimed. Preserve all B16 defaults.

## D-024 (2026-09-22, accepted) Countdown service sampling and retention
Context: SC-K left B3 calibration eligibility/aggregation, warning persistence and
snapshot aggregation undefined. User replied "Approve A: countdown service contract".
Decision: calibrate over [1.5 s, 4.5 s), averaging finite readings marked IMU-valid;
spread is maximum minus minimum. Require at least two valid readings and reject
the calibration if any reading in the window is invalid. Keep previous bias on
rejection. Latch a white-line warning during the final second and retain the
latest confirmed opponent mask from the final 300 ms.
Consequence: add explicit configuration constants for these specified boundaries
and the approved minimum count. Test exact endpoints, spread equality, invalid/
missing data, cancellation, delayed calls and wrap. Logical input freshness is a
caller contract; no real calibration or physical IMU acquisition is proved.

## D-025 (2026-09-22, accepted) ALL_IN preserves the safety envelope
Context: SC-E1 identified unconditional full duty in B11.3 conflicting with R5/R6.
User replied "Approve A: ALL_IN retains safety rules".
Decision: ALL_IN suppresses stall checks for ALL_IN_MS only. Full duty still
requires centered contact; target loss still brakes and edge handling retains
priority under the existing default-disabled bounded push-through rule.
Consequence: amend B11.3 visibly; future re-flank/FSM tests must cover centering/
contact loss, target loss, every edge mask, expiry and wrap. This approval does
not itself implement ALL_IN, change any cap or enable push-through.

## D-026 (2026-09-22, accepted) Deterministic bearing conflicts and memory
Context: SC-L lacked simultaneous rear-sensor and initial memory semantics.
User replied "Approve A: deterministic bearing memory".
Decision: both rear sensors keep the previous bearing and flag a conflict, as
specified for both side sensors. With no prior detection, expose no valid
bearing. Simultaneous first appearance of both front side sensors retains the
previous last-front-side value, unknown when no previous side exists.
Consequence: test all sensor masks/group priorities, conflict/no-history cases,
front recency ties, finite world angles and wrap-safe timestamps. No unsupported
target or side is invented. Other B5 stages remain separate.

## D-027 (2026-09-22, accepted) Horizontal impact and bounded contact latch
Context: SC-L left impact magnitude and contact-latch lifetime undefined.
User replied "Approve A: bounded contact lifetime".
Decision: IMU-valid horizontal sqrt(ax*ax + ay*ay) strictly above IMPACT_G is
an impact cue. Retain CONTACT_TICKS close-sensor cues. Latch contact only during
centered ATTACK; clear on target loss, loss of centering or leaving ATTACK, with
a fresh latch after re-flank.
Consequence: test exact impact/sample thresholds, invalid IMU values, all state
exits/re-entry and governor full-duty eligibility. Current cues may establish a
new latch; an old latch alone cannot authorize a later target. No physical impact
or IMU sampling measurement is supplied by this software decision.

## D-028 (2026-09-22, accepted) Retain first events and expose overflow
Context: SC-E2 identified finite4096 capacity versus unlimited no-drop wording.
User replied "Approve A: retain first events and report overflow".
Decision: retain the first4096 events; further events latch overflow and increment
a saturating rejected-event counter. Continue frame recording; clearly mark the
dump as incomplete evidence. Overflow does not change motion.
Consequence: visibly amend B15. Later recorder-buffer tests must cover4095/4096/
4097, earliest-event preservation, counter saturation, continued frames and dump
status. The current pure codec is not an implemented recorder ring or transport.

## D-029 (2026-09-22, accepted) Bounded phantom chase episode
Context: SC-O1 left the B5.5 time anchor and earlier contact history undefined.
User replied "Approve A: bounded phantom chase episode".
Decision: start at the first front-only TRACK/ATTACK observation, preserve the
episode across TRACK/ATTACK, end it when that chase ends and remember every
contact cue during it. An edge within PHANTOM_WINDOW_MS may mark the current
world bearing only if no contact occurred and heading is valid.
Consequence: implement explicit episode history, finite heading checks and exact
window/transition/contact regressions; no hardware fact or gate is inferred.

## D-030 (2026-09-22, accepted) One replaceable phantom marker
Context: SC-O2 left B5.5 marker storage and replacement unspecified.
User replied "Approve A: latest phantom replaces previous".
Decision: keep one active phantom bearing. A newly qualified PHANTOM_SET replaces
it and starts a fresh PHANTOM_MS interval.
Consequence: bounded storage, replacement/expiry/circular-distance tests; no
multiple-marker retention strategy is introduced.

## D-031 (2026-09-22, accepted) Observed heading span and latched stuck faults
Context: SC-P left B5.6 rotation evidence, IMU gaps and recovery undefined.
User replied "Approve A: observed sweep and reset-only recovery".
Decision: require continuous detection for OPP_STUCK_MS and an accumulated-heading
span (maximum minus minimum) strictly greater than 360 degrees. Invalid/unavailable
IMU restarts qualification. Once declared, a stuck bit remains ignored until reset,
even if it subsequently clears.
Consequence: test exact time/angle limits, clear/reassert, IMU gaps, observed span,
one-shot faults and reset; a host heading sequence is not a physical sweep test.

## D-032 (2026-09-22, accepted) Qualified timer or deflection stall trigger
Context: SC-Q left B11.1 early deflection and two-wheel duty qualification unclear.
User replied "Approve A: qualified timer or deflection".
Decision: trigger after STALL_MS continuous qualification OR earlier deflection
since contact strictly above STALL_DEFLECT_DEG. Both routes require centered
ATTACK contact, both forward final electrical duties at least STALL_MIN_DUTY,
and no edge event since contact. Keep IMU displacement refinement disabled.
Consequence: test exact thresholds/signs, contact/edge histories, invalid IMU and
D-025 suppression. This inference still needs P4 logs; no measured stall is claimed.

## D-033 (2026-09-22, accepted) SIDESTEP phase-specific detection priority
Context: SC-T identified competing front/outer-side aborts in B12 O1.
User replied "Approve A: phase-specific front priority".
Decision: during DRIVE/TURN_IN, current front has priority; otherwise outer-side
or outer-rear detection requests DEFEND_TURN. During PIVOT ignore front, but
outer-side/rear detection still requests DEFEND_TURN.
Consequence: implement both mirrors and simultaneous-mask tests in every phase.
This does not add the SIDESTEP outer-side exception to ARC or override edge priority.

## D-034 (2026-09-22, accepted) Current perception governs opener exits
Context: SC-U identified literal opener ATTACK exits versus B9 current-target rules.
User replied "Approve A: current perception governs opener exits".
Decision: opener exits request normal perception arbitration. Current front selects
TRACK; ATTACK requires ATTACK_ENTER_TICKS consecutive centered observations. Current
side/rear selects DEFEND_TURN; no current target selects SEARCH. A saved countdown
snapshot alone cannot authorize ATTACK. Preserve immediate target-loss braking,
contact rules and edge priority.
Consequence: executor outputs remain transition intents. Implement and test the
actual transitions in Robot integration; no snapshot or script grants motor permission.

## D-035 (2026-09-22, accepted) Qualified STOP hold and reset-only recovery
Context: remaining SC-J left B13 both-held STOP debounce anchoring/recovery undefined.
User replied "Approve A: qualified STOP hold and reset-only recovery".
Decision: for logical BOTH input, start the complete BTN_LONG_MS when BOTH has
qualified for BTN_DEBOUNCE_MS. Any observed release before expiry cancels the
pending hold. Once STOPPED, remain inhibited until reset; reset returns to the
normal boot/start sequence.
Consequence: implement logical hold and Controller composition with exact/adjacent
debounce/hold deadlines, release priority, boot-held BOTH, delayed calls, wrap,
latched release behavior and reset tests. SC-A electrical decoding remains separate;
this neither proves that A1 can distinguish BOTH nor authorizes a board reset.

## D-036 (2026-09-22, accepted) Bounded TRACK and ATTACK steering
Context: SC-V left B9's extra pivot and small corrections unquantified. User
replied "Approve A: bounded steering with existing gains".
Decision: mix left=base+correction and right=base-correction, bounded to [-1,1].
TRACK uses TRACK_DUTY and K_TRACK_PER_DEG times bearing, adding signed
TURN_MIN_DUTY for the +/-15-degree front-only rows; keep SEARCH_FORWARD governor.
ATTACK uses approach/contact base and K_TRACK_PER_DEG times bearing limited to
min(TURN_MIN_DUTY,base), with the ATTACK governor.
Consequence: test every front row, mirrors, invalid inputs, approach/contact,
final low-voltage caps, target-loss braking and centered qualification in the FSM.
This is an approved development policy, not measured steering performance.

## D-037 (2026-09-22, accepted) Timed re-flank arc and initial tie direction
Context: SC-W left B11 SWING duty and initial alternation unspecified. User
replied "Approve A: timed re-flank arc and right-first tie".
Decision: outer arc request TURN_DUTY (0.80), REFLANK_ARC_RATIO (0.40), and a
duration-only REFLANK_ARC_MS (400 ms) limit. When the specified edge/side-history
rules cannot choose, swing right first, then alternate.
Consequence: implement a time-only arc without inventing a sweep cutoff; test
duration boundaries, side precedence/ties, charger skip, both mirrors and safety.
The existing recent-edge and least-recent-front-side rules retain precedence.

## D-038 (2026-09-22, accepted) Qualified re-flank reacquisition
Context: SC-X left re-flank's ATTACK exit inconsistent with B9 qualification.
User replied "Approve A: qualified re-flank reacquisition".
Decision: re-flank exits use normal current-perception arbitration: current
front selects TRACK and must satisfy ATTACK_ENTER_TICKS centered observations
before ATTACK; side/rear selects DEFEND_TURN; none selects SEARCH. Preserve
D-027's fresh contact requirement.
Consequence: test qualification interruption, stale contact, every target group,
target loss and edge priority in the integrated Robot; no direct ATTACK bypass.

## D-039 (2026-09-22, accepted) One specific locked-test amendment for D-035
Context: the established case "B3 Controller qualified MODE cancels at GO deadline
and requires a new hold" in tests/locked/test_countdown_integration.cpp holds BOTH
for 5.1 s yet expects IDLE/restart without reset, contradicting accepted D-035.
User reviewed the concrete proposal in analysis/P1_stop_locked_conflict.md and
replied "Approve the single-case locked-test amendment".
Decision: apply exactly that documented replacement to this case only. Preserve
MODE cancellation and all initial cancellation/full-countdown checks. The BOTH
branch must instead assert latched STOPPED, reject release/START and explicitly
reset before the existing fresh full-hold checks.
Consequence: no other established locked test is authorized to change. Preserve
the initial failing receipt; rerun full host/sanitizer suites and separate review.
This approval synchronizes an old expectation with D-035, not weaker protection.

## D-040 (2026-09-22, accepted) Bounded re-flank completion
Context: SC-Y left natural arc expiry and TURN_IN continuation undefined.
User replied "Approve A: bounded re-flank completion".
Decision: arc completion without an inner-sensor trigger exits through D-038
current perception. TURN_IN retains its captured turn until front detection,
completion or timeout, then uses D-038. Edge and STOP preempt every phase.
Consequence: test natural/triggered exits, captured target, exact timing, timeout
and safety priority. Approval is recorded; implementation remains pending.

## D-041 (2026-09-22, accepted) Latest selected bearing side for SEARCH
Context: SC-Z left last-seen side ambiguous. User replied "Approve A: latest
bearing side for search".
Decision: use the sign of the latest valid nonzero selected relative bearing;
zero retains the previous side; no known side defaults right. The explicit
SIDESTEP scan hint still controls its first scan.
Consequence: test front/side/rear priority, zero/invalid bearings, initial default,
hint precedence and mirrors. This decision governs SEARCH side selection.

## D-042 (2026-09-22, accepted) Bounded full-scan fallback
Context: SC-AA left B8's full360-degree scan fallback unspecified.
User replied "Approve A: bounded scan fallback".
Decision: use directed yaw progress while IMU-valid. On loss, latch one timed
fallback for the last known remaining sweep clamped to0..360 degrees at
TURN_MS_PER_DEG, beginning at that loss observation. Recovery never restarts it.
Without IMU at scan entry, time the whole360 degrees. Do not inherit the short
turn's700ms cutoff or manufacture fresh heading observations.
Consequence: test initial/mid-scan loss, remaining/opposite progress, recovery,
exact fallback deadlines and wrap. Physical scan behavior remains unvalidated.

## D-043 (2026-09-22, accepted) Unseen front side is least recent
Context: SC-AB left unseen-versus-seen front recency unordered.
User replied "Approve A: unseen side is least recent".
Decision: one unseen side is less recent than a seen side. Both unseen or equal
recency fall through to the approved right-first alternation. Existing higher
priority recent-edge side selection remains in force.
Consequence: test both asymmetric histories, both unseen, equal/older histories,
alternation and recent-edge precedence; no new edge-direction mapping is implied.

## D-044 (2026-09-22, accepted) Head-on brake interval and reverse request
Context: SC-AC left B4.2 head-on brake duration/reverse duty undefined.
User replied "Approve A: one-tick head-on brake and existing reverse duty".
Decision: brake for one complete TICK_US, reverse EDGE_BACK_LONG_MS at
EDGE_BACK_DUTY, preserve the specified160-degree pivot and governor rules.
Consequence: test exact/adjacent times, delayed transitions, mirrors and low
voltage. Last-opponent-side selection and other escape ambiguities stay separate;
no established locked-test amendment is authorized by this decision.

## D-045 (2026-09-22, accepted) Count the current entry observation
Context: SC-AD left the normal TRACK-entry qualification anchor unstated.
User replied "Approve A: count the current entry observation".
Decision: count the current centered observation entering TRACK from a script as
the first required observation; discard qualification from before exit/preemption.
ATTACK still requires three actual consecutive centered observations by default.
Consequence: test entry/second/third samples, interruptions and opener/re-flank
reacquisition. Standalone FrontQualification already supplies the counter; actual
state-entry/reset integration remains to implement.

## D-046 (2026-09-22, accepted) Brake then route by current perception
Context: SC-AE conflicted front-loss SEARCH with current side/rear DEFEND_TURN.
User replied "Approve A: brake then route by current perception".
Decision: brake to zero immediately on front-target loss; select DEFEND_TURN for
a current side/rear target, SEARCH for none. The new state's motion begins no
earlier than the next tick. Edge/STOP and contact requirements remain intact.
Consequence: test residual masks, TRACK/ATTACK loss from existing duty, loss-tick
zero and next-tick demand, fresh contact and safety preemption. No motor run or
phase gate is authorized.

## D-047 (2026-09-22, accepted) Shared opponent-side history for head-on escape
Context: SC-AF left B4.2's last-seen-opponent side ambiguous after D-044.
User replied "Approve A: shared opponent-side history".
Decision: reuse D-041's latest valid nonzero selected relative-bearing sign;
zero retains the side, and no known history defaults RIGHT. Use this history
when selecting the head-on escape pivot direction.
Consequence: test front/side/rear changes, zero/unknown/conflicted observations,
default/reset and mirrored head-on selection. Approval is not hardware evidence.

## D-048 (2026-09-22, accepted) Inhibited recovery for three-white or exhausted replans
Context: SC-R lacked an approved wheel-command mapping toward black for three
white sensors or exhausted replans. User replied "Approve A: inhibited recovery fault".
Decision: in either case latch an escape fault with zero duties and motors
disabled until reset. This explicitly replaces the unspecified recovery movement;
the existing all-white priority and reset-only inhibition remain intact.
Consequence: test all four three-white masks, the exact replan-limit boundary,
all-white priority, persistence after black, reset and zero final duties. A stopped
robot can sacrifice a match; physical validation is still pending. Existing locked
tests may not be amended without a separately explicit approved amendment.

## D-049 (2026-09-22, accepted) Pushed-out priority and direction
Context: SC-S lacked a both-rear direction and a precise forward-duty predicate.
User replied "Approve A: pushed-out priority and direction".
Decision: all-white/three-white faults take priority. Otherwise current centered
front plus both previously applied final wheel duties strictly above zero
qualifies. One white rear side pivots45 degrees away; both rear sides pivot
opposite the shared opponent-side history (default LEFT), then use the specified
forward segment. Ordinary B4.2 rows follow this higher-priority pushed-out check.
Consequence: cover all16 masks, centering, duty-sign/zero boundaries, mirrors,
fault priority and governed phase limits. Physical validation remains pending.

## D-050 (2026-09-22, accepted) Bounded replanning lifecycle
Context: B4.4 left non-pivot triggers, completed-but-white and exhaustion unclear.
User replied "Approve A: bounded replanning lifecycle".
Decision: during PIVOT, replan for newly white bits on its turning side. During
other active phases, any newly white bit requests replacement. Finished script
with persistent white also requests replacement. At most one replacement per
fresh observation. Initial entry uses zero budget; allow three replacement
starts, then latch the D-048 inhibited fault on the fourth request. Reset budget
only after actual escape exit or reset. Fault masks always take priority.
Consequence: exact third/fourth boundaries, simultaneous bits, phase-deadline
ties, persistent white, black-before-completion and reset tests are required.

## D-051 (2026-09-22, accepted) Delegated engineering choices without more questions
Context: user instructed "for any questions do not go back to me, you choose
the best course and recommedned choices" while P1 host work was continuing.
Decision: Codex selects the recommended engineering course for remaining design
questions and records each material choice, reasoning, limits and regression
requirements without requesting another decision. This supersedes mandatory
return-to-human questioning for those delegated choices in the project workflow.
Consequence: keep decisions explicit and specifications visibly amended. This
instruction is not evidence of physical testing, a written phase-gate pass, or a
specific identified motor run. Preserve established locked tests where possible;
do not fabricate human measurements, approvals or reviewer output. Unknown
hardware/API facts remain unknown until verified; continue feasible host work.

## D-052 (2026-09-22, accepted) Bare UNO Q testing scope
Context: user reports UNO Q connected with nothing else, authorizes testing it,
and requests no additional hardware connections. User supplied a Windows CLI
and permits WSL/tools if needed. USB inventory identifies explicit ADB serial
2629958581; existing ADB suffices. No credentials are recorded or required.
Decision: execute eligible inert P0 board inventory/build/upload/measurement
tasks using the existing board-side toolchain and documented USB ADB fallback.
Keep MOTORS_ALLOWED=0 and reviewed-source restrictions. Preserve default SSH
workflow and strict host-key checking; no arbitrary LAN probing or new key setup.
Consequence: attachment/isolation is human-reported; installed/tool/runtime facts
need their own evidence. Do not request sensors/drivers/motors now or infer
PINMAP OK, STAND/RING authorization, physical rule compliance or a phase gate.

## D-053 (2026-09-22, selected under D-051) Frozen RAM timing readout
Context: P0 needs bare-board scheduler measurements; current RouterBridge Monitor
has unresolved blocking/allocation behavior. Installed core's required Bridge
library does not justify using Monitor in the measurement loop. A reviewed
MEM-AP-only debug connection can read completed RAM without reset/halt/MCU writes.
Decision: retain the existing RAM-only60000-sample diagnostic. Let it finish before
attachment, verify exact loader/sketch bytes, resolve final-ELF BSS symbols from
the verified loader's bounded LLEXT list, and validate two identical complete
snapshots before reporting max/p99. Include installed loop-hook overhead.
Consequence: no R3/R4 exception or invented log round trip. P0's Monitor counter
and physical cold-boot/display checks remain distinct pending evidence. No GPIO,
voltage, wiring, core behavior or config default changes. Incomplete/inconsistent
reads fail, and an attachment during capture invalidates the unperturbed result.

## D-054 (2026-09-22, selected under D-051) Full Escape observation lifecycle
Context: D-047..D-050 settle selection/replan policy; the wrapper still needs
precise boundary, cancellation and inward-evidence semantics. Separate spec/header
audits agree on the following recommendations, recorded without another question.
Decision: newly-white replanning uses the phase and intended pivot side present
at call entry, independent of overshoot correction sign. Then independently
check completed-but-white after row advancement; at most one replacement per
fresh observation. Keep the prior mask across replacements and update on clears.
Losing motion permission during an active episode latches an inhibited reset-only
fault; never count disabled time as completed physical escape or clear its budget.
Publish inward heading only on actual all-black+DONE exit with current healthy
finite yaw. Unavailable yaw produces no new inward evidence; cached heading is
only a motion coordinate. Validate numeric/enum context only when consumed, after
gate/fault-pattern priority. Invalid consumed context latches an inhibited fault.
Consequence: this can stop a match on invalid data/permission loss. Test phase
deadline ties, overshoot, clear/reassertion, all16 masks, exact replan limit,
permission recovery/reset, context selection, unavailable yaw and inward pulses.
No sensor timing, pin, B16 value, established locked test or phase gate changes.

## D-055 (2026-09-22, selected under D-051) WAIT approach and complete sidestep
Context: SC-G conflicts PLAN6.2's evasive intent with O4's no-pivot straight
segment; the widening front cue could abort that segment immediately. The saved
spec-only P1_wait_contract_audit.md recommends the complete existing SIDESTEP_R.
Decision: an ordered widening cue starts the full SIDESTEP_R, including its
initial pivot, with unchanged gains/durations and D-033/D-034 exits. This explicitly
supersedes O4's skip-pivot text. HOLD brakes; FC must stay continuously confirmed,
then a flank newly rises on a later fresh observation within inclusive300ms.
Initial simultaneous FC+flank is not ordered; a held FC never refreshes/rearms an
expired window; FC clear rearms. Current side/rear abort outranks cue, cue outranks
WAIT expiry. Both flank cues select RIGHT. No snapshot/contact substitutes for cue.
Consequence: extra pivot latency and actual evasive geometry need later physical
validation. Do not suppress the existing front exit when the pivot finishes.
Test cue ordering/interruption, exact window/deadline ties, persistent FC, wrap,
flank delegation, stationary braking and normal qualified reacquisition. No B16
value, pin, established locked test, motor permission or phase gate changes.

## D-056 (2026-09-23, selected under D-051) Single contact commit and governor pass
Context: the full Robot needs current ATTACK contact to decide stall/re-flank,
but Fusion must commit exactly once to the final selected state; running the
governor speculatively would advance filtering/slew twice. Public-header audit:
analysis/P1_robot_interface_audit.md, item1/2.
Decision: add a read-only Contact/Fusion candidate preview. Robot previews current
candidate ATTACK contact for stall arbitration, then commits once to final state;
only the final commit may supply contact permission/events. Stall and pushed-out
selection use explicitly identified preceding applied final electrical duties,
with zero feedback for hardware inhibition. Run Governor once after arbitration.
Consequence: no provisional contact can survive a re-flank/edge exit or authorize
full duty. Qualification starts from actual reported applied-duty evidence, not a
speculative command; app/MotorGate feedback ownership must be explicit in Robot's
future interface. Test preview purity/alternative states, invalid pending state,
cue counters, skipped commit, final re-flank clear and retained real contact.
No existing commit semantics, locked tests, tuning values or physical claims change.

## D-057 (2026-09-23, selected under D-051) Route service START without match start
Context: B13 service START must not start the match countdown. Existing Controller/
Lifecycle privately sample Buttons and expose only Gate's accepted release, so a
menu cannot safely suppress a match start or reuse its qualified event afterward.
Spec/header-only audit: analysis/P1_mode_menu_contract_audit.md, section3.
Decision: add an allow_match_start argument, default true, filtering only the
qualified release command passed to Gate. Continue all debounce, STOP, MODE and
timer processing. Expose the latest qualified ButtonEvents as a read-only snapshot
on Controller/Lifecycle; preserve Result.start_release as accepted match start.
A suppressed release is consumed with no deferred replay. The selector is not
an inhibit and cannot revoke an already-started countdown/READY. Service requests
must separately obey final IDLE/fault/STOP policy and never grant motor permission.
Consequence: default behavior and established locked tests stay unchanged.
Test suppressed release/re-enable/fresh press, exact hold, cancel/STOP priority,
snapshot purity/reset, service non-start with invalid previous bias, active service
continuation, wrapped/delayed observations and default-argument equivalence.
No menu policy, hardware decoding, config value, phase gate or motor-run change.

## D-058 (2026-09-23, selected under D-051) Logical mode and service menu gestures
Context: B13 gives six match modes, four services, short MODE under600ms and long
MODE1000ms, but leaves duration anchors, intermediate holds and gesture recovery
undefined. P1_mode_menu_contract_audit.md recommends explicit conservative input
semantics; D-057 already provides qualified service START routing.
Decision: implement a pure countdown::Menu. Only IDLE-at-entry with no final
STOP/fault inhibition admits actions. Require qualified NONE after boot/reset or
contamination, then qualified exclusive MODE; anchor hold at actual qualification.
First NONE freezes hold and wins a tied long deadline. Qualified release cycles
only if age<600ms; a [600,1000)ms hold is a no-op. Continuous MODE at>=1000ms
toggles services once, with no subsequent short action. Interrupted release,
START/BOTH/invalid input or leaving IDLE cancels gestures and requires rearming.
Cycle six match modes/four service items in documented order. Service entry
selects SENSOR_VIEW; exit retains match mode. Reset selects MODE_DEFAULT; expose
no arbitrary selection setter. Centralize existing600ms as MODE_SHORT_MS only.
Use D-057's genuine qualified START pulse for a one-call typed service request,
only with current NONE/services/IDLE/no inhibition; that call starts fresh NONE
arming. DRIVE_TEST request is explicitly unavailable in P1. Other requests need
real bounded consumers and do not certify hardware availability. Duplicate time
returns selection with pulses cleared and ignores changed input. Saturating ages
prevent repeat actions across timer wraps. Match mode snapshots at accepted match
START are owned by the future Robot; no service response grants motor permission.
Consequence: some noisy/medium/late-release gestures do nothing and can be retried.
Record exact boundaries, cancellation/STOP/state transitions, reset/boot mixtures,
all selections, service routing/no countdown, duplicate/wrapped/delayed streams
and finite bounded outputs in independent tests. No ADC/pins/B16 value/motor-run
or phase-gate change; physical service execution and complete Robot remain open.

## D-059 (2026-09-23, selected under D-051) Logical match origin and continuous yaw
Context: B3 GO zeroing can fabricate a >360-degree StuckFilter span or invalidate
same-tick captured references if applied to Fusion/HAL. Resetting Fusion would
clear reset-only safety state. Audit: P1_robot_heading_contract_audit.md.
Decision: preserve continuous raw integrated yaw for Fusion for the Robot lifetime.
Establish a separate match origin atomically at actual GO, after cancellation/STOP
arbitration and before moving entry. Capture current healthy finite yaw, else the
last genuine healthy sample, else nominal local0 with pending origin/imu=false.
The latter preserves missing-at-boot B14 fallback. First healthy recovery anchors
that pending origin at the nominal coordinate, without replacing script references,
replaying GO or extending deadlines. Later losses retain the fixed origin/local yaw.
heading_reset_requested means this logical operation, never a HAL integrator reset.
Calibration affects later integration increments only. Retain raw world/inward
evidence and actual timestamps; project views without resampling or refreshing age.
Use double subtraction, check float representability, reduce directional angles
before adding small bearings or narrowing; current world views retain the checked
double difference even when the published float match heading rounds it.
Exact directional antipode ties select+180; a negative non-tie rounding to-180
uses the nearest interior negative float so rounding cannot reverse its side.
Continuous headings stay unwrapped. Expose origin
source/time; pending source time is GO, not a claimed measurement.
Healthy nonfinite yaw (even pre-GO), nonrepresentable match difference or repeated
GO without reset latches an inhibited coordinate fault until reset. Ordinary IMU
absence is not a fault. Immediate duplicate time ignores changed input and clears
pulses. Invalid read-only projections return invalid/finite0 without mutation;
future Robot must honor both source validity and projection validity.
Consequence: malformed healthy data can stop a match; missing data still uses
the specified bounded fallback. Test raw-Fusion continuity across GO, missing
history/last-known recovery, unchanged motion deadlines/references, sticky faults,
extreme finite coordinates, angle ties, duplicates/wrap and truthful provenance.
This contract does not prove provider continuity, physical yaw, full Robot wiring
or complete-loop WCET. No pins/config/locked tests/phase or motor authority change.

## D-060 (2026-09-23, selected under D-051) Production Robot transaction and evidence
Context: all P1 behavior components now exist, but their ordering, input ownership,
actual-duty feedback and event/frame lifecycle are not yet a production Robot.
Public-only proposals: P1_robot_api_proposal.md and P1_robot_event_contract_audit.md.
Decision: adopt the concrete contract in P1_robot_contract.md with public APIs in
fsm.h/logframe.h. One fresh raw sensor observation, one final Fusion commitment
and one Governor pass. Preserve original gate/edge/script/centering/contact rules,
D-059 raw/match coordinates and missing-IMU fallback. Invalid required/stale input
stops immediately; process STOP while canceling services before stale sampling.
Applied receipts require exact prior identity/time, permission, finite duties and
requested direction/magnitude (PWM quantization toward zero). Missing application
faults; missing/invalid duration only marks timing incomplete. Matched complete-
tick duration must agree with its start/completion timestamps, not loop intervals.
Use bounded token/history/event/frame state, explicit metadata and21-event capacity
with separate loss counters; PHANTOM_SET uses match-world projection. Preserve
last-match recorder evidence through reset; frames use actual matched application,
not requests. Stop recording at cancellation, STOPPED or inhibited Escape fault;
include the final stopping tick in match timing if GO occurred. QTR warning uses
actual reported opposite-sign duties and continuous white strictly beyond its
existing duration; warning never changes edge behavior. Contract file records
remaining exact boundaries, duplicate/reset semantics and invalid-state recovery.
Consequence: stale or unverified actuator feedback can stop the match; timing or
logging incompleteness alone cannot. These are explicit software integration
choices, not measured acquisition, motor or timing facts. Test the actual Robot,
not another test-only arbiter. Do not modify existing locked cases. No additional
hardware request, phase gate, wiring, motor-run or configuration-value change.

## D-061 (2026-09-23, selected under D-051) Bounded ambiguous DEFEND entry
Context: the first production Robot runtime suite passed875/876 cases; seven
assertions in10000-stream R1/R5 scenarios expected no contract fault for legitimate
D-026 unknown bearing. Both-side conflict without prior bearing instead reached
DefendTurn's required-bearing start and safely inhibited with SCRIPT_START.
This exposes an ambiguity-policy/test-expectation gap, not unsafe motor behavior.
Decision: adopt P1_ambiguous_defend_contract.md before dependent code/new tests.
Robot waits at governed zero for up to existing DEFEND_TIMEOUT_MS when entering
DEFEND without a usable bearing. Later real capture cannot extend that interval;
front/clear and edge/STOP preserve priority. Expiry uses existing SEARCH routing.
Keep DefendTurn's strict public API and all other invalid-context faults intact.
Consequence: conflicting detections can cost800ms but cannot invent a turn or
permanently fault merely from valid unknown information. Preserve the original
failure/trace and unchanged locked property; add independent exact/wrap/preemption
regressions. No B16 values, wiring, physical acceptance, gate or motor authority
changes. This is an explicit delegated behavior choice, not a hidden test repair.

## D-062 (2026-09-23, selected under D-051) P0 bounded counter transport
Context: installed Monitor/Bridge/RPClite/ZephyrSerial can allocate or wait without
a total deadline. The installed loader disables asynchronous UART. Source proves
the existing router accepts a fixed mon/write notification without a reset RPC.
Decision: adopt P0_counter_transport_contract.md before code/tests. Implement one
fixed notification slot, explicit busy refusal and terminal partial-send fault.
Investigate a sole-owned transmit-only IRQ adapter for the existing internal UART,
without starting Bridge/Serial2 or changing pins, loader, dependencies or R3/R4.
Require installed-driver/ownership proof, independent review and exact inert
source manifest before any D-052 upload. Preserve the Immediate matrix prohibition.
Consequence: notifications may be lost without acknowledgment; diagnostics report
that limitation rather than treating transmission as delivered evidence. If driver
bounds cannot be justified, retain the tested packet primitive and explicit blocker.
No P2 implementation, human gate, wiring, B16 tuning or motor authority is granted.

## D-063 (2026-09-23, selected under D-051) P0 startup-only ADC timing
Context: P0 0.4 requests bare-board analogRead timing before pin-map acceptance.
Installed ADC1/A0 is PA4/channel9/index14, but stock analogRead waits indefinitely
for ownership/completion even after warmup; ADC async/stream/DMA are disabled.
Decision: adopt P0_adc_contract.md before implementation/tests. Run1000 A0 calls
only in setup of a new inert diagnostic, preserve first-use/subsequent costs,
paired micros overhead and raw returns in frozen RAM. Empty loop; no Bridge,
matrix, GPIO output or motor writes. Passive hash-pinned readout only after the
measurement, with a fresh source/binary review and default-only upload allowlist.
Consequence: startup can hang; incomplete records and negative setup/read errors
fail explicitly. Zero is valid raw data. No timeout wrapper, production ADC solution,
accuracy, robot pin-map, phase gate or physical WCET acceptance is inferred.

## D-064 (2026-09-23, selected under D-051) P0 internal LED GPIO timing
Context: P0 0.4 requests GPIO API timing. Installed F-080 maps the builtin LED
to PH10/index50, with finite native GPIO paths and no active competing loader
owner after setup. Arduino wrappers mask errors; initial LED level is unknown.
Decision: adopt P0_gpio_contract.md before implementation/tests. Check GPIOH
readiness, then400 setup-only timing samples for pinMode, digitalWrite, reads
and the contiguous configure/write pair, keeping signed readbacks and clock
overhead. Stop on mismatch, finish HIGH/off, freeze results and use reviewed
passive capture. Default-only, MOTORS_ALLOWED0; no header or motor pins.
Consequence: readbacks cannot recover discarded native errors or prove optical
behavior. Finite instruction paths and measured maxima do not prove robot WCET.
No wiring assumption change, B16 tuning, PINMAP approval or phase gate follows.

## D-065 (2026-09-23, selected under D-051) P0 bare-board QTR-style timing
Context: P0 0.4 requests four-pin charge/timeout timing without attached sensors.
F-082 verifies installed GPIOA/B mappings and finite API paths; floating neutral
inputs cannot guarantee a timeout, and delayMicroseconds(10) requests only9us.
Decision: adopt P0_qtr_contract.md and qtr_capture.h before code/tests. Collect
100 neutral and100 distinctly labeled diagnostic pull-up acquisitions on the
specified D2/D4/D7/D8, with measured11us charge guard, actual four-read passes,
full1500us observation window, finite4096 guards and no-pull INPUT cleanup.
Preserve raw late/early LOW observations and failure records; no synthetic HIGH
or substituted timeout. Default-only inert setup, exact reviewed passive readout.
Consequence: stimulated success proves sampled bare-pad timeout-path timing only.
No sensor discharge/freshness, physical cleanup, PINMAP, wiring/B16 change or R4
acceptance follows. SC-B and all human gates remain open. Independent tests,
source/binary review and exact inert manifests are required before any upload.

## D-066 (2026-09-23, selected under D-051) P0 MPU6050 compile-only compatibility
Context: G6 source candidates are pinned, but installed UNO Q compilation and
Wire1/link compatibility remain unverified. Missing sensor prevents measurements,
not compilation. Installed Wire/native waits and library fault handling preclude
assuming these dependencies are suitable for the production1kHz control loop.
Decision: adopt P0_imu_compile_contract.md. Install only absent exact pinned
MPU6050/BusIO/Unified Sensor dependencies with provenance and --no-deps; preserve
existing versions. Compile a retained never-called API probe whose setup only
stores its function and Wire1 addresses. Explicitly omit unused display libraries.
Consequence: this records compatibility only, not runtime validity. No upload
allowlist entry, I2C execution, wiring/config value, upstream patch, P2 HAL, sensor
claim or human gate. Preserve source/ELF/review/test evidence and every failure.

## D-067 (2026-09-23, selected under D-051) P0 PWM/interrupt compile-only probes
Context: G2 source candidates still need installed header/link verification.
Native PWM device dispatch and Arduino interrupt wrappers have distinct error,
ownership and export limitations; successful compilation alone cannot clear them.
Decision: adopt P0_pwm_irq_compile_contract.md and its public api_probe.h before
implementation and independent tests. Retain never-called native PWM, Arduino
analogWrite and attach/detach API probes; setup stores only function addresses.
Consequence: no probe execution, upload allowlist entry, pin selection, frequency
adoption, asynchronous QTR semantics, upstream change, P2 HAL or motor authority.
Preserve actual installed source, compile, ELF, test and fresh review evidence;
unmeasured electrical/timing behavior and genuine phase/human gates remain open.


## D-068 (2026-09-23, selected under D-051) Narrow offline B8 preparation on resume
Context: after the saved blocked checkpoint, the user resumed "cotinue working".
The existing direction defers physical testing and delegates recommended engineering
choices without questions. P2 permits early individual drivers and reserves GATE P1
for integration; fixed RAM storage needs no external part. A separate read-only
scope audit identified an overly broad stop on this offline preparation.
Decision: as a coordinator interpretation of those instructions, select a narrow
scheduling exception for offline P2 B8 RAM storage components and independent host
tests. Supersede only D-016's scheduling exclusion for this specified track.
Do not characterize the latest short resume as an explicit human P2 approval.
Consequence: P0/P1 remain HARDWARE/GATE-PENDING. No integration, Bridge runtime
transport, upload, new hardware request, pins/wiring, motor authority, measured
RAM or B8/P2 acceptance. Record contracts and independent reviews; retain actual
failures. This is software preparation under delegated choice, not a phase pass.

## D-069 (2026-09-23, selected under D-051) Latest-frame ring with explicit evidence loss
Context: B15 specifies a200-second frame capacity but no frame eviction policy;
D-028's first4096 rule is specifically for events. Core supplies25-byte encoded
frames with separate PackStatus and already owns cadence/actual-duty matching.
Decision: adopt P2_frame_buffer_contract.md and recorder_frames.h. Fixed latest-
frame ring, exact bytes plus status, saturating overwrite/unknown-status/CLAMPED/
INVALID counters and explicit local incomplete flag. Logical reset is constant
work and remains a future accepted-attempt owner's responsibility. Capacity is
ceil(200000ms*LOG_HZ/1000)+1 to retain initial/final endpoints.
Consequence: overwritten or degraded data never appears gap-free. Keep all B16
values, notably LOG_HZ50. Required frame/event payload292794B exceeds installed
262144B pool; deployment remains blocked pending explicit memory/cadence work,
not a claimed fit. No lifecycle integration, event-ring duplication, transport,
physical measurement, hardware approval or phase gate. Independent boundary,
wrap, reset, status, alias-source and oracle tests precede fresh review.


## D-070 (2026-09-23, selected under D-051) Offline attempt evidence ownership
Context: D-069 payload storage is verified, but a delayed prior receipt can share
a result with a new START and core reset must preserve last-match evidence.
Decision: adopt P2_attempt_recorder_contract.md/recorder.h for an offline fixed
owner: accepted-START epoch validation, prefix/frame exclusion, bounded ingestion,
one final flush, explicit reset interruption, monotonic tokens and explicit
exhaustion envelope. Preserve distinct loss counters and core snapshots.
Consequence: no generic erase, phantom final frame or silent loss; no new cadence,
app/transport integration, hardware instance or gate. Keep SC-AH RAM deployment
blocker/B16 defaults. Independent contract-derived tests and fresh review remain
required before declaring this software component complete.

## D-071 (2026-09-23, selected under D-051) Isolated B8 target-memory candidates
Context: default50Hz frame/event payload alone exceeds the installed extension
pool; B15 permits25Hz when RAM is short but target owner/code costs are unknown.
Decision: adopt P2_memory_compile_contract.md and memory_probe.h before code and
independent tests. Prepare isolated50Hz baseline and25Hz fallback source trees,
retaining actual single Robot/AttemptRecorder owners and never-called paths for
compile-only ABI/section/constructor evidence. Supersede D-070's hardware-instance
exclusion only for this bench; keep production cadence/config/app unchanged.
Consequence: no firmware execution, upload allowlist expansion, transport runtime,
loader change or gate. A size-check failure remains failure; candidate fit is not
free-RAM, loadability,200s/no-gap recording or WCET proof. Preserve source hashes,
failures, independent candidate/locked tests and separate fresh-context review.

## D-072 (2026-09-23, selected under D-051) Adopt specified25Hz recorder fallback
Context: D-071 proves actual50Hz owner image exceeds installedRAM356608/262144B;
the specified B15 fallback25Hz compiles226584B with reviewed source/ELF and245
candidate/locked regressions. Full firmware/load/free-RAM/physical acceptance is
still absent; this evidence supports a development default, not deployment.
Decision: adopt P2_rate_adoption_contract.md. Set LOG_HZ25 with visible B15/B16
provenance,5001frame capacity/40ms cadence; preserve200s window,4096events and all
motion/sensor/control timing. Supersede only D-069/070/071's production50 retention.
Update independent unlocked rate/capacity expectations without removing assertions;
retain every locked file and full fixed-seed requirements. Keep25/50 compile
experiments reproducible from either supported source rate, always compile-only.
Consequence: one evidenced B16 value changes; other75 remain. No app/transport
integration, runtime/loader workaround, physical tuning, upload authority or gate.
Independent tests/review and exact source-guard review precede completion claims;
SC-AH deployment and SC-I platform/runtime issues remain explicit.


## D-073 (2026-09-23, selected under D-051) Offline B8 CSV evidence formatting
Context: verified RAM owners expose exact bytes and loss metadata but B8 has no
serializer; dump_match.sh/transport remain absent. An independent read-only audit
identifies pure formatting as eligible software preparation, not integration.
Decision: adopt P2_csv_contract.md and recorder_csv.h before independent code/tests.
Extend D-068 only to bounded stateless offline CSV headers/rows/metadata snapshot;
preserve raw bytes, signed scaled wire integers, statuses and every loss field.
Consequence: no transport/cursor/app integration or live dump authorization.
SEALED does not prove IDLE and incomplete=false does not prove completion.
No config/locked/behavior value changes, upload, physical claim or human gate.
Independent tests/fresh review and exact existing inert-guard review required.


## D-074 (2026-09-23, selected under D-051) Local CSV evidence validation
Context: D073 formats exact rows but does not verify stored file integrity,
owner-summary consistency or supplied provenance. Hardware and runtime dump
requirements remain unfulfilled. A separate public-contract audit identified
raw codes/ordinals, lifetime counts and phase/loss distinctions to preserve.
Decision: adopt P2_csv_bundle_contract.md before separate implementation/tests.
Extend offline B8 preparation only to one read-only local-file Python validator
with bounded input, exact raw/schema checks, separate consistency/loss/lifecycle
reports and optional explicit caller-declared hash/provenance metadata.
Consequence: no firmware/config/locked-test/transport/app change or fabricated
physical/common-attempt/closure proof. Valid files are not B8 acceptance.
Independent synthetic fixtures, actual host formatter roundtrip, full relevant
tooling checks and fresh read-only review are required. No board action/gate.

## D-075 (2026-09-23, user-directed) Resume P2 software before physical acceptance
Context: user explicitly says hardware has not been checked, prioritizes software
speed, requests development using working-hardware assumptions and reports board
connected. This changes the previous no-eligible-work scheduling checkpoint.
Decision: permit P2 HAL software preparation and host/compile-only verification
before P0/P1 human acceptance, beginning B4 MotorGate per P2_motor_gate_contract.md.
This supersedes D016/D068-D074 scheduling exclusions for this development, not
their evidence limitations. Select conservative checked-port/fault policies under
D051. Real integration/deployment must retain unresolved electrical/API blockers.
Consequence: no invented EXPLAINED/PINMAP/GATE record, no physical success, wiring
change, motor-capable upload/run or relaxed test. Existing gates remain pending.
Implement actual bounded modules, independent tests and fresh read-only review;
do not spend this authorization on further bookkeeping-only tasks.

## D-076 (2026-09-23, selected under D-051/D-075) Checked native opponent GPIO
Context: P2 B1 lacks a HAL; installed digitalRead converts GPIO errors to LOW,
which can masquerade as active-low detection. Physical sensors remain untested.
Decision: adopt P2_opponent_contract.md and opp_sensors.h before independent code/
tests. Use checked native configure/raw-read status, bounded seven-channel scans,
explicit invalid snapshots and original raw polarity into core. Copy HARDWARE3's
unchanged proposed indices into config::OPP_INPUT_PINS; no B16/default tuning.
Consequence: actual native driver can be host-tested through API substitutes and
target-compiled without executing it. This is not PINMAP approval or a new wire
assignment. No fake success, double debounce/polarity, upload, physical B1 result
or human gate. Preserve original tests and review five inert source guards.

## D-077 (2026-09-23, selected under D-051/D-075) Native MotorGate backend
Context: checked Gate exists but lacks native callbacks; installed PWM writes
update preloads, so successful setters alone do not authorize EN HIGH. Retrieved
RM0456 and current ES0499 plus installed clock/register audits support a bounded
fresh-update check for the specified TIM1/3/4 modes and exclusive ownership.
Decision: adopt P2_motor_native_contract.md and motor_port_unoq.h. Name unchanged
proposed D3/D5/D6/D9 and D10 pins in config. Select development10kHz carrier,
150us whole-settle deadline and4096-pass guard (explicit count-name exception),
all new constants, no B16 change. Clarify only D075's construction prerequisite:
source-derived immutable period candidates may be copied before begin, then
validated by native setup after EN LOW and before any admitted duty write. Do not
mutate periods or describe cached cycle metadata as measured physical frequency.
Consequence: only MotorGate invokes the bounded checked backend; native setup
failures/ownership mismatch or missing fresh updates fail closed. Preserve old
locked tests; add independently authored native safety tests, real target builds
and separate fresh review. No app integration, upload/run, wiring change, physical
waveform/WCET/PINMAP or human gate follows. All candidate timing needs later proof.


## D-078 (2026-09-23, selected under D-051/D-075) Bounded native battery ADC
Context: stock ADC calls have unbounded waits (F078); current installed-source,
RM0456, DS13086 and ES0499 checks support a concrete private ADC1/A0 candidate.
Decision: adopt P2_power_contract.md/power.h, ordinary14-bit channel9 calibration,
814-cycle sampling with required LFTRIG1, one fresh synchronous native conversion,
explicit validity/status/timestamps and reset-only fault lifecycle. Preserve the
unchanged A0/100k/22k proposal; nominal3.3V/122:22 scaling is not measured accuracy.
New setup deadlines100/5000/2-minimum/100us, runtime100us and separate total100us
fault cleanup; setup65536/runtime4096 poll guards (count-name exceptions).
No stale voltage, second B6 filter, stock ADC call, peripheral reset or blind
cleanup after ownership loss. No B16 value changes or wiring authorization.
Consequence: independent native-source tests and inert target compilation/fresh
review are required. Preserve actual stock MSIS auto-calibration configuration;
its ES0499 2.2.27 unlock/accuracy issue is a separate GLOBAL runtime integration
blocker. Readiness/metadata is not a lock/frequency measurement. Do not turn off
shared clocks, invent a lock predicate or claim this resolves deployed runtime.
Physical B5 accuracy, supply/reference/pin verification, tick WCET and all human
gates remain pending. Only software/compile-only work is authorized here.


D078 source-review clarifications (2026-09-23): ADC clock enable is bounded
admission preparation before meaningful register reads; it alone does not claim
ownership or justify rollback. After pristine admission, a process/boot-lifetime
claim latch prevents retry by a new Reader even if the first configuration write
was ignored. No release/reset hook is introduced. Also require the documented
EPOD BOOSTEN/BOOSTRDY and stock PLL1MBOOST DIV1 at160MHz (RM10.5.4 pp410–411),
distinct from the analog-switch booster. These are read-only operating guards;
no source/timing default or shared clock/power setting changes. Targeted tests
preserve actual readiness-loss and ignored-write draft failures before repair.


## D-079 (2026-09-23, selected under D-051/D-075) Bounded native MPU6050 transport
Context: installed Wire1/I2C4 has indefinite ownership waits and500ms completion
waits; elapsed checks afterward cannot satisfy R4. Native installed registers,
RM0456/current ES0499 and the U585-specific filter/timing calculation support a
finite polling mechanism while source clock and electrical premises stay open.
Decision: adopt P2_imu_bus_contract.md/public imu_bus_unoq.h. Retain the installed
PD12/PD13 AF4 Qwiic route; name it in config, not as wiring/PINMAP approval.
Select address0x68 with0x69 supported; the real AD0 strap remains unverified.
Select conditional TIMINGR0x40EB202C, analog filterON/DNF0,100us setup acceptance,
600us whole-transfer acceptance,50us separate local disable and8192 shared polls.
These are new development constants; no B16 value changes. Limit the transport
to typed MPU6050 register reads/writes and one15byte INT_STATUS+motion burst.
Completion is not sensor identity/settings/freshness/heading. Any runtime fault
latches until reset; retain the irreversible boot claim even after ignored first
writes. Invalid requests do no I/O. Choose conservative invalidation for BERR;
cleanup only clears PE under retained ownership, with finite acknowledgement.
No synthesizedSTOP/retry/reenable/RCCreset/bit-banging; DISABLED means localPE0,
not externally idle/recovered bus. Do not blindly clean up after ownership loss.
Consequence: independent spec-derived actual-source tests, inert target compile
and fresh review required. The proposed ±1% clock envelope is conditional, not a
measured guarantee or permission to exceed MCU ratings; SC-AJ remains global.
No stock Wire calls, new generic framework, app integration, hardware evidence,
phase gate or upload/run follows. MPU bounded setup/config/readback, sample-age
and axis/bias integration remain a distinct next B3 task.


D079 diagnostic clarification (2026-09-23): error_flags retains both observed
hardware error flags and unexpected protocol status bits, includingADDR/TCR or
unexpectedTXIS/RXNE/STOPF/TC/DIR/ADDCODE. Normal allowed progress is not an error.
Independent tests exposed the initial ambiguity; choose retained causal evidence
before PE0 rather than dropping protocol-fault evidence. No partial data or
success assertion is weakened. Original failures stay in author receipts.


## D-080 (2026-09-23, selected under D-051/D-075) Checked MPU6050 setup and decode
Context: native transport D079 exists; coherent bytes alone do not prove settings,
new samples or heading. Manufacturer source audit provides a finite fixed profile.
Decision: adopt P2_imu_setup_contract.md and imu.h before independent code/tests.
Select1000dps/8g/DLPF1/divider0, waits110/110/50/20/20ms, absolute1s setup deadline,
1024advances/64Bus-call caps (count-name exceptions). Verify reset state, identity
and full selected register bytes; unexpected reserved bits reject this profile.
At most one bounded Bus call per advance; all waits return, faults latch. Decode
coherent sensor coordinates explicitly, with raw rails and no freshness/yaw claim.
Consequence: new development constants only, no old B16/pin/core/locked changes.
Independent scripted-bus tests, target compile and separate review are required.
Setup readiness means observed profile, not physical settling or accepted sensor
freshness. Defer acquisition aggregate deadline, bias/axes/yaw to subsequent B3
work; SC-AJ/F091, physical acceptance and human gates remain pending.


## D-081 (2026-09-23, selected under D-051/D-075) Qualified MPU acquisition
Context: D080 settings/coherent decoding alone do not establish a new sample.
F101 source audit supplies a conditional status/STOP/15byte-shadow inference;
B14 requires explicit failure when no data is observed for20ms.
Decision: adopt P2_imu_acquisition_contract.md and its public native/Acquirer
headers. One native600us/8192 Operation covers status plus full15byte burst;
keep existing cleanup bound and all previous public transport behavior. Preserve
both status bytes diagnostically, no second generation or retry of a consumed
event. Acquirer privately owns Bus/Setup and emits NOT_READY/NO_NEW/OBSERVATION/
FAULT, never cached gyro as new. Name B14 IMU_SILENCE_US20000; anchor to setup
completion then accepted observation completions, check both call and completion
with equality failing. Select reset-only silence/runtime-fault recovery.
Consequence: sample freshness is conditional on documented shadow behavior and
exclusive verified profile, not physical silicon proof.198clock slow corner can
exceed600us and must fault; no changed timing budget,800us tick claim or gate.
Independent native and wrapper tests, full relevant regression, inert target
compile and separate review required. Bias, axes, calibration-presence and
continuous-yaw integration follow separately; SC-AJ/F091 remain global blockers.


## D-082 (2026-09-23, selected under D-051/D-075) Explicit body coordinates and yaw
Context: D081 publishes qualified sensor-coordinate observations. B3/D059 need
continuous yaw, a future-increment bias path and distinct fresh/retained evidence.
The physical sensor orientation and a numerical gap rule were unspecified.
Decision: adopt P2_imu_heading_contract.md and imu_heading.h. Require an explicitly
confirmed proper signed axis permutation; choose body X forward, Y right, Z down,
without selecting the robot's unverified mounting. Integrate mapped body-Z rate
with a double trapezoidal accumulator using observed completion times, explicitly
an approximation. First observation anchors zero; no GO reset or NO_NEW increment.
Select IMU_HEADING_MAX_GAP_US=2000 as a development continuity limit, equality
allowed, larger gaps reset-only faults. B14's separate20ms acquisition deadline
is unchanged. Apply finite accepted bias to future increments only. Distinguish
fresh gyro/acceleration from retained bounded-age heading; selected yaw gyro rail
loses continuity, horizontal acceleration rails invalidate acceleration only.
Consequence: no physical map, measured timing/accuracy or gate is inferred. This
is the concrete HAL estimator, not yet core/app wiring: the current combined
imu_ok still needs separate availability/freshness routing. D024 averaging and
D059 logical GO origin remain unchanged. New spec-derived tests, target compile
and fresh separate review are required; no old locked assertion changes.


## D-083 (2026-09-23, selected under D-051/D-075) Explicit countdown gyro admission
Context: D082 NO_NEW is not an invalid gyro reading, and replayed sensor data
must not bias D024 averaging. Existing Services has only imu_ok and tick time.
Decision: adopt P2_calibration_presence_contract.md and append explicit gyro
presence/source identity to ServiceSample, preserving LEGACY defaults. ABSENT
skips only aggregation; INVALID rejects; VALID uses finite raw pre-bias data,
source and decision calibration windows, forward sequence/time and at-most2000us
delivery age using the existing D082 limit. Ignore identical replay, reject
conflicting/reversed identity and mixed explicit/legacy mode. Calibration closes
at its original decision deadline; late delivery cannot reopen it or delay GO.
Consequence: unchanged averaging/spread/minimum/bias-on-rejection and all service/
STOP/hold behavior. No old test edits or physical assumption. This implements
Services/Lifecycle only; separate heading/Fusion/Robot/B15 routing remains required
before app integration. Independent tests, target compilation and review required.


## D-084 (2026-09-23, selected under D-051/D-075) Complete IMU evidence routing
Context: D082 separates fresh gyro/acceleration from retained yaw; D083 accepts
explicit calibration data, but Robot/Fusion/heading/recording still conflate them.
Decision: adopt P2_imu_integration_contract.md and additive pure interfaces. One
Robot owner validates explicit report shape/time/identity and suppresses replay.
Retained bounded yaw remains usable for motion without refreshing measurement
history; fresh-only impact, phantom creation, inward capture and stall angle
evidence remain separate from event timers. Stuck extrema use fresh samples while
qualified opponent age advances; world evidence retains heading source time.
Typed HeadingReference preserves actual GO/source times and prevents old retained
data reviving after clock wrap. Thin applyEstimate connects the actual HAL report.
B15 uses a self-identifying two-by-two-bit presence extension in the existing25B
frame, with explicit encoder selector and unchanged legacy behavior/CSV schema.
Consequence: no old test changes, config values, physical facts or gate inferred.
Complete software path plus independent spec tests, host/sanitizer, targetcompile
and fresh review required. Physical mounting/accuracy/WCET, SC-AJ/F091 and full
QTR/app integration remain pending; no motor-capable upload/run permission.


## D-085 (2026-09-23, selected under D-051/D-075) Async QTR frames and explicit freshness
Context:10us charge plus1500us discharge cannot complete every1000us tick. Actual
IMU600us work also prevents assuming precise once-per-tick polling. Current Robot
couples line/opponent freshness and Escape would replan repeatedly on cached white.
Decision: adopt P2_qtr_native_contract.md, source audit and additive interfaces.
Keep10/1500 thresholds and1kHz control. Select cooperative native timing brackets,
minimum2000us starts,2500us whole-frame guard and6000us source-age expiry; explicit
line identity/presence and split opponent freshness prevent stale confirmation,
replans and exits. Ambiguous color is invalid/inhibited, never fabricated black.
Use exact native GPIO guards and explicit exclusive-pad grant; no IRQ registration
or automatic takeover. Selected call/cleanup/charge/count guards live in config.
The original P2 B2 timeout+100us whole-call criterion is explicitly replaced for
this asynchronous method by bounded calls/frames and measured color separation.
Consequence: these software choices do not prove physical cadence, pad handoff,
QTR color separation, SC-AJ/F091, full-tick800us or any human gate. Native driver,
adapter and actual Robot evidence routing need independent tests/target/review.
Original B16 timing/threshold defaults and every established locked test remain.


## D-086 (2026-09-23, selected under D-051/D-075) Optional fixed A1 acquisition
Context: B6 needs raw A1 evidence; D078 already owns ADC1 for A0. Primary-source
P2_adc_pair_audit verifies PA5/channel10 and legal enabled-idle rank changes.
Decision: adopt P2_adc_pair_contract.md. Preserve battery-only begin/read and
append explicit beginWithButtons/readButtons with typed raw/time/sequence data.
One boot-lifetime owner, fixed profile, per-channel exact rank history, independent
PA5/DAC2 guards and shared reset-only faults prevent stale cross-channel output.
Use existing100us conversion/shutdown bounds; BUTTON_INPUT_PIN15 records the
unchanged proposal. No second owner, generic router, decoder or added timing value.
Consequence: actual native implementation plus independent regressions, inert
compile-only/source/ELF checks and fresh separate review are required. SC-A,
settling/accuracy/full-tick timing, SC-AJ/F091 and all physical gates remain open.
No wiring claim, upload key, B16 value or established locked assertion changes.


## D-087 (2026-09-23, selected under D-051/D-075) Button evidence and fresh gesture routing
Context: D086 supplies raw A1 data; mapping failure to NONE or replaying a cached
level could manufacture a release/hold. Existing LINE_CONTRACT256 is also rejected
by the legacy B15 detail7 range, whose established tests must remain unchanged.
Decision: adopt P2_button_routing_contract.md. Use explicit raw windows with no
configured physical defaults, distinguish absent/invalid/ambiguous data, and select
5000us bounded continuity/age with reset-only BUTTON_CONTRACT512. Source timestamps
qualify fresh sampled gestures; actual decision ticks anchor full START/STOP/menu
holds. Gate/services continue on no-new ticks. Require fresh neutral qualification
before START after boot; preserve legacy APIs and all existing tests. Append B15
extended contract detail11 for known high fault bits, preserving detail7 semantics.
Consequence: actual decoder/Robot/gesture/event implementation, independent tests,
real MotorGate boundary checks, target compile-only and fresh review are required.
No unique START/BOTH electrical distinction, wiring change, physical acceptance,
full-tick timing, app integration, human gate or motor permission is inferred.


## D-088 (2026-09-23, selected under D-051/D-075) Bounded matrix output
Context: B3/B13/B14 require actual UI rendering; installed matrix APIs are void
and the ISR shares one104-byte buffer. User explicitly permits bare-board tests.
Decision: adopt P2_matrix_contract.md and the installed source audit. Fixed pure
renderer, explicit unavailable data, display-only ranges/cadence and one granted
normal-startup owner use checked native calls with exact saved-PRIMASK restore.
Return initialization/submission unconfirmed, never fabricated optical readiness.
A separately reviewed inert built-in-matrix bench may run on the connected bare
UNO Q with recorded target/source/artifacts; no external acquisition or motor path.
Consequence: independent tests, actual target/disassembly and separate review
precede deployment. Runtime counters are not optical acceptance or full800us WCET.
No existing locked test, wiring, gate, motor-run or physical fact changes.


## D-089 (2026-09-23, selected under D-051/D-075) Actual QTR calibration and handover
Context: B13 needs raw white/black calibration; current threshold ambiguity faults
Robot before service intent, and cached reclassification could fabricate freshness.
Decision: adopt P2_qtr_cal_contract.md. Explicit raw-only BOOT/IDLE preparation
inhibits match/motors while preserving native faults, STOP and actual menu gestures.
Eight genuine service requests collect16distinct frames per stage with1000ms
deadlines; conservative interval extrema define an atomic versioned RAM bank.
Later-source classified frames and fresh neutral/START restore readiness without
clearing faults or weakening existing tests. Share raw validation and export an
exact bounded printable config snippet; no new MATCH Bridge traffic.
Consequence: actual owner/adapter/Robot/MotorGate pipeline needs independent tests,
target compilation and fresh separate review. No physical colors, wiring, pinmap,
clock/WCET, human gate or motor permission inferred. Existing defaults unchanged.

D-089 review disposition (2026-09-23): fresh review proved unseen old-frame
era alias after full wrap. Adopt the contract source-era addendum: indefinite
absence stays inhibited, but valid source presentation at accumulated half-range
requires reset; below it, tie source deltas to accumulated decision age. Robot
LINE_CONTRACT/owner SOURCE_ORDER preserve banks and faults; add regression tests.


## D-090 (2026-09-23, selected under D-051/D-075) Bounded IDLE dump path
Context: B8/B15 has RAM/CSV but no live transfer; stock Bridge uses allocation
and unbounded locks. SEALED alone cannot authorize STOPPED dumping.
Decision: adopt P2_dump_contract.md. One current-IDLE local service intent owns
a bounded, cancelable, checksummed stream of the retained real recorder; Linux
capture receives only and publishes exact validated CSV without motion/reset.
Retain explicit origin, source/epoch/summary identity, missing/loss metadata and
SENT_UNCONFIRMED status. Native transport requires installed-source proof and a
separate bounded backend; no stock blocking Bridge call is accepted.
Consequence: actual implementation, independent tests, target compilation and
fresh review required. Local reset UI/app integration, physical RAM/WCET/200s
and all human gates remain pending. No new wiring, motor upload/run or gate.


## D-091 (2026-09-23, selected under D051/D075) Inert recorder runtime probe
Context: D090 software is tested/target-compiled; actual200s loaded recording/freeRAM remain unmeasured. User authorizes bareUNOQ tests without sensors. Installed heapstats/stackwatermark APIs are unavailable (F113).
Decision: adopt analysis/P2_recorder_bench_contract.md. First isolate real-time synthetic Robot/MotorGate/AttemptRecorder retention with no nativeoutput/sensor/UART operations; use fixed diagnostics and separately reviewed read-only allocator snapshots/parser. Explicit failures/losses remain evidence; no fast-forwarded time or claimed stack high-water. Exact inert source/run review precedes upload; never relax old capture guards implicitly.
Consequence: actualboard runtime/memory evidence may advance B8 preparation, not physicalsensor/motor/fullWCET/human gate. Clean nativeUART transport is a subsequent separately identified scope. No B16 values or wiring change.

## D-092 (2026-09-23, selected under D051/D075) Complete-tick timing separate from decision
Context: SC-AK: D084 sensor admission requires post-acquisition decision time,
but D060 timing equates that time with whole-tick start and excludes acquisition.
Decision: adopt analysis/P2_tick_timing_contract.md. Fixed-lifetime explicit timing
mode saves each token's actual acquisition start; ordered start/decision/application/
completion/next-start/next-decision share an unsigned half-range anchor. Invalid
timing remains incomplete evidence only; preserve actual application validation,
legacy defaults, GO/STOP membership, sensor timestamps and established tests.
Consequence: independent additive tests, actual target compile-only and fresh
review must prove integration. No clock/WCET/physical/gate or motor-run claim.

## D-093 (2026-09-23, selected under D051/D075) Fixed ADC app input owner
Context: per-tick A0+A1 contributes to a native deadline sum exceeding800us before
other work. D078's fresh-only API supplies timestamps but app integration lacks
qualified retained battery evidence and shared failure routing.
Decision: adopt P2_power_inputs_contract.md and public power_inputs.h. A fixed
exclusive callback owner performs one pair setup and all A0/A1 calls, with10ms A0
period and strictly below20ms retained age, real source brackets, accumulated age
and reset-only shared faults. This explicitly permits bounded retained voltage at
app projection only; native Reader stays fresh-only. Existing each-tick governor
filter/caps, UI validity, Robot inhibition and locked tests remain unchanged.
Consequence: independent host/native/pipeline tests, inert target compile and fresh
review required. Limits are development choices, not measured margins or800us proof.
No hardware/wiring/gate/motor-run permission or actual scheduler is implied.


## D-094 (2026-09-23, selected under D051/D075) Resumable native IMU runtime
Context: SC-AL atomic runtime I2C cannot yield for QTR service; existing component
guards do not prove a complete800us schedule. RM0456/installed LL source supports
retained progress flags and clock-stretched continuous bursts, with D081 freshness
remaining conditional. Both prerequisite audits are saved independently.
Decision: adopt P2_imu_resume_contract.md and frozen public progress APIs. One
native protocol action per advance, original600us/8192poll budget through all
yields, unchanged one50us cleanup. Pending is a separate envelope, never NO_NEW.
Explicit cancel or supported legacy call during pending terminally cancels; invalid
legacy requests still refuse without mutation. Actual Acquirer validates every
active caller time/silence and cancels active native work on semantic abort.
Consequence: additive native/Acquirer implementation, independent tests and fresh
review required before actual app scheduling. No config/old B16/locked change,
rate relaxation, physical clock/stretch/WCET, gate or upload/run authority.

D094 implementation clarification,2026-09-23: preserve D079's8192nd allowed
observation and reject the next attempted pass; elapsed600us equality still
rejects. IDLE/unknown progress cannot certify native termination, so RESPONSE
cancels once regardless of transfer status. Only declared COMPLETE/FAULT keeps
nonOK TRANSPORT precedence over remaining pulse/shape/time checks. Independent
review found the missing state check; production was corrected. Two contradictory
new authored expectations were reconciled with additive unknown+NACK coverage;
no established/locked test changed. See P2_imu_resume_failures.md and contract.


## D-095 (2026-09-23, selected under D051/D075) Actual application transaction owner
Context: after D094, app composition still lacks an exclusive S..C/Robot/Gate/
recorder owner. Invalid clock or lifecycle can prevent a fresh Robot command;
Gate.reset clears faults and duplicate-token apply is not a valid emergency API.
Decision: adopt P2_app_transaction_contract.md and frozen public headers. Add one
terminal non-token MotorGate.halt and a fixed app::Transaction owning actualRobot,
Gate and AttemptRecorder. It captures real start/decision/completion, overrides
caller receipt fields, applies once and preserves final real-tail recording.
Invalid lifecycle/clock/identity halts once and interrupts evidence truthfully.
Consequence: ordinary800/1000us timing retains B14 count/log behavior; no new
runtime timing stop, source schedule, config/wiring change, physical proof or
phase gate. Source scheduling/grants/expiry remain next integration work. Add
independent tests and real inert target/source review; preserve all old tests.


## D-096 (2026-09-23, selected under D051/D075) Actual native app source scheduling
Context: D095 supplies actual transactions; app.ino remains inert. Native source
integration requires exclusive QTR charge service, truthful source expiry at actual
D, raw calibration readiness and a real release/STOP-tail owner. Separate codebase
explorers identified the projection-time race and raw-readiness/publication traps.
Decision: adopt P2_app_runtime_contract.md and public runtime/DecisionSource headers.
Bind existing native HAL owners; complete real epochs on the original1kHz grid;
finite service/clock guards, no catch-up. Project source ages at actual D, retain
genuine source identity, raw boot unless thresholds explicitly confirmed, and
actual post-Gate calibration/display/STOP cleanup inside S..C. Default hardware
grants stay false. STOP receives one real final tail then passive runtime stop.
Consequence: no B16 change, physical grant or measured800us claim. New development
limits are QTR servicewindow600us,8192pump passes,65536equal-idle-clock observations.
Original IMU600us/ADC/QTR/Gate guards remain. Adverse sum can exceed800us; record
actual complete timing and resolve before physical acceptance. NativeUART/local
reset/calibration-snippet transport remain follow-on P2 tasks, not completed here.
Preserve old tests and motor-run restrictions; compile actual app only, no upload.

D096 API naming clarification: name the projection entry decideFrom(DecisionSource),
not an overload of decide. The overload made existing D095 smoke decide({}) calls
ambiguous. Preserve legacy source compatibility and unchanged callback semantics;
record/add regression before new test establishment, no old test edits.

D096 review clarification: optional pure DecisionSource.clockAccepted rejects
source-owner clock chronology after projection but before Robot/Gate.apply/recorder.
False causes Transaction CLOCK/halt and Runtime CLOCK. A late D earlier than actual
acquisition observations must not be encoded as LINE_CONTRACT to manufacture a
stopping Robot tick. Reviewer identified this MAJOR; preserve originalreproduction,
fix and independentverification. Pure projection performs no actuator-bearing abort.

D096 further independent corrections: admit actual Gate A into Runtime clock
chronology before postwork; finishAfter validates actual latest outer observation
against D/A/C before publishing completion/previous feedback. Retain legacy finish.
Pump advances every active QTR at least once per actual epoch before threshold
short-circuiting, preventing retained lower bounds from starving frame completion.
Both are implementation corrections, not altered source timing/color or Gate rules.
Actual full-app compile first failed RAM276368 >262144; preserve target failure and
linked artifacts. No capacity reduction, fake compile success or upload follows.

## D-097 (2026-09-23, selected under D051/D075) Passive IMU setup-fault evidence
Context: actual app exceeds target memory by14312B. Native setup-fault retrieval
currently references the legacy runtime read API solely to obtain a stored fault,
retaining unused synchronous runtime paths in the app image.
Decision: adopt P2_imu_fault_access_contract.md; add const setupFailure() returning
exact latched setup fault, or canonical NOT_READY outside actual setupFAULT. Bind
only native setup-fault retrieval to it, ignoring that callback's time argument.
Consequence: preserve all legacy/async/setup semantics and every evidence field;
no capacity/config/timing/startup change. Independent tests, target dependency/
size comparison and separate review required. Estimated saving is not proof and
cannot alone close the full RAM blocker. No upload or physical/gate authority.

## D-098 (2026-09-23, selected under D051/D075) Isolated forced-library experiment
Context: primary-source audit finds mandatory RouterBridge discovery and directly
linked singleton objects, with no supported source-level opt-out. Actual app RAM
exceeds the limit. Source-only include changes cannot prove removal.
Decision: adopt P2_bridge_dependency_experiment.md for a compile-only control/
candidate comparison using the single explicit discovery-flag property override,
identical frozen source and separate output/build directories. No production
policy is changed; inspect all native/startup/dependency and memory consequences.
Consequence: property is CLI-supported but not an official Bridge opt-out; accept
no speculative saving or fabricated compile. Separate review and explicit future
build contract/tests required before adoption. No installed edits, capacity change,
new upload key, MCU operation, physical gate or motor authority.

## D-099 (2026-09-23, selected under D051/D075) Checked app-only dependency policy
Context: D098 control/candidate evidence1447ec8 proves27452B real saving with
unchanged app/native/startup paths. Ordinary app build remains RAM-blocked.
Decision: adopt P2_app_build_contract.md: fixed app-only native-app-v1 compile
policy, pinned identities, strict successful CLI JSON/properties/zero-library
checks, fresh policy/mode paths and hashed actual artifacts. Preserve bench
commands and every upload/motor guard. Test independent expectations first.
Consequence: bypass is not an official Bridge-disable API; reject drift or any
external library. Validate all adopted modes on board Linux only, with exact
source/ELF/startup/import evidence and separate review. No firmware/config change,
loadedRAM/WCET/physical/gate claim or upload follows.

## D-100 (2026-09-23, selected under D051/D075) Precompile effective configuration
Context: D099-R1 proves selected safety metadata does not constrain effective
recipes/compiler/hooks; postcompile rejection cannot prevent a bad prebuild hook.
Decision: adopt P2_app_override_contract.md: resolved directory queries, explicit
profile/local/global override refusal, precompile installed pins, one hook-free
expanded-properties preflight and complete effective-command reference checks,
then real compile and repeated checks. This narrowly amends D099's show-properties
ban for a separate preflight only, never as firmware-build/library success.
Consequence: preserve default/Immediate/MATCH meaning and all upload restrictions;
no source/config/capacity or hardware authority change. Independent regressions,
exact primary-source audit, actual target evidence and separate review required.

D-100 clarification (2026-09-23): the effective reference has84 keys including
build.compiler_path/build.crossprefix/build.zip.pattern. Reject all six documented
override/profile paths (regular files or dangling symlinks), and reject ambiguous
or shell-active directory strings before properties/compilation. Ordinary spaces
remain allowed. See the contract addendum and independent regression receipts;
these tighten build-input checks without changing firmware or any human gate.

D-099/D-100 acceptance (2026-09-23): corrected actual default, inert Immediate
and MATCH compile-only builds pass, exact source/ELF/dependency/startup audits and
fresh same-model review PASS. D099-R1 is addressed. Explicit fixture under fixed0
and ordinary discovery is compiled then rejected for nonempty libraries. Initial
forced1 control failure remains; stock-template correction is documented. Adopt
only the scoped checked-build policy; no firmware/hardware/gate/run authority.
Evidence P2_app_build_validation.md and P2_app_acceptance_review.md.

## D-101 (2026-09-23, selected under D051/D075) Actual Runtime dump attachment
Context: D090 bounded transfer/native port exists, but actual app never invokes it.
Decision: adopt P2_app_dump_contract.md and public optional DumpPort/Runtime seam;
Gate-first setup, actual post-Gate/recorder authority, full S..C service timing,
explicit owner-abort cancellation, unchanged terminal behavior and absent grants.
Consequence: independently test actual app pipeline, final target memory/dependency
and fresh review. No new protocol/remote control/config/pins/permission. Post-STOP
local service reset and calibration delivery remain explicit subsequent tasks;
this does not claim physical B8 or a phase gate.

## D-102 (2026-09-23, selected under D051/D075) Lossless frame storage
Context: D101 Runtime dump is host-tested but cache-source MATCH model exceeds
its262144B loader pool by256B. The26-byte frame includes only three accepted
status values; storing status in two bits preserves its exact information.
Decision: adopt P2_frame_packing_contract.md, separate25-byte payloads and two-bit
status lanes. Explicitly replace D069 StoredFrame pointer lookup with copied
read(index,out), plus bytesAt for its genuine retained-payload alias guarantee.
Preserve5001frames/4096events/25Hz, every raw byte/status/loss/counter, constant
logical reset, CSV/wire/CRC and existing test expectations. Migrate only current
unlocked fixtures/API callers; leave locked tests and historical evidence intact.
Consequence: independently test the contract and review lifetime/fixture changes,
then verify actual source/ELF/loader savings before closing D101-R1. This is not
loadedRAM/WCET/physical evidence, a gate, new wiring or upload/motor permission.

## D-103 (2026-09-23, selected under D051/D075) Local inhibited service after STOP
Context: D101 connects dump but Runtime becomes permanently passive after STOP;
physical reset loses retained RAM. D1029a8797d restores conditional build capacity.
Decision: adopt P2_service_reset_contract.md. Optional default-off local gesture
qualifies after genuine STOP tail; one guarded Robot-only reset occurs inside
next real S..C with EMPTY/SEALED evidence. Keep GateSTOPPED/nativeowners/clocks/
tokens/recorder/thresholds; service-only RAW/absent sensors prohibit every match
start. Continued stopped observations honestly retain expected QTR absence faults.
Fresh ADC/opponent evidence is still mandatory; report unsupported actions in
app/display fields. A second STOP tails then becomes permanently passive.
Consequence: explicitly extends D096 terminal passivity only for opt-in; unchanged
core STOP/default-off tests and no native rearm. Independent tests/target memory/
review required. No physical fact/gate, wiring, upload or motor authority follows.

D-103 clarification (2026-09-23, before independent test freeze): preserve first
post-reset A1 source continuity across Robot.reset, separately from pending-S
admission. A real reset followed by stale first acquisition remains an actual
reset pulse plus terminal Runtime fault, never a fabricated successful epoch.
Use actual MODE source completion for the hold deadline. Preserve the expected
absent-line fault on the second real STOP tail. See the contract addendum.

## D-104 (2026-09-23, selected under D051/D075) Bare-board Runtime load probe
Context: D1031b1d77d passes software/target review; actual loaded Runtime remains
unmeasured. The user freshly confirms UNOQ alone and authorizes testing. Normal
app configures proposed motor pins even with output inhibited, so it is unsuitable
for a no-pin probe without physical wiring approval.
Decision: adopt P2_runtime_inert_contract.md and public pure probe ABI. Use actual
Runtime with absent grants and checked inert callbacks,200s real MCU-clock window,
stable truthful terminal evidence and exact separate capture. Extend checked build
policy only to the named probe; no upload key until independent exact review.
Consequence: a new reviewed inert run may establish only that image's BOOT/load,
allocator and sampled-stack facts. Full-app/native/motor/WCET/physical gates remain
open; no new pin/source grant, synthetic START or changed production tunable.

## D-105 (2026-09-23, selected under D051/D075) Bounded bench calibration output
Context: D089 commits a valid RAM bank and formats its config line, but no actual
Runtime delivery exists. D1041fa2a01/c82460e measured the separate bare probe;
full-app capacity remains narrow. User delegates routine engineering choices.
Decision: adopt P2_calibration_delivery_contract.md and public output report.
Require both existing dump and new default-off calibration grants, non-MATCH
only, one native output owner, real commit/receipt authority and symmetric
cancel-before-new-writer arbitration. Preserve poison, exact formatter payload,
actual S..C, thresholds and recorder bytes. Regenerate bounded stack payload;
compile out mutable exporter state/code in MATCH. Strict file-only receiver
publishes unauthenticated evidence and never edits config.h.
Consequence: implement/test/review and verify exact full-app target fit; no new
wire, tunable, locked-test relaxation, native UART success or hardware/gate grant.
Current inert source keys remain historical exact snapshots and must refuse
changed source uploads until separately reviewed. MCU remains frozen D1042bd817c4.

D-105 before-test-freeze clarification: preserve D101 invalid-receipt Transfer
step suppression and failed-epoch/public-abort cleanup without fabricated C.
Freeze refusal/cancel/failure phase mapping and unavailable-port disposition
in the contract; no change to existing D101/D103 safety or timing rules.

D-105 test-author clarification before Runtime test freeze: a chronologically
forward but expired now-D>=TICK_US is CONTEXT, matching stale admission; reverse/
half-range clocks are TIME_ORDER. Preserve literal phase mapping above.

## D-106 (2026-09-23, selected under D051/D075) One installed native pin table
Context: D105 default modeled loader peak263112 exceeds262144 by968 bytes. Four native consumers retain identical560-byte installed tables.
Decision: adopt P2_pin_table_contract.md; one lifetime-stable const table/count definition derived from installed wiring_private.h, with unchanged native bounds, metadata, grants, operation order and errors.
Consequence: require independent cross-unit tests, unchanged native suites, exact table/relocation/import/startup and ordered loader audits. No pin/config/core-installation change, hardware approval, upload or relaxed assertion. Gross1680-byte removal is not a measured net-fit result.

## D-107 (2026-09-23, selected under D051/D075) Motor-free opponent-view bench
Context: P2 B1 has native driver and compile probe, but lacks its named live-view bench. OPP-VIEW-1 geometric UI discrepancy is recorded separately.
Decision: adopt P2_opp_view_contract.md and public Runner/Native headers. Literal channel-index strip, current unknown/error indication, actual bounded source/callback timing, one sensor/matrix owner and all grants false. No motor owner or EN/PWM operation.
Consequence: independent literal tests, compile-only target review and default startup silence precede software acceptance. Upload allowlist remains closed; no sensor electrical grant, physical ranges/false-hit result, optical claim or phase gate. Existing production geometric display remains separately tracked.

## D-108 (2026-09-23, selected under D051/D075) Correct front display identity
Context: OPP-VIEW-1 identifies a D088 presentation mismatch against B0/D076:
FL15 bit0 is displayed at FC and FC bit1 at FL15.
Decision: adopt P2_display_channel_contract.md; swap only those two geometric
coordinates and the corresponding unlocked literal oracle positions, with new
independent projection regressions. Preserve original D088 text as provenance.
Consequence: no core/pin/polarity/config/native or locked-test change. Full host,
target and separate review evidence precede acceptance; no physical/gate/upload
authority follows from this delegated presentation correction.

## D-109 (2026-09-24, selected under D051/D075) Finite QTR bench evidence
Context: D085 native acquisition exists, but the named B2 raw bench is missing.
Decision: adopt P2_qtr_raw_contract.md and public Runner/Native headers, including
the pre-test clock/cleanup precedence clarifications. One Reader, default-false
pad grant, cooperative single-call servicing and immutable first128 raw frames;
automatic finite freeze, separate actual fault/cleanup evidence, no other owners.
Add only QTR_BENCH_FRAMES=128 to config and its unlocked literal registry; preserve
all earlier values/assertions. No new output transport or acquisition semantics.
Consequence: independent expectations precede implementation execution; separate
author/implementer contexts may write in parallel from the frozen public contract.
Freeze executable tests before their first run. Exact native checked target
review follows; stable RAM capture is software preparation, not physical surface
evidence or readout. No pad/pin/electrical/upload/motor grant or human gate follows.

## D-110 (2026-09-24, selected under D051/D075) Finite battery bench evidence
Context: native D078/D086 power acquisition exists but P2 B5 named bench/vbat is missing.
Decision: adopt P2_vbat_contract.md and public Runner/Native headers after independent author preflight. One battery-only Reader, false grant, immutable first128 fresh samples at existing10ms cadence. Preserve actual sample/shutdown and source/call/closing times; no A1/stop/transport/other owner. Add only VBAT_BENCH_SAMPLES128 plus its unlocked literal assertion. Exact float boundaries and publicly reachable missed-release saturation profile are explicit.
Consequence: independent expectations freeze before first execution while separate contexts author in parallel; exact checked compile-only target review follows. No native driver/pin/scaling/default-cadence or locked-test change, upload key, physical accuracy, electrical/motor permission or human gate.

## D-111 (2026-09-24, selected under D051/D075) Finite IMU heading bench
Context: P2 B3 named bench is missing; existing Acquirer/Estimator/Services already supply source, heading and bias policy. Independent public-oracle and actual-source preflight PASS on draftc08128b2.
Decision: adopt P2_imu_heading_bench_contract.md and public interfaces. Explicitly permit Services.start at accepted setup C for this motor-free bench only; it is not Controller release/START/GO. Preserve all production countdown/calibration semantics. Add only five bench duration/count values60s/1s/61/70s/100M with exact additive unlocked expectations. One Acquirer, actual pure consumers, false grants, paced setup/new-read and bounded pending advances,61 immutable source checkpoints.
Consequence: independent frozen expectations, implementation, checked target and separate review precede software acceptance. No pins/native guards/mounting/behavior/locked-test change, upload key, physical drift/rotation claim, motor permission or phase gate.

## D-112 (2026-09-24, selected under D051/D075) Finite A1 raw/decoder evidence bench
Context: P2 B6 lacks a named acquisition bench; production electrical windows remain unconfigured and SC-A unresolved. D111 completedc1f48d4; historical registry proof repair769727a preserves live value checks.
Decision: adopt analysis/P2_ui_bench_contract.md after both separate preflights. One existing Reader beginWithButtons/readButtons, actual ui::decodeButtons,128 immutable raw/source/decode records at existing TICK_US, defaultfalsegrant and no matrix/motor/transport owner. Keep actual UNCONFIGURED/UNKNOWN/AMBIGUOUS/INVALID decoder diagnostics distinct from admitted raw capture; rejected A retains older decode with explicit provenance. No fabricated stop API or physical thresholds. Add only UI_BENCH_SAMPLES128 and one literal registry expectation.
Consequence: independent frozen tests, native/default passivity, strict profiles, checked default/Immediate target and separate review required. This is raw acquisition preparation, not full gesture/menu/display B6, electrical/PINMAP acceptance, upload authority or a gate. All prior hardware/safety/core defaults remain.

## D-113 (2026-09-24, selected under D051/D075) Observable receive-only TCP connection
Context: existing blocking dump receiver cannot expose attachment while capturing; cached router has no exact-client registration acknowledgement. D112 completed d8a5bf5; prerequisite inventory191046f.
Decision: adopt analysis/P2_dump_receiver_arm_contract.md after separate public/source preflights. Add only optional fresh UUID ticket to existing capture and one bounded observe mode. Exclusive immutable Linux receipts, exact identities, sampled PID/fd/TCP checks, deadlines and failure-prefix evidence; unchanged no-ticket/offline path. Use literal schema appendix,128-character target bound and event-time/deadline distinction.
Consequence: independent frozen tests and actual source review before acceptance. CONNECTED means sampled TCP only; router registration remains UNKNOWN. No RPC, MCU command, UART operation, reset/upload/service change, clean-framing/exclusivity proof, locked-test change or gate follows. A later benign connected-board smoke needs its own reviewable scope.

## D-114 (2026-09-24, selected under D051 and current bare-board test authority) Native A1 diagnostic preparation
Context: user freshly reports bare UNO Q and permits testing; D112 driver/bench software passed but default grant remains false. D078 compile-only policy and SC-AJ clock qualification must remain visible.
Decision: adopt analysis/P2_ui_adc_probe_contract.md for a named true-grant wrapper reusing unchanged D112 sources. Narrowly supersede D078 compile-only restriction only for a separately identified and independently reviewed observation-only bare ADC diagnostic. Preserve SC-AJ as open, all native guards, pins, limits/reference/divider/windows, and no competing ADC/DAC/pad owner.
Consequence: firmware/staging preparation may proceed; independent host checks, exact enabled target/startup/ownership/loader audit, public pinned readout contract/tests and run-specific upload review precede any MCU action. No physical button/clock/voltage qualification, PINMAP, motors, production runtime or human gate is inferred. Original bench/ui default/upload refusal stays unchanged.

D-114 readout software adoption 2026-09-24T02:05:42.112669+04:00: adopt P2_ui_adc_capture_contract.md
from enabled-target proposal7d18789b; exact Runner9892/public fields, raw ET_REL
symbol offset0, two flash/descriptor brackets,22 reads/588016bytes/26 commands.
Full-byte terminal consistency includes semantically ignored padding; truthful
fault/nonterminal/invalid snapshots stay distinct from COMPLETE128. Independent
literal fixtures precede execution; unchanged p0 helpers and fixed public seams.
Original incorrect nm interpretation preserved/corrected before implementation.
No capture execution, artifact placement, upload key or identified MCU run yet.

D-114 readout/guard acceptance 2026-09-24T02:23:09.648935+04:00: final contract0e8ead40 retains fullBSS range and once-only ordered metadata clarification. Run contractb37fb854 adopts exact default M0 run01 guard; independent capture/guard reviews and tests pass. Add only the exact396bcc45 probe manifest key, preserving all eight old values. This does not approve another run or assert physical success; run01 must bind the completed software, final review and actual tool staging before launch.

## D-115 (2026-09-24T02:29:41.458146+04:00, selected under D051/D075) Finite motor inhibition preparation
Context: named motor_stand bench remains missing; complete B4 needs a separate command authority and full B7 conflicts with retained R6. Existing D091/D104 synthetic composition is not repeated.
Decision: adopt analysis/P2_motor_stand_inhibit_contract.md after source/public-oracle preflights. One native Port/Gate, defaultfalsegrant, actual begin once then D095 halt once, retained immediate begin fault and actual halt receipt, terminal passivity. MATCH0/M0 only; no apply/reset, demand, token, contact, clock wrapper or new tunable.
Consequence: independent frozen host traces, exact checked target and separate review precede software acceptance. Truegrant exists only in controlled host fixtures in this scope. No upload key, physical pin operation, directional/brake/powered-kill/B7 claim, wiring or locked-test change, motor authority or human gate follows. Full B4/B7 remains explicitly incomplete.

D-115 prefreeze tooling clarification 2026-09-24T02:37:40.596486+04:00: adoptedcontract nowd8f5fd96 adds only literalmotor_stand.ino/default/M0 checkedcompile-only route with earlyrefusals and no sourceallowlist/upload path. Benchoracles unchanged; firstsourcefreeze binds this exactcontract. D114 run completed once and independentlyreviewed; its exacteleven prior tooling files are archived before any later toolingextension. No reuse of consumedrun approval.

D-115 software acceptance 2026-09-24T02:51:44.704000+04:00: exact firstimplementation and rootliteralcheckedroute pass independent/private/fullhost/policy/targetreviews. SingleNativefixture identifier correction and temporary-ELF audit-model correction preserve originalfailures and assertions. No changedHAL/core/config/establishedlockedtests, motorcommandauthority, sourceallowlist/upload key, B7/R6 exception or human gate. Completedtask is partialB4 preparation only; remaining scopes are explicit in P2_after_D115_checkpoint.md.


## D-116 (2026-09-24, selected under D051/D075) Full synthetic recorder transport bench
Context: P2 B8 still lacks the named complete recording-to-dump bench. D091's prior terminal/no-UART runner stays unchanged; native UART ownership/framing and throughput remain unqualified.
Decision: adopt analysis/P2_recorder_transport_contract.md and bench/recorder/src/recorder_transport.h after independent public-oracle and source preflights. One actual Transaction/Transfer, inert motor callbacks, full200s synthetic attempt, real STOP/tail, qualified synthetic service gesture and guarded reset, permanent service-only projection, actual menu intent and retained-source transfer. Default disabled; no new native wrapper, mutable result or physical grant.
Consequence: independent frozen normal/sanitizer/full-length roundtrip tests and actual source review are required. Literal checked default/M0 compile-only route; no upload key or board execution. Slow-progress TOTAL failure and actual byte/packet accounting must expose native throughput limits; no shortened recording, extended timeout, sensor truth, physical B8 or human gate is inferred. Contract912434c4/headerb43ed245; prefreeze fixes clarify cleanup, source chronology and total deadline502633000us. Production HAL/core/config/locked tests stay unchanged.

D-116 software acceptance 2026-09-24T03:24:52.542645+04:00: finalcontract056c69c8 includes prefreeze8-clock clarification. Firstproduction unchanged, independent/private/fullhost/policy/checkedtarget reviewsPASS. The reviewed new unlocked test-input amendment preserves two upstream static refusals and coherentG==long runtime boundary; original failures and exactdiff retained, no locked/production assertion changed. Native throughput remainsopen underF143; software closure does not mean B8physical or phasepass. Proposed D117 stronger170-byte unrestricted raw-width bound is separate from this bench acceptance.

## D-117 (2026-09-24T03:27:39.645635+04:00, selected under D051/D075) Explicit bounded native TX FIFO mode
Context: D116993afdd0 host composition passes but D090FIFO-off cadence cannot deliver a full recording. Public/source/separate reviewer preflights agree on contract00a6c36c; corrected unrestrictedFR170 width preserves all raw diagnostics.
Decision: adopt analysis/P2_dump_fifo_contract.md exactly and additive Buffering enum/passive constructors. Default legacy remains; only app and recorder explicitly select FIFO8 while all grants/disabled flags remain false. Fixed owned setup writes/readbacks, immediateTEACK refusal, mandatory conditional setup cleanup, AUTOCR0, unchanged8byte/80us/100ms/300s bounds and no remoteRX. Header SHA505868a36ac85e7cd5ac61ff61d65aa12178eb439fa9bceeafa7774dd1fcf66e.
Consequence: independent additive native FIFO/serial-time/full-capacity tests freeze before implementation execution; all legacy/native/factory/D116 assertions preserved. Fourproductionfiles only, plus evidence/tests. Exact appdefault/MATCH and recorder compile/loader reviews required; default headroom456 means fit not assumed. No new native grant, upload key, hardware success, changed R1-R11/config/lockedtest or human gate.

D-117 implementation disposition 2026-09-24T03:48:32.722241+04:00: preserve original default loader-model failure262152>262144. Adopt only equivalent bounded-index setup-state repair1 (nativefdd3df0b); no oracle, capacity, timing, grants, config or lockedtest changes. Exactdefault262136, MATCH260504 and recorder220744 fit conditionally; default8-byte span is not loadedRAM. Independent first26methods, private12, unchanged legacy/factory/D116 and fullnormal/san pass. Evidence and limitations in P2_dump_fifo_validation.md and separate scopedreview; no physical delivery or phasegate follows.

## D-118 (2026-09-24T04:09:29.021567+04:00, selected under D051/D075 and current bare-board test permission) Exact unchanged inert app load observation preparation
Context: D117ed5a9dea exact default/M0 app has only8bytes conditional loader span, not measured loading/RAM. Eligibility1b1a13ba explicitly identifies real EN LOW/zeroPWM/timer initialization despite false optional grants. Separate public/source preflights pass final capture contract06377731.
Decision: adopt analysis/P2_app_default_probe_contract.md for capture software preparation. Keep sourcee820c0e1, ELF8379f152/ZSKc60443cd and all firmware/config/grants unchanged. Select the prospective experiment including existing inhibited motor initialization under the human-reported bare-board premise, not pin/electrical/motor acceptance. New64read/80command ceiling admits exact62/66/1405088B complete plan, preserving2MiB/16KiB RAM/600s/30s limits and all old probe caps/tests. Literal sampled-prefix, allocation-containment, fullflash-bracket, live/absent/fault and failed-collection rules are frozen by the contract.
Consequence: independent executable expectations freeze before implementation execution; new passive tools/app_default_capture.py only plus additive tests/evidence. A separate standalone exact app-run guard contract, software/target/run review, once-only records and explicit input staging are still required before any upload or MCU read. Generic app upload and old manifest remain unchanged; no reused D104/D114 grant, optional peripheral grant, motor permission, terminal-success/WCET/stack/physical claim or human gate. Draft run name app-default-e820c0e1-run01 is reserved, not executed.

D-118 pre-execution clarification and guard adoption 2026-09-24T04:18:22.586487+04:00: capture contractfbf34f25 clarifies collect-owned exclusive output creation and literal opaque tool fixtures; prior06377731 preserved. Separate preflight PASS. Adopt standalone run contract7b364da5 after separate preflight; exact one default/M0 app build/upload route with current-HEAD/source/tool/record checks, unchanged generic refusal/nine-key manifest and one fsynced attempt. No upload authority is exercised until actual source/test/target/run review and live records are complete. Root guard20method oracle6e4c84ad froze before separate implementation; capture oracle remains separate-author work. No firmware/config/grant/oldtest/phasegate changes.

D-118 actual run disposition 2026-09-24T04:42:52.533106+04:00: software9b4afcb2 and separate exactrunreview admitted one unchanged default/M0 app upload and one passivecapture on reportedbare board. Freshchecked10f172 reproduced exactELF/ZSK; bothcommands exit0. Separate744-check actualreview passes narrow loadedimage, sampledprogress and retainedheap scope; no production/config/oldtest change or human gate. Bothclaimsconsumed; no replay/reset/restore. SC-AL gains actualdefault-image load/heap evidence only; stack/fullsources/WCET/physical acceptance remainopen. See P2_app_default_actual_validation.md.

## D-119 (2026-09-24T04:53:21.519504+04:00, selected under D051/D075) Finite B4 directional request sequence
Context: B4 directional software is still missing after D115 inhibition preparation. Native dump execution has unresolved UART prerequisites; delegated engineering choices permit useful independent P2 implementation.
Decision: adopt P2_stand_sequence_contract.md and its public header as the first bounded software slice. One pure twelve-row left/right forward, brake and coast, reverse, brake and coast sequence; distinct timestamp and finite gap rules, permanent STOP/edge cancellation, no restart. Add only STAND_SEGMENT_MS500 and nominal STAND_DUTY0.25, with two additive unlocked literal registry expectations. Existing B16 values, Robot/Gate/DRIVE_TEST and locked tests remain unchanged.
Consequence: independent spec-derived executable tests freeze before first implementation execution, followed by normal/sanitizer host checks and separate source review. This helper has no motor authority or hardware effects. The real B4 profile/Robot/Runtime integration, electrical cap/coast/STOP policy, target fit and powered B4/B7 remain explicitly unfinished; no upload, sensor/grant assumption, B7/R6 exception or human gate.

D-119 validation extension 2026-09-24T04:58:53.292274+04:00: after independent source/oracle freeze, include one checked default/M0 app compile-only build on the existing UNO Q Linux transport. Unreferenced helper sections are expected to be garbage-collected, but the narrow loader margin must be compared rather than assumed. This adds Linux staging/compilation and ordinary artifact collection only; no upload, MCU read/write/reset, UART operation, grant change or new run is authorized. The pure helper behavioral contract/oracle stays unchanged.

D-119 software disposition 2026-09-24T05:03:06.238610+04:00: firstimplementation8dfc2dcb passes unchanged amended publicoracle5e03938c, full normal/sanitizer suites and private review. Original unexecuted oracle65351127 retained; amendment preserves all expected conditions while making fatal prerequisites work with installed no-exceptions doctest. Canonical-registry launch fix changes no expectations. Checked default/M0 source62e38204 reproduces identical D118 loadables; no upload or relaxed safety boundary. See P2_stand_sequence_validation.md. Pure sequence slice complete; real B4 integration remains next.

## D-120 (2026-09-24T05:11:09+04:00, selected under D051/D075) Real B4 bench controller profile
Context: D119 is a pure request helper; actual B4 directional integration remains unfinished. Default target has only eight bytes of conditional loader margin.
Decision: adopt analysis/P2_stand_integration_contract.md and its public conditional interfaces. Compiler-wide SUMOX_B4_STAND defaults0, rejects MATCH; profile1 uses real Robot/Transaction/Gate, finite OPENER bench sequence, final STAND_DUTY cap, shared-EN coast, existing edge escape and full hold/source/receipt checks. Natural completion or successful escape exit inhibits immediately and requests actual lifecycle STOP next distinct tick; STOP/edge arbitrate first. Refuse D103 service reset. Add literal motor_direction default/M0 compile-only wrapper, no upload key.
Consequence: independent frozen tests, unchanged old locked tests/default routes, separate review and measured default/bench target fit required. No new hardware grant, synthesized sensor, motor-capable run, B7/R6 exception, physical fact or human gate. Additive helper interrupt supplies owner safety cancellation only; D119 step contract stays intact.

D-120 software disposition 2026-09-24T05:23:16+04:00: prefreeze contract clarifies immediate SCRIPT_RESULT UI STOPPED and until-reset stand_stopping latch. First implementation passes unchanged independent18-case M0/M1 and configured19-case normal/sanitizer expectations; full4targets normal/sanitizer,54policy methods,9private profile probes and separate scopedreviewPASS. Default sourceef1efc59 loadables remain exactD118; motor_direction24fe6356 compiles M0 with conditional loaderpeak248576/free13568. Harness-only factory/import/index guard repairs preserve originalfailures and every expected condition. No oldlockedtest, configvalue, sourcegrant, upload/run authority or phasegate changed. Evidence: P2_stand_integration_validation.md,146indexedrawfiles. B4 directional software complete; physical B4 and B7/R6 boundary remain unaccepted.

## D-121 (2026-09-24T05:25+04:00, selected under D051/D075) P2 acceptance checkpoint and B7 disposition
Context: D120 completes the eligible directional B4 software slice, but no human phase gate or assembled-robot acceptance exists. Original B7 requires full forward/full reverse while R6 and actual ATTACK prevent that reverse path.
Decision: preserve R6, governor/MotorGate/hold/edge authority and the original B7 criterion; mark B7 BLOCKED/NOT ACCEPTED. Do not fabricate contact, patch outputs, repeat the0.25sequence as a substitute, or implement a new stress controller. Consolidate actual P2 task evidence and unmet criteria in analysis/P2_software_acceptance_packet.md; obtain a fresh separate read-only readiness review, not a fabricated gate pass.
Consequence: no firmware, pin, tunable, locked-test, threshold or physical-test requirement changes. A supported protected resolution and later identified physical run remain prerequisites for B7. Native UART, sensors, electrical/PINMAP, full-source WCET/stack, dimensions, P0/P1 explanation/gates and P2 human gate remain genuine dependencies. Do not begin P3 or invent further helper work when these are the only remaining dependencies.

## D-122 (2026-09-24T06:57+04:00, explicit user scheduling authorization) Advance to P3 software
Context: after the D121 physical acceptance checkpoint, the user said "assume physical accpetence is accepteed and continue". Earlier D051 delegates engineering choices and the user prioritizes software progress.
Decision: treat physical prerequisites as an explicit scheduling assumption and make P3 software active now, superseding only D121's prohibition on starting P3. Execute the existing P3_first_drive.md software scope; keep actual P2 readiness review and physical test results unchanged.
Consequence: ASSUMED-PHYSICAL is not measured PASS, PINMAP/EXPLAINED/GATE evidence, an R6 exception or per-run motor authorization. Preserve R1-R11, locked tests, source grants, existing deadlines and physical 3.1-3.7 acceptance. No request for additional hardware now. First task: actual DRIVE_TEST software with SEARCH/edge only, unchanged initial SEARCH_DUTY_MAX0.30 and independent verification.

## D-123 (2026-09-24, selected under D051/D122) P3 DRIVE_TEST build and local start
Context: P3 requires SEARCH/edge without attacks; default P1/P2 intentionally inhibits DRIVE_TEST. Real menu, Lifecycle, Search, Fusion, Governor, Transaction and MotorGate already exist.
Decision: adopt analysis/P3_drive_test_contract.md. Exclusive compiler-wide profile defaults0; profile1 admits only a genuine selected DRIVE_TEST service release into the unchanged full hold, then uses State::DRIVE_TEST with actual Search and edge priority. Ignore opponent interruptions only at Search routing; retain actual perception/logs/history. Default0 locked cases and D120 remain unchanged. Energized DRIVE_TEST is valid only in this new profile; no new motor authorization follows.
Consequence: independent new profile safety tests freeze before implementation execution; same real Gate/source/receipt boundaries apply. No B16/pin/grant change. New bare native wrapper uses M0 and empty grants, compile-only checked route. P3 stopping-duty trials and isolated turn trials are separate unfinished tasks. Host/target checks do not establish ring results.


D-123 software disposition 2026-09-24T07:09:12.408796+04:00: independent original draft27-case oracle exposed one wrong current-report token field; separate author/reviewer corrected this new unaccepted oracle to require blank current result AND preserved previous identity, keeping all safety assertions. Original/failure retained; accepted lockedhash5bde7967 now protected, all35establishedlocked files unchanged. Firstproduction remains unchanged and passes all6normal/sanitizer suites, configured28cases perM0/M1normal/san,93tooling,20privateconfig/policy and4privateRuntimecases perM0/M1. Separate scopedreviewPASS. CheckedP3cc1ef324/ELFbf530d15 conditionalfree10624; default090e2182/ELF21b28ee3 free16,8bytes smaller thanD120 not identical. No upload/MCU/physical/grant/gate action. Next P3 3.4 isolated finite turn trial. Evidence P3_drive_test_validation.md.


## D-124 (2026-09-24T07:10:51.912453+04:00, selected under D051/D122) Finite directed P3 turn-trial helper
Context: P3 3.4 needs isolated +/-90 and +/-180 turn trials; existing Turn preserves a RIGHT exact-half-turn tie.
Decision: adopt analysis/P3_turn_trial_contract.md and core/turn_trial.h. Explicit coordinate reflection plus wheel swapping provides LEFT trials without changing Turn, actual imu_ok or raw evidence. One accepted attempt, unchanged700ms turn bound/fallback/tolerance, observed500ms brake interval, permanent safety cancellation and separate primitive/physical outcomes. Add only TURN_TRIAL_BRAKE_MS500 development value and literal registry expectation.
Consequence: independent oracles precede execution; purehelper host/sanitizer/separate review first. No Robot integration/profile/native route, default behavior, existing locked test, B16/pin/grant or hardware evidence changes. Actual runtime trial integration is next; brake interval does not prove settling and DONE does not prove physical accuracy.

## D-125 (2026-09-24T07:19:58.614899+04:00, selected under D051/D122) Isolated actual P3 turn trial
Context: D124 pure helper has passed independent tests/review; P3 3.4 still needs actual application/Gate wiring.
Decision: adopt analysis/P3_turn_integration_contract.md. Compiler-wide exclusive turn profile, config-only +90 development default, actual local DRIVE_TEST release/full hold, one governed turn/brake then inhibition/Lifecycle STOP; full edge escape permanently cancels trial. Exact other signed angles require identified config build, never a remote command.
Consequence: independent new profile M0/M1 safety/oracle checks, checked inert compile-only route and separate review before completion. No original B16, established locked test, pins/grants, motor-run approval, physical metric or human gate changed. Default profile has no trial storage.

D-125 software disposition 2026-09-24T07:33:25.330480+04:00: all8normal host targets, new28-case M0/M1 sanitizer and allfourangle overlays pass. Independentauthor/reviewer corrected only newunaccepted configuredfixture readiness prerequisite; olddraftb90/failure retained, accepted7d6c5193 preserves allassertions/adds readiness guards. Corrected29-case configuredM0/M1normal/sanPASS;36oldlocked unchanged.107tooling+2registry and4privatecases perM0/M1PASS. Actual checkedinert turnsourcefcf43381/ELFf41e2cb7 conditionalfree11424; default5c7df067 ELF/ZSK/loader byte-identicalD123, free16. No MCU action, physical metric or gate. Evidence P3_turn_integration_validation.md; nextfinite3.3stoppingtrial.

## D-126 (2026-09-24T07:35:40.045964+04:00, selected under D051/D122) Finite isolated stopping trial
Context: D125completedf39c9929; P3 3.3 needs independent0.30..0.70straighttrial requests without changing productionSEARCHcap; SC-AN separates reference/peak/rest evidence.
Decision: adopt analysis/P3_stop_trial_contract.md and public core/stop_trial.h. Exclusive compilerprofile, actual Straight/Governor/Gate, conditional final electrical selectedcap, fixed1000msapproach/observed500msbrake, completeescape thenstop, no automaticrepeat. Defaulttrial0.30 and whitelist5values; no B16 change. Retain originalrestmetric and require supplemental measuredcommon-reference peak/R_room beforecap advice.
Consequence: independentneworacles/review and inertcheckedcompile-only preparation;37priorlocked unchanged. No physicaldistance, optimalcap, settling/WCET, pin/sourcegrant, motorpermission or phasegate inferred. No-edge timeout is invalidstoppingevidence.

D-126 software disposition 2026-09-24T07:48:31.258197+04:00: all10normal targets, new30-case M0/M1 sanitizer/all5duty profiles and configured31-case normal/sanitizer PASS first execution;121tooling+2registry PASS. Separate private4cases/36170assertions perM0/M1 and unchanged priorlayouts PASS. Acceptedlocked01213382 now protected;37priorlocked unchanged. Checked stopping9fd0f6ed/ELFb4f15bfe conditionalfree11912; defaultf1d1292d ELF/ZSK/loader exactD125, free16. No MCU action/physical metric/gate. Evidence P3_stop_trial_validation.md; next offlineP3.1countdown analysis.

## D-127 (2026-09-24T07:49:06.959350+04:00, selected under D051/D122) Offline countdown evidence analysis
Context: P3.1 requires fifty recorder-derived starts and exact hold/spread checks; the existing CSV validator establishes format/owner consistency only.
Decision: adopt analysis/P3_countdown_analysis_contract.md. Read-only bounded cohort of up to fifty explicitly identified attempts; unchanged validator plus hash-bound events/summary reread; preserve exact receipt-derived FIRST semantics, wrap handling and original 5.1s/strict5ms thresholds. Conservative qualification requires sealed loss-free owner records and caller-declared closed manifest. Synthetic arithmetic can pass while hardware acceptance remains false.
Consequence: separate spec-derived test author, implementation and read-only reviewer; no firmware, established test, tuning or transport change. Missing physical starts and native dump acceptance remain pending, not generated. Original programmed historical hold must be declared explicitly; unsupported values fail.

D-127 software disposition 2026-09-24T07:58:23.231917+04:00: independentnew33methods plus38existingCSV methods PASS onWSL after one reviewed correction to the new unaccepted fault-injection helper; originals/failures retained. All7private methods PASS WSL andWindows, unchangedproduction1a91b857. Full publicWindows suite remains environment-limited by actualsymlinkcreation privilege; no testskip.38locked and493D126files unchanged. Evidence P3_countdown_analysis_validation.md. No firmware, actualstart, transportacceptance or phasegate inferred.

## D-128 (2026-09-24T07:59:42.088781+04:00, selected under delegatedD051 and explicit hardware-at-end direction) P4 software and reactive profile
Context: D123-D127 complete the identified P3 software preparation (latestc58aeae0). The user explicitly requests continuing until the full project is finished and defers hardware tests; D122 already distinguishes assumed physical prerequisites from actual gates. Original P4 requires SEARCH at GO with reactive combat enabled and openers disabled.
Decision: active software phase advances to P4 while real P3 acceptance remains pending. Adopt analysis/P4_reactive_profile_contract.md: exclusive compile profile, unchanged normal local match-menu admission/fullhold; non-edge GO selects actual SEARCH for one observation, then existing current-perception arbitration/contact/stall/edge paths. No opener runs. Existing selected mode is metadata; no new controls/grants. Public REACTIVE_PROFILE identifies the build.
Consequence: preserve all38establishedlocked tests, default/P3 behavior, B16 values, disabled push-through and fresh run permission. This is software scheduling, not a human GATE P3/P4 or physical measurement. SC-AO exact timing evidence is a subsequent bounded P4 task. P6 eligibility and schedule remain tied to actual gate records.

D-128 software disposition 2026-09-24T08:10:38.176472+04:00: all12normal targets,34-case M0/M1 normal/sanitizer and35configured normal/sanitizer PASS first execution;135tooling+2registry PASS. Separate5-case privateM0/M1 and prior-layout checks PASS. Acceptedlocked0e26c02e now protected;38priorlocked/499frozen sources unchanged. Actual reactive9ddaa2aa/ELF01e39e39 conditionalfree6512; default43d16734 exactD126 ELF/ZSK/loader,free16. No MCU, physical metric or gate. Evidence P4_reactive_profile_validation.md. NextSC-AO bounded P4-only timingevidence; optionsartifact remainsproposal until contract adopted.


## D-129 (2026-09-24T08:14:23.047481+04:00, selected under D051/D128) P4 exact source-to-applied timing evidence
Context: SC-AO; 25Hz frames cannot prove P4.2's 35ms duty-drop bound. Existing D128 reactive profile is complete; current default native memory has no instrumentation margin.
Decision: adopt analysis/P4_timing_evidence_contract.md. Explicit default-off P4-only trace, one candidate per accepted attempt, validated acquisition interval, actual normal loss-brake predicate and full-token matching applied-zero receipt. Conditional code10 metadata and capacity26 preserve legacy option0; exact inert reactive_timing build only. No changes to debounce, motion, source grants, pins, tuning, recorder retention/rate or run permissions.
Consequence: independent spec-derived tests, separate implementation/review, source-bound host/target evidence required. Offline analyzer follows separately. Timestamp evidence describes observed acquisition to output-receipt completion, not physical removal or mechanical rest. Physical P4.2 and human gates remain pending.

D-129 clarification 2026-09-24T10:04:23.773317+04:00: trace source qualification while ARMED/OBSERVING requires the current explicit tick start after the preceding completed epoch, validated by existing S/D/A/C timing plus duration_valid; malformed chronology closes INVALID_SOURCE_TIME without motion changes. Expected loss-receipt rejection remains INVALID_RECEIPT. This makes the adopted source-ownership contract explicit; a source-review gap is being independently reproduced before repair. Codec keeps existing enum-only packEvent versus strict validEventMetadata/appendEvent separation. No established oracle change.

D-129 software disposition 2026-09-24T10:35:07.882427+04:00: IMPLEMENTED/HOST-TESTED; all14normal targets,30-case M0/M1 normal/sanitizer,32-case configured normal/sanitizer,149tooling+2registry PASS. Separate scoped review PASS with no open BLOCKER/MAJOR; one chronology fix retains original failed/unchanged passing repro. New unaccepted tooling syntax oracle corrected independently to actual17compile scenarios; original failure/oracle preserved, no production change for it. All39priorlocked exact; accepted newlocked e384e7fbe3b3ab0123d77b1ef6200c3545d88450e5dc4fa99109b3f33e1296d8 is now protected. Target/native fit pending because board absent; no MCU/physical/gate. Evidence analysis/P4_timing_evidence_validation.md. D130 contract remains separately proposed.

## D-130 (2026-09-24T10:36:36.114838+04:00, selected under D051/D128) Offline target-loss interval analysis
Context: D129 is host-tested/reviewed in f7397d0e; its source-window and matched applied-zero markers need read-only P4.2 evaluation. Physical trials and target qualification remain deferred.
Decision: adopt analysis/P4_loss_analysis_contract.md: at most10explicit attempts, unchanged CSV validator and hash-bound rereads, exact versioned trace grammar, unsigned common-anchor chronology and interval[A-E,A-S] against35000us. Ten qualified intervals determine PASS/FAIL/INDETERMINATE; excluded/missing/lost/M0 evidence cannot satisfy the cohort. Every result keeps hardware/transport/common-attempt acceptance false.
Consequence: independent spec-derived Python tests, separate implementation and fresh-context review; preserve all firmware, prior tools/tests and40locked files. No timing threshold, tuning, board command or gate changes.

D-130 pre-execution clarification 2026-09-24T10:38:14.875246+04:00: whenever both START/GO exist, require their ordinal order and GO release-offset<half-range, including no-trace/header-only records; no separate hold check is invented. Closed loss-free sealed M1 header-only cancellation with positive epoch/go_seen0 is NOT_EXERCISED, while other owner-incomplete conditions retain priority. Reject UNC/network-style URI paths at cohort schema boundary before access. These resolve independent author/implementer questions before oracle freeze/execution.

D-130 software disposition 2026-09-24T10:49:00.951761+04:00: IMPLEMENTED/HOST-TESTED/fresh-context scoped review PASS. Originalsourceb2229370,41-method oracle83d86d6a and fixture33291a25 unchanged;112public(41new+71existing) first-runPASS and13privatePASS. All648prior tracked inputs and40protected files exact. Initial private wrapper-only exit error retained, unchanged rerunexit0; no implementation/oracle fix. No firmware/board/tuning/physical/gate change. See analysis/P4_loss_analysis_validation.md. Next P4.4 bounded push-through contract/integration; default0 remains.

## D-131 (2026-09-24T10:59:34.016882+04:00, selected under D051/D128) Bounded B9.4 push-through
Context: P4.4 requires the original bounded exception before any positive tuning; edge currently rejects positive duration. Separate fresh-context design review found no BLOCKER/MAJOR and clarified stall admission and union fault transitions.
Decision: adopt analysis/P4_push_through_contract.md and visible B9.4 clarification. Prior ATTACK/current confirmed and raw FC; fresh front-white starts one nonrenewable window, deadline<=100ms; spent until actual escape exit/reset. Revoke on eligibility/permission loss, rear/fault/expiry and any qualified unsuppressed stall before limiter side effects. Reuse mutually exclusive episode storage; no new tunable/event/build grant.
Consequence: shipped literal0 and40established protected files remain unchanged. New independent copied-source20/100ms fixtures precede execution, default regressions and fresh review required. No positive tuning, target fit, physical evidence, gate or motor permission inferred.

## D-132 (2026-09-24T11:14:29.730456+04:00, selected under D051/D128) Raw push duration build admission
Context: fresh D131 review identified MAJOR: native -w may suppress overflow before typed duration bounds; host-Werror is not target admission. Default0 unchanged and no unbounded represented duration inferred.
Decision: adopt analysis/P4_push_literal_contract.md; stage validates copied canonical unsigned decimal0..100 before any remote action. Preserve exact shipped configuration/profile flags/source hashes and per-run upload guards. Narrow unsupported source forms fail explicitly; no second tuning source.
Consequence: independent new Python oracles and separate review; only necessary minimal-config fixture declarations may be added without assertion changes. Do not change any prior locked test. Implementation waits for ongoing D131 frozen host matrix to finish. Native compilation/fit, hardware trials and gates remain pending.

D-131 timing-policy clarification 2026-09-24T11:25:40.729640+04:00: first configured20/timing1 sanitizer run passed36of37 M1cases, failing only frozen deferred-white exclusion expectation; M0all37passed. Separate author/reviewer identified ambiguousD131wording versus originalD129actual-escape policy. UnderD051 explicitly extend evidence-only exclusion to admittednonzero line masks whilearmed/observing andotherwiseeligiblefirstarming tick; neverreopenafterblack. Preserveoriginalpolicy/failure, frozenexistingoracle, invalid-source/receiptprecedence andcode8EXCLUDEDformat. Actualmotion/default0unchanged; addindependentfirstarming/no-retry regressions and rerunoldD129safetytests. This is a policyextension, not an oldD129defect or weakenedassertion.

D-131/D-132 checkpoint 2026-09-24T11:41:12.8901108+04:00: positive-only timing exclusion preserves default0 classification;42public/14private M0/M1 sanitizer and old30-case M0/M1 sanitizer pass. D132 explicitly rejects code-level physical-line %: directives after lexical masking, as well as prelexical splices. Its first32-method run has3failed app-layout subcases in1new oracle method; no amendment or acceptance inferred. User paused before independent adjudication. No target, physical result, tuning or gate change.

## D-133 (2026-09-24T12:10:04.9863411+04:00, selected under D051) Historical upload fixture identity
Context: D132's32 new admission methods and12 private methods pass; the wider296-method suite fails80 subcases because historical tests copy changed current sources. The pre-D132 tool reproduces P0 refusal; D118 fails its exact fixture hash before tool use.
Decision: adopt analysis/P4_historical_fixture_contract.md. Restore exact historically approved source inputs only in isolated tests, retaining current production tools, all assertions, source approvals and consumed run records. This narrowly extends D132's fixture-maintenance scope; no production approval changes.
Consequence: independently review hash-bound fixture providers and rerun affected/full regression. Preserve the failed receipts. No physical, target, tuning or human gate claim.

D-131/D-132/D-133 software validation 2026-09-24T12:20:21.6435372+04:00: D131 final firmware remains identical to completed default/positive/configured Runtime and sanitizer checks. D132 corrected32-method admission and12 independent methods PASS; D133 same296-method regression PASS,224.289s, zero failures/errors/skips. Historical fixture repair retains344existing assertion calls, exact approvals and consumed run records. All684D131inputs bound with only6named tooling/fixture/attribute changes; all41protected source files exact. Original failed receipts retained; source config0 unchanged. Final scoped review records disposition separately; target/physical/gates remain pending.


D-131/D-132/D-133 final software disposition 2026-09-24T12:21:47.1876091+04:00: separate-context same-model review PASS, no open scoped BLOCKER/MAJOR/MINOR. Retain native fit/WCET and physical gates as pending. Review state/reviews/P4_push_through_review.md; next P5 software contract proposal only.

## D-134 (2026-09-24T12:23:25.0621783+04:00, selected under D051 and explicit hardware-at-end direction) P5 software and optional-mode availability
Context: P4's identified software tasks are implemented/host-tested/reviewed in39791703; physical gates remain pending. P5 requires optional ARC/WAIT pass or removal, and the future scope cut needs a config-only removal mechanism. All six openers already exist.
Decision: advance active software phase to P5 and adopt analysis/P5_mode_availability_contract.md after separate design review. Two canonical0/1 flags default1; mandatorySIDESTEP/DIRECT; bounded menu skip; direct-entry rejection; stable historical IDs; exact raw admission with explicit pre-feature compatibility. P5.3 follows approvedD034 same-tick normal perception, not an immediate ATTACK exemption. Names are explicit dimensionless availability exceptions to units suffix conventions.
Consequence: preserve all B16 values,41establishedprotected sources, original assertions and run authority. Add only two literal registry expectations. Independent tests from contract/public headers precede execution; separate implementation/review and source-bound validation. No GATE P4/P5, physical measurement, native fit or motor permission; P6 dates unchanged.

D-134 unaccepted draft-oracle correction 2026-09-24T12:45:38.5977130+04:00: first focused20-case run has19PASS/1FAIL perM0/M1, solely the newly authored edge-preemption case's universal zero-duty assumption. Independent author and reviewer confirm B4.2/D021 moving masks4/8/12 forward and5/10 pivot; brake1/2/3/6/9 and inhibited-fault7/11/13/14/15. Original new draft remains in425c8a97 with exact failed receipts; it has never passed or been accepted as established coverage. Correct only this new case to existing human-approved B4/D021/D048/D020 semantics: retain loops/first-observation state/mask/contact, zero for brake/fault, exact fault/permission, immediate B6-bounded row-consistent motion and settled literal vector at+40000us, actual M1 PWM/receipt and M0zero. No firmware, prior41protected file, protected behavior or previous accepted assertion is changed. This corrects an invented draft expectation; it does not authorize changing established locked tests.


D-134 private-probe setup correction 2026-09-24T12:53:13.0971150+04:00: focused public20cases pass in M0/M1 after independently reviewed draft B4 correction. Private firstM0 passes5/6, failing the stale-snapshot case because it supplies no observation in B3's final300ms window. Separate spec-only author confirms this precondition error. Preserve original private source/freeze and failure; correct stimulus only to capture confirmedFC at5.000/5.001s, start raw replacement at5.060s, and complete clearing/current qualification atGO5.100s. Add explicit snapshot/current/GO preconditions; retain every original routing/contact/cap assertion. Production and all41 established protected sources unchanged. Broader296tooling PASS132.531s; fullhost/matrix pending.

D-134 build integration repair 2026-09-24T13:03:36.9430756+04:00: full18 retry failed beforeCTest because an earlier D131 timing-only test source was assigned to ordinarypush timing0 targets. Independent author/reviewer approve moving that unchanged source to existing timing_evidence M0/M1 targets; all18targets and assertions retained. Fullregression nowrunning; positive20/configuredsanitizer supplementalcoverage mustrun wholepush familyunderTIMING1 plus5D131 timing-family cases, while oldD129completecoverage remainsat0. EarlierP4fullpasspredatedtheaddition and is notfinal-sourceproof; historicalreports corrected without rewritingreceipts. No production/lockedtest change.

## D-135 (2026-09-24T13:03:36.9430756+04:00, selected under D051 within active P5) Qualified opener-abort evidence
Context: P5.3 one-tick acceptance cannot be measured by25Hzframes or60fpsvideo. Reviewed proposal4dc72ac1/c6314c04 resolves cause/phase, sourceepoch and actual appliedreceipt distinctions; D134frozenregression isstillrunning.
Decision: adopt analysis/P5_abort_evidence_contract.md for bounded softwarepreparation: separate opt-in P5profile, actualpredicatepulse plusindependentrouteobservation, same-observation handover and conservativeA-D<=TICK_US, existingPending fulltoken/epochownership, EventBatch21 with explicitlossdisqualification. M1disabledEN rejects inproducer; wireendpoints andproducer-only chronology remainseparate claims.
Consequence: spec-onlytestdraftpreparation canproceedindependently; no production/header/build changes untilD134frozenvalidationends. Default/P4behavior/storage andallprotectedassertions remainunchanged. Actualtargetfit mayfail givenhistorical16byteheadroom; no memorycut, nativefit, physical10/10trial, deploymentauthority or gate isassumed.

D-134 final host disposition 2026-09-24T15:22:18.031850+04:00: all18 ordinary targets, four availability-pair ASan/UBSan matrices with20public+6private cases perM0/M1, positive20 supplement37push+5D131 timing cases perM,60admission+296regression+8privatePython PASS. Separate-context same-model scoped review PASS/no open findings. Frozen649 inputs and41prior protected files exact. New locked safety source 901b735c69f13def646b033539121e55f289035e5a6ee206dbb9ffa1802d63b0 accepted and now protected; no existing protected assertion amended. Original failed builds/oracles and corrected historical P4 claim remain retained. D135 production may proceed after exact native staging; no physical/human gate inferred.

D-135 first unaccepted draft-oracle adjudication 2026-09-24T15:32:56.340156+04:00: firstpublicM0 37/40 andM1 33/40; separate spec-only author and source reviewer independently account all42failedassertions:20STOPPED-fault assertions,4pushed-out diagonal assertions,18global-ordinal0APPLIED assertions. Approve narrownewdraft corrections to match D075STOPPEDreceipt, D049actual-applied pushed-out priority and D135receipt-before-current-event chronology, retaining exactinhibit/PWM/token/row/slew/timing checks. Originalb0540500/firstimplementation2d924f1f andfailedreceipts retained. No production or42existingprotected file change; newlockedcandidate hasnotbeen accepted. Equivalent ordinalassumptions in unexecutednew Runtime cases correctedconsistently.

D-135 private draft correction 2026-09-24T15:38:17.280582+04:00: exactfirstprivateM1failure is sameglobalordinal0APPLIED assumption alreadyadjudicated fornewpublictests. Preserve private_spec_probes_first.cc/freeze_first.json/run_private_first.py and normal_retry1private receipt. Correct onlythatcase toallow exactprevious FIRST_NONZERO receiptprefix (fulltoken/EN/time/mask/quantizedduty checked), thenuniqueAPPLIEDbeforeanycurrentevent; other12cases unchanged. No production/publicor42existingprotected change. Originalprivatefrozen06a74b56; correctedf9eb1025.

## D-136 (2026-09-24T15:45:14.8925240+04:00, selected under D051 within active P5) Offline qualified-abort analysis
Context: D135 profile compiles and its public40-case M0/M1 tests pass; broader frozen matrix continues. P5.3 needs source-bound logical analysis without fabricating physical acceptance. Separate design review closes all three MINOR findings against draftfea16ebd.
Decision: adopt all five choices in analysis/P5_abort_analysis_contract.md: byte-verified historical seven-literal config plus declared source/profile matching, narrow canonical input syntax, explicit HANDOVER_FAILED evaluated failure, precise missing/header/GO/read chronology, and reported-origin eligibility with all acceptance booleans false. Reuse unchanged CSV validator and D130 public pattern; no shared framework or firmware change.
Consequence: independent public/private oracle drafts freeze before companion execution. No src/tools/tests change until D135 frozen validation completes. Default native-fit, physical10/10, transport, producer-only guarantees and human gates remain separate. Review reviews/P5_abort_analysis_draft_review.md.
D-136 public-interface clarification 2026-09-24T15:46:36.7322666+04:00: adopt pure decode_cue(value,mode) returning exact five-field cue orNone for invalid/mismatched metadata; reject bool/noninteger/range errors. This supports independent65536-value table checking without repeated filesystem cohorts; representative complete-cohort checks remain. No firmware/currentconfig access or extra behavior.
D-136 pre-freeze clarification 2026-09-24T15:49:29.8637472+04:00: terminal_detail/value retain completed20/1,25/state or excluded diagnostic pair, null for unfinished/no trace; handover_state records either19or25 actualstate. Config uniqueness concerns canonical declarations; ordinary unconditional uses (actual LOG_FRAME_WINDOW_MS/LOG_HZ derived frame count) are allowed, while conditional/macro mentions stay unsupported. No existing producer/validator/test change.
