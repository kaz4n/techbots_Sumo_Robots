# D091 inert recorder runtime and memory evidence

2026-09-23, selected under D051/D075 and explicit user bare-UNO-Q test authority.
P2 B8 preparation only. No sensors/driver/motor connections requested or inferred.
No human gate or motor authority. B16 values and existing tests remain unchanged.

## Sequence and limits

Implement a new explicitly synthetic, MOTORS_ALLOWED0/MATCH0 bench. Use actual
Robot -> MotorGate with inert checked callbacks -> AttemptRecorder. No native
motor, sensor, ADC, QTR, IMU, matrix or UART initialization; no Bridge.begin,
Monitor or RX parser. No transport in this first run. The existing strong empty
loop hook must remain linked. Any proposed upload needs fresh source/ELF review
and an exact inert run scope; the old compile-only probes remain unapproved.

Use micros() through a clock port and at most one actual tick per poll, at TICK_US.
No fast-forwarded timestamps or catch-up loop. Repeated time does no work;
backward/half-range chronology fails. Skip missed scheduler slots explicitly and
retain missed counts/max lateness. Synthetic startup supplies stable NONE, START
and NONE intervals of BTN_DEBOUNCE_MS plus four TICK_US, then lets the actual
countdown/Robot qualification run. START must be accepted within BTN_LONG_MS after
the synthetic release phase starts; otherwise freeze failure. Inputs are clearly
synthetic: black QTR=QTR_TIMEOUT_US, inactive opponent raw bits before GO and a
center-front detection after GO, nominal valid battery, absent IMU, no real ADC.
Do not label these samples physical or hardware-reported.

After the actual accepted START release, retain a real elapsed
LOG_FRAME_WINDOW_MS (200000ms) recording, then request STOP and continue bounded
ticks until the final deferred frame is consumed and source becomes SEALED.
Require sealing within BTN_LONG_MS after STOP. Inert MotorGate callbacks reject
and count any attempted nonzero PWM or enabled EN. No external pin is touched.
Pass actual prior-tick timing/applied feedback to Robot; preserve every recorder
loss/status field. Completed sequence is not equivalent to no gaps or acceptance.

After sealing, checksum retained frame bytes plus each pack-status byte, followed
by insertion-order event bytes using CRC32/ISO-HDLC. Process at most one retained
row per poll; no whole-buffer work in a tick. Then freeze evidence. Fixed
diagnostics publish with an even sequence and memory barriers; no dynamic memory
after setup. Record phase/failure, actual MCU times/epoch, tick/lateness/miss
counts, recorder counts/loss/timing, CRC and nonzero-write counters. Sampled SP
headroom may be added only with validated current-thread region and installed
nonzero API; NEVER call the zero stack-watermark export or paint a live stack.
No sampled number proves historical stack high-water or complete robot WCET.

## Pinned allocator decoder API

New tools/recorder_heap.py is a pure offline decoder, not an MCU command tool.
Public HeapError(ValueError) has .code. decode_pool(blob:bytes, *,
base_address:int=0x20013890)->dict accepts only the pinned32-bit loader LLEXT
pool, exact262144bytes and exactbase. compare_pools(first:bytes,second:bytes, *,
base_address:int=0x20013890)->dict rejects different allocator metadata and returns
the decoded report plus second_snapshot_sha256 and consistency="CONSISTENT_SAMPLED".
It does not claim an atomic snapshot or exclude allocate/free cycles between reads.

Derive the layout from pinned primary/lib/heap/heap.h and heap.c in
P2_recorder_bench_raw/native. No runtime stats/canaries; AUTO mode, target32bit.
8-byte units; initial262144bytes reserve8-byte footer; end_chunk32767 selects
16-bit chunk fields. z_heap header16bytes,15four-byte bucket heads, so chunk0 is
10units/80bytes and must be used with left_size0. Normal fields at chunk*8 are
uint16 left_size, uint16(size_units<<1|used); free chunks additionally have uint16
prev/next ids. Normal payload=8*size_units-4. End marker must be used,size0,with
matching left_size. Reject every malformed bound/zero/nonforward step/left-link,
wrong metadata size, unsupported header, invalid free-list or unavailable bucket.

Walk at most32768chunks. Validate all fifteen bucket heads and avail bitmask;
free nodes must form disjoint circular reciprocal lists in floor(log2(size_units))
buckets, matching exactly all free chunks from the forward chain. Reject adjacent
free chunks (the allocator coalesces them), links into used/metadata/end chunks,
cycles that miss their head, duplicate membership and out-of-range bucket bits.
No field from user payload may supply an unchecked address or loop bound.

Report schema_version1, base_address, pool_bytes, end_chunk, metadata_bytes,
free_payload_bytes, largest_free_payload_bytes, used_payload_bytes,
overhead_bytes, free_chunk_count, used_chunk_count (exclude metadata chunk),
chunks (normal records index,size_units,used,payload_bytes), metadata_sha256 and
snapshot_sha256. Metadata digest includes header/bucket/chunk fields and free
links, excludes live used payload and free stale payload. Document deterministic
canonical digest encoding. Free+used+overhead must equal262144. Overhead includes
chunk0, footer/alignment and normal headers. Largest free payload does not promise
arbitrary aligned allocation. No totals across unrelated heaps or minimum-runtime
free-memory claim. Independent tests use literal source-derived fixtures and
corruptions, including all-free/all-used/fragmented/maximal bounded chains.

