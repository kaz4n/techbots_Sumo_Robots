# P0 QTR-style diagnostic exact binary audit — 2026-09-23

Result: **PASS for the exact final default-startup binary and source identity
below; no open binary finding.** This is an offline artifact audit, not an upload,
GPIO measurement, real QTR qualification, R4 timing acceptance or phase gate.
The neutral INPUT and diagnostic-only INPUT_PULLUP datasets remain separate.
No MCU connection, memory/peripheral read, debug target, reset, upload or pin
operation was performed by this audit. Only this report was added; code,
configuration, shared state and capture constants belong to the coordinator.

## Exact candidate and provenance

Inspected only after `P0_qtr_target_compile_final_20260923.txt` recorded successful
compile-only completion: 76,924 program bytes, 45,896 global bytes, 216,248 bytes
remaining; MATCH=0, MOTORS_ALLOWED=0, STARTUP=default. Local time was
2026-09-23 02:55 Dubai during the final receipt check.

The sole approved source aggregate is
`61d7a2d00ec1e7f1782d0a7439bd71cb123338dc1073e55abe43b9c6e3fe521e`.
Earlier fb4248d9, 016896c1 and 23fb81e6 candidates are superseded and receive no
approval from this report. In particular the final image no longer calls micros
or writes end_us when an acquisition outcome fails.

Paths used below:

