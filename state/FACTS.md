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

## D075 MotorGate target compilation, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-093 | Does the real MotorGate boundary compile for the installed UNO Q toolchain? | CLI1.5.1/core1.0.0 refreshed on USB2629958581. Source807b576899bc8c9f9703e284d2d43ab1ab75a9eeb36e3b006ae53220cde79965 compiled default0:76220B program/31276B globals; enabled1 Immediate:76692B/31612B. Both exit0. Retained methods, pointer-only setup and empty loop independently reviewed from ELF; no Port implementation or execution. | analysis/P2_motor_gate_validation.md; P2_motor_gate_raw/target_default.json, target_enabled.json, target_elf_symbols.json; reviews/P2_motor_gate_codex.md | TARGET-COMPILED and source/ELF-reviewed | board Linux build only; no upload, PWM, native adapter, physical acceptance, fullfirmware RAM or WCET claim |

## D076 checked opponent GPIO, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-094 | Can the actual native opponent GPIO path preserve failures and compile on the installed target? | Proposed indices11/12/13/16/17/18/19 resolve PB15/PB14/PB13/PA6/PA7/PC1/PC0 with zero flags. Checked configure/raw read use finite native device paths; real driver independently host-tested and target-compiled sourceef44ace3, exit0,76308B program/31032B compiler memory. Exact ELF uses inline device dispatch;31 retained native device/clock exports nonzero. | analysis/P2_opp_gpio_audit.md; analysis/P2_opp_gpio_audit_raw.json; analysis/P2_opponent_validation.md; P2_opponent_raw/installed_typedefs.json,target_elf.json; reviews/P2_opponent_codex.md | INSTALLED-SOURCE/ELF-VERIFIED, HOST-TESTED, TARGET-COMPILED; separate same-model review PASS | Linux files/compiler only; no GPIO execution/upload, physical polarity/range/pin approval or WCET. SPI2 and Wire2 ownership conflicts require exclusion; invalid samples require future app fault policy. F091 inherited runtime limits remain |


## D077 native PWM source prerequisites, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-095 | Can selected native timers support checked10kHz periods and post-write preload confirmation? | Installed RCC/PLL/APB source and offlineELF give TIM1/3/4kernel160MHz with PSC63/4/4, candidate Gateperiods3200/250/3200/3200. DT-derived mapping and native reset/partial/full-register states verified. Retrieved ST RM0456Rev6 supports fresh post-clear UIF after allwrites under specified guards; current ES0499Rev12 timer limitations excluded by plainPWM1/noOCclear/noBreak. | analysis/P2_motor_clock_audit.md; analysis/P2_motor_update_audit.md; P2_motor_native_raw/clock.json,update_sources.json with primaryURLs/hashes/excerpts | INSTALLED-SOURCE/OFFLINE-ELF/PRIMARY-MANUAL VERIFIED; algorithm inference explicitly conditional | No live register/rate/waveform/WCET or silicon revision measurement; source candidates require actual setup validation, exclusivity and target checks. No physical gate or run authority |


## D077 actual native MotorGate software, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-096 | Does the actual checked native motor backend compile and satisfy independent software tests? | Final source c35726f4 compiles on installed CLI1.5.1/core1.0.0: default 85052B program/35160B compiler memory; enabled Immediate 85588B/35552B, both exit0. Independent native replay passes 152 case executions/217368 assertions across 78 executables, including real Gate/Robot composition. Exact 38-file maps, 33 nonzero native exports and direct fresh-UIF MMIO/activation paths inspected in both ELFs. | analysis/P2_motor_native_validation.md; P2_motor_native_raw/target_c35726f4_* and native_target_*_mask receipts; reviews/P2_motor_native_review.md and raw receipts | HOST-TESTED/TARGET-COMPILED; fresh separate same-model review PASS/no open findings | Board Linux compiler/files only; no upload/reset/native GPIO/PWM execution, live clock/waveform/EN, physical B4/B7, whole-tick WCET, PINMAP or human gate. F091 inherited runtime limitations remain |


## D078 ADC source prerequisites, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-097 | What supports a bounded native battery acquisition candidate? | Installed ADC1 channel9/PA4, common-register ABI, finite NVIC reads and private clock-enable path verified. Stock ADC4 initializes then disables conversion; IRQ113 can remain enabled. DAC1 boot only configures analog pads. Current DS13086Rev10 gives ordinary calibration31849cycles; RM0456Rev6 requires LFTRIG for occasional samples. HCLK160/div4, high-supply profile and timing deadlines are conditional software selections. Stock MSIS automatic calibration is enabled and ES0499Rev12 unlock accuracy issue remains SC-AJ, not a proved clock lock. | analysis/P2_adc_native_audit.md/raw; P2_adc_limits.md/raw; P2_adc_ownership.md/raw; P2_adc_errata.md; P2_power_contract.md | INSTALLED-SOURCE/OFFLINE-ELF/PRIMARY-DOCUMENT VERIFIED with explicit retrieval limits and engineering inferences | No live ADC/clock/silicon/supply/divider/accuracy/timing measurement, deployed-loader match or gate; D078 host/compile-only work only |


## D078 actual bounded battery ADC software, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-098 | Does the actual native ADC driver preserve bounded failure and compile on the installed target? | Implementation e6b7060, final power.cpp SHA505e008e. Independent author and fresh same-model reviewer each pass9methods/75positive native cases; two required child-failure sentinels return1. Final sourcea936d10d compiles with CLI1.5.1/core1.0.0:81132B program/33476B compiler memory, exit0. Exact40file map,36exports, direct register/IRQ/barrier paths and inert setup inspected. Existing411tooling methods also pass; normal and sanitizer host2/2 pass. | analysis/P2_power_validation.md; analysis/P2_power_raw/; reviews/P2_power_review.md and raw receipts | HOST-TESTED/TARGET-COMPILED, independent review PASS/no open findings in software scope | Board Linux compiler/files only. No upload/reset/MCU/ADC/pin operation, physical voltage/reference/divider/0.05V accuracy, whole-tick WCET or human gate. SC-AJ global clock qualification and F091 inherited runtime paths remain open |


## D079 I2C4 source and conditional timing prerequisites, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-099 | Can a bounded native MPU6050 transport be implemented on installed I2C4? | Native I2C4/ordinal40/IRQs100-101/defaultPD12-PD13AF4, private clock/pinctrl and finite TXIS/TC/RXNE/STOP/PE operations are source-verified. Conditional0x40EB202C AFON/DNF0 arithmetic passes128corners:300.300..393.993kHz;15byte162clock portion411.175..539.460us. Current U585filter50..115ns, clock158.4..161.6MHz mathematicalenvelope with actual160MHz rating separately binding.600+50us softwarebounds are not physicalWCET. | analysis/P2_i2c_native_audit.md/raw; analysis/P2_i2c_timing.md/raw; analysis/P2_imu_bus_contract.md | INSTALLED-SOURCE/OFFLINE-ELF/PRIMARY-DOCUMENT VERIFIED, conditional engineering arithmetic; source download/indexed limits preserved | Linux/sourcefiles only, no MCU/I2C/pad operations. No oscillatorlock/waveform/address/pullup/MPUfreshness or whole-tick acceptance; SC-AJ global clock issue remains. Driver/tests/targetreview recorded separately when complete |


## D079 actual bounded MPU6050 transport software, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-100 | Does the concrete native MPU6050 transport satisfy independent software tests and installed target compilation? | Implementation a749816, CPP940f4e2c. Author and fresh same-model reviewer each pass10methods/83positive native cases/992parent assertions; two required failure sentinels return1. Four reviewer final-boundary regressions pass after saved defects were repaired. Actual sourcef3e9b546 compiles on CLI1.5.1/core1.0.0:81992B program/33788B compiler memory,exit0;42files/3ELFs/36nativeexports and inert startup inspected. | analysis/P2_imu_bus_validation.md/raw; reviews/P2_imu_bus_review.md/raw | HOST-TESTED/TARGET-COMPILED; fresh independent software review PASS/no open findings | Linuxcompiler/files only,no MCU/I2C/pad operation or upload. Bus completion is not MPU identity/configuration/freshness/yaw; no address/electrical/waveform/WCET/phase acceptance. SC-AJ/F091 remain global runtime blockers |


## MPU6050 setup/sample source boundaries, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-101 | What do the manufacturer sources establish for MPU6050 setup and data freshness? | Documented registers support checked reset/profile/readback and coherent14motion-byte decoding. Status-to-shadow atomic generation binding is not specified. A status/STOP/motion handshake is a labelled inference with198clock cost; it requires aggregate budgeting. Setup waits and8g selection are D080 engineering defaults, not guaranteed settling. | analysis/P2_mpu6050_sample_audit.md/raw, linked manufacturer RMRev4.0 and product tables with revision/download limits; analysis/P2_imu_setup_contract.md | PRIMARY-DOCUMENT REVIEW plus labelled temporal model; not physical proof | No sensor/bus operation. Actual identity/address/power/settling/rate/axes/yaw/WCET remain pending |


## D080 actual checked MPU6050 setup and coherent decoding, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-102 | Does the concrete MPU6050 setup/decoder pass software validation and target compilation? | Implementation63c7eaa CPPf38f0f21. Independent author and reviewer pass26cases/1562374assertions,44config variants plus2inert probe builds/eight upload refusals;13strictconfig checks. Root fullhost andsanitizer2/2 pass. Actual targetsourcec45ffd3d compiles84132Bprogram/34748Bcompiler memory,exit0;44filemap/3ELFs/startup verified. | analysis/P2_imu_setup_validation.md/raw; reviews/P2_imu_setup_review.md/raw | HOST-TESTED/TARGET-COMPILED, fresh same-model review PASS/no open findings | No MCU/I2C/pad/upload operation. Observed configuration/coherent bytes do not prove physical settling, freshness, axes, bias, yaw or full-tick WCET. SC-AJ/F091 and human gates remain pending |

F102 final regression addendum: existing432tooling methods PASS630.788s exit0;442distinct methods across separate existing/new setup runs. NativeBus102new subprocess receipts preserve100exit0 plus2required failure sentinels. Exact aggregate command/output and relocation provenance are in P2_imu_setup_raw. This adds software regression evidence only.


## D081 actual qualified MPU6050 acquisition, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-103 | Does compound acquisition preserve one budget and explicit observation/silence semantics? | Implementation7b46598:one600us/8192 Operation across status/STOP/15byte burst; owned Acquirer validates setup, phases, timestamps and20ms silence. Independent author/reviewer15Acquirer cases36491assertions and14native cases pass;9variants,2inert probes/eight upload refusals,14config pass. Cleanhost2/2 and sanitizer2/2 pass. Actual target147e08b1 compiles86236Bprogram/36172Bcompiler globals,exit0;46files/3ELFs/36exports/startup and exact5existing inert identities reviewed. | analysis/P2_imu_acquisition_validation.md/raw; reviews/P2_imu_acquisition_review.md/raw | HOST-TESTED/TARGET-COMPILED; separate same-model review PASS/no open findings | Linuxcompile/files only,no MCU/I2C/pad/upload. Conditional shadow inference is not physical synchronization/sample rate; timestamps are observation times. Bias/axes/yaw/full-tick WCET remain pending. SC-AJ/F091 and human gates remain open |


