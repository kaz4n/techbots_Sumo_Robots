# D103 target source, ELF, memory and reset-stack audit

2026-09-23. **PASS for the selected frozen-source/offline target audit and the
conditional loader model.** Both images fit the same pinned model, with a narrow
MATCH margin. This is not an actual load, free-RAM, full-stack, 800 us WCET,
hardware/grant, motor-run or phase-gate result. No firmware compilation, upload,
reset or MCU execution was performed by this audit; all board commands read
Linux files or inspect ELF/DWARF offline.

## Exact artifacts and reproducibility

The selected source is
`1fbd72385c9a729be869bebaaabcc28b5614aa8ff23616843d7b2809a187301f`.
Both D100-policy wrapper receipts completed successfully:

| Build | Receipt | Final ELF SHA-256 |
|---|---|---|
| Default, MATCH=0 / MOTORS_ALLOWED=0 | `147ff7c62e974466a115cc42e75a5637` | `52e2c18e9cc5cb83ead5b2faf8356cb987daf613c55a81187bb74598d95f1b5b` |
| Immediate, MATCH=1 / MOTORS_ALLOWED=1 | `46a4514f871e49a9b103b4252f388fd0` | `e3d539a21a54c481ba8e8a6f91ff3551082f4f2313deaf53c12114b7c3c88bc3` |

Each collection verifies all 87 source files against both the build's aggregate
digest and a retained local source snapshot. It preserves the actual wrapper
receipt, three ELF files, ZSK package, 77 object audits, 77 compiler commands and
129 hashed metadata files, including 125 dependency files. All six ELF hashes
and both package hashes agree with the completed build receipts. Package
identity here is a receipt hash check; decoding its header is separate.

The new `P2_service_reset_target_collect.py` reuses the D101 collector and the
D098 board audit program. Its new freeze routine explicitly requires 87 files
and the exact selected digest. `P2_service_reset_target_analyze.py` extracts the
D101 pure audit functions via AST and deliberately adapts its two 85-file
constants to 87, after asserting there are exactly two. The historical collector,
analyzer and evidence are unchanged. Allocation order is reused from D102.

Evidence is under `P2_service_reset_raw/`:

- `target_sources_1fbd7238/`: complete frozen source and manifest.
- `target_1fbd7238_bench-default/` and `target_1fbd7238_match-immediate/`:
  receipts, board stdout/stderr, audits, three ELFs and ZSK packages.
- `target_abi/` and `target_abi_caller_path/`: exact offline commands, timestamps,
  tool/ELF/config hashes, target type output and installed loader/reset disassembly.
- `target_summary.json`: repeatable source, object, function, startup, import,
  allocation-order, target ABI and stack analysis.

Reproduce the local checks with
`python state/analysis/P2_service_reset_target_analyze.py`. Board recollection
uses the completed receipt and explicit mode with the new collector. ABI
collection uses the successful default receipt and offline GDB only; no new
probe compilation was needed.

## Source, mode and retained-path checks

Relative to D102's frozen 85-file source, the new files are
`src/app/runtime_service.cpp` and `src/app/transaction_service.cpp`. The other
changed files are runtime.cpp/.h, runtime_inputs.cpp, transaction.cpp/.h and
ui_display.cpp/.h. The exact nine-file difference is asserted. Core and recorder
sources remain identical. Actual app setup still has `SetupGrants{}`; this audit
does not grant or exercise local service reset on hardware.

Both images retain Runtime service qualification/continuity/reset methods,
Transaction completion proof and guarded reset, and `Robot::reset`. Their
normalized instruction bytes and relocations agree across modes. The actual
call relocations connect Runtime::step -> applyServiceReset ->
Transaction::resetStoppedRobotForService -> Robot::reset. Existing Runtime dump,
Transfer, CSV, UART and native dump-port factory paths remain retained. CSV and
native UART object allocated sections/relocations are unchanged from D102.

The complete cross-mode comparison covers 1,473 common allocated sections over
77 objects. Only the expected three motor sections differ:
UnoQPort::writeEnable, UnoQPort::writePwm and MotorGate::transact. No objects are
added or removed between modes. The initial analyzer assertion mistakenly
allowed only motors.cpp and omitted motor_port_unoq.cpp; its failure is retained
in `target_analyzer_initial_failure.txt`. The correction asserts these exact
three sections across the two files. It required no production change.