- S = `/home/arduino/sumox26-build/61d7a2d00ec1e7f1782d0a7439bd71cb123338dc1073e55abe43b9c6e3fe521e/p0_qtr`
- B = `S/artifacts/bench-default`
- C = `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- E = `C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- T = `/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

All 26 staged files under S, excluding generated artifacts, were independently
read and hashed. Each matched its corresponding local `build/stage/p0_qtr`
file. SHA-256 over sorted relative POSIX path + NUL + file bytes equals the
61d7 aggregate above. This is a complete map check, not a check of the sketch
alone. The staged unused core sources are included in that identity.

| Relevant staged source | SHA-256 |
|---|---|
| p0_qtr.ino | `6b8c72b04ca7acdb81c4ade58b9edafce0d1bd72c7fb467126888538702d5c06` |
| src/config.h | `b0115938d72162a8f765e372d71fe688bc5070b8462c209326f930acabc12ee3` |
| src/qtr_capture.h | `f11d4fc816155202389a50c499043c632a5867973ee94e59d2f8a725fbfcc745` |
| src/qtr_ready.cpp | `9df2d1c91a0d9879ebb7ba4b29389eb95126defb00794a13f0d2e6be549d5b64` |

## Artifact hashes, wrapping and exact debug equivalence

| File under B | Bytes | SHA-256 |
|---|---:|---|
| p0_qtr.ino.elf | 76924 | `080142c992024089255c0ced50904bb0ef4a6f41a7caf748ddecfcde625d1077` |
| p0_qtr.ino.elf-zsk.bin | 76924 | `46d305b50bd71f8f48aa8fb97a8f71d5faff1faa032dad1db123c1b62d93e632` |
| p0_qtr.ino_debug.elf | 1429120 | `ad7ec53bcd26613225c2454c15671c64f157eea44738998af2771600c4dad83c` |
| p0_qtr.ino.bin | 44404 | `78f0d4df49d0329b7a52a6996f01b661511db3ddb9b839145b021d299fe5aa38` |
| p0_qtr.ino.bin-zsk.bin | 44420 | `1678cf73e763a33e70502754b237cc6e0cbe8e75fe5eb17f3a4b346c63c6954b` |
| p0_qtr.ino.map | 989886 | `31427ad93409331d4ab5c4d4b3b9b919be5c25e7d4cce70b615e0f7f8b1a938b` |

Default startup uses the **wrapped relocatable ELF** `p0_qtr.ino.elf-zsk.bin`,
not the raw BIN wrapper. Installed platform.txt:68–70,164–165,197–198 and
boards.txt:54–63,161 establish the default dynamic recipe versus the static
override and destination 0x08100000. Their freshly rechecked hashes are:

- platform.txt: `d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638`
- boards.txt: `bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84`

The wrapped ELF is the same length as the ELF. Its first 16 bytes are
`7f454c46010101017c2c010041230000`; bytes 16 through 76923 are exactly identical
to the final ELF. The little-endian size field is 76924. The raw BIN wrapper
instead prepends `000000000000000184ad000041230000`, and its remaining 44404
bytes equal the raw BIN. These were direct byte comparisons on this candidate.

The final ELF is little-endian ELF32 ARM ET_REL, entry 0x48c9, with no program
headers. The following eight allocated sections have identical type, flags,
address, size and alignment in debug and final ELF, and identical contents
for every file-backed section: .rodata (1496), .llext.rodata.noreloc (1188),
.text (22376), .data (12), .bss (21980, NOBITS), .exported_sym (8),
.init_array (16), .fini_array (8).

Every final relocation also matches the debug ELF after normalizing symbol
indices to name/value/size/info/other/section: .rel.rodata 244 entries,
.rel.text 877, .rel.data 3, .rel.exported_sym 2, .rel.init_array 4,
.rel.fini_array 2. Thus the disassembly observations below apply to the actual
final linked image, including its relocations, rather than merely a similarly
named debug file.

## Capture layout and bounds

| ELF property | Exact final value |
|---|---|
| .bss section index/type | 9 / SHT_NOBITS |
| .bss sh_addr | 0x5778 = 22392 |
| .bss sh_size | 0x55dc = 21980 |
| .bss alignment | 8 |
| p0Qtr readelf st_value | **4, relative to section 9** |
| p0Qtr size/type/binding | 14424 / OBJECT / GLOBAL |
| p0Qtr nm display | 0x577c = section sh_addr + 4 |
| Header/sample/count | 24 bytes / 72 bytes / 200 |

Raw readelf row: `985: 00000004 14424 OBJECT GLOBAL DEFAULT 9 p0Qtr`.
The record occupies BSS-relative interval [4,14428), within 21980 bytes.
Do not subtract sh_addr from readelf's already-relative value 4. One 14424-byte
record read fits the existing 16384-byte passive-read bound. The actual runtime
BSS base must still come from validated deployed LLEXT identity; 0x5778 and
0x577c are not standalone MCU RAM addresses. Source static assertions at
qtr_capture.h:40–41 agree with this linked object.

## Final pin table, readiness and owners

Final `.llext.rodata.noreloc+0xe4` holds the 16-byte P0_QTR_PINS array
`02000000040000000700000008000000`. Actual Arduino pin entries are 8-byte
gpio_dt_spec records in the 560-byte arduino_pins object at .rodata+0x88.
Relocations and encoded pin/flag fields give:

| Arduino index | Table offset | Port relocation | Encoded pin / dt_flags | Pad |
|---:|---:|---|---|---|
| 2 | .rodata+0x98 | __device_dts_ord_90 | 3 / 0 | PB3 |
| 4 | .rodata+0xa8 | __device_dts_ord_89 | 12 / 0 | PA12 |
| 7 | .rodata+0xc0 | __device_dts_ord_90 | 2 / 0 | PB2 |
| 8 | .rodata+0xc8 | __device_dts_ord_90 | 4 / 0 | PB4 |

`p0::qtrReadyMask` at .text+0x2808 calls existing device readiness twice and
combines A into bit0 and B into bit1. Relocations +0x281c/+0x2820/+0x2824 target
z_impl_device_is_ready / ordinal89 / ordinal90. The installed loader exports
are nonzero: readiness Thumb0x08019e6f, GPIOA0x0801c064, GPIOB0x0801c040;
shared native GPIO driver API0x0801c6e0. No device initialization or register
operation is added to the readiness path.

The installed source/native ownership evidence is in
[P0_qtr_bare_contract_audit_20260923.md](P0_qtr_bare_contract_audit_20260923.md),
including source lines and DT declarations. E was freshly rehashed as
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`, unchanged
from that audit and the exact GPIO native-path audit.

Those verified installed facts remain applicable to the final imports:
proposed motor pads PB0/PA11/PB1/PB8/PB9 do not overlap; default core console
PB6/PB7 and internal UART PG5–PG8 do not overlap. PWM2/PWM3/PWM8 and CAN
candidates that can share the QTR pads are deferred; their relevant default
pin selections do not establish an active owner. USB PA12 is disabled.
The PB3/PB4 SWJ DT defaults do not establish active SWO/JTAG software ownership:
PM and relevant tracing are disabled and the corresponding SWJ power-management
implementation is absent; internal SWD uses PA13/PA14. GPIO configuration
replaces alternate-function mode on these pads. No competing owner is introduced
by this sketch's actual constructor/main/hook paths below.

This is a package/image ownership conclusion, not a reading of live pad mux
registers or proof of unknown external wiring. Deployed loader/image identity
must be compared before relying on it for the separate measurement.

## Setup-only acquisition in actual linked instructions

Offsets in this section are relative to .text, not live MCU addresses. Source
anchors refer to final `bench/p0_qtr/p0_qtr.ino`, hash above.

