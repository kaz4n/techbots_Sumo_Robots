# P2 recorder bench: installed runtime instrumentation audit

Date: 2026-09-23. Scope: read-only Linux files, installed EDK, offline packaged-ELF inspection, and pinned primary source. No MCU read, attach, upload, reset, serial RPC, GPIO operation, or service change was performed for this audit. No physical recorder result, free-RAM measurement, stack watermark, or phase acceptance follows.

## Result

The installed loader has **no usable exported heap-statistics API and no stack-watermark API**. `CONFIG_SYS_HEAP_RUNTIME_STATS` and `CONFIG_INIT_STACKS` are absent. The nominally exported `z_impl_k_thread_stack_space_get` has address **zero**, verified in the actual packaged ELF. Header declarations or symbol names alone would give the wrong answer here.

A minimal inert recorder bench can publish a fixed RAM diagnostic record and sampled stack-pointer headroom. Actual remaining LLEXT allocator capacity can be obtained by a separately reviewed, read-only MEM-AP snapshot of the identified loader's heap metadata and a bounded host decoder. It must be called a point-in-time allocator measurement, not minimum free memory throughout execution. The old compiler/loader budget remains a model.

The Linux router serial close/open methods create a new MessagePack decoder without invoking the systemd GPIO hooks. **Close/open alone does not prove a clean byte stream**: the pinned serial implementation does not explicitly flush input when opening. A router service restart has MCU-reset side effects. Decoder preparation therefore needs its own exact, bounded procedure before a transport run.

## Reproducible source set

New receipts and cached sources are in [P2_recorder_bench_raw/native](P2_recorder_bench_raw/native/). `manifest.json` records every file's bytes and SHA-256; receipt JSON records original paths/URLs, commands, return status, stdout, and stderr where applicable. This does not alter the earlier native-transport receipts.

Installed board-side roots:

