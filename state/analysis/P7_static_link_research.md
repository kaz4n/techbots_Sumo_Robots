# D140 Static-link source qualification

2026-09-24 Asia/Dubai. The pinned package has a concrete Static route worth a
separately reviewed compile-only feasibility study. No static image has been
built, processed or run. Production admission remains dynamic-only, and D139's
592-byte dynamic-loader deficit remains unchanged.

The [installed-source collection](P7_static_link_sources.md) records exact linker
scripts, entry source, allocator aliases and file-only packaged-loader inspection.
Its compact [index](P7_static_link_research_raw/validation_index.json) retains the
original failed text transfer and successful byte-exact recovery. Source findings
support a proposal; they do not authorize a compiler or establish runtime safety.

## Placement and dispatch established from source and packaged files

The linked flag selects a direct Thumb call to0x08100011 before the dynamic
LLEXT path. Static flash starts at0x08100010; writable application storage is
assigned the262144-byte backing buffer at0x20013890. The pinned allocator aliases
reach packaged libc, whose arena starts at0x20053890, exactly after that buffer,
and ends at0x200c0000. The system heap is a separate range. The entry prints its
diagnostic heap symbols but does not initialize an allocator over them.

This resolves the source-level overlap question for those aliases only. A future
image must prove its actual section intervals, initialization symbols and every
native binding; no new allocator or dynamic-LLEXT allocation path may be assumed
safe. Flash initialization/thread tables can carry SHF_WRITE, so an exact named
placement contract is needed instead of equating every such flag with RAM.

## Packaging tools: installed provenance and exact official source

The collector recorded fresh binary hashes and embedded Go module/VCS metadata.
Module names alone did not identify repository URLs: guessed standalone tool
repositories returned404. The exact reported revisions resolve in the official
ArduinoCore-zephyr monorepo. The coordinator fetched these small source files
over HTTPS, preserving their Apache-2.0 notices and exact bytes in a separate
[source manifest](P7_static_link_research_sources/source_manifest.json).
This is provenance evidence, not a reproduced binary build or executed tool test.

| Tool and embedded revision | Source finding relevant to a probe |
|---|---|
| [gen-rodata-ld,05a7b53a](https://github.com/arduino/ArduinoCore-zephyr/blob/05a7b53ab4988497d9c7dfa23996335179988025/tools/gen-rodata-ld/main.go) | Static selects an empty linker fragment before opening the intermediate ELF. |
| [zephyr-sketch-tool,720138e8](https://github.com/arduino/ArduinoCore-zephyr/blob/720138e8a1819634c385d5f49ad3c2d9593e8c9f/tools/zephyr-sketch-tool/main.go) | Raw input gets16 prefix bytes. Header version1, little-endian total length, magic0x2341 and linked flag0x02 describe default Static packaging. Several error paths return normally, so exit0 alone is insufficient. |
| [zephyr-check-size,850a2f64](https://github.com/arduino/ArduinoCore-zephyr/blob/850a2f6486bd7451d0e8551dcfc6c73cba5d98d7/tools/zephyr-check-size/main.go) | Static sums allocated sections carrying SHF_WRITE. This tally does not establish address intervals, alignment gaps, allocator separation, stack or live free RAM. |

The recipes generate both an ELF-based package and a raw-BIN-based package.
Only the latter can satisfy this loader's direct entry. Any future validator
must reject the wrong container, absent/stale outputs, altered header bits,
wrong lengths or payloads and out-of-range data even when the packaging process
reports success. No packaging invocation occurred during D140.

## Boundary for the next proposal

A proposal must preserve exact current sourcefcddbd8e, the verified read-only
stage, default startup, MATCH0/MOTORS_ALLOWED0, all grants/configuration/capacities,
and existing compiler settings. It must add explicit static expectations without
weakening dynamic admission. Independently frozen negative tests and separate
review precede implementation acceptance or any one-job compile-only probe.

The eventual artifact checks need actual ET_EXEC/entry, flash and RAM extents
including alignment/orphans, load/run addresses, data/BSS/constructor ranges,
all loader-owned addresses, known initialization tables and exact raw package
identity. Reusing the dynamic allocation model would be wrong. An accepted
artifact-only feasibility result would still leave execution, live memory,
stack/WCET, matrix/startup behavior, physical gates and deployment unqualified.