| Final routine | Offset / size | Verified behavior |
|---|---|---|
| charge | 0x6c / 68 | Default CHARGE_GUARD; at most4096 micros iterations; unsigned duration fault before success; measured duration >10, hence >=11us; final allowed iteration can succeed |
| observe | 0xb0 / 220 | At most4096 complete passes, four actual digitalRead calls each; common end-pass micros; clock-fault then level-validity checks; sticky first-LOW times; deadline before ALL_LOW and before guard exhaustion |
| acquire | 0x18c / 172 | Four OUTPUT/HIGH pairs, post-last-write charge start; four INPUT or diagnostic INPUT_PULLUP releases, post-last-release observation start |
| measureSample | 0x238 / 160 | Fixed initialized sample, UINT32_MAX unseen sentinels; overhead and start clocks; exactly four final INPUT attempts even after an overhead/acquisition fault; cleanup and total duration validation |
| storeSample | 0x2d8 / 100 | Writes all18 sample fields at stride72 after header24, then publishes completed=index+1 |
| setup | 0x33c / 112 | version1, readiness3 guard, 100 neutral then100 pull-up samples, failure return with record retained, completion/end only after200 successful acquisition outcomes |
| loop | 0x3ac / 2 | Immediate return; no GPIO or record mutation |

Concrete control-flow observations:

- setup compares readiness to3 at0x350 and returns at0x390 if unequal, before
  its start micros call0x356 or any sample/pin call (source:144–150).
- setup divides sample index by100 at0x366; measure/store calls are0x36a/0x370.
  Outcome check0x374–0x378 accepts only1/2 and returns on failure. There is
  **no failed-acquisition end timestamp call/store**. Only after index reaches
  200 does micros0x380 run. End span must be <2^31; end_us/complete stores are
  0x38c/0x38e. An ambiguous overall span leaves both unpublished (source:151–163).
- charge's elapsed comparison against10 branches back when <=10; guard4096
  is considered only after fault/success checks. This is the frozen11us reported
  floor, not the insufficient stock delayMicroseconds(10) path (source:24–37).
- observe calls digitalRead at0xe6 four times before its clock call0x106;
  invalid earlier levels do not skip later pin calls. Newly observed LOWs are
  assigned that shared end-pass timestamp, including LOW on the final/late
  deadline pass. Deadline comparison at0x148–0x150 precedes ALL_LOW at0x15e.
  timeout_mask is complement of the sticky four-bit low mask only on DEADLINE.
  CLOCK_FAULT precedes BAD_LEVEL; guard is considered last (source:40–74).
- cleanup is a four-pin INPUT loop regardless of a started sample's failure;
  each increments cleanup_calls. The final clock validates cleanup_us and
  total_us, and a clock fault supersedes the acquisition outcome (source:96–119).
- Fixed bounds are 200 samples, four pins, and4096 charge/poll iterations.
  No application allocation, delay, application interrupt-masking, transport,
  I2C, Serial begin, motor call, or unbounded measurement loop is in this path.
  Finite application counts still assume each selected native call returns and
  the scheduler eventually runs the thread; they are not a measured WCET bound.

The linked pinMode path0x49b8 selects INPUT=0x10000, INPUT_PULLUP=0x10010,
OUTPUT-initial-LOW=0x60000 and the native configure API. digitalWrite0x49f8
uses the native set/clear slots; digitalRead0x4a34 uses raw native read then
inversion/masking. This agrees with the installed finite pad configuration,
set/clear/read paths documented in the source audit. INPUT clears pull selection.
Readiness proves initialized controllers; it does not prove each write succeeded.
The Arduino wrappers discard configuration/write errors and mask negative native
read errors as LOW. Consequently cleanup_calls records attempts, and BAD_LEVEL
cannot reveal every possible native failure. These are contract limitations,
not newly claimed electrical verification.

## Clock and startup dependency closure

Final micros0x4a80 is28 bytes. It actually calls sys_clock_cycle_get_64
**twice** at0x4a84 and0x4a86, then divides the second result by160 via
__aeabi_uldivmod at0x4a8e. Its imports are at0x4a94 and0x4a98. This compiler
output is byte/relative-relocation identical to the prior GPIO diagnostic.
It provides the existing integer-us clock under the installed160MHz configuration;
the first native call is redundant but finite, and remains part of measured cost.

