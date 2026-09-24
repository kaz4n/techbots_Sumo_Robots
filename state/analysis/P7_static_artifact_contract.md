# Static artifact layout/package component

Draft for D142, 25 September 2026. Companion to the frozen
[parent probe contract](P7_static_link_probe_contract.md), not a replacement.
This component supplies structural checks for the single unchanged static/M0
probe. It cannot authorize a query/compiler or return the full probe verdict.
The [runner proposal](P7_static_runner_proposal.md) remains separately pending.

## Interface and result boundary

Implement only `P7_static_link_probe_raw/static_artifacts.py`, using Python's
standard library, with no file, process, clock, network or environment access:

```python
validate_artifacts(artifacts: dict[str, bytes]) -> dict
```

Require an actual dict with exactly these seven string keys; each value is
nonempty bytes, not bytearray/memoryview. Reject every malformed or unsupported
input with ValueError, without mutating the input. Import has no side effects.

| Key | Maximum bytes | Meaning |
|---|---:|---|
| app.ino.elf | 16777216 | Final ELF |
| app.ino_debug.elf | 16777216 | ELF before strip-debug |
| app.ino_temp.elf | 16777216 | First link, before empty static rodata fragment |
| app.ino.bin | 786416 | Raw flat payload |
| app.ino.bin-zsk.bin | 786432 | Flat payload plus 16-byte header |
| app.ino.elf-zsk.bin | 16777216 | Diagnostic metadata-patched ELF |
| app.ino.map | 16777216 | Retained nonempty link-map bytes |

These finite host-input limits bound parsing, not firmware capacity changes.
The map is hash-bound for the subsequent source/disassembly review; this function
does not parse it or treat its existence as proof of entry input-section order.

On success return a JSON-serializable dict with these exact top-level keys:

- `status`: literal `STATIC_LAYOUT_PACKAGE_PASS`.
- `entry`: integer 0x08100011.
- `flash`: `{start: 0x08100010, end: <exclusive load end>, remaining: <0x081c0000-end>}`.
- `ram`: `{start: 0x20013890, end: <complete .bss end>, remaining: <0x20053890-end>}`.
- `data_copy`: `{source: <_sidata>, destination: <_sdata>, bytes: <_edata-_sdata>}`.
- `bss_zero`: `{start: <_sbss>, end: <_ebss>, bytes: <_ebss-_sbss>}`.
- `sections`: final ELF nonempty allocated sections in address order, each
  `{name, type, flags, address, size, alignment, load_address}`; load_address is
  null for NOBITS. This preserves final BSS padding separately from zero extent.
- `weak_undefined`: sorted union of nonempty undefined weak-symbol names from
  all three ELF forms, for
  mandatory later call/reference classification, not accepted runtime bindings.
- `artifacts`: each input name mapped to `{bytes, sha256}`.

Success explicitly leaves source/run freshness, actual instruction semantics,
native symbols/wrappers/heaps, constructors, ABI sizes/offsets, loading and runtime
unproved. The full `STATIC_ARTIFACT_PROBE_PASS` still requires every parent-contract
item and independent review of the source-bound real build. No caller-supplied
boolean may replace those checks.

## ELF identity and bounds

Decode ELF32 little endian directly from bytes. All three ELF inputs must have
magic, class1, data1, ident/version1, System V OSABI0/ABIversion0/zero ident padding,
ET_EXEC2, EM_ARM40, e_version1, e_entry0x08100011, and **exact e_flags0x05000400**.
This EABI5/hard-float expectation is derived from the pinned executable loader,
recipe and Arm ABI, not an observed static app. `.ARM.attributes` and descendants
must be absent as required by the pinned static DISCARD clause.

Require e_ehsize52, e_phentsize32, e_shentsize40; ordinary nonextended counts,
1..64 program headers and 1..4096 sections. Every table/file-backed extent must
fit the input; integer extents must stay within the 32-bit address space. Reject
overlapping header/table extents. Section0 must be the all-zero null section.
e_shstrndx selects a STRTAB; section names must terminate within it and be ASCII.
Each decoded section/symbol name is at most4096 bytes; reject a longer name.
Require unique nonempty section names. Nonzero alignment is a power of two;
allocated addresses and file-backed offsets obey their section alignment.
Reject overlap of nonempty file-backed section extents or with ELF/header tables.
NOBITS has no bytes to read but its offset must be within the file.

