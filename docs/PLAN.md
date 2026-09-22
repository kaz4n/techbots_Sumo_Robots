# SumoX-26 Plan

Version 1.0, Tuesday 22 September 2026. Built from the team interview; every line here was confirmed by the team.
Humans decide. Agents read this file for scope, schedule, and gates, and never edit it without a human "yes".

---

## 1. Goal and success metrics

**Goal:** win matches at SumoX-26 (Dubai Techbots League, Saturday 3 October 2026, Canadian University Dubai) with a 3 kg robot that starts legally every time, never drives itself out of the ring, and fights with a hybrid flanking strategy. Evidence for the Best Programming and Best Strategy awards comes out of the same tests and logs.

**Priority order** (use it to settle every conflict):
1. Rule compliance (5-second hold, autonomy, no remote control, size, weight)
2. Ring survival (no self-exits)
3. Winning pushes
4. Award evidence (only as a by-product; polish only if time allows)

| # | Metric | Target | How we measure | Phase |
|---|---|---|---|---|
| M1 | Movement before the 5-second hold ends | 0 in 50 starts | Recorder: first nonzero duty time minus START release time | P3 |
| M2 | Self-exits in solo search | 0 in 20 runs of 60 s | Observation + recorder | P3 |
| M3 | Edge escapes from 8 approach angles | 24/24 stay in | Observation | P3 |
| M4 | Opponent box acquired from random placements | 9/10 within 3 s of GO | Recorder | P4 |
| M5 | Box pushed out, robot stays in | 8/10 | Observation | P4 |
| M6 | Lost-target test (box yanked away mid-attack) | 10/10 stay in | Observation + recorder | P4 |
| M7 | Spectator test (person 30 cm outside the edge) | 0 exits in 20 runs | Observation | P4 |
| M8 | Re-flank on a blocked push | 8/10 reach the box side | Observation + recorder | P4 |
| M9 | Sidestep against a charger proxy | 8/10 dodge + side contact | 60 fps video | P5 |
| M10 | Control tick, worst case | under 800 us | On-board measurement, 5 min | P2 |
| M11 | Brownout resets under motor reversal | 0 in 20 cycles | Uptime counter | P2 |
| M12 | Weight | 2,950 g, within 20 g | Kitchen scale, every day from P2 | P2 to P7 |
| M13 | Footprint | fits a 199 x 199 mm square, all parts attached | Box check | P2, P7 |

---

## 2. Locked decisions

Full records with reasons live in `state/DECISIONS.md`.

| ID | Decision | One-line reason |
|---|---|---|
| D-001 | 2 BTS7960 (IBT-2) boards, one per side, front and rear motor of a side in parallel | Each board drives one motor channel; 4 boards need 8 PWM pins and the UNO Q has 6 |
| D-002 | All real-time control on the MCU; Linux only builds, flashes, and stores logs | Determinism, boot time, and no radio in the control path |
| D-003 | Add an IMU on the Qwiic connector | Repeatable turns and arcs, stall and impact cues |
| D-004 | Sensor layout: 3 JS200XF front (0, left 15, right 15), MZ80 at left 90, right 90, rear-left 135, rear-right 135, QTR at the 4 corners | Covers the flank while we arc, and the rear where a flanker attacks |
| D-005 | JS200XF range pads soldered to 120 cm | Ring is 150 cm; less spectator detection |
| D-006 | UNO Q powered through a Schottky diode + 1000 uF hold-up; separate 5 V buck for sensors | A brownout reboot loses the round |
| D-007 | Hybrid flanking strategy with 4 openers in priority order, default SIDESTEP | Confirmed in interview |
| D-008 | Match performance first; award polish (P6) only if GATE P4 passes by 30 September | Confirmed in interview |
| D-009 | Claude Code builds and orchestrates; Codex reviews every gate; firmware built and flashed on the board over SSH | Avoids WSL USB passthrough trouble |
| D-010 | Stall detection = contact timer + IMU heuristics | No wheel encoders; an IMU cannot measure steady speed |
| D-011 | START and MODE buttons share one ADC pin (resistor ladder) | Frees a pin for a hard motor-enable line |
| D-012 | Search speed cap set from a measured stopping table | Top speed is about 2.7 m/s; stopping takes 20 to 30 cm; the white band is 3 cm |

---

## 3. Schedule and gates

