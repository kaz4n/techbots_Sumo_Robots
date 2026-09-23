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

## P0 primary-source review, 2026-09-22 (coordinator merge)

F-001 through F-018 above remain the original seeds for provenance, not installed
or physical verification. The following findings qualify/correct them. Full
question coverage, primary-source URLs, pinned revisions, DESIGN IMPACT analysis
and a concrete test for every unknown are in [G1](analysis/P0_G1.md),
[G2](analysis/P0_G2.md), [G3](analysis/P0_G3.md), [G4](analysis/P0_G4.md),
[G5](analysis/P0_G5.md), [G6](analysis/P0_G6.md). Read those before dependent work.
All hardware remains pending. Source main and release 1.0.0 are different snapshots;
no result from main certifies an installed release. No [P] wiring tag becomes [V].

| ID | Question | Answer / dependency | Source URL | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-019 | G1 PWM pins/timers (qualifies F-001) | Manual advertises six; pinned main maps 13. Proposed D3 TIM3/CH3, D5 TIM1/CH4, D6 TIM3/CH4, D9 TIM4/CH3 exist. Full mapping G1; verify installed devicetree and scope all four before approval. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | conflict in advertised/source count; source mapping verified | pending |
| F-020 | G1 D0/D1 ownership | USART1 console/shell; Bridge uses internal LPUART1. Preserve reserved pins; observe bare-board startup if needed. | https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/boards/arduino/uno_q/arduino_uno_q.dts | verified source | pending |
| F-021 | G1 SDA/SCL vs A4/A5 | D20/PB11 and D21/PB10 are separate from A4/PC1 and A5/PC0. Avoid enabling Wire2 on opponent pins. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | verified source | pending |
| F-022 | G1 header 5 V tolerance (F-003) | Silicon FT qualifications conflict with board-wide 3.6 V absolute max. Retain 3.3 V-only interface; exact pad table and scope/preconnect checks in G1. | https://docs.arduino.cc/tutorials/uno-q/power-specification/ ; https://www.st.com/resource/en/datasheet/stm32u585ai.pdf | conflict | pending |
| F-023 | G1 A0/A1 | Official power page says ADC-only; manual/source expose DAC/GPIO. Keep planned ADC-only use; no output reassignment approved. | https://docs.arduino.cc/tutorials/uno-q/power-specification/ | conflict in permitted use | pending |
| F-024 | G1 LED_BUILTIN/RGB | Pinned main LED_BUILTIN PH10/index50 = MCU LED3 red; RGB3 PH10-12, RGB4 PH13-15 active low. D13 is not builtin LED. Verify installed macros and observe. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/variants/arduino_uno_q_stm32u585xx/variant.h | verified source | pending |
| F-025 | G1 matrix | Core1.0.0 bundled matrix0.1.3 supports begin, grayscale3, draw104-byte frame. Avoid blocking text/playSequence and apparent renderBitmap buffer defect. Draw underlying copy bounded; ISR timing needs measurement. | https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/libraries/Arduino_LED_Matrix/src/Arduino_LED_Matrix.h | verified source; target API pending | pending |
| F-026 | G1 Qwiic | Wire1/I2C4, PD12 SCL/PD13 SDA, 3.3 V, source default400kHz. Verify actual model/interface and read times. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/libraries/Wire/Wire.cpp | verified source | pending |
| F-027 | G2 PWM resolution/frequency | analogWrite defaults8-bit, fixed500Hz; input resolution does not set frequency. Fallback on absent/unready PWM can become digital HIGH; checked MotorGate API required later. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/cores/arduino/wiring_analog.cpp | verified source | pending |
| F-028 | G2 10â€“20kHz API/timer coupling | Native pwm_set_dt candidate, not installed-compile validated; check pinctrl/init/status, equal periods on shared timers, duty limits and 0/full/reversal waveforms. | https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/include/zephyr/drivers/pwm.h | verified API; integration unknown | pending |
| F-029 | G2 micros | Integer-us conversion from cycle counter; actual resolution and long-run wrap depend on installed 64-bit cycle configuration. G2 gives conditional wrap calculations and required measurement. | https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/cores/arduino/zephyrCommon.cpp | verified source; runtime unknown | pending |
| F-030 | G2 pinMode/write/read cost | GPIO wrappers; no measured execution bounds; read errors can resemble LOW. Bare-board batch timing with overhead/max/p99/failure cases required. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/cores/arduino/wiring_digital.cpp | implementation verified; timing unknown | pending |
| F-031 | G2 watchdog | Zephyr API and watchdog0 node exist; installed CONFIG_WATCHDOG/loader exports unknown. Inspect config, compile/link then inert expiry/feed/reset test. | https://docs.zephyrproject.org/latest/doxygen/html/group__watchdog__interface.html | unknown usable installed support | pending |
| F-032 | G2 available RAM (qualifies F-015) | MCU capacity is not free sketch RAM; main configuration includes256KiB LLEXT heap, other heaps/stacks. Installed map/load/headroom measurements required before recorder sizing. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.conf | source verified; available RAM unknown | pending |
| F-033 | G2 attachInterrupt | Wrapper exists; ignores GPIO configuration errors. Validate installed modes, intended four QTR channels, simultaneous capture and rearm races; semantics unapproved. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/cores/arduino/WInterrupts.cpp | source verified; working configuration unknown | pending |
| F-034 | G2/G6 I2C timeout | Wire calls synchronous I2C, ignores stopBit in inspected main; bounded fault behavior/repeated-start compatibility unknown. Exact IMU/library required. | https://github.com/arduino/ArduinoCore-zephyr/blob/39f8354ffc80883d595746abe6b6e16b69a5efa8/libraries/Wire/Wire.cpp | unknown bounded installed behavior | pending |
| F-035 | G3 Immediate option (F-005) | Core1.0.0 exact FQBN arduino:zephyr:unoq:wait_linux_boot=no; no means immediate. Default yes waits for Linux; app is different. | https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/boards.txt | verified release source | pending |
| F-036 | G3 readiness (F-005) | Index67 is internal MCU PG13, not Linux GPIO67 or header67. High does not guarantee responsive Bridge; installed mapping/boot observation required. | https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/loader/main.c | verified release source | pending |
| F-037 | G3 startup time (F-004) | Rough35s seed remains reported. Measure both modes from power-on to first visible frame, several cold boots, exact revision. | https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/loader/main.c | unknown actual times | pending |
| F-038 | G3 Bridge nonblocking (corrects F-009) | RouterBridge0.4.3 notify may wait indefinitely on mutex; call result and destructor wait. No demonstrated R3-compliant integration. | https://github.com/arduino-libraries/Arduino_RouterBridge/blob/0.4.3/src/bridge.h | conflict with seeded nonblocking interpretation | pending |
| F-039 | G3 Monitor allocation (F-008) | write constructs String and may wait; begin may initialize Bridge/RPC. Required counter round trip blocked by SC-I; RAM counter not equivalent. | https://github.com/arduino-libraries/Arduino_RouterBridge/blob/0.4.3/src/monitor.h | verified source; R3/R4 conflict | pending |
| F-040 | G4 core/tool versions | Published core1.0.0 SHA79b3f1af; package dependencies and archive hash in G4. Installed CLI/core/libs unknown; scripts check core before compile. | https://downloads.arduino.cc/packages/package_index.json | verified metadata; installed unknown | pending |
| F-041 | G4 compile/upload (corrects F-006/F-007) | On-board arduino-cli compile then separate upload, FQBN arduino:zephyr:unoq, local remoteocd. No serial-port argument; ttyHS1 reserved by router. Exact installed commands still need validation. | https://github.com/arduino/remoteocd/blob/0.1.1/README.md ; https://docs.arduino.cc/tutorials/uno-q/user-manual/ | source verified; seed port conflict | pending |
| F-042 | G4 adb fallback | Source supports explicit serial-ID device selection; host adb/device/permissions not verified. Harmless inventory/shell/transfer validation required first. | https://github.com/arduino/remoteocd/blob/0.1.1/board/adb.go | source verified; installed route unknown | pending |
| F-043 | G4 library install | lib install Name@version is supported; candidate RouterBridge0.4.3/RPClite0.3.1/Graphics1.1.5; resolve transitive versions before installing/relying. No packages installed on board. | https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_lib_install/ | source syntax verified; installed unknown | pending |
| F-044 | G4 Monitor transport | Routerv0.10.0 default TCP127.0.0.1:7500; official app-cli monitor bidirectional and EOF-sensitive. Project receiver uses recv-only Python over SSH; physical round trip pending. | https://github.com/arduino/arduino-router/blob/v0.10.0/internal/monitorapi/monitor-api.go | source verified; script test separate | pending |
| F-045 | G5 QTR timing/mount (F-017) | QTR-1RC2459 correct: charge >=10us, release/time, parallel possible; recommended3mm, max9.5mm. Read times depend on actual surface/interface. | https://www.pololu.com/product/2459 | verified vendor | pending |
| F-046 | G5 QTR OUT maximum | Schematic capacitor tied VIN; startup/transient coupling possible. Safe maximum with VIN5V/charge3.3V not established. Scope isolated OUT with both power sequences before connecting. | https://www.pololu.com/docs/0J13/all ; https://a.pololu-files.com/picture/0J631.230.jpg | topology verified; maximum unknown | pending |
| F-047 | G5 acquisition | Pololu4.0.0 polling full1500us timeout cannot fit tick. Threshold-censored or async aged samples require approved semantics and measured validation; neither implemented. | https://github.com/pololu/qtr-sensors-arduino/blob/4.0.0/QTRSensors.cpp | source verified; design conflict | pending |
| F-048 | G5 JS200XF (qualifies F-010) | 5V/15mA/600Hz/1.68ms/active-high vendor values; topology unknown. Current vendor rear range-learning button conflicts with D-005 pads120cm. Identify purchased revision first. | https://www.jsumo.com/js200xf-infrared-long-range-sensor | verified specs; output unknown; revision conflict | pending |
| F-049 | G5 MZ80 (F-011) | NPN and wire variants verified; internal pull-up/leakage/guaranteed levels unknown. Isolated loaded measurements and approved interface required. | https://www.jsumo.com/mz80-infrared-sensor | verified NPN; limits unknown | pending |
| F-050 | G5 IBT-2/74HC244 (F-014) | Vendor example VCC5V with HC244; team module unknown. Exact3.3/5V VIH figures not tabulated; 0.7VCC is inference. Neither proposed supply is certified by a successful-looking bench run. | https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf ; https://assets.nexperia.com/documents/data-sheet/74HC_HCT244.pdf | source verified; module compatibility unknown | pending |
| F-051 | G5 BTS7960 truth/threshold | INH0 coast; INH1/IN0 low-side; INH1/IN1 high-side. Max rising2.15V INH/2.0V IN, min falling1.1V within datasheet conditions. Module mapping/polarity conditional; G5 complete table. | https://www.infineon.com/assets/row/public/documents/10/57/infineon-bts7960-ds-en.pdf | verified chip data | pending |
| F-052 | G5 motor/wheel refresh | Titan seeded12V/1000RPM/5.9A/7.5kg-cm confirmed; JS5230 52x30mm and48g vendor figure, not measured team part. | https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp ; https://www.jsumo.com/sumo-robot-silicone-wheel-js5230 | verified vendor | pending |
| F-053 | G6 exact model/library/range/ODR (F-018) | Model unknown. Identify chip/breakout, official library/version, >=1000dps range and >=800Hz unique samples, compile/readback before reliance; candidate list is not purchased identity. | No actual model supplied; analysis/P0_G6.md | unknown | pending |
| F-054 | G6 read duration/age/faults | Register layout/bus clock/read size unknown; measure successful and timeout paths, sample generation, bias/axes. 800Hz ODR cannot imply new data every1kHz tick. | No actual model supplied; analysis/P0_G6.md | unknown | pending |
| F-055 | Local environment/delegation | WSL Ubuntu g++13.3.0/CMake3.28.3/Python3.12.3/rsync3.2.7 available; native four-context delegation and Codex CLI0.155.1 exec/review available. | Local command evidence: analysis/environment.md | verified locally | no board checked |

