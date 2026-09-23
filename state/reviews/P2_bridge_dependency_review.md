# D098 independent isolated dependency experiment review

2026-09-23 Asia/Dubai. Separate fresh-context, same-model reviewer. Read-only
source/receipt/ELF review; this agent wrote only this review and its `_raw/`
directory. No board command, build, upload, MCU operation, source/test/tool/package
edit, commit or production policy adoption. AGENTS, active P2, PLAN section 3,
FACTS, D051/D075/D096-D098 and the D090 native dump contract were read. Today is
the scheduled P0/P1 day; software authority does not supply those human gates.

**Disposition: PASS for the bounded D098 investigation.** The isolated candidate
actually compiles, removes the unintended library roots and preserves reviewed
application/native/startup paths. No open BLOCKER/MAJOR/MINOR defect was found in
this experiment. **Production remains target-memory-blocked:** the unchanged
ordinary command still fails, and D098 has not adopted the experimental property.
Compiler fit is not loaded-memory, startup-execution, UART or WCET qualification.

## Identity and controlled change

Both branches compile frozen actual app source
`570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84`
(D097 source, separately reviewed). `experiment_validation.json` independently
reconstructs all 82 source bytes from the repository and their aggregate hash.
The two target collectors enumerate the same 82 source files after compilation,
excluding artifact directories; these exactly match both original run receipts.
The candidate additionally records exact-file-set preflight. Each branch records
an absent output directory and uses its own fresh build/output paths outside the
sketch tree. The baseline's first preflight checked expected files only; its
subsequent enumerated collection and candidate's preflight close that evidence gap.

The normalized command arguments differ only by:

```
--build-property build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0
```

FQBN remains `arduino:zephyr:unoq`; MATCH=0, MOTORS_ALLOWED=0 and default startup
remain. Both generated `app.ino.cpp` files are byte-identical, SHA-256
`b4f05a6e010af374a876085c654597977cae7581efd58a09936af0085d27130f`.
No fake/shadow header, stub, alternative main, loader change, reduced recorder
capacity, altered tunable or dropped application source produces the saving.

The CLI override mechanism is supported. **This particular value is not an
official Bridge-disable feature:** it bypasses the published discovery-phase
semantics. `source_validation.json` checks 33 source-receipt hashes, 43 original
audit-manifest entries and nine pinned primary/installed comparisons. These are
local checks of the saved primary-source receipts, not a new upstream download.

- [Pinned CLI preprocessing](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/internal/preprocessor/gcc.go)
  sets the phase property to 1 before expanding the C++ recipe. Literal flag
  replacement avoids that property substitution.
- [Pinned UNO Q postvariant](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/variants/arduino_uno_q_stm32u585xx/postvariant.h)
  forces RouterBridge discovery at phase 1, but tests header availability at
  phase 0. The installed file matches those pinned bytes.
