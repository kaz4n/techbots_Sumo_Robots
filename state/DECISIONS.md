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
D-136 pre-execution inherited-schema clarification 2026-09-24T15:53:55.1092984+04:00: absent manifest or validunknown/open closure isINCOMPLETE; a suppliedmanifest null/missing requiredclosure staysINVALID through unchangedD074. Aggregateincomplete without detailedloss retains validator consistencyINVALID. This clarifies existing validator-first precedence, not a schema change.

D-135 final software disposition 2026-09-24T15:59:01.2251070+04:00: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/independent scoped reviewPASS with noopenfindings. Full20targets; normal40/configured42public+13private perM0/M1, normal+ASan/UBSan;18new+74admission+296regression;72legacy layoutpairs and8isolatedfaults PASS. All656 frozeninputs/42priorprotected exact. Newlocked e9fd2cf062b57550ae24b678c3bcc6f0983ff2ce15069028fba9008e711df56e accepted/protected. Nativeinertprofile1328B conditionalfit; fullappdeficit/liveload/WCET/physical/humangates remainseparate. Originalfailures retained. Frozenvalidationends; D136offlineimplementationeligibleafteroraclefreeze.

D-136 new private-harness adjudication 2026-09-24T21:53:54.631188+04:00: original test16 patched a separately imported module instead of the analyzer actual unchanged CSV dependency; callback count0 proved no stimulus injection. Separate reviewer preserved original probe/freeze/failure before narrow test16-only seam correction, retaining all assertions and adding dependency-file identity. Root inspected exact diff and reran unchanged firstsource9891: all19private PASSexit0 in2.469s. No existing established test or production changed. New independent8-method declarations suite reproduces genuine production admission defect (141 failing subcases), retained in d0169983; fix remains pending.

D-136 final software disposition 2026-09-24T22:14:55.246824+04:00: finalsource8e002c6f/5277dec0 passes93public (including65536cuewords),19private and previously112unchanged-dependency regressions. Separate same-model scoped source/receipt reviewPASS/no openfindings; all694priorinputs/43protected exact. Added19spec-derived public methods preserve first declaration/source-read failures; no establishedtest weakened. Original19private failure was independently corrected onlyatnewtest16 actualdependency injection, allassertions retained. Single-directory discovery fixes archive/import collision withouttestchanges. Literal configuration admission remainsfinite, notgeneralC++validation; hardware/producer/transport/physical/gate acceptance remainsfalse. Evidence analysis/P5_abort_analysis_validation.md and reviews/P5_abort_analysis_review.md.


## D-137 (2026-09-24T22:17:20.531829+04:00, selected under D051/D075/D122 and continued software-first direction) P7 operator-document preparation
Context: P5 D134/D135/D136 software and scoped reviews are complete (d6a8319e/70c964a7/0faf2e6d); real physical acceptance and human gates remain pending. The user requests continued work with the bare UNO Q and prompt commits. P6 remains conditional on an actual P4 gate by30September and the stronger28September scope cut.
Decision: make P7 software-document preparation the single active work stream, limited to original7.2/7.4 runbook, mode card, inventory and blank7.3 rehearsal/scouting records. Correct7.1's build example to --match --compile-only as explicitly required by the takeover instruction. Preserve actual source limitations (empty SetupGrants, unconfigured physical button windows, unqualified release/rearm/dump/display paths) and mark the documents draft pending operational acceptance. This scheduling decision does not close P5 or activate P6.
Consequence: no firmware/config/locked-test change, target build, upload/run, fabricated measurement, printed-copy claim, release tag, rehearsal result or human gate. Separate read-only document review and local link/command checks precede closure. Actual P7 freeze/release/rehearsal and all prior physical criteria remain pending; no additional hardware is requested now.

D-137 software-document disposition 2026-09-24T22:23:40.901462+04:00: original7.2/7.4 drafts and blank7.3 rehearsal/scouting records complete; separate reused-context same-model scopedreviewPASS/noopenfindings.52local links/9fragments,43protected hashes, originalPROGRESSprefix andno src/host/tests/tools difffrom0faf verified. Per-run authorization/tagcondition drafts corrected before review. SC-AP explicitly preserves unresolved READY/battery-on-matrix criterion plus fullrearm/capture qualification; no external-meter substitution accepted. No new firmware/tests/tuning/build/board action, printing, physicalresult, release tag, P6eligibility orhuman gate. Evidence analysis/P7_software_acceptance_packet.md and reviews/P7_operator_docs_review.md.


## D-138 (2026-09-24T22:39:49.314109+04:00, selected under D051/software-first direction within P7) Actual informational pre-start status
Context: D137 operator preparation exposed SC-AP, but current-source audit identifies a host-implementable projection gap independent of physical qualification. D088's coarse bar straddles VBAT_WARN_V and the mode glyph does not distinguish start readiness. Initial design review identified D087 initial-neutral qualification is not current Buttons rearming; that MAJOR was resolved before adoption.
Decision: adopt analysis/P7_readiness_contract.md SHA568bc277 after separate designreviewPASS5bc6f928. Observe existing actual button arming and START admission without changing control; Runtime pairs current genuine zero/disabled Gate context; bound IDLE views add live blinking R and an exact threshold pixel. Preserve default-unbound pixels, all established tests and current grants. R is the explicit proposed READY symbol and conservative all-clear snapshot, not countdown READY, physical acceptance, future health or motor permission.
Consequence: independent fresh-context tests freeze before implementation execution; actual Runtime M0/M1/configured tests, focused sanitizer/fullhost and source-bound target/layout qualification required. Only existing source metadata/display work, no new configuration, pin, grant, profile, transport or deployment authority. Terminal stale-frame, native MATCH/Immediate matrix ownership, calibrated voltage, rearm/dump and human gates remain pending. This supersedes D137's blanket no-further-host-task next action only for this concrete originalP7.2 software deficiency.

D-138 new draft compile correction 2026-09-24T22:51:37.784414+04:00: first build failed before test execution because whole-Guard memset violates class-memaccess/Werror. Separate spec-only author and reviewer approve only three typed bounded array fills retaining0xa5, all assertions/stimuli/cases. Originalac109bab/freeze/failedreceipt preserved in d19f8964; correctedc007ff8e installed byte-exact. No production or43established protected test change.

D-138 second independent draft compile issue 2026-09-24T22:54:30.278769+04:00: configured_first exits2 beforeexecution on doctest decomposition of3-term CHECKdisjunction. Separateauthor/reviewer approve only enclosingcompleteexpression inparentheses; e0714344 retainsalloperands/assertions/stimuli. Originale13f301/freeze/failure retained. Normal20caseM0/M1 alreadyPASS; no firmware/establishedtest change. This is separatefromcorrectedGuard warning; no failedproductionfixattempt.

D-138 new unaccepted Runtime-oracle adjudication 2026-09-24T23:02:08.560265+04:00: configured_retry1 executes31cases perM0/M1,30PASS/1FAIL each (sole !low_battery assertion). Spec-onlyauthor and separate source reviewer agree existingP1contract/B14 and establishedrobot/power tests require immediatewarning on validbelowthresholdIDLEsample; the1sfilter belongs onlytogovernor compensation. Adoptnewcase-onlyrename, CHECK(low_battery), explicitIDLE/validvoltage/raw9000 preconditions while retainingmarker3/noR/zero/no-motion. Pure synthetic renderer tests retain contradictorywarning/voltage independence checks. Originale0714344/failure preserved; no production,43protected or establishedassertion changed. Correctionstaysinsideconfigured-onlyregion; fullordinary683inputmatrix runningbeforeinstallation.

D-138 final software disposition 2026-09-24T23:13:03.869573+04:00: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh-context same-model scopedreviewPASSbe80b5ad/noopenfindings. Full22targets; ordinary20 andconfigured29public+2private perM0/M1, normal+ASanUBSanPASS; configured-onlyoracle correction leavesordinarypreprocessedtranslations byte-identical. Final687inputs/43protected and82links9fragmentsPASS. ExactMATCHsourcefcddbd8e/ELFcb5fbb53 conditional261280Bpeak/864Bspan,62imports,16ABI/72offset matches. Originalnewdraftcompiler/assumptionfailuresretained; no firmwarefix/establishedtestweakening. SC-APnative/physical/rearm/dump, defaultfit, liveRAM/stack/WCET andhumangatesremainpending. Nexteligibleoriginaltask isunchangedcurrentdefaultM0 qualificationperremaining-scopeaudit, notblindcontinuationofoldfailedcandidates.

## D-139 (2026-09-24T23:14:41.007952+04:00, selected under D051/software-first direction within P7) Current default-app qualification
Context: D138 closes in e16e6a57 with host/sanitizer/review and conditional MATCH fit. Independent original-scope audit identifies current default/M0 full-app target fit as unfinished software qualification. D13432B deficit and two failed24/32B isolated repairs describe older sources; neither was adopted. The old optimization loop remains stopped.
Decision: authorize one unchanged-current-source checked default-startup MATCH0/MOTORS_ALLOWED0 compile-only baseline, single compiler job, then exact source/loader/import/layout account. No optimization candidate, upload/reset, capacity/feature cut, config/test change or new physical assertion is authorized by this baseline decision. Preserve all current build-policy/toolchain checks and failures. Any subsequent repair needs a separate bounded reviewed proposal.
Staging constraint: automatic review rejected deletion of existing build/stage/app. Leave it intact. A narrowly scoped read-only reuse adapter is permitted only after separate review and controlled tests prove exact source/stage sets, hashes and digest, existing source/path/config validation, failure on drift, and no call to original destructive staging or deletion. No fallback or retry may erase that path. Reusing verified unchanged bytes is not permission to bypass a denied action.
Consequence: native worker owns new P7_default_qualification_raw/plan/validation only; root owns decisions and final disposition, separate reviewer remains read-only. This is an original release prerequisite in activeP7, not a physical gate or continuation of the rejected two-candidate optimization. No additional hardware is requested. Compilation waits for adapter review and tests.

D-139 pre-execution identity clarification 2026-09-24T23:20:31.8473521+04:00: separate review found that mutually consistent replacement source, stage and caller-supplied manifests could otherwise pass fixed counts. Pin the authorized staged source digest fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2 in the adapter and both manifest byte hashes in the one-run wrapper. Preserve the initial drafts. Public controlled tests may substitute a synthetic authorized digest only inside isolated RAM fixtures, must separately assert the real literal, and must reject coherent source/stage/manifest drift. No helper execution or native compile precedes independent frozen tests and separate review. This refines the existing unchanged-source authorization; production and tool policy stay unchanged.

D-139 negative baseline checkpoint 2026-09-24T23:31:08.808641+04:00: the single unchanged-source compiler passed, but the initial conditional loader model has a592-byte deficit. Complete exact negative evidence and review under D139. A bounded read-only explorer may identify one behavior-preserving repair with concrete artifact/source basis while that evidence finishes; this does not authorize implementation or another compile. Preserve all features, capacities, defaults, toolchain, flags, source grants and tests. Neither old failed candidate is adopted or restarted. A concrete subsequent proposal requires separate review and a new scoped decision.

D-139 final disposition 2026-09-24T23:38:12.327347+04:00: qualification task is complete with TARGET-COMPILED / CONDITIONAL-FIT-FAIL. Separate same-model review6321c944 accepts evidence while retaining one592-byte release-fit BLOCKER; this is not a passed phase or ready image. Original validator exit1, first-allocation576B shortfall and full592B hypothetical deficit are preserved. All61 imports resolve and16 layouts/79 old offsets match. Source/metadata inspection found no defensible single repair; current -Os/gc-sections already apply. The pinned package exposes a distinct Static linking mode, currently unsupported by project admission. Permit read-only primary-source investigation only; any probe/policy implementation needs a concrete separate reviewed scope. No existing policy check, capacity, feature, test or run permission is relaxed.

## D-140 (2026-09-24T23:40:52.370501+04:00, selected under D051 within active P7) Static-link feasibility source qualification
Context: D139 completed in28faccc9 with a592-byte dynamic-loader deficit; no defensible single source repair was identified and current recipes already use -Os/gc-sections. The pinned UNO Q core exposes Static linking, and retained loader source branches directly to its entry point before dynamic LLEXT loading. Exact placement, packaging and allocator/native-address compatibility are not yet qualified.
Decision: perform a bounded read-only primary-source audit, including compact collection of exact installed static scripts/wrappers, packaged-loader file disassembly and three packaging-tool identities/build provenance. Keep official downloaded sources separate from installed observations. The existing production policy remains dynamic-only. No compile, expanded-property build, policy/source/config/test change, upload/reset, target/inferior, motor run or denied-cleanup retry is authorized by this source-audit decision.
Consequence: native collector owns research_raw/source note only; coordinator owns separate official-source folder and ledgers; reviewer remains read-only apart from its findings. If the source audit supports a concrete inert compile-only feasibility proposal, separately review its exact commands, input identities, static bounds/package checks and negative tests before any implementation or compiler invocation. Static fit/runtime compatibility remain unknown; D139's negative result and all human/physical gates remain unchanged.

D-140 final source-audit disposition 2026-09-24T23:47:08.429572+04:00: exact installed linker scripts and packaged-file dispatch/allocator evidence support drafting a distinct static/M0 compile-only proposal. Separate review6d3ab597 found no source-packet defect. Linked code skips dynamic LLEXT loading; static writable region ends at0x20053890 and packaged libc arena starts there. Required actual image bounds/bindings/initialization/flat packaging remain unknown. Three official tool sources were obtained from the actual monorepo at embedded VCS revisions; module paths alone did not establish repository URLs. No policy/source/test/compile/run changed. Draft D141 experiment belongs under its scoped evidence directory rather than a new general-purpose tool; interfaces, complete static expectations and independent tests must be reviewed before any adoption or execution.


## D-141 (2026-09-25T00:05:46.246440+04:00, selected under D051 within active P7) Fixed static-policy host component
Context: D140 source qualification is complete in 6e6fe21c; e5c20fed closes the two initial proposal findings. A separate fresh-context reviewer independently reconstructed all 84 fixed static command properties and verified eight additive pins, preserving all 18 production pins. The remaining full probe needs artifact/runner interfaces, negative tests and exact-code review. No static compilation is authorized.
Decision: adopt only the Fixed public policy interfaces section of analysis/P7_static_link_probe_contract.md (current SHA256 d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae) for implementation and host tests. Freeze the separate spec-derived policy oracle before execution. Admit one literal static/M0/wait/app profile, exact properties and reviewed reference bytes; reject malformed JSON, all nonfinite numbers, drift and external compile libraries. All production admission and sources remain unchanged. Record upload.extension=bin-zsk.bin as fixed metadata, without any upload interface.
Consequence: only the scoped static_policy.py and small host evidence may be added after oracle freeze. No target properties query, compiler, artifact/runner implementation, dynamic-policy relaxation, source/config/test change, capacity cut, upload/reset, runtime result or phase gate is implied. Completing this host component leaves the full static feasibility probe pending its own remaining review and authorization. The 592-byte dynamic default deficit remains unchanged.

D-141 policy-only host disposition 2026-09-25T00:15:12.102192+04:00: final source ec3d8a5e passes35 independently frozen methods and the unchanged4-case private reproducer. Separate same-model code review8fe8726a closes one MAJOR path substitution defect and reports no open findings. First source49389784/commit92d9bb8b, original27-pass receipt, private0/4 failure and independent supplemental failure are retained. One single-pass substitution repair; no established assertion changed. All8 oracle inputs and production policy/reference/pins remain exact. HOST-TESTED only; full artifact/runner scope, target query/compiler, static fit/runtime and human gates remain pending. Preserve frozen policy contract; define remaining interfaces in a companion scope.


## D-142 (2026-09-25, selected under D051 within active P7) Static artifact structural host component
Context: D141 pure policy passes independent host tests and scoped review; D139's592-byte dynamic deficit remains. Separate reused-context same-model design review reports no open findings on the companion artifact contract b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54. Pinned scripts/packager and official ELF/Arm documentation support the derived expectations, not an observed static app.
Decision: adopt only analysis/P7_static_artifact_contract.md for a pure standard-library host parser in the existing scoped raw directory. Accept exact EABI5/hard-float0x05000400, named allocations, segment/LMA mapping, initialization bounds and both packaging forms; conservative unsupported structures stop this experiment rather than trigger changed linker flags. Code writing may proceed independently alongside the separate spec-only test author; no implementation import/execution precedes the independent fixture/oracle freeze. Do not edit existing policy or protected tests. Maximum input/name/symbol counts are host parsing limits, not firmware capacity changes.
Consequence: only STATIC_LAYOUT_PACKAGE_PASS is possible from this component. Source/run freshness, actual entry/constructor/native binding/ABI audit, full runner adoption, query/compiler, loading/runtime and gates remain separate. No firmware/config change, upload/reset or motor permission. Preserve first failures; separate code review and scoped host tests are required before this component closes. The full parent-contract probe remains unadopted.

D-142 final host disposition 2026-09-25T00:40:30.855361+04:00: repaired source d30372dd/9f79bf41 passes45 independent public methods and6 unchanged private methods; separate reused-context same-model code review305c87e2 PASS/no open findings. Original50d06722/a986ffdb retained; later private reproduction gives18 failing negative subcases with3 positive methods still passing. One pre-execution patch closes empty-allocation/full-entry comparison gaps, no oracle amended or weakened. All11 public frozen inputs exact. IMPLEMENTED/HOST-TESTED only: no static compiler, fit, native binding/ABI/runtime result or full-probe adoption. Next remaining task is one-shot runner interface/command binding and independent negatives under a separate scope.

## D-143 (2026-09-25T01:04:43.817769+04:00, selected under D051 within active P7) One-shot static probe host tooling
Context: D141/D142 pure policy/artifact components are host-tested; D139 default dynamic fit remains592B short. Separate reused-context same-model design review15eadc42 closes command-size, process-inventory and ADB completion-boundary findings without changing production admission.
Decision: adopt only host implementation and independent tests of analysis/P7_static_runner_contract.md (35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7) and analysis/P7_static_remote_contract_draft.md (a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39), with exact bootstrap templatea6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419. Implement scoped run_static_probe.py and static_remote.py only; reuse reviewed fixed inputs and unchanged validators. One fixed inert/static/default app configuration, one query/compile dispatch each, no upload/reset/deletion. Nonzero ADB or uncertain compile completion stops remote actions and preserves original failure. No validator replacement or fixture substitution can prove target execution.
Consequence: independent spec-derived tests may be written alongside code, then frozen before any new implementation execution. Separate code review and real host checks precede a later source-bound native GO. Do not modify frozen prior contracts/oracles, firmware/config, production build policy, existing tests or capacities. Structural collection is not native entry/ABI/runtime proof or a human gate. No board command is authorized by this host-only adoption.

D-143 pre-execution clarifications 2026-09-25T01:13:43.547866+04:00: public main uses standard nonzero CLI return on runtime/admission failure; run_probe retains exceptions. A missing process record is ignored only for a confirmed departed PID. Direct module loads bind captured source, with nested unchanged-loader cache/source guards and python-B invocation. See analysis/P7_static_runner_implementation_notes.md; no existing contract/test altered. Separate inspection found two helper failure-path gaps in first fa209bee source before any execution; preserve it then repair bounded paths.