P0 0.1 result: all G1-G6 questions answered or explicitly unknown with proposed
validation. This is SOURCE-REVIEWED, not TARGET-COMPILED or a passed P0 gate.

## Recovery update: MPU6050 and independent source review, 2026-09-22

F-018/F-053's unidentified-model status is superseded by the user-reported model
below. Initial seeds and research snapshots remain above as provenance. The user
does not currently have SSH/setup details available and asks software work to
assume the intended setup; this is not measured connectivity or electrical safety.
No board was contacted. G6 preserves its initial unknown-model checkpoint and
appends the concrete source findings and exact remaining tests.

| ID | Question | Answer / dependency | Source URL | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-056 | Purchased IMU identity | User reports MPU6050; breakout manufacturer/revision, supply circuit, AD0 and pull-ups remain unknown. Do not infer a GY-521 board or new wiring. | User message 2026-09-22; analysis/P0_G6.md | reported by human | pending |
| F-057 | MPU6050 gyro/rate capability | FS_SEL=2/3 gives +/-1000/2000 dps; DLPF_CFG1..6 with SMPLRT_DIV0 permits nominal 1kHz gyro and accel sampling. Prospective settings are not applied. Filter delay and genuinely new samples must be measured. | https://product.tdk.com/system/files/dam/doc/product/sensor/mortion-inertial/imu/data_sheet/mpu-6000-datasheet1.pdf ; https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf | verified manufacturer documents; configured state unknown | pending |
| F-058 | Candidate library and error handling | Adafruit MPU6050 2.2.9 accepts a TwoWire pointer/Wire1. Unchanged adoption is blocked: burst-read success ignored, getEvent returns true, reset-bit polling unbounded. Target compilation and failure-safe integration unproven. | https://github.com/adafruit/Adafruit_MPU6050/blob/502a7caccda630a151dfb03ecbdd4b8452809ef7/Adafruit_MPU6050.cpp | verified pinned source; target compatibility unknown | pending |
| F-059 | MPU6050 read-time budget | 14-byte burst lower bound at400kHz=382.5us; candidate getEvent adds two range reads for562.5us ideal. Excludes overhead/stretching/interrupts/status reads. These are arithmetic bounds, not WCET. | analysis/P0_G6.md timing arithmetic and pinned library/BusIO sources | derived from source | pending |
| F-060 | STM32 I2C fault bound | Inspected research Zephyr snapshot defaults timeout500ms, minimum1ms, and takes bus semaphore K_FOREVER. Installed release-built driver/config unknown. Synchronous failure path cannot be assumed R4-compliant. | https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/Kconfig.stm32 ; https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32.c | verified research source; installed configuration unknown | pending |

