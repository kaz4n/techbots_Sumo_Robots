# D096 actual application RAM audit

2026-09-23 Asia/Dubai. Read-only source and captured-ELF analysis; the only file
written by this audit is this report. No compile, board command, upload, MCU
operation, firmware edit, capacity/tunable change, or toolchain/core change.
Active P2 software authority is D051/D075/D096; physical acceptance and gates
remain separate. Today's date is the scheduled P0/P1 day in PLAN section 3;
the software exceptions do not constitute those scheduled gate passes.

## Exact failed image and budget

Evidence: `P2_app_runtime_raw/target_compile_01.txt` and
`P2_app_runtime_raw/target_fe65a3ad_bench-default.json`, source aggregate
`fe65a3adcefccd3084a8e9d131baf8bb01902434a5dd54816df46952298a7b89`.
The JSON SHA-256 at inspection was
`44b09ef1421b04fb4430a4d1b972e31f2934ca19829c0716dccdeb7c34a4ae1d`.
Its `records[0]` is the final linked app ELF, 211260 file bytes, SHA-256
`53dbdd21cc620b2641a2d4094fa22990cefbc304f80a7d57e26bda79e0545bc4`.
The target link produced an inspectable ELF; the subsequent size check failed.
This is **not a successful target build or load**. Subsequent source revisions
must receive their own identity and budget.

| Allocated region | Bytes |
|---|---:|
| `.text` | 94756 |
| relocated `.rodata` | 4172 |
| `.data` | 12 |
| `.bss` | 177332 |
| `.exported_sym` | 8 |
| `.init_array` | 48 |
| `.fini_array` | 40 |
| Compiler-counted extension payload | **276368** |
| Fixed LLEXT pool | **262144** |
| Payload deficit before loader overhead | **14224** |

`.llext.rodata.noreloc` is 2137 bytes and is excluded by the installed size
scheme. It is not another 2137-byte RAM-saving opportunity. The full allocated
section sum including it is 278505. Program-file size is not extra RAM to add.
F089/F113 and `P2_memory_loader_budget.md` establish that executable text and
relocated constants share the LLEXT pool with data and loader metadata. The old
D091 measured image and D095's 238628-byte probe cannot certify this different
whole application. Removing exactly 14224 bytes would still leave no loader
overhead/headroom; a new exact loader budget is required after any reduction.

## Retained objects and paths

Addresses below are captured `nm -S -C` values in this relocatable image, not
physical loaded addresses. Constructor aliases and `Serial`/`Monitor` aliases
are counted once.

| Symbol or region | Address | Bytes | Interpretation |
|---|---|---:|---|
| `(anonymous namespace)::runtime` | `0x17238` | 168888 | Actual app owner, including recorder; preserve capacity |
| `(anonymous namespace)::sources` | `0x40618` | 848 | Actual fixed native HAL owners |
| `Serial3`, `Serial2`, `Serial1` | `0x40d90`, `0x415fc`, `0x41e68` | 2156 each; **6468** total | Inherited Arduino serial objects |
| `Monitor` / `Serial` | `0x409f8` | 568 total | Two names for the same Bridge monitor |
| `Bridge` | `0x40c30` | 352 | Inherited singleton |
| `RouterBridge::HCI` and its guard | `0x40968`, `0x17230` | 40 + 4 | Header-instantiated inline object |
| Four `zephyr::arduino::arduino_pins` tables | `0x46c`, `0x69c`, `0x8cc`, `0xafc` | 560 each; **2240** total | Relocated constants retained by four HAL translation units |
| `imu::Acquirer::read(unsigned int)` | `0xccb4` | 268 | Legacy synchronous read kept by setup-fault callback |
| `imu::Bus::acquireMotion()` | `0xeaf8` | 484 | Legacy synchronous runtime acquisition |
| `__loopHook()` | `0x1079c` | 2 | Strong empty override; already resolved |

Recorder payload is still `5001*26 + 4096*8 = 162794` bytes. Runtime minus this
payload is 6094 bytes of owners, metadata, core state and reports; that difference
is not automatically redundant storage. After runtime and sources, `.bss` has
7596 bytes remaining. Serial objects, Monitor, Bridge, HCI and its guard alone
account for 7432 of those bytes. There is no evidence of a second recorder.

**Bridge retention is a concrete dependency chain, not a live call assertion.**
Cached installed source under `P2_dump_raw/native/sources/` shows:

1. `core/cores/arduino/Arduino.h:176` includes `postvariant.h`; the variant
   `postvariant.h:18-21` explicitly forces RouterBridge library discovery.
2. `Arduino_RouterBridge/src/hci.h:161` defines inline `HCI(Bridge)`. The app
   initializer and eight HAL initializers have relocation references to this
   object and `Bridge`, even for an unused native dump translation unit.
