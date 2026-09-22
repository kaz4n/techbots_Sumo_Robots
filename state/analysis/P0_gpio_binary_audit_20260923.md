# P0 GPIO exact target binary audit — 2026-09-23

Result: **PASS for the D-064 internal LED diagnostic; no open BLOCKER, MAJOR,
or MINOR finding in this scope.** Read-only inspection of staged source,
installed headers/ELF and exact compiled artifacts. No MCU connection,
execution, live memory/register read, upload, reset, or peripheral operation
was performed. Actual readiness, readbacks, timing and deployed identity remain
for the separately reviewed capture. This is not robot GPIO/HAL acceptance,
physical pin-map approval, optical verification, WCET proof or a phase gate.

## Artifact identity and capture layout

`S=/home/arduino/sumox26-build/1dfbd5711114e699fec324bcc0b97de7defd37889b5dc81c824dcde69be93dda/p0_gpio`;
`B=S/artifacts/bench-default`. Filenames below are relative to B.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| p0_gpio.ino.elf | 76148 | `46c135bd8d2385e860dcc86ddf577407da9f205721a4a576e14c984836ac934f` |
| **p0_gpio.ino.elf-zsk.bin — dynamic/default upload** | **76148** | `a0a36e77e467d4a0f02bf59637f40dda3fa60334acd18e7c3c2c7efd2b093828` |
| p0_gpio.ino_debug.elf | 1420404 | `02cf5953472806c861b6e46c770dac6000536e37f160ec6a182c0926348223f7` |
| p0_gpio.ino.bin | 43924 | `cc0e73f8141e31ad4c1368b3098ff6d6af1ff6137c9b29f1c1aa733ab6dea7bb` |
| p0_gpio.ino.bin-zsk.bin — separate wrapped raw output | 43940 | `ab9a1865cbe1034fd19f5dfeafa87bd816e37cee9b2a4faca0b76215d438674b` |
| p0_gpio.ino.map | 988798 | `04a415888a271ebf148a54f183716c67282908ccb997f9438e40ad5b99acc562` |

Exact final `readelf -hSW` and `-sW` observations:

```text
Class: ELF32; Data: little endian; Type: REL; Machine: ARM
Entry point: 0x46e9; program headers: 0
[ 9] .bss NOBITS 00005598 006038 0055dc 00 WA 0 0 8
903: 00000004 14428 OBJECT GLOBAL DEFAULT 9 p0Gpio
```

**Use raw ELF st_value=4 as the BSS-relative record offset.** `nm` displays
0x559c because it adds the section VMA0x5598. Subtracting 0x5598 from
`readelf`'s st_value4 is wrong. Debug ELF is also ET_REL and reports st_value4.
The .bss size is **0x55dc=21980**, alignment8; p0Gpio size is
**0x385c=14428**. Its range [4,14432) lies within BSS and each record read fits
the existing 16384-byte bound. Do not read all21980 bytes as one RAM request.
The .static_thread_data_area section6 is empty; .init_array has16 bytes/four
entries. Live `find_bss` must independently observe size21980 and the same
extension identity before/after capture; this audit did not observe runtime RAM.

Installed core root is
`C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`.
Re-read platform.txt:68–70 selects dynamic, wait, `elf-zsk.bin`; :197–198
selects `{build.project_name}.{upload.extension}`. :164–165 emits both wrapped
files. boards.txt:54–63 changes the upload extension for the static option only;
:161 sets flash address0x08100000. Their SHA-256 values remain
`d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638` and
`bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84`.

Correct wrapped ELF header: `7f454c46010101017429010041230000`.
Version1, length76148, magic0x2341, flags0: dynamic, default Linux wait, no
Immediate/wait-for-app/debug flags. Wrapper/final ELF lengths are equal and
bytes16 onward identical; changed offsets are only7,8,9,10,12,13. The separate
raw wrapper prepends16 bytes, header `0000000000000001a4ab000041230000`.
It is not the reviewed default upload file. Its presence does not establish a
static build; this invocation generated both with the dynamic recipe.

## Debug/final equivalence