## Capture and qualification

Verify exact deployed loader/sketch bytes and LLEXT symbol layout before any
private address interpretation. Use read-only MEM-AP, no Cortex attach, halt,
reset, write, flash or daemon action hidden in capture. The existing p0_capture
16-read/16KiB guards remain intact. A new capture wrapper must independently bound
all allowed addresses, total reads/bytes/deadlines, and preserve exact command
receipts; it needs review/tests before execution. Take two allocator metadata
snapshots in terminal bench state and compare validated metadata, not changing
used payload. Report timing brackets and sample consistency limitations.

Hardware run evidence must distinguish actual MCU execution/record retention,
MCU-clock duration, observed Linux monotonic intervals, loaded allocator capacity
and sampled stack headroom. SC-AJ clock qualification and full800us worst case,
actual sensor logging, native UART transport, assembled-robot B8 and human gate
remain separate. A later transport run needs its own clean-decoder preparation;
serial close/open alone does not purge RX, and router restart has MCU-reset hooks.

## Frozen runtime diagnostic / capture API

bench/recorder_inert/src/recorder_bench.h freezes Report64 uint32 words (256B),
StackSample8words and Diagnostics74words (296B). Report58named words plus6reserved0;
header comments give word indices. Phase0BOOT/1RUNNING/2FINALIZING/3CHECKSUM/4FROZEN/
5FAILED. Failure0NONE/1CLOCK/2REENTRY/3GATE/4START_TIMEOUT/5ROBOT/6RECORDER/
7SEAL_TIMEOUT/8CHECKSUM. Diagnostics front sequence at0, report at4, stack at260,
tail at292. Native global recorderDiagnostics is BSS, external C symbol.
Sequence must be nonzero even and equal at both ends; terminal values freeze.
Stack validity is separate from runner completion; fault or unavailable metadata
invalidates sampled stack evidence, never manufactures a watermark. Reserved0.

New tools/recorder_capture.py provides decode_diagnostics(blob:bytes)->dict and
capture_values(capture,base:int,symbols:dict)->None, alongside a CLI following P0
receipts. Decoder strictly rejects wrong type/size/schema/reserved/enums/incoherent
sequence/nonterminal phase and impossible stack data; preserves every actual
failure/loss count rather than treating completed capture as passed experiment.
Return report (field-named words), stack (field-named words), sequence. FROZEN needs
failure0; FAILED needs nonzero failure. Bool fields are0/1, frames<=5001/events<=4096.
Valid stack requires fault0,samples>0, aligned SRAM bounds, 0<=delta<=size,
start<=minSP<=start+size-delta and headroom=minSP-start; invalid stack is not proof.

Capture independently bounded: <=48 memory reads, <=2097152 total memory bytes,
<=16384 per RAM read, <=64 commands, <=600s entire command sequence and <=30s per
command. Read bounds count attempts, including failures. Read purposes are only
pinned loader/sketch identity, bounded <=4-node LLEXT traversal, exact296B relocated
diagnostic, fixed24B llext_heap descriptor, and exactly16 aligned16KiB blocks per
262144B pool snapshot. Keep p0_capture unchanged. Reuse only verified pure helpers
and bounded find_bss/flash routines; no weakening monkeypatch of old guards.
Pin exact reviewed artifact path/ELF/ZSK hashes in the new helper before execution;
unset pins fail before any MCU read. Exact installed tool/config/loader checks
remain. No CLI address/size/command inputs or writes/reset/attach/daemon actions.

After flash/layout/LLEXT identity, decode first frozen diagnostic, read heap
24B descriptor0x2000112c (ptr/initmem/initbytes must0x20013890,0x20013890,262144),
read two complete pools, validate/compare metadata with recorder_heap, reread the
same descriptor and diagnostic identically. Store both raw pools and all raw read
fragments plus monotonic/UTC command brackets and complete failure receipts.
Report CAPTURED denotes read evidence only, not physical B8/P0/P1 acceptance.

### Evidence-driven flash read subdivision (same limits)

First actual capture timed out30s on263680B loader read, leaving94208B partial;
no private RAM or recorder result was interpreted. Preserve runtime_run1 evidence.
Production flash verification now uses exact indexed65536B blocks (loader5,
sketch3), comparing every byte before RAM access. Every block counts against the
unchanged48-read/2MiB/64-command/600s/30s bounds;16KiB RAM bound also unchanged.
With one loaded sketch the complete capture uses47reads; additional extensions
may exhaust the guard and fail explicitly, never weaken it. Legacy whole-span
API remains for compatibility but the production verifier uses blocks only.
No firmware change/reupload; new capture helper bytes require reviewer approval.
