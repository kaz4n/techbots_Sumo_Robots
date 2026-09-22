# AGENTS.md: SumoX-26 autonomous sumo robot firmware

Read this whole file at the start of every session. It is the rules file for every agent on this repo. Codex reads it directly; Claude Code imports it from CLAUDE.md.

---

## 1. Mission

Firmware for a 3 kg autonomous sumo robot competing at SumoX-26 (Dubai Techbots League) on **Saturday 3 October 2026**. The team is building its first sumo robot while you write the code. Check today's date with `date` and compare it with the schedule in docs/PLAN.md section 3.

Priority order for every decision:
1. Never break a competition rule (5-second hold, autonomy, no remote control).
2. Never drive out of the ring on its own.
3. Win pushes with the hybrid flanking strategy (docs/BEHAVIOR.md).
4. Leave evidence for the judges (tests, logs, plots) as a by-product, never at the cost of 1 to 3.

---

## 2. Source-of-truth documents (load only what the task needs)

| Document | Load when |
|---|---|
| docs/PLAN.md | Scope, schedule, gates, strategy rationale |
| docs/HARDWARE.md | Pins, wiring, electrical limits, physics numbers, anything in src/hal |
| docs/BEHAVIOR.md | Anything in src/core, strategy, tunables |
| docs/prompts/Pn_*.md | The active phase only |
| state/FACTS.md | Before relying on any hardware or API fact |
| state/PROGRESS.md | Session start (resume point) |
| state/DECISIONS.md | Before changing anything already decided |

If two documents conflict, stop and ask (section 9). Never pick one silently.

---

## 3. Hardware at a glance

- **Controller:** Arduino UNO Q. The sketch runs on the STM32U585 (Arduino core on Zephyr). Linux on the QRB2210 is used only to build, flash, and store logs. The rules forbid any additional microcontroller.
- **Logic level:** header I/O is 3.3 V. Treat every pin as 3.3 V only.
- **Drive:** 4 Titan 12 V 1000 RPM gearmotors, 52 x 30 mm silicone wheels, skid steer. 2 BTS7960 (IBT-2) boards, one per side; the front and rear motor of a side run in parallel.
- **Opponent sensors (7, digital):** 3 JS200XF front (0, -15, +15 degrees), 4 MZ80 (-90, +90, -135, +135 degrees).
- **Edge sensors:** 4 QTR-1RC at the corners (RC timing).
- **Other:** IMU on Qwiic (Wire1), battery sense on A0, START and MODE buttons on A1 (resistor ladder), 8 x 13 LED matrix.
- Pin numbers in docs/HARDWARE.md are proposals until state/FACTS.md marks them verified and the human has replied "PINMAP OK".

---

## 4. Hard rules (non-negotiable)

- **R1. Five-second hold.** After START release, MOTOR_EN stays LOW and every duty stays 0 until COUNTDOWN_MS + COUNTDOWN_MARGIN_MS have passed. Only `MotorGate` (src/hal/motors) may write EN or PWM pins. Tests in tests/locked/ prove this. Never edit a locked test without a human-approved entry in state/DECISIONS.md.
- **R2. No remote control.** No code path accepts motion commands from Wi-Fi, Bluetooth, Bridge, or serial. In MATCH builds the Bridge is used only to dump logs while in IDLE.
- **R3. Linux independence.** The control loop never waits for Linux. No Bridge call may block. With the Immediate startup option, check the Linux-ready signal before any Bridge use.
- **R4. Deterministic tick.** 1 kHz control tick scheduled with micros(). After setup: no delay(), no heap allocation, no Arduino String, no unbounded loops, no I2C without a timeout. Worst-case tick under 800 us, measured on the robot.
- **R5. Edge first.** EDGE_ESCAPE outranks every behavior except the countdown gate. The single exception is the push-through window in docs/BEHAVIOR.md B9.4.
- **R6. Governor.** All motor duty passes through the governor (B6). Full duty only after contact with a centered opponent.
- **R7. Motors need a human.** Never flash or run a build that can energize motors unless the human has replied `STAND OK` (wheels off the ground) or `RING OK` (on the ring, area clear) for that specific run. Bench builds default to `MOTORS_ALLOWED 0`.
- **R8. Wiring is human-owned.** Never change a pin, voltage, or wiring assumption without a DECISIONS.md entry and a human "yes".
- **R9. Tunables** live only in src/config.h, with units in the name (_MS, _US, _DEG, _DPS, _DUTY, _V, _G, _M).
- **R10. Git.** Small commits, one task each, clear messages. Never force-push, never push to a remote, never rewrite history without human approval.
- **R11. Evidence.** A task is done when its test or measurement passes and the result is written to state/. "Should work" is not done.

---

## 5. Architecture