Relevant debug/final section bytes match exactly: .rodata1496,
.llext.rodata.noreloc1172, .text21896, .data12, .exported_sym8,
.init_array16, .fini_array8. .text SHA-256 is
`77ee6a5e8e2b850712630071136dccc8f2b1f96d3508868dc4a52f59d130972c`.
ELF32 parsing compared relocation offset/type plus target symbol name, value,
size, binding/type, visibility and section identity, rather than raw symbol
indices. Every relevant set matches: rodata244, text869, data3, exported2,
init4, fini2. The following debug disassembly therefore describes the final
artifact's code and relocation semantics. Addresses below are section-relative
instruction addresses; callable Thumb values add1.

## Readiness, configured pin, and finite setup

- `p0::gpioReady()` at0x2638–0x2646 loads GPIOH and tail-dispatches readiness.
  Relocations .text+0x2640 and +0x2644 target `__device_dts_ord_95` and
  `z_impl_device_is_ready`. Packaged loader exports are nonzero0x0801bf68 and
  0x08019e6f. Re-read native readiness body0x08019e6e–0x08019e82 only checks
  null and initialization state; no stores, calls, waits or device init.
- `setup`0x170–0x1da writes version1, invokes readiness once, and stores ready.
  The false branch at0x182 returns before timing or GPIO calls. It makes no
  LED-off guarantee in this readiness-failure case because it has not touched
  the device. On success it stores start_us and begins the fixed loop.
- `measureSample`0x6c–0xfa passes **50** at each actual GPIO call. It measures
  paired micros overhead, pinMode(OUTPUT), LOW read, HIGH write, HIGH read,
  then contiguous pinMode(OUTPUT)+HIGH write; the final pair read is untimed.
  OUTPUT/HIGH arguments are1. No pre-sample GPIO call discards first-use cost.
  The record preserves all six unsigned intervals and three32-bit readbacks.
- `storeSample`0xfc–0x132 writes all nine fields at record+28+36*index, then
  publishes completed=index+1 at0x12c. `setup` checks LOW/HIGH/pair against
  **0/1/1** after this store. Any mismatch tail-calls finish(false) immediately;
  no later sample or hidden retry occurs. The success loop compares index with
  **400** at0x1b8; its only backedge is that finite count.
- `finishMeasurement`0x134–0x16e writes HIGH to pin50 once more, records a final
  readback and end_us, then sets complete only if success and final_level==1.
  Failure remains complete0. On the normal path there are800 OUTPUT calls,
  801 HIGH writes and1201 digital reads, all on pin50. `loop`0x1dc is `bx lr`;
  the application never updates the record or GPIO after setup.

The compiled table `zephyr::arduino::arduino_pins` begins .rodata+0x88 with
8-byte entries. Entry50 is at+0x218, bytes `000000000a000000`, with its pointer
relocation to ordinal95: GPIOH, pin10, flags0. The other table entries are
linked data, not calls/configuration. All actual diagnostic indices above are50.
This independently completes the named LED macro/PH10 mapping from the source
contract. No header pin, motor, PWM, ADC, matrix, I2C, or Bridge startup call is
introduced by the diagnostic. Final symbol scan finds no MotorGate,
analogWrite, analogRead, matrixBegin, BridgeClass::begin or updateEntryPoint.

`pinMode`0x47d8 selects0x60000 for OUTPUT; its inline helper0x47ac clears the
PH10 inversion bit from flags0 and dispatches api->pin_configure. Installed
GPIOH API at0x0801c6e0 selects configure0x08019151, finite pad routine
0x080178bd, read0x080190bd, set0x080190db and clear0x080190e5. The previously
audited finite configure routines remain in the identical loader image.
`digitalWrite`0x4818 dispatches to API set/clear slots directly;
`digitalRead`0x4854 calls API read, applies inversion and selects0/1.
There is no sketch relocation to the null `z_impl_gpio_*` exports. Direct
native read/set/clear bodies were re-read: IDR load, BSRR store, BRR store,
respectively; no locks, polling or allocation.

OUTPUT therefore establishes physical LOW/red-on; subsequent HIGH is off.
The Arduino wrapper still discards configure/write errors and maps native
read errors to LOW. LOW/HIGH observations are not recovered native error codes
or electrical/optical proof. Ready checks successful device initialization,
not future pin configuration success. Empirical timing remains subject to
interrupts, scheduling and microsecond quantization; no runtime WCET inferred.