D-143 first-host adjudication 2026-09-25T01:21:05.083685+04:00: originalrunner006fdb70/helper521773e5 and freezes047d6576 retained. Runner21/22, bootstrap23/23, helper27/28. Independentauthor/reviewer agree inputs.json exclusion is a new-oracle overconstraint: correct only exactdirectoryset to include this required compact provenance and add exact metadata assertions, retaining otherchecks. Helperinode replacement already rejects; adopt narrower SOURCE_DRIFT classification for positive source identity changes per separate review, preserve othererrors and unchangedhelperoracle. See implementation_notes and originalreceipts; no established/locked test change, boardcommand or gate.

D-143 finalhost disposition 2026-09-25T01:26:57.645290+04:00: finalrunner983e86d7/helper8ba9b190 pass80 independent methods (22+2runner,28+5helper,23bootstrap). Separate same-model source/receipt reviews close allfindings; helperreview freshcontext, runnerreview reusedcontext. Originalfirstfailures047d6576/5fc7c2d9 retained; only independentlyadjudicated newrunner-oracle metadata correction, unchangedhelperoracle and diagnostic refinement. All687 prior inputs/17pins/legacyprogressprefix exact. No boardcommand or staticartifact/runtime/gate claim. See analysis/P7_static_runner_validation.md/root_receipt.json. Nextreview minimalnativeinvocation before separate source-boundGO.

## D-144 (2026-09-25T01:28:22.454675+04:00, selected under D051 within active P7) One source-bound static compile-only experiment
Context: D143 closes in5e953b8e with80 independent host methods and scopedreviewsPASS; literal invocation plane2834aa0 separately reviewed145d7fcf with no openfindings. Currentdefault dynamic fit remains592B short.
Decision: coordinator GO for one guarded native invocation of reviewed runner983e86d7/helper8ba9b190 on bareUNOQ ADB2629958581, current sourcefcddbd8e, static/default/MATCH0/MOTORS_ALLOWED0. Create exact missing runs parent after ancestry checks; retain unique run/launcher receipts. Use the exact reviewed plan, transient environment, unchangedmain/transport/policy/stage, maximum one expandedproperties query and onejobs1 compile. No upload/reset/run/deletion/retry. Any failed or unknown result is retained and ends this experiment; further repair/diagnosis requires separately scoped direction.
Consequence: only actual observed command/results may be claimed. Collection success still needs parent-contract read-only entry/constructor/nativebinding/ABI audit; no static adoption, runtime/motor permission, physical acceptance, release tag or human gate. Source/tool drift rejects before dependentwork.

D-144 terminal disposition 2026-09-25T01:35:17.972285+04:00: one query/compile returned0 on bareUNOQ, runf0220228320c4b2aa20c3e5e8264c813; static artifact metadata stable but D142layout exits2 LAYOUT_REJECTED unsupported symbol encoding. RunnerFAILED/layout, allindependentpostchecksPASS, launcherexit1/sourcehashesunchanged.25commands terminal; no ELFtransfer/retry/upload/reset. GOconsumed. Keep negativeevidence and frozenparser/contract; nextrequires separatelyscopedread-only inspection of existing170616B ELF5cc2dfde, not guessedtype/admissionrelaxation. No staticfit/runtime/release/gate acceptance.

## D-145 (2026-09-25T01:40:34.028033+04:00, selected under D051 within active P7) Read-only diagnosis of rejected static ELF
Context: previousgoalturnmadeprogress: D14380hostmethods passed and D144compiled currentinertstatic source but rejected symbolencoding. Nativeexperiment1e35b70e isterminal anditsGOconsumed; noretry. Separatecompositionreviewf50620b5 closes entrypoint-admission and removable-assert findings against plan5f52f306.
Decision: coordinatorGO for one exactread_elf invocation composedfromunchangedrunner983e86d7/helper8ba9b190, using pinnedD1440001/0009/0021receipts andcurrentboot/directory/file identitychecks. Retrieveonly170616B ELF5cc2dfde into freshlocaldiagnosis-v1, with actualreadreceipt andlocalafterchecks. ExactADB admission andexclusivepathguards remain; zeroquery/compile/upload/reset/delete actions. Then perform localread-onlysymbol inspection and primarysource research toidentifyactualencoding.
Consequence: DIAGNOSTIC_ELF_COLLECTED proves byteidentity only, not structural/native/runtimeacceptance. PreserveD142contract/parser/oracles, productionpolicy andD144negativeevidence. Anyadmission amendment needsseparately reviewed evidence-backed scope andindependenttests; no automaticretry/rebuild.

D-145 terminal disposition 2026-09-25T01:47:55.543075+04:00: one checkedexistingELF readexit0, query/compile0, no postcheckerrors; exact170616B/5cc2dfde collected. Independentstruct/readelf identify2242symbols/sixGLOBALdefaultABS TLS6,size0. Fresh-contextsame-model scopedreviewPASS/noopenfindings independentlybinds17pins/103sources/102stage/25originalD144receipts. OfficialArduino TLSassemblygeneration is consistent, installedassembly/object anduse remainunproved. No parser/oracle/productionchange, retry/upload/reset. D144negativeunchanged; D145readconsumed. Next separatelyscoped installedtls-syms.S/map/object read-onlyevidence beforeanyadmissionproposal.


## D-146 (2026-09-25T01:53:37.269853+04:00, coordinator selection under D051 within P7) Existing TLS provenance inspection
Context: the previous goal turn made verified progress in61fc3795: D145 identified six unadmitted TLS symbols, with original D144 rejection preserved. Official generation and local direct-reference observations do not prove actual installed/input provenance. Separate fresh-context composition review d07b37cf has no open material findings.
Decision: authorize one exact read-only collection using reviewed collector2443cedc and remote48ca3cdf, hash-checked before execution. Reuse unchanged D143 descriptor/claim/pin/postcheck functions, read installed TLS assembly and exact existing map/debug/temp artifacts, and the fixed TLS object only if named in that map. No alternative-path search, query/compiler/upload/reset, remote writes or retry. Then inspect returned bytes locally; unresolved object status stays explicit.
Consequence: diagnostic byte/provenance evidence only. Preserve D142 validator/contracts/oracles and D144 negative; any later admission amendment needs separately reviewed scope and independent tests. No source/config/behavior, runtime, physical or human-gate acceptance follows.

D-146 disposition 2026-09-25T01:57:12.617230+04:00: one read-only collection exit0, no query/compiler/upload/reset/retry. Exact installed TLS source68bb1476 is bound to checked loader39d4a4fd; map15da1417 LOADs objectbf3b5c57. Object/debug/final have identical six size0 GLOBAL/default/ABS TLS6 constants; object adds no allocation/relocation, map has no actual tdata/tbss input and discards the accessor wrapper. Separate collection review and independent local analysis pass. D144 rejection and frozen parser/oracles remain. A narrow structural extension is now evidence-supported but not yet adopted; entry/native ABI/runtime/physical gates still pending.


## D-147 (2026-09-25T01:59:34.545921+04:00, selected under D051 within P7) Exact inherited TLS structural extension
Context: D1469ee2d559 establishes installed assembly/object/map provenance for six size0 absolute TLS aliases; the frozen D142 parser rejects their type. Separate reused-context design review 4f6e358742929aca9a57ef0b3f1c4124a7a619c30ae0a1179bcdd7a2b5f32943 passes contract588e1ad8 with no open material findings.
Decision: adopt only the new pure host interface in analysis/P7_static_native_tls_contract.md. Require exact assembly and frozen-validator byte hashes, all six exact tuples once in each ELF form, all unchanged D142 layout/package rules and a distinct extended result status. Reuse the frozen validator in a fresh private namespace; preserve its source, contracts, original tests, D144 rejection and all consumers. Independent spec-derived tests freeze before first implementation execution; separate code/receipt review follows.
Consequence: this is evidence-backed interpretation of inherited ELF metadata, not arbitrary TLS support or source/runtime qualification. No consumer integration, board command, compiler/upload/reset, firmware/config/behavior change, locked-test amendment, native ABI/free-RAM/WCET claim or physical/human gate. Later native validation/integration requires separate scope.

D-147 final host disposition 2026-09-25T02:05:56.567390+04:00: IMPLEMENTED/HOST-TESTED, first sourcecd52a29a unchanged. Independent19 methods and original39+6+6 regressions all PASS (70total);10 source/oracle pins exact, frozen tests precede execution. Separate fresh-context code/receipt reviewdc7156b3 has no open findings. Initial private CLI exit2 (missing --source-ref) is preserved; corrected command passed with no test/source change. No native artifact acceptance, consumer integration, compiler/upload/reset or physical gate. Next separately scoped read-only existing-packet validation under the distinct new interface.


## D-148 (2026-09-25T02:16:39.990665+04:00, coordinator selection under D051 within P7) Existing native packet structural validation
Context: D14716d95b4e passes70 host methods and fresh-context review; original D144 rejection remains. Fresh-context same-model composition review960a693ffce8741b8b43637be60bfc58e7229e205dfc286e209b87033b027993 passes after two receipt-only repairs, with six in-memory finalization scenarios passing. Original glue1359fcab/preflight preserved in8e3c4348.
Decision: authorize one execution of analysis/P7_static_native_actual_plan.md (a0169e7405a5550fca8828ba4cd43b7f1387e015b92f980c6d1964707dd828e4), exact hostfbde292662d3c183097ac5956a51efc23dedc6067a778e0ada81c9a24dbe7a32 and remotec6099f6d29ebdc400df5280032a8b5b0d229a003c594033a920f459316e2b8e7. Five intended read-only commands bind installed/source state before and after one D147 validation of existing D144 seven artifacts and export. Preserve original Claim/FileRecords, all frozen dependencies, first failure and independent postchecks; no automatic retry. Hash-check captured launcher source before execution and after. Local command preparation28859UTF16units/zero dispatches passes.
Consequence: only distinct native structure/package evidence is possible. No rebuild/query/upload/reset/remote mutation, production integration, source/config/test change, native entry/ABI/runtime qualification or physical/human gate. Original negative evidence stays unchanged. Existing local entry/constructor inspection may proceed independently; retain compact receipts rather than duplicate binaries.

D-148 terminal disposition 2026-09-25T02:19:12.339568+04:00: all5 read-only commands exit0, query/compile0, no stderr/postcheckerrors. Distinct native structural report PASS for unchangedD144 seven-artifact packet;103sources/102stage/17localpins/26installedpins and originalClaim/FileRecords bindsourcefcddbd8e. Flash93080B/staticRAMspan167792B/configuredregiontail94352B; tail is not liveRAM. Reused same-model actualreview12cbec6b PASS; all27 originalD144JSON records preserved. No binaries downloaded, firmware/production/test change, upload/reset/staticadoption/runtime/humangate. D148 consumed; next localentry and separate nativebinding/ABI audit.


## D-149 (2026-09-25T02:25:02.744813+04:00, coordinator selection under D051 within P7) Existing static DWARF comparison
Context: D148a1d2daae proves structure/package; focused entry audit faec0d57 has separate scopedreview PASS. The16type/82offset actual comparison remains. Reused same-model glue review7d054afbd68a19a734053f69fc4c3992a55fee5498b675a44cb0194f316eb994 passes finalsource7c7fa476 and plan9ad886b9; local script checks pass with zero board dispatches.
Decision: authorize one captured-source execution of analysis/P7_static_link_probe_raw/compare_native_abi.py SHA7c7fa4769019c7aed0449fa3979d7c6c97edc3bf8625e60a5741313b88b6772b per plan9ad886b9ebeacc6f8285fbf61e5f3ccf2342650141732b1a7a890106ad31eba9. Reuse all230 pinned baseline queries verbatim against D144 debug ELF; add only -iex 'set auto-load no' before file selection, preserving init suppression. Five intended read-only commands bracket one file-only GDB with installed/source/artifact checks; no target/inferior/function call, compile/upload/reset or retry. Original465argument draft and preflight remain in3bf17a9c; final467args/11536UTF16units preflight passes.
Consequence: exact queried ABI equality or explicit mismatch only; native device/function ABI completeness, static adoption/runtime/liveRAM/WCET and human/physical gates remain separate. No production source/config/test change. Pin and record source before/after, keep first failure and independent checks, preserve all old evidence.

D-149 terminal disposition 2026-09-25T02:27:56.075972+04:00: one file-only GDB invocation and four bracket checks all exit0. All16 queried type size/alignment pairs and82 offsets match the exact current-default baseline. Source7c7fa476/currentfcddbd8e, installed26pins,103source/102stage, Claim/eight FileRecords unchanged; no postcheckerrors. Reused same-model actualreview3f4d20b7 PASS,35 priorD144/D148JSON records preserved. No target/inferior/compiler/upload/reset/productionchange; D149 consumed. Full native driver ABI/reference coverage and runtime qualification remain separate.


## D-150 (2026-09-25T02:42:26.110850+04:00, coordinator choice under D051 within P7) Existing direct native API boundary
Context: 4ced5cff identifies actual GPIO/PWM calls; separate reused-context same-model review8fd3b0d4 passes exact collector65cb7785 and plana795f5fe. Host preflight has50queries/215arguments/3561command units, four marker parser checks and zero board dispatches.
Decision: one captured-source execution of read_native_api.py SHA65cb7785234ac96d489a8f4439eabf1809745fba74eda1ab5a636cec0f7dd6c5. Five read-only commands bind original D144 identity/files and current source/installed dependencies around one GDB batch. Read both existing ELFs with init/object auto-loading disabled; require exact50nonempty ordered sections, successful status/empty stderr. Preserve first error and independent afterchecks; no retry.
Consequence: file observation and subsequent direct ABI/slot interpretation only. Internal packaged-driver calls remain inherited behavior; no compiler, upload, reset, firmware execution, production admission, source/config/test change, physical acceptance or human gate. No duplicate binary/build tree.

D-150 terminal disposition 2026-09-25T02:45:29.547149+04:00: exact one-shot ended NATIVE_API_READ_FAILED, preserved in result/launcher. Allfive commands returned0 with no postcheckerrors; GDBstderr states No function contains specified address, by-name wrapper section empty and whatis resolves void*const. Other49nonempty sections are partial file evidence, never a whole-collectionPASS. The original invalid-output failure staysunchanged; no retry/compiler/upload/reset. Retained olderADC receipt already contains the same name-query failure and successful do_device_init body; next only missing18-byte entry-wrapper range requires separately scoped observation.


## D-151 (2026-09-25T02:48:51.444270+04:00, coordinator choice under D051 within P7) Missing native init wrapper bytes
Context: D150 correctly failed its strict collection check on the ambiguous by-name wrapper lookup. Retained helper disassembly plus current partialtype evidence leaves only18bytes[08019e5c,08019e6e) for the wrapper-to-helper edge. Separate reused-context reviewd6124220 passes planfb7043e6/source4c39fafc.
Decision: one hash-bound read_native_init.py execution, SHA4c39fafc2efe646f53020ff121cd4441956c71b95c9ae1cb245454f9209da415, five read-only commands around the exact numeric-range disassembly. Preserve existing17local/26installed/source103/stage102/Claim/eightFileRecords and independent afterchecks, firsterror, no retry.
Consequence: missing file-evidence observation only, not a repeat or success relabel of D150. No production/source/config/test change, compiler/upload/reset/MCU execution, static admission, physicalresult or human gate.

D-151 actual observation 2026-09-25T02:50:29.998683+04:00: five read-onlycommands exit0/emptystderr/noaftercheckerror; source4c39fafc and alloldbindings unchanged. Numeric18-byte body readsdevice.state+12/initializedbyte1 bit0; ifclear tail-branches to observeddo_device_init08019e2c, otherwise returns-120. D150negative/49partialsections preserved. No newcompile/upload/reset/MCU; direct-boundary combinedreviewpending, runtime/production/physicalgatesremainseparate. Scopeconsumed.

D-151 final scoped disposition 2026-09-25T02:53:01.140514+04:00: actual collection reviewe35ee292 and
separate fresh-context combined dispatch reviewe4eca064 PASS, no open findings.
The selected GPIO/PWM/RCC/device-init file boundary is closed; D150 original
failure remains unchanged. Next is concrete inert startup qualification planning
with existing packet and verified upload/observation path. No new deployment
authority, firmware/config/test change, physical result or human gate follows.


## D-152 (2026-09-25T03:07:56.900112+04:00, coordinator selection under D051 within P7) Pure static startup interpretation
Context: dependency evidence4ba1c84e and retained D149 prefixes support the exact18-read/713656-byte passive plan. Separate fresh-context same-model design reviewe18be2cb42c54ad039e562a2ceed993640132e2c8df565c3ed8bd0d4245b6abd PASS/no open findings.
Decision: adopt analysis/P7_static_capture_contract.md SHAee1bb8d4acd969fa16330f2e7a55bf26daac71a6dbe4f6922c730f46bcb96fc3, limited to a pure host plan/parser in P7_static_startup_raw/static_capture.py. Exact full-image brackets precede diagnostic interpretation; malformed/fault/progress states stay distinct, modular counter evidence has explicit limits. Pre-adoption clarifications define exact scalar types, list/tuple containers, lowercase raw_hex and FAULT-phase precedence. Independent tests freeze before first implementation execution, followed by separate code/receipt review.
Consequence: no I/O, upload/reset, new MCU observation, production static admission, firmware/config change, old helper/oracle change, live RAM/WCET or physical/human gate. This is host preparation only; later capture and upload need separate bounded scopes. Synthetic fixtures remain in memory; use Python-B and no binary/source copies.

D-152 pre-native reference correction 2026-09-25T03:10:12.888418+04:00: original caller-provenance paragraph incorrectly named packagedBIN6b2ffd as the complete loader reference. Separate reference review53cb6ee7 independently derives263680B/SHAe9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 from checkedELF39d4a4fd using pinned p0.loader_image; original BIN differs at260287 (ELF0/BIN255). Adopt corrected contract58959d7c; original erroneous prose/designPASS preserved6d45e3b5 and explicitly superseded on this point. Pure comparator/interface and frozen synthetic testsbcb63005 unchanged; sourceb7ab979d passes37first-run methods, exit0, no fixes. No native operation occurred. Final code review pending.

D-152 final host disposition 2026-09-25T03:12:05.758851+04:00: firstsourceb7ab979d passes all37 frozen spec-derived methods in0.206s/exit0. Separate fresh-context same-model code/receipt reviewcdae7896 PASS/no openfindings. Original caller referenceMAJOR independently corrected per53cb6ee7/8fa01d1f; interface and tests unchanged. Local17pins/103source/102stage and PROGRESSprefix exact; production src/tools/host/tests unchangedfrom82b34f4a. No MCU observation/upload/reset/build or physical/gate acceptance. Next smallest guarded actual startup composition, no duplicate artifacts.