F103 final regression addendum: existing443tooling PASS678.339s exit0;450distinct methods across separate existing/new runs. Shared native receipts contain369exit0 plus4required negative-sentinel exits1, and prior setup variants92exit0. All D081 jobs complete. These remain software checks, not physical acceptance.


## D082 actual body-coordinate IMU estimator, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-104 | Does the concrete axis/yaw estimator distinguish new samples from retained heading? | Implementationc1188b1/contract00f0cc2; independent22cases/64370assertions and6new tooling methods pass. Fullhost/sanitizer2/2 pass,1093main+37enabledGate cases. Selected287existing methods pass;293distinct across scoped runs. Actual sourcea746b27b compile79060/32208B exit0;48files/3ELFs/36native+42math exports/startup checked. | analysis/P2_imu_heading_validation.md/raw; reviews/P2_imu_heading_review.md/raw | HOST-TESTED/TARGET-COMPILED; fresh separate same-model reviewer PASS/no open findings | No upload/MCU/pad/sensor action; map unconfigured, completion-time approximation, no loader/runtime/accuracy/WCET or physical acceptance. SC-AJ/F091 and human gates pending |


## D083 explicit countdown gyro admission, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-105 | Does Services distinguish absence and distinct source observations without changing hold/STOP? | Implementation5516bef,contract3c356ec; new31cases/2283assertions pass normal/sanitizer. Fresh reviewer94new+locked cases/3507334assertions pass both modes. Fullhost2/2PASS12.51s; sanitizer2/2PASS24.57s,1124main+37enabledGate. Selected27existing+5new methods pass. Actual target9a7c6432 compile79248/31916B exit0;46sources/3ELFs/36native+42math exports/startup checked. | analysis/P2_calibration_presence_validation.md/raw; reviews/P2_calibration_presence_review.md/raw | HOST-TESTED/TARGET-COMPILED; fresh separate same-model review PASS/no open findings | No upload/MCU/pad/sensor/motor operation, physical calibration or gate. Services interface implemented; remaining HeadingReference/Fusion/Robot/B15/app integration andSC-AJ/F091 remain pending |


## D084 complete estimator-to-Robot software, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-106 | Does actual estimator evidence reach Robot consumers without stale measurement reuse? | Implementation2c16023/contractaef3be2. Independent27cases165477assertions and5tooling PASS; freshreview118cases1727511assertions normal/sanitizer,5tooling/15config PASS. Root fullhost2/2PASS6.39s/fullsan2/2PASS31.38s,1151main+37enabledGate. Actual sourcef3bc1f7f compiles135536program/66352compiler globals exit0;51sources/3ELFs/36native/42AEABI+fmod/sqrt/startup checked. | analysis/P2_imu_integration_validation.md/raw; reviews/P2_imu_integration_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh separate same-model review PASS, no open software finding | No upload/reset/MCU/pad/sensor/motor action; physical mounting, calibration/drift/accuracy/rate/WCET, SC-AJ/F091 and human gates remain pending. Actual controller path integrated; full QTR/UI/app scheduler remains unfinished |

## D085 native QTR source and target evidence, 2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-107 | What supports checked asynchronous acquisition on the four proposed QTR pads? | Pinned/installed GPIO, CMSIS and LL sources bind D2/PB3,D4/PA12,D7/PB2,D8/PB4; checked native configuration preserves status, with direct clock/reset/lock/mode/EXTI/NVIC/trace guards. D085 selects conservative sampled RC intervals and explicit source-age admission. Final inert source57f4b001 compiles145012program/71092compiler globals, exit0; exact56source files/3ELFs/36native and42AEABI plus fmod/sqrt bindings checked. | analysis/P2_qtr_native_audit.md; analysis/P2_qtr_native_raw/source/manifest.json; target_final.json; target_57f4b001_bench-default.json; root_target_integrity.json | SOURCE-VERIFIED/TARGET-COMPILED; final host/review closure follows in validation report | Compile and offline files on board Linux only. No upload, MCU/pad/sensor/motor action or physical exclusivity/color/cadence/WCET proof. SC-AJ/F091 and human gates remain open |

F107 software validation addendum: implementation47f4d9a/contractdcd4682;
root fullhost2/2PASS7.35s/fullsan2/2PASS34.54s,1173main22840417assertions plus
37enabledGate3796846. Independent22purecases26881assertions normal/san; native
14contract/10boundary/3actualpipeline cases,11toolingmethods and16configchecksPASS.
Fresh separate same-model fullhost/sanitizer/native/config review passes against
364unchanged frozen files; final disposition in P2_qtr_native_review.md. Exact5
inert identities adopted;25existingtools+2stagingPASS,54distinct scoped methods.
All initial failures remain documented. No physical/runtime or human gate follows.

F107 final disposition: fresh separate same-model review completed 2026-09-23T14:30:40+04:00; PASS withinD085software scope with no open BLOCKER/MAJOR/MINOR. Final rootLinux tooling25/25PASS resolves the documented invocation-only failure. No physical acceptance or phase pass.


## D086 fixed A0/A1 software acquisition,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-108 | Does one native ADC1 owner acquire separate A0/A1 evidence while preserving battery-only behavior? | Implementation327c5db/contractf194579. Source audit binds A1/PA5/channel10/DTchannel_a and legal idle rank switching. Independent reviewer15methods/150positivecases/1329parentassertions PASS; rootfullhost/san2/2PASS1173main+37Gate. Finaltarget5f2c2329 compiles83912/34700B exit0;56files/3ELFs/36native42AEABI and inert startup inspected; exact5existing registry keys approved/adopted. | analysis/P2_adc_pair_audit.md/contract.md/validation.md/raw; reviews/P2_adc_pair_review.md/raw; cached official RM0456Rev6 and pinned installed overlay | PRIMARY-SOURCE/HOST-TESTED/TARGET-COMPILED; separate same-model software review | Linuxcompile/files only. No MCU/upload/ADC/pad/sensor/motor action, physical voltage/settling/carryover/START-BOTH or WCET acceptance. Decoder/app and SC-A/SC-AJ/F091 remain pending |


## D087 explicit button software routing,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-109 | Does raw A1 evidence reach logical gestures with explicit freshness and fail-closed outputs? | Implementationb69fa12/contract6c01bb4. Fullhost/san1209main+38Gate PASS; independent36cases/8tooling methods PASS. ActualMotorGate callback writes inhibit on invalid/expired/unconfigured decode. Finalcompile-only557e0e5f142288program/69864globals exit0;59exactGit/sourcefiles/3ELFs,36native42AEABI+fmod/sqrt verified;5existinginertkeys reapproved after LF repair. | analysis/P2_button_routing_contract.md/validation.md/raw; reviews/P2_button_routing_review.md/raw | HOST-TESTED/TARGET-COMPILED; separate same-model reused reviewer context | No physical voltage windows, unique START/BOTH distinction, ADC accuracy/cadence/WCET or hardware/human gate. Board Linuxcompile/offlinefiles only; no MCU/upload/pad/motor action |


F109 final disposition 2026-09-23T15:18:47+04:00: separate reused same-model reviewer PASS/no open BLOCKER/MAJOR/MINOR; final59source/ELF and5registry identity verified. Not newly fresh-context/cross-model or human gate. See reviews/P2_button_routing_review.md.


## D088 actual matrix output,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-110 | Does actual matrix rendering/native output compile and execute on the bare UNO Q? | Contract8fd11dd/source385c46c. Fullhost/san1224main+38Gate PASS; independent15renderer cases,23native/capture methods PASS;5newupload+27existing methods PASS. Exact61committed sources e50c6da3 compile80592program/32244compiler globals;40native42AEABI bindings and actual PRIMASK sequence inspected. Fresh separate same-model review PASS. Authorized normal-startup upload exit0; verified deployed loader/sketch bytes and runtime submission scalar3341->3418,zero reported failures. | analysis/P2_matrix_contract.md/native_audit.md/validation.md/review.md; P2_matrix_raw/source_integrity.json,runtime_report.json,runtime_run1/ | SOURCE/HOST/TARGET/ACTUAL INERT RUNTIME verified within stated scope | Bare UNO Q only,9read-only MEM-AP reads; initialized1 and SUBMITTED_UNCONFIRMED. No optical orientation/brightness/visibility, independent clock/WCET/IRQ interference, external sensor, physical button distinction, motor run or human gate proved. SC-A/SC-AJ/F091 remain |


## D089 QTR calibration software,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-111 | Can raw QTR calibration feed an atomic threshold bank without bypassing Robot or MotorGate inhibition? | Implementation311bf40; fullnormal/san1255main+39GatePASS;31newcases1915assertions;4toolingmethods/alternateprofiles/config18checks PASS. Fresh reviewer fixed and rechecked source-era replay defect, finalPASS. Actualcompile-onlycc4819aa145824program/72004compiler globals,67exactGit/sourcefiles/3ELFs/40native42AEABI verified;6existinginertkeys reapproved. | analysis/P2_qtr_cal_contract.md/validation.md/review.md; raw/source_integrity.json and command receipts | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh separate same-model review | Board Linux compile/files only, no MCU/upload/reset/pad/sensor/motor action. All calibration samples synthetic; no physical thresholds/buttons/WCET/human gate. App acquisition/lifetime and print transport remain pending. |


## D090 bounded IDLE dump software,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-112 | Can a retained attempt be streamed with bounded IDLE authority and reconstructed without hiding loss? |26independent owner cases4052assertions;33receiver methods including18config checks;11native methods154normal/san scenarios4870assertions PASS. Fullnormal/san1281main+65enabledGate PASS. Actual finalcompile-onlyb8bb9366,315332program/238596compiler globals and lowRAMwarning;72exactsourcefiles/3ELFs/40native42AEABI+fmod/sqrt bindings. Fresh reviewer verified strong empty __loopHook and actual main linkage/constructors, approved six existing inert source keys; final review records remaining tooling closure. | analysis/P2_dump_contract.md/native_audit.md/native_contract.md/validation.md/raw; reviews/P2_dump_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh separate same-model source review | Board Linux compilation/offlinefiles only; no MCU/upload/reset/peripheral/sensor/motor action. Setup device_init has unbounded acknowledgement waits; SC-AJ clock, actual UART/framing/cleanup, loaded freeRAM/200s/no-gap, fullapp/WCET and all human gates remain pending. |


F112 final software disposition 2026-09-23T16:49:58+04:00: fresh separate same-model review PASS/no openfindings. All72target/current files exact; strongemptyhook in3ELFs andactualmain/startup/imports inspected. Final56existingcontrolledchecks and4Windows publication/outcome methods PASS. No upload/runtime/humangate follows; software source approval applies onlysixexistinginertkeys.


