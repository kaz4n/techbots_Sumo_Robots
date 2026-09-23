# D101 frozen target audit and conditional loader budget

2026-09-23 Asia/Dubai. P2 software under D051/D075. Audit scope is completed
board-Linux source/artifact reads and offline ELF analysis through ADB2629958581.
The coordinator owns the actual compilations. This audit performs no compile,
upload, reset, MCU attachment/access, UART or motor operation and changes no
firmware, configuration, tests, installed package or shared ledger.

**Latest inspected source83600858 remains D101-R1 BLOCKED by the conditional
loader model: MATCH complete peak262400B,256B over the fixed pool.** Source,
artifact, dependency and retained-path checks pass; runtime acceptance does not.

## Initial source: compiler pass, conditional loader BLOCKER

The initial source is
`96c80701b2149cbc080c0416e5beacfc17d2da8a21ab9831fa6c20d1ec58a8a7`.
Default and MATCH both compile successfully, but exceed the pinned pristine
LLEXT loader model. This blocks acceptance as a loadable full app; no actual
load was attempted and no measured free-memory claim follows.

| Initial build | Compiler payload | Nominal compiler remainder | Modeled complete peak | Peak deficit against262144B |
|---|---:|---:|---:|---:|
| Default MATCH0/MOTORS_ALLOWED0 |257968|4176|262576|432|
| MATCH Immediate1/1 |258344|3800|262960|816|

The successful CLI size check excludes transient loader metadata. The existing
model independently counts each copied region, alignment/header cost, extension
object, section map, temporary global-symbol table, export copy and heap
bookkeeping. The cached pinned source receipts are rehashed by
`P2_app_dump_raw/target_analyze.py`; `target_summary.json` records the full
calculations, sources and exact ELF identities.

| Allocation checkpoint | Default | MATCH |
|---|---:|---:|
| Copied-region chunk bytes |258008|258384|
| Plus extension200 + section-map128 + initial bookkeeping88 |258424|258800|
| Remaining pristine chunk span before symbol table |3720|3344|
| Largest possible payload at that point |3716|3340|
| Temporary symbol count |516|517|
| Temporary symbol payload |4128|4136|
| Required symbol allocation chunk |4136|4144|
| Shortfall at this allocation |416|800|
| Subsequent export-copy chunk, also included in complete peak |16|16|

The largest copied region is BSS171472B, requiring171480B with allocation
overhead. Under the pristine assumptions it is not the first failing request:
the temporary symbol table is. Pinned `llext_load.c` copies regions at855,
allocates the temporary symbol table at869, exports symbols later and frees
temporary map/symbol data only at908/916. Returning temporary memory afterward
cannot eliminate this overlap. Failed allocation returns `-ENOMEM` in the
source at638-640; this is a predicted path, not a captured target error.

Assumptions remain those of the earlier reviewed model: unchanged pinned
non-Harvard loader/configuration,262144B shared LLEXT pool, pristine allocator,
persistent flash at0x08100010 permitting aligned peeks, and no extra constructor
or interleaved allocation. All peek alignments and zero region prepadding are
checked from each final ELF. System heap/libc arenas are separate capacity.
Negative residuals in the original `loader_account.json` are arithmetic deficits,
not negative measured memory; the summary explicitly reports deficits and null
for an impossible post-peak largest payload.

## Later cache-only reduction: blocker narrowed, not closed

The coordinator selected source
`836008588522b81c0f94435725a9b93cbd3cf826b871caf960285797b17b9db0`
after removing the redundant full RobotResult cache. Relative to the initial
frozen source, only `src/app/runtime.h` and `src/app/runtime_inputs.cpp` differ.
This audit collected its completed MATCH Immediate build only; it supplies no
actual default build or inferred default-acceptance result for that revision.

All85frozen source files,75objects, three ELF files and packaged ZSK match the
new completed receipt. The same startup/native/dependency/retained dump, CSV and
UART checks pass. Runtime is169968B,400B below the initial revision; the actual
compiler payload falls560B to257784B, with171336B program bytes and4360B nominal
compiler remainder. Recorder capacity and source configuration are unchanged.