## D-153 (2026-09-25T03:19:15.414942+04:00, coordinator choice under D051 within P7) Bounded passive collector host implementation
Context: D1528837a457 closes pure interpretation; a real collection still requires durable one-shot ownership, fixed native argv/timeouts and partial failure evidence. Separate fresh-context same-model designreview7c7e8139 PASS/no openfindings for contract0b2cb941060954ea863f03194d10b7e3decf274bc3891d6055a6b2324b8e48fb andbindingsc2c87df6.
Decision: implement only new capture_remote.py and independent tests per analysis/P7_static_capture_remote_contract.md. Reuse hash-bound frozen descriptor helper/D152decoder/loader parser; exact18reads/713656B,600s launch/wait budget,30s command deadline/+5s bounded reap, one2s recorded interval, exclusive/fsynced ownedfiles and independent finalization. Test actual wrapper through controlled process substitutes; freeze before first execution. No alternative output/native path; preserve original source/grants/production admission.
Consequence: host implementation/testing only, no MCU read/upload/reset/compiler. Known-clean newupload and source-bound reviewed launcher remain prerequisites to later native capture. Test-only synthetic bindings are not native provenance. Default process-group timeout can retain unknown outcome, never claim quiescence. Keep small required evidence and release owned temporary fixtures.

D-153 pre-execution clarification 2026-09-25T03:20:46.302183+04:00: contracta2385cbe explicitly permits failure/finalization receipts through retainedoriginaldirectoryfd when pathname drift is detected, after verifying heldfdidentity; never write replacementpath. Newcommands/claims requirecompletepathidentity; helpercontext-exiterror remainsadditionalfailure. This clarifies retainedpartialevidence without broadening nativepermission. No tests executed yet; original0b2cb941 contract/design preservedf5f708ee.

D-153 pre-freeze review repairs 2026-09-25T03:22:48.142627+04:00: currentcontract0371739e makes literalbraces/eight-digitlowercasehex and immediateprePopen deadline recomputation explicit, plus retainedlastvalid timestamps for failure receipts after clockerrors. Originalsourceb099e4d9 preservedd5c8d6d6 before any execution; reviewer identified stale default-wrapper budget and possible context-exit error replacement, root identified failure-timestamp retention. Worker repairs remain within agreed scope; independent test author clarifies draft oracles solelyfromcontract. No establishedtest/productionfile changed and no test/nativeexecution yet.

D-153 final host disposition 2026-09-25T03:28:45.809989+04:00: IMPLEMENTED/HOST-TESTED. Firstexecutedsource1aa602d0 passes46 frozen independent methods2.569s/exit0 plus4 reviewer supplemental boundaries0.153s/exit0. Separate fresh-context same-model revieweed7414decef44a54896f8e9fb2b55f5ad2dd87bca9d97318509ec7e97d7e8f8 PASS/no openfindings. Original unexecuteddraftb099 preservedind5c8d6d6; repairs precedefirstfreeze5f85268f. All12union frozeninputs/17localpins/103source102stage and originalPROGRESSprefix exact; productionunchangedfrom8837a457. Zero native capture/upload/reset/compiler. Known-clean upload/source-boundhostcoordinator remainseparate nextscope. Existingboardloaderutility885c4e42 file-verified supports smaller inlinepayload; no newhelperinstallation.


## D-154 (2026-09-25T03:43:48.551006+04:00, coordinator choice under D051 within P7) One-shot upload wrapper host scope
Context: D153 collector is complete; F165 file observations bind selected core/uploader and expose CLI initialization side effects. Separate same-model design review in reviews/P7_static_upload_design_review.md passes contract319ce137 and bindingsa31bca78, no open material findings.
Decision: implement and independently test only the fixed upload_remote.py contract, composing frozen descriptor and stateless process helpers without changing them. One durable owned attempt, exact M0 packet/argv/environment,180s total budget/120s childwait/+5sreap, complete failure and independent postcheck evidence. Freeze spec-derived tests before first execution and obtain separate code/receipt review.
Consequence: host-only scope; no native upload/reset/activation/capture authorization. Host coordinator/source/HEAD/D144/run admission and missing CLI initialization prerequisites remain separate required work. No production/config/locked-test changes, binary/source copies or gate claims.

D-154 pre-freeze clarification 2026-09-25T03:46:30.549111+04:00: contract7fa1c0f0 explicitly fixes every17 role path (fixtures may change size/hash only) and retains strictlytyped unsuccessful process mappings while malformed returns leave subprocessNone. This narrows/clarifies original reviewedcontract319ce137; no new native permission. First unexecutedsource68ea5ee9 is retained before independent tests/review; AST-only parsePASS, longest33lines.

D-154 final host disposition 2026-09-25T03:55:21.028709+04:00: source81668c79 passes55 unchanged frozen spec-derived tests after one implementation repair; three code-informed reviewer supplemental cases also PASS. Original53/55 failures/source retained. Separate same-model reused-design-context review8efe48a3 PASS, R1/R2 resolved. No source/config/locked-test/support changes, native upload/reset/capture or gate. Host coordinator/fresh source-bound native admission remain next; F166 prerequisite observations are not execution proof.

## D-155 (2026-09-25T03:59:13.575391+04:00, coordinator choice under D051 within P7) Minimal fixed host startup composition
Context: D153 collector and D154 upload wrapper are implemented, host-tested and scoped-review PASS. Actual current-image inert startup still needs source/packet/CLI prerequisites, durable host intents and conditional observation. Separate same-model reused design-context review55c8f8ad PASS for amended contractf91f1210; initial capture-schema gap explicitly resolved before freeze.
Decision: implement only analysis/P7_static_startup_launcher_contract.md via one fixed startup_run.py plus independent host tests. Reuse frozen modules, original D144 objects and exact F166 file-only inventory commands. Separate host and remote one-shot claims, currentHEAD/source/packet checks, one upload then conditional passive capture, bounded commands/timeouts, independent failure finalization; no new build or copied source tree.
Consequence: HOST-ONLY adoption; native_run01_scope.json is deliberately absent until final code/test review and specific inert-run identification. No native upload/reset/capture, source/config/locked-test change, static production admission or physical/human gate follows. Native public entry refuses absent scope; future scope is committed and binds reviewed implementation/tests/reviews while CLI argument binds its containing currentHEAD.

D-155 pre-freeze clarification 2026-09-25T04:00:32.562765+04:00: contract2bdbc3c9/designreviewec0a0abaPASS clarifies that full localHEAD/source admission gates upload/capture; four captured fixed Linux-file command forms may still perform independent final checks after a separate localdrift failure, with pinnedADB identity rechecked. No new command, retry, native authority or changed orchestrationinterface. Originalcontractf91f1210 preserved8b0e1e58.

D-155 final host disposition 2026-09-25T04:08:23.503879+04:00: source6f86e645 passes30 frozen independent methods0.046s/exit0 and10 code-informed reviewer adapter methods0.119s/exit0, both first execution. Scoped same-model reused-context review26fcf2f7PASS. Three source findings repaired before tests; original firstsaved7149bfb6 preserved0cdfa50b, subsequentfdbd3cb5/3bcc8219. Actual local composition validates16new+17runnerpins/103workingmanifest/102stage and sixcommandforms; upload28068/capture24981UTF16units, zero dispatches. Rawsourcecountnull projection preserved/explained. Native scope stillabsent; no board/compiler/source/config/test change or gate. Next identify one exact inert native scope.

## D-156 (2026-09-25T04:11:07.233776+04:00, one inert run under existing user bare-board permission and D051)
Context: the user reports UNOQ connected alone and expressly permits testing it. D155code/receipt review26fcf2f7PASS and concreteplan1702591a/scopec7447815 pre-runreview484725e8PASS bind the existing sourcefcddbd8e D144static/defaultM0packet. Both C/C++ compile flags in pinned0017receipt are MOTORS_ALLOWED=0/MATCH_BUILD=0. No STAND/RING exists and none is inferred.
Decision: commit and execute native_run01_scope.json exactly once through startup_run.py6f86e645 with --execute --reviewed-head naming the containing currentcommit. Target ADB2629958581/expectedboot6d4aca1b/UID1000; operationstatic-fcddbd8e-run01. Permit only fixed14-clean-path/sixcommandforms: freshpacket/installed/F166 checks, one D154upload and its intrinsic loader/sketchflash/reset/activation sequence, conditional D15318passive reads, independent finalchecks. Exactbudgets/paths are in analysis/P7_static_startup_run_plan.md.
Consequence: no compile, firmware/source/config change, extrareset/retry, privileged takeover, additionalhardware or motor-capable firmware. Unknown/failed upload suppresses capture; consumed attempts stayconsumed. Actualoutputs/failures retained; collected evidence is not byitselfstartupsuccess and cannot approve liveRAM/WCET, physicalacceptance, staticproductionadmission or human gates. Source/HEAD/board/prerequisites must pass freshadmission, otherwisefail explicitly.

D-156 actual outcome 2026-09-25T04:18:00.171497+04:00: FAILED, scope consumed, no retry. ReviewedHEADe173053c invocationexit1; nine transportcommands0, one upload childexit1/reapedtrue/notimeout, capture0. InheritedD153RLIMIT_FSIZE1048576 prevented2303728Bloadercopy. Allindependentfinalpacket/source/installed/F166/localchecksPASS. Actualreview8a60e74b accepts containment but leaves MAJORuploadpolicydefect. Versionedsource ordering placescopyerrorbeforeOpenOCDcall byinference, notMCUmeasurement. Readonlyinventoryfindsone1MiBfragment/tmp/remoteocd; itsfullhash matchesexactprefix ofretainedcheckedloaderELF. No cleanup/reset/furthernativeaction. Preserveallfirstattempt evidence; next minimalupload-onlycapcorrection plusrealharmlesscopy/boundaryregression and separatelyreviewedfutureownership/residuehandling.

## D-157 (2026-09-25T04:22:47.679134+04:00, additive host-tool correction under D051)
Context: D156 failed before remoteocdOpenOCDlaunch bysourceinference because inherited1MiBfilecap blocked2303728Bloadercopy. Realhostcopyregression4/4PASS provesminimumfiniteextent. Designreview73386970 PASS for contract8b31b281.
Decision: explicitly permit the additiveD154uploader edit in analysis/P7_upload_file_limit_contract.md: newupload_loader usesper-instancelimit_upload_files withRLIMIT_FSIZE soft/hardexact2303728; legacyupload andallitsoraclesstayunchanged. Sharedlifecycle avoidsduplication; frozenD153 untouched. Acceptedstdout/stderrremainstrictly<1MiB each, whiletransientstreamfilescanreach2303728; thischangedphysicalceiling isexplicit,notrepresentedaspreserved. Newindependentcompanionmustexerciseall55inheritedcases plusfournewboundaries/bindingchecks; legacy55regressionmuststillpass.
Consequence: HOST-ONLY; no capturebinding, consumedpath, nativecaller ororiginalrun scopechange. D155oldsourcepinmustrejectchangeduploader. OriginalD154source81668c79 remainsGit evidence, noneofitsoldtestassertionschanged. Laternativeownership/callerselection/knownpartialtmpfilehandling requireseparatereview. No firmware/pin/config/lockedtest/motor/humangate change, cleanup or retry.

D-157 final host disposition 2026-09-25T04:27:13.330765+04:00: source bb6f9631 passes all 55 unchanged legacy methods and 59 independent companion methods on first execution (3.595s/3.698s, exit0). All nine frozen pins remain exact; separate review fc1b2414 PASS, no material findings. Four real copy-boundary tests also pass. D156 remains failed/consumed; old D155 pin correctly rejects the new uploader. Next is explicit fresh run ownership and separately reviewed residue handling. No native action, firmware change or physical/human gate.

## D-158 (2026-09-25T04:30:03.033122+04:00, coordinator under D051) Explicit fresh startup ownership
Context: D157 corrected the file cap; the old run01 ownership is consumed. A new attempt requires distinct claims and explicit selection without duplicated wrappers or module-global rebinding. Separate design review2f98c2d2 PASS; test-only interface clarifications add exact payload/run identity and historical source-free pin baselines.
Decision: implement analysis/P7_startup_run02_contract.md (SHA256 71ed0e595471c92c2272334909249173c88c3cefd202bdf99bf40d958da37e41) as narrow per-instance run01/run02 selection in the existing uploader, collector and launcher. Original defaults/pins/oracles/scopes remain; explicit optional bindings and closed run_id select fresh paths. Legacy upload remains run01/original cap. The unchanged collector body receives only ownership parameterization, expressly superseding its source-freeze restriction for this additive interface alone. Independent tests freeze before execution; actual diff/receipts need separate review.
Consequence: HOST-ONLY, no native_run02_scope file, cleanup, upload/reset/capture or gate yet. The known temporary partial file remains an admission blocker. No firmware/config/locked-test change, clone, new tool install or changed acquisition semantics.

## D-159 (2026-09-25T04:32:28.296465+04:00, exact cleanup under the user storage instruction)
Context: the reaped D156 loader-copy failure left one reproducible1MiB prefix in /tmp/remoteocd. Original raw failure/inventory/prefix evidence and full checked loader are retained. Separate pre-action source review2f9c02f5 PASS for guarded source3b3d899b; two observed-drift gaps were fixed before execution.
Decision: permit one exact execution of remove_failed_fragment.py against ADB2629958581, boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6, as described in analysis/P7_failed_fragment_cleanup.md. It may unlink only the fixed hash/inode/UID/mode/size/mtime/single-link regular fragment and then rmdir its verified empty original directory, with fresh process/file/board checks. No recursive deletion, other file removal or automatic retry. Save exclusive local intent and actual result.
Consequence: this recovers board temporary space, not Windows C:. It does not approve upload/reset/capture, revive run01, erase failure history, assert global quiescence or change firmware/config/tests/gates. Any failure or changed identity leaves the new evidence and stops.

D-159 actual outcome 2026-09-25T04:32:59.517971+04:00: one execution at HEAD e2fdacf3 returned0/empty stderr, REMOVED; exact1,048,576-byte fragment unlinked and original empty directory removed, held descriptor link counts/path absence verified by code. Same fixed boot and source hash; no additional board/MCU action. Scope consumed; original failed run evidence remains. See fragment_cleanup_intent.json and fragment_cleanup_result.json.

D-158 final host disposition 2026-09-25T04:37:49.562285+04:00: scoped review bda4208e PASS,227 aggregate methods passing. Original bcf623dc implementation and2975e2a8 oracle/negative receipts preserved1854bb8e. One implementation repair restores default legacy binding/call compatibility; run02 strict projection/identity unchanged. One fixture-only correction supplies missing pure json_bytes serialization, with all assertions unchanged and no locked-test edit. Final launcher c9588835, upload23661c8a, collectorab0bb320, oracle84503c31; all18 repaired-freeze pins exact. Local composition16+17 pins/verifiedstage/six forms/zero dispatch, commands28751/25436units. D159 residue removed separately; a new native scope is still required.

## D-160 (2026-09-25T04:39:32.174941+04:00, separate inert run under existing user bare-board permission and D051)
Context: D158 implementation/test/composition reviewbda4208e PASS; exact run02 plan c464f8a1/scope78bb3e56 pre-action reviewdb051e4f PASS. User reports UNOQ connected alone and permits testing. D1440017 pins both C/C++ MOTORS_ALLOWED=0/MATCH_BUILD=0. D156/run01 remains failed and consumed; D159 separately removed only the known temporary fragment.
Decision: commit and invoke startup_run.py c9588835 once with --execute --run run02 --reviewed-head naming the current scope-containing commit. Operation static-fcddbd8e-run02, target ADB2629958581/boot6d4aca1b/UID1000, unchanged sourcefcddbd8e and original D144 packet. Scope permits exact fresh file/source/installed/prerequisite checks, one upload_loader call with its intrinsic loader/sketch program/reset/activation sequence, conditional18-read passive capture and independent final checks. Fresh tmp absence/conflicting-process/identity checks remain mandatory. Exact limits/owners are in the reviewed plan.
Consequence: no compile, source/config/pin/locked-test change, extra hardware, motor-capable firmware, additional reset, privilege takeover or automatic retry. Unknown/failed upload suppresses capture; terminal scope stays consumed. Collection status and observed startup progress are separate; neither grants RAM/WCET/physical/production-static/human-gate acceptance.

D-160 actual outcome 2026-09-25T04:44:51.069949+04:00: scope consumed, one upload succeeded and one18-read/713656B capture collected. All14 transport commands0/empty stderr; full loader/sketch before/after comparisons true, final checks clean, no query/compile. Observation NO_RUNNING_PROGRESS: both runtime samples STOPPED/epochs3/initfalse/faultNONE; transaction IDLE finished/timingvalid,495us unchanged. No extra reset/read/retry follows. Running qualification remains open;790us sampled maximum is not WCET. See analysis/P7_static_startup_run02_actual_validation.md and original receipts.

D-160 actual review closure 2026-09-25T04:58:02.214143+04:00: separate same-model reused-context review974b452653a8dba17f916c4b45846797cc45e2481f5480360211b1c3718afb17 PASS for collection, running qualification NOT MET. All14 local receipt forms/hash bindings and diagnostic prefixes audited; remote raw flash was not refetched. Nested Robot/MotorGate faults remain unobserved. No new native action, firmware change or gate.

## D-161 (2026-09-25T05:00:25.097694+04:00, separate passive diagnosis under user bare-board permission and D051)
Context: consumed D160 successfully uploaded sourcefcddbd8e/static/default/M0 but stopped at epoch3. The saved prefixes cannot identify nested Robot/MotorGate faults. Exact D149 offsets are available; scoped review71305a36 PASS binds source71507fd8 and planbf992388, including repaired failure finalization and controlled host checks.
Decision: one separately owned diagnostic as analysis/P7_stopped_diagnostic_plan.md. Commit the reviewed source/plan/review, verify current clean HEAD/local103-source102-stage/pinned helper/support/bindings/ADB, create exclusive local stopped_diagnostic01/intent.json, then dispatch one Python-B command with60s outer timeout. Target ADB2629958581/boot6d4aca1b/UID1000; fresh remote static-stopped-fcddbd8e-run02-diagnostic01. One fixed MEM-AP OpenOCD invocation reads four labelled windows totaling752B,30s child/+5s bounded reap. Retain all outputs/errors and independent afterchecks; exact labels/addresses/word counts required for interpretation.
Consequence: no upload/reset/halt/resume/firmware write, new build or source/config/locked-test change. No automatic retry. D160 full flash provenance is inherited, not remeasured. Equal sampled prefixes do not prove atomicity or uninterrupted MCU continuity. No physical/human/production-static/WCET gate follows; consume this scope after its sole attempt.

D-161 actual outcome 2026-09-25T05:05:44.191981+04:00: one fixed752B passive observation at1d455be7 returned0/clean finalchecks; exact labels/counts/addresses independently parsed, reviewc323dc88 PASS. Runtime/transaction prefixes match D160; stored Robot0x0110 and MotorGateIO3 confirm invalid application feedback. Original native failing callback/latency remains unknown; no safety-limit change. Scope consumed, no retry/reset/upload or gate. Evidence analysis/P7_stopped_diagnostic_validation.md.