## Constructors, static threads and actual loop hook

Final main0x46e8 calls initVariant0x46e4 (return), start_static_threads0x4740,
setup, then loop and the selected hook. No SerialUSB.begin call occurs in this
compiled main. Both static-thread boundary symbols reference the empty
section6 at VMA0x5588, so start_static_threads creates no sketch worker.

| Actual .init_array target | Inspected effect |
|---|---|
| 0x25f0, `_GLOBAL__sub_I_p0Gpio` | RouterBridge HCI reference/guard and empty fixed state; no GPIO call or p0Gpio write despite constructor name |
| 0x428c, `_GLOBAL__sub_I_Bridge` | Fixed reference/scalar/buffer initialization only; zeros Bridge mutex at+0x38 and started at+0x158 (store0x42f4); no Bridge begin/thread |
| 0x4c84, Serial constructor | Serial1/2/3 device references and six fixed buffers; helper0x4c58 initializes semaphore/indices, no UART begin |
| 0x5468, error-category constructor | Destructor registration via __aeabi_atexit; local __cxa_atexit0x4368 simply returns0 |

None initializes a GPIO, transport, motor or peripheral from these constructors.
The installed loader's separate boot handshake/matrix activity remains outside
the diagnostic; this is not a claim that whole-board boot has zero I/O.

The selected weak **__loopHook at0x25ac is RouterBridge's 68-byte hook**, not
the empty core hook. It calls k_yield, locks Bridge+0x38 with K_FOREVER, reads
started+0x158, unlocks, and calls update_safe only if started. The exact
constructor sets started false and leaves a zeroed mutex; no begin or concurrent
Bridge worker exists to change them. This was established from this image's
constructors, main/static-thread section and relocations, not its filename.

The hook, Bridge constructor, Serial constructor, initVariant, main and
start_static_threads additionally compare **byte-for-byte equal**, with equal
relative relocation offset/type/target names, to the exact earlier ADC image
audited in P0_adc_binary_audit_20260923.md. Native mutex bodies were re-read:
lock0x08010b48 takes the count0 immediate path0x08010b86–0x08010b9c; unlock
0x08010c2c accepts null queue at0x08010c78–0x08010c7a, clears owner/count and
returns. Yield/lock/unlock exports are nonzero0x080119e5/0x08010b49/0x08010c2d.
Thus this exact inactive/uncontended hook does not wait for Linux or execute
the transport update branch. It runs after the measured setup window.

The zeroed-mutex behavior is an upstream image-specific caveat, not a general
mutex initialization pattern or proof under concurrency. Starting Bridge,
introducing another owner/thread, changing linked libraries or claiming a
wall-clock scheduler bound invalidates this narrow argument. No such change
is present in the reviewed artifact.

## Complete staged source verification

Independently read **all26** staged source files under S, excluding generated
artifacts. SHA-256 over sorted relative POSIX path + NUL + file bytes equals
`1dfbd5711114e699fec324bcc0b97de7defd37889b5dc81c824dcde69be93dda`, matching
tools/board_tool.py:148–154's source aggregate. Every individual SHA-256 also
matched the corresponding local `build/stage/p0_gpio` file. No compile/upload
or staging mutation was used to obtain this result.

