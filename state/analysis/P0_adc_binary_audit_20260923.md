# P0 ADC exact target binary audit — 2026-09-23

Result: **PASS for D-063's inert, setup-only diagnostic; no open BLOCKER,
MAJOR or MINOR finding in this scope.** Source and packaged artifact inspection
only. No MCU target connection, live memory/register read, peripheral function
execution, upload, reset or device write occurred. This is not ADC liveness,
accuracy, runtime WCET, deployed-image identity or phase-gate evidence.

The reported target compile succeeded before this audit. I independently read
its exact files, recomputed the 25 staged source files' aggregate and obtained
`f5f637b2f0799a3b08d9c4c1897c6706842e0a5ffd737e355d409ed881989c1c`.
The aggregate uses sorted relative POSIX filenames plus NUL plus file bytes,
excluding the generated `artifacts` subtree, matching tools/board_tool.py.

## Exact identity and capture layout

`B=/home/arduino/sumox26-build/f5f637b2f0799a3b08d9c4c1897c6706842e0a5ffd737e355d409ed881989c1c/p0_adc/artifacts/bench-default`.
All artifact filenames in this table are relative to B.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| p0_adc.ino.elf | 74636 | a8e02489b14145f06312db3578e3349033e8b07e732beb5baeebcb8ea3a66683 |
| **p0_adc.ino.elf-zsk.bin — dynamic/default upload artifact** | **74636** | **2cff4f0635d45c2d75c75c6b0f96444d7e28fec088973835b7b4038061d84fba** |
| p0_adc.ino_debug.elf | 1415772 | 0dae70ddc0e78be8c57695417ad35a716426d901f3013ab2fb2c497e9f246a6a |
| p0_adc.ino.bin | 41356 | 2ea9feadd00d97d0aa67a0d6c5946c9131e9a531ab194a378d8482a2d8aa838c |
| p0_adc.ino.bin-zsk.bin — separate output, not default upload | 41372 | e89ad70386df16f835f97513112143e906646229ff1061a1e302dd8356dc4386 |
| p0_adc.ino.map | 996116 | 0e7378934a90eda7e5eaee15adaa7d2916687769991a90ead847ae478ac01a27 |

Use final `.ino.elf` readelf symbols, not an nm display address, for RAM offsets:

| Item | Exact value |
|---|---|
| ELF class/type/machine | ELF32, little-endian, ET_REL, ARM |
| .bss section index/type | 9 / NOBITS |
| .bss size/alignment | 0x4c74 = **19572 bytes** / 8 |
| p0Adc section-relative st_value/size | **0x4 / 12020 bytes** |
| Record range within BSS | [4,12024), fully inside [0,19572) |
| .static_thread_data_area size | 0 |
| .init_array size/entries | 16 bytes / 4 |

These are offsets in the dynamically allocated sketch BSS, not physical RAM
addresses. Resolve and validate the live LLEXT/BSS identity only through the
separately reviewed passive capture. Frozen-record reads are 12020 bytes each;
do not accidentally request the entire 19572-byte BSS through a helper whose
per-RAM-read limit is 16384 bytes.

### Correct upload file and wrapper

Installed `platform.txt`:68–70 sets dynamic link, wait boot, and
`upload.extension=elf-zsk.bin`; :197–198 selects
`{build.project_name}.{upload.extension}` as the sketch artifact. Its postcopy
hooks :164–165 emit **both** wrapped ELF and wrapped raw binary. `boards.txt`:
54–63 changes the extension to `bin-zsk.bin` only for the static option;
:161 sets sketch flash address 0x08100000. No static/Immediate option belongs
to this reviewed default build. SHA-256 of installed platform.txt:
`d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638`;
boards.txt: `bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84`.

The correct wrapped ELF's first 16 bytes are
`7f454c46010101018c23010041230000`: version 1 at offset 7, length 74636 at 8,
magic 0x2341 at 12 and flags **0** at 14. These match the
[release loader header](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/loader/main.c)
:27–39, :162–163, :239 and :284: not prelinked, not Immediate, not wait-for-app.
The loader source was read as versioned primary material; installed loader
identity still depends on its hash and later passive flash comparison.

The wrapped ELF and final ELF have equal lengths and are byte-identical from
offset 16 onward; changed offsets are only 7,8,9,10,12,13. The separate raw
`.bin-zsk.bin` instead prepends a 16-byte header. An interim message called that
41372-byte file an upload binary before checking the recipe; this was corrected
before capture pinning. **Pin the 74636-byte `.elf-zsk.bin` above.**

## Setup and ADC call path

All following sketch code offsets refer to `.text`; low-bit Thumb symbol values
are one greater than instruction addresses. Debug and final `.rodata`,
`.llext.rodata.noreloc`, `.text`, `.data`, `.exported_sym`, `.init_array` and
`.fini_array` bytes were compared and are identical. Their relocation tuples
(offset, type, target name/value/section) also match: text 860, rodata 180,
data 3, exported 2, init 4 and fini 2 entries. Thus the debug disassembly describes
the code and relocation semantics of the final image. `.text` SHA-256:
`c30467e23a8eb9cb13c40cbf158f76db735df80ac0962c1ff36e1522314a146a`.

- `setup` 0x6c–0xcc writes version=1 and start time, then uses four micros reads
  per sample and one raw ADC call. At 0x90 it passes **14**; the 0xcc literal
  relocation targets analogRead. This is the **only analogRead relocation**.
  The loop compares against **1000** at 0xa6. Stores at 0xaa/0xac/0xae preserve
  overhead, elapsed and the full signed 32-bit return; 0xb2 publishes completed
  only afterward. The final time and complete=1 are written at 0xba/0xbc.
  No pre-init or discarded warmup call precedes sample 0. `loop` at 0xd0 is
  `bx lr`, with no record write or ADC call.
