# D145 static ELF TLS diagnosis: source evidence

2026-09-25, Asia/Dubai. Read-only same-model research, not gate review. No board
command, compilation, validator/oracle edit or admission change. D144's rejection
remains valid under its frozen D142 contract.

## Observed final ELF

Checked local `P7_static_link_probe_raw/diagnosis-v1/app.ino.elf`: 170616 bytes,
SHA256 `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
The D145 `diagnosis-v1/result.json:1` binds it to the D144 run and records one
checked read, zero queries/compiles and no postcheck errors. Rehashed locally;
WSL GNU readelf 2.42, `readelf -SWlr <file>` and `readelf -sW <file>` returned 0.
No generated disassembly or duplicate ELF was saved by this research task.

All six unsupported entries have GLOBAL binding, TLS type, DEFAULT visibility,
ABS section index and size 0:

| Symbol-table index | Name | Value |
|---:|---|---:|
| 1557 | `_TLS_MODULE_BASE_` | `0x08` |
| 1598 | `errno` | `0x14` |
| 1615 | `_localtime_buf` | `0x1c` |
| 1872 | `_strtok_last` | `0x18` |
| 1927 | `z_tls_current` | `0x10` |
| 2071 | `_rand_next` | `0x08` |

The final file has nine sections, three program headers (two LOAD, GNU_STACK),
no section with SHF_TLS, no PT_TLS and no remaining relocation section. This
identifies its format, but does not establish that linked instructions never
access native thread-local data. Completed static linking can resolve references
and leave no relocation record.

## Primary definitions and the Arduino generation mechanism

The [generic ELF symbol specification, section 5.3](https://gabi.xinuos.com/elf/05-symtab.html#symbol-type)
assigns STT_TLS value 6. Its defined value denotes a TLS offset, not an ordinary
virtual address; TLS uses special relocation semantics. Do not treat `0x14` as
an invalid low RAM address, or size 0 as evidence that the underlying variable
has no storage. [Arm AAELF32, section 5.6.1.9](https://github.com/ARM-software/abi-aa/blob/main/aaelf32/aaelf32.rst#5619-relocations-for-thread-local-storage)
distinguishes TLS-block-relative and thread-pointer-relative relocations.
[Arm RTABI32, section 5.3.5](https://github.com/ARM-software/abi-aa/blob/main/rtabi32/rtabi32.rst#535-thread-local-storage-new-in-v201)
defines `__aeabi_read_tp` as the thread-pointer accessor. Specifications were
read live on this date; they do not certify this installed runtime.

At official ArduinoCore-zephyr commit
`79b3f1afdad455f55e4a25030953617152c0227c`,
[extra/gen_provides.py:198-202](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/extra/gen_provides.py#L198)
collects TLS symbols separately and excludes them from PROVIDE generation.
[Lines 268-290](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/extra/gen_provides.py#L268)
generate global symbols with type `%tls_object` and constant `.set` values.
The generator adds two pointer widths for the TCB: 8 bytes on ELF32. It records
the original size only in a comment, emitting no storage or `.size` directive.
This explains how zero-size absolute TLS offsets can be produced without app
TLS allocation. [extra/build.sh:122-124](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/extra/build.sh#L122)
generates variant `tls-syms.S` from the firmware ELF, separately from both
symbol linker scripts. [GNU as `.type`](https://sourceware.org/binutils/docs/as/Type.html)
documents `tls_object` as STT_TLS.

**Inference, not yet installed-source proof:** the six entries are consistent
with generated firmware TLS aliases. The exact installed `tls-syms.S`, its input
object and the D144 map were not collected or examined by this task. No claim
that all six are unused, safe or correctly bound follows from that inference.

## Retained installed provenance and limits

- `P7_static_link_research_raw/syms-static.ld:1-6` records generation from
  `zephyr.elf` SHA256
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
  Its rechecked SHA256 is
  `f4f05a8a411196fad575360a1b6cc9f5f10a337864548e7387fb8580c4092d62`.
  None of the six names occurs in that file. Its PROVIDE aliases therefore
  cannot directly explain these entries; the official separate assembly
  generation is the evidence-backed candidate.
- `P7_static_link_research_raw/build-static.ld:75-93`, rechecked SHA256
  `04be061156ebb88fa43537c811e0a8fdc2b721d1bcc0a1a9ac5990018536123e`,
  consumes `.tdata*` into `.data` and `.tbss*` into `.bss`. Absence of sections
  named `.tdata`/`.tbss` alone is consequently insufficient to establish the
  absence of application TLS contributions; inspect input sections in the map.
- `P7_static_link_probe_raw/static_reference.json` fixes the static linker
  scripts and post-link `--strip-debug` recipe. The retained installed
  `P2_bridge_dependency_raw/installed/core/platform.txt:44-52,88,138,145-152`
  documents picolibc's statically initialized `errno`, assembler compilation,
  static scripts and stripping. This is retained provenance, not a new installed
  byte check and not proof that a particular TLS object reached this link.
- Historical `P2_dump_raw/native/native_symbols.txt:27,33,695,698,707,710`
  lists the same names at offsets 0, 0, 8, 12, 16, 20 respectively. Adding 8
  gives all six current values. This is corroboration only; do not substitute
  that historical listing for a freshly identity-bound packaged symbol check.

## Recommended next evidence, before any admission proposal

1. Obtain a separately scoped read-only identity-bound view of installed
   `variants/arduino_uno_q_stm32u585xx/tls-syms.S`, the existing D144 map and its
   contributing TLS assembly object. Bind the assembly header to the exact
   packaged firmware hash; verify each name, binding, type, visibility, size,
   index and value. Check debug/temp/final forms consistently.
2. Account for all `.tdata*`/`.tbss*` input contributions and any discarded TLS
   allocations. Inspect existing input-object relocations and final instructions
   to determine actual TLS references; no-relocations in the final ELF does not
   answer that question. If used, validate thread-pointer access, offset and
   native storage/lifetime against the packaged implementation.
3. Preserve the frozen rejection. If evidence supports an amendment, propose a
   narrowly identity-bound inherited-symbol rule with independent positive and
   negative tests (wrong/missing/additional/duplicate symbol, altered value/type/
   binding/visibility/size/index, application TLS allocation and runtime TLS
   segment/relocation). Do not broadly admit arbitrary type 6 or modify the
   original oracle to make this image pass. Structural acceptance would still
   leave entry/constructors/native ABI/runtime and physical gates pending.

Only this compact note was created. No downloaded repository/tree or additional
binary copy was retained; keep the note as source/provenance evidence.
