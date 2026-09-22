# P0 G2 installed interrupt contract audit — 2026-09-23

Result: **installed Arduino API and native GPIO/EXTI paths verified; target
probe compilation and interrupt execution not performed by this audit.**
FALLING/RISING/CHANGE have a native edge path. LOW/HIGH are accepted by the
Arduino wrapper but rejected by the installed STM32U5 driver; the wrapper hides
that failure. `detachInterrupt()` only changes its software handler state,
leaving a successfully configured hardware interrupt and EXTI ownership intact.
The four proposed QTR pads use distinct EXTI lines, which establishes mapping
feasibility only. Safe acquisition/rearming and SC-B remain unresolved.

Scope: read-only Linux package files through the existing ADB serial2629958581,
offline packaged-ELF inspection and pinned official sources. No live interrupt
registration, GPIO operation, MCU debugger connection, peripheral/memory read,
upload, reset, PWM action, library install or compile. Only this report and
`P0_irq_installed_raw_20260923/` were added. No shared ledger/config/code edit,
fact number, motor authorization, PINMAP approval or human phase gate.

Read AGENTS.md in full, current PROGRESS, P0 task0.1 G2, PLAN section3,
HARDWARE proposed pins, FACTS F-033/F-080/F-082/F-083, D-051/D-052/D-065/D-066,
P0_G2 and the previous installed GPIO/QTR audits. Local clock at start was
2026-09-23 03:18:51+04:00: Wednesday's P0/P1 schedule window, before scope cuts.
D-051 delegates engineering choices; this audit does not select async sample
semantics or modify B4/B16. No relevant memory-registry entry was found.

## Reproducible evidence and identities

Abbreviations:

- C = `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- H = `C/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include`
- DT = `H/generated/zephyr/devicetree_generated.h`
- E = `C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- T = `/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

Installed version.h reports kernel4.4.2-rc1 and build
`v4.2.0-18364-g1743741760ee`. Native interpretation uses pinned official Zephyr
revision `1743741760ee5d2d58da50d504855d43f9f8e826`; actual installed headers and
ELF remain authoritative. Arduino release source is pinned to
`79b3f1afdad455f55e4a25030953617152c0227c`. The complete pinned WInterrupts.cpp
bytes exactly match the installed file; no blanket source identity is inferred.

| Re-read installed file | SHA-256 |
|---|---|
| E | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.config | `a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba` |
| C/cores/arduino/WInterrupts.cpp | `2c323e40fd94d34101ce59cc3ddd079d676765de3115c9932127f9d60ca27166` |
| C/cores/arduino/Arduino.h | `5f068c10a0aeb2f6d3cec1fa8b2a313b1f7374bcb77716f0b6cddba5bc198514` |
| C/cores/arduino/api/Common.h | `f50252fe58ee67f4d9ed4f38b91d718c129976b65f2e0eb726b80c51d31265f1` |
| C/cores/arduino/wiring_private.h | `b85c0bb1099e24301524fd7e1a76678873cb42bdb191ed747071ba05d82cd9c3` |
| DT | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| H/zephyr/drivers/gpio.h | `aab7888876f29b6ad98217d8099aac677f5238249b95599511038cc35d982316` |
| H/generated/zephyr/syscalls/gpio.h | `6cd7d45375e80f61680c35b8cbd67b23f6abfa95558a0f557e655598dc2fd902` |
| H/zephyr/drivers/gpio/gpio_utils.h | `7c29ab8de3dcb99f9b5157d5085cf9f5b15849cea872d235ed7fd709e04165e4` |
| H/zephyr/drivers/interrupt_controller/gpio_intc_stm32.h | `e870140dd96c6b662d90fe66e986b23e867700b3999e2416796bed6a4c91f067` |

Full contents, additional hashes, literal remote command argument arrays, host
timestamps, stdout/stderr and exit statuses are retained in the raw directory:

- `installed_read_01.json`: twelve installed source/config/ELF hashes and text
  except ELF bytes. Remote Python exit0.
- `installed_nm_02.json`: remote Python and nested `Tnm -anC E`, both exit0.
  The recorded program retains all matching GPIO/EXTI/interrupt/device symbols.
- `installed_gdb_03.json` and its text view: `Tgdb -nx -nh -batch E` with only
  `p` and `disassemble` commands; exit0, empty stderr. There is no target/run/call.
- `installed_read_04.json`: five further installed headers/core sources, exit0.
- `source_read_01/02/03.json`: exact HTTPS URLs, HTTP statuses, complete source
  text and SHA-256. Two initial guessed paths returned404 and are preserved;
  corrected official paths returned200. These failures are not missing APIs.

Raw source copies are convenience views of the recorded responses. Installed
ELF-file BSS values are initial image data, **not live MCU state**. None of these
receipts independently verifies the currently running loader/sketch identity.

## Public Arduino contract and important failure behavior

`Arduino.h` includes Common.h and declares digitalPinToInterrupt at:137.
Common.h declares the callback as `void (*)(void)`, and exposes:

```cpp
int digitalPinToInterrupt(pin_size_t pin);
void attachInterrupt(pin_size_t pin, voidFuncPtr callback, PinStatus mode);
void detachInterrupt(pin_size_t pin);
```

PinStatus values are LOW0, HIGH1, CHANGE2, FALLING3, RISING4. This is an enum API,
not a generic integer mode argument. The wrapper implementation lives in the
sketch-linked core, not as an attachInterrupt symbol exported from E. Its exact
final code/relocations must therefore be inspected in the separate probe ELF.
[Pinned, byte-matched WInterrupts source][arduino-irq].

Installed WInterrupts.cpp:19–44 contains one static callback record per GPIO
port; each contains16 handlers for this DT, an enabled flag per handler, a port
mask and a device pointer. The installed Arduino table contains9 unique ports;
`wiring_private.h:70–76` derives these bounds at compile time. There is no heap
allocation in this implementation. Port lookup also claims the first unused
record; it is not a read-only lookup and has no reclamation path.

- `digitalPinToInterrupt`:149–155 checks the Arduino index range, claims/finds
  its port record, then returns the original Arduino number or-1. It neither
  configures hardware nor verifies readiness, supported mode, EXTI availability
  or physical pin suitability. Even this query must remain uncalled in a probe
  whose setup contract permits only address publication.
- `attachInterrupt`:92–128 rejects invalid Arduino indices, null callbacks and
  unknown PinStatus. Otherwise it ORs the pin into the port mask, stores the
  handler and sets enabled **before** configuring the native interrupt. It then
  initializes/adds the port callback. Both configuration and callback-list
  return codes are discarded; there is no rollback or status returned.
- `detachInterrupt`:130–135 first stores a null handler, then clears enabled.
  It does not disable EXTI, remove the GPIO callback, clear the port mask,
  release the native line callback, or clear pending flags.

The null-before-disabled order plus `handleGpioCallback`:58–67 (enabled check,
then unconditional handler call) is a **source-level null-call race risk** if an
IRQ interleaves. No lock encloses those operations. Exact compiled ordering and
an exercised fault are not established by this source finding. Likewise first
attach enables the native line before adding the application's GPIO callback;
an intervening event can be consumed without that callback. Repeated attach
reuses/reorders a per-port list entry. None is an atomic rearm primitive.

| Arduino mode | Native request | Installed STM32U5 result |
|---|---|---|
| LOW / HIGH | GPIO_INT_LEVEL_LOW / HIGH | `-ENOTSUP` (-134), hidden by wrapper |
| CHANGE | GPIO_INT_EDGE_BOTH | Supported edge route, subject to ownership |
| FALLING | GPIO_INT_EDGE_FALLING | Supported edge route, subject to ownership |
| RISING | GPIO_INT_EDGE_RISING | Supported edge route, subject to ownership |

The driver verifies this independently of Arduino source: E's
gpio_stm32_pin_interrupt_configure0x0800d72c compares level mode and returns-134
at0x0800d7c2. Edge trigger validation returns-EINVAL(-22) at0x0800d7c8; an occupied
line returns-EBUSY(-16) at0x0800d7ce. A failed reconfiguration does not guarantee
that any previous successful edge configuration has been disabled. A void return
from attachInterrupt is therefore insufficient runtime acceptance.

## Native ABI, exports, ownership and cleanup

The installed GPIO API (`gpio.h:734–736`) uses this different callback ABI:

```cpp
void callback(const struct device *port, struct gpio_callback *cb,
              gpio_port_pins_t pins);