The sys_clock_cycle_get_64 export is Thumb0x080103d5; the previously inspected
native body0x080103d4–0x08010400 has finite SysTick sampling with bounded
BASEPRI masking/restoration. Thus the application's no-masking rule does not
assert that installed micros never briefly masks kernel interrupts. The final
__aeabi_uldivmod wrapper at0x48a4 resolves through the nonzero packaged export
at0x0801cbc8 to Thumb0x08001365. Native __aeabi_uldivmod0x08001364 and
__udivmoddi4 at0x08001458–0x08001710 were re-read offline. Constant nonzero
divisor160 bypasses divide-by-zero handling; the selected division paths are
finite arithmetic with bounded correction branches, no service/transport wait.

The11us measured charge floor accounts for sub-microsecond timestamp
quantization when requiring a10us charge. A1500us reported observation deadline
has the documented sub-microsecond quantization uncertainty; it does not prove
exactly1500us of physical time or continuous electrical HIGH between polls.

Actual .init_array targets and effects:

| Target | Effect in this image |
|---|---|
| 0x27c0 _GLOBAL__sub_I_p0Qtr | RouterBridge HCI guard/reference and empty fixed state; no GPIO or capture write despite the name |
| 0x446c _GLOBAL__sub_I_Bridge | Fixed references/scalars/buffers; zeroes mutexes, including Bridge+0x38, and started+0x158 at0x44d4; no begin/worker |
| 0x4e64 Serial constructor | Serial1/2/3 device references and six fixed buffers; helper0x4e38 initializes semaphore/indices; no UART begin |
| 0x5648 error-category constructor | Destructor registration; local __cxa_atexit0x4548 returns0 |

initVariant0x48c4 is an immediate return. main0x48c8 calls initVariant,
start_static_threads, setup, then loop and the selected loop hook; there is no
SerialUSB.begin in actual main. Static-thread start/end symbols both have
value0 in the empty .static_thread_data_area, so that range adds no worker.

The selected weak __loopHook0x277c is RouterBridge's68-byte implementation,
not the empty core hook. It yields, locks Bridge+0x38 with K_FOREVER, reads
started+0x158, unlocks and calls update_safe only if started. Exact constructors
set started false, leave the mutex zeroed, and introduce no competing Bridge
thread. No sketch begin call changes this. The hook executes after setup's
measurement window; its inactive branch does not call the transport update.

For the hook, Bridge constructor, Serial constructor, error-category constructor,
initVariant, main, start_static_threads, micros and division wrapper, byte strings
and relative relocation offset/type/target-name sequences match the previously
audited exact GPIO image. The common loader was independently rehashed. The
native zeroed/uncontended mutex fast-path proof in
[P0_gpio_binary_audit_20260923.md](P0_gpio_binary_audit_20260923.md) therefore
applies: lock0x08010b48 takes count0 path0x08010b86–0x08010b9c and unlock
0x08010c2c accepts the null queue at0x08010c78–0x08010c7a and returns. Exported
yield/lock/unlock are Thumb0x080119e5/0x08010b49/0x08010c2d. This is an
image-specific inactive/uncontended argument, not a general mutex-initialization
pattern or a bound under concurrency. Starting Bridge, adding owners or changing
linked code invalidates it. Loader boot handshake/matrix activity is separate;
whole-board boot is not asserted to have zero I/O.

## Reproduction, limitations and next acceptance

Used existing ADB serial2629958581 through tools.board_tool.remote, with
SUMO_TRANSPORT=adb and the installed Windows adb32.0.0 executable. Remote
Python used pathlib/hashlib/struct and T readelf/nm/objdump; any GDB inspection
was offline on E without target, run or call. Final-file reads and subprocesses
completed successfully. All final artifact comparisons above were performed
after the final successful receipt; no earlier candidate substitutes for them.

The setup-only finite diagnostic can record a genuine all-four-polled-HIGH
1500us timeout with the separately labeled internal-pull-up stimulus. Actual
stimulus acceptance still requires the record: DEADLINE, low_mask0,
timeout_mask15, unseen first-LOW sentinels, and the specified timestamps/counts
and cleanup attempts. Disconnected neutral INPUT has no guaranteed level and
need not time out. Neither dataset validates real QTR discharge, freshness,
production HAL semantics, physical wiring or R4. SC-B remains open.

The next separate authorized acceptance step must use the exact default artifact,
compare deployed loader and all76924 wrapped-ELF bytes, validate LLEXT/BSS
identity and bounds, then obtain two identical complete records without rerunning
or rewriting the diagnostic. Failed/incomplete readiness, stimulus or acquisition
records remain failures. This audit supplies no measurement, upload result,
motor authority, PINMAP approval or human phase gate.
