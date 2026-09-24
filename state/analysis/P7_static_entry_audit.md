# P7 current static image: focused entry and constructor audit

2026-09-25, Asia/Dubai. **FILE-AUDITED, runtime and complete native/ABI acceptance
pending.** This read-only audit examines the actual D144 static/default/M0 full
application collected in D146. It changes no firmware, config, policy or tests
and performs no board command, upload, reset, target connection or execution.

## Binding and reproducible evidence

The compact [receipt](P7_static_link_probe_raw/entry_audit.json) records 32 focused
Arm disassemblies, the init-array dump and selected symbol-query output, with
arguments and zero statuses for all 34 commands. Tools are local WSL
`/usr/bin/arm-none-eabi-objdump` and `/usr/bin/readelf`; their hashes agree before
and after. Each disassembly uses the queried function's even Thumb start and
symbol-size end, so same-address C1/C2 constructor aliases cannot silently yield
an empty `--disassemble=name` result. Blank lines and repeated file-format headers
are omitted. Objdump also elides two zero-filled literal spans: Runtime
[0x08100908,0x08100910),8B, and Robot [0x08102f10,0x08102f24),20B.
The separate reviewer checked all5194 rendered bytes against the ELF, verified
these28 omitted bytes are zero and confirmed branches skip both literal spans.
The original receipt's `stdout_format` field overstates literal completeness;
this note corrects that description while preserving the original receipt bytes.

Inputs are checked before and after against these retained identities:

- `P7_static_tls_raw/observed/app.ino_debug.elf`: 1,764,708 bytes,
  `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
- Its map: `15da1417d5a7f781195d86ba1554dd449e4e14548dde1ea8052e8da78cd16806`.
- Installed `main.cpp`, `build-static.ld`, `memory-static.ld`, `syms-static.ld`:
  exact identities in [D140 source provenance](P7_static_link_sources.md).
- All 103 project source files match the D139
  `P7_default_qualification_raw/working_source_manifest.json` before and after.
  The manifest's own byte hash is also retained unchanged. The current source
  binding remains `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.

No new source download or tool installation was needed. Existing authoritative
full ELF/map/source artifacts are referenced, not duplicated.

## Entry, initialization and handoff

The source contract is the pinned installed
[`main.cpp`](P7_static_link_research_raw/main.cpp), together with
[`build-static.ld`](P7_static_link_research_raw/build-static.ld). The actual
`entry_point` symbol is Thumb `0x08100011`, instruction address `0x08100010`.
Its literals and register flow implement this order:

1. Three `printk` calls through `0x080173d5`, displaying system/sketch heap
   addresses. These occur **before** the application's data copy and BSS clear.
2. Copy 208 bytes from `_sidata=0x08116ad8` to
   `[_sdata,_edata)=[0x20013890,0x20013960)` through image `memcpy`.
3. Clear 167,272 bytes in `[_sbss,_ebss)=[0x20013960,0x2003c6c8)` through image
   `memset`.
4. Iterate the empty preinit range `[0x08115970,0x08115970)`, then the one-word
   init range `[0x08115970,0x08115974)`. Its word is `0x08100101`, exactly the
   Thumb address of `_GLOBAL__sub_I_setup`; no additional dynamic initializer
   is present in this array.
5. Call image `main` at `0x081157a1`.

The copy/clear values agree with the linker bounds, including `.noinit` being
inside the BSS output region. The clear ends at `_ebss`, before the linker's
final 1024-byte BSS alignment padding. This is not reset-persistent recording:
entry clears the application's recorder and constructs its owner again.

`main` calls weak `initVariant` (`0x0811579d`, a `bx lr` body), then
`start_static_threads` (`0x081157cd`), then `setup` (`0x081000c9`), and repeatedly
calls `loop` (`0x081000f1`) and the strong project `__loopHook`
(`0x081106e5`, also `bx lr`). There is no SerialUSB initialization call in this
compiled main. The static-thread iterator's start and end both equal
`0x08115970`; its body contains thread-create/name-set calls, but the initial
comparison skips them for this empty image table. This does not claim the
packaged OS has no other threads.

[`src/app/app.ino`](../../src/app/app.ino) supplies the actual setup/loop entry.
`setup` zeros a 21-byte temporary `SetupGrants` and passes it with the runtime
object at `0x20013960` to `Runtime::begin` (`0x08100f9d`). `loop` passes that same
runtime to `Runtime::step` (`0x0810144d`). No changed grant or alternate runtime
instance is introduced by the static entry path. The begin/step bodies and their
complete native effects are outside this focused constructor audit.