```

The callback object has list node, handler and pin mask. The installed header
explicitly requires a lifetime beyond stack scope while registered. The
low-level STM32 callback is `void(gpio_port_pins_t, void*)`, explicitly invoked
in ISR context. Arduino's adapter ultimately runs the no-argument user callback
in that same ISR chain, not on a worker thread.

`gpio_init_callback` is inline/void. `gpio_add_callback` and
`gpio_remove_callback` inline-dispatch through manage_callback and return int;
they return-ENOSYS when absent. This installed driver's remove returns-EINVAL
for an absent entry, and add removes an existing identical list node before
prepending it. No allocator, semaphore or retry wait occurs in those actual
functions, but list traversal depends on the number of registered callbacks.
No fixed execution-time bound follows from an API signature.
[Pinned GPIO utility implementation][gpio-utils].

| Actual packaged ELF object/function | Address/value |
|---|---|
| GPIOA / `__device_dts_ord_89` / matching LLEXT export | `0x0801c064` |
| GPIOB / `__device_dts_ord_90` / matching LLEXT export | `0x0801c040` |
| shared GPIO driver API | `0x0801c6e0` |
| pin_interrupt_configure API pointer | Thumb `0x0800d72d` |
| manage_callback API pointer | Thumb `0x080190fd` |
| get_pending_int API pointer | NULL |
| `__llext_sym_z_impl_gpio_pin_interrupt_configure.addr` | **0** |

The installed generated syscall header calls z_impl_gpio_pin_interrupt_configure;
the normal gpio.h local inline body decodes flags and dispatches through the
nonzero device API (:887–952). Named z_impl_gpio_* weak symbols/exports at0
cannot be assumed callable just because link metadata contains their names.
Inspect the probe's real undefined symbols and local dispatch body. Generic
`gpio_get_pending_int` would return-ENOSYS for this NULL API slot; it cannot
prove pending-state cleanliness. The ELF has native stm32_gpio_intc_*/exti_*
function symbols, but the captured symbol inventory has **no corresponding
LLEXT export entries**. Direct imports of those internals are not established.

Installed CONFIG_GPIO_STM32/EXTI_STM32/GPIO_INTC_STM32 are enabled;
CONFIG_GPIO_ENABLE_DISABLE_INTERRUPT is disabled. Consequently the optional
disable-only/enable-only API modes are not available. Ordinary
GPIO_INT_DISABLE is a different operation with the cleanup below.

The native interrupt path is:

1. GPIO interrupt configure obtains line `1 << pin` irrespective of port.
2. `stm32_gpio_intc_set_irq_callback`0x080096fc operates on16 line slots.
   The same `(gpio_stm32_isr, device)` pair is accepted again; a different
   registered pair yields-EBUSY. Thus PA3 and PB3 cannot both own line3.
3. On success it programs that line's source port, sets trigger bits, unmasks
   the EXTI line and enables the NVIC IRQ. The inspected paths do not clear
   a preexisting EXTI pending flag before enabling.
4. `stm32_intc_gpio_isr`0x08009610 checks pending, clears it, then dispatches
   to the line callback. `gpio_stm32_isr`0x08019222 walks the port's application
   callback list, intersects each mask and calls its handler. The installed DT
   describes16 one-line IRQ ranges, rather than a shared5..9/10..15 grouping.

Ordinary GPIO_INT_DISABLE checks that the currently selected source port matches
the requested port, then masks the line, clears the native line callback and
sets trigger NONE (E0x0800d74c–0x0800d770). A mismatched port returns0 without
those changes. This does not remove an application gpio_callback list entry,
clear pending flags, or disable the NVIC IRQ itself. `gpio_remove_callback`
is a separate list operation and does not disable hardware. Safe lifecycle
handling requires a coordinated policy; neither primitive alone proves it.
[Pinned GPIO driver][gpio-driver], [pinned GPIO interrupt controller][gpio-intc],
[pinned EXTI pending/clear implementation][exti].

This is edge notification, **not hardware timestamp capture or an event FIFO**.
The ISR clears a pending bit before software callbacks. Callback times include
interrupt latency and serialization; multiple edges while pending can coalesce.
Those are consequences of the inspected path, not observed lost-edge counts.
No latency, maximum edge rate, simultaneous-edge order, worst-case ISR or complete
800us control-tick measurement is supplied by this audit.

## Proposed QTR mapping and outstanding conditions

The re-read installed DT:19188–19257 gives:

| Proposed signal | Arduino index | Pad | GPIO ordinal | EXTI line |
|---|---:|---|---:|---:|
| QTR_FL | D2 / 2 | PB3 | 90 | 3 |
| QTR_FR | D4 / 4 | PA12 | 89 | 12 |
| QTR_RL | D7 / 7 | PB2 | 90 | 2 |
| QTR_RR | D8 / 8 | PB4 | 90 | 4 |

All four have DT flags0. They are pairwise distinct line numbers and both GPIO
devices have nonzero exports. This is a source/binary-supported candidate for
four falling-edge notifications, not proof that all lines are free now. The
packaged intc_gpio_data contains16 zero initial callbacks; runtime owner state
was deliberately not inspected.

The existing [bare QTR ownership audit](P0_qtr_bare_contract_audit_20260923.md)
remains applicable: PB3/PB4 have SWJ initial-mode caveats; PA12 can belong to
CAN/MCU USB; PB3/PB4/PB2 are PWM alternatives. GPIO mode configuration must be
deliberate and competing pinctrl owners excluded from the final image. This
report does not reclassify initial pad mode or hardware wiring as measured.
Interrupt configuration alone does not select GPIO INPUT mode. The installed
Arduino OUTPUT mode first drives LOW, so a charge/mode sequence can itself
create transitions if interrupts are left armed.

Future acquisition work must explicitly handle charge/release-to-arm timing,
already-LOW pads, stale pending events, ISR/main synchronization, per-acquisition
identity, timeout censorship, lost/late events, detach/rearm races, errors and
bounded cleanup. Actual isolated3.3V stimulus and then real QTR tests must cover
each channel, simultaneous edges, timeout, noise and lifecycle boundaries.
Those checks require separate eligibility/contracts and do not follow from
this compile-only task. Sensor voltage, freshness semantics, SC-B, wiring
acceptance, PINMAP OK and full robot WCET remain pending.

## Minimal compile-only contract recommendation

Record the coordinator's material decision before implementing the probe.
Use an unregistered, never-uploaded sketch with no global callback registration,
pin operations or device initialization. Include Arduino.h; gpio.h is also
included by it, but an explicit native include is reasonable.

1. Retain a noinline public probe accepting `(pin_size_t pin,
   void (*callback)(), PinStatus mode)`. Inside only that never-called body,
   compile digitalPinToInterrupt, attachInterrupt and detachInterrupt using
   the parameters. Preserve the query return in the probe result so it remains
   observable if compiled. Do not choose a new production pin or runtime value.
2. If native ABI coverage is included, use another retained never-called function
   with device, callback-object, pin, flags, native handler and mask parameters.
   Compile gpio_init_callback/add/configure/remove and preserve integer statuses.
   Static callback storage is necessary for an eventual live registration, but
   parameter-only compilation does not register an object or adopt a lifecycle.
3. setup publishes only function addresses to externally visible volatile
   function-pointer anchors; loop is empty. Do not call even digitalPinToInterrupt
   from setup. Used/noinline alone does not prove survival of linker GC.
4. Inspect the final source map and ELF: both probes and intended calls retained;
   setup/loop do not invoke them; no dynamic constructors register callbacks;
   ordinary local inline GPIO dispatch, no executed zero-valued import; actual
   callback ABI matches. Inspect any linked dependency startup/hook behavior.
5. A pass means selected source/API and retained link compatibility only.
   Preserve any compiler/link errors; do not repair upstream source silently,
   add an inert upload allowlist entry or equate a build with interrupt operation.

Coordinator next action: integrate the installed findings into the scoped G2
decision/facts, then separately implement and review that compile-only probe.
No production QTR architecture or runtime workaround is adopted here.

[arduino-irq]: https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/cores/arduino/WInterrupts.cpp
[gpio-driver]: https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/gpio/gpio_stm32.c#L398
[gpio-intc]: https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/interrupt_controller/intc_gpio_stm32.c#L110
[exti]: https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/interrupt_controller/intc_exti_stm32.c#L94
[gpio-utils]: https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/include/zephyr/drivers/gpio/gpio_utils.h#L96