Separate-context source review refreshed the tooling dependencies and found the
G4 tool list incomplete; it now records all 13 package-index dependencies,
including gen-rodata-ld. F-040 still does not represent an installed inventory.
Validation plans cover configuration readback, unique sample generation, bus
waveform, successful and fault timings, axes/units, and safe interface inspection.

## P0 manual-check review, 2026-09-22

| ID | Question | Answer / dependency | Source URL | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-061 | Immediate matrix startup indicator | Official manual section5 (printed p15) warns that matrix access before Linux startup completes may interfere with MCU operation. Installed loader/matrix ownership unknown; Immediate matrix upload blocked pending verification. Boot logo is not sketch start; current sketch initially draws blank then scrolls. Define an identifiable sketch marker and its delay before timing. | https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf ; bench/p0_matrix/p0_matrix.ino | verified manual warning and project source; installed interaction unknown | pending |

F-061 qualifies F-025/F-037 and G3's earlier first-visible-frame proposal. No
physical failure has been observed. Required follow-up: inspect the actual loader
revision and matrix initialization/ownership under each startup option, select
and review a non-conflicting observable sketch-start marker, then collect raw
cold-boot timings. No pin or behavior change is authorized by this finding.

## Connected bare-board inventory, 2026-09-22

D-052 records the user's bare UNO Q setup and authorization. Read-only evidence:
analysis/P0_connected_inventory_20260922.md and P0_board_inventory_20260922.json
(38 explicit command/status/output records). No firmware mutation in this inventory.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-062 | Actual USB target | UNO Q VID2341/PID0078 serial2629958581; COM10 and ADB driver OK; matching mDNS serial; ADB device state device | Local PnP/CLI/adb commands in connected inventory | observed device identity | USB connection only; isolation human-reported |
| F-063 | Installed board toolchain | user arduino; /home/arduino; aarch64 Linux6.16.7; CLI1.5.1 commit01f3d4f2b; arduino:zephyr1.0.0; FQBN options dynamic/default wait_linux_boot=yes and Immediate=no; Python3.13.5;2.8GiB free; rsync missing127 | Exact-device ADB shell commands in board inventory | installed versions observed | actual board OS queried; compilation not yet tested |
| F-064 | Installed libraries/router | No sketchbook libraries; bundled Arduino_LED_Matrix0.1.3, Wire1.0.0, SPI1.0.0; router package0.10.0 and127.0.0.1:7500 listener; packaged remoteocd0.1.1/OpenOCD0.12.0-arduino1-static/compiler1.0.1 paths exist | Board lib/dpkg/listener/package-file inventory | installed files observed | neither Monitor round trip nor library execution tested |
| F-065 | Host ADB/CLI fallback | Existing bundled ADB32.0.0 matches running server and reaches the exact USB target; user Windows CLI1.5.2-rc.1 is present but local zephyr core absent; native Python3.13.11 available | Connected inventory; local Get-Command | observed tools/connection | no host-core installation needed for board-side build |

