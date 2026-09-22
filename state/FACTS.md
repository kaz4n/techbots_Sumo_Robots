# FACTS

Seeded 2026-09-22 from planning research. P0 fact-checkers confirm or correct every row against primary sources before code or wiring depends on it.
Confidence: verified (primary source) / reported (secondary source) / unknown / conflict. Hardware-checked: pending / yes / no.

| ID | Question | Answer (seed) | Source URL | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-001 | UNO Q header logic level and PWM count | 3.3 V logic on the MCU headers; 6 PWM-capable pins; D0/D1 hardware UART | https://raspberry.tips/en/arduino-uno-q-pinout-guide | reported (confirm with official pinout) | pending |
| F-002 | UNO Q supply input | VIN accepts 7 to 24 V | https://docs.arduino.cc/tutorials/uno-q/power-specification/ | verified | pending |
| F-003 | 5 V tolerance of header pins | Some STM32U585 pads tolerate 5 V in digital mode, not in analog mode; Arduino lists a 3.6 V absolute maximum for the maker headers. Treat as 3.3 V only | https://docs.arduino.cc/tutorials/uno-q/power-specification/ | conflict | pending |
| F-004 | Default time from power-on to sketch start | About 35 s (waits for Linux) | https://forum.arduino.cc/t/time-to-start-sketch/1413323 | reported | pending |
| F-005 | Immediate startup option | ArduinoCore-zephyr adds a startup menu (wait_linux_boot=no, boot_mode immediate); do not use Bridge before Linux is ready; Linux-ready signal reported on GPIO 67 | https://github.com/arduino/ArduinoCore-zephyr/commit/8119c2bf68f5d1eb81d9b0560df972170d76ca7c | verified in source; confirm it ships in the installed core version | pending |
| F-006 | arduino-cli target | FQBN arduino:zephyr:unoq; on-board upload port /dev/ttyHS1 | https://pub.dev/documentation/arduino_bridge/latest/ | reported | pending |
| F-007 | Command-line workflow | Copy the project to the board, SSH in, run arduino-cli on the board; WSL recommended on Windows | https://shawnhymel.com/3074/how-to-use-the-command-line-cli-with-the-arduino-uno-q/ | reported | pending |
| F-008 | Printing from the sketch | Monitor object via RouterBridge | https://github.com/pillo79/Arduino_RouterBridge | reported | pending |
| F-009 | Non-blocking Bridge calls | notify is fire-and-forget; call waits for a response | https://github.com/pillo79/Arduino_RouterBridge | reported | pending |
| F-010 | JS200XF specs | 5 V, 15 mA max, digital (1 = seen), 600 Hz, 1.68 ms response, 200 cm; rear pads bridged give 120 cm. Output stage type unknown | https://www.jsumo.com/js200xf-infrared-long-range-sensor | verified (vendor) | pending |
| F-011 | MZ80 specs | 5 V, NPN output, trimpot 10 to 80 cm, M18, 20 g, two wire-color variants. Internal pull-up unknown | https://www.jsumo.com/mz80-infrared-sensor | verified (vendor) | pending |
| F-012 | Titan 1000 RPM HP | 12 V, 240 mA no-load, 5.9 A stall, 7.5 kg-cm, 37 mm x 75 mm, 6 mm D shaft | https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp | verified (vendor) | pending |
| F-013 | JS5230 wheels | 52 mm diameter, 30 mm wide, aluminum hub, silicone tire | https://www.jsumo.com | verified (vendor) | pending |
| F-014 | IBT-2 module | One full H-bridge per board; 6 to 27 V; RPWM, LPWM, R_EN, L_EN, R_IS, L_IS; PWM up to 25 kHz; 74HC244 input buffer; about 66 g | https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf | reported | pending |
| F-015 | UNO Q MCU | STM32U585 Cortex-M33 at 160 MHz, 2 MB flash, 786 KB SRAM (RAM available to a sketch unknown) | https://docs.arduino.cc/tutorials/uno-q/user-manual/ | verified | pending |
| F-016 | 1.8 V connectors | JMISC, JMEDIA, JCTL are 1.8 V: do not connect sensors there | https://docs.arduino.cc/tutorials/uno-q/power-specification/ | verified | pending |
| F-017 | QTR-1RC read procedure and limits | Drive OUT high about 10 us, switch to input, time the discharge; mounting height and max OUT voltage with VIN 5 V to confirm | https://www.pololu.com/product/2459 | unknown (P0 G5) | pending |
| F-018 | IMU model, library, range, rate | Not yet chosen | | unknown (P0 G6) | pending |
