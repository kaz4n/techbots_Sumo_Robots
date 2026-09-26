# D204 actual constant metadata ABI evidence

One fixed file-only attempt succeeded at clean reviewed HEAD
`d3bcfaa026e971c902f33c1f4c648338a6263677`, after source/host review ae662c11
and admission review 763b0c82. Check-only and execution both returned zero.
One transport ran four successful, reaped children: tool versions, complete
readelf header/sections/symbols, and guarded file-only GDB type/layout queries.
All 13 remote closing checks and independent local closure passed. First error
is null. No compile, upload, reset, MCU memory access or motor operation occurred.
D201 remains the latest flashed image.

The actual attempt ran 26 September 2026 at 13:22:50-13:22:52 Dubai. The command
used 6225 UTF-16 units against the unchanged 30000 limit. Fresh identity reports
UID1000/arduino, expected boot55c386b9, fixed CLI hash, no recognized conflicting
processes and13914439680 free board-home bytes. Eight artifacts plus readelf,
GDB, loader and TLS source passed closing checks, followed by board identity.

| Saved file under P7_motor_const_compile_raw/native_abi_static01 | Bytes | SHA256 |
|---|---:|---|
| inputs.json | 33427 | 9e8db724955f5bcf5c5e206d862ff445778b08c7a48808f447b14884d46f124c |
| result.json | 904847 | bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0 |
| abi.json | 5410 | 6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97 |
| local_result.json | 275 | 3cd224b237fc1b18586d7b2fb22c2a47833a801fea06b96b338027102db5d55d |

The independently checked complete .symtab has2299 rows. Current raw/debug ELF
hashes remain390b69c1/b3520cac. The new observation places Runner at0x20013960,
169736 bytes/alignment8, and the separate SETTLE report at0x2003d3e8,28bytes/
alignment4, both in section5. The report is wholly within checked zero-BSS and
outside Runner. These coordinates were freshly observed from D203 files even
though they equal the historical image's coordinates.

The exact223 GDB expressions contain23 SIZE/ALIGN/LAYOUT groups in total:
22 TYPES plus terminal bool. Earlier shorthand saying23 plus bool was ambiguous;
there is no extra group or query change. All11 Runner offset queries, Sample12/4,
Report28/4, Reason1/1, eleven SETTLE offset/width pairs and nine enum values match.
The raw readelf and GDB encodings are preserved; decimal size normalization is
restricted to a private parser copy and recorded in the ABI summary.

| Exact emitted symbol (short name) | Thumb symbol value | Bytes |
|---|---|---:|
| candidatePeriod | 0x08110c91 | 20 |
| publishSettle | 0x08110cd5 | 60 |
| mapChannel | 0x08110da1 | 264 |
| UnoQPort::timerValid | 0x081111a5 | 384 |
| UnoQPort::writePwm | 0x08111411 | 228 |
| UnoQPort::bankValid | 0x081114f5 | 68 |
| UnoQPort::settle | 0x08111539 | 292 |

The exact candidateRate, expectedRate and expectedPeriod names have zero rows.
This does not establish absence of inlined calculations, clones or division in
consumers. Current instruction ranges must be derived from this symbol table;
no D199 range/address may be silently reused. A separate adopted entry scope
and actual semantic review will investigate emitted constant selections and
preserved live checks. No speedup, SETTLE repair, WCET, atomic publication or
physical/human gate is established here.

Root closing abi_native_closing01.json (6866 bytes / e181ebe1) verifies238 host,
eight scope and143 runtime local pins, exact command/stream identities and all
13 ordered closing rows. It retains eight native owner files/1857008 logical
bytes; C: free space was9487302656 bytes. No duplicate ELF/debug download,
manual cleanup or reclaimed-byte claim. The first read-only coordinator audit
stopped on an incorrect assumption that serialized dictionary order retained
runtime insertion order; the corrected audit reconstructs the exact original
artifact/tool/loader/TLS order. No reader, oracle, result or native run changed.

Separate actual-evidence review PASS: reviews/P7_motor_const_abi_actual_review.md,
10178 bytes / 4cd28fe8ce3b689319da5ddb42739c664fd0e4bcdc2552b521ee23b8b3331411.
It independently reconstructs the submitted program and all expressions,
markers, numeric answers, symbol rows, closing order and current pins. Numeric
remote stamp arrays were internal; saved PASS rows establish the guarded checks
completed, without exposing a separate numeric stamp inventory. No open material
finding. The native ABI owner is consumed; preserve raw receipts and do not rerun.