F-063 supersedes only the earlier installed-unknown status, not source or timing
limitations. Packaged loader ELF/bin do not prove flashed-loader identity. No
PINMAP OK, electrical verification, GPIO/ADC/QTR/IMU measurement or gate follows
from successful Linux inventory. Source and actual behavior remain distinct.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-066 | Actual target compilation | Timing source3de6da69 and matrix72214f8a compile successfully on UNO Q CLI1.5.1/core1.0.0 with MATCH0/MOTORS_ALLOWED0/default startup. Timing reported74008 bytes program/33964 globals; matrix74444/30216. These CLI size figures are not measured runtime headroom. | analysis/P0_timing_target_compile_deps_20260922.txt; P0_matrix_target_compile_20260922.txt | TARGET-COMPILED | actual board-side compiler, not MCU execution proof |
| F-067 | Required installed dependency graph | RouterBridge0.4.3, RPClite0.3.1, MsgPack0.4.2, ArxContainer0.7.0, ArxTypeTraits0.3.2, DebugLog0.8.4 installed with explicit pins/no-overwrite/no-deps after core mandatory stub error. No Graphics dependency needed for raw matrix draw. | analysis/P0_library_provenance_20260922.json contains index URLs/checksums; P0_board_libraries_install_20260922.txt | installed and target-compiled | Bridge runtime boundedness still unresolved for application use |
| F-068 | Actual inert upload | Board-side CLI upload over selected USB2629958581 completed23:19:29+04, reviewed timing3de6da69, MATCH0/MOTORS_ALLOWED0/default/dynamic. MCU reset/flash occurred as upload requires; no motor pins written by sketch. | analysis/P0_timing_upload_20260922.txt | upload command exit0 | capture/runtime readback still pending |