## D-162 (2026-09-25T05:12:13.698242+04:00, host diagnostic preparation under D051)
Context: D161 observes GateIO/invalid receipts but the original failing callback is not retained. User permits bare-board testing; no motor-capable run is authorized. Fresh-context same-model design review finds no material safety conflict for the bounded bench diagnostic; in-progress marker and unchanged blocking-setup limitation clarified before implementation/test freeze.
Decision: implement only analysis/P7_motor_fault_contract.md and its public header/new bench/new independent tests. Copy native callbacks through a fixed64-record trace, retain first false across cleanup, use four explicit zero-output sample commands through the real MotorGate, and halt once. Default permission false; reject MATCH or motor-enabled compilation. Fixed evidence extents are not control tunables. No native adapter/config/core/existing locked-test change; all timing limits remain.
Consequence: HOST-ONLY until implementation/spec-derived tests/review pass. This does not add upload permission or static production admission, identify D160's original callback, or prove WCET/physical gates. Diagnostic timing perturbation and potentially blocking unchanged setup are explicit. Serial RAM-backed builds and compact evidence; native compile/run need later identified scope.

## D-163 (2026-09-25T05:21:30.876862+04:00, additive host build-route preparation under D051)
Context: D162 diagnostic source is implemented; host evidence still executing. Generic bench compile bypasses checked project/recipe/artifact admission. Fresh-context design review accepts analysis/P7_motor_fault_build_contract.md: reuse existing checked route with five exact literal additions, no new framework or upload allowlist.
Decision: admit bench/motor_fault/motor_fault.ino in the existing checked/default-inert/project selectors of board_tool.py and app_build_policy.py only. Preserve all oldtests/recipes/manifests and D162oracles; independently author/freeze companion tests before execution. Old historical probes retain their original pins and must reject these changed tooling bytes rather than silently adopting them.
Consequence: host tooling only, not a board build/run. Existinggeneric checked route still lacks serial remotechild deadline; actualcompile requires laterfixedcaller with jobs1/explicitCLI/env/config/paths/deadline/reap and artifact evidence. No source/config/nativeadapter/safetycap/lockedtest change, no uploadauthorization, no physical/gate claim.

D-162/D-163 final host disposition 2026-09-25T05:29:30.226819+04:00: IMPLEMENTED/HOST-TESTED, scoped separate same-model reviews 7a182ffb/204d425d PASS, no open material findings. D162 normal and ASan/UBSan each18cases/2570assertions; driver3methods; unchanged fullhost22/22. D163 new13+legacy52 policy methods PASS. Original missing compiler-flag/import failures retained; driver-only flag and caller-only import repairs change no assertions or production bytes. All46diagnostic/10policy pins exact. See analysis/P7_motor_fault_validation.md. No target build/run, physical evidence or human gate; next bounded identified compile-only caller.

## D-164 (2026-09-25T05:31:43.976461+04:00, per-call host build executor under D051)
Context: D163 exposes the inert diagnostic through checked compilation, but bounded explicit target execution currently requires global transport replacement or copied policy. Neither is needed.
Decision: implement only analysis/P7_compile_executor_contract.md: optional keyword-only command_runner on the three existing checked-build helpers. Default behavior and old tests remain; an explicit callable routes every command per invocation with no global rebinding. Independent companion tests freeze before execution.
Consequence: HOST-ONLY interface preparation; no native scope, new policy/flags/upload/reset, firmware/config/locked-test change or gate. The parameter does not itself bound execution; the next fixed native caller must supply verified CLI/env/config, jobs1 and board-side deadline/reap.

D-164 host outcome 2026-09-25T05:40:57.831764+04:00: source2a7d805a (4707fbce) unchanged, all146legacy methods passed first invocation; all15new methods pass after one fixture-only classifier repair bb04de24. Original161method negative retained; assertions unchanged,20freeze pins exact. Separate fresh-context same-model reviewaf090dbc PASS, no material findings. See analysis/P7_compile_executor_validation.md. No native action or gate; optional executor alone supplies no deadline.

## D-165 (2026-09-25T05:44:31.580657+04:00, identified inert target compile under D051 and existing user bare-board permission)
Context: D162/D163 diagnostic and D164 explicit-executor host/source reviews pass; controlled real-child checks4/4 pass after a fixture bytes-type repair, with original negative retained. Pre-run review77c7f5d37b5c5a983418810ba986fee0d07b50ffd72dcedde5aa15099bc6a5e3 PASS binds callerf804f452,117-pinmanifestd1ba918d andplandee61f93. Local admission passes; largest checked hash command8952units below30000; both new ownership paths absent.
Decision: commit the fixed caller/input/review/host receipts, then execute it once exactly as analysis/P7_motor_fault_compile_plan.md using Python-B and per-process isolated pycache_prefix. TargetADB2629958581/UID1000/boot6d4aca1b; bench/motor_fault default dynamic M0/MATCH0; fresh motor-fault-compile01. Scope includes read-only initial identity/prerequisites, exact fresh staging/file pushes, one properties query/one compile withjobs1 and childdeadline/reap, existing policy/artifact validation and independent final checks.
Consequence: compile-only; no upload/reset/MCU read, changed source/flags/pins/safetylimits/lockedtests, package install or automatic retry. Failed/uncertain attempt stays consumed with raw evidence. Checked compilation is not startup, originalfault causation, WCET, static production admission, physical acceptance or human gate. Preserve old policy-denied caches; no global configuration changes.

D-165 actual outcome 2026-09-25T05:47:55.737680+04:00: TARGET-COMPILE-FAILED, scope consumed. Reviewed3c291ea2 executed one query/onecompile; compilerexit1/reapedtrue/notimeout, all122transports0 and sevenfinalchecksPASS. Actual Zephyr CONFIG_PWM=1 macro collides with diagnostic enum, not a MotorGate safety-limit failure. Original64702B compilerJSON and source4ec345c0 retained; no verified artifact, upload/reset/MCUread or gate. See analysis/P7_motor_fault_compile_actual.md. Next identifier-only source fix plus observed-macro regression before a fresh attempt.

## D-166 (2026-09-25T05:49:10.681321+04:00, identifier-only target compatibility repair under D051)
Context: D165 actual target compile fails because generated Zephyr autoconf.h defines CONFIG_PWM=1, colliding with the new diagnostic enum. Host tests lacked that native macro. Original source/receipts and consumed117-pin scope remain intact.
Decision: rename only diagnostic Operation::CONFIG_ENABLE/CONFIG_PWM to CONFIGURE_ENABLE/CONFIGURE_PWM in its header, implementation and corresponding public test identifiers. Preserve enum ordering/numericvalues, trace fields, callbacks and all behavior. Author an independent syntax regression with the observed CONFIG_PWM=1 macro and unchanged numeric operation identities; retain all existing test assertions and locked tests.
Consequence: no macro undefinition, core/HAL/native safety-limit/config/wiring change or native retry. Run focused normal/sanitized and macro-host validation plus source review. D165 compile_inputs.json remains historical and must reject changed source; a later compile requires explicit fresh ownership/source binding. No target acceptance, motor permission or human gate follows.

D-166 final host outcome 2026-09-25T05:53:05.273575+04:00: macro1/1 plus driver3/3, normal and ASan/UBSan each18cases/2570assertions PASS,47pins exact, separate reviewa877c709PASS. Only enum labels and three test identifier references changed; no assertions/controlflow/native safety limit changed. See analysis/P7_motor_fault_macro_validation.md. Original D165 failedscope/sourcebindings remain; target recompilation pending fresh ownership.

## D-167 (2026-09-25T05:54:42.401073+04:00, narrow compile ownership under D051)
Context: D165 failed on a target macro; D166 host-tested rename is ready. Compile01 is consumed and its manifest must stay historical.
Decision: implement analysis/P7_compile02_contract.md as closed per-instance compile01/compile02 path selection in the existing caller. Preserve old inputs/receipts and exact child-execution machinery; independent companion expectations freeze before testing. Default historical selection remains but rejects changed source.
Consequence: HOST-ONLY, no new native action or automatic retry. A fresh input binding/plan/review and identified compile02 decision must precede target compilation. No firmware behavior/config/pin/locked-test or upload permission change.

D-167 host outcome 2026-09-25T06:09:46.394702+04:00: caller2f1cdbb3 unchanged after implementation7bd0108c. Independent12/12 controlled methods PASS, seven freeze pins exact, separate fresh-context same-model reviewf84cad37 PASS. Original7PASS/2fixtureERROR retained9490278f; fixture-only additions preserve all original assertions, intermediate067draft never executed. Actual Windows local admission117pins PASS, zero transports. See analysis/P7_compile02_validation.md.

## D-168 (2026-09-25T06:09:46.394702+04:00, identified corrected inert compile under D051 and existing bare-board permission)
Context: D166 target macro correction and D167 ownership are host-tested/reviewed. Pre-run reviewf84cad37 binds caller2f1cdbb3,117-inputmanifest74af663e,plan3a3f841b and frozen12-test result. D165 remains failed and consumed; no source or flags are changed for this new attempt.
Decision: commit this scope and execute the existing caller once with --execute --run compile02, Python-B and its absolute native_compile02/pycache prefix, as analysis/P7_motor_fault_compile02_plan.md. TargetADB2629958581, UID1000/arduino, boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6. One checked default/dynamic M0/MATCH0 diagnostic properties query and compilation, jobs1; fresh identity/prerequisites, exclusive stage/remote paths, unchanged child deadlines/reap and independent final checks.
Consequence: compile-only, no upload/reset/MCU read, source overlay, installation, automatic retry or additional hardware. The sketch's grant remains false: even target success is syntax/artifact evidence, not an active diagnostic or original-fault measurement. Preserve failures and actual artifacts; no physical/human gate or motor-run permission follows. Remove only verified disposable local staging after evidence review.

D-168 actual outcome 2026-09-25T06:18:16.600243+04:00: TARGET-COMPILED, scope consumed. ReviewedHEAD2f0379f6, actual packet1edf4a08; source5d3d126e/finalELF87fb03e5, one query/compile,123 transports and ten children exit0/reaped/no timeout, seven final checks PASS. Separate actual review32e1c119 PASS. No upload/reset/MCU read; grant remains false. CLI size reports are not live RAM/WCET. New local staging cleanup was rejected by automatic review (blocked by policy);104files/764049B retained, no retry. See analysis/P7_motor_fault_compile02_actual.md.

## D-169 (2026-09-25T06:20:11.607810+04:00, minimal diagnostic selector under D051)
Context: D168 default-disabled diagnostic compiled and passed review, but cannot observe callbacks without an explicit inert activation. The user authorizes bare-board work; no motor-capable run or human gate exists.
Decision: implement analysis/P7_fault_activation_contract.md: default-zero SUMOX_MOTOR_FAULT_PROBE in config.h, 0/1 and inert/exclusive profile assertions, one conditional existing sketch grant, and exact project-specific checked flag admission. Reuse the real Runner/Trace/MotorGate unchanged. Independent companion tests and separate diff/evidence review precede completion.
Consequence: HOST-ONLY preparation; no upload allowlist, source snapshot, consumed scope/manifest, firmware/native safety-limit or locked-test change. No board action or deletion of the policy-blocked stage. A later active compile and inert run require fresh source/artifact evidence; this build selector supplies no permission.

D-169 pre-execution clarification 2026-09-25T06:24:08.801319+04:00: root and separate reviewer found new draft fd03b1c0 asserts generic app flag rejection at selected_project alone, beyond that helper's historical contract. Complete flag admission belongs to expected_properties/preflight/result validators. Preserve production helper behavior and draft0c140362; independent author replaces the misplaced assertion with full-boundary rejection/control coverage and corrects recorder_inert.ino to admitted recorder.ino. No tests have executed, no existing assertions or requirements relaxed; original public refusal requirement is retained at its actual boundary.

D-169 final host outcome 2026-09-25T06:30:31.750945+04:00: source32b2d9d4 unchanged; independent13/13 PASS first execution,29 unchanged tooling methods PASS, diagnosticdriver3/3 PASS with normal and ASan/UBSan each18cases/2570assertions/0skips. All63 frozen hashes exact; separate fresh-context same-model revieweeb297fa PASS. Original unexecuted draft/public-boundary correction retained0c140362/84b3fbaf. No existing assertion, source limit or B16 value changed. No new target compile/upload/reset or stage cleanup. See analysis/P7_fault_activation_validation.md. Next additive explicit fresh-attempt staging, then fresh active artifact/inert capture binding.

## D-170 (2026-09-25T06:33:38.717625+04:00, additive local staging under D051 and storage instruction)
Context: D169's active inert selector is host-tested, but the fixed staging path holds D168 evidence whose cleanup was policy-blocked. Never retry that deletion through implicit staging.
Decision: implement analysis/P7_fresh_stage_contract.md: keyword-only explicit attempt ownership, bounded portable token, checked plain ancestry/containment, exclusive absent owner and the existing Arduino copy/layout body. Default callers keep legacy behavior. Independent companion tests and separate review cover preservation and failure retention.
Consequence: host source preparation only; no CLI/native/build/upload/reset action, old attempt reuse, ROOT redirection, duplicate wrapper, firmware/config/locked-test change or human gate. Explicit failures retain their owned partial files for inspection.

D-170 pre-execution layout clarification 2026-09-25T06:38:21.942112+04:00: independent draft5e8d05d1 is preserved2a586e22 before any execution. The public contract now states that both bench and app stages receive project src/app C/C++ support under staged src/app (no duplicated app.ino), matching the unchanged legacy copy body. Independent author adjusts only this new draft expectation. No production copy logic or existing tests are changed.

D-170 first execution 2026-09-25T06:39:52.360073+04:00: frozen ninepins exact; WSL25PASS/1Windows-onlyskip, Windows16PASS/1fixtureFAIL/9symlinkprivilegeskips, actualjunctionPASS. Original0160d1a6/firstreceipt retained. Installed Windows3.13.11 copy2 uses CopyFile2 without copyfile; independent failure injection missed its boundary. Author corrects fixture boundary only, preserving every assertion and production73f14c29. See analysis/P7_fresh_stage_failure.md; no native action or deletion.

D-170 final host outcome 2026-09-25T06:46:21.730677+04:00: implementation0160d1a6 unchanged; corrected independent7b3efe58 fixture keeps every assertion. WSL25PASS/1platformskip, Windows17PASS/9symlinkprivilegeskips (actualjunctionPASS),91unchanged tooling methods PASS. Separate fresh-context same-model review8233de35 PASS; all9pins,104retainedstage filebytes/mtimes and PROGRESSprefix exact, no scratch remnants. Original draft2a586e22 and Windowsfixturefailure0160d1a6 retained. No native action or denied deletion retry. Next minimal active-profile ownership in existing compile caller; see analysis/P7_fresh_stage_validation.md.

## D-171 (2026-09-25T06:49:40.220307+04:00, active diagnostic compile preparation under D051)
Context: D169 activation and D170 fresh staging are independently host-tested/reviewed. Compile01/02 are consumed; retained legacy stage cannot be deleted or implicitly replaced.
Decision: implement analysis/P7_active_compile_contract.md as one closed active01 selection in the existing bounded caller, with explicit per-instance source/owner paths and exact inert activation flags. This extends only D167's selector/path contract; old behavior/manifests/assertions and child machinery remain. Independently derive/freeze companion tests and obtain separate review.
Consequence: host-only preparation, no native operation, upload/reset, source overlay, old manifest repinning, cleanup retry or locked-test change. Actual active compilation needs fresh source/identity binding and a later identified scope; no physical/human/motor-run permission follows.

D-171 pre-execution fixture review 2026-09-25T06:54:35.569150+04:00: preserve independent unexecuted78923db5 draft449c4698. Separate reviewer found a text-read spy on the raw-byte manifest interface, first_error mapping/message confusion and missing selected-cache preconditions masking two run refusal boundaries. Independent author corrects only these new fixture/oracle targets and adds reached-boundary checks; production84efd006 unchanged. Existing12testsPASS and actual117-pin local admissionPASS/native0; no new independent test execution yet.

D-171 final host outcome 2026-09-25T06:56:42.283480+04:00: caller84efd006/source1a89c4a1 unchanged. Independent16/16PASS0.145s firstexecution,12legacyPASS, all12frozenpins exact and actualWindows117-pin localadmissionPASS/native0. Separate fresh-context same-model reviewc9781e61PASS for source/tests/manifestb91cf39c/plan41d697b2. Original unexecuted449c4698 draft retained. Old manifests and all child machinery unchanged. See analysis/P7_active_compile_validation.md.

## D-172 (2026-09-25T06:56:42.283480+04:00, identified compile-only attempt under D051 and existing bare-board permission)
Context: D169 active inert flags, D170 explicit staging and D171 ownership are host-tested and separately reviewed; current user permits bare UNO Q work. Source/input/plan reviewc9781e61 has no open findings. Compile01/02 remain consumed; no motor-capable run is authorized.
Decision: commit this scope and execute caller84efd006 once with --execute --run active01, Python-B and the absolute native_active01/pycache prefix, per analysis/P7_motor_fault_active_compile_plan.md. TargetADB2629958581/UID1000/boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6;117-inputmanifestb91cf39c. Fresh owner build/stage/motor-fault-active01, fresh local native_active01 and remote motor-fault-active01. Exact default/dynamic flags MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1; one checked query/compile, jobs1, all prior deadlines/reap/identity/prerequisite/source/artifact/final checks retained.
Consequence: no upload/reset/MCU read, dependency change, source overlay, motor run, extra hardware or automatic retry. Changed identity/binding or any failure preserves evidence and consumes the attempt; never repin during it. Active compilation is not diagnostic execution or physical acceptance. Retained legacy stage and all policy-denied paths stay untouched.

D-172 actual outcome 2026-09-25T07:06:20.297115+04:00: TARGET-COMPILED, scope consumed. ExecutionHEAD6bf5ecb1/evidence db1228ce; source8f592937/finalELFf9460a16, one query/compile,123transports/tenchildren0/reaped/no timeout, sevenfinalchecksPASS. Separate actual review41ecc2c9PASS. Active inert flags compile, but no upload/reset/MCU read or runtime/gate evidence. New104-file/764719B stage cleanup rejected by automatic review; retained and excluded from retries. See analysis/P7_motor_fault_active_compile_actual.md. Next bounded file-only ELF/ABI and upload-recipe observation.

## D-173 (2026-09-25T07:10:13.872609+04:00, bounded file-only artifact investigation under D051)
Context: D172 active inert compilation and separate actual review pass; runtime diagnosis requires real ARM layout and exact dynamic artifact binding.
Decision: execute analysis/P7_motor_fault_abi_plan.md once after source review, using the existing transport/reap primitives and five fixed readelf/GDB file-only commands. Bind D172 artifacts/tools/loader before and after, preserve failed/partial evidence and fresh local ownership.
Consequence: no upload/reset/MCU read, source or consumed-stage change, dependency install, motor permission or gate. A later inert upload/capture remains separately scoped.

D-173 pre-execution review 2026-09-25T07:14:12.509806+04:00: original unexecuted reader273d1871/review FAIL retained. Fixed manifest SHA/count, independent local closure and byte-preserving per-stream failure collection; root-controlled9cases PASS/native0, final composition6009units/25pins/fivechildren verified. Revised reader50c07402; separate source revieweb9e2d78PASS, original context reused for fix review. No native attempt yet; one file-only observation follows containing commit.

