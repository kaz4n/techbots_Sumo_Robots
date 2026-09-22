# P0 installed ADC contract audit — 2026-09-23

Status: **INSTALLED SOURCE / PACKAGED BINARY VERIFIED; NO ADC MEASUREMENT.**
Read-only audit started 02:03 Dubai. PLAN section 3 schedules P0 completion/P1
today; PROGRESS leaves human gates pending. Scope is P0 0.4 bare-board feasibility
under D-052, with no MCU connection, register read, function execution, upload,
reset, peripheral write, pin reassignment, external hardware request or P2 work.
Only this new analysis file is owned by this audit; other agents' files are untouched.

**Verdict:** stock `analogRead(A0)` has no finite total deadline, even after
warmup. The installed loader offers synchronous ADC only. A narrowly reviewed,
inert **setup-only** timing diagnostic can characterize successful first/warm
calls without claiming R4 runtime compliance. Its setup can hang; calling it
from the control loop, another post-setup thread, or an ISR does not establish a
bounded acquisition path. No production ADC HAL is approved by this report.

## Installed identity and reproduction

Abbreviations:

- `C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- `I=$C/variants/arduino_uno_q_stm32u585xx/llext-edk/include`
- `Z=$I/zephyr/include`
- `E=$C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- `T=/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

All board reads used `tools.board_tool.remote('2629958581',
['python3','-c',PROGRAM],capture=True,timeout=30..45)` with
`SUMO_TRANSPORT=adb`, `SUMO_ADB_SERIAL=2629958581`, and
`SUMO_ADB_EXECUTABLE=C:\Users\narut\AppData\Local\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe`.
This targets the exact serial via `shell -T`. Python read public package files
using `Path.read_text().splitlines()` with numbered lines, and
`hashlib.sha256(Path.read_bytes()).hexdigest()`. Every remote query, nm,
objdump and offline-GDB invocation returned exit 0. No live GDB target was opened.

Exact ELF commands, with these variables expanded:

```text
${T}nm -n "$E"
${T}objdump -d -l --disassemble=NAME "$E"
${T}objdump -d -l --start-address=START --stop-address=STOP "$E"
${T}gdb -nx -nh -batch "$E" -ex 'p EXPRESSION'
```

`NAME`: `adc_stm32_read_sync`, `adc_stm32_channel_setup`, `adc_stm32_enable`,
`adc_stm32_disable`, `adc_stm32_init`, `adc_stm32_calibrate`,
`adc_stm32_calibration_start.isra.0`. Address ranges inspected separately:
`0x08009ce4/0x08009d02`, `0x0800a070/0x0800a128`,
`0x080097dc/0x080098e0`. GDB expressions: `__device_dts_ord_17`,
`adc_stm32_cfg_0`, `adc_stm32_data_0`, `__llext_sym___device_dts_ord_17`,
`__llext_sym_z_impl_adc_read`, `__llext_sym_z_impl_adc_read_async`,
`*(struct adc_driver_api *)0x0801c5f4`,
`__pinctrl_dev_config__device_dts_ord_17`, `__pinctrl_states__device_dts_ord_17`,
`__devicedeps_dts_ord_17`, `__llext_sym_z_impl_k_sem_take`,
`__llext_sym_z_impl_device_init`. These read packaged objects only.

| Installed file | SHA-256 |
|---|---|
| E | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.config | a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba |
| C/cores/arduino/wiring_analog.cpp | 32d805872068e175b03cc291d3697f3ea7443501424dd870165d0bebeddd6c98 |
| C/cores/arduino/Arduino.h | 5f068c10a0aeb2f6d3cec1fa8b2a313b1f7374bcb77716f0b6cddba5bc198514 |
| C/cores/arduino/main.cpp | d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed |
| C/cores/arduino/zephyrPinctrl.cpp | f48670ba733b9a1a3de8fe6ee903009f48b1f3d4da6b05521daffd93a88c51b9 |
| C/cores/arduino/zephyrPinctrl.h | f2c7bd8cacb563ebc89881c9771ad226eadee52419b4fc8c36895a332368183b |
| C/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5 |
| Z/generated/zephyr/devicetree_generated.h | 5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80 |
| Z/generated/zephyr/autoconf.h | 52178f5eefcf276720b859bdd60fc87ca4207b0130ac1fd5ba099af74b877a0c |
| Z/generated/zephyr/version.h | edc930eb795ececf06480cea0a0365392ecb9d1e47a5d038f8d708e7dad6ecf8 |
| I/zephyr/drivers/adc/adc_context.h | dbf014fe0d4d7c29e11df83a072a6336c1aff9387c53604b87b1b83846fa0b29 |
| Z/zephyr/drivers/adc.h | aa99e8f7b11c5471b8aab63e6ec2cd96dc4d722da057dbcb34bfa56f0c57b551 |
| Z/generated/zephyr/syscalls/adc.h | 9826d89cadf700621f8fe67830f8737e0a10be47b48bb9995435ca5e366db7be |

Generated version.h:14–23 names Zephyr 4.4.2-rc1 /
`v4.2.0-18364-g1743741760ee`. No installed `adc_stm32.c` was found by
`C.rglob('adc_stm32.c')`; driver line references below come from ELF DWARF and
the corresponding versioned primary source, with relevant machine code checked.
Installed metadata and package hashes do not certify the currently deployed
loader; no new flash readback was performed.

## Pin and call contract

1. Arduino.h:104–110 derives `A0/A1` from generated ADC GPIO mappings; it does not
   hardcode a universal pin number. DT:19319–19340 and 20551–20572 map them to
   Arduino indices **14/15**, GPIOA **PA4/PA5**. DT:21080–21093 maps these to
   **ADC1 channels 9/10**; DT:2876 gives ADC1 ordinal **17**. Overlay:292–293,
   383 onward and 421–422 agree. This preserves HARDWARE's proposed ADC-only
   A0 battery/A1 button use and does not resolve F-023's wider output-use conflict
   or grant PINMAP OK.
2. DT:31073–31112 and 31191–31230 configure gain 1, `ADC_REF_INTERNAL`,
   acquisition value 16383 (`ADC_ACQ_TIME_MAX`, ADC binding header:21),
   single-ended **14-bit** conversion. Packaged API `ref_internal=3300` is a
   declared millivolt value, not a measured reference or calibration.
3. `wiring_analog.cpp`:185 defaults the returned width to **10 bits**;
   206–267 builds a stack `uint16_t` buffer and one-channel sequence with
   `options=nullptr`, no extra samples and `calibrate=false`. It searches the
   fixed six-element mapping, restores that ADC pin's analog mode, configures
   the channel, performs synchronous `adc_read`, returns negative setup/read
   errors, and shifts the 14-bit result to the requested width. At default width
   this is a right shift by four. `analogReadResolution` changes this mapping,
   not the DT hardware resolution. There is no explicit allocation in this
   wrapper; arrays are static and the per-call sequence/buffer are on the stack.
   **Zero is a valid nonnegative API result**, not a sentinel for failure.
   Preserve the signed return before classifying negative errors. Neither zero
   nor a positive value establishes physical accuracy; the wrapper has no
   separate status for a plausible but physically wrong conversion.
4. `zephyrPinctrl.cpp`:123–166 calls `device_init` if not ready, then restores
   only the selected pin in the installed `arduino` state. DT:3239 records
   deferred initialization, 3257–3262 identify A0/A1's analog states, and
   3245–3256 give empty default/sleep states. ELF confirms device flags=1,
   three states with 0/0/6 pins, API at 0x0801c5f4 and static driver context.
   First use can therefore initialize/calibrate ADC1; subsequent successful
   reads still do pinctrl plus channel setup. The wrapper **ignores the pinctrl
   helper's error** before proceeding to setup/read. A failed first init is not
   safely characterized by assuming the next call returns an error.

## Bounds and unavailable alternatives

- Installed ADC header:1040–1044 and 1088–1092 dispatch setup/read through the
  device API. ELF verifies non-null entries `adc_stm32_channel_setup` at
  0x080098f9 and `adc_stm32_read_sync` at 0x08009ce5 (Thumb addresses).
  The exported ADC1 device address is nonzero. Both `z_impl_adc_read` and
  `z_impl_adc_read_async` export records have **address zero**; an apparent
  exported symbol name alone does not prove a callable function. Normal
  synchronous headers use inline device dispatch; final diagnostic relocation
  inspection is still required after its actual compile.
- `adc_context.h`:51–52 defaults completion timeout to `K_FOREVER`; 137–141
  takes the context lock forever; 167–181 takes the completion semaphore with
  that timeout. ELF proves both on this package: 0x08009cf4–0x08009cfe loads
  64-bit -1 then calls `z_impl_k_sem_take` for the lock, and
  0x0800a0f4–0x0800a100 does the same for completion. The no-options path starts
  sampling at 0x0800a10c and branches directly to the same indefinite wait.
  Normal ISR completion gives the semaphore at 0x080098d2. Sole ownership can
  avoid ordinary contention; it cannot bound a missing conversion interrupt.
- Init polls LDORDY without a counter/deadline at 0x0800a22c–0x0800a230.
  Calibration has another hardware-dependent back edge at
  0x08009bda–0x08009bde. The disable helper polls conversion-stop and ADEN-clear
  without deadlines at 0x080183f0–0x080183f4 and 0x08018406–0x0801840a.
  The latter can also be reached when changing resolution, beyond first init.
  In contrast, enable has ten iterations of `k_busy_wait(100)` at
  0x080183b8–0x080183c6 and returns `-ETIMEDOUT` on expiry. That local timeout is
  **not** a whole-call bound; start_read's enable call at 0x0800a08a is followed
  by conversion setup without testing its return.
- Config:732–746 enables ADC/STM32 but disables **ADC_ASYNC, ADC_STREAM,
  ADC_DEFAULT_RTIO and ADC_STM32_DMA**. Header:1012–1023 and offline API object
  agree: only channel_setup, read and ref_internal are present. There is no
  installed nonblocking ADC read/cancel/deadline API established here. Defining
  ADC_ASYNC in a sketch would misdescribe the loader ABI; redefining
  ADC_CONTEXT_WAIT_FOR_COMPLETION_TIMEOUT in a sketch cannot change this
  precompiled driver. A timeout check after `analogRead` cannot interrupt it.
- Neither static storage nor warming proves complete allocation freedom or
  WCET: driver error paths call logging and initialization calls dependencies.
  This audit does not certify the entire transitive allocator/logger/scheduler
  path. These additional unknowns cannot repair the already-proved unbounded
  waits. No duration, jitter percentile or 800 us guarantee was measured.

## Exact prerequisites and permissible evidence

For a P0 setup-only diagnostic, the coordinator must first freeze a contract
that keeps **all** raw ADC calls (first and repeated) inside setup, names only
the existing A0 ADC input, preserves signed API errors, and uses fixed storage.
Two measurements must not be confused: a **first raw call** intentionally
includes any deferred device initialization, whereas explicit checked pre-init
would separately measure initialization and exclude it from the subsequent
first raw call. Raw-first is eligible as a setup-only diagnostic; it is not
required to pre-initialize away the cost it is measuring. Label subsequent
calls as warmed only if prior initialization/conversion actually completed
successfully. Record attempted/completed counts and reject incomplete/error
captures. The discarded helper error described above remains a raw-first risk,
not an implicit success assumption. A strict finite sample count bounds only
calls attempted, not their completion. The inert source and target image
need independent review, successful compile, exact pin/ABI/relocation/startup
inspection and the existing D-052 upload eligibility checks before execution.
Setup liveness remains unproved; an incomplete diagnostic yields no timing
result. Any outside observer timeout must be labeled as an observation limit,
not an ADC timeout. No unreviewed recovery/reset or driver modification follows.

**Global and loop hook check:** installed core `main.cpp`:26–46 optionally
starts SerialUSB, calls initVariant/start_static_threads, runs setup, then
repeats loop plus `__loopHook`. The core weak hook is empty, but installed
`/home/arduino/Arduino/libraries/Arduino_RouterBridge/src/bridge.h`:354–356
also defines a weak hook calling `k_yield()` and `safeUpdate()` (SHA-256
`ca275c57d1865db16a24e14c901757c31fac7ada91bb09130e07dfb6b4b9febb`). An empty
sketch loop therefore does not alone prove no post-setup library work. The
previous image-specific audit in P0_installed_debug_contract.md found that
RouterBridge hook linked, including its mutex path; do not transfer that
image's conclusions to a new ADC sketch. Inspect the final selected hook,
constructors, initVariant, main and static-thread section. A strong no-op hook
is an available diagnostic design choice requiring its own source/binary
review, not a change made here. The ADC source's static table initializers do
not themselves call peripheral APIs; this is not an audit of every linked
constructor or loader service.

If the coordinator requires a diagnostic with a finite total execution bound,
stock analogRead is **blocked**. Keep that measurement pending; do not move the
blocking call into loop, a background thread or interrupt. A later runtime ADC
solution needs an explicitly designed, reviewed bounded driver/acquisition
contract (including ownership, completion, cancellation and stale-data/fault
handling), actual target support and fault/WCET measurement. A worker thread
or a prospective loader rebuild is not an already available compliant API and
is outside this source-audit/P0 diagnostic scope.

Successful setup-only samples may report observed first/warm elapsed time,
overhead, sample/error counts and empirical min/max/percentiles for that exact
image and interrupt configuration. They prove neither worst-case function time
nor full-loop R4 compliance. Floating A0 readings prove no battery voltage,
divider ratio, ADC accuracy, button ladder separation or sensor acceptance;
those depend on later physical evidence. P0/P1 human gates remain unchanged.

## Versioned primary-source cross-check

Official pages were opened with the web tool; exact raw sources were also read
in memory with `urllib.request.urlopen(...,timeout=20)` and compared, exit 0.
Installed [wiring_analog.cpp](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/cores/arduino/wiring_analog.cpp)
is byte-identical to that release source. The
[ADC context](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/adc/adc_context.h)
source agrees on both waits; its only line-level difference from the installed
header is removal of a comment on a default label. The
[ADC API](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/include/zephyr/drivers/adc.h)
was checked against the installed header, whose hash is recorded separately;
the installed content and binary control the conclusions above.
The [STM32 driver](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/adc/adc_stm32.c)
explains the matching packaged paths at source lines 416–457, 499–549,
1285–1295 and 1454–1508. Raw driver source SHA-256:
`d70756d2a035794897a0aab1c2c5393b92c34d3aac885bac7d6dc72b58caf397`.
No current branch was substituted for the installed revision.