## Recorder runtime instrumentation prerequisites,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-113 | Does the installed loader provide safe free-heap/stack-watermark queries? | CONFIG_SYS_HEAP_RUNTIME_STATS and CONFIG_INIT_STACKS absent. Actual packaged z_impl_k_thread_stack_space_get export address0; NEVER invoke it. Thread stack-region metadata exists; current-thread-query export nonzero. LLEXT256KiB/system32KiB/libc remaining-arena are distinct pools, not measuredfreebytes. Proposed private allocator snapshot uses exactpinned header/chain validation and a new bounded capture wrapper; serialclose/open resetsparser but hasnoexplicitRXpurge, routerrestart pulsesMCUreset. | analysis/P2_recorder_bench_native_audit.md; P2_recorder_bench_raw/native/manifest.json, installedheaders/exports/offlineELF and primaryZephyr1743741760ee sources | PRIMARY/INSTALLED-SOURCE-VERIFIED; proposed probe architecture only | Read-only boardLinux files/offlineELF; no MCUread/write/attach/reset/upload/daemon or actualfreeRAM/stack/runtime measurement. |

## D091 synthetic bare-board recorder runtime,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-114 | Does the real Robot/Gate/recorder retain the200s synthetic attempt on bareUNOQ, and what loaded memory is observed? | Software17bb38a/source1502e948; exactreviewed ELF/ZSK uploaded. FROZEN/SEALED,5001frames8events,independentCRC900325728 matches bothidenticalpool snapshots;200000998us release-toSTOP and5100000us hold inMCUtime;zero recordedloss/misses/overruns/activewrites,maxsyntheticstep203us. LLEXTfreepayload25116B/largest21604B of262144;sampledstackheadroom31208B. | analysis/P2_recorder_bench_validation.md,run.md,raw/runtime_summary.json,runtime_retry1/,storage_layout.json; reviews/P2_recorder_bench_review.md | HOST/TARGET/ACTUAL INERT MCU verified within explicitsynthetic scope | Bareboardonly.47MEMAPreads934892B/281.633s;twoidentical snapshots andindependentretainedCRC. No nativeUARTdump/physicalsensor/motor/WCET/calibratedclock/stackwatermark/allRAMminimum or humanphasegate. Expected absentIMU calibration-rejection event preserved. |


## D093 fixed ADC application owner,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-115 | Does bounded retained battery evidence preserve shared native ADC faults and real source age? | Contractd248782; independent24cases2421assertions each motor mode plus native/config/probe cases PASS; fullnormal/san1327main+111Gate PASS; fresh review6adversarialcases20059assertions PASS. Actualcompile-only4d5e21cc retains Reader/owner/Robot/Gate/recorder,76exactsourcefiles/3ELFs/40native42AEABI exports. Compiler321652program/241524globals,20620residual and lowRAMwarning. | analysis/P2_power_inputs_contract.md,validation.md,raw; reviews/P2_power_inputs_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh separate same-model review PASS | Board Linux compile/offlinefiles only. No D093 upload/reset/MCU ADC/pad/motor operation, measured accuracy/settling/clock/loadedRAM/WCET or phase gate.10/20ms are development limits; actual app scheduling remains pending. |


## Resumable I2C source prerequisites,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-116 | May the current native I2C transaction yield without consuming progress or losing unread data? | RM0456Rev6 supports retained TXIS/TC/STOP flags; unread RXDR plus shift register triggers controller stretching before next ACK. ISR reads do not consume bytes. Keep continuous burst/ownership/config and reobserve before action. ES0499Rev12 adds no contrary selected-mode condition. No service-gap/WCET or autonomous600us line-release guarantee; D081 shadow inference remains conditional. | analysis/P2_imu_resume_source_audit.md and raw/source/receipt.json; cited official ST RM/ES and pinned installed LL | PRIMARY/INSTALLED-SOURCE VERIFIED, offline cached RM/PDF hashes plus fresh ES retrieval; fresh RM retrieval failed explicitly | No board operation/measurement, physical stretching/rate/clock or human gate. |

## D094 resumable runtime source,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-117 | Does the actual native runtime retain one acquisition across bounded advances? | Independent22pure cases/17259assertions eachmotor mode;21native/728parentassertions and44legacy/932 pass. Fullnormal/san1349main+111Gate pass. Actualcompile-only b495f085 has78exactcurrent/staged/targetfiles/3ELFs, unchanged188imports/loader and40native42AEABI exports. Compiler330844program/247564globals,14580nominalremaining/lowRAMwarning. | analysis/P2_imu_resume_contract.md,validation.md,failures.md,raw; reviews/P2_imu_resume_review.md | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; same-model independent review recorded separately | Board Linux compile/offlinefiles only; no D094 upload/reset/MCU I2C/sensor/motor operation, measured cadence/clock/stretching/loadedRAM/full800us or human gate. App schedule remains pending. |


## D095 actual application transaction,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-118 | Does the actual app owner preserve complete timing, once-only application and terminal inhibition? | Contractc17f6d6;28newcases617259/617260assertions eachmotor setting PASS; fullnormal/san1377main+139Gate PASS; freshreview47703checks eachsetting PASS. Target9d6c0005 has80exactsourcefiles/3ELFs/188unchangedimports/40native42AEABI exports. Compiler149120program238628globals23516nominalremaining/lowRAMwarning. | analysis/P2_app_transaction_contract.md,validation.md,raw; reviews/P2_app_transaction_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; fresh same-model review PASS | Board Linux compile/offlinefiles only; no D095 upload/reset/MCU/motor operation or physical measurement. Native source scheduling, loadedRAM/full800us and all human gates remain pending. |

## D096 actual native runtime and memory blocker,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-119 | Does the full native application fit the pinned target build? | No. Finalsource4cb637f9 actualcompileexit1:211444program,276456memory versus262144,14312Bexcess.82exactsourcefiles/3linkedcacheELFs,188unchangedimports/loader,40native42AEABI exports; sourceidentity passes but target_compile_accepted=false. Freshreview independently verifies131711sanitizerchecks eachmotor setting and fixes2clockMAJORs; RAM remainsBLOCKER. | analysis/P2_app_runtime_contract.md,validation.md,failures.md,ram_audit.md,raw; reviews/P2_app_runtime_review.md/raw | ACTUAL-TARGET-BUILD-FAILED; linked evidence/source verified; host software results separately recorded | Board Linux compile/offlinefiles only. No D096 upload/reset/MCU sensor/motor operation; old D091 recorder image remains. No physical accuracy/clock/loadedRAM/full800us or human gate. |

## D097 passive fault access,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-120 | Does passive setup-fault retrieval remove the unintended legacy runtime dependency? | Yes: exact570ef35f threeELFs omit268B read and484B acquireMotion, retain56B getter; net696B saving.82sources exact;188imports/loader/startup unchanged. Fullnormal/san1418main+173Gate and separate685111assertion review pass. Actual compile stillexit1 at275760B/13616Bexcess. | analysis/P2_imu_fault_access_contract.md,validation.md,raw; reviews/P2_imu_fault_access_review.md/raw | HOST-TESTED/dependency reduction verified; fullapp TARGET-BLOCKED | Board Linux compile/offlinefiles only. No upload/reset/MCU/pin operation, measured loadedRAM/full800us, human gate or motor authority. |

## D098 isolated dependency experiment,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-121 | Does the isolated discovery-property change remove incidental Bridge roots while preserving the app? | Exact82-file570ef35f control exits1 at275760B; candidate exits0 at248308B,27452B saving. SixELFs/1438common object sections reviewed;493projectfunctions/startup retained;188imports become176 with no additions,39native42AEABI exports present. Conditional pristine loaderpeak252472B/largest9668B. | analysis/P2_bridge_dependency_audit.md,experiment.md,validation.md,raw; reviews/P2_bridge_dependency_review.md/raw | EXPERIMENT TARGET-COMPILED; independent same-model review PASS; production policy not adopted | Board Linux compile/file reads only. No actual load/freeRAM/WCET/MCU operation, physical/gate or motor authority. Ordinary production command still RAM-blocked. |

## D099 partial checked-build checkpoint,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-122 | Does the new wrapper complete a default actual app build? | Yes, exit0/248308B, finalELF hash identical to D098 candidate.29new+49established tooling tests pass. Adoption remains FAIL: D099-R1 MAJOR demonstrates unchecked effective recipe/compiler/hook overrides; Immediate/MATCH/library experiment and final review pending. | analysis/P2_app_build_checkpoint.md/raw; reviews/P2_app_build_checkpoint_review.md/raw | Default TARGET-COMPILED; policy WIP/REVIEW-PENDING; no blanket acceptance | Existing board-Linux compile finished before pause. No upload/reset/MCU/loadedRAM/WCET/physical/gate claim. User explicitly paused further work. |

## D100 local precompile correction,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-123 | Does the corrected wrapper close the demonstrated effective-command gap locally? |46 independent new+78 established cases PASS, old assertions unchanged. Fresh same-model review verifies84 templates,19 controls/3118 rejected mutations and reruns46 cases; no open local findings. D099-R1 addressed locally; target adoption pending. | analysis/P2_app_override_checkpoint.md/contract/source_audit/raw; reviews/P2_app_override_review.md/raw | IMPLEMENTED/HOST-TESTED/LOCAL-REVIEW-PASS; TARGET-PENDING | No corrected-wrapper target compile/upload/MCU run. Prior get-state reported device and auto-restarted local ADB on protocol mismatch; stderr/correction saved. Paused by user. |

## D099/D100 actual build-policy acceptance,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-124 | Does the corrected app-only build policy work on the pinned board toolchain? |All3mode builds exit0:248308B inert and248684B MATCH. Exact82sources/9ELFs/3packages audited; only3expected motor sections change in MATCH; startup/176imports preserved. Explicit-library fixed0/stock-control compile and reject as required. Fresh same-model review PASS; initial forced1 experiment failure retained. | analysis/P2_app_build_validation.md,acceptance_audit.md,acceptance_raw,library_raw; reviews/P2_app_acceptance_review.md/raw | TARGET-COMPILED/INDEPENDENT-REVIEW-PASS within build-policy scope | Board Linux compile/files only; no upload/MCU/run, measured loadedRAM/full800us or physical/human gate. |

## D101 integrated dump checkpoint,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-125 | Does actual Runtime now attach the recorder dump, and does its target fit? | Post-Gate attachment/abort tests pass, fullnormal/san1423main+178Gate and separate review tests pass. Initial source exceeds modeled loaderpool432B default/816B MATCH. Finalcache83600858 MATCH compiles257784B; modeled262400B peak remains256B over. | analysis/P2_app_dump_validation.md,target_audit.md,raw; reviews/P2_app_dump_review.md/raw | HOST-TESTED/TARGET-COMPILED; loader-capacity BLOCKER | No upload/load/MCU/reset, actual UART/freeRAM/WCET, physical or human gate. |

## D102 lossless frame packing,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-126 | Does lossless status packing resolve D101's modeled loader deficit? | Yes for exact85-file3bf0da00: default253772/MATCH254156B compilerpayload; modeledpeaks258376/258768 fit262144. ActualDWARF FrameBuffer126300/align4,3752B smaller; MATCHnetloader saves3632B. Fullnormal/san1434main+178Gate and freshreview PASS; serializedRuntime dump bytes unchanged. | analysis/P2_frame_packing_validation.md,target_audit.md,raw; reviews/P2_frame_packing_review.md/raw | TARGET-COMPILED/ABI-VERIFIED/INDEPENDENT-REVIEW-PASS; D101-R1 model scope CLOSED | Board Linux compile/offlineELF only. No actual load/freeRAM/WCET/MCU/physical/human gate. |