Reject nonempty REL/RELA sections in this first structural component, even if
non-ALLOC: none is silently classified as harmless. Reject DYNAMIC, DYNSYM, any
TLS flag/section, GOT/PLT sections and `.ARM.attributes` even when not allocated.
The forbidden name predicates are prefixes `.tdata`, `.tbss`, `.got`, `.igot`,
`.plt`, `.iplt`, and exact `.ARM.attributes` or prefix `.ARM.attributes.`.
This is a stop for unexplained output, not a new linker option removing evidence.
Nonallocated PROGBITS/SYMTAB/STRTAB/NOTE or empty REL/RELA sections may remain
subject to bounds and the explicit forbidden names/types/flags. Other types
fail. This does not interpret arbitrary PROGBITS metadata as validated debug
information. NULL is permitted only at index0.

Allowed program-header types are NULL0, LOAD1, PHDR6, GNU_STACK0x6474e551 and
ARM_EXIDX0x70000001. Reject other types, including INTERP/DYNAMIC/TLS. Non-NULL
headers need file bounds, filesz<=memsz, power-of-two-or-zero alignment and
p_vaddr/p_offset congruence. LOAD flags use only R/W/X bits. Reject executable
GNU_STACK. Every nonempty LOAD VMA extent must lie wholly in the flash-payload
or RAM interval below; LOAD VMAs must not overlap. Its file-backed physical
extent must lie in flash. No ELF-header mapping before the flash payload start
is accepted. Each LOAD must contain at least one nonempty allocated section.
Nonempty LOAD physical file-backed extents must not overlap each other. Each
section's LOAD needs READ and any WRITE/EXEC permission declared by that section.

## Named allocations and ELF/BIN mapping

| Output section | SHT type | Allowed exact flags | Placement |
|---|---|---|---|
| .text | PROGBITS1 | 6 (ALLOC,EXEC) | Flash, first at 0x08100010 |
| .static_thread_data_area | PROGBITS1 | 2 or 3 | Flash |
| .preinit_array | PREINIT_ARRAY16 | 2 or 3 | Flash |
| .init_array | INIT_ARRAY14 | 2 or 3 | Flash |
| .fini_array | FINI_ARRAY15 | 2 or 3 | Flash |
| .rodata | PROGBITS1 | 2 | Flash |
| .ARM.extab | PROGBITS1 | 2 | Flash |
| .ARM | ARM_EXIDX0x70000001 | 2 or 130 | Flash |
| .data | PROGBITS1 | 3 or 7 (script includes .ramfunc) | RAM; flash LMA |
| .bss | NOBITS8 | 3 | RAM |

Flash is [0x08100010,0x081c0000); RAM is [0x20013890,0x20053890).
Require nonempty .text/.data/.bss. Optional table/rodata/exception sections may
be absent/empty. Reject every other allocated section, including zero-size
orphans. Validate even empty named sections' declared type/flags/alignment.
All nonempty allocated VMA extents are disjoint and in their assigned region.
.data begins at RAM origin; .bss follows .data without overlap. .bss end includes
the script's final padding and must be 1024-byte aligned. No RAM segment may
extend beyond that end or before RAM origin; no flash segment beyond load end.

Each nonempty allocation belongs to exactly one LOAD by VMA. For file-backed
sections its bytes must fit that segment's filesz and have matching offset/VMA
displacement. LMA is p_paddr+(sh_addr-p_vaddr); it must fit flash. Flash sections'
LMA equals VMA. All file-backed LMA extents are disjoint. Reconstruct the flat BIN
from the lowest LMA (exact payload start) through the highest exclusive LMA end,
placing exact section bytes and zero-filling only gaps between those extents.
Require exact BIN length/content; trailing bytes and nonzero gap bytes fail.
Segment padding is accounted for by the same bounds; it is not added as data
unless covered by a file-backed section. Require at least two text bytes.

Final/debug/temp normalized allocated records (name/type/flags/VMA/size/alignment,
LMA and bytes) and entry must match exactly. File offsets and nonallocated debug
content may differ. Static rodata generation produces an empty script, and the
second link uses the same objects/options; --strip-debug must preserve allocations.

