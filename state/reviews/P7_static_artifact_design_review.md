# P7 static artifact component design review

Date: 2026-09-25. Reviewer: separate reused-context, same-model Codex agent;
not a fresh-context, cross-model or human gate. Read-only design/source review;
no implementation, test execution, board query, compiler, upload or reset.

**Disposition: no open BLOCKER, MAJOR or MINOR in this bounded design.** The
interface is sufficiently concrete for independent fixtures and a separately
adopted pure host structural component. This review does not adopt the full
probe or claim that any real static image has passed these expectations.

## Exact scope reviewed

- Companion `state/analysis/P7_static_artifact_contract.md`: 12,193 bytes,
  SHA-256 `b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54`.
- Frozen parent `state/analysis/P7_static_link_probe_contract.md`: 11,554 bytes,
  SHA-256 `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae`.
- D139/D140/D141 dispositions and the retained static command reference were
  checked for the unchanged-source, dynamic-policy and execution boundaries.

The final companion includes the pre-freeze clarifications on the union of weak
undefined names, exact forbidden names, finite name/symbol counts, nonallocated
section types, symbol-table partition/bindings, deferred strong-main resolution,
LOAD physical non-overlap and LOAD/section permissions. No unresolved design
finding or requested scope expansion remains.

## Material checks

- **Identity and placement (companion lines 59-137):** the fixed ELF32/ARM/Thumb
  entry, named allocations, partition bounds, VMA/LMA separation and segment
  containment form a coherent conservative admission policy. The pinned script
  places `.entry_point` first and `.data` in RAM with its load image in flash.
  Its `.bss` includes `.noinit` and final 1024-byte padding. No impossible GNU
  output assumption was identified; these are explicit experiment expectations,
  not a claim to accept every otherwise valid ELF. Unexpected real output must
  stop the probe. GNU describes output placement by input alignment and `AT>`
  load placement separately from VMA. [GNU output addresses](https://sourceware.org/binutils/docs/ld/Output-Section-Address.html),
  [GNU load addresses](https://sourceware.org/binutils/docs/ld/Output-Section-LMA.html).
- **ABI and bytes:** `0x05000400` and odd Thumb entry are consistent with the
  reviewed hard-float executable expectation, but remain derived rather than
  observed static-app evidence. Allocated bytes are compared across the three
  ELF forms without requiring debug/file-offset identity. The static rodata
  generator emits an empty script; strip-debug is not permitted to change the
  accepted allocation image. BIN reconstruction uses LMA and excludes NOBITS;
  zero inter-section gaps are a frozen expected form, while bytes within each
  section remain exact. [Arm ELF ABI 2025Q4](https://github.com/ARM-software/abi-aa/blob/2025Q4/aaelf32/aaelf32.rst),
  [ELF sections](https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.sheader.html),
  [ELF program headers](https://refspecs.linuxfoundation.org/elf/gabi4+/ch5.pheader.html),
  [GNU objcopy](https://sourceware.org/binutils/docs/binutils/objcopy.html).
- **Initialization boundary (lines 155-167):** required copy/zero symbols match
  the pinned script and `main.cpp:100-103`; `_ebss` deliberately excludes final
  BSS padding. Actual instructions, constructor/static-thread ranges and order,
  strong app `main`, absolute native references, wrappers, heaps and ABI layouts
  remain mandatory later audit work. Unreferenced PROVIDE aliases and fini
  bounds are not incorrectly demanded as universal GNU output.
- **Packaging (lines 171-180):** both header layouts match the retained writer:
  version at byte 7, full length at 8-11, magic at 12-13, exactly linked flag
  `0x02` at 14, zero byte 15; the flat form prepends 16 bytes and the diagnostic
  ELF form patches only bytes 7-15. The latter is not the direct-entry upload
  form. Exact payload equality and size checks do not claim freshness.
- **Parent obligations (lines 3-7, 51-55, 160-167, 179-200):** the structural
  status cannot become `STATIC_ARTIFACT_PROBE_PASS` by caller assertion. Source,
  tool/command identity, exclusive new outputs, stale-output rejection, native
  audit and the single terminal compiler-attempt rule remain in the parent and
  pending runner scope. The map is retained evidence, not parsed proof.

## Retained source identities

All paths below are under `state/analysis/`; each was read directly and rehashed.

| Source | SHA-256 |
|---|---|
| `P7_static_link_research_raw/build-static.ld` | `04be061156ebb88fa43537c811e0a8fdc2b721d1bcc0a1a9ac5990018536123e` |
| `P7_static_link_research_raw/memory-static.ld` | `cbe17b74e93d2a05f4e101366d036e6a9b3d89d400855349734d5419984d6341` |
| `P7_static_link_research_raw/syms-static.ld` | `f4f05a8a411196fad575360a1b6cc9f5f10a337864548e7387fb8580c4092d62` |
| `P7_static_link_research_raw/main.cpp` | `d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed` |
| `P7_static_link_research_sources/zephyr-sketch-tool_main.go` | `a4270be85f66b0f309a7c540917aa23820812bd04a5a6355863e70585aaabf4b` |

Independent fixture freeze, implementation, first host results and exact-code
review remain prerequisites to claiming this component complete. Full runner
adoption, properties query, native compile, artifact/native audit, loading and
runtime qualification remain pending. D139's 592-byte dynamic deficit, existing
production rejection of static input and all physical/human gates are unchanged.