## D103 inhibited local service reset,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-127 | Does the optional actual STOP-to-service lifetime preserve inhibition and retained evidence, and fit the target? | Fullnormal/san1443main+187Gate, independent34 configured cases,4 strict real-Runtime host roundtrips and freshreview PASS.87-file1fbd7238 default/MATCH compile256332/256716B; conditional peaks261056/261448 fit262144 with1088/696B remaining spans. TargetRuntime166304B/Robot2640B; reset ownstack2680B, reserved mainstack32768B. | analysis/P2_service_reset_validation.md,contract.md,target_audit.md,raw; reviews/P2_service_reset_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/INDEPENDENT-REVIEW-PASS within scope | Board Linux compile/offlineELF only; no actual load/availableRAM/stackhighwater/full800us/nativeUART/source recovery/motor/physical/human gate. |

## D104 bare-board Runtime observation,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-128 | Does the exact no-pin actual Runtime probe load and sustain its200s zero-miss observation? | Source2bd817c4/software1fa2a01 deployed identities verified;200001epochs/0misses,actualS..Cmax269us,Runnermax285us,alloutputrequests inhibited. Currentpoolfree28668B/largest25172B; sampledPSPheadroom30952B. Stable diagnostics/pools; decoderacceptancePASS. | analysis/P2_runtime_inert_validation.md,raw/runtime_summary.json,runtime_run1; reviews/P2_runtime_inert_review.md/raw | ACTUAL-BARE-BOARD-MEASURED within exactprobe scope | BareUNOQ2629958581 only. No sensors/nativeUART/motors/full-app800us/clockcalibration, stackwatermark or human gate. |

## D105/D106 software and conditional target fit,2026-09-23

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-129 | Does actual Runtime deliver a newly committed calibration bank through the bounded owner? | D1052eb97cc and receiver36ae9bc pass independent normal/sanitizer, active-Gate, MATCH exclusion and strict host roundtrip checks. No retained-success retry or config mutation. | analysis/P2_calibration_delivery_validation.md/raw; reviews/P2_calibration_delivery_review.md | IMPLEMENTED/HOST-TESTED/REVIEWED; synthetic source fixtures | Native UART and physical calibration pending; no upload/gate. |
| F-130 | Does one unchanged installed native pin table recover D105 target capacity? | Exact91-filed72bff70 retains one560B/70-entry table with exact descriptor relocations. Default/Immediate peak261688/span456; MATCH260056/span2088 in262144 pool. Native27+26methods, independent cross-unit variants and scoped review PASS; D105-R2 conditional fit closed. | analysis/P2_pin_table_validation.md/raw; reviews/P2_pin_table_review.md/raw | TARGET-COMPILED/OFFLINE-ABI-VERIFIED/REVIEW-PASS; conditional loader model | Linux compile/offline files only. No full-app load/freeRAM/WCET, physical pin verification or gate. |

## D107 opponent bench,2026-09-24

| ID | Question | Observed answer | Source | Confidence | Hardware-checked |
|---|---|---|---|---|---|
| F-131 | Is the named opponent bench implemented and checked without inherited Bridge startup? | Independent24runner cases normal/sanitizer,2native cases,invalid-config/polarity variants,15new+85old policy methods PASS. Checked96-file332787f0 default/Immediate share ELF2a20fbc1; payload3733/conditional loader peak4496. Separate review PASS; both earlier generic artifacts remain rejected. | analysis/P2_opp_view_validation.md/raw; reviews/P2_opp_view_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS within scope | Board Linux compile/offline files only. Default grants false; no upload,pins,sensor/optical/physical acceptance or gate. |

| F-132 | Does geometric SENSOR_VIEW preserve FL15/FC identity after D108? | Two corrected coordinates; unchanged masks/control. Independent red/green proof and fullnormal/san1446main+187Gate PASS. Exact91-file618d3a96 default/MATCH finalELFs change only two read-only bytes vsD106; conditional peaks261688/260056 unchanged. Separate review PASS closes OPP-VIEW-1 in software. | analysis/P2_display_channel_validation.md/raw; reviews/P2_display_channel_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS | No new upload/MCU/optical/physical/gate claim. |

| F-133 | Does the finite named QTR bench preserve raw evidence and fit the checked target? | Firstsource54b0a21b; independent normal/san32cases/20131assertions, native2/39, capacity1/0 and flag/registry checks PASS. Exact96-file5c468e20 default/Immediate share ELFe65ffd46; payload31929/conditional peak32920. Separate source/host/policy/target review PASS, minor evidence newline claim corrected. | analysis/P2_qtr_raw_validation.md/raw; reviews/P2_qtr_raw_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS within scope | Board Linux compile/offline files only. Grants false; no upload, pad permission, physical color/cadence/WCET/readout or gate. |

| F-134 | Does the named battery bench preserve finite fresh evidence through the battery-only ADC path? | D110b5fa7eea passes28 executable profiles incl normal/san31cases/21066assertions and public saturation, plus114 policy methods. Exact96-file8e3efb92 default/Immediate share ELF508bedea; payload12333/conditional peak13200. Separate source/test/target review PASS with no findings. | analysis/P2_vbat_validation.md/raw; reviews/P2_vbat_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS within scope | Board Linux compile/offline files only. False grant; no actual ADC run, battery accuracy, readout, electrical/pin permission, full-app WCET or gate. |

| F-135 | Does the named finite IMU bench reuse actual estimator/calibration with bounded immutable evidence? | D111 firstsource6d3c6c5f passes28 executable profiles; normal/san31cases/1342660assertions each, additive Native startup3/38 each,108 registrychecks and121 policy methods. Exact96-file9520e473 default/Immediate share ELFe55565ff; payload26833/conditional peak28224. Separate scoped source/test/target review PASS, no findings. | analysis/P2_imu_heading_bench_validation.md/raw; reviews/P2_imu_heading_bench_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS | Board Linux compile/offline files only. False grants; no IMU run, drift/rotation accuracy, readout, supply/mount/clock acceptance, full-appWCET or human gate. |

| F-136 | Does the named A1 bench preserve raw/actual-decoder evidence without qualifying unknown electrical levels? | D112bc2def36 passes30profiles incl normal/san35cases/21759assertions and exhaustive16384-code configured/overlap profiles,90registrychecks,128policy methods. Exact96-sourcebf67d46d default/Immediate share ELF4fa8171d; payload16245/conditionalpeak17128. Separate scoped review PASS/no findings; superseded firstsource/target retained. | analysis/P2_ui_bench_validation.md/raw; reviews/P2_ui_bench_review.md/raw | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEW-PASS | Board Linux compile/offline files only. False grant; no actual ADC/stimulus/window/START-BOTH/gesture/display/readout/WCET or gate evidence. |

| F-137 | Does opt-in dump connection evidence preserve bounded receive-only behavior and truthful failure evidence? | Final5a78257a, independent42new+33legacy methods and separate private75/75 PASS; exact source/contract/test bindings and no open findings. Initial fixture failure and production missing-transport red/green retained. | analysis/P2_dump_receiver_arm_validation.md/raw; reviews/P2_dump_receiver_arm_review.md | IMPLEMENTED/HOST-TESTED/SCOPED-REVIEW-PASS | Controlled substitutes only; no actual Linux socket/MCU/native UART or physical/gate claim. |

| F-138 | Does the exact D113 receive-only connection observer work on the connected UNO Q Linux environment? | One reviewed12s run observed CONNECTED then TERMINAL/TIMEOUT with0bytes; remote/host capture exit1 expected, no outer timeout or successful bundle. Closed12013.388427ms after start; boot/router/socat/existing sockets unchanged. Original receipts and14-file manifest verified. | analysis/P2_dump_receiver_arm_raw/reviewer/smoke_scope.md; smoke_runs/01aac4fffa214aa2b332b261734de7e9; root_smoke_verification.json | ACTUAL-BOARD-LINUX-OBSERVED, exact5a78257a | BareUSB2629958581 Linux only; no MCU action, nativeUART transfer/registration/cleanframing, physical acceptance or human gate. |

| F-139 | Is the enabled bare A1 diagnostic wrapper isolated, staged correctly and target-compiled? | Independent/private24 policy methods, rootunion145 PASS. Exact96-source396bcc45 checked default target ELF76e23fe0/ZSK567fb90d; all94 shared sources and all compiled functions except setupgrant0-to1 unchanged. Runner9892 at rawET_REL BSSoffset0; conditionalpeak17128. Separate scoped reviewPASS. | analysis/P2_ui_adc_probe_firmware_validation.md/raw; reviews/P2_ui_adc_probe_review.md | IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/SCOPED-REVIEW-PASS | Board Linux compile only; no ADC execution, loadedRAM/physical clock/pin/button or human gate evidence. |

## F140 - Pinned bare ADC readout and one-attempt guard (software-verified)
D114 readout/guard software complete: capturef4b3 passes independent/private42; guard1aa passes22; boardd1f retains145 prior policies; manifest-only narrow39 PASS. See P2_ui_adc_readout_validation.md and separate reviews. MCU still D104; no new upload/reset. Exact run01 plan and Linux tool staging precede final bound review, then one identified inert upload/passive capture. SC-A/SC-AJ/physical/human gates remain pending.
Evidence: analysis/P2_ui_adc_readout_validation.md, raw/author_capture, capture_reviewer, guard_author, guard_reviewer; app_build_raw/ui_adc_guard_prior145 and ui_adc_manifest39. Hardware-checked: NO for ADC/run; only Linux input file copies actually occurred.

## F141 - Actual bare native A1 diagnostic (2026-09-24T02:37:40.596486+04:00)
Verified one identified D114 run on ADB2629958581 with source396bcc45/ELF76e23fe0/ZSK567fb90d. Actual COMPLETE128, faultNONE, contiguous1..128, zero missed releases, raw2061..3984; identical9892B Runner reads SHA3d33a0ed. Setup957 MCUus; source54..60, read59..65, sampled duepoll63..70. All decoder results UNCONFIGURED/INVALID, never valid release. Exact18reads587232bytes22commands and63-file transfer verified; separate210-check actual reviewPASS and independentliteraldecode agree.
Evidence: analysis/P2_ui_adc_probe_actual_validation.md; analysis/P2_ui_adc_probe_actual_analysis.md; reviews/P2_ui_adc_actual_review.md; raw actual_run01, run01_build_receipt68f3, upload/capture receipts and manifests. Software9bb947b. Hardware-checked: YES only this source-bound bare raw-acquisition observation; setup is human-reported. Physical acceptance remains false, SC-A/SC-AJ/calibratedclock/voltage/buttons/PINMAP/fullapp800us/motors/gates not established.