All six ELFs retain the same 176 imports as the previously audited native app;
the installed loader's 39 native exports, 42 AEABI mappings and static-thread
evidence agree with the pinned baseline. No Bridge, RPClite, MsgPack or external
Arduino-library dependency appears. Main, loop, initVariant, static-thread
startup, micros and the strong two-byte return-only `__loopHook()` preserve the
previous startup implementation after relocation normalization. The single
initializer remains `_GLOBAL__sub_I_setup`, with no fini array. Setup and loop
resolve to the real singleton Runtime; main is the exported sketch entry.

## Ordered conditional loader model

The model retains the installed loader hash
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`,
the 262,144-byte llext pool and hashed loader-source receipts from
`P2_memory_validation_raw/source_receipt.json`. It assumes a pristine pool,
persistent flash peeks at `0x08100010`, and no constructor/interleaved allocation.
Required flash-peek sections and section headers satisfy their alignments.
See `P2_memory_loader_budget.md` for the inherited source/allocator model.

| Bytes | Default | MATCH Immediate |
|---|---:|---:|
| Compiler program output | 175,036 | 175,516 |
| Compiler RAM payload | 256,332 | 256,716 |
| Compiler nominal remainder | 5,812 | 5,428 |
| Copied region chunks | 256,368 | 256,752 |
| Span before temporary symbols | 5,360 | 4,976 |
| Temporary-symbol chunk | 4,256 | 4,264 |
| Complete conditional peak | 261,056 | 261,448 |
| Remaining span at peak | 1,088 | 696 |
| Largest next allocation payload | 1,084 | 692 |

The ordered MATCH allocation ledger is:

| Request | Chunk | Remaining span |
|---|---:|---:|
| Heap bookkeeping | 88 | 262,056 |
| Extension | 200 | 261,856 |
| Section map | 128 | 261,728 |
| Text | 85,504 | 176,224 |
| Rodata | 3,808 | 172,416 |
| BSS | 167,416 | 5,000 |
| Exported symbol region | 16 | 4,984 |
| Init array | 8 | 4,976 |
| Temporary symbols | 4,264 | 712 |
| Separate export copy | 16 | 696 |

Every request fits the preceding span, including the largest region and the
temporary symbol allocation; the complete peak also fits. The separate export
copy remains accounted while the temporary table exists. Model arithmetic does
not treat a compiler remainder as available local-variable space.

Compared with each same-mode D102 image, the payload rises 2,560 bytes and the
conditional peak rises 2,680 bytes. BSS rises 88 bytes; text rises 2,472 bytes;
rodata remains 3,800 bytes. MATCH's prior modeled margin of 3,376 bytes therefore
becomes 696 bytes. No new modeled fit blocker is found for these exact images;
the small remaining margin requires re-auditing any later change.

## Actual ABI and retained reset stack

Offline GDB on the actual completed-target debug ELF reports:

| Type/owner | Bytes | Alignment |
|---|---:|---:|
| app::Runtime | 166,304 | 8 |
| app::Transaction | 162,544 | 8 |
| fsm::Robot | 2,640 | 8 |
| recorder::AttemptRecorder | 159,200 | — |
| recorder::FrameBuffer | 126,300 | — |

The linked Runtime BSS symbol independently has 166,304 bytes, exactly 88 above
D102. Other singleton owners remain sources=848 and dump_port=204 bytes.

The retained `Robot::reset()` prologue saves nine registers (36 bytes) and
subtracts 2,644 bytes from SP. Its **own direct frame is 2,680 bytes**, including
the 2,640-byte temporary Robot used by the existing reset implementation. The
epilogue restores that exact allocation. Immediate caller frames are 24 bytes
for Transaction::resetStoppedRobotForService, 32 for Runtime::applyServiceReset
and 32 for Runtime::step. These are inspected frame sizes, not a complete
worst-case stack bound; reset also invokes memory routines, with older callers
and possible interrupt use outside this subtotal.

The installed base ELF and configuration independently reserve 32,768 bytes for
`z_main_stack` and 262,144 bytes for `kheap_llext_heap`. CONFIG_USERSPACE and
CONFIG_INIT_STACKS are absent. Actual base disassembly shows main calling
loader.constprop.0.isra.0, then llext_bootstrap, which calls the sketch entry on
that thread. No separate userspace sketch-thread allocation applies to this
installed route. The stack reservation is separate from the llext pool and is
not a measurement of remaining stack. The exported stack-space query address
is zero, and no query was executed. Loaded allocator state, real stack high-water,
reset latency and whole-epoch WCET remain unmeasured and unqualified.
