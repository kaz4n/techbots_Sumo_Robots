# P2: Drivers and bench tests

**Goal:** every sensor and actuator works through its HAL module and passes a bench test on the assembled robot; the full firmware runs at 1 kHz with the flight recorder.
**Needs:** GATE P1 for integration. Each driver can start as soon as its part is wired, even on the bare board.
**Load:** AGENTS.md, docs/HARDWARE.md, docs/BEHAVIOR.md B13 to B15.

## Parallel tracks (one sub-agent per track; each owns its files)

| ID | Track | Files | Bench sketch | Pass criteria |
|---|---|---|---|---|
| B1 | Opponent sensors | hal/opp_sensors.* | bench/opp_view | LED matrix shows 7 live bits; polarity correct; each sensor detects the black test box at its set range (record ranges); 0 false hits in 60 s pointing across an empty ring |
| B2 | QTR line | hal/line_qtr.* | bench/qtr_raw | Parallel read of 4 sensors within QTR_TIMEOUT_US + 100 us; raw times logged on black, white border, brown line; clear gap between white and black on every sensor; brown reads black |
| B3 | IMU | hal/imu.* | bench/imu_heading | Bias calibration at rest; drift under 2 degrees in 60 s still; a hand-rotated 360 degrees reads 360 within 3; read time fits the tick budget |
| B4 | Motors | hal/motors.* incl. MotorGate | bench/motor_stand | Requires STAND OK. Each side: forward, reverse, brake, coast; MOTOR_EN LOW kills output within 1 tick; both wheels on a side turn the same way; PWM frequency matches FACTS; no driver fault with the chosen IBT-2 logic supply |
| B5 | Power | hal/power.* | bench/vbat | Within 0.05 V of a multimeter from 9.5 to 12.6 V (bench supply or packs at different charge) |
| B6 | UI | hal/ui.* | bench/ui | START and MODE distinguished on A1, both-held detected; mode cycling, service menu, and countdown shown on the matrix |
| B7 | Brownout | none | bench/motor_stand | Requires STAND OK. Half-charged pack, 20 cycles of full forward to full reverse; the uptime counter never resets |
| B8 | Recorder | hal/recorder.* | bench/recorder | 200 s at LOG_HZ fits in RAM (report the free RAM); tools/dump_match.sh yields frames and events CSV with no gaps |

## Then integrate
2.1 src/app/app.ino: setup (MotorGate LOW first, then UI, sensors, IMU), the 1 kHz scheduler, HAL reads, Robot::step, HAL writes, recorder, watchdog if FACTS.md says it is available.
2.2 Tick measurement: worst case and p99 over 5 minutes with all sensors live. Target under 800 us. Log it in TUNING_LOG.md.
2.3 MATCH flag: MATCH=1 disables all Bridge traffic except the log dump in IDLE.
2.4 QTR_CAL service mode works (B13).
2.5 Weigh the robot and check the footprint; log both.

## Exit gate (GATE P2)
- [ ] B1 to B8 pass on the assembled robot, with numbers in TUNING_LOG.md
- [ ] FACTS.md hardware-checked column updated
- [ ] Tick under 800 us worst case; zero resets in B7
- [ ] safety-auditor PASS; Codex review with no open BLOCKER; human writes `GATE P2 PASS`

## Do not
Run motors without STAND OK. Change pins (R8). Hide sensor polarity in code: it belongs in config.h.
