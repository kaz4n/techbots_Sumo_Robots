# D102 target frame layout and conditional loader audit

2026-09-23 Asia/Dubai. Scope: completed board-Linux artifacts, frozen source,
offline ELF/DWARF and the previously pinned loader model. No upload, reset,
MCU attachment/access, runtime or physical measurement. The coordinator owns
actual app compilation; this audit required no additional compilation.

**Result: target identity/retention and conditional loader fit PASS for default
and MATCH. The modeled deficit underlying D101-R1 is cleared by these artifacts.**
Separate review and ledger disposition remain the coordinator's responsibility.
Actual loaded RAM, stack, full800us timing and physical/human gates remain open.

## Source and reproducible collection

Exact source:
`3bf0da005d3268adfca52bb86f96ab40921c4bb4f2c2d10ea1cd90a8cf2a0f38`.
Each mode's85-file target enumeration and recomputed source digest match the
complete frozen local snapshot. Relative to cached D101 source83600858, exactly
three production files differ: recorder_frames.h, recorder_frames.cpp and the
FRAME_ROW consumer in recorder_dump.cpp. No source/config capacity or rate change
is hidden in this build;5001frames/4096events/25Hz remain.

`P2_frame_packing_target_collect.py` reuses the D101 collector with an explicitly
selected new source and separate RAW directory; that collector reuses the D098
offline program by AST extraction. Existing D101/D098 evidence and collectors
are unchanged. Default receipt39fedf763646445b8a7db864916e1121 and MATCH
receipt06a1ad24c02247d3a9af320d267a9585 are copied intact into their target folders.
Each supplies75objects, three final/debug/temp ELFs and a packaged ZSK with exact
wrapper-matching hashes. All source/current-source/artifact checks passed.

`P2_frame_packing_target_analyze.py` loads only the prior analyzer's function
definitions, with new evidence paths, avoiding execution of its old entry script.
`P2_frame_packing_raw/target_summary.json` records the reused source hash, detailed
results, allocation order and target ABI. All125metadata texts and121dependency
files per mode are hash/length checked.75actual compile commands retain the
correct0/0 or1/1 macros, fixed phase0 and no external library include path.

## Actual target ABI

Offline GDB reads the already produced debug ELF; it never starts an inferior,
attaches to a target or evaluates a runtime call. The exact debug ELF and GDB
hashes, argv, timestamps and output are in `target_abi_retry/`.

| Target type | sizeof | alignof |
|---|---:|---:|
| StoredFrame |26|1|
| FrameBuffer |126300|4|
| AttemptRecorder |159200|8|
| Runtime |166216|8|

The target's actual type layout is125025payload bytes at offset0,1251packed
status bytes at offset125025, and six4-byte index/counter fields from126276
through126299. This is5001*25 + ceil(5001/4) +24, exactly126300B. StoredFrame
remains the26-byte caller-owned value. Runtime's ELF BSS symbol independently
matches166216B in both modes, versus169968B in cached D101:3752B smaller.

The initial GDB command returned1 because its default max-value-size refused
large-type alignof/ptype expressions. Its partial sizes and errors are preserved
in `target_abi/`. A retry changes only GDB's local inspection limit to unlimited;
all eight sizeof/alignof values and the complete layout then return successfully.
No ABI probe source/object or additional compile was needed.

## Net target saving and retained paths

Compare actual MATCH Immediate to the same mode of cached D10183600858:

| ELF payload region | D101 | D102 | Change |
|---|---:|---:|---:|
| BSS |171072|167320|-3752|
| Text |82928|83024|+96|
| Copied rodata |3772|3800|+28|
| Complete compiler-counted payload |257784|254156|-3628|
| Conditional complete loader peak |262400|258768|-3632|

This counts extra code/rodata and allocator rounding; it does not equate raw
array savings with loader savings. The517-entry temporary global-symbol table
is unchanged in MATCH. Header-layout changes also change offsets in existing
Runtime/Transaction/AttemptRecorder object code; the detailed comparison records
those changes instead of claiming every unrelated translation unit is identical.

FrameBuffer::read is retained; the former at API is absent. bytesAt exists in
the compiled frame object and may be discarded from the final app when unused.
Dump's FRAME_ROW path calls the new copy-out read and the unchanged CSV formatter.
The native UART and CSV object's allocated sections/relocations remain identical
to D101. Actual Runtime receipt/readiness/service, Transfer step/abort, CSV and
UnoQDumpPort setup/ready/transmit/cancel paths remain retained.

All six ELF files preserve176undefined imports.39native and42AEABI exports
remain nonzero in the same pinned loader. Main, loop, initVariant, static-thread
startup, micros and the strong two-byte empty loop hook retain normalized code
and relocations. Main remains exported, with one actual app constructor entry
and no fini entries. Setup/loop references resolve to the real Runtime; setup
continues with zero-initialized grants. No Bridge/Serial/RPC root reappears.

## Conditional complete allocation budget

| Actual build | Compiler exit | Program bytes | Compiler payload | Nominal remainder | Modeled complete peak | Remaining span | Largest payload |
|---|---:|---:|---:|---:|---:|---:|---:|
| Default0/0 |0|171028|253772|8372|258376|3768|3764|
| MATCH Immediate1/1 |0|171508|254156|7988|258768|3376|3372|

Both real compiler warnings about low memory remain in the saved receipts.
The projected allocation order follows pinned llext_mem enumeration and
llext_load.c: heap bookkeeping, extension, section map, copied text, rodata,
BSS, exported-symbol region and init array, then temporary global symbols and
the separate export copy. Empty/flash-peeked regions request no copied chunk.
Every request fits the preceding pristine span; the full sequence is recorded.

BSS is the largest request:167320B payload/167328B retained chunk. Before that
allocation default has175272B contiguous span; MATCH has174888B. After all copied
regions and fixed metadata, default has7920B span and MATCH7536B. Their temporary
symbol allocations need4136B and4144B chunks respectively, followed by16B export
copy. These are the allocations that failed the earlier D101 budget; both now fit.

The model retains the same assumptions: pristine262144B non-Harvard LLEXT pool,
unchanged pinned loader/configuration, persistent flash at0x08100010 with verified
peek alignments, no region prepadding, and no extra constructor/interleaved
allocation. It does not measure current free RAM, fragmentation, stack, load
success, startup execution or a worst-case memory minimum. Margin is small and
future integration requires a new exact-source budget.

Default final ELF SHA256:
`d4b8e4bdbc9b4669e3ad67e7e153c5b5ee5ffe959cf410f8276c8e8ecf26d5c3`.
MATCH final ELF SHA256:
`0499a9b5a2491adc790b405ac248caa27015c053bcf0421edffe91e36988bea0`.
Neither image was uploaded or run by this audit. No physical B8/UART, motor-run
authorization, PINMAP acceptance or human phase gate follows from this result.