## D-174 (2026-09-25T07:17:00.948767+04:00, offline diagnostic decoding under D051)
Context: D173 observes exact ARM Runner2592B and its nested fields; no diagnostic RAM has been captured.
Decision: implement analysis/P7_motor_fault_decode_contract.md as a pure finite offline decoder, with independent spec/ABI-derived tests and separate review. Retain reported failures/partial state and explicitly unproven coherence; DECODED is not acceptance.
Consequence: no firmware, pins, limits, locked tests, native run, upload/capture admission or human gate changes. Later collection must preserve raw bytes and bind exact deployed identity independently.

D-173 actual outcome 2026-09-25T07:19:13.636532+04:00: FILE-OBSERVED, scope consumed. Execution089de986/evidence cc9f50c6; one transport/fivechildren exit0/reaped,26remote+120local checksPASS. Runner2592B/alignment8, symboloffset0 in2632B BSS, all10type layouts and exactloader196B/BSS32/92 verified. Separate actualreview60fdc78ePASS; compactABI822c917d independently matches raw GDB. No upload/reset/MCU read; next D174offline decoding. See analysis/P7_motor_fault_abi_validation.md.

D-174 final host outcome 2026-09-25T07:22:47.577059+04:00: source68653597/f6e2fd36 unchanged; independenttest b2995dea/frozen7712ae0b passes22/22 firstexecution0.825s, sevenpins exact. Separate fresh-context same-model reviewefe5a39ePASS. All source fields/64calls/4results,208enum/367bool/eightfloat locations and partial/failure states covered. No firmware/native/locked-test changes. See analysis/P7_motor_fault_decode_validation.md; decoder is structural only, coherence UNPROVEN.

## D-175 (2026-09-25T07:27:50.665982+04:00, closed diagnostic upload preparation under D051)
Context: D172 active inert compilation, D173 exact ARM ABI and D174 offline decoder pass review. A bounded fresh file-only observation deployment_files01 confirms raw/exported ELF extents29836B and config/loader identities; no MCU operation. Existing uploader is restricted to historical static app profiles.
Decision: implement analysis/P7_motor_fault_upload_contract.md as one per-instance closed dynamic diagnostic selection in the existing loader-cap uploader, preserving all legacy behavior and command/evidence bounds. Independent public-contract tests and separate review precede completion.
Consequence: host preparation only; profile selection is not artifact-origin proof or run permission. Exact native bindings/prerequisites/capture preparation and a separately identified inert scope remain necessary. No firmware/locked-test/limit/pin or old consumed-manifest change.

D-175 outcome 2026-09-25T07:35:20.576695+04:00: source/oracle67eccbc5 unchanged; new34PASS, legacy55+59+3PASS, harmless filelimit4PASS. Historical run02 ownership19PASS/1FAIL retains its consumed old sourcepin23661c8a; independent review1317cc4f confirms expected snapshot mismatch, no behavior regression or manifest/assertion change. All12pins exact. HOST-TESTED only, native0. See analysis/P7_motor_fault_upload_validation.md. Next finite dynamic capture profile; no old run may be reused.

## D-176 (2026-09-25T07:38:51.718499+04:00, bounded inert capture preparation under D051)
Context: D175 closed uploader is host-tested/reviewed; observed ARM2592B Runner and2632B BSS require a finite relocated capture before another inert run.
Decision: implement analysis/P7_motor_fault_capture_contract.md using the existing collector primitives and real bounded find_bss, with independent source-derived tests and separate review. Preserve raw snapshots, full flash/relocation bracketing, explicit UNPROVEN coherence, legacy behavior and consumed manifests.
Consequence: host preparation only; no upload/reset/MCU read, new motor permission, firmware/config/locked-test change or inferred physical gate. Use compact source/receipts and serial RAM fixtures while disk space is low.

D-176 corrective scope 2026-09-25T07:47:06.244936+04:00: initial38independent tests PASS4.247s; separate source review4eddcdb5 found twoMAJOR inherited finalization issues. Apply analysis/P7_motor_fault_capture_finalization_contract.md to preserve600s total and first-child-failure evidence, including later cleanup diagnostics. Add independent supplemental regressions before shared lifecycle repair; keep original tests/source/review and failure receipts. No new board action or relaxed requirement.

D-176 outcome 2026-09-25T07:55:04.381581+04:00: IMPLEMENTED/HOST-TESTED source7b7e8c69/95b0344d. Initial38PASS; independent8-method regression reproduced34failing subcases after source review4eddcdb5. First source repair passes8+38+46methods, fourteenpins exact, finalreview93ef66a7PASS (reviewer context reused); bothMAJORs closed. Original draft/FAIL/negative receipts retained; expectations unchanged. Native0, no human gate. See analysis/P7_motor_fault_capture_validation.md.

## D-177 (2026-09-25T10:51:35.504088+04:00, thin inert action composition under D051)
Context: D175 upload and D176 capture primitives are independently tested/reviewed; prior full-disk interruption prevented the final thin integration. The user resumes with the board disconnected.
Decision: implement analysis/P7_motor_fault_actions_contract.md as host-only source-pinned command composition, bounded response admission and conditional callbacks, reusing existing APIs/transport rather than cloning a native launcher. Inline sources use standard-library bounded bz2 framing to fit Windows commands; three previously observed installed capture modules remain independently pinned.
Consequence: no board call, upload/reset/capture, firmware/pin/config/locked-test change, historical scope repinning or acceptance claim. Installed bz2/current board identity and actual native scope remain pending; independent controlled tests and separate review are required before use.

D-177 first tested-source corrective scope 2026-09-25T11:01:55.266944+04:00: frozen oracle6c9c264b gives45PASS/1FAIL (current sys.dont_write_bytecode can be false despite startup-B flag); separate reviewer agrees to require both, retaining assertion. Actual full upload composition exceeds the unchanged30000UTF16-unit bound (30598), while capture25155 fits. Add only canonical b85:-prefixed base85 transport fallback when the original base64 command is too long, with the same payload/hash/bz2/framing and command ceilings; original small base64 behavior and46tests remain unchanged. Author independent additive codec tests before repair execution, preserve original failures838fa1f1. No board/API/firmware or consumed-scope change; implementation remains host-only.

D-177 outcome 2026-09-25T11:08:31.211321+04:00: HOST-TESTED source58d32dda/8ffb65c0. First tested-source repair passes all46 unchanged original methods plus16 independent codec methods;11pins unchanged. Actual production upload/capture commands28,989/25,231UTF16 units fit the unchanged30,000 ceiling. Separate reviewb1de6217/c40c9436 PASS; original45PASS/1FAIL and size rejection retained. Native calls0, board disconnected, no firmware/locked-test/gate change. Exact next task and limitations in CODEX_HANDOFF.md.


## D-178 (2026-09-25T12:34:54.715887+04:00, offline capture error preservation under D051)
Context: user requests continued host work without hardware; a separate context reproduced error.json ENOSPC masking the original D090 CaptureError and partial path.
Decision: adopt analysis/P7_dump_error_retention_contract.md. Preserve primary failure, existing evidence and CLI failure status while exposing any secondary journal failure; one best-effort write, no retries or cleanup. Independent additive regression tests and separate review precede closure.
Consequence: host Python-only repair for original P7 log preservation; no firmware, native action, limits, old source pins, locked tests or physical/human gates change. Synthetic storage failures are explicitly labeled.

D-178 first repair adjudication 2026-09-25T12:42:46.874077+04:00: sourcecb4c0d73 gives11PASS/2FAIL in13 new methods. Retain first output; fix source primary-message prefix. Separate source reviewer and independent spec-only author identify the other failure as new json.dumps-vs-json.dump fixture/order error; approve only streaming prefix/TypeError injection and exact one-open/retained-prefix expectations described in analysis/P7_dump_error_retention_failure.md. Original draft90471804/failures retained, every established/locked assertion unchanged; no production serialization change to accommodate the fixture.

D-178 outcome 2026-09-25T12:46:14.434284+04:00: IMPLEMENTED/HOST-TESTED/REVIEWED source3f73fd58/baca4d79.13new+45selected existing Python tests PASS/no skips; ordinary error.json bytes unchanged,5task+11priorD177pins exact. Review7649fb58 PASS. Original failures and independently adjudicated new-fixture correction011b2394 retained; every established/locked assertion unchanged. No native/build/firmware/gate change. Exact evidence/remaining board dependency in CODEX_HANDOFF.md.


## D-179 (2026-09-25T12:53:18.540214+04:00, host preparation of fixed inert caller under D051)
Context: D177 composition and conditional APIs are reviewed, but their actual caller can be prepared offline before hardware returns. Existing CompileOnce.prerequisites hardcodes a historical boot; old scopes must remain untouched.
Decision: adopt analysis/P7_motor_fault_caller_contract.md. Reuse existing pinned local-ownership helpers and unbound transport; bind later fresh expected identity with exact non-boot baseline comparison, fixed command allowlist and durable single-use upload/capture ownership. Independent tests and separate review before native eligibility.
Consequence: implementation and controlled host validation only now; no real run scope, owner, query, upload, capture, firmware/config/locked-test change or gate. Board verification and a new identified scope remain future tasks.

D-179 first oracle adjudication 2026-09-25T13:08:16.5537417+04:00: first44methods42PASS/1FAIL/1ERROR retained02d7e9ee; separate reviewer and spec-only test author agree two new fixture errors. Correct dangling-owner case to fresh instance with exact link retention, and max11 case to prescribed full sequence then twelfth rejection; keep pin-drift and pre-exhaustion allowlist negatives. Source d8418fad/8b47b1d6 unchanged; no established/locked tests or limits altered. Details analysis/P7_motor_fault_caller_failure.md. Freeze corrected oracle before execution.

D-179 outcome 2026-09-25T13:11:28.7376621+04:00: IMPLEMENTED/HOST-TESTED/REVIEWED unchanged source d8418fad/8b47b1d6.44 independent methods PASS after two independently adjudicated new-fixture corrections6e3d69c8; original42PASS/1FAIL/1ERROR retained02d7e9ee.24pins exact; Windows28,990/25,232UTF16includingNUL fit30,000; missing scope exits1 before process/owner. Separate review dbd4c2e4/d67c0dca PASS; no existing/locked assertion, firmware, old scope, physical/human gate or device action changed. Next fresh board admission/new scoped inert attempt when hardware returns.

## D-180 (2026-09-25T13:17:02.4409736+04:00, main-app setup binding under D051)
Context: fresh original-scope audit found app.ino's literal empty grants cannot be configured for final operation through config.h, despite D096 only requiring unconfirmed defaults. This is eligible offline integration, superseding the D179 handoff's no-further-offline-omission assessment.
Decision: adopt analysis/P7_setup_binding_contract.md: pure constexpr mapping of explicit config declarations to existing SetupGrants, connected only to main app; all shipped declarations false/zero/UNKNOWN. Independent tests and separate review precede closure.
Consequence: no physical fact, grant enablement, pin/button/default behavior change, bench guard change, old diagnostic repin/rebuild, motor/deployment permission or gate. Target compilation/actual setup remain hardware-pending. Existing consumer checks retain authority; no generic release framework.

D-180 outcome 2026-09-25T13:28:16.015271+04:00: IMPLEMENTED/HOST-TESTED/REVIEWED source70b9cea5; independent oraclead9bd19c first-run16PASS plus26unchanged legacy methods PASS/no skips. No source/fixture repairs; ten current/24priorD179pins exact. Separate fresh-context same-model review30f3927f/4e26ed27 PASS/no findings. All17grants remain0, axes unconfigured/originUNKNOWN; every prior value/pin/bench/locked assertion unchanged. Main-app target compilation and actual qualification pending; native0, no gate. Evidence analysis/P7_setup_binding_validation.md.

## D-181 (2026-09-25T13:53:39.630604+04:00, offline compiler evidence preservation under D051)
Context: user explicitly requests finishing without hardware. Actual controlled reproduction finds receipt stdout ENOSPC masks compiler exit43 as2 and prevents stderr retention.
Decision: adopt analysis/P7_compile_error_retention_contract.md, with independent regression on original source, bounded repair and separate review.
Consequence: tools-only failure handling; preserve original commands/permissions, historical pins, existing tests and actual hardware-pending status. This real offline task supersedes the prior no-further-task assessment.

D-181 original-oracle adjudication 2026-09-25T13:58:25.984762+04:00: source unchanged; frozen07d6d28a gives3PASS/2FAIL/22ERROR. Retain original output840ac831. Fresh reviewer independently confirms two new-fixture mismatches: command receipt omits encoding; successful None does not convert to empty. Correct only these test assumptions after independent author agreement, including fake Path non-str TypeError. Never change production successful semantics or established tests to satisfy them. Both actual CLI43->2 failures remain valid regression evidence.

D-181 final host outcome 2026-09-25T14:03:27.813702+04:00: source0d73967b passes27 independent methods plus33 unchanged executor/parser methods,60PASS/no skips. Two new-fixture corrections independently adjudicated; original3PASS/2FAIL/22ERROR and oracle07d6d28a retained. Source repair tested once; no established/locked assertion changed. Separate fresh-context same-model review acafc242 PASS/no findings, evidence7ad55b8c;4current/10D180/24D179pins exact. No compiler/native operation or gate. Next bounded current dynamic/Immediate MATCH deployment software.

## D-182 (2026-09-25T14:04:24.607864+04:00, offline MATCH upload adapter under D051)
Context: current documented dynamic/Immediate MATCH policy exists but upload source route is unimplemented; physical qualification is distinct from preparing guarded source. Frozen uploader safely owns the existing process lifecycle but accepts only historical inert profiles.
Decision: adopt analysis/P7_match_upload_adapter_contract.md. Add a versioned strict precompiled MATCH profile/initializer reusing unchanged uploader lifecycle, including actual packaged/exported byte equality. No historical pin changes, static adoption, new process/transport stack or native execution.
Consequence: independent contract-derived host tests and separate review required. Outer source/evidence/target/authorization integration remains next; this internal adapter is never a human run permission or hardware/phase acceptance.

D-182 new-oracle adjudication 2026-09-25T14:09:06.014735+04:00: frozen24c52d18 first35methods34PASS/1FAIL, outpute8095857 retained. Independent spec-only author and separate source reviewer agree sole __builtins__ deepcopy equality fixture defect. Keep all module names/object-identity assertions and all uploader data deep comparisons; replace only interpreter builtins deep equality with keys/entry identity comparison. No source change or established/locked assertion amendment. Freeze corrected new oracle before rerun.

## D-183 (2026-09-25T14:10:42.767794+04:00, offline guarded precompiled deployment under D051)
Context: D182 supplies the unchanged native upload lifecycle, while canonical tooling lacks identified MATCH deployment. Design audit corrects qualification target/runtime binding, reply request/build identity and exact schema before adoption.
Decision: adopt analysis/P7_match_deploy_contract.md, reusing board_tool transport and frozen uploader. Add explicit scope-only precompiled route, current-source/build/evidence bindings, one-hour maximum human authorization receipt lifetime as a conservative tooling bound, and one consumed attempt with independent closing checks. No scope/qualification/human permission is authored now; record files cannot authenticate human provenance.
Consequence: independently authored host tests/fresh separate review before software closure. No hardware/network/compiler/upload, static adoption, new process stack, gate or firmware/test weakening. Generic MATCH refusal and compile-only safety persist. Real current-session human run authorization and same-artifact physical qualification remain future requirements.

D-182 outcome 2026-09-25T14:11:57.344739+04:00: source72950615 unchanged; corrected independent oracle41c596ee passes35methods/no skips. Original34PASS/1FAIL retained80c7d11a and independently adjudicated builtins fixture correction preserved. Fresh same-model reviewcdbff1d5 PASS/no findings;6current/10D180/24D179pins exact, firmware/locked/progressprefix unchanged,0native. Evidence analysis/P7_match_upload_adapter_validation.md. Next D183 actual outer integration, not an authorized run.

D-183 first-run adjudication 2026-09-25T14:22:05.657120+04:00: source396e3359/oracle721e090b yields59PASS/4FAIL (output89c96b3d). Retain original source/oracle/results. Independent reviewer and spec-only author identify open-call-only ENOSPC fixture miss; reviewer identifies in-process bootstrap missing required isolated flag. Approve narrow fixture injections/flag modeling with all assertions retained. Separate review identifies actual success-save error lacks UNKNOWN/attached outcome, Windows resource import fails, and policy JSON rereads bypass checked snapshots. Repair source: preserve primary errors/UNKNOWN plus outcome_write finding; isolate five frozen pure binding defs and replace exactly two policy JSON read ASTnodes with checked strings. All other code preserved; add independent public regressions. No established/locked test or historical pin change, no native action.

D-183 final host disposition 2026-09-25T14:34:30.259403+04:00: caller69bb9981/payload8a1c8523/comment-only35e86452 IMPLEMENTED/HOST-TESTED/REVIEWED.66independent WSL and26Windows methods PASS,60unchanged compiler/parser cases previouslyPASS; fresh same-model review76fbc5ef has no open material findings. First59/4 errors and oversized30303/30289units retained. Representation-only repair gives29919/29904units with strict30000per-request guard; source-aware realistic supplement accurately labeled.18current/6D182/10D180/24D179pins checked; originalfreeze-label and two Git newline differences explicitly mapped in integrity.json, no historical bytes rewritten. Evidence24d94bb4. No firmware/locked changes, native operation, real approval/scope, qualification or gate. Offline route complete; fresh board/current target build/inert diagnostic and physical/human acceptance remain dependencies.

## D-184 (2026-09-25T15:57:57+04:00, connected inert diagnostic continuation)
Context: the user explicitly reconnected the board and requested continuation plus storage cleanup, superseding the prior offline-only instruction. Fresh admission observes boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 and matching CLI inventories/capabilities.
Decision: follow analysis/P7_motor_fault_run01_plan.md with the unchanged D179 caller and D172/D173 exact source8f592937 artifact, MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1. Commit fresh scope and separate review, check local admission, then one bounded upload plus conditional capture and independent closure. No changed firmware, old scope reuse or automatic retry.
Consequence: native experiment, not physical acceptance, human gate or motor permission. Preserve first connection stderr/assertion, all failed/partial observations and compact receipts. Current main-app compilation remains separate.

D-184 outcome 2026-09-25T16:13:06.920927+04:00: execution133f77bc completed exactly one inert upload and capture;11transports0/empty stderr, all independent closing checks PASS. Two2592B snapshots hash8805ee82 agree: COMPLETE/failureNONE, four valid inhibited zero-output applications,41 successful callbacks and confirmed halt/STOPPED6. Raw retrieval matches four report/snapshot hashes; coherenceUNPROVEN. Separate reused same-model actual review2e5ba8ac PASS, no material finding. This isolated dynamic run did not reproduce or resolve D160/D161 static full-app IO failure. No firmware/pin/limit/locked change or physical/human gate. Scope/owner consumed; next current-source checked app compilation. See analysis/P7_motor_fault_run01_validation.md.