- [Pinned CLI library handling](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/libraries.go)
  and [RouterBridge metadata](https://github.com/arduino-libraries/Arduino_RouterBridge/blob/0.4.3/library.properties)
  explain direct singleton-object linkage after discovery.

## Actual compiled dependency and behavior comparison

`object_validation.json` independently compares actual captured object-section
byte digests and complete relocation records, not just source names. The control
contains 74 objects; the candidate contains 73. The only omitted object is
`libraries/Arduino_RouterBridge/singletons.cpp.o`. All 1,438 common allocated
sections were checked. Every shared section except `_GLOBAL__sub_I_setup` has
identical content/size/alignment and relocation targets; 2,904 unchanged
relocations were compared. The changed app initializer is reviewed below.

All 244 metadata text payloads match their recorded byte counts and hashes.
The candidate's 73 expanded compile commands preserve the exact default safety
flags. All C/C++ commands use phase 0; the unchanged `tls-syms.S` assembly recipe
does not consume that property. Its 117 dependency files reference none of
RouterBridge, RPClite, MsgPack, DebugLog, ArxTypeTraits or ArxContainer. The normal
control explicitly selects those six installed libraries; the candidate selects
none. Core Serial sources can still be compiled into the archive; their unused
objects are no longer retained in the final candidate image.

`elf_validation.json` independently decodes all six downloaded ELF32/ARM files,
checks their byte counts/hashes against the remote-download and target receipts,
and matches each undefined-symbol set to the captured tool result. Final candidate
ELF SHA-256 is
`9808dc594d77be8f43865a17542a48b715b4d5ee4a1277d6f946d0a6ccb09e65`.

- All 493 retained project function identities remain. The actual Runtime is
  still 168,888 bytes and NativeSources is still 848 bytes. Four original
  DT-derived 560-byte pin tables remain; no hand-written pin map replaces them.
- Bridge, Monitor/Serial aliases, Serial1/2/3, HCI, RPClite/MessagePack and
  ZephyrSerial symbols disappear from the final candidate. Their associated
  init/fini work disappears: 12 init and 10 fini entries become one init entry
  and no fini entries.
- The remaining initializer is `_GLOBAL__sub_I_setup`. Its decoded body and
  relocations initialize the existing sources/storage, call the passive motor
  and source port factories, then construct the actual Runtime. It does not
  start UART/Bridge or remove the required app constructor.
- `main`, `initVariant`, static-thread startup, `setup`, `loop` and the strong
  empty `__loopHook` remain. Main's five relocation targets are exactly
  initVariant, start_static_threads, setup, loop and __loopHook. Main is still
  exported. The strong hook is exactly Thumb `70 47` (`bx lr`).
- Setup still zeroes the 13-byte grant object and calls Runtime.begin; loop
  calls Runtime.step. Their linked instruction bytes match after resolving the
  relocated runtime object at its changed BSS offset. Original-object bytes
  already match exactly. The loader's static-thread range remains empty, with
  start/end both `0x0801c454`; startup execution has not been measured.
- Imports decrease from 188 to 176 with no new import. Removed imports are float
  printf, ring-buffer calls, device_deinit, mutex/semaphore calls and sleep.
  The only removed entry in the native-export subset is `z_impl_device_deinit`.
  All 39 retained native and all 42 unchanged AEABI bindings have recorded
  nonzero loader export addresses. LPUART1 device ordinal 78 remains available.
  Loader SHA-256 remains
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

Reviewer-harness corrections are recorded in the raw JSON: final-linked BSS
addresses require relocation-aware comparison, and the assembly recipe has no
discovery flag. Neither observation required a production change.

## Memory result and its limits

| Actual result | Control | Candidate |
|---|---:|---:|
| Compile exit | 1 | 0 |
| Program storage bytes | 210600 | 153684 |
| Compiler-counted extension payload | 275760 | 248308 |
| Difference from 262144-byte pool | -13616 | 13836 |
| Init / fini entries | 12 / 10 | 1 / 0 |

The measured link reduction is **27,452 bytes**. Candidate payload is
3,748 rodata + 74,768 text + 169,780 BSS + 8 exported-symbol bytes + 4 init bytes.
Its additional 1,433-byte nonrelocated rodata section is not counted as copied
RAM by this source-derived persistent-flash model. There is no data/fini payload.

Independently applying the pinned 32-bit non-Harvard LLEXT allocator model gives:

| Conditional allocation | Chunk bytes |
|---|---:|
| Copied five regions, including alignment/header costs | 248352 |
| Extension object | 200 |
| 15-entry section map | 128 |
| 460-entry temporary global symbol table | 3688 |
| Export copy | 16 |
| Initial heap bookkeeping/footer | 88 |
| Pristine-load peak consumption | **252472** |
| Remaining chunk span / largest payload | **9672 / 9668** |

No merged-region prepadding occurs in this final ELF. At the previously described
persistent flash base `0x08100010`, no-reloc data, symbol/string tables and section
headers meet their peek alignment. This is conditional arithmetic: same pinned
loader/configuration, pristine pool, successful persistent peeks, no additional
constructor/interleaved allocations. It does not measure a load, current free
RAM, fragmentation, stack use, transport growth or a worst-case minimum. The
independent decoder reproduces the earlier D071 reference model as a sanity check.
See the cached pinned sources and assumptions in `P2_memory_loader_budget.md`,
especially [llext_load.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_load.c)
and [llext_mem.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_mem.c).

## Current and future native dependency boundary

The existing source uses Arduino/Zephyr declarations, micros-derived clocks,
DT bindings, GPIO/PWM/ADC/I2C and matrix APIs. It intentionally calls no stock
Bridge/Monitor/Serial method. Native app function sections, native bindings and
the safety/control/recorder capacities above remain unchanged.

`src/hal/dump_uart_unoq.cpp` is compiled in both branches; its shared allocated
sections and relocation targets match. The current app does not instantiate its
UnoQDumpPort, so neither final ELF retains its native dump methods. That is the
existing integration boundary, not a new removed feature. Future transport still
requires D090's direct LPUART1/PG13 native APIs, exclusive lifetime ownership,
clean framing, setup-only device_init, per-call readiness/context/deadline checks,
and poisoned cancellation. Device_init's unbounded setup acknowledgement waits
and physical framing uncertainty remain. No Bridge singleton/worker is needed
for the fixed `mon/write` protocol, but the receiver and full native path still
need their own runtime qualification. This experiment does not budget or qualify
later UART, calibration-snippet or local-reset integration.

## Required next evidence before production adoption

1. Adopt a separate explicit reviewed build contract. Pin the exact CLI/core/
   loader/EDK and relevant library-discovery semantics; restrict the single
   literal property to named eligible app builds. Preserve ordinary bench
   behavior and every upload/inert-source/motor guard. Source identity alone
   cannot distinguish ordinary and experimental binaries.
2. Independently test ordinary versus selected command construction, exact
   properties, new build directories, source/generated-input integrity, unknown
   version/property rejection and failure preservation. Inspect the actual
   selected-library/dependency set and fail closed on unexpected or omitted
   required dependencies. Test an intentional external dependency: globally
   forcing phase 0 can change other libraries' discovery-only branches.
3. Repeat exact target/source/object/startup/export/memory review for each build
   mode actually adopted, including any future MATCH/MOTORS_ALLOWED or startup
   variant. This experiment proves only default MATCH0/MOTORS_ALLOWED0.
4. When native UART or other pending app services are integrated, link the real
   owner and remeasure its complete image; retain D090 ownership/readiness/clock/
   framing behavior. Preserve the strong empty loop hook and actual app startup.
5. Obtain separately scoped actual load/free-memory/stack and full-loop timing
   evidence. No compiler result or modeled 9,668-byte largest payload establishes
   the complete 800-us bound, physical acceptance, PINMAP OK, motor-run permission
   or a human P0-P7 gate.

Next action: coordinator may use this successful investigation to define that
bounded production build contract. This review does not adopt the property,
approve an upload key or close the ordinary-build RAM blocker.