## F142 - D115 finite motor inhibition preparation (2026-09-24T02:51:44.704000+04:00)
Software/target-verified only: fivefile firstsource7e1b99a4 unchanged; independent/private58cases4,242,601assertions normal+san each,4Native/defaultprofiles,6flagrefusals,8newpolicychecks. Rootfullnormal+san1457main45,984,586asserts and187activeGate4,536,952;175policymethods pass. Exact95sourcebb3b462a default/M0 receipt a7b05d1e; ELF7a9c5cb5/ZSK682f3b65,25524bytes,payload5556,conditionalorderedpeak6312 in pristine262144pool, free255832/largest255828.35 usedimports resolve. ABI Runner120/Native40/Report24@88/Halt16/Port44.
Evidence: analysis/P2_motor_stand_inhibit_validation.md; analysis/P2_motor_stand_inhibit_raw; reviews/P2_motor_stand_inhibit_review.md. Scope: setup/inhibit owner with defaultfalsegrant, no apply/reset/motionrequest. Hardware-checked: NO; no upload/reset/motor/native-pin action. B4directional/brake/poweredkill/B7/R6 policy, physical timing/wiring/gates remainopen. ActualMCUlastimage remainsD114396bcc45.


## F143 - Native full-dump cadence limit and FIFO feasibility (2026-09-24)
Source-derived, not hardware-measured: existing FIFO-off native owner cannot send the full5001-frame stream within300s at one call per1kHz. Conservative frames-only lower bound614013 wire bytes exceeds600000 two-store capacity. RM0456Rev6 table686 documents eight-entry LPUART FIFO; setup-only FIFO proposal preserves all current byte/time limits. Full5001+4096 worst-width model requires212658 calls at8 stores/call (283574 at6); actual service rate and UART grants remain unproved.
Evidence: analysis/P2_native_dump_throughput_audit.md (pinned source hashes and primary source pages/links); analysis/P2_recorder_transport_raw/coordinator/cadence_arithmetic.json independently checks integer arithmetic. Hardware-checked: NO. DUMP-RATE-1 OPEN; no native code/config/board action or gate follows.

F143 pre-adoption correction: independent D117 public preflight identified that D073 formats arbitrary raw byte values, including invalid enum/mask values. The earlier166-byte frame model assumes semantically valid widths. The stronger unrestricted170-byte bound controls D117:217659 calls at8,288575 at6,331091 at5, and1,505,629 wire bytes. Both original and corrected arithmetic remain preserved; no hardware claim. See P2_dump_fifo_test_preflight.md and raw/coordinator/unrestricted_cadence_arithmetic.json.

## F144 - D116 full synthetic recorder transport software (2026-09-24T03:24:52.542645+04:00)
Firstsource unchanged; independent/private normal+san22cases4,202,902assertions each, actual5001frame/8event fullattempt/reset/menu/Transfer stream532562B in10027chunks, strict receiver/source comparisonPASS; slow300000B TOTAL prefix refusal retained. Fullnormal+san each1478main50,172,466assertions+187Gate4,536,952;183policymethodsPASS. Exact95sourcee2cd303f checkeddefault ELF538a7c81/ZSK96b5f843; conditionalorderedpeak220280/span41864/largest41860, Runner164176/native204. Source/test/target reviewPASS; initial fixture/audit failures retained.
Evidence: analysis/P2_recorder_transport_validation.md/raw; reviews/P2_recorder_transport_review.md. Hardware-checked:NO; boardLinuxcompile/offlineELF only, no upload/reset/MCU or physical/gate result. Native FIFO-off throughput DUMP-RATE-1, UARTownership/framing and actualdelivery/timing remainopen. D114396bcc45 remainslastMCUimage.

## F145 - D117 explicit native TX FIFO software (2026-09-24T03:48:32.722241+04:00)
Finalnativefdd3df0b; independent frozen first26methods/599commands PASS without amendments, new201stimuli21,915,290checks eachnormal/san; unchanged D090/D116 and factory193 PASS. Private12new methods PASS. Fullnormal/san each1478main50,172,466assertions plus187Gate4,536,952. FullD116native replay532562payload/682967wire/99267modeledcalls; unrestricted rawcapacity5001frames4096events/1496311wire/215676calls. These are host models, not physical service-rate evidence.
Exact91sourcee820c0e1 appdefault ELF8379f152 peak262136/span8; MATCH Immediate ELF79844885 peak260504/span1640. Exact95sourcece5a1f4e recorder ELF44297059 peak220744/span41400. Native208@data; Runtime166376default/166304MATCH, Runner164176. Firstdefault8-byte deficit and equivalent repair1 preserved; conditional final allocations pass. Evidence: analysis/P2_dump_fifo_validation.md/raw; reviews/P2_dump_fifo_review.md. Hardware-checked:NO; Linuxcompile/offlineELF only. Actual loadedRAM, nativeownership/framing/ACK/service/delivery and full800us remainpending; D114396bcc45 remainslastMCU, no upload/reset/motor/humangate.

## F146 - Native dump Linux prerequisite follow-up (2026-09-24T03:53:56.128348+04:00)
Actual read-only ADB2629958581 inventory identifies kernel6.16.7-g0dd6551ae96b and ttyHS1 char239:1 on qcom_geni_serial. Official Arduino kernel commit0dd6551ae96b78024086e72339fefbef6fcc604b matches release identity, not a reproducible running-binary comparison. TCIFLUSH clears flip+line-discipline queues but is not DMA completion; last-close matters, driver cancellation results may be hidden, and open may return without successful RX-DMA preparation. CurrentUID1000 sees2/167 fd directories;165 denied includingrouter. PID sets are equal; onefd vanished. Original mistaken ordering/membership claim and corrected report/index retained. All19 indexed final artifacts/report hashes verified.
Evidence: analysis/P2_native_dump_prerequisite_followup.md/raw and separate review. Hardware-checked: Linux metadata/access only; no UARTopen/read/RPC/service/privilege/MCU action. Exclusive-holder, quiescence/cancel/reopen and framing grants remain unproved; no preparation helper may declare READY from present evidence. D117softwareed5a9dea remainsaccepted separately.

## F147 - Exact unchanged default/M0 app load and sampled progress (2026-09-24T04:42:52.533106+04:00)
One app-default-e820c0e1-run01 upload on human-reported bare UNOQ2629958581, software9b4afcb2; checked10f172276dcb46edab7c991b8cf03e3f reproduces sourcee820c0e1/ELF8379f152/ZSKc60443cd. Actual capture exit0,58reads/62commands/1404304B/422.776532s. Both fullflash brackets match, one validated resident sketch, Runtime RUNNING/NONE epochs212505→292059; missed0 and storedmax513us in both; Transaction ACQUIRING/NONE, initializationfalse. Two allocator decodes agree4500free/4364largest/257512used/132overhead; metadata matches while livepayload differs.
Evidence: analysis/P2_app_default_actual_validation.md/raw; reviews/P2_app_default_actual_review.md; separate first744-check actual audit PASS and183files rehashed. Hardware-checked: exact bare-board MCU flash/RAM observations only. No transient8-byte minimum, stack/totalRAM, full800us/calibratedclock, electrical/pin/sensor/UART/motor/physical/human-gate claim. Currentapp remainsloaded with M0/falseoptionalgrants; upload/capturebothconsumed, no retry/reset/restore.

## F148 - D134 native compilation and loader deficit (2026-09-24T15:32:56.340156+04:00)
Fresh bare-UNOQ inventoryserial2629958581 verifies CLI1.5.1/core1.0.0. ExactD134source c598cad1 app compiler/policyPASS, ELF9cbde4df/ZSKb91c1aec; loader39d4a4fd unchanged. Compilerpayload257320B is not loaderfit: conditional pristine peak262176B exceeds262144B pool by32B. D128comparison +48B copiedtext, Runtime166376 unchanged. Exactreactive_timing39605f34 compiler/policyPASS, ELFdbc68caa; conditionalpeak257128/free5016/largest5012, Runtime166496.
Evidence: analysis/P5_native_compile.md and raw manifests/actualcommands/receipts/accounting. Source134snapshotfiles unchanged and123buildinputs matchD134hostfreeze; excludesD135. Hardware-checked:NO for MCU/peripherals; actualLinux targetcompiler only. No upload/reset/MCU/pins/motor/physicalgate, actualloadedRAM/stack or full800us proof. Defaultapp nativefit BLOCKED; proposed zero-window size reduction unimplemented/unvalidated.

## F149 - D135 opener profile native compile and layout (2026-09-24T15:45:14.8925240+04:00)
Exact2d924f1f production, stage97f8bec1/receipt afc5f0cc638745bf8cb44f85682e2422, defaultM0 flags compile PASS first invocation. ELF9583f94d; program172752, payload256044, retained loader-model peak260816/free1328/largest1324. All61 relocation-used imports resolve in checked packaged loader. Offline DWARF Runtime166424, Robot2680, Input200, Pending88 (tag in padding), Tick200; recorder capacity unchanged. Root independently rehashed44 artifacts and report successfully.
Evidence: analysis/P5_abort_native_compile.md and raw/evidence_index.json. TARGET-COMPILED/CONDITIONAL-MODEL-FIT only; wrapper omits default app native dump transport, so F148 default32B deficit remains. No upload/reset/MCU/physical trial, calibrated clock, live stack/RAM/WCET, native extraction or human gate.

## F150 - Isolated default-app code-size experiments (2026-09-24T16:04:36.3723862+04:00)
Candidate1 source9ba3caa4/ELFc6d2a4da compiled but orderedloader modelpeak262168/deficit24B. Candidate2 d77ccbc7/ELFb0cc2375 compiled butpeak262176/deficit32B; Direct restored20B while switchgrew20B. Escape208/Robot2640/Runtime166376 and44 oldqueriedoffsets unchanged.134finalevidencefiles independently rehashed. Both unadopted; optimization stopped aftertwo failedfit candidates, no candidatehosttests or thirdfixcompile.
Evidence: analysis/P5_default_fit_experiment.md/raw and reviews/P5_default_fit_review.md. Separate source-equivalence reviewPASS is not nativefit or adoption. OriginalD134default32Bdeficit is observed; unmodifiedD135default is not targetcompiled. No upload/reset/MCU/physical/human gate.

## F151 - Unchanged production MATCH/Immediate compile and conditional loader fit (2026-09-24T21:57:56.772014+04:00)
ExactD135production staged18cbf8bf/receipt e555c86831ce4f74a5e366c897fd856f compiled beforepause with MATCH1/MOTORS_ALLOWED1/Immediate; ELF eae32ea3, program173820B/payload255752B. Current retained orderedmodel peak260560B leaves1584B span/1580B largestpayload in pristine262144pool; compiler nominal6392B is notloaderfree. All62relocationusedimports resolve against freshlyhashed packagedloader39d4a4fd. Root rehashed42rawfiles plus3dependencies.
Evidence: analysis/P5_match_native_validation.md and raw/validation_index.json, actual compiler/account/GDB file-query receipts. Hardware-checked:NO for MCU/peripherals; resumedboardaccess was Linux read-only inventory/filehash/offlineGDB only. HostADBdaemon auto-restarted for40/41versionmismatch, notMCUreset. No newcompile/upload/run/defaultprofilefix/liveRAM/stack/WCET/physicalgate. Separate scopedreviewpending.

F151 scoped review disposition 2026-09-24T21:58:37.004159+04:00: separate same-model read-only review PASS/no material findings. Independent ELF parser reproduces255752payload+4808loaderoverhead=260560peak,1584span/1580payload;42raw+3dependencies and102staged/133working bindings verified. Evidence reviews/P5_match_native_review.md and compact independent check_result.json. Same conditional limits apply; no gate or default-profile repair.

