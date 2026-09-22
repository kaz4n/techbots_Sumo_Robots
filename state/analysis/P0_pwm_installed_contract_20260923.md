# P0 installed PWM contract audit — 2026-09-23

Result: **installed source/device/API facts verified; explicit-period target
probe not yet compiled in this audit; output behavior unmeasured.** The next
eligible check is a retained, never-called compile-only PWM API probe with all
specification, pinctrl index and timing values supplied as arguments. No motor
pin, carrier frequency, production HAL or runtime sequence is adopted here.

The installed analogWrite path defaults to8-bit software input and reuses500Hz
DT periods. It can fall back to digital HIGH when PWM mapping/readiness fails,
and discards pinctrl and PWM-write status. Native pwm_set_dt supports an explicit
period and returns status, but initialization, routing, readiness, timer sharing
and actual linked imports must be checked separately. A successful native call
does not establish MotorGate safety or a measured waveform.

Scope: read-only Linux installed files, offline packaged ELF and pinned primary
source. **No live PWM/GPIO write, MCU/debug operation, upload, reset, installation
or runtime probe occurred.** Only this report and its task-specific raw receipt
were written. No shared ledger/configuration edits or commit.

## Context and evidence identity

Read the complete AGENTS.md, P0_G2.md, current PROGRESS, relevant FACTS
F-019/F-027/F-028 and proposed HARDWARE motor pins. Local date was Wednesday
2026-09-23, PLAN section3's P0/P1 window. The source-count/manual PWM discrepancy
and human PINMAP status are preserved. D-051 engineering delegation permits
bounded source/build choices but supplies no motor-run permission or gate.

Abbreviations:

- C = `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- H = `C/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include`
- DT = `H/generated/zephyr/devicetree_generated.h`
- E = `C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- T = `/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

Installed source is authoritative. The already established package version
header names kernel4.4.2-rc1/build v4.2.0-18364-g1743741760ee; driver source
interpretation below uses full revision1743741760ee5d2d58da50d504855d43f9f8e826
and is cross-checked against E, not assumed from a mutable branch name.

| File | SHA-256 |
|---|---|
| E, 2303728 bytes | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.config | `a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba` |
| C/cores/arduino/wiring_analog.cpp | `32d805872068e175b03cc291d3697f3ea7443501424dd870165d0bebeddd6c98` |
| C/cores/arduino/zephyrPinctrl.cpp | `f48670ba733b9a1a3de8fe6ee903009f48b1f3d4da6b05521daffd93a88c51b9` |
| C/cores/arduino/zephyrPinctrl.h | `f2c7bd8cacb563ebc89881c9771ad226eadee52419b4fc8c36895a332368183b` |
| C/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | `bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5` |
| DT | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| H/zephyr/drivers/pwm.h | `e029bddf7a2bf912cf7b375967cf7c7f74c2307297bf9aa4a3dc85260ff18da5` |
| H/generated/zephyr/syscalls/pwm.h | `1b0f9a20a506c33be9cca2548e1eaa530029eab79f730a656e0e6c41838120bd` |
| Pinned Zephyr drivers/pwm/pwm_stm32.c | `f86792a749312ee29e9ce6c10444760df666d787b9f248b291a63da603e236d1` |

The reproducible raw receipt is
[P0_pwm_installed_raw_20260923.txt](P0_pwm_installed_raw_20260923.txt).
It is83280 bytes, SHA-256
`e50cedcc257c7bc00315c207ddd6b010b250375ad24cbb6a92347532cf725f1e`.
It includes exact offline GDB argument arrays and zero exit statuses, device/API
values, full native get/set/init disassemblies, source hashes, installed header
excerpts and selected pinned-driver source ranges. No memory target was attached.
Source line numbers below are conventional file lines, not web-extractor lines.

## Arduino API: resolution, fallback and discarded errors

Installed wiring_analog.cpp:97 defaults resolution to8. Setter:107–109 clamps
bits to1..31; getter:111–113 returns that software setting. Setter declaration
is Arduino.h:149; C++ getter is overloads.h:24. The setter changes the common
software input interpretation, not a timer's prescaler or carrier frequency.
No analogWriteFrequency declaration was found in the searched installed core
or variant headers.

For the PWM overload at wiring_analog.cpp:118–147:

1. It finds the pin in the DT-generated PWM mapping. If absent, it calls
   pinMode(OUTPUT), then writes HIGH if value>(maxInput>>1), otherwise LOW.
2. If mapped, it calls init_dev_apply_channel_pinctrl but ignores that status.
3. If the device remains unready, it takes the same digital fallback. At the
   default8-bit setting, value>=128 produces HIGH; this is not PWM duty control.
4. Only the ready-PWM path clamps value into0..maxInput, maps it with64-bit
   arithmetic to0..spec.period, and calls pwm_set_pulse_dt. Its status is ignored.

Thus a failed routing operation can be hidden even if device readiness succeeds.
Native setter failure has no defined fail-closed action in this wrapper and may
leave earlier output state. Increasing input bits does not increase hardware
resolution. The device's current period is not queried: pwm_set_pulse_dt uses
the DT period on every call. A subsequent analogWrite can restore500Hz after
an explicit-frequency native write, and shared-timer effects can reach another
channel. None of these functions is a later MotorGate substitute.

The installed observations corroborate the corresponding
[pinned Arduino analog source](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/cores/arduino/wiring_analog.cpp#L96).
This audit does not assume other uninspected files in that public tree exactly
match the installed package.

## Actual DT mappings and shared devices

The following table verifies existing proposals as software mappings; it neither
adopts them in the new probe nor supplies PINMAP OK. Overlay:366–373,400–407 and
the exact DT fields in the raw receipt agree. All listed specs have normal
polarity flags0 and period2000000ns, i.e.500Hz.

| Proposed signal/pin | Pad | DT pwms index | Device/channel | ARDUINO pinctrl index |
|---|---|---:|---|---:|
| L_FWD D3 | PB0 | 1 | pwm3/TIM3 CH3 | 0 |
| L_REV D5 | PA11 | 2 | pwm1/TIM1 CH4 | 0 |
| R_FWD D6 | PB1 | 3 | pwm3/TIM3 CH4 | 1 |
| R_REV D9 | PB8 | 6 | pwm4/TIM4 CH3 | 0 |

Pinctrl index is the position within that device's ARDUINO state, not channel-1,
the global PWM index or Arduino pin number. zephyrPinctrl.h:21–33's helper
computes the number of preceding specs using the same device.

| Device | DT ordinal / native export | Timer base | Prescaler | Native data |
|---|---|---|---:|---|
| pwm1 | 120 / 0x0801c3c4 | 0x40012c00 | 63 | 0x200002cc |
| pwm3 | 105 / 0x0801c37c | 0x40000400 | 4 | 0x200002b4 |
| pwm4 | 109 / 0x0801c358 | 0x40000800 | 4 | 0x200002a8 |

All three native objects have deferred flag1, shared API0x0801c720, init
Thumb0x0800e1c5 and NULL deinit. Their counter mode is0 (up), deadtime0 and
mastermode0. DT ordinal lines are18292/15931/16587; prescalers additionally
appear in overlay:105,136,150 and actual native config objects. Native config
addresses are0x0801e6c8/0x0801e5f8/0x0801e598 respectively.

Their default/sleep pinctrl states are empty; ARDUINO state id2 has4/3/2 pins.
For TIM3 the exact ARDUINO pin sequence is PB0, PB1, PB4, confirmed by DT
16066–16074 and native pinmux514/546/642. Applying the whole ARDUINO group
would also claim the QTR D8/PB4 pad. The one-channel helper applies one indexed
pin. It is not correct to route a whole group just because one PWM channel is
needed. TIM4's second group pad is PB9/D10, the proposed enable signal; TIM1's
other group pads include header SPI pins. No such group routing is performed here.

The broader installed source maps13 header PWM entries plus3 LED entries; the
advertised six-pin distinction remains as documented in G1. This audit does not
change pin assignments to resolve that documentation discrepancy. PWM2/5/8 are
also deferred, but their extra channels are not proposed probe settings.

## Public explicit-period API and routing contract

Installed headers provide these calls:

| Call | Return / relevant installed source |
|---|---|
| zephyr::arduino::init_dev_apply_channel_pinctrl(dev,index) | int; zephyrPinctrl.h:14, .cpp:123–167 |
| pwm_is_ready_dt(spec) | bool; pwm.h:1139–1142 -> device_is_ready |
| pwm_get_cycles_per_sec(dev,channel,&cycles) | int; pwm.h:640–650 |
| pwm_set_dt(spec,period_ns,pulse_ns) | int; pwm.h:715–719 |
| pwm_set(dev,channel,period_ns,pulse_ns,flags) | int; pwm.h:669–694 |
| pwm_set_cycles(dev,channel,period_cycles,pulse_cycles,flags) | int; pwm.h:615–627 |

pwm_set_dt uses spec.device/channel/flags and the explicit period argument,
ignoring spec.period. In contrast pwm_set_pulse_dt:736–740 reuses spec.period.
The period inputs100000ns and50000ns represent10kHz and20kHz respectively;
these are arithmetic examples, not selected runtime constants.

pwm_set first obtains the cycle rate, computes floor(ns*cycles_per_sec/1e9)
for period and pulse, rejects results beyond UINT32_MAX, then calls
pwm_set_cycles. The latter rejects pulse_cycles>period_cycles before dispatch.
Nanosecond values can quantize to equal cycles or zero. Native period_cycles0
disables the selected channel; it is different from a positive period with
zero pulse. These helpers do not initialize the device, route its pads or
verify readiness. They also do not validate arbitrary caller pointers.

The channel routing helper returns-EINVAL for NULL device, calls device_init
if unready and propagates a negative init result, looks up ARDUINO state,
bounds-checks index and configures exactly one pin. It returns0 when the device
has no entry in its generated map, so generic helper success plus readiness
does not independently prove routing for an arbitrary device. For the specific
installed PWM devices above, map/state/pin correspondence is source-supported.
Even a bad index is checked only after possible device initialization, so this
API is a hardware action if executed; the compile-only probe must never call it
from setup, loop or constructors.

device_init is not merely a read-only readiness operation. Actual native PWM
init enables/configures clocks, obtains timer clock rate, toggles timer reset,
applies default pinctrl, sets prescaler/ARR0, enables the counter and, for advanced
timers, all outputs. The driver's reset-toggle result is discarded, whereas
clock/rate/pinctrl failures are returned. Reinitialization and timer reset are
not isolated per-channel actions. No live readiness or init result was sampled.

## Exact exports and native runtime limits

The installed config enables CONFIG_PWM/CONFIG_PWM_STM32
(:1031,1049), disables PWM_CAPTURE/PWM_EVENT (:1040–1041), and disables PM
and PM_DEVICE (:114,102). The actual8-byte driver API contains:

| Field/export | Exact value |
|---|---|
| pwm_stm32_driver_api.set_cycles | Thumb0x0800de4d |
| pwm_stm32_driver_api.get_cycles_per_sec | Thumb0x080196d7 |
| __llext_sym_z_impl_pwm_set_cycles | **0** |
| __llext_sym_z_impl_pwm_get_cycles_per_sec | **0** |
| __llext_sym_z_impl_device_init | Thumb0x08019e5d |
| __llext_sym_z_impl_device_is_ready | Thumb0x08019e6f |
| __llext_sym_pinctrl_configure_pins | Thumb0x08019637 |

The named PWM syscall exports are zero-valued weak placeholders, despite a
nonzero native driver. Installed pwm.h supplies local inline vtable dispatch,
so a target may link usable local wrapper bodies without calling those zero
exports. That must be established from the **actual final probe ELF's imports,
relocations and disassembly**, not inferred from an exit0 link. A retained call
through a zero-valued import is not runtime compatibility. No PWM capture/event
facility is established by the generated header declarations alone.

Native get_cycles_per_sec0x080196d6–0x080196ea performs
`tim_clk / (prescaler + 1)`, stores a64-bit result and returns0. It ignores the
channel argument and has no readiness test. The packaged file's cached tim_clk
is initially0 for all inspected PWM devices; init populates it from the clock
driver. This file initializer is not a live rate reading. A future checked path
must reject an unusable zero rate and cannot treat this call's0 status as
validation of a channel or initialized device.

The source/native setter behavior has the following material limits:

- Buildwide channel check is1..6 (native0x0800de5a–0x0800de66). This is not a
  per-timer proof that every accepted number has a routed physical output.
- Non32-bit timers reject period_cycles>65536. The driver also rejects an
  unsupported complementary-output request or unsupported counter mode.
  Pulse<=period is checked by the public wrapper, not independently by the
  native setter. Calling its address directly would bypass that check.
- At zero period the setter clears the selected enable bit
  (0x0800df0a–0x0800df16). With positive period and installed up-counting,
  it uses ARR=period_cycles-1, writes channel compare, and **writes shared ARR**
  at0x0800df74. Every enabled channel on the same timer shares the period;
  D3 and D6 therefore cannot have independent frequencies.
- On first enable, it configures PWM1 mode/idle state, enables channel and
  preload, and generates UPDATE at0x0800e04c–0x0800e052. This update affects
  the shared timer. The code does not provide an atomic multi-channel group
  update, an inter-channel reversal protocol or automatic MotorGate protection.
- The selected valid setter path is finite register work plus a fixed compare
  function call. No semaphore/service wait appears in this setter. Error paths
  can call logging; initialization has separate clock/reset dependencies. This
  is not a measured execution bound, electrical-glitch proof or R4 acceptance.

The [pinned STM32 driver](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/pwm/pwm_stm32.c#L252)
at raw lines252–354/649–773 explains the matching native code; full function
receipts preserve the exact installed implementation. Generic header statements
about PWM update behavior do not establish simultaneous updates across separate
timers or validate the bridge's physical0/full-duty/reversal behavior.

Effective cycle counts remain conditional on the initialized timer clock:
`C = floor(f_timer/(prescaler+1))`,
`N = floor(period_ns*C/1e9)` and `P = floor(pulse_ns*C/1e9)`.
For up-counting, the intended period uses N counts and compare P; duty granularity
depends on N, not the software resolution setting. The CPU160MHz configuration
alone is not a measured timer cycle rate. No particular effective duty-bit count
or frequency accuracy is asserted here.

## Minimal compile-only probe recommendation

Recommended includes are Arduino.h, zephyrPinctrl.h and zephyr/drivers/pwm.h.
One suitable public signature, subject to the coordinator's recorded contract,
is:

```cpp
int pwmCompileProbe(const pwm_dt_spec* spec, size_t arduino_state_pin_index,
                    uint32_t period_ns, uint32_t pulse_ns,
                    uint64_t* cycles_per_sec);
