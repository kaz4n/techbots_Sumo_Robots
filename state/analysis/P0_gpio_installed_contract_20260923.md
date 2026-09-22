# P0 installed GPIO / internal LED contract — 2026-09-23

Result: **eligible source/binary path for an inert, finite GPIO timing diagnostic**
using the named `LED_BUILTIN` macro. No unbounded wait, allocation, or lock was
found in the installed `pinMode(OUTPUT)`, `digitalWrite(LOW/HIGH)`, or
`digitalRead` path for this native GPIOH device. This is not measured WCET,
physical LED verification, a robot HAL acceptance, a PINMAP approval, or a gate.

The safe explicit final state is `pinMode(LED_BUILTIN, OUTPUT)` followed by
`digitalWrite(LED_BUILTIN, HIGH)`: **OUTPUT initially drives LOW / red LED on;
HIGH drives the active-low red LED off**. Do not substitute D13. Do not infer a
known pre-setup LED state from this audit.

Scope: D-051/D-052 bare UNO Q; P0.4 GPIO cost candidate. Read Linux installed
files and packaged ELF only. No MCU connection, execution, register/memory read,
reset, upload, GPIO operation, or other peripheral operation was performed.
Only this new report was written; no fact IDs or ledger/config/code edits.

## Installed identity and evidence

Path abbreviations:

- `C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- `I=C/variants/arduino_uno_q_stm32u585xx/llext-edk/include`
- `Z=I/zephyr/include`
- `E=C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- `T=/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`
- `DT=Z/generated/zephyr/devicetree_generated.h`

All hashes are SHA-256. These are installed package identities, not a new check
of the currently executing MCU loader.

| File | SHA-256 |
|---|---|
| E, 2,303,728 bytes | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.config | `a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba` |
| DT | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| Z/generated/zephyr/autoconf.h | `52178f5eefcf276720b859bdd60fc87ca4207b0130ac1fd5ba099af74b877a0c` |
| C/cores/arduino/wiring_digital.cpp | `ff579a531d1fffffadb05a165f407e8b26d907edac6764f285c1c58632a4d27e` |
| C/cores/arduino/Arduino.h | `5f068c10a0aeb2f6d3cec1fa8b2a313b1f7374bcb77716f0b6cddba5bc198514` |
| C/cores/arduino/wiring_private.h | `b85c0bb1099e24301524fd7e1a76678873cb42bdb191ed747071ba05d82cd9c3` |
| C/cores/arduino/main.cpp | `d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed` |
| C/variants/arduino_uno_q_stm32u585xx/variant.h | `b684000848b9100b6781185045688dcc6701184fa3d43b12696f73747623d678` |
| C/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | `bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5` |
| Z/zephyr/drivers/gpio.h | `aab7888876f29b6ad98217d8099aac677f5238249b95599511038cc35d982316` |
| Z/zephyr/pm/device_runtime.h | `d2a1d76bc51d22a2cdb9c0ccc7d40d9ca83cc3e27e0a3f578df8690310f6cf6e` |

The generated version identifies `v4.2.0-18364-g1743741760ee`. Official primary
sources were opened at Arduino core commit
`79b3f1afdad455f55e4a25030953617152c0227c` and Arduino Zephyr commit
`1743741760ee5d2d58da50d504855d43f9f8e826`; no current-branch API assumption.

## Exact macro, pad, polarity, and ownership

1. Arduino.h:44–70 maps the first `builtin-led-gpios` device/pin back to the
   Arduino digital-pin array; :158–160 supplies `LED_BUILTIN`. Variant.h:37–44
   derives `LED3_R` from `led3_red`, with no conflicting builtin override.
2. Installed overlay:332 identifies digital index **50** as `gpioh 10`, and
   :354 identifies the first builtin entry as the same pad. Both Arduino entries
   have `GPIO_ACTIVE_HIGH`. DT:19715–19720 and :20217–20222 independently confirm
   GPIOH/pin10/flags0 for those entries. Thus `LED_BUILTIN == LED3_R == 50` for
   this installed mapping. Use named macros in the candidate.