## Global objects and constructor calls

Actual named object placement is:

| Object | Address | Bytes | Initialization |
|---|---:|---:|---|
| `dump_port` | `0x20013890` | 208 | Data image, including constexpr FIFO8 selection |
| `runtime` | `0x20013960` | 166376 | BSS then Runtime constructor |
| `motor_port` | `0x2003c348` | 40 | BSS/default values |
| `sources` | `0x2003c370` | 848 | BSS then inlined member defaults |

These symbol sizes are observations, not the separate requested public ABI
size/alignment/member-offset comparison.

`_GLOBAL__sub_I_setup` first materializes fixed source/member defaults. Its
out-of-line work then calls `UnoQPort::port`, `NativeSources::adcPort`,
`NativeSources::port`, `unoQDumpPort`, and `Runtime::Runtime`, using the above
static objects. Their captured bodies distinguish storing a callback pointer
from calling it: the GPIO/PWM, sensor, matrix and UART begin/write/read pointers
are assembled into fixed port values, not invoked by these factories.

The motor port factory computes candidate PWM periods from retained devicetree
constants through `candidateRate`/`candidatePeriod`; it does not read live timer
registers or call the stored motor configuration/write callbacks. The ADC factory
ends in `power::readerInputPort`, which also only constructs a callback bundle.
The dump factory calls `UnoQDumpPort::port`, which stores write/cancel callbacks;
it does not initialize UART or query Linux readiness.

The captured Runtime constructor reaches Transaction, InputOwner, Thresholds,
Snapshot and calibration Report constructors and fixed-memory initialization.
Transaction reaches MotorGate, Robot and RobotResult constructors. Robot reaches
FusionObservation, RobotResult, Turn, Straight and Flank value constructors;
Flank reaches its Turn/Straight constructors. All these bodies are retained in
the receipt, with same-address aliases handled explicitly. MotorGate construction
copies the port and initializes fields; its hardware `begin` operation is not a
constructor call. These paths agree with
[`runtime.cpp`](../../src/app/runtime.cpp),
[`transaction.cpp`](../../src/app/transaction.cpp),
[`native_sources_unoq.cpp`](../../src/app/native_sources_unoq.cpp),
[`dump_port_unoq.cpp`](../../src/app/dump_port_unoq.cpp),
[`motor_port_unoq.cpp`](../../src/hal/motor_port_unoq.cpp),
[`motors.cpp`](../../src/hal/motors.cpp), and their checked headers.

No explicit heap-allocation call, peripheral callback invocation, Bridge call or
serial initialization occurs in the inspected project constructor/factory path.
It uses fixed storage, copies/clears and integer arithmetic. The image's tiny
`memcpy`, `memset` and `__aeabi_uldivmod` bodies tail-branch to packaged native
functions: their complete native behavior is not re-proved here. No claim about
all application call paths or post-setup allocation follows from this result.

## Remaining limits and next checks

- **Startup dependency:** entry relies on an already initialized packaged native
  environment, including three early `printk` calls and native memory/arithmetic
  services. This inherited installed-core path has not been executed for this
  static image. Startup stack headroom, completion time, fault behavior and Linux
  independence therefore remain unmeasured; this audit cannot replace an inert
  startup experiment or full WCET measurement.
- **Full native binding audit pending:** the focused literal/call analysis is
  insufficient to cover every used external function and device/data pointer in
  the complete app. That audit must include stored callbacks and HAL accesses.
- **ABI comparison pending:** run the established D139 16 size/alignment and 82
  member-offset queries against this image's DWARF. The few object symbols above
  do not establish those layouts.
- **Qualification unchanged:** no runtime, motor-run authorization, full static
  adoption, physical acceptance or human gate is supplied. No scoped entry or
  constructor/source discrepancy was found in the inspected paths.

Receipt size is 101,536 bytes (under the assigned 100 KiB limit). Two preliminary
in-memory captures exceeded the limit and wrote no files; their measured sizes
and the final exclusion of optional `Runtime::begin` disassembly are recorded.
No temporary file, build tree or Python bytecode was created. Retain this compact
receipt and note for review; existing ELF/map files remain authoritative evidence.