## F152 - D138 informational readiness software and MATCH target qualification (2026-09-24T23:32:13.224071+04:00)
D138 is implemented, host-tested and target-compiled with separate fresh-context same-model review PASS. Full22 host targets and ordinary20/configured31 cases perM0/M1, normal and ASan/UBSan pass. Exact sourcefcddbd8e, MATCH/Immediate receipt04b266d5, ELFcb5fbb53: compiler payload256440B, conditional ordered peak261280B, span864B/largest860B,62 used imports resolved. Sixteen target size/alignment pairs and72 prior offsets are unchanged. All43 protected sources remain exact. Evidence: analysis/P7_readiness_validation.md, analysis/P7_readiness_native_validation.md, reviews/P7_readiness_review.md. This is not a measured load, live memory/stack/WCET, calibrated battery/UI observation, full rearm/log workflow, physical acceptance or human gate. The default/M0 image is separately qualified under D139.

## F153 - D139 current default/M0 negative loader qualification (2026-09-24T23:32:13.224071+04:00)
Exactly one unchanged-current-source default/M0 compile-only invocation passed: sourcefcddbd8e, receipt52b4ba3a, ELF72a8bfcd, compiler payload257848B and nominal4296B remainder. Exact ordered pristine-loader model instead requires262736B in262144B: deficit592B. Its first failing4400B global-symbol allocation has3824B available; the subsequent16B export copy explains the full hypothetical peak deficit. The model validator saves the negative account and returns1. All61 imports resolve;16 target type size/alignment pairs and79 old offsets match D134 default. Runtime166376B is72B larger than the current MATCH profile as expected, not new ABI growth. Evidence: analysis/P7_default_qualification_raw/app/ordered_account.json and related source/import/layout receipts; separate review is being finalized. TARGET-COMPILED / CONDITIONAL-FIT-FAIL, no actual loading/upload/reset/liveRAM/stack/WCET/physical or gate claim. No repair or second compiler is part of this baseline.

F153 final review disposition 2026-09-24T23:38:12.327347+04:00: review6321c944 and final receipta48bb845 independently bind86 raw files/1708702B, seven dependencies and reportfad32546. Evidence accepted, one current default release-fit BLOCKER remains; no additional findings. See reviews/P7_default_qualification_review.md.

## F154 - D140 installed Static-link source and packaged-file qualification (2026-09-24T23:47:08.429572+04:00)
The pinned core exposes Static mode. Fresh file-only disassembly confirms linked flag0x02 dispatches to Thumb0x08100011 before llext_load. Exact static scripts put payload flash at0x08100010 and writable app storage in[0x20013890,0x20053890); packaged allocator aliases reach libc arena[0x20053890,0x200c0000), not the separate system heap. Fresh executable hashes and Go VCS metadata bind three packaging tools; exact main.go files resolve in ArduinoCore-zephyr at those revisions, despite standalone-looking module names. This is source/provenance and packaged-file evidence, not a rebuilt loader/tool or a static image/runtime observation. Evidence: analysis/P7_static_link_research.md, analysis/P7_static_link_sources.md, their raw/source indexes and reviews/P7_static_link_research.md (6d3ab597). No static compile/load/fit/WCET/physical/gate acceptance. Current dynamic admission and D139592B deficit remain.


## F155 - Static artifact inherited TLS symbols (2026-09-25T02:05:56.567390+04:00)
Installed-file/target-artifact verified, no MCU execution: D144 static compile returned0 but the original D142 parser rejected six STT_TLS6 symbols. D146 checked installed tls-syms.S SHA68bb1476 whose header matches packaged firmware39d4a4fd; the actual map15da1417 LOADs objectbf3b5c57. Its six GLOBAL/default/ABS/size0 offsets (8,8,16,20,24,28) match debug/temp/final forms. The object has no allocated bytes or relocation; map has no actual tdata/tbss inputs and discards the direct accessor wrapper. Official generator: https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/extra/gen_provides.py#L268 .
Evidence: analysis/P7_static_tls_provenance_validation.md, observed hashes/receipts, independent local analysis and collection review. Confidence: verified for these exact installed/source/artifact bytes. This does not exclude indirect/native TLS use or establish native ABI/runtime correctness, memory/WCET, physical acceptance or a gate. The original rejection remains; D147 adds only a separately tested pure structural interface.


## F156 - Existing static packet structural/package validation (2026-09-25T02:19:12.339568+04:00)
Installed-file/target-artifact verified, no MCU execution: D148GOdbb5f1a4 applies testedD147cd52a29a to D144's exact seven artifacts, preserving original D142 rejection. Five read-only commands exit0 and all source/installed/artifact postchecks pass. FinalELF5cc2dfde170616B, flatpackage5f08afe093096B; flashload93080B, staticRAMspan167792B, regiontail94352B. Three normalizedimages, initializationbounds, bothpackagingforms and exact six inherited TLS tuples pass; no weakundefined symbols. Confidence verified for exact bytes only, not static adoption/native binding/ABI/runtime/physical acceptance. The region tail is not live freeRAM/stack/heap.
Evidence: analysis/P7_static_native_actual_validation.md and linked original command/results; separate reused same-model actualreview12cbec6b PASS. OriginalD14425commandreceipts+inputs/result unchanged; D139dynamic592B deficit remains separate. No compiler/upload/reset/source/config/test changes or human gate.


## F157 - Static/current-default queried debug-layout equality (2026-09-25T02:27:56.075972+04:00)
Target-artifact/file-only verified, no MCU execution: D149GO2cd8d795 reads existing debugELF0f7f2825 using pinnedGDB8e709e32. All16 selected type size/alignment pairs and82 member offsets equal current-default baselinefe137985, including Runtime166376B/align8. ActualGDB and four independent bracket checks exit0, no stderr/postcheckerrors; all230 baseline queries retained with object auto-loading explicitly disabled. Current sourcefcddbd8e and all Claim/FileRecord/installed/local/stage bindings remain unchanged.
Evidence: analysis/P7_static_native_abi_validation.md, original native_abi/0003.json output and comparisonresult, separate reused-context actualreview3f4d20b7 PASS. Confidence verified only for these selected debug-layout entries, not complete native function/device ABI, actual execution/liveRAM/stack/WCET or physical/human acceptance. No source/config/test/production change, compiler/upload/reset or runtime permission follows.


## F158 - Bounded static native binding evidence (2026-09-25T02:30:41.957002+04:00)
Local target-artifact audit only:168 present linker-provided ABS values agree in final/debug forms;22 instruction-decoded native veneers match named packaged-loader exports.62 distinct catalogued native values bind61 retainedD139 export values plus D140printk080173d5.119 table entries contain118 named device pointers and one null. Five allocator/random wrapping aliases are absent/[!provide] with no identified reference in checked encodings, not a missing-definition defect or whole-program no-allocation proof.
Evidence: analysis/P7_static_native_bindings_audit.md, raw/native_bindings_audit.jsonc3233593 and separate reused-context scopedreviewf738ef54 PASS. Six local commands0, input/tool/source103 hashes unchanged. Confidence verified for enumerated encodings only. Complete indirect driver/API dispatch/reachability remains pending, demonstrated by opponent setup08111788 loading device+8 then API+0. Next existing-source audit is analysis/P7_static_native_dispatch_next.md. No board action/runtime/physical/gate claim.


## F159 - Selected static/native driver boundary file evidence (2026-09-25)
D150 partially observes matched device/device_ops/GPIO/PWM/RCC/pclken layouts,
scalar widths and selected driver values for current sourcefcddbd8e and packaged
loader39d4a4fd. Its collector remains FAILED on the ambiguous init-name query;
that failure is never relabelled. D151 GOa60ef466 separately reads exactly18 bytes
[08019e5c,08019e6e) with the pinned GDB. Five clean commands and all postchecks
establish its conditional tail branch to retained do_device_init08019e2c, which
calls device.ops.init at+20. Actual GPIO/PWM/RCC application instructions and
selected callback types agree with the observed native targets.

Evidence: analysis/P7_static_native_dispatch_validation.md and its linked three
companion reports/compact receipts. Preserve original native_api/result.json
FAILED and native_init/result.json COLLECTED. Confidence: verified for the selected
file boundary only; combined fresh-context review is pending. M0 still initializes
GPIO/PWM; empty SetupGrants keep optional services disabled. No MCU execution,
whole native dependency proof, live RAM/stack/WCET, static production admission,
physical acceptance or human gate follows.

F159 final scoped review 2026-09-25T02:53:01.140514+04:00: separate fresh-context same-model review
e4eca064 PASS with no open findings. Independently checked31 receipt inputs,
17 local pins,103 working and102 staged source files, and836 retained application
instruction/literal rows against ELF bytes. D150 remains FAILED; D151 closes
only its missing wrapper edge. No runtime, physical or human-gate acceptance.


## F160 - Static upload dependency inventory (2026-09-25T03:06:32.969894+04:00)
Verified file/source evidence only: three Linux read-only calls exited0/empty stderr; eleven installed tools/configs/loader identities, mem_helper include and seven higher-priority absent shadow paths were recorded. Pinned CLI version1.5.1 commit01f3d4f2b. Source-derived raw app.ino.bin selector resolves the checked static flat sibling; no actual upload is claimed. See analysis/P7_static_startup_dependencies.md and analysis/P7_static_upload_route.md. No MCU read/reset/compiler or physical result. Recheck identities/paths before a separately scoped run.


## F161 - Current static observation interpretation (2026-09-25T03:12:05.758851+04:00)
Verified host/file evidence: D152 exact18requests/713656B pure parser passes37 frozen spec-derived methods; fresh-context reviewcdae7896PASS. Checked loaderELF39d4a4fd yields263680 physical bytes/SHAe9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 using pinned helper885c4e42; packagedBIN6b2ffd differs at offset260287 (ELF0/BIN255). Independent review53cb6ee7 also checks both historicalD118 brackets. Original contract assumption retained6d45e3b5, corrected8fa01d1f. Evidence analysis/P7_static_capture_validation.md. No current MCU state, runtime/stack/WCET/physical acceptance is inferred.


## F162 - Explicit empty CLI config (2026-09-25T03:20:46.302183+04:00)
Actual read-only pinnedCLI1.5.1/01f3d4f2b accepts --config-file /dev/null with fixedminimalenvironment; version and two configdump queries all exit0/empty stderr. Correct nested config reports data/home/arduino/.arduino15, user/home/arduino/Arduino and updaterfalse. Original top-level projectionnull retained; corrected fulloutput in P7_static_startup_raw/cli_isolated_directories.json. Source rationale and exactenvironment in P7_static_upload_route.md and P7_static_startup_design_review.md. No upload/reset/MCUread or compiler; futureexactargv/grant stillpending.


## F163 - Finite passive collector host behavior (2026-09-25T03:28:45.809989+04:00)
D153source1aa602d0/bindingsc2c87df6/contract0371739e passes46 independent plus4 reviewer supplemental host methods on firstexecution; scopedrevieweed7414dPASS. Exact18reads/713656B, durableclaim, deadline/timeout, mismatchedflashbeforeRAM and partial/fault/clock evidence are verified in controlledfixtures. No actualMCUcapture/sourceorigin/kernel-lock/quiescence/liveRAM/WCET/gate claim. Evidence analysis/P7_static_capture_remote_validation.md.