Today is Tuesday 22 September. First drive on the ring: Saturday 26 or Sunday 27 September.

| Date | Humans | Agent | Gate |
|---|---|---|---|
| Tue 22 Sep | Order parts (section 4). Email organizers (section 5). Lock motor layout (HARDWARE.md section 6). UNO Q on Wi-Fi + SSH. | P0: fact checks in parallel, toolchain scripts, repo scaffold | |
| Wed 23 Sep | Parts arrive. Cut or print chassis. Solder dividers and harness. | P0 finish; P1 starts (core logic + tests on the laptop) | GATE P0 |
| Thu 24 Sep | Bench each sensor on the bare board as it arrives. One motor driver on a stand. | P1; P2 bench sketches for sensors | |
| Fri 25 Sep | Assembly and wiring | P1 finish; P2 drivers | GATE P1 |
| Sat 26 Sep | Finish assembly. Weigh. Run bench tests B1 to B8 on the robot. | P2 integration, flight recorder | GATE P2 |
| Sun 27 Sep | First drive: countdown proof, stopping table, edge escapes | P3 | |
| Mon 28 Sep | Solo reliability runs; start box tests | P3 finish; P4 | GATE P3, then GO/NO-GO |
| Tue 29 Sep | Box tests: acquire, push, lost target, spectators, re-flank | P4 finish; P5 SIDESTEP | GATE P4 |
| Wed 30 Sep | Opener tuning | P5 DIRECT, ARC; decide on P6 | |
| Thu 1 Oct | Opener tuning. Code freeze 21:00. | P5 WAIT; P6 if allowed; tag v1.0 | GATE P5 |
| Fri 2 Oct | Dress rehearsal. Judge pack. Charge packs. Pack spares. | P7 runbook, judge pack | GATE P7 |
| Sat 3 Oct | Competition | Config changes only, each with TUNING_LOG evidence | |

**Gate rule:** a phase closes when its exit criteria pass, the Codex review has no open BLOCKER, and a human writes `GATE Pn PASS` in `state/PROGRESS.md`.

**GO/NO-GO (end of Monday 28 September):** if GATE P3 has not passed, cut scope to the reactive core plus openers SIDESTEP and DIRECT. Drop ARC, WAIT, and all of P6 except the flight recorder.

**P6 rule:** P6 (judge pack polish) runs only if GATE P4 passes by Wednesday 30 September.

**Code freeze:** Thursday 1 October, 21:00. After freeze, only `src/config.h` values change, each with a `state/TUNING_LOG.md` entry.

---

## 4. Order today (local delivery, 1 to 2 days)

Skip any line you already own.

| # | Item | Qty | Why |
|---|---|---|---|
| 1 | 3S LiPo, 1300 to 2200 mAh, 30C or more, XT60 + balance charger + LiPo bag | 2 packs | Stall draw is about 24 A (4 x 5.9 A). Two packs let one charge while the other runs |
| 2 | IMU breakout with Qwiic/STEMMA QT, 3.3 V (LSM6DS3/LSM6DSOX/ICM-42688 class, or Arduino Modulino Movement) + Qwiic cable | 1 (+1 spare) | Heading for turns and arcs; impact cue. Fallback: MPU-6050 (GY-521) wired to the Qwiic pins |
| 3 | 5 V buck converter, 3 A (MP1584/LM2596 class) | 2 (1 spare) | Sensor rail separate from the UNO Q |
| 4 | Resistor kit including 4.7 k, 10 k, 18 k, 22 k, 100 k | 1 | Level dividers, pull-ups, battery sense, button ladder |
| 5 | Electrolytic capacitors 1000 uF 25 V; ceramic 100 nF | 4; 15 | Driver bulk caps, UNO Q hold-up, motor noise, ADC filters |
| 6 | Schottky diode 3 A (SS34 or 1N5822) | 2 | UNO Q hold-up isolation |
| 7 | Inline blade fuse holder + 30 A fuses | 1 + 3 | Short-circuit protection |
| 8 | Main switch rated 30 A or more (or an XT60 removable link) | 1 | Safe power-off |
| 9 | Momentary pushbuttons, panel mount | 3 | START, MODE, spare |
| 10 | Matte black spray paint | 1 | Blade and front must not be white (rule 4.5) |
| 11 | Wire: 14 AWG silicone (battery to drivers), 18 AWG (motors), 22 to 26 AWG (signals); heat shrink; XT60 pairs; JST or Dupont connectors | set | Harness |
| 12 | Blue threadlocker, zip ties | 1 each | Each detached part is a warning |
| 13 | Kitchen scale 5 kg / 1 g, multimeter | if missing | Weigh-in, pre-connect voltage checks |
| 14 | Test opponent: box about 20 x 20 x 10 cm, matte black paper on all sides, 2.5 to 3 kg of weights, 3 m of string | 1 | P4 and P5 tests |
| 15 | Ring materials (only if you lack a ring): 1.5 m plywood or MDF circle, matte black paint, 3 cm white border, brown tape for two start lines 20 cm long, 10 cm from center | 1 | Testing on the right surface |