```
src/
  config.h            every tunable and pin assignment (the only file tuned on the ring)
  core/               pure C++17, no Arduino.h; compiles on the laptop and on the MCU
    types.h           Inputs, Outputs, State, Mode, Event
    countdown.*       START handling and the hold logic (B3)
    edge.*            line classification and escape planner (B4)
    opp_fusion.*      debounce, bearing table, memory, contact cue, phantom mask (B5)
    governor.*        caps, slew, voltage compensation (B6)
    motion.*          turnTo, arc, straight, brake; IMU closed loop and timed fallback (B7)
    openers.*         data-driven opening routines, mirrored L/R (B12)
    stall.*           push-stall detector (B11)
    fsm.*             arbitration and state machine (B1, B2, B8, B9, B10, B11)
    logframe.*        recorder frame and event packing (B15)
  hal/                Arduino/Zephyr specific, thin, no strategy logic
    motors.*          BTS7960 driver and MotorGate (EN pin)
    line_qtr.*        parallel RC read of 4 QTRs
    opp_sensors.*     7 digital inputs, polarity from config
    imu.*             init, bias calibration, yaw integration
    power.*           battery ADC
    ui.*              button ladder, LED matrix, RGB LED
    recorder.*        RAM ring buffers and dump over Bridge
  app/
    app.ino           setup() and the 1 kHz scheduler: HAL reads -> Inputs -> Robot::step -> Outputs -> HAL writes
host/                 CMake project: builds src/core + tests with g++ (doctest)
tests/                unit and scenario tests
  locked/             R1 and R5 safety tests (human approval to change)
bench/                one sketch per bench test (P2)
tools/                flash.sh, logs.sh, dump_match.sh, test_host.sh, plot_match.py
docs/  state/  logs/
```

Core rule: src/core has no clock and no I/O. Time arrives in Inputs.t_us. That makes every decision testable on the laptop and replayable from logs.

---

## 6. Code conventions

- C++17 subset: no exceptions, no RTTI, no templates beyond small constexpr helpers, `enum class`, fixed-width integers, floats allowed (the M33 has an FPU).
- One namespace per module. Constants UPPER_SNAKE with units, functions lowerCamel, types UpperCamel.
- Each file opens with three comment lines: what it does, why it exists, how it is tested.
- Functions under 60 lines. Comments explain why, not what.
- **Explainability:** a student must be able to explain every module to a judge in two sentences. If a construct needs a paragraph, simplify it.
- Every behavior has a test that names its BEHAVIOR.md section.

---

## 7. Commands

The agent creates these scripts in P0 and updates this table once they work.

| Task | Command |
|---|---|
| Host tests | `tools/test_host.sh` |
| Read-only board inventory (script-tested; board pending) | `tools/preflight.sh` |
| Build + flash a bench sketch | `tools/flash.sh bench/<name>` |
| Build + flash match firmware | `tools/flash.sh app --match` |
| Compile only (no upload) | `tools/flash.sh app --compile-only` |
| Live log | `tools/logs.sh` |
| Dump the last match | `tools/dump_match.sh` |
| Plot a log | `python3 tools/plot_match.py logs/<file>` |

Build path: sync the sketch to the UNO Q over SSH, then compile and upload on the board with arduino-cli (FQBN `arduino:zephyr:unoq`). Fallback: adb over USB. P0 verifies exact commands and records them in state/FACTS.md.

---

## 8. Workflow

- Phases P0 to P7 live in docs/prompts/. Work only on the active phase named in state/PROGRESS.md.
- A phase closes when (a) its exit criteria pass, (b) the Codex review (docs/prompts/REVIEW_GATE.md) has no open BLOCKER, and (c) the human writes `GATE Pn PASS` in state/PROGRESS.md.
- State files:
  - state/PROGRESS.md: append one line per task (date, phase, task, result, commit).
  - state/DECISIONS.md: append decisions in ADR style (context, decision, consequence).
  - state/FACTS.md: verified facts with source URL and confidence.
  - state/TUNING_LOG.md: append every ring or bench measurement and every config change with its evidence.
- **Scope rules:** match performance first. P6 runs only if GATE P4 passed by 30 September. If GATE P3 has not passed by the end of Monday 28 September, cut scope to the reactive core plus openers SIDESTEP and DIRECT; drop ARC, WAIT, and P6 except the recorder.
- **Code freeze:** Thursday 1 October, 21:00. After that, only src/config.h values change, each with a TUNING_LOG entry.

---

## 9. Talking to the humans

When you need hands, eyes, a measurement, or a decision, print exactly this block and wait:

```
=== HUMAN ACTION REQUIRED ===
What:  <one line>
Why:   <one line>
Steps: <numbered, concrete, with expected readings>
Reply: <the exact reply you need, e.g. "STAND OK", three numbers, or yes/no>
=============================
```

Batch requests when you can: the humans are building the robot at the same time. Keep working on unblocked tasks while you wait.

When documents conflict, a requirement is missing, or a fact is unverified, print:

```
=== CONFUSION ===
Issue:   <one line>
Options: A) ...  B) ...  C) ...
Recommend: <letter + one-line reason>
=================
```

Never invent requirements, pins, or API behavior.

---

## 10. Never

- Design or change the chassis or mechanical layout.
- Add parts or libraries that need a purchase without asking.
- Weaken or delete a test to make a build pass.
- Enable Wi-Fi-dependent behavior in match firmware.
- Run motors without `STAND OK` or `RING OK` for that run.

## Codex handoff (user-authorized 2026-09-22)

Codex implements and orchestrates; a separate fresh-context reviewer reviews only.
D-015 supersedes only the agent-role assignment in D-009 and legacy Claude prompts.
All safety rules, phase gates, human decision rights, and the board-side SSH build
path remain in force. Resume through `state/CODEX_HANDOFF.md` and
`docs/prompts/CODEX_RESUME.md`; `state/PROGRESS.md` remains authoritative.
D-016 permits P1 host development while P0 hardware acceptance remains pending;
it is not a passed gate. D-017/D-018 record the human-approved governor and
gated-service ordering changes; other protected decisions remain separate.
D-019/D-020/D-021 approve the release-debounce anchor, persistent/all-white edge
guard and forward escape base/cap. Read their precise scopes before integration.