## F164 - Existing native loader utility (2026-09-25T03:28:45.809989+04:00)
Fresh Linux file-only observation finds p0_capture.py18880B/SHA885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c beside the existing checkedpassiveconfig (fullpathin analysis/P7_static_startup_raw/installed_loader_helper.json). Notimported/executed. Reusehash-checkedbytesforloader_image ratherthan anothercopy. Localfour-source inlinepayloadestimate22942UTF16units leaves7058below30000; finalbootstrapstillrequiresqualification. No compiler/upload/reset/MCUread.


## F165 - Installed core and uploader selection files (2026-09-25T03:38:33.159664+04:00)
Fresh Linux file-only observations: only zephyr1.0.0 and arduino remoteocd0.1.1
versions were found; selected boards/platform bytes exactly match retained
core sources. Both core local overrides, both global platform files and user
hardware directory are absent. Installed metadata303397B/SHA985d3ba1 has
wrapperversion2 and one matching platform; its toolsDependencies exactly match
the indexed zephyr1.0.0 entry, including remoteocd0.1.1. CLI and uploader hashes
match F160; /dev/null is character1/3. Selection is a source-derived inference
from observed files, not a newly executed CLI resolution/upload. Board-details
initialization can download/migrate dependencies, so it was deliberately not
run. Original100KB content-bound rejection and empty root metadata projection
remain, followed by observed-bound/nested corrections. See
analysis/P7_static_cli_selection.md and its four original receipts. No compiler,
MCU read/reset/upload, new tool installation or physical/gate evidence.


## F166 - CLI initialization prerequisites observed (2026-09-25T03:50:08.003244+04:00)
Two file-only Linux calls exit0/empty stderr. Data/staging/packages and both
indexes exist; library index58226703B/SHA36dad4c2. All five latest indexed
builtins have checked regular0755 executable files (no .exe alternatives).
Other package fallback roots contain only tools, excluded by pinned loader;
sole selected platform metadata is current format2. Independent source/receipt
review in analysis/P7_static_cli_initialization.md closes those bounded existence
and migration-condition gaps. No executable invoked or package downloaded. This
is not successful initialization/runtime purity, futurestability or native-run
authority; later coordinator must recheck exact sources/paths/HEAD/run.

## F167 - Fixed upload wrapper host behavior (2026-09-25T03:55:21.028709+04:00)
D154 current source81668c79/contract7fa1c0f0/bindingsa31bca78 passes55 unchanged independent methods3.685s/exit0 plus3 reviewer cases0.205s/exit0. Original53/55 failure preserved; first implementation repair fixes primary processerror and known-outcome retention through cleanup. Review8efe48a3 PASS within host scope. Controlled substitutes establish wrapper behavior only, not native upload/startup/quiescence or physical acceptance. Evidence analysis/P7_static_upload_validation.md.

## F168 - Fixed startup host composition (2026-09-25T04:08:23.503879+04:00)
D155source6f86e645/contract2bdbc3c9 passes30 independent+10 reviewer host methods; review26fcf2f7PASS. Actual local source/artifact binding construction passes, sixcommandforms, finalinlineupload28068/capture24981UTF16units below30000. No board command dispatched. The103workingfiles/102stage remainchecked; receipt source_file_count=null is a projection limitation, not absence of source checking. See analysis/P7_static_startup_launcher_validation.md. Native upload/startup/freeRAM/WCET and gates remain pending.

## F169 - Actual upload file-limit failure (2026-09-25T04:18:00.171497+04:00)
D156native_run01 atreviewedHEADe173053c FAILED: CLIchildexit1/reaped/notimeout, loadercopy filetooLarge, capture0;9transportcalls0 andallrecordedfinalchecksPASS. Installedloader2303728B cannotfit inheritedRLIMIT_FSIZE1048576. Remoteocd0.1.1source returnsfrombinarycopyfailure beforeitsOpenOCDlaunch; inferenceonly. Separatefile-onlyinventorysameboot finds/tmp/remoteocd dev34/inode800 andoneUID1000 regular0664loaderfile1048576B/inode801/SHA256b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf. Localretainedloader39d4a4fd exactprefixmatches. No MCUstartup/freeRAM/WCET/gateproof, no retry. Evidence analysis/P7_static_startup_actual_validation.md and linked originalrecords.

## F170 - Real host inherited file-copy limits (2026-09-25T04:21:45.057377+04:00)
Independent test_upload_file_limit.py163ed282 usescheckedretainedloader39d4a4fd readonly andharmlessrealLinuxparent/descendantcopies. FourfrozenmethodsPASS0.393s/exit0;1MiBcapreproducesb6fced5c partial/EFBIG, exact2303728Bcapcopiesfull,one-byte-overfails,belowcapsucceeds. Bothinputpinsunchanged; rootobservedzeroownedRAMscratchremnants afterward. This provesOScopyboundary only, notcorrecteduploader/CLI/nativeoperation. Evidence analysis/P7_static_startup_raw/file_limit_freeze.json,file_limit_first.json; independentreviewd38e2b84.

## F-171 - Static/default M0 run02 sampled stopped state (2026-09-25T04:44:51.069949+04:00)
Status: HARDWARE-OBSERVED, limited to D160 recorded samples. Source: analysis/P7_static_startup_raw/native_run02/result.json and its14 numbered original receipts, reviewed HEAD e852e2a5. One upload succeeded; full loader/sketch references matched before/after18 passive reads. Runtime epochs3/STOPPED/initfalse/faultNONE and finished IDLE transaction495us were unchanged across the two sampled intervals. Interpretation: no running progress observed; cause unknown pending source analysis. Sampled max790us is not R4 WCET, free RAM, physical acceptance or a human gate. Firmware sourcefcddbd8e remained unchanged; no other board hardware connected per user report.

## F-172 - Observed stopped-state nested fault records (2026-09-25T05:05:44.191981+04:00)
HARDWARE-OBSERVED within D161 sampled windows. Sourcefcddbd8e/static/default/M0 inherited from D160; sameboot6d4aca1b. Robot faults0x0110, MotorGateIO3, consumed token3 with invalid feedback; previous token2 invalid, duration546us. Exact752B/orderedwords and D160 prefix matches reviewed independentlyc323dc88. First failed native callback and timing unknown; zero stored duties are not measured pad voltages. See analysis/P7_stopped_diagnostic_validation.md and raw/parsed records. No physical/WCET/human acceptance.

## F171 - Inert MotorGate diagnostic host validation (2026-09-25T05:29:30.226819+04:00)
Observed local host only: 18 contract-derived cases/2570 assertions each normal and ASan/UBSan, three driver methods including refusal of three unsafe flag combinations, full existing22-target host matrix and65 compile-policy methods all pass. Source/freeze/review and exact commands are in analysis/P7_motor_fault_validation.md. Callback tracing retains first failure but adds timing overhead; it cannot identify the original D160 operation or prove native timing. No target compilation or run in this scope.

## F172 - Observed native macro collision and host correction (2026-09-25T05:53:05.273575+04:00)
D165 actual UNOQ/zephyr1.0.0 compiler reports generated autoconf.h:402 CONFIG_PWM=1 colliding with motor_fault.h:15. Compiler1/reaped/no timeout; all sevenfinalchecksPASS. Source receipt native_compile01/0116-checked-command/child.stdout; analysis/P7_motor_fault_compile_actual.md. D166 renames only enum identifiers and passes observed-macro syntax plus normal/sanitized regression; numericvalues unchanged. This is observed toolchain evidence and host correction, not a successful target recompile or physical measurement.

## F173 - Corrected diagnostic target compilation (2026-09-25T06:18:16.600243+04:00)
Observed on UNO Q ADB2629958581, boot6d4aca1b, CLI1.5.1/zephyr1.0.0: default/dynamic bench diagnostic M0/MATCH0 compiles successfully. Source5d3d126e and complete artifact identities are in analysis/P7_motor_fault_raw/compile02_verified.json; actual packet1edf4a08 and separate review32e1c119 reconcile all123 transports/ten children and seven final checks. Original CONFIG_PWM collision is resolved for this source. CLI reports29836B program/10432B globals, not measured loader/live RAM/WCET. Default grant remains false; no upload or active diagnostic result. See analysis/P7_motor_fault_compile02_actual.md.

## F174 - Explicit inert diagnostic activation host validation (2026-09-25T06:30:31.750945+04:00)
HOST-OBSERVED only: default0/explicit0/explicit1 selection, binary/inert/exclusive constraints, exact-byte sketch setup/loop with substituted Arduino/native headers, exact checked flag/property boundaries and17 other valid project controls pass13 independent methods.29 legacy tooling methods and normal/sanitized real diagnostic18cases/2570assertions each also pass. Source32b2d9d4/frozen84b3fbaf/revieweeb297fa; analysis/P7_fault_activation_validation.md contains command receipts. This is not a new target image or native callback/physical measurement.

## F175 - Explicit fresh staging host behavior (2026-09-25T06:46:21.730677+04:00)
HOST-OBSERVED only: D170source0160d1a6 and independent26methods pass on applicable WSL/Windows platforms, including actual Windowsjunction refusal;91existing tooling methods also pass. Source/test/review hashes and platform skips are recorded in analysis/P7_fresh_stage_validation.md. Retained D168104files/764049B preserve bytes and mtimes after validation. Explicit ownership refuses reuse and retains partial failures in controlled fixtures; no hostile concurrent-filesystem or target-build guarantee. No new board operation.

## F176 - Active inert diagnostic compilation (2026-09-25T07:06:20.297115+04:00)
TARGET-OBSERVED: exact MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1 diagnostic compiled with installed CLI1.5.1/zephyr1.0.0 on UNOQ ADB2629958581. Source8f592937/finalELFf9460a16; complete identities in analysis/P7_motor_fault_raw/active_verified.json, actual packet db1228ce and separate review41ecc2c9.123transports/tenchildren exit0, all sevenfinalchecksPASS. Compiler29836B program/10432B globals are not live RAM/loader/WCET or diagnostic execution evidence. D160 remains last upload. See analysis/P7_motor_fault_active_compile_actual.md.

## F177 - Exact active diagnostic ARM ABI (2026-09-25T07:19:13.636532+04:00)
FILE-OBSERVED on installed ZephyrSDK1.0.1 readelf2.43.1/GDB16.2: finalELFf9460a16 is ARM ELF32 little-endian REL; LOCAL diagnostic symbol0/2592B in section7 .bss2632B/alignment8. Debug7a4b2953 Runner2592/alignment8, traceReport44/mainReport2312, ten complete type layouts in analysis/P7_motor_fault_raw/active_abi.json SHA822c917d. Loader39d4a4fd confirms list0x200017bc,196B nodes,BSSindex3/base32/size92. Dynamic build/export ELF-ZSK bothb4416792. Evidence cc9f50c6/review60fdc78e; fivechildren0 and all146postchecksPASS. No live relocation, MCU state, runtime cause or physical acceptance observed. See analysis/P7_motor_fault_abi_validation.md.