---

## 5. Questions for the organizers (send today)

Email: dubaitechbotsleague@besomi.com

1. May robots be placed at any orientation behind the start line (for example angled 45 degrees), or must they face the opponent?
2. May the team change the robot's strategy mode between rounds using a button on the robot? (No component changes; rule 4.7.)
3. The Arduino UNO Q has built-in Wi-Fi and Bluetooth. Is it acceptable if radios are disabled during matches and used only in the pit for uploading code?
4. Is the arena raised? If yes, how high? Is the 3 cm white border painted or taped?
5. For the 5-second hold: does the referee count from the button press? Is a press-and-release start button acceptable as "activation"?
6. Which scale is used for the 3 kg weigh-in, and what tolerance applies?
7. Is matte black painted steel acceptable for the front blade under rule 4.5?

Record replies in `state/DECISIONS.md`. Answers 1 and 2 change the strategy (see section 6.5, A2 and A6).

---

## 6. Strategy

### 6.1 Summary

Hybrid flanking. The robot opens with a flank, engages head-on when it is well placed, and breaks off to re-flank when a head-on push stalls. Every behavior sits on a reactive core that always does four things: escape the edge first, never outrun its ability to stop, keep the opponent centered while pushing, and turn to face anything that appears at the side or rear.

Why hybrid: pure flanking loses to opponents that track us with side sensors, because they keep turning to face us and the round becomes circling near the edge. Pure head-on loses to a lower, sharper wedge. The hybrid keeps flanking as the signature move and still wins the rounds where flanking cannot happen.

### 6.2 Opener menu (tuning priority; drop from the bottom if time runs out)

| Priority | Mode | What it does | Best against |
|---|---|---|---|
| 1 (default) | SIDESTEP_R / SIDESTEP_L | Pivot about 50 degrees away, drive a short burst, turn in when the inner side sensor sees the opponent | Chargers, unknown opponents |
| 2 | DIRECT | Straight attack, full push on contact | Waiters, spinners, weak robots |
| 3 | ARC_R / ARC_L | Wide arc toward the opponent's rear, turn in on side-sensor contact | Waiters and slow turners |
| 4 | WAIT (matador) | Hold still up to 2 s; if the opponent closes in, sidestep and turn in; else hunt | Aggressive chargers with weak edge logic |

Every opener aborts into the reactive core the moment its abort condition fires (docs/BEHAVIOR.md B12). Left and right versions are mirror images of one definition.

### 6.3 Stress test: opener vs opponent type

`++` strong, `+` fine, `-` weak.

| Opener | Charger | Waiter | Spinner | Tracker | Heavy wedge | Weak or slow | Edge-careless |
|---|---|---|---|---|---|---|---|
| SIDESTEP | ++ | + | + | + | + | + | ++ |
| DIRECT | - | ++ | ++ | + | - | ++ | + |
| ARC | + | ++ | - | - | + | ++ | + |
| WAIT | ++ | - | + | - | + | - | ++ |

Reasons:
- **Charger:** it covers the 20 cm gap in about 0.2 s. SIDESTEP and WAIT take us off its line, and a fast charger with weak edge logic can drive itself out, which scores for us (rulebook section 8). DIRECT turns the start into a wedge-height contest we may lose.
- **Waiter:** it stays near the center and turns to face us. DIRECT and ARC reach it before it adapts. WAIT burns its 2 s cap for nothing.
- **Spinner:** it rotates to find us, then charges. DIRECT hits it mid-spin. ARC hands it time.
- **Tracker (side sensors, fast turns):** it keeps its front toward us, so any flank becomes head-on. DIRECT engages early; the re-flank breaks the stalled push.
- **Heavy wedge:** head-on we lose. SIDESTEP and ARC aim for its side. WAIT lets its momentum carry it past.
- **Weak or slow:** anything works; DIRECT finishes fastest.
- **Edge-careless:** evasive openers let it drive itself out.