The linked timing ELF includes a local yield/mutex loop hook from RouterBridge,
but does not call begin/start UART/create RPC threads. Exact constructor and
packaged-loader mutex branches were inspected before upload; this is specific
to these binary versions, not a portable guarantee. The uninitialized-mutex API
pattern is not endorsed for new code. See P0_installed_debug_contract.md.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-069 | Bare scheduler lateness | Default timing image completed60000 samples: max3us, nearest-rank p99=3us, zero observations >=1000us late. Histogram bins0/1/2/3 contain16561/16683/16603/10153. Loader+sketch flash identity verified; two4016-byte snapshots identical. Includes installed loop-hook overhead. | analysis/P0_timing_capture_run2_20260922.json and P0_timing_run2_raw/; D-053 | MEASURED on actual MCU; not full-loop WCET | USB2629958581, bare setup human-reported; no motors/sensors |
| F-070 | Immediate target compilation | Exact same inert timing source compiles with wait_linux_boot=no/MOTORS_ALLOWED0, exit0; compile-only did not upload/reset/start. | analysis/P0_timing_immediate_compile_20260922.txt | TARGET-COMPILED | startup runtime and cold-boot duration unmeasured |
| F-071 | Default matrix upload | Reviewed72214f8a source rebuilt and uploaded with MOTORS_ALLOWED0/default startup, exit0 at23:34:33+04. | analysis/P0_matrix_upload_20260922.txt | UPLOADED | counter observation and optical display check remain separate |

F-069 supersedes timing-readout-pending in F-068. Run1 failed before RAM because
the packaged BIN differed from the actually uploaded ELF by one alignment byte;
the corrected verifier compares every ELF PT_LOAD byte, without exceptions.
See analysis/P0_loader_identity_analysis.md and P0_capture_validation_20260922.md.
The first debug attachment began over248s after timing upload completed. Run2
captured the frozen histogram in104.316s; debug reads are not part of the sampled
one-minute scheduler workload. No power-on timestamp, loaded-tick WCET, matrix
optical confirmation, external-pin measurement or phase gate is inferred.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-072 | Matrix sketch progress | Default matrix image verified byte-for-byte; p0Seconds441 then444 with three-second requested wait, observed read bounds3.000219..3.078029s; same list/sketch/BSS mapping confirmed afterward; exit0 | analysis/P0_matrix_capture_20260922.json; P0_matrix_run1_raw/ | MCU counter advancement observed | software progress through matrix workload; optical appearance/1Hz accuracy not qualified |

