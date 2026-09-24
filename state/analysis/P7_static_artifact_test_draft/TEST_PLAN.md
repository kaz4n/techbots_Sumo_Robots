# Independent static artifact tests

This plan derives from the public D142 artifact contract and its frozen parent.
The author has not read artifact-validator implementation bodies or executed a
validator. The coordinator supplied the reviewed adoption contract hash
`b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54`.
The matching freeze manifest controls later coordinator-owned host execution.
No board, compiler or artifact-origin claim follows.

## Positive synthetic packet

Construct the seven required inputs entirely in memory. Each ELF is under 4 KiB
and has ordinary ELF32 little-endian ARM ET_EXEC headers, the exact hard-float
flags, a small symbol table, and two LOAD segments plus nonexecuting GNU_STACK.

- Flash origin is 0x08100010. Eight text bytes occupy origin..origin+8;
  eight rodata bytes occupy origin+16..origin+24. The eight-byte gap is real.
- Eight data bytes have VMA 0x20013890 and LMA flash-origin+32. This adds another
  eight-byte gap and distinguishes copying from load addresses.
- BSS begins at RAM-origin+8. Its zero extent ends at RAM-origin+24, while its
  section and RAM LOAD end at 0x20013c00. The positive oracle therefore requires
  final 1024-byte alignment padding to count toward used RAM without extending
  the zeroing range.
- Final, debug and temp ELF file offsets differ. Debug/temp include distinct
  nonallocated debug contents; normalized allocations and essential symbols match.
- Null and empty-name section symbols, duplicate local names, and a named
  undefined weak symbol exercise explicit permitted symbol forms.
- Flat BIN is exactly 40 bytes, with zero gaps and exact section bytes. ELF gap
  bytes may be nonzero because only allocated section bytes reconstruct the BIN.
- Both package forms are constructed independently from the exact 16-byte field
  specification. The diagnostic form replaces ident bytes 7..15 only.

Expected output is checked in full: exact keys/status/entry, flash/RAM span and
remaining counts, distinct data source/destination, shorter BSS zero extent,
section records, weak-symbol result, seven SHA-256 and byte-count receipts.

## Structural rejection matrix

Every mutation starts from a valid small packet. Mutations that describe an ELF
layout flaw apply independently to all three ELF forms and regenerate diagnostic
packaging, so an unrelated final/debug mismatch or stale package cannot mask the
structural rejection. Dedicated mismatch cases deliberately alter only one form.

1. Input map type, missing/extra/nonstring keys, every empty/nonbytes value,
   finite byte limits, nonmutation, and import/call side-effect tripwires.
2. Every ELF identity field, class/data/ABI flags, entry Thumb bit, version,
   header/table sizes, zero/extended/excess counts, table bounds/overlaps.
3. Null section, string-table type/index/name bounds/termination/ASCII/duplicate
   names, invalid alignment, VMA/file-offset misalignment, file section bounds,
   section/section and section/header overlap, NOBITS offset beyond file.
4. Forbidden relocation/dynamic/TLS/GOT/PLT/attributes types or names, including
   nonallocated forms; unknown allocated sections including zero-size orphans.
5. Each named output's exact type/flags/region; required empty/missing output;
   flash/RAM bounds, disjointness, data origin, BSS ordering/end alignment.
6. Program type/flags/stack execute, alignment/congruence, filesz > memsz, bounds,
   32-bit wrap, overlapping LOADs, empty ownership, file-backed physical bounds,
   excessive RAM/flash segment extents and ambiguous/missing allocation ownership.
7. LMA/VMA and file displacement, segment filesz coverage, overlapping LMAs,
   flash LMA != VMA, BIN wrong length/content/gaps/trailing bytes/ELF magic.
8. SYMTAB count/type/entsize/linked table/bounds/name/index errors, null symbol,
   strong undefined names, COMMON/extended indices, essential missing/duplicate/
   undefined/incorrect address; entry type/Thumb/address/size, copy alignment,
   zero-range bounds and padding rounding; duplicate locals remain positive.
9. Final/debug/temp normalized allocation or essential-symbol mismatch, while
   offset/debug-only differences remain positive.
10. Every package field/flag, length, payload byte, prepended diagnostic header,
    diagnostic first-seven/trailing-byte drift and independently bad pair.

## Resolved contract clarifications

The final contract defines sorted weak-name union across all three ELF forms,
explicit forbidden prefixes, the SYMTAB local/nonlocal split and admitted
binding/type/visibility values, and the nonallocated section type allowlist.
It also requires disjoint file-backed LOAD physical spans and adequate READ,
WRITE and EXEC permissions for every contained allocation. A distinct negative
case overlaps only segment padding while section load extents remain disjoint.

The coordinator permits one transient 16 MiB + 1 immutable RAM buffer for the
input limit rejection loop; it is reused sequentially and never written to disk.
Ordinary fixtures remain tiny. Numeric table bounds and 4096-byte name decode
bounds use compact malformed inputs. The tests prewarm standard-library imports
before import/call tripwires, then forbid component file/process/clock/network/
environment effects. No bytecode or binary fixtures are saved by the test loader.