- Core `C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`.
- Variant `V=C/variants/arduino_uno_q_stm32u585xx`.
- EDK headers `V/llext-edk/include`; exported link map `V/syms-dynamic.ld`.
- Packaged loader `C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`, SHA-256 `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
- Offline tools `/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-{gdb,objdump}`. GDB was invoked with `-nx -nh -batch` against that ELF, without any target command. Its overall status is zero; its two missing-symbol errors for `__heap_start`/`__heap_end` are retained, not interpreted as successful queries.

The installed generated version header says Zephyr 4.4.2-rc1 and build `v4.2.0-18364-g1743741760ee`. Primary source was pinned to full commit [`1743741760ee5d2d58da50d504855d43f9f8e826`](https://github.com/zephyrproject-rtos/zephyr/tree/1743741760ee5d2d58da50d504855d43f9f8e826). The fetched public `include/zephyr/sys/sys_heap.h` is byte-identical to the installed copy. This agreement and ELF checks support the specific conclusions below; they do not constitute a reproducible build of the entire installed loader.

Selected source hashes (full inventory is in the manifest):

| Cached file | SHA-256 |
|---|---|
| `installed/syms-dynamic.ld` | `946c78583eed20806317836e543dd6155970f70990a98c3e11b9c76c4dd8ebfd` |
| `installed/zephyr/include/generated/zephyr/autoconf.h` | `52178f5eefcf276720b859bdd60fc87ca4207b0130ac1fd5ba099af74b877a0c` |
| `installed/zephyr/include/zephyr/sys/sys_heap.h` | `1a86c8839aa0becf4e13b5a70ff6464979c78135ae3cdfa219e7d9c68b382eac` |
| `installed/zephyr/include/zephyr/kernel.h` | `e21b66c8acad2d63de058f316d54637c1b16f95f891e19653c0c58904e4d14a9` |
| `primary/lib/heap/heap.h` | `ab4f448e15c0f887158e4bdb0748a2f33e01971467a87678ab4f6d3e291c92d4` |
| `primary/lib/heap/heap.c` | `55db5bce2fa1fc4f30f6489adc8981ee53cb382ea3a24f059d74afd4c57222a7` |

One guessed primary filename (`subsys/llext/llext_bootstrap.c`) returned HTTP 404 and is recorded as such. The actual implementation is in cached `primary/subsys/llext/llext.c:318`.

## Which memory numbers mean what

Installed `autoconf.h:57-74,115,259-286,462-468,491-508` establishes:

| Quantity | Installed value | Meaning and limit |
|---|---:|---|
| Main stack | 32,768 B | Reserved stack size, not unused stack |
| Workqueue / idle / ISR stacks | 1,024 / 320 / 2,048 B | Separate reservations; main-stack observations do not qualify these |
| System heap configuration | 32,768 B | Requested system pool capacity, not a free-byte observation |
| LLEXT heap configuration | 256 KiB | Fixed pool shared by image instructions, data, and loader metadata |
| libc malloc arena | `-1` | Uses remaining SRAM after `_end`; separate from LLEXT |
| Stack-region metadata | `CONFIG_THREAD_STACK_INFO=1` | Region boundaries are available; no painting/high-water information |
| Heap statistics / stack painting | Both absent | No runtime statistics fields; no reliable historical stack scan |
| Heap allocation loop budget | 3 | Allocator search setting, not a proof that application allocation is allowed after setup |
| Heap registry array | 0 | No populated heap-array enumeration to use |

Offline GDB proves these **packaged initializers/layouts**, not current RAM:

- `llext_heap` at `0x2000112c`: `init_mem=0x20013890`, `init_bytes=262144`; its initial `heap` pointer is zero before runtime initialization. `sizeof(struct k_heap)=24`.
- `_system_heap` at `0x20001114`: backing buffer `0x2000af90`, 32,852 B. This backing-buffer size must not be reported as free usable payload.
- `z_malloc_heap` at `0x200017b0`: initial values zero. `_end=0x20053890`; SRAM end `0x200c0000`. The nominal remaining arena span is 444,272 B before allocator overhead and allocations.
- `z_main_thread` is at `0x20001320`, `sizeof(struct k_thread)=256`; `stack_info` offset 160, `callee_saved` offset 48. `z_main_stack` size is 32,768 B. Initial fields in the file are zero, not evidence that the running thread has an empty stack.

Primary `malloc.c:89-110,193-211` and actual `malloc_prepare.txt` show the libc arena calculation/initialization; `malloc.c:126` uses a `K_FOREVER` mutex. Primary `llext_kheap.h:13-23,35-60` aliases metadata/data/instruction storage to one LLEXT pool and uses `K_NO_WAIT` allocation there. These pools cannot be added together to claim available sketch-loader capacity.

The old [loader budget](P2_memory_loader_budget.md) estimates a particular old image and loader allocation sequence. Neither ELF section totals, static `.bss`, a successful compile, nor `pool capacity minus sections` measures remaining loaded capacity, fragmentation, stack high-water, or transient load peak. Any new bench/native transport changes require a new image hash and budget. A post-load snapshot cannot reconstruct the peak during loading.

## Exact API availability

Installed `kernel.h:512-534` and primary `kernel/thread.c:940-1106` condition `k_thread_stack_space_get` on **both** stack painting and stack-region metadata. Its implementation counts the painted unused region. Painting is off. `syms-dynamic.ld:446` explicitly has `/* NULL z_impl_k_thread_stack_space_get */`; GDB reads the actual export object's `addr=0`. Do not invoke it, manually declare it, or treat a weak zero symbol as support.

Heap statistics declarations likewise do not make a working export. `primary/lib/heap/heap.h:91-100` omits the three statistics fields when statistics are disabled; `primary/lib/libc/common/source/stdlib/malloc.c:265-280` excludes malloc statistics. Installed dynamic exports contain no usable `sys_heap_runtime_stats_get`, malloc runtime statistics, heap-array enumeration, or `k_heap_*` import. Reading assumed `free_bytes` offsets would instead read other allocator data.

`k_malloc` is a real nonzero export (`syms-dynamic.ld:196`; ELF export `0x08012585`). Allocation-until-failure would perturb memory, use the wrong pool for a LLEXT-capacity question, and violate the post-setup rule; it is not the proposed probe.

`k_sched_current_thread_query` has the real implementation export `z_impl_k_sched_current_thread_query=0x08011ae1` (`syms-dynamic.ld:418`; matching disassembly captured). The installed header declares the public syscall at `kernel.h:788-790`. This gives a possible native route to current-thread stack-region metadata, subject to compile/import verification. In contrast, `k_current_get()` at `kernel.h:836-850` takes the TLS path in this configuration; do not assume that path's additional TLS relocations are usable merely because it is inline.

Primary `kernel/thread.c:461-496` sets stack-region information but paints only when configured. A main-thread probe may sample its actual SP and record the minimum observed address after validating thread mode and the active stack selector. Subtracting the region start gives **sampled headroom at those locations**, not a historical maximum-use measurement. A saved `callee_saved.psp` can be from the last context switch. Scanning zeros or `0xAA` in an unpainted stack is invalid; painting the live stack would be unsafe. ISR-stack use needs separate evidence.

The existing loader source [official_main.c:331-396](P2_dump_raw/native/official_main.c) takes the non-userspace branch for this configuration and calls `llext_bootstrap` directly. Primary `llext.c:318-340` and packaged disassembly show bringup, entry call, and teardown after return. No new per-sketch 32 KiB stack should be added to the memory budget solely because an extension is loaded.

## Bounded read-only allocator measurement candidate

This is a proposed future capture architecture, not a capture performed here and not permission to run an existing broader debug recipe.

1. Verify actual flash against the pinned loader and exact inert bench binary before interpreting private addresses. Resolve the loaded extension and relocated diagnostic symbols using the existing bounded list/ELF approach. Reject mismatches.
2. Read the actual runtime `llext_heap` descriptor. Validate its backing span and initialized `heap` pointer against the pinned region. The zero pointer in the file initializer must never be substituted for a runtime read.
3. In a terminal bench phase with no concurrent LLEXT load/unload, take bounded pool snapshots and decode on the host. Compare allocator metadata from two snapshots plus stable phase/sequence fields; a changed chain is an inconsistent observation, not a measurement. Live payload/heartbeat bytes can change without an allocator change, so compare the metadata separately. Equality still does not prove an atomic observation or exclude a complete allocate/free cycle between reads.
4. Decode exact installed layout from `primary/lib/heap/heap.h:63-167,222-245,289-327` and initialization from `heap.c:726-800`. Validate every bound, forward step, size, used bit, left-neighbor consistency, metadata chunk, and terminal marker. Limit the walk to the region's maximum chunk count. Reject corruption, unsupported configuration, ambiguous alignment, or incomplete snapshots.
5. Report free usable payload sum, largest free chunk payload, used payload, allocator overhead, image identity, capture times, and consistency checks. Largest payload is not an unrestricted aligned-allocation guarantee; stronger alignment may need a split and extra space. This point-in-time LLEXT result is separate from libc/system heaps and stack headroom.

Concrete pinned layout: 8-byte allocation units; `z_heap` header is 16 B without stats. At this exact 262,144-byte span initialization reserves an 8-byte footer, giving `end_chunk=32767`; `CONFIG_SYS_HEAP_AUTO` then selects small-chunk fields. Chunk `c` begins at `heap_base+8*c`, with little-endian 16-bit left-size and size/used fields. `size=field>>1`, `used=field&1`; normal usable payload is `8*size-4`, with no canary trailer in this configuration. Skip used chunk zero and stop only at the validated zero-size used end marker. Derive field width again from the observed validated header rather than hardcoding the threshold for other pools.

`tools/p0_mem_read.cfg:1-15` deliberately has MEM-AP access without a Cortex target, flash driver, reset GPIO, or target hooks. However, `tools/p0_capture.py:191-205` permits only **16 reads total** and at most **16,384 B per RAM read**. One full LLEXT copy already takes 16 RAM reads before identities, descriptors, and duplicate capture. The existing script cannot perform this proposed capture unchanged. A new narrowly reviewed wrapper with explicit total bytes, read count, addresses, subprocess deadlines, unchanged no-write/no-reset behavior, and receipts is required. Do not silently relax the old timing-capture guards.

## Decoder-clean preparation is a separate obligation

The prior installed-router inventory [runtime_inventory.json](P2_dump_raw/native/runtime_inventory.json) records package 0.10.0 and binary SHA-256 `3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19`. Cached primary router source is tag v0.10.0 / commit `b92ba75a62781a7b79d4bc0429a499542f939233`; matching version is not a full binary/source build proof.

Installed systemd drop-ins include `ExecStartPre` driving gpiochip1 line 37, `--after-ready` driving line 70 high, and `ExecStopPost` driving line 70 low then line 38 low/high. Thus stopping/restarting the service includes MCU-reset GPIO operations. These commands were inspected only.

Cached router `main.go:180-269` registers `$/serial/close` and `$/serial/open`, each with exactly one string parameter `/dev/ttyHS1`. Close waits for the serial connection to close; reopening creates a fresh `router.Accept(wr)` connection and decoder. Open returns `true` after signalling the reopen request, **before** serial-open success is established. Linux-ready remains a separate process-level signal and cannot supply the missing proof.

The router's pinned `go.mod` uses `go.bug.st/serial v1.6.4`. Cached primary `serial_unix.go:214-294` opens, configures, and returns a port without an explicit input purge; `serial_linux.go:71-73` uses `TCSETS`, not a flush-setting ioctl. Fresh parser state alone therefore does not prove absence of leftover kernel/UART bytes. A future exact preparation must establish exclusive serial ownership, quiescent MCU TX, discarded input/in-flight residue, completed close, successful actual reopen, and an already attached monitor receiver. This audit does not claim an implemented/validated clean preparation sequence.

The cached router CLI can invoke the methods over `/var/run/arduino-router.sock`, but caller deadlines and explicit response validation are necessary: a command's zero exit alone is not proof of a successful RPC/open. No router RPC was sent in this audit. No service action should be hidden inside a recorder-capture helper.

## Next minimal runtime probe architecture

Build a **new inert bench**, rather than uploading the old compile-only `p2_recorder_memory` size probe. Its explicit scope should include:

1. A pinned source/config/artifact identity; `MOTORS_ALLOWED 0`; no motor/sensor/robot-output initialization; no motion-command receiver; no `Bridge.begin`, Monitor, or inherited RPC parser execution. Inspect linked startup/constructors and strong loop-hook ownership, retaining the separate native ownership/counter proof requirement from the transport audit.
2. The actual bounded recorder/attempt owner under a real elapsed-time 1 kHz scheduler with 25 Hz recording for at least the B15 200-second requirement. Feed deterministic synthetic inputs with an explicit fixture provenance. Do not fast-forward timestamps and call it a 200-second runtime run. Preserve expected frame counts, capacities, every loss field, attempt lifecycle, duration, scheduler gaps, and overruns.
3. A fixed `volatile` diagnostic structure with bounded publication: version/run identity, phase, elapsed time, tick count, recorder counters/status, heartbeat, failure code, and sampled SP/validated region bounds. Optional retained-data checksums can bind the later dump to the sealed data. A coherent sequence/terminal-state protocol must let the host reject torn reads without unbounded MCU retry loops.
4. First obtain the read-only runtime evidence from that structure and the separate allocator snapshot. This isolates recording/load/retention from Linux transport. Only a subsequent explicitly prepared run should exercise the native dump path after a genuine current IDLE condition and fresh owner request; sealing an attempt does not establish IDLE.
5. For transport, use the existing fixed-size owner/native contract, ready check, exclusive UART ownership, and no-resume-after-poison behavior. Arm the passive receiver and prove clean decoder preparation before the bench's planned transmit window. Bind session/epoch/count/hash and original CSV bytes; require explicit receiver completeness, not merely MCU TC completion.

This can prove that the exact loaded inert image records, retains, and possibly transports the declared fixture, along with sampled memory facts. It does not qualify physical sensors, motor behavior, full application WCET below 800 us, minimum stack headroom over every call/interrupt, transport timing under all Linux states, or a phase gate. Actual runtime work remains a separate execution step with its own exact artifact and run scope.
