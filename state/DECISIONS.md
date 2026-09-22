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
