# D139 unchanged default/M0 qualification: compile PASS, modeled fit FAIL

2026-09-24. **The current full default app compiles, but fails the conditional
pristine-loader model by592 bytes.** Exactly one authorized default-startup,
MATCH0/MOTORS_ALLOWED0 compilation ran with `--jobs 1`. No repair, second
compilation, upload, reset or MCU/native-I/O action followed. Default full-app
fit remains blocked; the two older optimization candidates remain unadopted.

## Exact source and artifact

Production remains first D138 implementation `d19f8964`, closed in `e16e6a57`.
The current final687-input host freeze is `P7_readiness_raw/freeze_final.json`
SHA256 `0fe188b7f8d6d179c85d7beff1a152245ab2455ba015baea9d2a4b82d38ce839`.
All103 current source hashes,102 staged/remote hashes and five native tool/policy
assets were bound separately; no older configured-test freeze was substituted.

- Source/stage: `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
- Checked run: `52b4ba3a377b40efa3715c8f609ef0fb`.
- Final [ELF](P7_default_qualification_raw/app/app.ino.elf),177100 bytes:
  `72a8bfcd320e8bfff7e5bcc6ef8607a98f9033866f3fa3d2be2cb95433e42f1d`.
- Debug ELF: `e68ed7508190c35fb841816faf60b47246e7a7ab4f62a8344e90ba776ef93bd4`.
- ZSK: `5b40026825ed851e27f185cb0a62d5f091c02122d620a6b68dad43201bd48f96`.
- Packaged loader: `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

`python -B state/analysis/P7_default_qualification_raw/compile_target.py` ran
19:26:31–19:30:22 UTC, exit0, through current checked board tooling. Actual argv
uses `arduino:zephyr:unoq`, default startup, exact C/C++ flags
`-DMATCH=0 -DMOTORS_ALLOWED=0`, fixed discovery flag and `--jobs 1`.
CLI1.5.1/core1.0.0 and all18 installed dependency pins passed; no external library
or configuration overlay was introduced. See [actual commands](P7_default_qualification_raw/actual_remote_commands.jsonl)
and [checked policy receipt](P7_default_qualification_raw/app/receipt/verified.json).

The independently reviewed read-only adapter reused the existing exact stage;
it never called the deletion/restaging path. The fixed source constant and both
manifest-file pins passed. Root's21 independent controlled probes passed before
the compile, preserving actual source/stage hashes. The pre-execution identity
correction and first drafts remain in `draft_01/`. The later syntax-receipt update
changed only its scope and the two corrected helper/wrapper inspection entries;
it was AST-only, with exact before/after details in `syntax_receipt_update.json`.

## Ordered failure and comparisons

The unchanged retained `elf_review.py` model gives262736-byte hypothetical peak
consumption in the262144-byte pool. **First failure:** the4400-byte temporary
global-symbol allocation encounters only3824 bytes, a576-byte shortfall. A final
16-byte export copy produces the full592-byte hypothetical peak deficit. No
actual load was attempted. All persistent-flash peek alignments pass at base
`0x08100010`; copied regions need no prepadding.

| Exact profile | Compiler payload | Conditional peak | Span / deficit |
|---|---:|---:|---:|
| Historical D134 default |257320 B|262176 B|deficit32 B|
| Current D138 MATCH/Immediate |256440 B|261280 B|864 B span|
| **Current D139 default/M0** |**257848 B**|**262736 B**|**deficit592 B**|

Versus D134 default, text/payload grows528 bytes and four additional global
function/object symbols grow metadata allocation32 bytes: peak rises560 bytes.
Data, rodata and BSS payloads are unchanged. Versus current MATCH, text grows1336
bytes, default BSS adds72 and symbol metadata adds48: peak rises1456 bytes.
These are measured artifact differences, not an isolated source-change experiment.
The compiler's nominal4296-byte remainder omits required loader allocations.

[Full ordered account](P7_default_qualification_raw/app/ordered_account.json)
and [baseline comparisons](P7_default_qualification_raw/app/loader_account.json)
retain all regions and allocation details. Accounting returned0; the ordered
validator saved the complete negative account and then deliberately returned1
for failed fit. Its original stdout/stderr and real return code are retained.

## Target layout, imports and integrity

File-only GDB against freshly hashed current-default, D134-default and
current-MATCH debug ELFs returned0; no inferior or target connection was made.
All16 queried size/alignment pairs and79 queried legacy member offsets match
D134 default exactly. Current counts include three additional metadata offsets.
RobotInput remains192 bytes, RobotResult400, Robot2640, TransactionReport504,
Transaction162544, Runtime166376, DisplaySample36, AttemptRecorder159200 and
FrameBuffer126300. No recorder capacity or copied-result size changed.

The three new Boolean fields occupy old padding: RobotResult offset396 and
DisplaySample offsets33/34. Against current MATCH, all common offsets and15 of16
size/alignment pairs match; default Runtime has its existing72 additional bytes
(166376 versus166304). See [ABI comparison](P7_default_qualification_raw/abi_comparison.json)
and the three retained raw DWARF command/output folders.

All61 relocation-used imports resolve to nonzero exports in the freshly hashed
packaged loader. The local verifier reparsed the exact import set and source
binding. Source, import and layout commands all returned0. The final evidence
index binds these results and the expected negative fit-validator return1.

## Retention and stopped boundary

One final ELF is retained locally with compact receipts; checked debug/temp ELF
and ZSK remain on board Linux. Only233 disposable `.o/.d/.a` files from this
unique D139 build were removed after evidence capture (7369554 bytes, exit0).
All four checked remote artifact hashes matched again afterward. The local
102-file,753087-byte stage remains exact; no local deletion/restaging attempt or
older denied-cleanup retry occurred. Cleanup receipts support the coordinator's
storage ledger. No duplicate checkout or native object tree was copied locally.

This is a completed qualification with a negative fit result. The model assumes
the pinned32-bit loader, pristine contiguous pool, successful persistent peeks
and no extra/interleaved constructor allocations; it is not measured live RAM,
stack, fragmentation, loading, WCET or physical acceptance. No phase gate or
default-profile readiness follows. Stop here: any repair needs its own reviewed
scope and validation; D139 authorizes no repair or further compiler invocation.