3. `singletons.cpp:18-19` constructs Bridge and Monitor together. The actual
   ELF relocation at `.text+0x15fbc` resolves the configured transport to
   **Serial2**; do not use the source's fallback `Serial1` as the compiled fact.
4. `core/cores/arduino/zephyrSerial.cpp:190-192` defines all DT serial instances
   together. Its retained 124-byte initializer constructs all three globals.
   Monitor's 36-byte vtable retains read/write/RPC methods.

In `records[0].sizes.stdout`, unioning symbol byte ranges (so aliases are not
double-counted) gives 13402 text + 530 static bytes for names matching
`Rpc|RPC|Bridge|arduino::msgpack`; `arduino::ZephyrSerial|^Serial[123]$` adds
942 text + 6520 static bytes, and the Monitor/Serial object adds 568 bytes.
This **21962-byte named cohort** is an attribution figure, not proven removable
space. Shared dependencies and additional unnamed/standard-library code mean
only an exact new link can establish a saving. Notable retained bodies include
`RpcUtils::detail::unpackObject` 1228 B, `BridgeMonitor<512>::operator bool`
1076 B, and its buffer `write` 912 B. No app source intentionally calls them.
Their presence does not establish execution or motor command acceptance.

The old weak-hook hazard is not the current memory root: `src/hal/loop_hook.cpp`
already produces strong `T`, a single `bx lr`. Deleting or changing it would
reopen a solved timing dependency without addressing the singleton roots.

## Ranked reduction opportunities

1. **Largest potential: remove inherited Bridge dependency roots.** Narrow
   native HAL headers to the exact installed declarations they use and inspect
   sketch preprocessing/library discovery separately. Preserve the strong hook,
   native clock semantics, checked GPIO/ADC/I2C/PWM APIs and all startup behavior.
   Simply omitting explicit Bridge calls, suppressing HCI in one source file, or
   defining an installed private header guard does **not** prove that library
   discovery or `singletons.cpp` stops retaining its initializer. The `.ino`
   Arduino include and every compiled TU matter. No complete supported
   source-only removal mechanism is established by this captured ELF. First
   require an isolated compile-only dependency/init-array comparison; do not
   patch installed libraries/core, replace startup, invent a build mode or claim
   the full 21962 bytes in advance.
2. **Straightforward structural opportunity: share the generated pin table.**
   One bounded repository-owned accessor may replace four local references to
   the installed table while keeping every DT-derived pad/flag/PWM identity and
   validation unchanged. Three duplicate 560-byte tables give a gross **1680 B**
   opportunity, less accessor code/alignment. Prove all relevant pin entries and
   invalid indices through existing native fixtures; verify exactly one table
   in the new ELF. Never substitute a handwritten pin map. This cannot alone
   close the deficit and adds calls on time-sensitive paths, requiring timing
   review.
3. **Smallest and most independently testable: stop using a synchronous reader
   to fetch a latched setup fault.** `src/app/native_sources_unoq.cpp:45-46`
   invokes `imu_.read(t)`. `Runtime::setupImuFault` calls it only after the
   actual setup state is FAULT. `Acquirer::start/advanceSetup` have already
   latched the complete failure; `Acquirer::read` then returns `result_` through
   its faulted branch. That call retains the full 268-byte reader and 484-byte
   `Bus::acquireMotion` path. A const latched-sample accessor can remove this
   app dependency while preserving the legacy API for its existing callers.
   Gross direct opportunity: **752 text bytes**, subject to actual linking and
   new accessor code. Do not count `Bus::transfer` or the 28-byte `readMotion`
   wrapper: the 48-step setup still needs synchronous register/motion calls.

Do not prioritize shrinking numeric/glyph tables: the 576-byte `imu::STEPS`
symbol is at `0x11d4`, inside the already excluded no-relocation region. Nor
does this audit support removing UI, changing numerical precision, lowering
recorder capacity/rate, weakening validation, or deleting established tests.

## Proposed next bounded fix and acceptance

Take opportunity 3 first as a small source-only dependency correction; retain
the larger Bridge investigation as the likely route to meaningful headroom.
Specify a const accessor returning the existing latched `Sample` and bind only
the setup-failure callback to it. No fault field, timestamp, sequence, bus status,
cleanup evidence or setup call order may change. Preserve legacy `read` and its
mixed-API cancellation behavior unchanged.

Independently test setup faults from both `start` and `advanceSetup`, exact sample
field equality, repeated passive reads, and zero new bus/clock/native operations.
Run affected acquisition/native binding tests and the full established safety
regression suite. Compile the same actual app in the same default mode without
upload; retain source hashes and all ELF sections, symbols, relocations and init
arrays. Verify the two legacy runtime symbols disappear from the app while setup
register/motion paths remain; measure the actual net difference. Report any
remaining oversize result as a failure, then independently test the next option.
No host test, compiler fit or projected saving establishes loaded free RAM, full
800-us execution, physical sensor acceptance, motor-run authority or a phase gate.