### 6.4 Mode selection guide (print this card for match day)

| What you saw the opponent do | Pick |
|---|---|
| Charges straight at the whistle | SIDESTEP (either side), or WAIT |
| Waits, or turns slowly to face | DIRECT, or ARC |
| Spins in place scanning | DIRECT |
| Tracks well with side sensors | DIRECT (rely on re-flank) |
| Has a lower or sharper wedge than ours | SIDESTEP or ARC; never DIRECT |
| Barely moves | DIRECT |
| Unknown | SIDESTEP_R (default) |

Round 2 rule: lost round 1, change mode. Won round 1, keep the mode unless the opponent visibly changed its opening. Round 3: pick the mode that beat what they did in the round they won.

Scouting: whoever is not operating watches the opponents' earlier matches and fills one line per team: name, opening move, speed, wedge height, sensor coverage, edge behavior.

### 6.5 Hidden assumptions and how we validate them

| ID | We are betting that | Validation | If false |
|---|---|---|---|
| A1 | Many opponents charge at the whistle | Scout early matches | Default to DIRECT against non-chargers |
| A2 | SIDESTEP clears the charger's path in time (12 to 15 cm lateral move in about 0.25 s) | P5 test 5.2, 60 fps video | Pre-angled placement if organizers allow (Q1); else WAIT |
| A3 | JS200XF mounted 3 to 5 cm high sees a black robot at useful range and ignores the ring surface | P2 opponent-sensor bench | Adjust height and tilt; lean on MZ80 |
| A4 | IMU heading drifts under 2 degrees per minute after calibration in the 5-second hold | P2 IMU bench | Recalibrate in SEARCH pauses; fall back to timed turns |
| A5 | Grip and stopping on our ring match the competition ring | Re-check stopping at the venue if practice is offered | Keep the 70 % stopping margin |
| A6 | Changing mode between rounds is allowed | Organizer Q2 | Fix one mode for the day: SIDESTEP_R |
| A7 | Contact time without progress is a usable stall signal | P4 test 4.5 logs | Raise STALL_MS; enable the IMU refinement only if logs support it |

---

## 7. Architecture decision: the MCU fights, Linux keeps the black box

**Decision.** All sensing, decisions, and motor control run on the STM32U585 in a 1 kHz loop that never waits for Linux. Linux (Qualcomm QRB2210) builds and flashes the firmware on the board, receives the flight-recorder dump after a round, stores CSV logs, and runs plots.

**Why, in numbers.**
- **Edge timing:** at 2.5 m/s the robot crosses the 3 cm white band in 12 ms. The MCU loop sees it within 1 to 2 ms. Linux user-space scheduling gives no such guarantee.
- **Boot:** in default mode the sketch starts about 35 s after power-on because it waits for Linux. The Immediate startup option starts the sketch without waiting (P0 verifies).
- **Rules:** no radio in the control path leaves no argument about remote control.
- **Testability:** one loop and one state machine in plain C++, which compiles and runs on a laptop for tests and log replay.

**Judge one-liner:** "The MCU fights; Linux keeps the black box."

---

## 8. Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Build slips past 28 September | Medium | High | GO/NO-GO cut; bench sensors on the bare board early |
| Brownout reboot mid-round | Medium | High | Diode + 1000 uF hold-up on VIN; bench test B7; Immediate startup; good packs |
| 5 V sensor output damages a 3.3 V pin | Medium | High | Dividers and pull-ups; measure every output before connecting (HARDWARE.md section 9) |
| IBT-2 ignores 3.3 V logic | Medium | Medium | IBT-2 VCC from 3.3 V; bench test B4 |
| JS200XF sees spectators | High | Medium | 120 cm pads; low horizontal mount; phantom mask; speed governor |
| Self-exit at speed | High | High | Governor from the stopping table; approach duty below full until contact; lost-target braking |
| SIDESTEP too slow against chargers | Medium | Medium | Pre-angled placement if allowed; WAIT as the alternative |
| Head-on loss to a better wedge | Medium | High | Re-flank; mechanical: low knife-edge blade, weight at the limit |
| IMU drift or failure | Low | Medium | Bias calibration during the hold; timed-turn fallback |
| Toolchain friction (WSL, USB, SSH) | Medium | Medium | P0 on day 1; adb fallback |
| Rule interpretation (orientation, mode change) | Medium | Medium | Organizer email today |
| Loose part costs a warning | Low | Medium | Threadlocker, zip ties, pre-match check |
| Over weight or over size at inspection | Medium | High | Weigh daily; 2,950 g target; 199 mm box check |

