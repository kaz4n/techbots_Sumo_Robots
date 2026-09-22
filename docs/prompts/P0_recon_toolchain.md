# P0: Recon and toolchain

**Goal:** every hardware and API fact the design relies on is verified or flagged, and you can build, flash, and read logs on the UNO Q with one command each.
**Needs:** the UNO Q on a desk. No robot, no motors.
**Load:** AGENTS.md, docs/HARDWARE.md sections 1 to 3 and 5, state/FACTS.md (seeded with research from 22 September).

## Tasks

### 0.1 Fact verification (parallel: one fact-checker per group)
Start from the seeded rows in state/FACTS.md; confirm or correct them against primary sources.
- **G1 UNO Q pins:** which header pins are PWM-capable and which timer or channel each uses (the two PWM inputs of one driver need the same frequency); whether D0/D1 are used by Bridge or the console; whether the SDA/SCL header pins share A4/A5; which pins tolerate 5 V in digital input mode (the Arduino power document also lists a 3.6 V absolute maximum for the maker headers, so resolve that conflict); A0/A1 restrictions; the pins behind LED_BUILTIN and the RGB LEDs; the LED matrix API; the Qwiic bus object (Wire1?).
- **G2 Zephyr Arduino core:** analogWrite resolution and default PWM frequency, and how to set 10 to 20 kHz; micros() resolution; the cost of pinMode, digitalWrite, and digitalRead; watchdog access from a sketch; RAM available to a sketch; attachInterrupt support.
- **G3 Startup and Bridge:** the Immediate startup option (exact board option or FQBN suffix for arduino-cli; seeded as `wait_linux_boot=no`), the Linux-ready signal (reported as GPIO 67), which Bridge calls are non-blocking (notify vs call), how Monitor output reaches the laptop.
- **G4 Toolchain:** compile and upload with arduino-cli on the board itself (FQBN `arduino:zephyr:unoq`, reported upload port /dev/ttyHS1); the adb fallback from the laptop; installing libraries on the board.
- **G5 Components:** QTR-1RC RC read procedure, timings, recommended mounting height, and the maximum voltage on OUT with VIN at 5 V; JS200XF output stage (push-pull or open collector); MZ80 output stage (internal pull-up or not); IBT-2 truth table for forward, reverse, brake, coast; 74HC244 input-high threshold at 5 V and at 3.3 V supply; BTS7960 input thresholds.
- **G6 IMU:** once the human names the model, find a library that builds on the Zephyr core, the gyro full-scale setting of 1000 dps or more, output data rate of 800 Hz or more, and the I2C time to read gyro Z plus accel X and Y.

### 0.2 Toolchain (HUMAN ACTION: Wi-Fi, SSH key, board IP)
- Staging: arduino-cli compiles only files inside the sketch folder (and its src/ subfolder) plus installed libraries. flash.sh therefore builds a staging sketch under build/stage/<name>/ with the .ino at the top and src/config.h, src/core/, src/hal/ copied into its src/ folder, then syncs that. Verify the include paths compile.
- `tools/flash.sh`: rsync the staged sketch folder to the board over SSH, run arduino-cli compile and upload on the board, print the result. Flags: `--match` (MATCH=1, MOTORS_ALLOWED=1, Immediate startup if verified), `--compile-only`, default bench build with MOTORS_ALLOWED=0.
- `tools/logs.sh` (stream Monitor output), `tools/test_host.sh` (configure, build, run host tests).
- Prove the loop: flash a sketch that scrolls "SUMO" on the LED matrix and prints a counter once per second; read it back with tools/logs.sh.
- Measure power-on to sketch-running time in default and in Immediate mode (HUMAN ACTION with a stopwatch, or log timestamps). Record both in FACTS.md.

### 0.3 Repository scaffold
Create the layout in AGENTS.md section 5: host/CMakeLists.txt, doctest single header in host/third_party/, one passing dummy test, .gitignore (build/, logs/*.csv optional), empty src/config.h with the B16 table as constants. Commit.

### 0.4 Micro-benchmarks on the bare board (no motors)
Loop jitter at 1 kHz for 60 s (max and p99); pinMode + digitalWrite toggle time; a 4-pin QTR-style charge-and-time cycle with nothing connected (timeout path); analogRead time; I2C transaction time if the IMU has arrived. Record everything in FACTS.md.

### 0.5 Pin map
Update docs/HARDWARE.md section 3 with verified pins. Any change from the proposal goes to DECISIONS.md, then HUMAN ACTION for "PINMAP OK" before the team wires anything.

## Exit gate (GATE P0)
- [ ] FACTS.md answers every G1 to G6 question; every unknown has a proposed bench test
- [ ] tools/flash.sh and tools/logs.sh round trip works (matrix text + counter)
- [ ] Startup time measured in both modes
- [ ] tools/test_host.sh passes
- [ ] Human replied "PINMAP OK"
- [ ] Codex review with no open BLOCKER; human writes `GATE P0 PASS`

## Do not
Write strategy code. Energize motors. Guess a pin.
