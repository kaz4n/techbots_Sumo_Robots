# P2 B6 installed matrix API and bounded submission audit

2026-09-23 Asia/Dubai. D051/D075 software scope; source/API and offline packaged
ELF evidence only. No upload, MCU/debugger attach, reset, register read, matrix
operation or physical observation. Existing ADB serial2629958581 was used only
for Linux file reads and offline nm/objdump/GDB. Today is Wednesday23September;
PLAN section3 schedules P0/P1, while D075 permits this P2 software work without
manufacturing physical gates. No FACT ID or ledger change is made here.

## Result and recommended adapter contract

A concrete native adapter is viable for bounded **SUBMITTED_UNCONFIRMED** output.
The four installed void calls cannot establish display readiness or optical
success. Keep a single explicitly granted boot owner, normal startup only, and
initialize only during setup. The existing Immediate matrix prohibition remains.
No automatic constructor, destructor, text playback, or repeated begin belongs
in the tick. Grant is a software precondition, not evidence that loader ownership
or the actual physical display was inspected.

Use exactly104 readable bytes, row-major8x13 as the library canvas convention,
`matrixSetGrayscaleBits(3)` and binary pixel values0/7. At grayscale1, value1 is
legal but maps to ISR case4 (`counter % 3 == 0`), so it is not full brightness.
Reject wrong length, null input and values outside0..7 before any native write;
using fixed-size Frame and restricting output0/7 simplifies this. The source
copy consumes the caller bytes before returning and does not retain its pointer.
Application code must not mutate the supplied bytes concurrently.

`matrixGrayscaleWrite` copies directly into the one buffer read by the timer ISR.
There is no double buffer, swap, lock, queue or display-complete acknowledgement.
For a coherent buffer update, check privileged Thread context first
(`__get_CONTROL() & 1` must be0 and `__get_IPSR()` must be0), then save PRIMASK,
disable IRQ, call the fixed write, issue DMB and restore the exact saved PRIMASK.
Keep rendering, input validation and all error handling outside this section.
Never use unconditional `__enable_irq()` to close it. The installed CMSIS
implementations are finite inline instructions with compiler memory clobbers
on masking/restoring/barrier operations. A target-retained compile/disassembly
must confirm the actual adapter emits this sequence; that is later verification.

This exclusion prevents an ordinary ISR from reading a partly copied buffer on
this single Cortex-M33. It does **not** synchronize the commit to scan index0:
one physical104-LED scan may still contain slots from the old and new images.
It does not block NMI/HardFault, so exclusive ownership must prohibit writes from
those handlers too. Masking delays other IRQs and may coalesce matrix updates;
its duration and effect on QTR/IMU/control deadlines remain unmeasured. Avoid
calling Zephyr `arch_irq_unlock_outlined` as a PRIMASK-restoring substitute: its
actual ELF unconditionally enables fault/IRQ before restoring BASEPRI.

Set grayscale and submit an initial blank frame before setup starts scanning,
under the owner/context contract. `matrixBegin` has no success return. A local
initialized flag means only that the call was made. `matrixEnd` stops its counter
but neither blanks the last driven LED nor resets the scan/brightness counters;
do not expose an optical-off guarantee or invoke it as a per-frame synchronization
trick. Native timer validation beyond the readiness precheck below would need
a separately frozen ownership/clock/timer contract.

### Required readiness precheck and available introspection

Include `<zephyr/device.h>` and `<zephyr/devicetree.h>`; the exact installed node
is `DEVICE_DT_GET(DT_NODELABEL(counter_matrix))`. Missing node/export must fail
the target build; a null pointer or failed `device_is_ready(dev)` must reject
initialization before begin/grayscale/frame calls. A host seam should exercise
both null and not-ready failures. The node resolves to ordinal233 and has an
actual nonzero LLEXT device export, detailed below.

`device_is_ready` is an inline syscall wrapper, not an exported function of that
name. Its actual LLEXT target `z_impl_device_is_ready` is0x08019e6f; its installed
body checks null, then device state `initialized && init_res == 0`, with no wait
or allocation. This precheck establishes only kernel device initialization.
It does not establish that matrixBegin succeeded, the timer is running, the
display is visible, or exclusive ownership. Keep INIT_UNCONFIRMED and
SUBMITTED_UNCONFIRMED even after it passes. No retry/device_init is needed for
this enabled, nondeferred device. A changed package must be re-audited.

Available public native getters are `counter_get_value(dev,&ticks)` (returns
status and reads TIM CNT), `counter_get_top_value(dev)` (reads TIM ARR), and
`counter_get_frequency(dev)` (returns a cached driver frequency). Their installed
inline bodies dispatch through the nonzero device API. None proves actual ISR
delivery, visible pixels, independent clock accuracy or a completed scan. There
is no matrix-specific framebuffer/grayscale/scan-complete getter in this header,
nor a public is-running method in the retained counter API. Do not dereference
private framebuffer addresses as a portable production status interface. This
audit did not execute any getter on the MCU.

## Fresh installed identities and bindings