3. DT:23269–23306 identifies `led3_red` as the onboard RGB LED3 red channel,
   GPIOH pin10, **flags1 / ACTIVE_LOW**. The pinned board DTS:18–20 agrees.
   Arduino's physical-level convention and the LED's electrical polarity are
   different descriptions, not a pin conflict. [Board DTS](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/boards/arduino/uno_q/arduino_uno_q-common.dtsi#L18)
4. DT:14466 assigns GPIOH device ordinal95; :14516 gives register base
   `0x42021c00`; :14553 says not deferred. Overlay:289 assigns **D13 to PB13**.
   Matrix entries :339–349 are PF0–PF10. Neither is the proposed LED pad.
5. PH10 also supports TIM5 CH1, but overlay:166–173 declares PWM5 deferred
   with empty default/sleep pinctrl; PH10/11/12 are the separate PWM state.
   GPIO measurement must not call `analogWrite`, initialize PWM5, or enable a
   competing LED/PWM service.

This establishes the installed software mapping and intended onboard load.
It does not establish observed color, brightness, voltage, or physical identity
on a damaged/modified board.

## Wrappers, native dispatch, and boundedness

`wiring_private.h:11–16,23–25` uses a fixed constexpr DT table and a bounds
check. `wiring_digital.cpp:19–44` contains no allocation, deferred device init,
polling, lock, sleep, or delay. `pinMode(OUTPUT)` passes
`GPIO_OUTPUT_LOW | GPIO_ACTIVE_HIGH`. It discards the native configure result;
`digitalWrite` discards the write result. `digitalRead` returns HIGH only when
the native result is exactly1; zero and negative errors both become LOW.
Invalid pin indices likewise become silent no-ops or LOW. [Pinned wrapper](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/cores/arduino/wiring_digital.cpp#L19)

Installed gpio.h:1033–1052,1066–1071 ORs the DT flags into configure flags,
updates the per-pin inversion bit, and dispatches `api->pin_configure`.
With this Arduino flags0 entry it clears PH10 inversion. Subsequent
`gpio_pin_get_dt/set_dt` (:1630–1632,:1719–1721) use port/pin, not the spec's
flags anew; set uses the driver's inversion bitmap (:1690–1705), then the raw
set/clear dispatch (:1650–1667). Hence explicitly configuring before writing
also removes ambiguity from any earlier logical-polarity configuration.

Offline GDB on E resolves `__device_dts_ord_95` at **0x0801bf68**, name
`gpio@42021c00`, config **0x0801dd80**, API **0x0801c6e0**, data **0x200016d0**,
init **0x08006541**, flags0. Configuration has base0x42021c00, port7,
pin mask65535. `__llext_sym___device_dts_ord_95.addr=0x0801bf68` is nonzero.
The actual `gpio_stm32_driver` function pointers and disassembly are:

| Operation | Native address (Thumb pointer) | Installed executed body |
|---|---|---|
| Configure | 0x08019151 | `gpio_stm32_config`, 0x08019150–0x08019220; finite flag branches; output LOW writes bit10 to BRR; calls only the finite pad-config routine for this path |
| Pad config | 0x080178bd | `stm32_gpioport_configure_pin`, 0x080178bc–0x080179c4; finite register read/modify/write branches; normal OUTPUT bypasses alternate-function selection; no call/wait/lock/retry loop |
| Read | 0x080190bd | 0x080190bc–0x080190c6; one IDR read at base+0x10, return0 |
| Set HIGH | 0x080190db | 0x080190da–0x080190e2; one BSRR write at base+0x18, return0 |
| Clear LOW | 0x080190e5 | 0x080190e4–0x080190ec; one BRR write at base+0x28, return0 |

The generic driver source contains runtime-PM and other-SoC paths, but these
cannot be assumed active. Installed config:102,114 disables PM_DEVICE/PM;
device_runtime.h:192–201 supplies return0 inline get/put stubs. E confirms no
runtime-PM call or hardware-semaphore wait in the selected native paths.
Config:145 disables assertions and :1701 tracing. The driver and pad-manager
primary sources provide context; E supplies target-specific dispatch/bounds.
[GPIO driver](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/gpio/gpio_stm32.c#L197),
[pad manager](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/soc/st/stm32/common/gpioport_mgr.c#L96)

The LLEXT entries named `z_impl_gpio_pin_configure`, `z_impl_gpio_port_get_raw`,
`z_impl_gpio_port_set_bits_raw`, and `z_impl_gpio_port_clear_bits_raw` all have
**addr0**. They are not callable loader exports. The supported sketch path
must compile the header dispatch and relocate the nonzero GPIOH device; final
candidate ELF inspection remains necessary. API table `port_get_direction`
is NULL despite CONFIG_GPIO_GET_DIRECTION=y; do not add that API as a verifier.

No GPIO API timeout is needed for these finite native paths. This is a bound
on the inspected instruction/control path, not a wall-clock deadline under
interrupts/scheduling/bus stalls. The port configuration and inversion bitmap
use read/modify/write without mutual exclusion, so the diagnostic must be the
sole PH10 configurator and must avoid concurrent GPIOH reconfiguration.

## Loader startup and post-setup state

Config:976 disables CONFIG_LED; the `gpio-leds` DT node alone does not create
an LED driver. E has empty LED API lists and no `led_gpio_init`. Its normal
GPIOH init entry at0x0801bde4 points to the device. `stm32_gpioport_init`
0x08006540–0x08006564 enables VddIO2/port clock; it does not establish PH10's
output mode or level. Packaged `gpio_stm32_data_h` initially has invert0 and
clock-use bitmap0; these ELF values are not a live post-boot observation.

Pinned loader/fixups.c:323–625 places the RGB backup/control service entirely
under CONFIG_BOARD_ARDUINO_VENTUNO_Q. UNO Q E has none of `configure_leds`,
`on_gpio_changed`, `system_utilities`, or `tacho_thd`. This is not an active
UNO Q RGB owner. [Loader fixups](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/loader/fixups.c#L323)

Normal loader startup may run the matrix while awaiting Linux, blanks it and
calls matrixEnd before sketch handoff (:239–272). If Linux is already ready,
that animation block is skipped. E's `turnLed` 0x08005404–0x0800544c accesses
**0x42021400 / GPIOF**, not GPIOH. Do not confuse the separate board variant's
GPIOH matrix implementation with this compiled UNO Q path. USB-mode's infinite
animation path never reaches setup and is not a valid completed measurement.
[Loader startup](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/loader/main.c#L239)

Installed core main.cpp:26–45 starts SerialUSB, calls initVariant and static
thread startup, then setup, then loop plus `__loopHook`. The default weak hooks
are empty, but a linked library can select another implementation. A future
GPIO candidate must audit its own constructors, static threads, initVariant,
and selected hook. The prior ADC/image hook proof is not blanket approval for
an unbuilt GPIO image. No reviewed default loader path above periodically
writes PH10 after setup; the candidate must preserve that ownership.

There is consequently **no certified initial RGB level** here. After successful
explicit Arduino OUTPUT configuration, LOW means LED3 red on and HIGH means
off. Retain HIGH at completion with no later PH10 writes. Readback HIGH is an
internal digital-level check, not optical/electrical calibration.

## Recommendation and remaining prerequisites

Recommend a finite **setup-only** measurement with frozen RAM results and an
empty application loop, using `LED_BUILTIN` only. This is a simple diagnostic
scope choice; unlike installed analogRead, these inspected GPIO paths do not
require a setup exception to conceal an unbounded synchronous wait. Preserve
R4 and independently audit any selected core/library loop hook.

Measure the P0.4 `pinMode(OUTPUT)` plus `digitalWrite(HIGH)` pair, and optionally
its individual operations/readback. Repeated OUTPUT calls transiently light
the red LED; each iteration should end HIGH/off. Keep first-use and repeated
costs distinguishable, preserve paired micros overhead/raw samples, use a
fixed sample count, and label microsecond quantization. A zero duration is
possible at this resolution; a measured maximum is not a mathematical WCET.

Before execution/acceptance:

- Review the concrete source/build for LED macro mapping and exclusive PH10
  operations; no header, PWM, matrix, motor, Bridge startup, or extra peripheral
  operation is implied by this recommendation.
- Audit exact final/debug ELF, relocation through ordinal95, wrapper bodies,
  constructors and loop hook; pin its correct wrapped upload artifact identity.
- Establish successful GPIOH readiness in setup or make its absence fail the
  diagnostic before measurements. Readiness checks do not reconfigure the pin.
  Arduino void/error-masking APIs must not be described as checked native
  success. Expected LOW/HIGH readbacks can detect a mismatch but do not recover
  discarded configure/write error codes.
- Finish HIGH/off before freezing completion; capture must reject missing or
  inconsistent completion/readbacks. Use the separately reviewed bounded
  passive capture and exact deployed-image identity procedure.
- Retain unknown physical initial state/optical confirmation and production
  timing under robot load as separate unproved facts. No additional hardware
  or human action is required merely to prepare this bare-board candidate.

## Reproduction / command outcomes

Read-only transport was `tools.board_tool.remote('2629958581',
['python3','-c',PROGRAM],capture=True,timeout=40)`, with
`SUMO_TRANSPORT=adb`, `SUMO_ADB_SERIAL=2629958581`, and
`SUMO_ADB_EXECUTABLE=C:\Users\narut\AppData\Local\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe`.
PROGRAM used pathlib numbered reads/SHA-256 and subprocess commands:

- `Tnm -n E`; filter GPIO/init/LED symbols: exit0.
- `Tgdb -nx -nh -batch E -ex 'p __device_dts_ord_95'`, plus
  `gpio_stm32_cfg_h`, `gpio_stm32_data_h`, `gpio_stm32_driver`,
  `__init___device_dts_ord_95` and the LLEXT objects above: exit0.
- `Tobjdump -d [-l] --disassemble=FUNCTION E`, for all table functions,
  `stm32_gpioport_init`, `turnLed`, `matrixEnd`: exit0.
- All remote Python reads completed exit0. One exploratory GDB invocation
  ended exit1 only because `leds` and `led_gpio_init` were absent; the successful
  `nm` scan and empty API list independently confirm the latter absence.
- Versioned GitHub/raw reads completed successfully. One archive-print command
  hit Windows cp1252 on an arrow character (exit1); the relevant numbered
  source reads were repeated with UTF-8 stdout and completed exit0. No source
  or device state was changed by either command.

Raw official source hashes used for loader context: main.c
`0b2af678b67a21a10f211538f5c535f0f92fb3ddbf97a302ed22122665f916b8`;
fixups.c `45c3152b26fe6385ddc5eee606ff1307999bc743ab22f9ed521f4ae59499d0a4`;
matrix.inc `1ab79675a96c4f98fbfb4019253a1f0ee899bf0ba6a8f988aa59a269f47d8936`.
Pinned gpio_stm32.c hash:
`9eca88d50330f348995067c75423b17a1d23e4d2b76cf5f268f30c46048ce002`.

## Addendum: supported read-only GPIOH readiness query

The proposed public adapter is supported by the installed named DT node,
header wrapper, and nonzero native export:

```cpp
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

bool gpioReady() {
    return device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpioh)));
}
```

`device.h:12` already includes devicetree.h; the second include is explicit but
optional. `devicetree.h:197` defines DT_NODELABEL; DT:14488 maps `gpioh` to
the previously verified GPIOH ordinal95. `device.h:317` defines DEVICE_DT_GET
as the named device object's address, and :869 declares the public query.

The implementation is **not an exported function named device_is_ready**.
`Z/generated/zephyr/syscalls/device.h:46–59` supplies an inline wrapper calling
`z_impl_device_is_ready`, after a compiler barrier. Userspace/syscall tracing
are inactive in this installed configuration. E contains
`__llext_sym_z_impl_device_is_ready` at0x0801d340 with nonzero callable Thumb
address **0x08019e6f**. The named device export remains **0x0801bf68**.

Offline disassembly at **0x08019e6e–0x08019e82** checks null, then reads
`dev->state` (device+12), the initialized bit (state+1), and init-result byte
(state+0). It returns true only for initialized/successful state. There are
no stores, function calls, loops, waits, initialization, or peripheral-register
accesses in this body. It checks existing device initialization, not PH10's
mode, output level, optical LED state, or future hardware health.
[Pinned implementation, kernel/device.c:190–197](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/kernel/device.c#L190)

Additional installed hashes: device.h
`300420020155fc22a7e4e3a867f26fe30c6a79b9be3474caf990bacfecbd2d19`;
devicetree.h `7c202557ce2a12afb0016aa2471088bc61b7ad23d249bfbc8c1e67902e16833b`;
generated syscalls/device.h
`3d4e26c69424baf08feeb4b61edd366e2c07d40077e798afd285bd5bb2eaa3b3`.
Same read-only transport: numbered header reads, `Tnm -n E`, offline
`Tgdb ... -ex 'p __llext_sym_z_impl_device_is_ready'`, and
`Tobjdump -d -l --disassemble=z_impl_device_is_ready E` all completed exit0.
Initial exact-name inspection found no device_is_ready symbol, as expected
for this inline public wrapper. No query was executed on the MCU. The parent
candidate's actual compile and relocation inspection remain outstanding;
this addendum establishes source/API/export support, not a completed build.