The modeled copied chunks total257824B. Including extension/map/bookkeeping,
258240B is occupied before the temporary symbol table, leaving3904B span and
3900B largest payload. The517-symbol table needs4136B payload/4144B chunk, still
240B too large. Including the subsequent16B export allocation, complete modeled
peak262400B exceeds262144B by256B. D101-R1 therefore remains open. This source
can be described as host-tested/target-compiled within the coordinator's
evidence; it cannot be described as target-loadable from this audit.

Exact final ELF SHA256 is
`89fb7b39499aeb650908a28d62a87ef29dd873c87e11377bb28ecc9fd193f3e0`;
packaged ZSK is `68b7ea399ec461a46517c64ed55ba4d5f6ab251caa4f0e79699ad882fab49bf2`.
Evidence is retained separately under `target_sources_83600858/` and
`target_83600858_match-immediate/`; initial deficits and artifacts remain intact.

## Exact source, artifact and dependency evidence

`P2_app_dump_target_collect.py` deliberately requires the selected full source
digest and freezes all85 source bytes under `target_sources_96c80701/` before
collection. Each completed receipt, full target enumeration and recomputed
aggregate matches that snapshot. The collector reuses the D098 remote program
through the previous collector's AST extractor, recording its hashes and argv;
no historical collector/source policy is changed.

Both initial builds provide75objects, three final/debug/temp ELF files and one
packaged ZSK matching the completed wrapper hashes. Exact wrapper receipts,
raw stdout/stderr and decoded audit are in
`target_96c80701_bench-default/` and `target_96c80701_match-immediate/`.
Initial MATCH collection separately observed that two current worktree files
had changed during parallel development; the complete frozen source and all
artifact identities still match. Its original false current-worktree flag and
collector rejection are preserved in `target_collection_note.md`. Frozen target
identity is the acceptance check; a later worktree revision is a distinct source.

Each mode has75expanded compiler commands,121dependency files and125metadata
payloads with verified hashes/lengths. The correct0/0 or1/1 macros and phase0
appear in every relevant command; assembly retains its original recipe. No
Arduino library include directory or removed Bridge/RPC library dependency is
present. The strict successful wrapper metadata reports zero external libraries.

All six initial ELF files have exactly the same176undefined imports as D100.
The39native and42AEABI nonzero export addresses and the loader hash remain
unchanged. D101 retains existing native UART code without introducing Bridge,
Serial or RPC singleton roots. Native UART and CSV object allocated sections and
relocations remain byte-identical to D100; they were compiled previously and
are now retained through the real application's references.

## Retained application and startup

Two new objects are `dump_port_unoq.cpp.o` and `runtime_dump.cpp.o`. The final
image retains actual Runtime initializeDump/serviceDump/receipt/readiness checks,
Transfer step/abort and formatting pipeline, CSV headers/rows, UnoQDumpPort
begin/ready/advance/abort and the direct native factory. Initial Runtime grows
from168888B to170368B; one native dump owner is204B and NativeSources stays848B.

Main, initVariant, static-thread startup, loop, micros and the strong two-byte
empty loop hook retain their normalized code and relocations. Main remains
exported; one init-array entry names `_GLOBAL__sub_I_setup`, with no fini entry.
The initializer now binds the one native dump owner using the factory and the
four-argument Runtime constructor. The40-byte factory only constructs callbacks
and calls the existing pure port() binding; its relocations are preserved.

Setup remains the40-byte function zero-initializing the19-byte SetupGrants and
calling Runtime::begin with the real static Runtime. It grants no UART ownership,
framing, setup enable or physical authority. Both setup and loop BSS references
are resolved against the final ET_REL's section-relative symbols. The analyzer
explicitly corrects the inherited helper's irrelevant sh_addr subtraction, which
otherwise produced empty target lists; it now requires the actual Runtime target.
This decoder clarification changes no firmware or historical evidence.

This audit verifies retained compiled paths and their identities. It does not
exercise UART setup, Linux readiness, transmission/cleanup, actual loaded RAM,
fragmentation, stack, full800us timing, sensors, motors, PINMAP or any human gate.
The initial loader BLOCKER requires a separately tested source reduction and
new exact target evidence before a revised build can be assessed.