F-072 supersedes only F-071's pending counter observation. Full readout took
104.838s inside the unchanged120s limit. The MCU remains on the inert default
matrix image; no Immediate upload, cold boot, Monitor output or motor action.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-073 | Installed bounded-output primitives | Stock Monitor/Bridge/RPClite/ZephyrSerial lack a bounded runtime send path. Installed core disables async UART; internal router LPUART1 is deferred-init,115200/8N1/no flow control, separate from console. One-byte interrupt FIFO output is conditionally usable with exclusive ownership and short IRQ-lock containment of CR1 exclusive retries; setup initialization itself can wait and must never enter runtime paths. | analysis/P0_bounded_transport_source_20260923.md; P0_transport_installed_20260923.json; P0_uart_irq_installed_20260923.md | installed source/binary plus pinned primary-source verification | no adapter runtime/WCET proof |
| F-074 | Linux Monitor sink reachability | Receive-only connection to127.0.0.1:7500 accepted; sent0bytes, received0bytes, ended on3.004518694s receive deadline. Existing RAM-only matrix image remained installed. | analysis/P0_monitor_sink_20260923.json | actual Linux endpoint observation | not an MCU counter round trip |
| F-075 | Fixed-counter target compile | Candidate matrix source75ab5a22 compiles on selected UNO Q with MATCH0/MOTORS_ALLOWED0/default;77596B program,31416B globals,230728B remaining per compiler; exit0. One fixed packet slot, no Bridge start, separate final-TC completion. | analysis/P0_counter_target_compile_20260923.txt; P0_counter_inert_manifest_proposal.json | TARGET-COMPILED | no upload/reset/runtime during this compile |

D-062 selects a small P0 diagnostic adaptation of the existing notification
protocol, not a production recorder or an R3/R4 waiver. Source/binary and host
substitute results remain separate from actual delivery and timing measurements.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-076 | Reviewed counter deployment | Revision6b99a60/source75ab5a22 uploaded to USB2629958581; MATCH0/MOTORS_ALLOWED0/default; upload/reset/start exit0 at2026-09-23 01:55:51.731+04. Rebuilt Linux artifacts retain pre-upload reviewed hashes. | analysis/P0_counter_upload_20260923.txt; P0_counter_post_upload_identity_20260923.json | actual inert upload plus artifact identity | post-check is Linux artifact identity, not MCU flash readback |
| F-077 | Actual MCU Monitor counter delivery | Real project receive-only logger observed4..11 and56..63, eight complete sequential counter lines in each8-second window; sent0input bytes. Linux SIGALRM intentionally ended each remote capture with142; local validator passed separately. | analysis/P0_counter_monitor_capture_20260923.json; P0_counter_monitor_reconnect_20260923.json; P0_counter_validation.md | actual physical output and this-client reconnection | another client was established; no no-subscriber/Linux-down/WCET/optical/cold-boot claim |

F-077 closes the fixed P0 counter round-trip gap for D-062's explicit adapter,
not the stock Bridge API or production recorder. Current image is the inert
default matrix/counter fromF-076. Prior timing measurements use a different image.

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-078 | Installed A0 ADC mapping and liveness | Core1.0.0 maps A0/index14 to PA4/ADC1 channel9; DT14-bit conversion maps to default10-bit return. Negative setup/read errors are preserved; zero is valid. Packaged driver waits K_FOREVER for lock and completion even after warmup; async/stream/DMA disabled. First initialization has additional hardware polling with no total deadline. | analysis/P0_adc_installed_contract_20260923.md, versioned official sources and exact loader addresses/hashes | INSTALLED SOURCE/BINARY VERIFIED | No ADC execution/accuracy/WCET evidence from this audit; D-063 permits setup-only diagnostic, not production HAL |
| F-079 | Bare A0 startup API timing | Actual reviewed f5f637b2/default inert image9de8cd1 uploaded02:16:28+04 exit0; all1000 calls complete with nonnegative returns. First276us; subsequent999 min139/max140/p99140us; paired micros overhead1..2us/p992us, no subtraction. Total144116us, floating codes124..306. Loader/sketch bytes verified, two identical12020B records and unchanged BSS mapping. | analysis/P0_adc_validation.md, P0_adc_capture_20260923.json and P0_adc_run1_raw/ | MEASURED on actual MCU; no whole-call upper bound | Same-host wait70.995s before capture invocation; pre-attach completion independently unproved; no accuracy/battery/PINMAP/full-loop WCET acceptance |
| F-080 | Installed builtin-LED GPIO path | LED_BUILTIN=LED3_R=index50/PH10, not D13; installed Arduino OUTPUT establishes LOW/on, HIGH/off. Native GPIOH configure/read/set/clear paths are finite, with no discovered allocation/lock/wait; wrappers discard write/configure errors and map negative read errors to LOW. GPIOH ordinal95 has nonzero native device export; named z_impl wrapper exports are zero and cannot be assumed callable. | analysis/P0_gpio_installed_contract_20260923.md, versioned primary sources and exact installed ELF | INSTALLED SOURCE/BINARY VERIFIED | No GPIO execution/timing/optical or initial-level observation; candidate readiness/ownership/ELF and measurement contract still required |
| F-081 | Builtin LED GPIO API timing/readbacks | Reviewed1dfbd571/default inert a98bcf6 uploaded02:36:15+04, exit0;400 complete cycles/readbacks LOW/HIGH/HIGH plus final HIGH. First mode/write/read-low/read-high/pair4/2/2/2/3us. Subsequent399 mode2..11us/p993, write/reads1..2us/p992, pair2..3us/p993. Clock overhead1..2us/p992, unsubtracted; total8347us. Full deployed-image identity and identical14428B records verified. | analysis/P0_gpio_validation.md and raw P0_gpio_run1_raw/ receipts | MEASURED on actual MCU | Internal PH10 only; wrappers mask native errors, no optical/header-pin/electrical/WCET/gate qualification; pre-attach completion independently unproved |

