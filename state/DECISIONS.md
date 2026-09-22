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