## D-185 (2026-09-25T16:14:06.912492+04:00, current main-app compile-only qualification)
Context: D184 completed the isolated inert diagnostic; D180 current main-app source37a2099f has no checked target build. Generic flash staging would remove the protected old app stage, and the historical bounded executor binds an older boot/helper source.
Decision: adopt analysis/P7_current_app_compile_contract.md (initial SHA2562f2c90d58913c208aadef126733e465d4bf6de249b5065147e2ff870391174d4) under existing delegated D051 engineering authority. Compose unchanged stage(attempt=...), compile_app(command_runner=...) and pinned existing executor AST definitions in a private namespace. Separate fixed bench/default and MATCH/Immediate compile-only owners, canonical source/build roots, current source/tool/boot pins, bounded serial children and independent closing checks. Independently derive controlled tests and separately review before execution.
Consequence: no firmware/behavior/pin/tunable/locked-test change, upload/reset/native motor run, installed dependency repair, old scope/global mutation or denied cleanup retry. MATCH compilation grants no upload permission; physical/human gates and full-app startup/RAM/WCET remain open. Preserve failed attempts and compact evidence.

D-185 new-fixture adjudication 2026-09-25T16:22:59.620692+04:00: first source97a730a1/oracle41658123 run executes27 methods with five errors in four methods, all rejecting synthetic empty file_sha256. Separate reviewer independently identifies fixture mismatch against checked compile_app receipt schema. Preserve original oracle2895a5e6 and test_run01.json; independent author to verify and supply required synthetic installed/artifact hashes, with every assertion retained and no production/locked-test change. Freeze corrected new oracle before rerun. Supplemental five inherited-write failure tests723bc6b1 frozen separately before execution.

D-185 scoped-review disposition 2026-09-25T16:27:14.220832+04:00: corrected independent27methods PASS on source97a730a1; original supplemental five guard cases retain four missing-source-ownership fixture errors and one impossible simultaneous-write expectation. Independent author/reviewer adjudicate only new fixture corrections, preserving originalcc53ecd8/06d644e4 and every reached-failure assertion. Source reviewer found one minor missing plain ADB ancestry check; add exactly plain(Path(ADB)) before hashing (sourceaed3fbf4), then rerun final suites. No historical/locked test, executor body or compile policy changes.

D-185 final host outcome 2026-09-25T16:46:42.705781+04:00: final sourceaed3fbf4 passes27+7 independent controlled methods, durable receipts6bf5c9c9/49823ae6. Separate reused-context same-model review94fff07d PASS/no open findings; not a fresh phase-gate review. Both actual115-pin manifests and final freeze match current bytes. Actual ENOSPC and lost RAM receipt limitations preserved; original failures/new-fixture adjudications retained, no established/locked test change. Native0, no physical/human gate. Exact recovery and next clean-head compile-only action in analysis/P7_current_app_compile_validation.md.

D-185 bench actual result 2026-09-25T16:55:17.532077+04:00: reviewed34eb56ba completes one bench/default compilation, query1/compiler1/227transports, all7closing checks PASS; no upload/reset. Build6d9e48f8 binds current source37a2099f; rawELF72a8bfcd and package5b400268 equal D139, debugELF differs. Reuse only existing file-derived model/import conclusions under identical pinned loader:592B modeled deficit remains, no fresh ABI/live RAM/WCET claim. Native bench owner consumed; separate MATCH owner remains unused. Evidence analysis/P7_current_app_compile_raw/bench01_binding/.

D-185 MATCH actual result 2026-09-25T17:03:54.198450+04:00: reviewed80c059f7 completes one MATCH/Immediate compile-only, query1/compiler1/21transports, all7closing checks PASS; no upload/reset/run. Build1fcc7d57 binds source37a2099f; rawELFcb5fbb53/package004d51bf equal D138, debug2245bacd differs. Reuse only same-loader byte-derived allocation/import conclusions: conditional864B span/860B largest payload, no fresh ABI/live RAM/WCET acceptance. Both native owners consumed; no automatic retry or human gate. Evidence analysis/P7_current_app_compile_raw/match01_binding/.

## D-186 (2026-09-25T17:13:18.455868+04:00, inhibited full-application diagnostic under D051)
Context: D160/D161 static full-app I/O fault is not explained by D184's successful dynamic isolated Gate trace. D185 current compilations confirm unchanged firmware bytes and existing default allocation deficit.
Decision: adopt analysis/P7_app_motor_fault_contract.md and its public header. Add a default-disabled bench that composes the existing Trace with the actual Runtime, fixed empty peripheral/service grants, first-failure/pre-abort evidence and a four-completed-epoch bound. Add only exact shared-trace staging and pre-I/O generic-route refusal; native reproduction requires separately qualified static artifacts/layout/attempt.
Consequence: no shipping Runtime/core/HAL/config/timing/wiring/locked-test change, synthetic Robot command, target action, old-scope repin or human gate. Independent contract-derived tests and separate fresh-context same-model review precede closure. All existing failures and physical/RAM/WCET blockers remain evidence; hardware origin is never inferred from host fixtures.

D-186 pre-execution source-review correction 2026-09-25T17:17:19.788409+04:00: fresh D186 reviewer found oneMAJOR in b14c207a: shared trace sources rejected reparse paths but ordinary new-bench/project source traversal did not. Preserve initial review in reviews/P7_app_motor_fault_initial_review.md. Add new-sketch-only lstat/reparse tree and ancestry validation before copies; keep legacy behavior and every existing assertion. Independent author adds Windows reparse refusal coverage before oracle freeze. No test/native execution yet.

D-186 first-run adjudication 2026-09-25T17:26:33.135270+04:00: frozen c1f8d8f6 yields normal and ASan/UBSan13/14cases each, sole stalled-clock reason expectation mismatch (23882/23883assertions); other3driver methodsPASS. Original receipt retained. Separate reviewer and independent author agree contract priority3APPLICATION_INVALID follows Runtime-abort receipt invalidation before priority4RUNTIME_TERMINAL. Correct only new stalled-clock reason, add explicit decision_made/invalidated-feedback assertions; all other expectations preserved. New oracle588acb99 frozen before rerun; source and7other pins unchanged. No established/locked test, requirement or firmware change.

D-186 host outcome 2026-09-25T17:32:14.102604+04:00: IMPLEMENTED/HOST-TESTED/REVIEWED source539bfbb0, corrected independent oracle80eb359b;14cases/23885assertions normal and sanitized, scoped final reviewc41c6be1 PASS. Source-reparse finding closed; original first-run expectation/import-invocation errors preserved. Staging cross-platform skips explicitly recorded, actualWindowsjunctions exercised.67legacytooling/18legacyGate cases pass, eight pins/protected paths unchanged. No established/locked test, firmware/config or native change. Full22target historicalD162 record remains historical, not rerun. Next fixed static adapter retains old helpers/admission/byte checks before separately reviewed native work.


## D-187 (2026-09-25T17:33:58.596536+04:00, fixed static diagnostic adapter under D051)
Context: D186 is host-tested/reviewed; its new sketch is deliberately excluded from dynamic/generic tooling. Existing D141/D147 checks are frozen to original app filenames/flags.
Decision: adopt analysis/P7_app_motor_fault_static_contract.md: one offline fixed metadata/artifact adapter reuses exact historical checks in a private namespace with explicit expected-name/flag substitutions and seven-file alias map. Preserve raw inputs, source pins, flat export equality and every other rejection.
Consequence: independent frozen tests and fresh separate review before closure. No compiler/transport framework, board_tool/dynamic admission change, historical mutation, actual source/runtime qualification or native action. Fixed native compile composition remains next.

D-187 pre-execution design clarification 2026-09-25T17:35:30.918564+04:00: fresh reviewer confirms84templates/24project/5flag replacements and allfourpins; notes library wording broader than inherited D141. Preserve original behavior explicitly: compiled-result validation rejects external/malformed libraries, properties-only preflight leaves used_libraries uninterpreted. Clarify contract before source/oracle freeze, no new behavior or weakened inherited assertion. Nested common/reference loads must use checked snapshots in private namespace.

D-187 first-run adjudication 2026-09-25T17:44:53.249821+04:00: firstWSL33methods14reparse subFAIL/1helperERROR; Windows28methods24ERROR, originals806a3603. Independent reviewer/worker/root observe allfourplain dependencies stable within APIs but different Windows path/fstat ctime. Approve narrow sourcefix3e5d49e4: retain fullwithinAPI stamps and fullLinuxcross, exclude only Windowscrossctime; no hash/plain/reparse/size/identity relaxation. Independent author/reviewer identify newfixture pathdefaults and ineffective os.lstat-only injection; oraclee6d52ec6 passes BUILD/DATAexplicitly, intercepts both nofollowstat routes and asserts injection. Every original assertion retained; no established/locked amendment.12pinsrefrozen/10unchanged before rerun; originalobservations/failureskept.

D-187 host outcome 2026-09-25T17:48:25.099627+04:00: corrected39eac0a1 source3e5d49e4/oraclee6d52ec6 HOST-TESTED/REVIEWED;33WSL+28Windows methodsPASS/no skips, fresh same-model review1bc4b4db PASS. Bothfirstreceipts/statobservations retained; independent newfixturecorrections and Windows-onlyctime repair preserve priorchecks/10otherpins.12current/Gitpins exact; historicalsource/genericadmission/firmware/locked tests unchanged,0native. Next fixedcompile-onlycaller usesexistingboundedexecution and thisadapter; no actualscope or hardwarequalification created.


## D-188 (2026-09-25T18:00:27.471063+04:00, fixed static diagnostic compile-only caller under D051)
Context: D186/D187 are host-tested/reviewed; current full-app native IO fault remains open and hardware acceptance is deferred by the user.
Decision: adopt analysis/P7_app_motor_fault_compile_contract.md. Implement the fixed inhibited diagnostic caller using private pinned D185 execution and D187 validation, a fresh future manifest/attempt, exact static commands and bounded remote artifact observation. No new process framework or generic admission.
Consequence: freeze independent contract tests before execution, verify controlled failures and real command-size composition, obtain separate review. No actual manifest/board action, upload/reset, motor permission, changed firmware or human gate is created. Original source/evidence and denied cleanup paths stay intact.

D-188 first caller fixture adjudication 2026-09-25T18:12:42.063300+04:00: caller_first.json retains36setupERRORs at the new fixture class-level git_state patch; no testbody ran,134pins unchanged. Independent author/reviewer/root agree contract declares owner seams and implementation binds preserved D185 methods per instance. Approve moving only this new fixture patch into owner() after construction. Also correct its not-yet-reached CalledProcessError first_error expectation from stderr substring to exact type/message; preserve original exception identity, stderr and FAILED assertions. No implementation, established or locked test change. Freeze corrected new oracle before rerun.

D-188 second caller run 2026-09-25T18:17:03.667277+04:00: corrected40methods yield39PASS and one hard-pin subcaseERROR; all134pins unchanged. The first fixture issue is resolved. New case evaluates self.owner().check before its rejection helper, so correct legacy hard-pin constructor refusal escapes assertRaises. Independent author/root agree to wrap construction+check in one lambda; this retains identical rejection requirement and allows the earlier safer refusal. Source unchanged; preserve caller_corrected1.json and refreeze only this new fixture correction.

D-188 host closure 2026-09-25T18:21:12.104829+04:00: source6b6c883b unchanged after execution, finalcaller oraclead9f771a40PASS and remotee200477c14PASS/no skips. Separate fresh-context same-model reviewe6557e61 PASS;134pins/17ownedGitblobs exact, protected diffempty, Windowsactualcomposition29664units/zero dispatch. Original two new-fixture failure causes and ENOSPC preserved, established/locked tests untouched. No actual manifest/native operation or human gate. Next requires fresh hardware admission when deferred target work resumes; original full-app IO fault remains unresolved.

D-188 connected execution preparation 2026-09-25T19:00:10+04:00: later user instruction reconnects the board and resumes hardware work. Proceed with the already reviewed fixed static/default/M0/probe1 compile-only contract using fresh identity observation and new manifest; same observed boot is acceptable only because freshly read, not reused as an assumption. No protected behavior/pin/test change, upload/reset or motor-capable permission. Host-only wording in the frozen contract records its original development scope; this is its separately reviewed native-use preparation.


D-188 actual result 2026-09-25T19:11:07.512225+04:00: reviewed65b6d80e completes one fixed static diagnostic compile-only execution exit0;1query/1compiler/236transports,8closingPASS. Source21df6ae8/ELF2f8dc9f1/flatdeb40317 and all inputs/dependencies bound unchanged. Separate reused-context same-model actual review PASS/no material findings. Owners consumed, no upload/reset/MCUread. Next actual file-only ABI observation precedes distinct inert run scope; original full-app IO fault and physical/human gates remain open. Evidence analysis/P7_app_motor_fault_compile_actual_validation.md.


D-188 file-only ABI follow-up 2026-09-25T19:14:40.120096+04:00: after actual compile closure b54b76f9, adopt analysis/P7_app_motor_fault_abi_scope.md. Reuse pinned D173 file reader and private D185 transport for four actual file-tool queries; new native_abi_static01 owner, source21df6ae8/artifact/boot bindings and clean reviewed HEAD. No MCU read/connection, compiler/upload/reset or binary download. Initial separate source review found a closure-write error could mask the original failure; repair before any native execution, preserve first-error evidence and validate controlled paths. No firmware/locked or historical-helper changes. Actual types/addresses remain unknown until observed; later initialization audit and distinct inert run scope remain separate.


D-188 actual ABI interpretation 2026-09-25T19:19:17.201789+04:00: original90f2815c file-only invocation exit1/local symbol parser error;4nativechildren exit0/all remote and localclosingPASS. Unique readelfsize0x29708 is valid169736B, equal GDB Runner size; separate reviewer independently confirmed cause. Preserve consumedowner/originalfailure/reader. New offline interpreter6a990871 canonicalizes only unique size token in private copy, keeps originalbytes/hashes and unchanged summarize;16controlledchecks and actualinterpret exit0, no native repeat.19typepairs/10boundedwindows observed, no runtime inference. Evidence analysis/P7_app_motor_fault_abi_actual_validation.md.


## D-189 (2026-09-25T19:22:48.322656+04:00, new exact-artifact inhibited full-app diagnostic run preparation)
Context: D188 compiled new source21df6ae8/static/default/MATCH0/MOTORS_ALLOWED0/probe1; actual file ABI supplies six4536B windows. Earlier isolated D184 did not explain original full-app IO fault. User connected bare board and requested continuation; no motor-capable permission or human gate follows.
Decision: adopt analysis/P7_app_motor_fault_run_contract.md for a minimal private adapter around unchanged existing upload/capture lifecycle and a later exact-source/boot/artifact/init/review scope. One fixed upload selects rawBIN18598e13 and programs siblingflatdeb40317; conditional passive capture uses26reads727088B with full flash identity brackets and two small SRAM samples. Preserve inherited limits, first failure, exclusive owners and no retry.
Consequence: independent contract-derived tests frozen before execution, separate source review, actual new entry/global-initializer file audit and fresh native admission precede use. Contract alone performs no board operation. Do not reuse consumed old owners, change firmware/locked tests/limits, infer acceptance, download redundantbinaries or create a generic framework. Root owns local scope/sequence/ledgers; worker owns only fixed remote adapter.


D-188 entry file-query preparation 2026-09-25T19:25:32.330750+04:00: use new analysis/P7_app_motor_fault_entry_scope.md and helpercb9ee5bb, preserving original ABI helper and failedowner.27numeric ranges2654B and initializer bytes derive from observed symbols;9explicit private literal substitutions retain original boundedfilequery path. Separate reused-context source reviewPASS after exactbytecoverage correction,19parserchecks and localcompositionPASS/0native. Actual cleanHEAD query and semantic review precede D189run. No firmware/locked/helperhistorical change.


D-188 actual entry observation 2026-09-25T19:30:15.155741+04:00:252988828 cleancheck/nativeexit0,1transport/4children/27ranges2654B,allclosingPASS. Separate reusedcontextsemanticreviewPASS/no concreteunknowninitializer/hardwareAPI issue; priorunchanged constructor sources distinguished from newinstructionaudit. Ownerconsumed, no upload/reset/MCUread. D189adapter/source/test work maycontinue; actual runneeds fresh localbinding/review. Workerremote.py held10518B unchanged then restoredexactly, no remainingholdfile. Evidence analysis/P7_app_motor_fault_entry_actual_validation.md.


D-189 source-review/scope refinement 2026-09-25T19:31:49.922118+04:00: remoted796489f noBLOCKER/MAJOR; inheritedMINOR descriptorcloseerror disposition recorded in reviews/P7_app_motor_fault_remote_source_review.md. Preserve immutableoldlifecycles; isolatedprocessclose and strictoutererror+durablereport retention required, never reinterpret posterrorreport as success. Contract explicitly names inherited analysis.flash shape beforeoraclefreeze. Four-inlinepayload composition exceeds30000Windowsunits; choose exactexclusive staging of only10518Badapter at /home/arduino/sumox26_codex_build/app-motor-fault-21df6ae8-run01-adapter/remote.py, retaining3olddepsinline/boundedframing and descriptor/hashchecks before/after. Partial/uncertainstaging consumesattempt, no overwrite/retry. Localcallercontract/tests/reviewstillrequired,0native.


D-189 remote host closure 2026-09-25T19:36:05.465523+04:00: remoted796489f/spec-only independentoracle44f7651b firstexecution26PASS/no skips,12pinsunchanged. Separate reusedcontextsource/actualreviewPASS; inheritedcloseMINOR disposition retained forstrictouterhandling. Explicitanalysis.flash contractclarification beforefreeze, noimplementation/testrepair. Originalhelpers/firmware/lockedtests unchanged,0native. Fixed stagedadapter localcaller/action preparation follows under publiccontract; no actualscope/runpermissiongate created.


D-189 first caller execution 2026-09-25T19:48:42.338640+04:00: actions13PASS, caller19/20PASS; solechanged-upload-sketch-SHA preparation admitted locally. Original run_test01/freeze139pins preserved; remote rejection does not satisfy local preclaim contract. Repair implementation only with exact localbindingprojection/check; preserve independent oracle and original helpers. No native staging/upload/reset/capture. Evidence analysis/P7_app_motor_fault_caller_failure01.md.


D-189 caller host closure 2026-09-25T19:54:22.470215+04:00: unchanged independentoracles actions13/run20PASS, remote26PASS unchanged. Localbindingrepair d0f0e0d0 beforeclaim; firstfailure ef7f91d7/52bb346f retained,141pinsstable. Separate reusedsame-modelreviewPASS/noopenBLOCKERMAJOR. Freshreadonly19files/identity/owners admissionPASS; actualpreparation12pins/scope11pins ready for review and one static/default/MATCH0/MOTORS0/probe1 upload/conditionalcapture. No motor-capable approval, firmware/testchange or humanphasegate. Evidence analysis/P7_app_motor_fault_caller_validation.md.


D-189 actual run01 2026-09-25T19:59:56.229089+04:00:31170b08 checkonly0/execute1,9transports cleanclosures; stagedadapter but uploaderadmissionrefused preexisting/tmp/remoteocd beforeclaim/CLIchild. Capture0, noflash/reset/MCUread. Exactoriginalfailureandownerpreserved/consumed; no retry. Readonlyinspection identifies3candidateD184scratchcopies/no nativeprocess; cause/provenance reviewbeforecleanup orfreshscope. Evidence analysis/P7_app_motor_fault_run01_validation.md.