| F-082 | Installed bare QTR-style GPIO/clock candidate | D2/PB3, D4/PA12, D7/PB2 and D8/PB4 use GPIOA/B ordinal89/90; native neutral/pull-up modes have finite paths and audited ownership exclusions. Neutral INPUT cannot guarantee timeout; explicitly labeled internal pull-ups can exercise actual elapsed1500us polling. Arduino delayMicroseconds(10) calls busy_wait(9); measured charge guard needed. | analysis/P0_qtr_bare_contract_audit_20260923.md; pinned official Arduino/Zephyr sources and installed ELF hashes therein | installed source/binary verified; candidate not yet run | no sensor/pad/acquisition/cleanup or WCET measurement |

| F-083 | Actual bare QTR-style timeout timing | Reviewed dcca300/61d7a2d0 default inert image completed100 neutral and100 diagnostic-pull-up acquisitions. Both datasets:100 DEADLINE/mask15, no observed LOW, charge11..12us, cleanup attempts4. First/subsequent total neutral1535/1531..1536us, pull-up1534/1530..1536us; subsequent p991536us. Full deployed images and two identical frozen records verified. | analysis/P0_qtr_validation.md; P0_qtr_run1_raw/; reviews/P0_qtr_codex.md | MEASURED/independently receipt-reviewed, setup-only | actual MCU bare pads; not real QTR, physical cleanup, voltage, freshness or R4 WCET; debug overlap unexcluded |

| F-084 | Actual installed Wire1/native I2C limits | Wire1 binds deferred I2C4 ordinal40/PD12 SCL/PD13 SDA, DT400kHz; no live pin/state claim. Installed interrupt driver uses500ms per-message completion wait and K_FOREVER ownership/config waits. Wire ignores stopBit, issuing separate STOP-terminated transfers. Source+ELF imply BERR-only can return success without complete data; this fault was not exercised. Named z_impl_i2c exports are0; actual inline/device dispatch must be checked in probe ELF. | analysis/P0_imu_installed_contract_20260923.md; pinned official sources and installed hashes/addresses therein | installed source/binary verified; BERR consequence explicitly inferred | no I2C transaction, live peripheral check, waveform, sensor or fault measurement; runtime adoption blocked |

| F-085 | Actual MPU6050 candidate compilation | D-066 never-called API probe b7bd0df/sourcee0ee0fcc compiles on UNO Q core1.0.0/CLI1.5.1, exit0;96236B program/39356B globals. Installed exact MPU6050 2.2.9, BusIO1.17.4, Unified Sensor1.1.15 with archive/source/installed-file checksums; six earlier libraries unchanged. Final ELF retains requested APIs and Wire1 ordinal40; inline I2C device dispatch, no z_impl_i2c import. | analysis/P0_imu_compile_validation.md; P0_imu_compile_provenance_20260923.json; reviews/P0_imu_compile_codex.md | TARGET-COMPILED and independently offline-reviewed; no upload/execution | no sensor/I2C/runtime qualification; F-084/SC-AG limits unchanged |


| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-086 | Installed PWM APIs and fail-closed limitations | Core1.0.0 analogWrite defaults8 input bits and reapplies DT500Hz; missing mapping/unready PWM falls back to digital output and masks init/set errors. Native explicit-period API is available through nonzero device API; named PWM syscall exports are0. TIM3 D3/D6 share ARR; whole ARDUINO pinctrl groups can also claim QTR/EN proposals, so channel index/routing require exact checks. | analysis/P0_pwm_installed_contract_20260923.md; pinned primary sources and exact installed ELF/headers/raw receipt therein | INSTALLED SOURCE/BINARY VERIFIED | No PWM operation, live rate, waveform, motor-pin/PINMAP or WCET qualification |
| F-087 | Installed interrupt modes and lifecycle limits | FALLING/RISING/CHANGE have native edge paths; LOW/HIGH return hidden-ENOTSUP. digitalPinToInterrupt mutates port-slot state; attach hides mode/ownership failures; detach clears software handler/enabled only, leaving EXTI active/owned. Source order implies an interleaving null-call risk, not an exercised fault. Proposed QTR EXTI3/12/2/4 are distinct; live ownership unknown. | analysis/P0_irq_installed_contract_20260923.md; official pinned sources, installed hashes/offline ELF and raw receipts therein | INSTALLED SOURCE/BINARY VERIFIED; race consequence source-inferred | No IRQ registration/stimulation, timing/loss/rearm measurement or SC-B acquisition acceptance |


| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-088 | Actual retained PWM/interrupt compilation | D-067 implementation660eb08/source6578e07a target-compiles on UNO Q CLI1.5.1/core1.0.0, exit0 at03:22:01+04;80248B program/34048B globals. Exact26 source entries, three ELFs, retained probes, inline native dispatch and nonzero selected pinctrl/device exports independently verified.8 scoped host checks pass and fresh same-model review PASS/no findings. | analysis/P0_pwm_irq_compile_validation.md; compile/provenance/test receipts; reviews/P0_pwm_irq_compile_codex.md | TARGET-COMPILED/HOST-TESTED/REVIEWED; compile-only | No upload/reset, PWM/IRQ execution, live mapping/waveform/timing or runtime-load qualification; F-086/F-087 limits remain |


| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-089 | Arduino dynamic size label and recorder budget | Pinned zephyr-check-size sums allocated ELF sections incl text, excluding configured no-reloc rodata; program figure is upload-file length. Cached F-088 ELF independently sums34048B, matching its compile report. Default50Hz recorder payload292794B alone exceeds262144B pool;25Hz162794B is only a conditional candidate. Do not double-count P1 program125508B on top of its61004B RAM estimate. | analysis/P2_memory_budget_followup_20260923.md; pinned primary source URL, cached ELF/hash and corrected readelf receipt therein | SOURCE-VERIFIED; cached-artifact consistent; complete target headroom unknown | No current board query, load/allocation/free-RAM or B8 acceptance; host owner sizeof292968B is separate |

| F-090 | Actual isolated recorder memory images | D-071 repaired50Hz size-check fails exit1 at356608B vs262144B. Isolated25Hz passes exit0 at226584B, ELF294932B; target Robot2352B, owner162952B in data. Full ABI/sections/source hashes independently reviewed. Production50 unchanged. | analysis/P2_memory_compile_validation.md; raw compile/ELF receipts; reviews/P2_memory_compile_codex.md | TARGET-COMPILED25; EXPECTED_OVERSIZE50; HOST/SCRIPT-TESTED; no execution | Compiler35560B difference is not free RAM. Conditional pristine loader model230072B peak is source-derived, not measured. No full-HAL/load/WCET/200s/B8/human gate |
| F-091 | Inherited runtime and header boundaries in actual memory probe | Exact ELF includes4 platform initializer entries and default loop hook with indefinite mutex wait and conditional Bridge.update_safe. Robot reset local stack2392B before callees. Auto-included Zephyr EMPTY macro collides with recorder enum; bench include quarantine repairs compilation only. | analysis/P2_memory_compile_validation.md; raw elf_25_disassembly/relocations; pinned util_macro.h in review | ACTUAL TARGET ELF/compile evidence plus source interpretation | No hook/constructor execution, stack/WCET or Linux-independence proof. Future eligible runtime integration must resolve these inherited paths; SC-I remains |


| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-092 | Adopted25Hz production-source memory probe | D-072 changes only LOG_HZ among76B16 values. Actual source772bda55 compiles exit0 on CLI1.5.1/core1.0.0, default/MATCH0/MOTORS_ALLOWED0; ELF294932B, compiler RAM226584B. ELF b1fd8678 is byte-identical to reviewed D-071 candidate25.5001frames/40ms cadence,200s window and4096events preserved. | analysis/P2_rate_adoption_validation.md; P2_rate_validation_raw/; reviews/P2_rate_adoption_codex.md | HOST/SCRIPT-TESTED, TARGET-COMPILED, independently REVIEWED | Linux compile/read-only file evidence only; no upload/reset/MCU action, actual load/freeRAM/fullHAL/200s/WCET or human gate. F-091 runtime limits remain |
