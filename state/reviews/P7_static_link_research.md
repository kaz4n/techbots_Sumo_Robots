<!-- Reviews D140 static-link source feasibility without compiling or changing policy. -->
<!-- Separates exact installed observations from official tool-source provenance. -->
<!-- Read-only source/receipt inspection; no board, target, compiler or image-tool execution. -->
# D140 static-link source review

2026-09-24 Asia/Dubai. Separate same-model reviewer, continuing after D139.
**Source audit supports a separately reviewed, bounded default/M0 compile-only
feasibility proposal. It does not authorize that proposal or prove static fit.**
No demonstrated source-level dead end was identified. D139's 592-byte dynamic
loader deficit remains a release blocker. Production admission remains
dynamic-only at `tools/app_build_policy.py:137`; bypassing that policy is not an
accepted experiment design. No production source, policy, test or ledger was
changed by this review.

## Confirmed path and placement

The retained official `loader/main.c` at ArduinoCore-zephyr commit
`79b3f1afdad455f55e4a25030953617152c0227c` and the freshly hashed packaged loader
agree on a distinct linked path. `official_main.c:305` calls Thumb address
`base + 16 + 1` with the LLEXT heap object and size, before dynamic `llext_load`.
In the [file-only disassembly](../analysis/P7_static_link_research_raw/loader_dispatch.stdout),
`0x08005846` tests flag `0x02`, `0x08005852` calls through `0x08100011`, and the
dynamic call is separately at `0x080058ba`. This is not
`llext_load(pre_located)` and does not incur that dynamic allocation sequence.
The source/binary correspondence is to packaged loader SHA-256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`,
not proof of any deployed loader or static runtime.

The exact installed [`memory-static.ld`](../analysis/P7_static_link_research_raw/memory-static.ld)
and [`syms-static.ld`](../analysis/P7_static_link_research_raw/syms-static.ld) specify:

| Region | Half-open interval | Intended owner |
|---|---|---|
| Sketch flash, including 16-byte header | `0x08100000..0x081c0000` | Packaged static image |
| Executable/constant payload begins | `0x08100010` | First `.entry_point`, then flash sections |
| Static writable storage | `0x20013890..0x20053890` | LLEXT backing buffer reused by static image |
| Existing system heap buffer | `0x2000af90..0x20012fe4` | Packaged kernel allocator |
| Existing native libc arena | `0x20053890..0x200c0000` | Packaged `z_malloc_heap` |

[`build-static.ld:7`](../analysis/P7_static_link_research_raw/build-static.ld)
selects `entry_point`; line 21 keeps it first in `.text`. Code, constants and
initializer/static-thread tables are placed in FLASH; `.data` has a FLASH load
address and RAM execution address; `.bss` ends with 1024-byte alignment. Installed
[`main.cpp:76`](../analysis/P7_static_link_research_raw/main.cpp) ignores the passed
heap parameters, copies `_sidata` to `_sdata.._edata`, zeros `_sbss.._ebss`, runs
preinit/init constructors and calls `main`, which reaches the existing setup/loop.
Thus a future result must verify entry and initialization symbols/sections;
compiler success alone cannot establish correct startup.

## Allocator and native binding boundary

`syms-static.ld:329` maps the four allocation wrappers to packaged native libc
functions: calloc `0x08008095`, free `0x08008079`, malloc `0x0800800d`, realloc
`0x08008041`; random maps to `0x080126a9`. Fresh file-only disassembly confirms
these bodies use `z_malloc_heap` at `0x200017b0`. Its `malloc_prepare` initializes
an arena beginning at `0x20053890`, after the static RAM region. This closes the
specific suspicion that these wrapper aliases inherently create a second
allocator over the static object bytes. The static entry's `__heap_start/end`
references to the system buffer are diagnostic prints, not allocator setup.

Static data/BSS intentionally reuse an initialized LLEXT heap's backing bytes;
the heap object passed by the loader is different storage (`0x2000112c`). A future
static image must not subsequently use dynamic LLEXT allocation against those
overwritten bytes. The present aliases are evidence for the packaged path,
not a complete future image call-graph proof. Every actual absolute native
reference, allocator route and veneer/Thumb binding still requires image-specific
verification. No heap after setup, deterministic tick and all existing source
grants remain unchanged; static linking does not qualify their runtime timing.

## Packaging obligations

Official tool sources are retained separately under
[`P7_static_link_research_sources`](../analysis/P7_static_link_research_sources/).
Their exact ArduinoCore-zephyr revisions match the installed executables'
reported Go VCS fields. This is provenance evidence, not a reproduced binary.
The standalone-looking Go module paths do not identify standalone repositories.

- `gen-rodata-ld_main.go:44` deliberately emits an empty fragment in static mode.
  No dynamic rodata-splitting assumption belongs to this path.
- `zephyr-sketch-tool_main.go:56` prepends 16 bytes for a raw non-ELF payload,
  writes version 1, total length, magic `0x2341` and linked flag `0x02`. Several
  read/header/write failure paths simply return from `main`, so exit 0 alone is
  insufficient. Default startup must have flags exactly `0x02`, with debug,
  Immediate and wait-for-app unset.
- Both ELF-mangled and raw-binary-mangled outputs are generated by the recipes.
  Only **`.bin-zsk.bin`** is the static upload format. An `.elf-zsk.bin` file would
  put ELF metadata, rather than the intended entry instructions, at the direct
  jump address. A future verifier must bind the selected suffix and exact bytes.
- `zephyr-check-size_main.go:75` only sums section sizes carrying ALLOC and WRITE.
  This is not RAM interval accounting or proof of flash layout, overlaps,
  alignment, initialization, allocator ownership or useful runtime free memory.
  Known initializer tables may carry WRITE despite explicit FLASH placement;
  use a reviewed named-section placement contract instead of a blanket flags-only
  RAM rule, and reject unexpected writable/orphan/TLS/GOT placement.

## Boundary for a possible follow-up

A separate proposal could evaluate exactly one unchanged-source static/default
`MATCH=0 MOTORS_ALLOWED=0` image with one compiler job and no upload, reset or run.
Before implementation/execution it needs separately reviewed exact command and
property expectations, pinning of all existing dependencies plus static scripts
and three image-tool binaries, and independent frozen validator tests. Preserve
the current dynamic policy and every existing safety/profile/override/library
check; do not turn off validation to admit the static recipes. Reuse the exact
existing source stage read-only, with no retry of denied deletion.

Its bounded negative tests and final artifact checks must cover wrong profile,
startup/grants, tool/source drift, wrong or missing artifact, stale output despite
exit 0, malformed/truncated/oversized ZSK, wrong flags/length/magic/version,
payload mismatch and accidental ELF-mangled selection. Require an ARM ELF32
executable with the intended Thumb entry at `0x08100011`, named section and
load/execution intervals within their reviewed regions, initialization symbols
and constructor tables, no unexpected unresolved or runtime relocation need,
and exact native-address bindings. Account actual interval extrema, gaps and
padding; do not subtract the dynamic model's metadata from a compiler tally to
claim static fit. Preserve the first failure and stop without an automatic repair
or second compile. A successful result could establish artifact feasibility
only; execution, startup liveness, live memory, stack, WCET, hardware and human
phase gates remain separate.

## Evidence status

The initial CRLF-altered `cat` transfer failed its exact hash check and is
retained. Base64 recovery produced byte-exact installed scripts; it did not
change installed or project sources. The independent
[source binding receipt](P7_static_link_research_raw/source_binding.json)
rechecks all 66 native raw files (168157 bytes), six existing dependencies,
four exact installed source copies, the initial/closing installed hashes and
all three official tool sources against their reported build revisions.
Native index SHA-256:
`342b7acb993b404963fb9c0904d17c17a6e3cb9b18dc0089085a3dc4e9fbfb53`.
Collector report SHA-256:
`01e2ee8e16b654c7ede20f78e2e5dd7dd1cef5612cfbcf3bdded004eecce9644`.
Official source manifest SHA-256:
`819e07aff3b464fe07ecf6b1c4a76ebd7b708ba47678548fc55ccebd7b7ce241`.
No open defect was found in the bounded source-evidence packet; the follow-up
requirements above remain prerequisites, not completed artifact validation.
The reviewer read local files and receipts only, and did not execute a
board command, compiler, packaging binary, target/inferior or cleanup action.