CORE is `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`.
ELF is `CORE/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`,2303728bytes,
SHA256 `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
This is installed packaged loader evidence, not a current deployed-loader check.

| Native function | ELF code address | Dynamic/actual LLEXT export address | Audited behavior |
|---|---|---|---|
| matrixBegin |0x08005628|0x08005629|Start counter, configure10us top; ignores start result; prints on set-top error; returns void|
| matrixEnd |0x08005694|0x08005695|Dispatches counter stop; void; no blanking|
| matrixGrayscaleWrite |0x08005600|0x08005601|memcpy104 then color=true; void|
| matrixSetGrayscaleBits |0x0800561c|0x0800561d|Single byte store; no validation|

Actual LLEXT objects and syms-dynamic.ld agree on all four addresses.
Disassembly of installed memcpy at0x0801b2d2 shows a byte-copy loop bounded by
the supplied size, here104. Neither fixed write nor grayscale setter allocates,
waits, prints or calls Linux/Bridge. The ISR reads one grayscale byte and advances
its index modulo104. `turnLed` touches internal GPIOF MODER/BSRR and masks modes
for PF0..PF13, so matrix ownership is broader than one abstract framebuffer.

Generated devicetree maps counter_matrix to TIM17@0x40014800,
ordinal233/IRQ71/prescaler4. It is enabled and not deferred. ELF device
`__device_dts_ord_233` is at0x0801c1a8 with nameLED_MATRIX_COUNTER, nonzero native
counter API and nonzero LLEXT export. Named `z_impl_counter_*` symbols are zero;
any future native counter use must retain the installed inline device dispatch,
not assume those zero symbols are callable. Counter start/stop disassembly only
sets/clears CEN and returns0; set-top can reject active alarms and stores callback
plus user_data. Begin passes stack-address user_data, but this specific installed
matrix callback does not dereference that argument.

## Source provenance and evidence

The installed Arduino_LED_Matrix0.1.3 header is7155bytes, SHA256
`8c50c307eed4001789b8162c62fa3d0be20a0d2e969fa7b86a26f9dd284ea595`.
It is byte-identical to the freshly fetched pinned release header. Lines13..18
declare the native C functions; draw directly calls matrixGrayscaleWrite.
The wrapper begin always returns1 regardless of native outcome. The optional
ArduinoGraphics path and known three-word frameHolder/104-pixel conversion path
are not suitable for this adapter; direct native declarations matching the
header avoid pulling in that optional class behavior.

Primary sources are pinned to ArduinoCore-zephyr1.0.0 commit
`79b3f1afdad455f55e4a25030953617152c0227c`:

- [Matrix source](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/loader/matrix.inc#L248),
  saved `P2_matrix_raw/source/official_matrix.inc`,6559bytes, SHA256
  `1ab79675a96c4f98fbfb4019253a1f0ee899bf0ba6a8f988aa59a269f47d8936`.
- [Loader startup](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/loader/main.c#L239),
  saved `official_main.c`,11832bytes, SHA256
  `0b2af678b67a21a10f211538f5c535f0f92fb3ddbf97a302ed22122665f916b8`.
- [Matrix header](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/libraries/Arduino_LED_Matrix/src/Arduino_LED_Matrix.h),
  saved installed and official copies, hash above.

Installed package does not carry loader/matrix.inc at the checked CORE/loader
path. The online loader source is therefore a pinned primary-source comparison;
exact relevant machine-code behaviors were verified independently in the installed
ELF. This does not claim that remote source bytes reproduce the entire ELF.
Normal source startup ends/blank-stops its animation before sketch entry;
P0_installed_debug_contract and P0_matrix_readout_plan preserve prior exact
binary/startup and historical counter evidence. Their prior MCU measurements
are not new runtime evidence for this adapter.

All new raw artifacts are under `P2_matrix_raw/source/`: installed_receipt.json
(exact header/config hashes), official_receipt.json (URLs and hashes),
binary_receipt.json (offline disassembly/dynamic mappings), mask_receipt.json
(CMSIS definitions, devicetree/autoconf, actual LLEXT objects and device ABI).
CMSIS gcc header SHA256 is
`2d24e713d46324c056edce30837bb45fe4d9011c60fa0bc75ee9b87e1090ab44`;
m-profile gcc header SHA256 is
`56241ce5b4798048f84429e28c1949d30bb907155f0b8351cb36aaaa9cbbeabb`.
Their numbered excerpts include __disable_irq, __get/__set_PRIMASK,
__get_CONTROL, __get_IPSR and DMB. Scripts preserve reproduction commands;
all retained offline commands exit0. `readiness_receipt_final.json` adds the
device header/getter definitions and actual readiness export/disassembly.
The earlier `readiness_receipt.json` preserves a harmless offline GDB query for
the absent wrapper export `__llext_sym_device_is_ready`: GDB emitted an error
despite exit0, then the corrected implementation-export query succeeded with
empty stderr. An empty disassembly for wrapper `device_is_ready` likewise is
not implementation evidence; the actual z_impl body is present and inspected.
No tool contacted an MCU debug target. `verification.json` records passing local
hash/header equality and bounded-copy/mask checks, not a runtime test.

## Remaining blockers and next action

Freeze submitted-only semantics and the masked-copy contract, then implement
the real adapter with independent native-call/guard/context/PRIMASK tests and an
inert retained target probe. Do not infer successful initialization from a void
API. Prove no post-setup begin/end/play/text/heap/wait path in the selected binary.
Runtime loader identity/ownership, actual frame orientation/brightness, masked
section duration, matrix ISR interference, full-HAL800us WCET, SC-AJ/F091 and all
physical/human gates remain open. The source-fixed10us requested period is not
an external timing measurement. Rendering never changes motion or sensor facts.