## D-190 (2026-09-25T20:02:22.725554+04:00, separately reviewed fresh inert run after stale scratch recovery)
Context: D189run01 rejected beforeCLI because/tmp/remoteocd contains exactD184scratchcopies; originalowner/failure preserved f9152f33.
Decision: adopt analysis/P7_app_motor_fault_run02_contract.md underD051: descriptor-bound exact3file obsoletecopy cleanup withoriginals retained, then one fresh independentlyvalidated run02 using metadata-only sourcevariants, sameM0firmware andunchangedabsence/deadline/safetychecks. Retain59projectedoracles andaddmetadata/original-run rejection checks beforefreeze/execution.
Consequence: no oldownerreuse, automaticretry, helper/firmware/lockedtest amendment or motorcapablepermission. Actualcleanup, freshadmission andseparatereviewrequired; collection doesnotprovephysical/humangates.


## D-191 (2026-09-25T20:36:16.724862+04:00, human-assisted exact scratch cleanup preparation)
Context: the user reconnected the board and requested continued work. Fresh read-only ADB identity matches the D188/D189 boot. Previously unrecorded cleanup01 returned1 before any deletion because same-UID adbd PID637 denies FD/cwd inspection; current sudo-n read-only query also returns1/password required.
Decision: preserve cleanup01 and D189run01 as consumed failures. Complete D190's frozen host validation, and prepare a minimal human-invoked root02 wrapper under D051 with independent tests/review. It pins original cleanup/helper bytes, runs all deletion and original identity/content checks as UID1000, and temporarily uses the human-granted saved UID0 only for read-only process inspection. Strengthen exactly one private observer exception: missing readlink propagates to the existing PID existence check, rather than accepting surviving missing metadata. No other original check changes.
Consequence: agent may stage reviewed exact files but cannot execute the privileged cleanup because board authentication is unavailable. Request one concrete sudo command only after review/staging. No password search, PID exemption, permission/service change, board reset, firmware upload, motor permission or phase gate. Failed/uncertain cleanup prevents fresh run02; original helpers/tests remain unchanged.


D-190/D-191 outcome 2026-09-25T20:45:19.208771+04:00: independent author/root/reviewer agree two new-fixture repairs only: private oracle alias context retains stdlib pwd identity; fake stat/fstat return snapshots. Every original assertion/source/helper preserved. Final62+37methodsPASS, reviews/P7_d190_d191_final_review.mdPASS. Three source files staged only; privileged cleanup requires human terminal authentication. No native-run02 scope or hardware/gate claim. Frozen run02 count is147total/146unchanged plusdriver, correcting freeze02 prose.


D-191 authentication authorization 2026-09-25T17:59:04.856436+00:00: user explicitly supplied board authentication to proceed with the already prepared cleanup. This supersedes only the earlier authentication-unavailable/human-only invocation restriction. Unchanged source4192f23e, fresh exact stage/boot verification and separate reused-context review support one sudo-S-H isolatedPython-I-B invocation with credential via stdin only, exclusive result and70s bound. No credential is recorded; no general privileged access, source/guard change, motor permission or phase gate follows.


D-191 actual outcome 2026-09-25T22:01:32.975637+04:00: unchangedroot02 completed once, resultc0e45b30 independently locally inspectedPASS. Exact2334244B scratchcopies removed, originalsunchanged, three170-name/3sameUIDhandle scans and permanent privilege drop successful. Other-userFDcoverage limitation remains; no hardware qualification. D190 freshadmission verifies sameboot/fullidentity19pins and three absent owners plus scratchabsence; createonlymetadata-derived preparation_run02/scope and separatelyreview before oneM0nativeattempt.


D-190 actual outcome 2026-09-25T22:12:15.468980+04:00: existing run02 completed once at reviewed b3e584d1 with unchanged source21df6ae8/static/default/MATCH0/MOTORS0/probe1. Scope and owners consumed. Interpret saved pre-abort state before intentional-abort faults: EPOCH_LIMIT4, RUNNING/NONE,41 successful callbacks; no initiating fault observed. Preserve historical D160/D161 fault as unresolved; no safety-limit or production change is justified by this short successful run. Next define a longer bounded inhibited first-failure observation without trace overflow, with separate tests/review/new artifact and scope before any execution. No motor permission or human gate follows.


## D-192 (2026-09-26T00:52:48.114238+04:00, longer inhibited application observation)
Context: D190 completed four epochs without reproducing the original IO fault. Existing Trace independently retains first_failure/current after its64-call prefix fills.
Decision: adopt analysis/P7_app_motor_observe_contract.md under D051. New small Runner composes unchanged Trace and Runtime, explicitly reports prefix truncation/loss, stops on first callback/timing/application/runtime failure or finite10000epoch/10000000poll bounds. Two new config count constants are naming exceptions; all old values/sources/locked tests remain unchanged. Independent contract-derived tests freeze before execution.
Consequence: this is host-only preparation; no new physical grant, relaxed150us safety limit, old native owner reuse, motor permission or gate. New static target compilation/artifacts/ABI/identity/review required before separate native execution.


D-192 host outcome 2026-09-26T01:05:05.688830+04:00: first implementation and independent oracles pass. Final board_tool LF normalization changes only line endings (equal AST); affected staging tests rerun unchanged. Runtime traces, locked safety and historical diagnostics pass normal/sanitizer checks. Preserve one coordinator filename error and all first receipts. New compile-only D193 projection is the next task; no native source/artifact/run scope yet.


## D-193 (2026-09-26T01:07:15.736360+04:00, fixed static observation compile projection)
Context: D192 host observation is validated in ade88fc0; its changed source needs a new checked target artifact before any new capture. D188 already has a reviewed bounded compile lifecycle.
Decision: under D051, adopt analysis/P7_app_motor_observe_compile_contract.md (0301726f), one new launcher with exact original and projected hashes/counts, and private reuse of unchanged caller/policy/remote code. Preserve original on-disk pins/self.code, fixed M0/static/default/probe1 flags, full source/identity/owner/closing checks, and new unused compile owner. Independent frozen oracles and separate review precede native admission.
Consequence: no lifecycle copy, generic/dynamic admission change, motor permission, compile success, runtime qualification or human gate is inferred. A pre-execution source review found a bootstrap FIFO-swap hang; repair nonblocking open and pre-read descriptor validation without changing the contract, then test the unchanged refusal requirements.


D-193 host outcome 2026-09-26T01:18:25.052911+04:00:94Linux/75Windowschecks pass,19Windowsplatformskips explicit. Independently adjudicated WinError1314 was fixture construction before subject; retainoriginal9eb8c9c7, splitonlynewmixedlinktest soeveryhardlinkassertion runsWindows andeveryrealLinuxlinkassertion remains. Source70e1 unchanged. Supplementalactualprojectedremote/adapter validation closes reviewercoverage finding. Newsource3a08ddeb manifest/read-onlyadmission prepared foronefreshcompile-onlyattempt afterfinalreview/cleanHEADcheck; no upload or gate.


D-193 actual outcome 2026-09-26T01:31:58.826012+04:00: one fixed compile-only attempt succeeded atb5f589c5, result24d12778/artifacts5ceba77d; all8closingchecksPASS and128sourcepinsunchanged. Ownerconsumed. No production adoption, upload/runtime claim or change to historical IO fault; next separate D194 file-only ABI/entry evidence before newfinitecapture.


## D-194 (2026-09-26T01:33:29.470097+04:00, observed application file-only ABI projection)
Context: D193 produced checked static source3a08ddeb ELF2fd70da8/debug33e3b34d; D192 adds Report.polls and needs actual new layout before any finite capture.
Decision: under D051 adopt analysis/P7_app_motor_observe_abi_contract.md SHA889d6a76. One new wrapper privately projects exact unchanged D188 reader bytes, reuses only pinned normalizer definitions and D193 projected caller, strengthens pre-read descriptor checks, observes polls through member expressions, and keeps raw readelf unchanged while interpreting decimal/0x size privately. Independent frozen contract-derived tests and separate review precede actual admission.
Consequence: retain all old owners/pins/readers, four file-only children/deadlines,128MiB localgate and closingchecks. No compile/upload/reset/MCUaccess, guessedpadding/address, firmware change, motor permission or physical/human gate. Current localspace belowgate permits only small hostpreparation until independently resolved; do not retry earlier denied cleanup paths.


D-194 new-oracle adjudication 2026-09-26T01:40:17.662253+04:00: independentauthor and separate reviewer both identify the sole first-run assertIs(layout) failure as unsupported object-identity assumption; contract889d6a76 requires contentpreservation. Preserve original43PASS/1FAIL/oraclefcbb950e in974de230. Author may replaceonly that newmethod assertion with content equality and addoriginal-layout snapshot/preservation check, retainingallotherassertions. No source/contract/establishedtest change; refreeze before rerun.


D-194 host outcome 2026-09-26T01:43:00.541970+04:00: correctednewfixture passes44Linux/42Windowsmethods, twoWindowsskips coveredLinux; unchangedwrapper297eac8b/contract889d6a76 and135finalpins. No nativeclaim or newphysicalevidence. ActualABI query awaitsunchanged128MiB storageadmission and finalreview/cleanHEAD; no bypass or deniedcleanupretry.


D-194 Windows portability amendment decision 2026-09-26T08:32:10.227613+04:00: actualcheck-only5b6f2b27 stopped beforeowner/board on pinnedADB.exe. Independentpassiveaudit andCPython3.13.11 posixmodule/fileutils prove pathname-only synthesized0111 for case-insensitive .exe/.bat/.cmd/.com. UnderD051 permit the explicitcontractcorrection: retain exactmode equality, additionally accept onlyWindows ordinaryfile eligibleextension where path_mode==(fd_mode|0111) and xor==0111, withallothercrossAPIfields exact exceptexistingctime rule. Fullrawmode sameAPI stability, links/type/attributes/size/identity/hash andbefore-read checks remain. Preserve source297eac8b/contract889d6a76/firstpreflight inGit; independentlyfreezeandrun newregression againstoriginal before source/contractrepair. Existing44oracle requiresonly metadataCONTRACT_SHA update afteramendment, no assertionremoved/weakened. No nativeowner consumed, hardware/firmware/gatechange or safety bypass.


D-194 attempt02 query amendment 2026-09-26T08:40:50.176347+04:00: one actualfile-only attempt01 failedstrictly on GDBalignof(member-expression) syntax; preserve97dd06b7/e83afc5f and consumedowner. Actualmemberptypeunsignedint is observed, no alignment valueguessed. UnderD051 adopt supplementarycontract772615cd: newabi02wrapper privatelycomposes unchanged497f reader, changesonly newSELF/localremoteowner/scope and ALIGNsubject to observedunsignedint; currentmemberptypecheckedagain before inheritedsummary. Preserveallpriorfiles/tests/strictstderr/closure/bounds. Independentcontractoracle/freeze/source-review required before one freshfile-onlyattempt02; no firmware/motor/phasepermission.


D-194 entry observation adoption 2026-09-26T08:50:24.160991+04:00: ABI02acceptedresulta5e67635/ABIdfc34596 andactualreviewe9c8d255 establishcurrentfilelayout. UnderD051 adopt entrycontract437f8cb8, with27ranges/boundsconfirmedfromsuccessfulrawreadelfb3542b0d. Newentrywrapper privatelyreuses ABI02lifecycle andoldentryparser throughcount/hashchecked literalchangesonly, sixinputs beforeexecution/exact5bootstraphelpers. Source/testindependence, frozenhostresults andseparatereview precede onefreshfile-onlyentryscope. Arraybytes/instructionsemantics remainunobserved untilactualquery/review; noMCU/firmware/phasepermission follows.


## D-195 (2026-09-26T09:02:46.330577+04:00, fixed longer inhibited observation capture preparation)
Context: D193 artifact and D194 actual ABI establish six observer windows; the longer finite diagnostic needs a bounded observation interval.
Decision: under D051 adopt analysis/P7_app_motor_observe_remote_contract.md c2563449. Preserve D190 source and lifecycles, apply exact observer metadata only and one recorded 30-second wait before the first SRAM read; retain the 2-second separation, 26 reads, 600-second budget, exclusive owners and first-failure evidence. Independent contract-derived tests and review precede native admission.
Consequence: host preparation only. Caller/action validation, actual entry review, separately bound scratch cleanup and fresh exact inhibited-run scope remain required. Delay does not prove terminal state; no motor grant, changed firmware policy, physical evidence or human gate follows.


## D-196 (2026-09-26T09:03:35.890692+04:00, exact current upload scratch cleanup)
Context: fresh read-only inventory20db3c25 sees three D190 upload copies, 2399736B, in directory device34/inode869; D191 old cleanup is consumed. User requests continued connected-board work and supplied authentication.
Decision: under D051 adopt analysis/P7_app_motor_observe_cleanup_contract.md7258230a. Prepare only exact metadata-derived recipe1834edd3/wrappera089cc3b, new exclusive observe-root03 stage/result, retaining all original content/use/identity/privilege-drop guards. Independent frozen oracles and separate review plus fresh staged-source binding precede one specifically scoped authenticated invocation.
Consequence: no general privileged access, credential storage, old-owner retry, process exemption, firmware operation, motor permission or phase gate. Preparation is not deletion evidence; uncertain or failed execution is preserved without automatic retry.


D-195 caller extension 2026-09-26T09:06:42.000938+04:00: adopt analysis/P7_app_motor_observe_caller_contract.md03b61d0c. Preserve D190 caller/action lifecycle, exactD193128pin projection through load_caller, successfulABI02 evidence and newfixedowners. Validate recorded30swait ordering before unchanged2sgap; retain strictbindings/staging/firsterrors/13transports/deadlines. Independentoracles/review then freshpreparation/scope required; no executionauthorized by hostpreparation alone.


D-195 actual outcome 2026-09-26T09:35:15.664942+04:00: one fixed inhibited run atclean10be3126 completed collection and reproduced SETTLE failure atapplication921. Source3a08ddeb is latestflashed; scope/ownersconsumed. Preserve result4fc33583, raw3bb9425f, decodedc37a3069 andactualreviewf8779db4. PreabortRUNNING/NONE but invalidIOmotorreceipt; explicitabort explains finalfaultlabels. FinalHALTsettle alsofalse/inhibitionunconfirmed. Outer154us is not internaldeadline evidence because successfulSETUP also154us. Keep150us/4096pollbounds; nextminimalprobe must classifyexactbranch without extra hardware/clockcalls. No rootcausefix, productionWCET, physicalacceptance or gate follows.


## D-197 (2026-09-26T09:36:07.021364+04:00, internal native SETTLE exit observation)
Context: D195 actually reproduced SETTLEfalse atapplication921, but its outer154us span cannot distinguish seven internalrejections; successfulSETUPalso154us. FinalHALTsettlefalse leavesinhibitionunconfirmed.
Decision: underD051 adopt analysis/P7_motor_settle_probe_contract.md3346b119. Add only probe1 fixed28B separate current/first_failure report and return-site recording in motor_port_unoq.cpp plus oneheader. Preserve exactproductionprobe0 preprocessedsettle, existing hardware/clockcalls, shortcircuits,150us/4096polls, config/pins/lockedtests/Trace/Runnerlayouts. Use only existing elapsed/poll/fresh observations with explicit validity; no extra clockread, resetAPI or inferredsubcause.
Consequence: independentlyauthored tests freeze beforeimplementationread/execution, separate source/hostreview and newtargetartifacts/ABI/entry/scope before any nativeuse. This is diagnosticpreparation, notrootcausefix/guardrelaxation/physicalqualification/motorpermission/phasegate. Productionstaticcompile remainslaterwork.


## D-198 (2026-09-26T09:44:38.617576+04:00, fixed compile-only metadata scope for D197)
Context: D197 adds a separate28B probe-only report to the existing observer source; D193oldcompileowner isconsumed and its artifact has no suchreport.
Decision: underD051 adopt analysis/P7_motor_settle_compile_contract.mdc0b35281. New7570B launcher privately preservesD193/D188 behavior through exactmetadata substitutions; unchangedapp_motor_observe sketch/mapping/adapterstatus/staticdefaultMATCH0MOTORS0probe1, newapp-motor-settle-static01 owners andschemas. Existing srcinventory includesnewheader. Independentold59+35assertions plusdeltaoracles/review required.
Consequence: D197hostclosure andfreshmanifest/admission precedeonecompile-onlyattempt. Keepjobs1/query60s/compiler720s/reap5s/128MiBhost1GiBboardgates/allpins andclosingguards. No upload/reset/MCUread/oldownerreuse. ActualnewABI/entry/retention andlaterseparatecapture stillrequired; no rootcausefix/productionRAM/WCET/motorpermission/gate.


D-197 independent harness adjudication 2026-09-26T09:46:17.685977+04:00: firstLinux run stoppedlink-original before anytest/currentimplementation compile because newharness omitted unchangedopp_fusion.cpp defining motors.cpp'sfrontView dependency. Preserve originaloracle8d8f9e82/freeze136pins/receiptstderr e51481d3 in c7fa1679; no requirement/sourcefailure inferred. Independentauthor/reviewer agree minimalcommon-link dependency+pin correction only, no assertion/contract/firmware change. Existinglocked disabled/enabled suitesalreadyPASS76cases217020assertions/noskips with136pinsunchanged. Refreezecorrectedoracle andnewoutputowner before firstrunofcorrectedharness.


D-197 interface-fixture adjudication 2026-09-26T09:49:17.480561+04:00: dependency-corrected run proves21scenarios acrossoriginal0/current0/current1 exact, probe0preprocessedbody/symbols unchanged,4of5methodsPASS. Solefailure atnegativefixture expects accessor-name diagnostic butprobe0headerproperlyomitsmotorsnamespace, so compilerrejectsearlier. Preserveoracle451762cf/results573a3f6a ina0ccf86d. Independentauthor/reviewer authorizeonlyincluding unchangedmotor_port_unoq.h beforeaccessoruse todeclareexistingnamespace, preservingallassertions andseparateinertguardinput. Firmware/contract/C++cases unchanged; refreeze/newownerrequired, unexecutedinertguardcombinations stillpending.


D-197 host outcome 2026-09-26T09:52:54.246983+04:00: exactimplementationf1ee755a/2eced554 andunchangedcontract3346b119 passindependent5methods/21x3differentialruns plus76lockedcases217020assertions. All140pinsstable; reviewbe2ff77ePASS. DiagnosticvolatileRAMpublication retains firstfailure without extra hardware/clockcalls; productionprobe0preprocessedbody/symbolsexact. Twoharness-onlyfirstfailures remaininGit, no assertionorproductionrepair. No newnativeimage/address/retention/cause observed; D198compilethenactualABI/entry/capture remain.