---

## 9. Not doing (and why)

| Not doing | Why |
|---|---|
| Camera, vision, or ML | No payoff in 11 days; adds latency and failure modes |
| Linux in the control loop | Boot time, scheduling jitter, brownout exposure |
| 4 motor drivers | Pin count (8 PWM needed, 6 exist) and weight |
| Wheel encoders | Not in the parts list; no time to fit them |
| Full 2D physics simulator | Scenario tests plus ring time give more per hour |
| Live Wi-Fi dashboard during matches | Remote-control optics; post-match logs cover the need |
| Auto-resume after a mid-match reboot | Complex; the hardware fix is cheaper |
| Opponent learning or adaptive ML | No data to learn from |
| Deployable or expanding mechanisms | Mechanical time |
| Traction control from motor current | No free pins for IS lines |
| Agent-designed chassis | The team owns mechanics |

---

## 10. Judge evidence map

Evidence comes from work we do anyway. P6 only packages it.

| Award criterion (from the poster) | Evidence | Where |
|---|---|---|
| UNO Q architecture: MPU, MCU, or both | Section 7 decision with numbers | docs/ARCHITECTURE.md, JUDGE_PACK.md |
| Real-time loop and the 5-second start | Tick timing (M10); locked safety tests; histogram of 50 starts (M1) | tests/locked, TUNING_LOG, plots |
| Sensor fusion and filtering | Debounce + hysteresis, bearing table, phantom mask, IMU bias calibrated during the hold, per-sensor detection ranges | BEHAVIOR.md B5, bench results |
| Behavior implementation | State diagram, arbitration order, transitions tested | ARCHITECTURE.md, tests |
| Code quality, testing, telemetry | Test counts, Codex reviews, flight-recorder plots | state/reviews, logs/plots |
| Search and hunting | Last-seen world bearing, deliberate scan and advance | BEHAVIOR.md B8, recorder |
| Attack technique | Openers, approach-then-push, attack only when centered | B9, B12, test results |
| Defense and evasion | Side and rear defend turns, edge escapes, lost-target braking | B4, B10, M3, M6 |
| Modes and adaptability | 6 modes, selection guide, mirrored L/R | Section 6.4, B13 |
| Opening play | Calibration during the hold; openers that abort into attack | B3, B12, M9 |

---

## 11. References

- Rulebook: `Dubai Techbots League Competition 2026 Rulebook` (team copy)
- UNO Q power and I/O limits: https://docs.arduino.cc/tutorials/uno-q/power-specification/
- UNO Q user manual: https://docs.arduino.cc/tutorials/uno-q/user-manual/
- UNO Q pinout guide (third party, verify against official): https://raspberry.tips/en/arduino-uno-q-pinout-guide
- Immediate startup option (ArduinoCore-zephyr commit): https://github.com/arduino/ArduinoCore-zephyr/commit/8119c2bf68f5d1eb81d9b0560df972170d76ca7c
- Sketch start time report: https://forum.arduino.cc/t/time-to-start-sketch/1413323
- UNO Q command-line workflow: https://shawnhymel.com/3074/how-to-use-the-command-line-cli-with-the-arduino-uno-q/
- RouterBridge library: https://github.com/pillo79/Arduino_RouterBridge
- JS200XF: https://www.jsumo.com/js200xf-infrared-long-range-sensor
- MZ80: https://www.jsumo.com/mz80-infrared-sensor
- Titan 1000 RPM HP: https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp
- BTS7960 module notes: https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf
- Strategy reference (start routines, search, push, evasion): http://brooksbots.com/Strategy.html
- Firmware structure reference (state machine, pitchfork layout): https://github.com/artfulbytes/nsumo_video
- Mini sumo firmware inspired by the above (STM32, state machine): https://github.com/oddgrd/sumodd