```

The retained function can check arguments, invoke the checked channel-init helper,
check pwm_is_ready_dt, obtain and validate cycle rate, and call pwm_set_dt with
the supplied period/pulse while preserving each status. Such code exists to
compile/link the exact public path; it is **never invoked**. No constant device,
GPIO assignment or carrier frequency is needed. The coordinator owns precise
argument-error semantics and tests; this recommendation does not silently add
them to a production driver.

If Arduino compatibility is also required, use a separate retained never-called
function with pin_size_t pin, int bits and int value arguments that references
analogWriteResolution(bits), its getter and analogWrite(pin,value). Keeping it
separate expresses the API distinction and avoids suggesting a mixed native/
Arduino runtime sequence. No global device construction or runtime callback
registration is necessary for these C-style/core API probes.

As with the established compile-only IMU pattern, setup should only publish
probe addresses in externally visible volatile function-pointer anchors; loop
remains empty. Source used/noinline alone is not evidence against linker GC.
Final audit must verify retained code, checked dependencies, local PWM wrapper
dispatch, no zero-valued executed imports, constructors, and setup/loop that
never call the probes. Keep the sketch rejected by upload tooling and outside
the inert upload allowlist. MOTORS_ALLOWED0 is an extra compile assertion, not
a substitute for that nonexecution boundary when code contains PWM APIs.

A pass proves retained target API/link compatibility only. Later authorized
runtime work must validate actual chosen device/index/channel, initialized
cycle rate, all statuses, equal periods on shared timers,0/full-duty behavior,
frequency/duty accuracy, update/reversal transients and complete tick cost.
Motor writes still belong solely to MotorGate and need the existing specific
run authorization. None is requested or supplied by this source audit.

## Reproduction and remaining unknowns

Read-only transport was tools.board_tool.remote via ADB serial2629958581,
SUMO_TRANSPORT=adb and the installed Windows adb32.0.0 executable. Remote
Python used pathlib/hashlib and subprocess T gdb with `-nx -nh -batch E` and
only p/disassemble commands. All preserved remote/offline commands report
exit0 with empty stderr. Pinned public bytes were read via HTTPS and hashed;
no build, installation, target connection or device execution occurred.

Unknown/unmeasured in this source audit: final probe import selection; actual
live PWM readiness/clock rates; physical pin/wiring approval; waveform and
timer-interaction transients; output after error; motion behavior; MotorGate
implementation and R4 timing. The controller can expose an API without those
properties being qualified. No PINMAP OK, STAND OK, RING OK or human phase gate
follows from the report. Next action is the coordinator's bounded compile-only
contract/probe, with no board output operation.

Closing checkpoint: while this source audit was being written, the coordinator
implemented D-067 separately. The subsequently read
`P0_pwm_irq_compile_target_20260923.txt` records exit0 for source
`6578e07a23cc7209f127fa88c3defc8bad822818acea57097ce906053e7dc6bc`,80248 program
bytes/34048 global bytes, MATCH0/MOTORS_ALLOWED0/default, compile-only with no
upload. That receipt resolves target compilation as a separate result; this
report has not reviewed the probe's final binary or issued that later review.
The proposed signature above is historical source-audit guidance; the committed
D-067 public contract governs the implemented probe. Fresh combined source and
binary review is the next coordinator step, with all runtime limits preserved.