D-198 host outcome 2026-09-26T10:04:25.022331+04:00: exactsourceb98a5f54 passes102Linux/81Windowsmethodswith21explicitplatformskipscoveredLinux,167pinsstable. Firstnewstagingfixture omitted claim/stage afterprepare; preserve4c61913e, correctonlycontrolledfixturelifecycle+coupledhelperhash/allassertionsunchanged. Admission01extrainventorynlink1 restriction wasunnecessaryforinstalledhardlinkedcompiler; originalD193predicate restoredonlyinreadonlyadmission02 afterstablemetadata/hashproof, noproductionguardchange. Review50a276b9PASS. Exact129pinmanifestaa314548/source117cc0e7 prepared; newfixedcompile-onlyscope/cleanHEAD precedeexecution. No nativeartifact/faultrepair/gatecreated.


D-198 actual outcome 2026-09-26T10:16:08.181213+04:00: the single fixed compile-only attempt succeeded at clean18c1135c, with one compiler/one query and all eight closing checks. Result9b7f0c44 and artifactse18384c1 bind the new source117cc0e7; all129 manifest pins remain unchanged. Independent reviewf046db47 confirms complete source/tool/artifact closure. Consume app-motor-settle-static01; do not retry. Target report retention/layout/stores require new file-only evidence before a separate inhibited capture. No firmware upload, altered settle bound, physical qualification or gate follows.


## D-199 (2026-09-26T10:21:03.805944+04:00, file-only target SETTLE report ABI and later entry evidence)
Context: D198 compiled the D197 internal probe, but its target report layout, retention and publication instructions have not been observed.
Decision: under D051 adopt analysis/P7_motor_settle_abi_contract.md dfc76276. Privately compose the unchanged D194 ABI02 lifecycle with fourteen count-checked substitutions, fixed D198 evidence, three used types before report_.polls, and sixty-two appended expressions (223 total). Require an observed separate LOCAL OBJECT, exact fields/enums, initialized-BSS containment and no Runner overlap. Keep all eleven Runner windows. Freeze independent tests before their author's implementation read, then validate/review before one fresh file-only owner. Entry ranges must wait for this image's actual symbol table.
Consequence: initial contract a0e96100 is preserved in d04234dc. Before implementation/tests, root and independent reviewer removed six queries for unused inline constexpr masks: compiler debug visibility is not guaranteed, and masks are source semantics rather than ABI. No claim those symbols are absent, no failed query fallback and no weakened implementation/test assertion. Preserve 150-us/4096-poll limits, compiler flags, firmware, all lifecycle/error/identity checks and physical gates. No MCU read, upload or root-cause claim follows from file evidence.


D-199 pre-execution source review 2026-09-26T10:25:10.687750+04:00: root and independent reviewer found that three literal sites in initial wrapper6faa240e produce runtime newline bytes in the31 added GDB echo arguments, while contractdfc76276 and inherited queries require literal backslash-n. Preserve this initial source before repair. Change only those three string literal spellings; no contract, expected result, test assertion, query meaning or lifecycle change. No test or native execution has occurred. Independent oracle author remains isolated from this implementation finding until their freeze.


D-199 first host result and fixture coverage review 2026-09-26T10:28:21.949647+04:00: corrected source0f2b37c9 passes all66 Linux methods and64 Windows methods with one symlink-privilege and one Linux-FIFO skip, both covered on Linux; all190 frozen pins stay exact. Separate review found that appending the synthetic report last redirected an inherited duplicate-Runner subcase onto the report. Preserve oracle04f4ed14/freeze9b54d114 and first passing receipts before repair. Independent author/reviewer agree two fixture-only changes: insert the report before the existing final Runner row, and make the new report-specific test select its exact PROBE_SYMBOL row with uniqueness asserted. Retain all assertions/66 methods and production bytes. New frozen receipts will establish restored coverage; no native execution or query fallback occurred.


D-199 host outcome 2026-09-26T10:32:15.555509+04:00: source0f2b37c9 and independent oracle96763b42 pass66 Linux/64 Windows methods with two covered platform/privilege skips;192inputs stable and review076a9742 PASS. Preserve initial source bug and first fixture coverage gap with their original bytes/receipts; fixes retain contract/lifecycle/all assertions. Admit a fresh fixed file-only ABI scope after clean reviewed HEAD/check-only. Actual target report/global/fields and emitted stores remain unobserved; no upload, MCU read, timing limit change, physical gate or root-cause claim.


## D-200 (2026-09-26T10:35:35.875898+04:00, exact current uploader scratch cleanup preparation)
Context: one fresh nonprivileged inventorye95ebed4 observes exactly three D195 upload copies2399768B in /tmp/remoteocd device34/inode1172, all identical to retained D193/installed originals. D191/D196 owners are consumed. The user explicitly requested continued connected-board work and supplied authentication for the prepared cleanup workflow.
Decision: under D051 adopt analysis/P7_motor_settle_cleanup_contract.md6cb02590. Prepare only four-step recipe6afeea1b and six-step wrapper13f33327 metadata derivatives, with fresh root04 stage/result, preserving all process/content/identity/permanent-privilege-drop and exact user-owned deletion guards. Freeze independent oracles before their author's implementation read; source/host/staging review and fresh owner/board/file checks precede one specifically admitted authenticated invocation within the user's ongoing task authorization. Credentials may be supplied only through authentication stdin, never stored in files or argv.
Consequence: no general sudo grant, old-owner reuse, process exception, firmware operation, motor permission or gate. Draft24d849f2 is preserved in c1bb617d; pre-adoption clarification separates source-metadata/schema pin refusal from unchanged run_original's status-only JSON admission. The coordinator independently validates actual outer/nested receipt schemas and every success field; no new predicate or silently weakened oracle is permitted. Preparation is not deletion/process-use evidence, and uncertainty must remain visible without automatic retry.


D-199 actual ABI outcome 2026-09-26T10:38:09.109037+04:00: one fresh file-only attempt atclean23f0aeba succeeds withresult230ef847/summary069ed01b/localeb68ef2e and independent actualreviewa7c3993a. Report0x2003d3e8 is28B/align4/LOCAL OBJECT ininitializedBSS and separatefromRunner; allfieldoffsets/widths/reasons observed. Consume native_abi_static01; no retry or reuse. Derive next entry binding from this rawsymboltable: publishSettle range[0x08110d60,0x08110d9c), UnoQPort::settle[0x081115bc,0x081116e0), then inspect instructions separately. Symbols alone do not prove store order, execution or faultcause; firmware/150usbound/gates unchanged.


D-200 independent staged-observer finding 2026-09-26T10:46:41.390310+04:00: first read-only verifierf0ca0f68 failed KeyError(cleanup_remoteocd03.py) before a complete staged snapshot because its new stage_snapshot used recipe.inventory, whose content checks deliberately reference scratch-only global PINS. This is observer misuse, not evidence of source drift. Preserve original argv/receipt and first error before correction. No wrapper/recipe main, authentication, mutation or cleanup ran. Author/source inspection agree the sole repair is the original D196 explicit staged-file read/hash loop with full opening/closing stamps; recipe.inventory stays scratch-only. Permit one new separately named verification02 after this bounded correction; never overwrite01 or relax source/identity/result-absence checks. Actual invocation remains pending complete independent verification.


D-199 entry contract adoption 2026-09-26T10:49:56.692553+04:00: under D051 adopt analysis/P7_motor_settle_entry_contract.md af8ce726 and binding62346762, derived from accepted actual ABI230ef847/069ed01b/reviewa7c3993a. Prepare one private metadata-derived entry wrapper preserving file-only lifecycle, nine reader and36 parser substitutions,29fixedranges/31aliases/59expressions including actual publishSettle and UnoQPort::settle. Independent oracle freezes before author implementation read. Source/host review precedes fresh fixed file-only owner; actual initializer/instruction semantics remain unobserved. No upload, MCU read, guard change, motor permission or phase gate.


D-200 local input transport 2026-09-26T10:51:35.015224+04:00: plain host pipes returned EOF before credential input; launcher stopped at its input assertion before subprocess.run. Preserve cleanup_auth_input_failure01.json and the already saved immutable intent. Zero native authenticated invocations, no credential received or result owner created by this failed local launch. Use standard no-echo Windows console input for the same exact saved command; no change to target/pins/guards/one-invocation limit.


D-200 actual outcome 2026-09-26T10:56:13.468580+04:00: exact single root04 invocation succeeded, raw05507941/retrievalb7b776c9/actualreview5bc9d56dPASS. Precisely3copies2399768B andemptydirectoryremoved; allretainedoriginals/stagedsourcefullstamps/hashes verifiedunchanged; threeprotectedscans/errorfree/permanentUIDGIDtriples1000. Bothschemas/allactualfields independentlychecked. Originalreadonlyobserverfailure andlocalEOF-before-devicecall preserved; no guard weakened. Root04/resultowner consumed, no retry/generalprivilege/firmware/gate.


D-199 entry host outcome 2026-09-26T10:59:01.194294+04:00: first serial23Linux/23WindowsmethodsPASS/no skips,204inputpinsstable, independentfresh-contextreviewdcf1a079PASS. Admit only the fixed new file-entry scope after scope review/cleanHEAD/check-only; retain all lifecycle/identity/firsterror guards. Actual initializer/stores/nativeconditions remain unobserved; no firmwareoperation/limit change or gate.


D-199 actual entry outcome 2026-09-26T11:06:57.253762+04:00: single fixedfile-only attempt at5adbd784 succeeds, raw10d8a184/summary8332f797/localec4c45e9, actualreview20f54afaPASS. Observedinitializer points08100105; currentstoresprecedehas_current, failurestoresguardedbypreexistinghas_failure andprecedeflag atobserved2003d3e8. All7falseplusSUCCESS paths retain150us4096polls; selectedentryRunnerinertwiring/stops/passivityreviewed. Consume native_entry_static01; no retry. Fileemissiondoesnotestablishruntimecontents/cause/atomicity/WCET/physicalgate. Freshcapturecontracts/oracles/reviews/admission stillrequired.


## D-201 (2026-09-26T11:07:59.109709+04:00, bounded inhibited SETTLE capture preparation)
Context: D198compile/D199actualABI/entryreview20f54afa establish the new117cc0e7 image and separate28B report, but its runtimevalue remains unknown. D200cleanup iscomplete; allpriornativeowners consumed.
Decision: underD051 adopt analysis/P7_motor_settle_remote_contract.md6d245a4e and P7_motor_settle_caller_contract.md4a07cd9a with binding0a9d4a6a and currentfieldmap0faba243. Prepare exact11/9/17metadata derivatives only, preserving every D195native lifecycle/identity/error guard, sourcebytes/staticdefaultMATCH0MOTORS0probe1 and150us4096 limits. Read6currentwindows/26reads727432B withsame30s/2swaits/flashbrackets; replaceonlylivePrevious48 withseparateSettle28, retainingnestedpreabortPrevious/finalRuntimeTransactionGate. Independentfrozenoracles/sourcehostreviews precede fresh preparation/scope/cleanHEAD/admission and anynativeuse.
Consequence: no runtimecause/repair/atomicity/WCET/physicalgate ormotor-capable permission. Remote/callerprep doesnotexecute; no generalreset/read/sudo/retry/cleanup facility. A separatelyadoptedofflineinterpreter contract willpreserverawvalues/firsterrors/loss and distinguish completeformat, failedprefix andsemanticinconsistency withoutchangingnativeacceptance.


D-201 offline interpretation policy 2026-09-26T11:09:33.292674+04:00: underD051 adopt analysis/P7_motor_settle_interpreter_contract.md70070353 usingfixedobservedmap0faba243. Threepureseams decode/annotate_settle/interpret preserve all115selectedfields, rawnumericbytes, originalupload/capturereceipts andloss/firsterrors. Strictformat/linkage/bool/nonfinitef32 failures produceREJECTED; structurallyvalidfailedfixedprefix givesPARTIAL; completeformatgivesDECODED, nevernativePASS. Unknown/inconsistentpresence/reason/mask/reservedbytes produceorderedINCONCLUSIVE annotations, absentpayloadalwaysUNAVAILABLE, no atomicity/stage/epoch association. KeepcoherenceUNPROVEN. FixedofflineCLI requires-B andexplicitnewpacketSHA, boundedimmutableinputs/exclusivedecodedoutput; no sourceeditaftercapture forunknownhash. Independentoraclefreeze precedes implementationreview/execution; allnativeadmission remains separate.


D-201 decoder classification clarification 2026-09-26T11:12:39.527840+04:00: original70070353 preserved inad435841. Before independentdecoderoraclefreeze/sourceexecution, append exactcode distinctions for filemetadataranges/hashsyntax, nestedreceiptcontainers/keys, errorobjects, validbutfailed uploadfields, clock/wait records and missing/extra snapshot files. No acceptedpacket/sourcepredicate/annotation behavior changed. Amended interpretercontract6007ec4e2e22cdf0e8f751790c49924b26b4adb8f9dfde5d5f6db2ed9bd7dff8 is authoritative for both independentoracle andimplementation.


D-201 pre-freeze decoder interpretation 2026-09-26T11:16:55.909280+04:00: independentoracle author requested two remaining code classifications before anysubjectread/execution. Root confirms late saved-file/read-snapshot width orhash disagreement uses files/FILE_SIZE orFILE_HASH at file-row bytes/sha256 path, and complete correspondingflashchunk mismatch uses capture/STATUS at /capture_result after earlierflashflagchecks. Record theseinterpretations inindependentfreeze; contract6007acceptedpredicates unchanged. No observedtest/sourcebehavior used tochoose anexpectation.


D-201 first host results and bounded decoder correction 2026-09-26T11:30:07.352152+04:00: All 99 native methods passed on Linux; Windows passed 56 with 43 explicit Linux-only skips covered by the Linux run. Preserve the native freeze prediction typo (11 historical descriptor-free remote tests were already explicitly enabled on Windows). All 256 native input pins remained exact. Read-only admission02 checked current identity, 19 files, the exact completed D200 cleanup, retained originals, four absent paths and no recognized conflicting processes; no firmware operation occurred.
D-201 decoder first runs each executed 66 methods with 17 failure events, preserved in b69cc011 with original source and oracle. Fresh review identifies three implementation defects: reversed after-flash boundaries, premature count-member TYPE classification, and read-row field types classified as READ_PLAN. Permit only those contract corrections against unchanged 6007ec4e. A fourth issue is an oracle portability assumption: 2000 nested arrays are valid JSON and the local Python parser accepts them. Preserve deep-input rejection as KEYS when the independent standard parser accepts it, or JSON on actual RecursionError; add a controlled parser RecursionError case. Do not invent a depth limit, relax acceptance, alter any other assertion, or erase first failures. New frozen source/oracle bytes and serial Linux/Windows tests plus review precede diagnostic upload.


D-201 actual outcome 2026-09-26T11:47:14.501322+04:00: One fixed inhibited attempt completed at ff35c83e; rawfb529423, saved-file packete32415b2, decoded4d8383c3 and actualreview690a4164 establish SETUP_FAILED with lifetime FINAL_DEADLINE154us/poll5/fresh7 and later setup-cleanup SUCCESS132us/poll4. All owners consumed. This localizes the recorded rejection, not physical cause, atomicity or a remedy. Preserve D195's distinct921-epoch result. No bounds or safety checks changed.


## D-202 (2026-09-26T11:48:04.177041+04:00, compile-time expected motor metadata)
Context: independently reviewed D201 evidence690a4164 localizes the saved failure to FINAL_DEADLINE154us during setup. D199 saved file instructions retain runtime64-bit divisions in candidateRate/candidatePeriod, which derive only immutable DT/config values; this is a concrete emission opportunity, not proof of timing cause.
Decision: under D051 adopt analysis/P7_motor_expected_metadata_contract.md2abaae2995e1938e4c7f0dcef2522c9334d9550bd77d9da37727b47a7940a846. Permit only exact original math in constexpr expectedRate/expectedPeriod and three-scalar runtime selections within the original two-helper region. Supersede D197 helper-byte immutability only for this region; retain every byte outside, all live observations/count/order,150us/4096, report, pins/config/grants and locked/historical tests. Freeze an independent oracle before implementation inspection/execution; separate reviewer and serial host checks follow. Preserve any original D197 whole-symbol mismatch for explicit review, never force symbols or weaken its assertion.
Consequence: no new hardware assumption, timing benefit, runtime repair or gate is claimed. This does not authorize compile/upload against a consumed owner; any target build, ABI/entry or runtime attempt needs its own new fixed checked scope.


D-202 first host findings 2026-09-26T12:05:02.878295+04:00: Independent first oracle7methods has6PASS/1fixture compile failure: pinned predecessor with projected carrier0 receives GCC division-by-zero warning promoted by-Werror, despite its earlier zero return. All21four-way transcripts and36numericrows passed; no production defect established. Preserve original oracle2b8f66e3/freeze0ff50996/failedresult4d7b92a9. Independent author and reviewer agree to carrier_zero-only -Wno-error=div-by-zero identically for4variants, with exactly the expected visible warning required, allother-Werror/UBSan/zero assertions unchanged; no body/config/locked edits. Refreeze before rerun. Unchanged locked disabled/enabled suites PASS76cases217020assertions. HistoricalD197 remains4PASS/1FAIL on complete-symbol equality; display-only auxiliary retains full difference: removed read-onlyDOMAINS/SELECTORS and localcandidateRate, no additions. This is an explicitly reviewed D202 emission difference, never a D197PASS; review and full revised matrix remain pending.


D-202 host closure 2026-09-26T12:15:21.458124+04:00: Adopt final independent reviewf7b8a116 for the unchanged fdbc27d9 implementation. Corrected7methods/45four-waynumeric/21four-waytranscript checks pass, locked76cases217020assertions pass,154pins close unchanged. The zero-carrier fixture correction and original failure remain separate; exact three-symbol disappearance is explicitly accepted under the adopted narrow optimization contract while historicalD197 remains FAIL. Broad unittest discovery is therefore not wholly passing; document that boundary without filtering/weakening any assertion. Host acceptance permits preparation of a new fixed compile-only scope, not reuse of consumed owners, upload, timing claim or human gate.


## D-203 (2026-09-26T12:22:41.003548+04:00, fresh compile-only constant metadata diagnostic)
Context: D202 host implementation and independent reviewf7b8a116PASS close at d24620aa; currentmotor sourcefdbc27d9 and diagnosticmapping4bc3a2e6 differ from D198 only in the permitted helper region. All historical native owners are consumed.
Decision: underD051 adopt analysis/P7_motor_const_compile_contract.md318a6267f29a5837d6afe7197d6f86d88230886f1dd8ea0bb1af0345a4c75174 and data-only derivationd4c89cd5. Permit only ten exact metadata substitutions from D198 launcher to new tools/compile_motor_const.py7557B/957666a8, caller29874/bda40e96 and remote6893/914d4d11; adapter8266/e3d23d5c and every original bootstrap/lifecycle/resource/error/artifact guard stay exact. Fresh app-motor-const-static01 scope, same static/default/MATCH0/MOTORS0/probe1 observer. Independentoracle freeze before implementation review/execution; preserve all65caller/37remote methods and prior-owner negatives, addsettle refusal.
Consequence: this adopts preparation only. Newhostreview/freshactualmanifest/currentidentity/cleanreviewedHEAD and single-use owner checks precede one compile-only operation; actual ABI/entry/newinhibitedruntime remain separate. No upload/reset/MCUread, timinggain, physicalmeasurement or motor permission follows.