## F178 - Offline diagnostic decoder host verification (2026-09-25T07:22:47.577059+04:00)
HOST-OBSERVED only: tools/motor_fault_decode.py source68653597/f6e2fd36 decodes the exact2592B D173 ARM layout, preserving64calls/fourreceipts/uint64tokens and partial/failure states.22independent literal-ABI tests PASS on firstexecution; sevenpins exact, reviewefe5a39ePASS. All208enum/367boolean/eightfloat positions exercised; DECODED does not establish capture origin/atomicity/runtime acceptance. See analysis/P7_motor_fault_decode_validation.md. No new firmware build or native operation.

## F179 - Diagnostic deployment file extents (2026-09-25T07:28:53.343450+04:00)
FILE-OBSERVED in one read-only ADB/Python query: raw motor_fault.ino.elf and build/export .elf-zsk.bin are each29836B, matching D172f9460a16/b4416792. Loader ELF2303728B/39d4a4fd and flash_sketch.cfg680B/38706cee unchanged. The pinned config writes sketch as binary at0x08100000; merely reading it did not execute its reset/flash commands. Raw64-byte headers/config and complete path/hash/size checks in analysis/P7_motor_fault_raw/deployment_files01/result.json SHA060834c06032ac28bcda615954383aba1492305fd5beab989c13e76f68e00ca9. All five closing file checks passed; boot6d4aca1b/UID1000. No child executable, MCU operation or new firmware copy.

## F180 - Finite diagnostic collector host verification (2026-09-25T07:55:04.381581+04:00)
HOST-OBSERVED only: capture_remote.py source7b7e8c69/95b0344d closed collect_motor_fault enforces flash-before-RAM, exact2632B/BSSalignment8 and two2592B snapshots with full relocation/flash brackets, max24reads/593424B.92focused methods PASS after firstrepair;14pins exact/review93ef66a7PASS.600s finalization and child-outcome/cleanup evidence regressions reproduced then fixed, original failures retained. No target capture/upload or hardware identity/acceptance implied; coherence UNPROVEN. See analysis/P7_motor_fault_capture_validation.md.

## F181 - Historical installed capture-module bytes (2026-09-25T10:52:53.764286+04:00)
FILE-OBSERVED before disconnection, 25Sep08:00Dubai: read-only installed_capture_modules02 observes p0_capture.py18880B/885c4e42,recorder_heap.py11002B/d6610249,runtime_capture.py28644B/a4d58b3c under /home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/. All three exact local hashes and independent closing reads matched; raw inputs/results/transport receipts retained. Initial installed_capture_modules01 found runtime_capture.py absent under the older app-default directory; original negative preserved. No child executable/MCU/flash. User now disconnected board; these historical bytes do not prove current state or installed bz2 availability.

## F182 - Inert action composition host validation (2026-09-25T11:08:31.211321+04:00)
HOST-OBSERVED only: source58d32dda/8ffb65c0 enforces bounded framing, strict receipt admission and conditional upload/capture callbacks. Unchanged46 original plus16 independent codec methods PASS on first tested-source repair;11pins exact, separate same-model reviewb1de6217 PASS. Windows Python3.13.11 compositions28,989/25,231 units fit30,000; WSL Python3.12.3 executes controlled fixtures only. No current board availability/API, actual upload/capture, native startup or gate is established. Original failures and full receipts are in analysis/P7_motor_fault_actions_validation.md.

## F183 - Offline capture failure retention ( 2026-09-25T12:46:14.434284+04:00 )
HOST-OBSERVED only: source3f73fd58/baca4d79 preserves primary CaptureError/cause/connection evidence and partial path across a secondary journal Exception, reports failed-save details and retains partial bytes without retry/publication.13independent+45selected existing Python checks PASS; normal journal byte equality and5task/11priorD177pins verified, separate same-model review7649fb58 PASS. Synthetic ENOSPC/serialization injection is not actual full-disk or hardware acceptance. See analysis/P7_dump_error_retention_validation.md.

## F184 - Fixed inert caller host qualification (2026-09-25T13:11:28.7376621+04:00)
HOST-OBSERVED only: source d8418fad/8b47b1d6 requires fresh committed scope/identity, local pins, single-use ownership, bounded11transport sequence and durable failure closure through existing primitives.44 independent methods PASS/no skips; original two fixture failures preserved and independently adjudicated. Windows Python3.13.11 actual-source command sizes28,990/25,232UTF16includingNUL; missing real scope returns1 before process/owner.24pins exact, separate same-model review dbd4c2e4 PASS. Controlled transport/Git/ADB fixtures are not native behavior, board identity/capabilities, runtime/WCET or acceptance. See analysis/P7_motor_fault_caller_validation.md. No real scope/owner/device call.

## F185 - Main-app setup binding host qualification (2026-09-25T13:28:16.015271+04:00)
HOST-OBSERVED only: source70b9cea5 maps explicit disabled config declarations to existing SetupGrants without inference; real public-type constexpr, invalid-range, existing Estimator and controlled actual-entry checks pass.16new+26existing selected methods PASS with no repairs/skips;10current/24priorD179pins exact, review30f3927f PASS. No Arduino/target/native execution or physical/current ownership evidence follows. Changed main-app target compilation remains pending. See analysis/P7_setup_binding_validation.md.

## F186 - Compiler failure evidence retention (2026-09-25T14:03:27.813702+04:00)
HOST-OBSERVED only: source0d73967b preserves compiler status/object/streams when either receipt write fails, attempts both independently and records diagnostic failures without replacing primary errors.27new+33existing methods PASS; separate fresh-context same-model review acafc242 PASS. Synthetic ENOSPC/console failure is not actual disk-full or target evidence. See analysis/P7_compile_error_retention_validation.md.

## F187 - Precompiled MATCH adapter host behavior (2026-09-25T14:11:57.344739+04:00)
HOST-OBSERVED only: source72950615 derives fixed dynamic/Immediate paths/argv, checks equal build/export packages, deep-copies bindings and reuses the unchanged uploader lifecycle.35 independent methods PASS, five exercise inherited lifecycle with controlled RAM fixtures; separate reviewcdbff1d5 PASS. No physical/source qualification or actual permission/target operation. See analysis/P7_match_upload_adapter_validation.md.

## F188 - Identified precompiled MATCH deployment host qualification (2026-09-25T14:34:30.259403+04:00)
HOST-OBSERVED only: caller69bb9981 and payload8a1c8523 (comment-only35e86452) enforce exact source/build/runtime/target/evidence bindings, one consumed attempt, UNKNOWN on unaccepted dispatch and independent closing checks through existing transport/uploader.66independent WSL and26Windows methods PASS, plus60unchanged compiler/parser checks; scoped fresh same-model review76fbc5ef PASS. Realistic source-aware composition29919ADB/29904SSH units fits30000 with81/96unit headroom; future requests are checked individually. Synthetic approvals/commands establish no actual permission or physical truth. Actual sourcehash37a2099f agrees Windows/WSL; current target compilation/native acceptance pending. See analysis/P7_match_deploy_validation.md.

## F189 - Fresh connected UNO Q admission (2026-09-25T15:57:57+04:00)
DEVICE-OBSERVED via four bounded ADB calls: serial2629958581 returns device; UID/GID1000 arduino, Linux6.16.7-g0dd6551ae96b/aarch64, Python3.13.5, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. Both exact CLI inventory programs return COLLECTED and timestamp-projected content matches retained baselines; bz2/Base85/-B checks PASS. First get-state exit0/device emitted ADB40-to41 local daemon restart text, causing a retained initial host assertion; subsequent three queries have no stderr. No MCU/native-tool operation, peripheral or physical acceptance observed. Source: analysis/P7_motor_fault_raw/admission_20260925_1552/.

## F190 - Actual isolated inert diagnostic ( 2026-09-25T16:13:06.920927+04:00 )
DEVICE-OBSERVED: D184 source8f592937/ELFf9460a16/packageb4416792 dynamic/default MATCH0/MOTORS_ALLOWED0 runs to COMPLETE. Four MotorGate feedback receipts are valid with EN-disabled intent/duties0;41 retained callbacks complete successfully and terminal inhibition is confirmed (STOPPED6). Both2592B raw snapshots are identical, hash8805ee82; coherenceUNPROVEN. Six observed settle callbacks130us do not establish WCET or physical output voltage. Separate actual review PASS; original D160/D161 full-app fault remains unresolved. Source: analysis/P7_motor_fault_run01_validation.md and referenced raw receipts.

## F191 - Current-app compile-only caller host qualification (2026-09-25T16:46:42.705781+04:00)
HOST-OBSERVED only: final calleraed3fbf4, controlled27+7methods PASS/exit0, durable6bf5c9c9/49823ae6. Separate reused-context same-model review94fff07d PASS. Bench/default and MATCH/Immediate source37a2099f manifest mappings checked,115pins each. No current target compilation, motor upload/run, RAM/WCET qualification or gate follows. Actual disk-full failures retained distinctly. Source: analysis/P7_current_app_compile_validation.md.

## F192 - Current bench/default target compilation (2026-09-25T16:55:17.532077+04:00)
DEVICE-OBSERVED compiler only: source37a2099f, build6d9e48f8b648469787bc8623ae05d163, default startup/MATCH0/MOTORS_ALLOWED0, one query/compile, exit0/all7closing checks PASS. Raw ELF72a8bfcd/package5b400268 exactly match D139; debugELFccc8990a differs. Existing same-loader allocation model still has592B deficit; compiler size output4296B local-variable allowance is not a loader/runtime proof. No upload/reset/native app execution or physical/human gate. Source: analysis/P7_current_app_compile_raw/bench01_binding/comparison.json.

## F193 - Current MATCH/Immediate target compilation (2026-09-25T17:03:54.198450+04:00)
DEVICE-OBSERVED compiler only: source37a2099f, build1fcc7d57d66848cd9ea604297538e125, Immediate startup/MATCH1/MOTORS_ALLOWED1 as compile flags only. One query/compile,21transports, exit0/all7closing checks PASS; exact canonical source reused without push. Raw ELFcb5fbb53/package004d51bf equal D138, debug2245bacd differs. Same-loader model remains conditional261280B peak/864B span/860B largest payload,62imports resolved; no dynamic loading/live memory/WCET/physical/human qualification. Source: analysis/P7_current_app_compile_raw/match01_binding/comparison.json.


## F194 - Inhibited full-app diagnostic host behavior (2026-09-25T17:32:14.102604+04:00)
HOST-VERIFIED only. D186 source539bfbb0/corrected independent oracle80eb359b: normal and ASan/UBSan each14cases/23885assertions;5driver methodsPASS. New staging Linux/Windows passes with explicit platform skips and actual Windows junctions. Existing Trace/Gate normal+sanitized each18cases/2570assertions; legacy tooling final67PASS/1platformskip. Separate same-model source/evidence reviewc41c6be1 PASS, eight pins/protected files verified. Source: analysis/P7_app_motor_fault_validation.md, P7_app_motor_fault_raw/ and reviews/P7_app_motor_fault_final_review.md. No target qualification, D160/D161 cause/fix, physical/RAM/WCET or human gate inference.
