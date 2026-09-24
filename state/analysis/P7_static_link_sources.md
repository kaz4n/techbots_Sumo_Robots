# Installed static-link source collection

2026-09-24. Read-only Linux files and file-only GDB establish the installed
static-link placement and dispatch mechanism. **No static image was built,
processed, loaded or run; static fit and runtime compatibility remain unknown.**
Production, policy, tests and D139's negative result are unchanged.

## Exact installed sources

All remote core paths below are relative to
`/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/`.
Each local copy was decoded from a recorded base64 read and matched the remote
SHA256 before use; closing hashes remained unchanged.

| Installed path | Local copy | SHA256 |
|---|---|---|
| `variants/_ldscripts/memory-static.ld` | [memory-static.ld](P7_static_link_research_raw/memory-static.ld) | `cbe17b74e93d2a05f4e101366d036e6a9b3d89d400855349734d5419984d6341` |
| `variants/_ldscripts/build-static.ld` | [build-static.ld](P7_static_link_research_raw/build-static.ld) | `04be061156ebb88fa43537c811e0a8fdc2b721d1bcc0a1a9ac5990018536123e` |
| `variants/arduino_uno_q_stm32u585xx/syms-static.ld` | [syms-static.ld](P7_static_link_research_raw/syms-static.ld) | `f4f05a8a411196fad575360a1b6cc9f5f10a337864548e7387fb8580c4092d62` |
| `cores/arduino/main.cpp` | [main.cpp](P7_static_link_research_raw/main.cpp) | `d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed` |

`memory-static.ld` places flash at `_sketch_start + 16`, and RAM at the
`kheap_llext_heap` backing buffer. The installed symbol file supplies flash
`0x08100000`/size `0x000c0000`, and that RAM buffer at `0x20013890`/size
`0x40000`. `build-static.ld` keeps `.entry_point` first, places code/rodata and
constructor arrays in flash, copies data to RAM and includes BSS/noinit in RAM.
Its BSS output section ends with 1024-byte alignment.

The source entry ignores its heap arguments, copies `.data`, zeroes `.bss`,
runs preinit/init arrays and enters `main()`. It prints `__heap_start/end` but
does not initialize a second allocator over those addresses in this function.
This is source inspection, not execution of the entry or constructors.

## Packaged-loader dispatch and allocation aliases

The packaged loader is still SHA256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
The inspected GDB executable remains SHA256
`8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`.
All GDB commands used `-nx -nh -batch` against the file, without a target,
inferior or function call.

[Dispatch disassembly](P7_static_link_research_raw/loader_dispatch.stdout)
shows `loader` at `0x0800571c`, flag-byte load at `0x08005844`, `AND #2` at
`0x08005846`, and the conditional branch at `0x0800584a`. The set-bit path
calls through `0x08100011` at `0x08005852`, passing `&llext_heap` and its
`init_bytes`; the unset-bit path reaches `llext_load` at `0x080058ba`.
[Literal-word inspection](P7_static_link_research_raw/allocator_alias_dispatch.stdout)
confirms the heap-object and Thumb entry literals. The retained
[official loader source](P2_matrix_raw/source/official_main.c), bound by its
[receipt](P2_matrix_raw/source/official_receipt.json) to ArduinoCore-zephyr
`79b3f1afdad455f55e4a25030953617152c0227c`, defines flag `0x02` and the
same selected control flow. This cross-check does not reproduce the whole
packaged binary from that source revision.

No C/C++ `__wrap_*` definitions were found by the bounded installed-core search.
The definitions are linker aliases in `syms-static.ld:329–333`:

| Alias | Thumb address | Packaged function |
|---|---:|---|
| `__wrap_malloc` | `0x0800800d` | `malloc` |
| `__wrap_realloc` | `0x08008041` | `realloc` |
| `__wrap_free` | `0x08008079` | `free` |
| `__wrap_calloc` | `0x08008095` | `calloc` |
| `__wrap_random` | `0x080126a9` | `random` |

The [allocator disassembly](P7_static_link_research_raw/allocator_alias_dispatch.stdout)
shows the allocation functions use the packaged `z_malloc_heap` at
`0x200017b0`; `calloc` calls that `malloc`. The fresh
[initializer disassembly](P7_static_link_research_raw/libc_arena_dispatch.stdout)
computes arena `[0x20053890, 0x200c0000)`, consistent with the installed
[configuration excerpt](P7_static_link_research_raw/heap_config_lines.stdout)
and the earlier [native audit](P2_recorder_bench_native_audit.md).
This is separate from the LLEXT backing buffer and system-heap buffer
`[0x2000af90, 0x20012fe4)`. These are file-derived addresses and capacities,
not live free-memory measurements. They establish the aliases' packaged path;
a future static image still needs its own link map, resolved-call and placement
review, including any additional libc references and heap use.

## Installed tool identity, without invoking the tools

The version directories are package identities. No earlier binary hash was
confirmed for these three executables; the fresh hashes below bind this
collection. Read-only parsing of their embedded Go build-information records
found these values, with `vcs.modified=false` in all three:

| Package | Fresh executable SHA256 | Embedded VCS revision |
|---|---|---|
| `gen-rodata-ld/0.1.1` | `201f367f31aaf23081c949616e3ff9fa25a91aca1add259cf915957ff63156d7` | `05a7b53ab4988497d9c7dfa23996335179988025` |
| `zephyr-sketch-tool/0.4.1` | `c3c985833d778bd447b6fd20ea70be8555489eec5f7f5953f5eee3bc058838b1` | `720138e8a1819634c385d5f49ad3c2d9593e8c9f` |
| `zephyr-check-size/0.1.0` | `566f5c12f1f88f37c72a6d7d076e7ee4854aa1c1f1e4253e3f2232a64f2b8576` | `850a2f6486bd7451d0e8551dcfc6c73cba5d98d7` |

The observed module paths are `github.com/arduino/<tool-name>`; this is **not**
proof of a repository URL or a separate repository. Source-repository mapping
is the coordinator's separate research. The retained core source commit alone
does not establish these independently packaged binaries' source identity.
[Structured build information](P7_static_link_research_raw/go_build_info_summary.json)
and its raw receipt retain Go versions, module paths, revisions and timestamps.
No help/version execution, binary copy, installation or image processing was needed.

## Evidence boundary and retained transport failure

The first `cat` source read returned CRLF-altered bytes and failed its SHA256
assertion. The original bytes and exit-1 receipt are retained. The subsequent
base64 transfer produced exact remote hashes. Board `rg` was absent (exit 127);
bounded `grep` was used only under the installed core. The literal C/C++
wrapper search returned 1 for no matches; the entry/macro search returned 0.
These results are preserved, not rewritten as successful initial attempts.

The [index](P7_static_link_research_raw/validation_index.json) binds compact
sources, command/exit/output receipts, disassembly and existing provenance
dependencies. No expanded properties, compilation, policy bypass, cleanup,
upload/reset or MCU I/O occurred. This collection supplies review evidence;
it authorizes no feasibility build or static-fit/runtime conclusion.
