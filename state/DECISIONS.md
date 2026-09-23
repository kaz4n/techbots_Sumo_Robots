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