## Essential symbol consistency

Each ELF has exactly one well-formed SYMTAB with 16-byte entries, size a positive
multiple of16 with at most65536 entries, a valid linked STRTAB and bounded,
terminated ASCII names; its
first symbol is all zero. Its sh_info is in1..symbol_count and separates only
LOCAL entries before that index from only nonlocal entries at/after it. Admit
STB_LOCAL0/GLOBAL1/WEAK2, STT_NOTYPE0/OBJECT1/FUNC2/SECTION3/FILE4 and st_other0..3;
reject other bindings/types/reserved visibility bits. SECTION and FILE symbols
must be local; SECTION must name a real section and FILE must use SHN_ABS. Reject
invalid section indices, COMMON/extended-index symbols, and nonempty named
undefined non-weak symbols. Undefined weak symbols are reported, not assumed used.
No symbol-content interpretation relies on debug information. Empty-name section
symbols are permitted. Duplicate local names are permitted; each essential name
below must resolve uniquely to a defined symbol (section-relative or ABS).

Require `entry_point` to be STT_FUNC at0x08100011 in .text with positive size
contained in that section, handling the Thumb bit explicitly. Require `_sidata`
equal .data LMA, `_sdata`/.data start and `_edata`/.data end; all copy addresses and
lengths are multiples of4. `_sbss` equals .bss start; `_ebss` is four-byte aligned
within .bss, and rounding it up to1024 equals .bss end. These five values and the
entry symbol must match across the three ELF forms. This checks initialization
extents, not the actual memcpy/memset instructions. Constructor/static-thread
symbol tables and instruction/order inspection remain a subsequent explicit
artifact audit; no assumed empty range can satisfy that audit.
That audit must also show the app's strong main prevails over syms-static.ld's
PROVIDE(main) fallback; it must not demand every unreferenced PROVIDE alias or
fini bound. Source order is diagnostics, copy, zero, preinit, init, main;
main performs variant/static-thread initialization before setup/loop.

## Exact packaging

The 16-byte flat header is zero except byte7=1, bytes8..11=full packaged length
as little-endian uint32, bytes12..13=little-endian0x2341, byte14=0x02.
Byte15 remains0; no debug/Immediate/wait bits. Flat ZSK equals that header followed
by the exact raw BIN; raw BIN must not begin with ELF magic. Total <=786432.

Diagnostic ELF-ZSK equals final ELF with ONLY bytes7..15 replaced by the same
metadata pattern (length is the ELF-ZSK's length). No extra header is prepended.
Its first seven bytes and bytes16..end remain exact. It is never the direct-entry
upload form. Both pairs must pass; seven mutually consistent historical files
alone do not establish freshness, which belongs to the runner.

## Evidence and independent tests

Pin exact source links from D140/D141; no new source download/archive required:
memory-static.ld, build-static.ld, main.cpp and the reviewed packager at
P7_static_link_research_sources/. Read the Arm ABI and GNU ELF/BIN definitions:
[Arm ELF ABI 2025Q4](https://github.com/ARM-software/abi-aa/blob/2025Q4/aaelf32/aaelf32.rst),
[ELF program headers](https://refspecs.linuxfoundation.org/elf/gabi4+/ch5.pheader.html),
[GNU objcopy](https://sourceware.org/binutils/docs/binutils/objcopy.html).
Zero-filled inter-section gaps are the reviewed expected raw-BIN form, not a
claim that arbitrary linker padding is zero or that a mismatched image may pass.

Before implementation execution, a separate author freezes small synthetic ELF
fixtures and tests from this interface/spec, without reading implementation.
Cover a real gap and data LMA != VMA, final BSS padding, strip/debug differences,
all identity/table/bounds/overlap/type/flag/orphan/relocation/TLS/symbol failures,
packaging fields/content/length, all7 inputs and pure/no-mutation behavior.
No compiler, file I/O, giant fixture, production-policy or established-test edit
is necessary for these tests. Preserve first failures; do not weaken an oracle
to accept an unexpected actual image. Separate review before scope adoption;
then host tests and code review before any later full-probe adoption.
