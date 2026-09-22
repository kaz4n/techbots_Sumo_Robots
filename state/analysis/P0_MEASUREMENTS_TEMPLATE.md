# P0 measurement worksheet — BLANK TEMPLATE, NOT EVIDENCE

Prepared 2026-09-22. No board was measured for this template. No pin approval,
motor authorization or phase gate is contained here. Copy to a dated run record
when measurements occur; preserve raw files alongside that record. Leave unknown
fields blank or `not measured`. Do not replace observations with vendor values.

Instructions: [P0 manual checklist](../../docs/P0_MANUAL_CHECKLIST.md).

## Record identity and setup

| Field | Actual observation / evidence path |
|---|---|
| Date/time/timezone and human observer | |
| UNO Q label/revision | |
| Source commit plus uncommitted changes; staged-source hash | |
| Physical isolation; all connections; photo path | |
| Supply/cable; actual rail readings; ambient/test conditions | |
| SSH alias or user@host; WSL authentication result (no secrets) | |
| Host-key algorithm/fingerprint and trusted verification method | |
| Read-only preflight JSON path and exit/result | |
| Installed image / CLI / core / loader / library versions | |
| Exact FQBN/build flags; compile log and result | |
| Inert upload log/result and source review reference, if performed | |
| Instrument/model, probe/setup, sampling rate and timing resolution | |
| Relevant interface/diagnostic decision ID, if any | |

## Inventory and existing wiring

| Part / instance | Exact board/IC marks / revision / link | Existing connections / actual supply | Photo/evidence | Unresolved |
|---|---|---|---|---|
| MPU6050 breakout | | | | |
| JS200XF FL / FC / FR (record individually) | | | | |
| MZ80 SL / SR / RL / RR (record individually) | | | | |
| QTR FL / FR / RL / RR (record individually) | | | | |
| IBT-2 left / right (record individually) | | | | |
| Power / battery sense / buttons | | | | |

## Display and received counter (separate results)

| Check | Actual result | Raw evidence |
|---|---|---|
| `SUMO` scroll observed on this source snapshot | | |
| SC-I decision and reviewed counter implementation | | |
| Receive-only logs command; first/last counter; gaps/resets | | |
| Default vs Immediate behavior | | |

A RAM counter does not count as received Monitor output. Counter fields remain
unmeasured until the approved transport exists and a real round trip succeeds.

## Cold startup: duplicate rows for each run

Immediate matrix execution remains pending installed-loader/matrix-ownership
verification (FACTS F-061). Start: power application. End: a precisely identified
sketch SUMO frame, never the loader boot logo. Record the marker's software/display
delay and distinguish display readiness from sketch entry. Record orderly
shutdown/cold-start preparation and method; do not substitute MCU reset time.

| Mode / exact FQBN | Run | Supply / preparation | Elapsed seconds | Method / resolution | Failure / raw evidence |
|---|---|---|---|---|---|
| Default | | | | | |
| Immediate | | | | | |

| Mode | Run count | Minimum seconds | Maximum seconds | Failures / limitations |
|---|---|---|---|---|
| Default | | | | |
| Immediate | | | | |

## Electrical pre-connect observations

Use only the reviewed, approved isolated measurement setup. This table defines
no circuit or pass voltage; each result needs comparison with the exact part and
approved interface limits. Keep sensor output disconnected from the MCU during
pre-connect measurements. Duplicate rows for all actual devices/states.

| Device / node | State / power sequence | Approved setup / load / reference | Measured min/max V / steady V | Capture / instrument | Reviewer result / unresolved |
|---|---|---|---|---|---|
| JS200XF output / interface node | | | | | |
| MZ80 output / interface node | | | | | |
| QTR OUT including startup/transients | | | | | |
| IBT-2 EN / logic interface, motors isolated | | | | | |
| Battery sense node, MCU disconnected | | | | | |
| Button node: none | | | | | |
| Button node: START | | | | | |
| Button node: MODE | | | | | |
| Button node: both | | | | | |
| MPU6050 supply / SDA / SCL | | | | | |

Open concerns: QTR VIN=5 V/3.3 V charge transient maximum unknown; START/both
alias in proposed ladder (SC-A); JS200XF range revision conflict; IBT-2 supply
D-013 pending. Measurements do not silently resolve or approve circuit changes.

## Timing results: raw evidence first

| Test / exact configuration | Count / elapsed time | Timing overhead | Min us | Max us | p99 us or bound | Errors / missed periods | Raw capture |
|---|---|---|---|---|---|---|---|
| Bare 1 kHz scheduler, matrix inactive | | | | | | | |
| Matrix-active scheduler, if measured | | | | | | | |
| pinMode | | | | | | | |
| digitalWrite / toggle | | | | | | | |
| digitalRead | | | | | | | |
| Four-pin QTR-style timeout, nothing connected | | | | | | | |
| analogRead | | | | | | | |
| IMU successful read | | | | | | | |
| IMU absent-address / approved fault path | | | | | | | |

- Raw RAM/histogram file, extraction method and hash:
- `p0Samples`, `p0MaxLateUs`, `p0OverPeriod` and actual elapsed duration:
- Histogram bin widths, overflow bin meaning and percentile calculation:
- Clock/micros resolution and wrap evidence:
- Interrupt/load conditions and limitations:

Current timing sketch: 60,000 samples; overflow bin means >=1000 us. Do not turn
that bin into an exact p99. Bare-loop jitter is not complete robot tick execution
time, and this is not the later five-minute M10 qualification.

## IMU and pin acceptance inputs

| Check | Actual configuration/readback or observation | Evidence / unresolved |
|---|---|---|
| MPU6050 breakout/interface approval and bus/address | | |
| Device ID; gyro range; filter/sample-divider readback | | |
| Genuine new-sample count / interval min/max/p99 | | |
| Gyro/accel units, axes and manual-motion observations | | |
| I2C transaction count/bus rate, fault return and stale handling | | |
| Installed source/devicetree matches proposed pin map | | |
| PWM pin/waveform/frequency/duty/API error observations, drivers absent | | |
| EN off/boot evidence and interface review | | |
| Remaining G1-G6 unknowns and proposed tests | | |

## Review disposition — fill only after real work

- Measurements performed / omitted and why:
- Actual unexpected results and follow-up:
- Human decision references (only those actually provided):
- Files to be merged into FACTS / PROGRESS / TUNING_LOG:
- Independent review reference and remaining blockers:
- Next action:

This template has no prefilled PASS, PINMAP OK or GATE P0 PASS field. Approval is
a separate human action after supporting evidence and the required review.