- `analogRead` at 0x4694 selects table index 0 for pin 14 (0x46a6/0x473a),
  initializes/applies only that channel's pinctrl at 0x46e8, then dispatches
  through device API entries directly: setup at 0x46f4 and read at 0x4716.
  Both negative returns propagate. The raw sample is loaded unsigned at
  0x4724 and shifted to the configured output width. `.data+4` is 10; the
  first ADC table entry has channel 9 and 14-bit resolution. The ignored
  pinctrl-helper result and unbounded installed driver paths remain exactly
  the limitations in P0_adc_installed_contract_20260923.md.
- `.rodata+0x0` through +0x50 have six ADC1 device relocations, and +0xd0 has
  its pinctrl-map relocation. Offline packaged-loader GDB confirms
  `__llext_sym___device_dts_ord_17.addr=0x0801c238`, device API 0x0801c5f4,
  channel_setup 0x080098f9 and read 0x08009ce5. Device init, device readiness,
  pinctrl lookup/configuration exports are respectively 0x08019e5d,
  0x08019e6f, 0x08019613 and 0x08019637, all nonzero. There is **no sketch
  relocation to the null z_impl_adc_read or z_impl_adc_read_async exports**.
- Pin restoration helper 0x486c–0x48e8 checks readiness, calls device_init only
  if necessary, selects state 2 and calls pinctrl_configure_pins with count 1.
  A0 remains the established PA4 ADC input; no GPIO output, motor, PWM or
  matrix operation is introduced by this sketch path. Merely linking pinctrl
  table entries for other devices does not initialize them.

## Startup, constructors and selected loop hook

The final main at 0x45d0 calls initVariant (0x45cc, immediate return),
start_static_threads, setup, then loop and the resolved __loopHook repeatedly.
There is no SerialUSB.begin call in this main. Both static-thread list symbols
belong to the zero-byte section, so this sketch defines no static worker.
The four actual constructor targets are:

| Offset | Inspected effect |
|---|---|
| 0x24e8 | HCI reference/guard and empty fixed initial state; despite its p0Adc-derived name, no ADC call or record mutation |
| 0x4174 | Bridge/Monitor references, scalar zeroing and fixed buffer memset; Bridge.started at +0x158 is zeroed explicitly at 0x41dc |
| 0x4cc4 | Serial1/2/3 references and fixed buffer/semaphore construction; buffer helper 0x4c98 initializes semaphore and indices, no UART begin |
| 0x53c4 | Error-category destructor registration through __aeabi_atexit; its target __cxa_atexit at 0x4250 simply returns zero |

No constructor starts Bridge, a UART, ADC, GPIO output or a motor. No
BridgeClass::begin/updateEntryPoint symbol exists in this image; Monitor and
Serial vtable-linked methods are present but are not called from startup/setup.
The loader's existing default Linux handshake/boot animation precedes sketch
entry and is not a claim of zero hardware activity across the whole boot.

The selected weak **__loopHook at 0x24a4 is the RouterBridge hook**, not the core's
empty hook. Its exact 68-byte code calls k_yield, takes Bridge+0x38 mutex with
K_FOREVER, reads started at +0x158, unlocks and calls update_safe only if started.
The constructor above leaves started false and the mutex storage zero; no
concurrent Bridge worker or begin call can change that in the reviewed image.
This is the same mechanism as the previous timing audit, but it was checked
again on these exact code offsets and relocation targets.

Packaged loader mutex code was independently re-read: lock 0x08010b48 tests
lock_count at +12 and uses the zero-count immediate path
0x08010b86–0x08010b9c; unlock 0x08010c2c treats the null queue at
0x08010c78–0x08010c7a as empty, clears owner/count and returns. Export records
for lock/unlock/yield are nonzero. Thus the exact uncontended hook performs no
Linux wait, transport start or peripheral write. The unusual zeroed mutex
initialization is an upstream, image-specific caveat, not a generic approved
mutex pattern. This proof does not permit starting Bridge later or generalize
to concurrency, other library versions or bounded scheduler timing. The hook
also runs only **after** setup, outside this diagnostic's measurement window.

## Evidence method and remaining limits

Exact-device ADB transport/environment and package/tool roots are those recorded
in P0_adc_installed_contract_20260923.md. Every remote command here returned 0:
`tools.board_tool.remote('2629958581',['python3','-c',PROGRAM],capture=True,
timeout=30..45)`; Python used read-only Path/struct/hashlib and subprocess calls
to installed `arm-zephyr-eabi-readelf -hSW/-sW/-rW`, `nm -nC`,
`objdump -drC --start-address=... --stop-address=...`, and offline
`gdb -nx -nh -batch ELF -ex 'p SYMBOL'`. Loader mutex disassembly used
`objdump -d --start-address=0x08010b48 --stop-address=0x08010cb8`.
No debugger target, process launch or function call was requested in GDB.

Packaged loader ELF SHA-256 was rechecked:
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
It must still match deployed bytes before relying on these addresses. Subsequent
capture must also match **all 74636 wrapped-ELF bytes**, resolve the current
sketch's BSS, and validate two identical complete records. Actual readiness,
successful 1000-call completion, error-free values and elapsed statistics have
not been observed by this audit. Incomplete setup remains an expected explicit
failed measurement outcome, not a reason to infer or silently introduce a
timeout, reset, production HAL, pin acceptance or phase gate.