| Relative staged file | SHA-256 |
|---|---|
| p0_gpio.ino | `eac13086262a220d1e6655e217e7b3b7a60c26a2289717f4873f76af97fc75f0` |
| src/config.h | `5447a46697e552f69b887a6fa2d629f73f35f9357ca9fcdc654e60b17c3c802a` |
| src/core/.gitkeep | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| src/core/countdown.cpp | `34558f66b118c8298c0138d62ba4b98437864007935c08fcd9969507c3f1761b` |
| src/core/countdown.h | `1ad9fe88b6a9e368626cccf65701815bfce2c8609c9526ed1dcc68fb72b5f9da` |
| src/core/edge.cpp | `b48df54ad7708ec1776b30edb107fbbed57557b4a218ee1258e42aaec1e75835` |
| src/core/edge.h | `1fb78c92fb46d661272a660a663ef0aaf3aff416dd6e4b329607c0abb9134389` |
| src/core/fsm.cpp | `9334be82f508064e554a322ac7c11be598da73ff49d0cf80fd09dfbf94bc25cb` |
| src/core/fsm.h | `4ffb1cccaf44b21dd49a99892cadbbb6f7e21fc1f2cccbbe11a406cabc6555b9` |
| src/core/fsm_robot.cpp | `206d3d1dd82a3cb3be0eea2187fa1c703443620a5bf4caf03d470e902cab6daa` |
| src/core/governor.cpp | `249259d7230c5e0d033cf3fb3ff938b854a5a0629d22e83c81eee45b29ad2d68` |
| src/core/governor.h | `48174995c9c420a47bda8406774ca2241cb36366c476452aa20ca5169feb5999` |
| src/core/logframe.cpp | `daee8d7fe49d64e1f92102ad68c28817dac15d2481d98dbb1f62d19dfe73ae32` |
| src/core/logframe.h | `4cde17409858ba5e85e610f866537f1687bcea26bb9bb14b405235dd3345515b` |
| src/core/motion.cpp | `c8f4286e42d964275c269b97dca9e00b5d8d55524046a3ed63433ae0e9cb9656` |
| src/core/motion.h | `1d8baa81d23bc794562d9b3f695ba98eacd0a3fedfc3ae0f0b6ad4923d66fb78` |
| src/core/openers.cpp | `d924761e1d4af313530ba57f59949b217f0018915bd31811295d351dc65817b9` |
| src/core/openers.h | `4ef64dc3cddef2ece35070cda6d5099644d89935689289983e37b997f056a1be` |
| src/core/opp_fusion.cpp | `97bb8ed35f3ddfc59a19692da25452aeabf0e1643404f352d6f036bb53cb5be2` |
| src/core/opp_fusion.h | `0afd417533b1186e0a1a9e959655a2d0baa40d04b119075e40e53d864ed25956` |
| src/core/stall.cpp | `46e0f67eb3d3b820150d156eb2a1cae2e074e44c56f98d6ab4b739c837229436` |
| src/core/stall.h | `88accba473a43b04949a30696d968f3aaf308493ef00a9ba16aa40018765b9e3` |
| src/core/types.h | `28067a3e384f07abdd115b686c22b24d9e2789c117b611548ba4570255177dd7` |
| src/gpio_capture.h | `05f4b44214b31799a6afb07c169d06eb43865193fe13b51a4686f39c59ce4da5` |
| src/gpio_ready.cpp | `2ee064a19d5962253efe55aa7b96dc1cf951d32016b200ff79d2febb877559e8` |
| src/hal/.gitkeep | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Reproduction and remaining acceptance

Transport: `tools.board_tool.remote('2629958581',['python3','-c',PROGRAM],
capture=True,timeout=40)`, SUMO_TRANSPORT=adb, SUMO_ADB_SERIAL=2629958581,
SUMO_ADB_EXECUTABLE=
`C:\Users\narut\AppData\Local\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe`.
Every remote Python/subprocess command completed exit0. PROGRAM used pathlib,
hashlib, struct ELF parsing and installed toolchain prefix
`/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`:
`readelf -h/-SW/-sW`, `nm -nC -S`, `objdump -drC` over the cited sketch ranges,
and offline `gdb -nx -nh -batch E -ex 'p SYMBOL'`. No GDB target/run/call command.
Native full-function disassemblies for configure/pad-config/mutex lock/unlock
completed without range truncation; an earlier fixed-range stop cut a trailing
instruction, so full-function output was obtained before completion.

Packaged loader E (`C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`) SHA-256
was rechecked as `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
Native primary-source versions, source hashes, initial LED ownership limits
and header API evidence remain in P0_gpio_installed_contract_20260923.md.
Only this new binary-audit report was written by this task.

Next acceptance requires the reviewed default artifact upload and bounded
passive comparison of deployed loader bytes plus **all76148 bytes of the
wrapped ELF**, then two identical complete records and unchanged LLEXT/BSS
identity. No passed physical result is inferred here. Incomplete readiness,
mismatched readbacks, failed final HIGH readback or incomplete setup must stay
failed measurements; none authorizes retries, resets, another pin, motors,
production HAL changes or a phase gate.
