# P0 bare-board QTR-style acquisition audit — 2026-09-23

Result: **source/binary-supported candidate, not adopted or measured**. The
installed UNO Q core supports finite GPIO mode/write/read operations on D2, D4,
D7 and D8, with no discovered active competing loader owner after setup under
the exclusions below. A separately labeled **DIAGNOSTIC-ONLY INPUT_PULLUP
stimulus** can exercise the real four-pin, all-polled-HIGH timeout path without
external components. It must use actual GPIO reads and an actual elapsed-time
deadline; it must not synthesize HIGH values, sleep past the deadline or replace
production high-impedance sensor acquisition with pull-ups.

The ordinary disconnected `INPUT` experiment remains distinct: no pull and no
sensor means the level may float, so all four pins timing out is **not guaranteed**.
Pull-up results would establish only sampled digital levels and diagnostic timing.
Neither experiment proves real QTR discharge, sensor freshness, electrical
compatibility, production HAL behavior or R4. SC-B remains open.

Scope: read-only Linux package files, offline packaged ELF inspection, repository
documents and versioned primary sources. No MCU debug connection, MCU memory or
peripheral read, upload, reset, pin operation, compilation or execution was done.
Only this report was added. No code/configuration/ledger changes or fact IDs.

## Context and authority

- Local clock readings were 2026-09-23 02:32:44 and 02:40:05 Dubai in this audit.
  This is PLAN section 3's Wednesday P0/P1 window, before its scope-cut dates.
- Read AGENTS.md, P0_recon_toolchain.md, PROGRESS.md, HARDWARE sections 1–3/5,
  FACTS F-080, D-051/D-052 and the installed GPIO contract. P0 task 0.4 explicitly
  requests a bare-board four-pin QTR-style timeout measurement. D-052 reports
  only UNO Q attached and authorizes eligible inert P0 work; it is not independent
  physical inspection, PINMAP OK or a human gate.
- This report recommends options under D-051. A material diagnostic contract
  still belongs in DECISIONS.md before implementation. No production behavior,
  pin assignment, wiring, B16 value or established locked test is changed here.
- B4.1 requires HIGH charge, high-impedance input, and per-pin discharge timing.
  SC-B in spec_conflicts.md:26 remains: the 10 + 1500 us acquisition exceeds the
  1000 us period and the under-800 us execution budget. P0 setup-only timing
  does not resolve acquisition cadence, sample age, stale-fault behavior or
  required physical five-minute WCET evidence.

## Installed identities

Abbreviations:

- `C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- `Z=C/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include`
- `DT=Z/generated/zephyr/devicetree_generated.h`
- `E=C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- `T=/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

The installed Zephyr revision is `1743741760ee5d2d58da50d504855d43f9f8e826`
(the GPIO report records generated version `v4.2.0-18364-g1743741760ee`).
Core source context is pinned to `79b3f1afdad455f55e4a25030953617152c0227c`.
Current audit re-read and hashed these installed files; SHA-256:

| File | SHA-256 |
|---|---|
| E | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.config | `a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba` |
| DT | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| C/cores/arduino/Arduino.h | `5f068c10a0aeb2f6d3cec1fa8b2a313b1f7374bcb77716f0b6cddba5bc198514` |
| C/cores/arduino/wiring_private.h | `b85c0bb1099e24301524fd7e1a76678873cb42bdb191ed747071ba05d82cd9c3` |
| C/cores/arduino/wiring_digital.cpp | `ff579a531d1fffffadb05a165f407e8b26d907edac6764f285c1c58632a4d27e` |
| C/cores/arduino/zephyrCommon.cpp | `7e2721a0840aa3f7a00171b8269feb17db029c2075973530733995a04dbfb12a` |
| C/cores/arduino/inlines.h | `1598991f2cf2fbaeb42c2a565f1fd3bd32bbd81eb7b056e998d3ffe162c98481` |
| C/cores/arduino/main.cpp | `d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed` |
| C/variants/arduino_uno_q_stm32u585xx/variant.h | `b684000848b9100b6781185045688dcc6701184fa3d43b12696f73747623d678` |
| C/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | `bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5` |
| Z/zephyr/drivers/gpio.h | `aab7888876f29b6ad98217d8099aac677f5238249b95599511038cc35d982316` |
| Z/zephyr/dt-bindings/gpio/gpio.h | `5c139f8079c86558733696564752064b70625126c48eabafb85f45426dde52be` |
| Z/zephyr/arch/arm/misc.h | `363c09953066f7470e394aeb295db5373ab100128551f105ed3fb61bab0cb05f` |
| Z/zephyr/sys/time_units.h | `daa79f7396d72d3a09a97251001b6803e606c98cf0550b22448e605e87cddda8` |

These identify the installed package, not a newly verified running loader/sketch.

## Exact pins, names and exports

Arduino.h:89–100 generates `D2`, `D4`, `D7`, `D8` as named enum constants with
their digital indices. They are not standalone preprocessor macros. Use these
names and compile-time assertions against diagnostic config values; do not use
variant.h's unrelated legacy SDA/SCL/SPI macros, which are placeholders equal 0.
`wiring_private.h:23–25` derives the actual port/pin table from DT.

| Proposal / named constant | Index | MCU pad | Overlay line | DT mapping lines | Device |
|---|---:|---|---:|---|---|
| QTR_FL / D2 | 2 | PB3 | 278 | 19188–19191 | GPIOB ordinal 90 |
| QTR_FR / D4 | 4 | PA12 | 280 | 19210–19213 | GPIOA ordinal 89 |
| QTR_RL / D7 | 7 | PB2 | 283 | 19243–19246 | GPIOB ordinal 90 |
| QTR_RR / D8 | 8 | PB4 | 284 | 19254–19257 | GPIOB ordinal 90 |

All four DT Arduino entries have flags 0 / ACTIVE_HIGH. The official connector
source independently agrees at lines23,25,28,29.
[Pinned connector](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/boards/arduino/uno_q/arduino_r3_connector.dtsi#L23)

DT:13609,13633,13638,13698 gives GPIOA ordinal 89, named `gpioa`, base
`0x42020000`, non-deferred. DT:13754,13777,13782,13842 gives GPIOB ordinal 90,
named `gpiob`, base `0x42020400`, non-deferred. Both have 16 pins with full
`port_pin_mask=65535` in E.

Offline E GDB checks:

| Device | Export address | Config / data | API / init |
|---|---|---|---|
| `__device_dts_ord_89` | `0x0801c064` | `0x0801de0c` / `0x20001740` | `0x0801c6e0` / `0x08006541` |
| `__device_dts_ord_90` | `0x0801c040` | `0x0801ddf8` / `0x20001730` | `0x0801c6e0` / `0x08006541` |

The matching `__llext_sym___device_dts_ord_89/90` have those **nonzero**
addresses. Named readiness queries are therefore source/export-supported:
`device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpioa)))` and the corresponding
`gpiob` query. The GPIO report already establishes their finite read-only
`z_impl_device_is_ready` path/export; neither query initializes a peripheral.

Both devices use the same `gpio_stm32_driver` as F-080. The candidate must
relocate through these device objects and inline header dispatch. F-080's
zero-valued exports for several `z_impl_gpio_*` wrappers are not callable
shortcuts. Its `port_get_direction` function pointer is also NULL despite the
enabled Kconfig feature; `CONFIG_GPIO_GET_CONFIG` is disabled. Do not add an
unsupported direction/config query to claim final-state verification.

## Ownership and exclusions

There is **no pad overlap** with proposed motor signals: D3/PB0, D5/PA11,
D6/PB1, D9/PB8 and MOTOR_EN D10/PB9 (overlay:279,281,282,285,286). However,
the shared GPIO ports have register read/modify/write operations, and PWM3 has
both D8 and proposed motor pads in its Arduino pinctrl state. Therefore the
diagnostic must not initialize PWM/tone/Servo/CAN or any competing pin owner.
No motor operation or write to a motor pin is needed or authorized by this audit.

| Potential owner | Installed evidence and implication |
|---|---|
| Console / Serial1 | DT chosen console is USART1 (:37803), pinctrl PB6/PB7 (:11295–11298); no QTR-pad overlap. It is not deferred, unlike other UARTs. |
| Router / internal UART | Overlay:390–391 and DT:12020–12029 give LPUART1 PG7/PG8 plus PG6/PG5 control; no overlap. Candidate must not start Bridge/Monitor/Serial2. |
| Header extra UART / I2C | USART3 PB10/PB11; I2C2 PB10/PB11, I2C3 PC0/PC1, I2C4 PD12/PD13 (alternate PF14/PF15). No QTR-pad overlap; relevant bus devices deferred in overlay. |
| SPI | SPI2 PB13/PB14/PB15/PB9; SPI3 PG9/PG10/PB5/PG12 (DT:12718–12727,13431–13440). No QTR-pad overlap; deferred in overlay:221–246. |
| PWM2 / PWM3 / PWM8 | PB3, PB4, PB2 respectively. Overlay:124–144,190–196 gives deferred init, empty default/sleep states; Arduino states contain these pins. DT ordinals 100/105/123 confirm deferred 1 and empty states; E device flags 1 agrees. No `analogWrite`, tone, Servo or explicit device/pinctrl init in the candidate. |
| CAN1 | PA12 TX and PA11 RX, overlay:235–241. DT ordinal 61/deferred 1 at:9283,9545; E flags 1. Merely being the chosen CAN bus does not initialize it. Do not begin CAN or call its init/pinctrl functions. |
| MCU USB | PA12 is USB DP, but DT OTGFS status is disabled (:26160); both USB device stacks disabled (config:1702–1703). Core SerialUSB startup is conditional and no `cdc_acm_serial` property is configured. Linux's USB/ADB attachment is not this disabled MCU USB pad owner. |
| SWJ / JTAG / SWO | DT default SWJ pinctrl includes PB3 JTDO/SWO and PB4 NJTRST (:7876–7879), as well as PA13 SWDIO and PA14 SWCLK (:7867–7870). These alternate functions must not be confused with an active periodic owner. See next paragraph. |
| Loader / LEDs / other control | Loader GPIOs use PG13/PG15 for Linux-ready/USB-mode, PA2 for VREF switch, and GPIOF for matrix. Normal animation stops before setup. RGB is GPIOH; the extra system-utilities GPIO service is VENTUNO-only. None is one of the four QTR pads. |

SWJ is a meaningful initial-mode caveat. Pinned `pm_debug_swj.c` describes
reset/default debug pins and an optional startup transition to analog mode.
`soc/st/stm32/common/CMakeLists.txt:13–15` includes it only when **PM enabled
and DEBUG disabled**. Installed PM is disabled (:114), so E has no
`swj_to_analog`, `swj_pcfg` or associated init symbol. SWO logging is disabled
(:1564), as are tracing (:1701) and DWT use (:462). No software task that
repeatedly reclaims PB3/PB4 was found. Explicit GPIO configuration writes their
MODER to GPIO input/output and therefore must precede observations; do not
infer an initial neutral input state. The existing passive-capture configuration
selects SWD, whose DT pads are PA13/PA14, rather than JTAG/SWO on PB3/PB4.
This is configuration evidence, not an inspection of a currently attached
debugger or live mode registers.
[Pinned SWJ inclusion](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/soc/st/stm32/common/CMakeLists.txt#L13),
[SWJ startup source](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/soc/st/stm32/common/pm_debug_swj.c#L16)

Core main.cpp:19–24 supplies empty weak initVariant/loopHook defaults but starts
static threads before setup (:31–37). A linked library can override these.
Thus exclusive candidate ownership remains a final-image prerequisite: inspect
its constructors, static threads, initVariant, hooks and imported calls. This
audit is not blanket approval of an unbuilt sketch or arbitrary loaded library.

## Mode changes and GPIO boundedness

`wiring_digital.cpp:19–44` supports:

- `OUTPUT`: `GPIO_OUTPUT_LOW | GPIO_ACTIVE_HIGH` — **LOW first**, not HIGH.
  Each charge operation must subsequently call `digitalWrite(HIGH)`.
- `INPUT`: `GPIO_INPUT | GPIO_ACTIVE_HIGH`, with no pull flags.
- `INPUT_PULLUP`: `GPIO_INPUT | GPIO_PULL_UP | GPIO_ACTIVE_HIGH`.

Installed GPIO header values are INPUT=BIT16, PULL_UP=BIT4, PULL_DOWN=BIT5,
ACTIVE_HIGH=0. `gpio_pin_configure_dt` (:1066–1071) ORs the flags 0 Arduino
entry into these flags. E's input branch in `gpio_stm32_config`
`0x080191e0–0x080191f8` selects neutral input or input/pull-up without output
drive; the common pad routine at `0x080178bc–0x080179c4` updates PUPDR and
MODER using finite masked register writes. In particular, INPUT after
INPUT_PULLUP **clears the pull setting**; a previous HIGH output latch does
not turn neutral INPUT into an Arduino AVR-style retained pull-up.

E driver function pointers are configure `0x08019151`, raw read
`0x080190bd`, set bits `0x080190db`, clear bits `0x080190e5`. The configure
body has finite branches and a finite pad-config call; read uses IDR, set uses
BSRR, clear uses BRR. No lock, allocation, polling, sleeping or device-init
wait was found in these selected GPIO paths. PM_DEVICE is disabled (:102).
This is an instruction-path result, not a wall-clock upper bound under all
interrupt/scheduler/bus conditions.

Arduino wrappers discard configure/write status and return LOW for a native
negative read error. Readiness checks plus expected readbacks detect some
failures, but do not recover discarded status. Final INPUT must be attempted
on **all four pins** on every post-configuration exit. A checked native
restoration adapter is an option if its contract/export dispatch is separately
reviewed; otherwise report only source-proven restoration calls, not measured
mode verification. A floating final read is not expected to be LOW and cannot
prove that its pull-up was cleared.

## Clock and 10 us charge caveat

The installed core uses the 64-bit timer path: zephyrCommon.cpp:17–22 calls
`k_cyc_to_us_floor32(k_cycle_get_64())`; config:79 is 160 MHz and :1124/:1131
enable the 64-bit SysTick cycle counter. `arch/arm/misc.h:29–34` calls
`sys_clock_cycle_get_64`. Its nonzero E export is Thumb `0x080103d5`.
`time_units.h:1334–1335` supplies the truncating uint32 microsecond conversion.
`micros()` therefore has integer-us quantization and wraps modulo2^32 us;
short durations should use unsigned subtraction with an explicit valid span.

Offline E `sys_clock_cycle_get_64` at `0x080103d4–0x08010400` masks/restores
BASEPRI around `elapsed()` and the 64-bit cycle accumulator. `elapsed` at
`0x08010194–0x080101cc` uses a finite set of SysTick reads and rollover state
updates; no retry loop. The apparent generic source spinlock compiles to
single-core interrupt masking here, not a wait for another CPU.

**`delayMicroseconds(10)` is not source proof of a ten-microsecond minimum.**
Installed inlines.h:20–24 calls `k_busy_wait(us - 1)` for nonzero arguments.
The nonzero loader export `z_impl_k_busy_wait` is Thumb `0x08019e11`.
Its E body at `0x08019e10–0x08019e2a` computes 160 cycles/us and polls unsigned
cycle elapsed until the threshold. For an argument 10 at the Arduino API,
that threshold is 1440 cycles / 9 us, plus call/poll/return overhead. The actual
HIGH interval also contains sequential pin operations. Retain measured charge
and release spans; do not assert a >=10 us physical pulse from the function name.

Busy-wait termination and a microsecond deadline assume a functioning clock
and continued execution. Unlike the GPIO calls, this is a time-conditioned
poll loop, not a fixed instruction-count bound under stopped clock/starvation.
Keep interrupts enabled during the acquisition; do not wrap 1500 us in a global
interrupt mask. A finite diagnostic poll-count guard can expose an incomplete
timeout if the outer clock fails, but cannot turn the nested busy-wait into a
whole-call hard deadline. If a strict charge minimum is selected, specify and
test a conservative measured elapsed-time guard (including quantization) as a
new diagnostic contract, without silently tuning QTR_CHARGE_US.
[Pinned timer implementation](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/timer/cortex_m_systick.c#L553),
[busy-wait implementation](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/kernel/busy_wait.c#L93)

## Measurement options and recommendation

| Option | Meaning | Recommendation |
|---|---|---|
| Charge then neutral INPUT, nothing connected | Authentic GPIO mode sequence but bare pad capacitance/leakage/noise replaces the sensor. May discharge early or remain HIGH. | Retain as separately labeled neutral observation. Record actual per-pin first-LOW/timeout masks; no guaranteed timeout assertion. |
| Charge then INPUT_PULLUP, nothing connected | Known internal bias provides a HIGH stimulus. Actual repeated digitalRead calls can exercise all four unresolved inputs until the real 1500 us deadline. | Feasible diagnostic-only companion, conditional on observed HIGH reads; clean up all four to INPUT/no pull. |
| Replace reads with HIGH, omit reads, or merely wait 1500 us | Does not exercise the GPIO polling timeout path. | Not an acceptable substitute for P0's requested timing evidence. |
| Require external resistors/sensors | Can test different electrical conditions but violates the currently requested bare-board scope. | Do not request additional hardware for this P0 candidate. |

Pololu's procedure requires a HIGH charge lasting at least 10 us and then
high-impedance input. An internal pull-up changes that electrical experiment,
so its timeouts must never be presented as real QTR data or a production fix.
[Manufacturer QTR-1RC procedure](https://www.pololu.com/product/959)

Recommended next action is one new, reviewed **setup-only** contract with finite
sample count, frozen RAM and an empty loop, using the existing default startup
and MOTORS_ALLOWED 0 constraints. Define before implementation:

1. The exact named pins and readiness checks for both ports; explicit neutral
   and pull-up dataset labels; exclusion of motor/peripheral owners above.
2. Charge sequencing after the last HIGH write, separate charge/release/observe
   spans, the timeout epoch and sequential-release skew. For an all-four-HIGH
   stimulus intended to last a full 1500 us, starting its observation epoch after
   all input transitions makes that intent unambiguous; record preceding release
   overhead separately. This diagnostic convention does not select production
   timestamp/freshness semantics.
3. Actual per-pin polling. Preserve poll count, observed LOW mask, first-LOW
   times, final timeout mask, elapsed durations and explicit completion status.
   A valid stimulated timeout requires all four pins unresolved/HIGH in every
   performed poll and measured observation >=1500 us; an early LOW is retained
   as a failed stimulus/early observation, never overwritten with 1500.
4. Distinguish deadline exit from all-resolved exit and any finite guard/fault
   exit. Record raw total acquisition cost and adjacent-micros overhead without
   subtraction. One micros timestamp for all four reads has polling skew; record
   the convention. Sampled HIGH does not establish continuous analog HIGH
   between polls or a calibrated voltage.
5. INPUT/no-pull cleanup of all four pins, including early exits, before complete
   is published. Cleanup result semantics must reflect the wrapper's error
   masking. Do not require LOW on floating restored inputs.
6. Independent host tests for actual read ordering/count, mixed/early/all-timeout
   inputs, exact deadline ties, wrap, no-progress/fault guards, mode separation,
   cleanup on failure and incomplete-record rejection. They validate code paths,
   not actual pads or the clock.
7. Fresh source and exact target-ELF reviews, device/clock relocations, constructors
   and hooks, exact inert manifests and default-only upload checks before any run.
   Then use separately reviewed passive frozen-RAM capture with exact deployed
   identities and explicit debug-overlap limits. This audit authorizes no capture
   invocation and did not alter any uploader/readout allowlist.

Even a successful result measures an approximately 1.5 ms-plus diagnostic path,
not compliance with a 1 ms control schedule. Actual sensor response, physical
initial/final state, board isolation, load/interrupt WCET, async acquisition and
sample freshness remain unverified. Original human gates and PINMAP OK remain
absent; no later phase authority follows.

## Reproduction and source hashes

Read-only transport used `tools.board_tool.remote('2629958581',
['python3','-c',PROGRAM],capture=True,timeout=40)` with `SUMO_TRANSPORT=adb`,
`SUMO_ADB_SERIAL=2629958581`, and
`SUMO_ADB_EXECUTABLE=C:\Users\narut\AppData\Local\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe`.
PROGRAM used pathlib reads/SHA-256 and subprocess offline commands only:

- `Tnm -n E`, filtered symbols and init entries: exit 0.
- `Tgdb -nx -nh -batch E -ex 'p SYMBOL'` for device89/90, configA/B,
  gpio_stm32_driver, LLEXT device/clock exports and deferred CAN/PWM objects:
  exit 0. No `target`, `monitor`, connection or hardware operation.
- `Tobjdump -d [-l] --disassemble=FUNCTION E` for configure/pad routines,
  sys_clock_cycle_get32/64, elapsed, busy_wait and timer init: exit 0.
- Numbered source/DT/header reads and versioned GitHub/raw source reads completed.
  An exploratory local P0_bootstrap.md lookup and wildcard rg spelling failed;
  correct P0_recon_toolchain.md and explicit/glob-aware searches were then read.
  A remote read batch assumed nonexistent SerialUSB.cpp and exited 1; the corrected
  read found only SerialUSB.h and succeeded. No mutation occurred. Two guessed
  upstream filenames returned 404; directory listing found arduino_uno_q.dts and
  pm_debug_swj.c, then pinned reads succeeded. Web's first guessed DTS open also
  failed; no conclusion relies on those failed lookups.

Additional current installed hashes: `SerialUSB.h`
`4013a46af977f1d13b32c0a02e213343f592f3cbeaff6ee4be6ea3695e698350`;
`zephyrSerial.h` `40f88d2c2bb25f703acbac10d195167611ea2d8156fb7a02348044aef0ec24e6`.

Pinned upstream SHA-256, read from the exact revisions identified above:

| Source | SHA-256 |
|---|---|
| boards/arduino/uno_q/arduino_r3_connector.dtsi | `3dfba6e94a420edb9391285dcb601bb0e3a2cb14f3ee0eb8bbc5ed63f0236be3` |
| boards/arduino/uno_q/arduino_uno_q-common.dtsi | `3f8cc524d1e2c6f9ca460c2d5f7f9579c0e826e2b257498f46a717fd24810745` |
| boards/arduino/uno_q/arduino_uno_q.dts | `48e419675043511f4963894e58e85ce9755d0562f616e7766fd3021cc604258a` |
| soc/st/stm32/common/CMakeLists.txt | `5487584d756b0740ebf4fc2dee207993c43084547b264086704b9c2e45da2e42` |
| soc/st/stm32/common/pm_debug_swj.c | `7bd3b849829658a061aafe6adee80c28c91d630688acd1429bb23ed61c687fe2` |
| soc/st/stm32/common/gpioport_mgr.c | `9807c1b0501f4fe7a41ead122a205417840be38a1e2d8da34aeb05c9606331b1` |
| drivers/timer/cortex_m_systick.c | `b1650fac1fb760d1857324481437988458340a232d6df1a3aa4fe8085ca6b4a7` |
| kernel/busy_wait.c | `a9108a9265f7a6e6af6f81feddcca66c59df327d8f31b54e5d960a81cfc347a5` |
| ArduinoCore-zephyr loader/main.c | `0b2af678b67a21a10f211538f5c535f0f92fb3ddbf97a302ed22122665f916b8` |
| ArduinoCore-zephyr loader/fixups.c | `45c3152b26fe6385ddc5eee606ff1307999bc743ab22f9ed521f4ae59499d0a4` |
