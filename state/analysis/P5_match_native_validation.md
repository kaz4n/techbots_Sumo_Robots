# Unchanged MATCH/Immediate native artifact validation

2026-09-24. **PASS_CONDITIONAL_PRISTINE_MATCH_FIT_ONLY** for the archived,
unchanged production MATCH/Immediate artifact. Local ordered accounting gives
260560-byte peak consumption in the 262144-byte loader pool: 1584 bytes of free
chunk span and 1580 bytes of largest possible payload. These are conditional
model values, not measured live RAM or a runtime/physical acceptance result.

## Artifact and source binding

- Production implementation: `2d924f1f`; archived source-manifest HEAD:
  `70c964a71182e459bd58ac16ae9fd06cb8dc7c72`.
- Staged source SHA-256:
  `18cbf8bfd06168a5cef36af8c97d915c9df8d9c7578ea6e84522ea0b745f8e8d`.
- Checked compile receipt: `e555c86831ce4f74a5e366c897fd856f`.
- Final ELF: 173820 bytes, SHA-256
  `eae32ea373948ffcf8e24536819fdbc65288b9b2465d3071e606e38394b7ea72`.
- Archived ZSK hash:
  `f632e618409cf76c8461b404a25bf36768ae9b31b8ef3b1d0ec1e2eab071a47d`.
- Pinned packaged-loader hash:
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

The existing compile ran 12:03:11–12:07:02 UTC, exit 0, with
`arduino:zephyr:unoq:wait_linux_boot=no`, exact C/C++ flags
`-DMATCH=1 -DMOTORS_ALLOWED=1`, fixed discovery flag and one job. It was
compile-only. This validation did not repeat compilation. The archived actual
remote-command receipt contains exactly one original compiler invocation.

The local verifier checked the 133-entry working manifest's hash against that
compile record, mapped all 102 staged files to its entries, rehashed matching
current source bytes and reconstructed the exact staged-source digest. It also
rehashes the retained final ELF and loader-model source. This binds the archived
artifact and receipts; it does not assert that the ELF was deployed or loaded.

## Loader account

The unchanged prepared `account_target.py` ran locally, exit 0, using the retained
`state/reviews/P2_bridge_dependency_review_raw/elf_review.py` model
SHA-256 `1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`.
Compiler payload is 255752 bytes and its nominal remainder is 6392 bytes.
Required region and metadata allocations reduce the modeled remaining span to 1584.

| Allocation, in loader order | Chunk bytes |
|---|---:|
| Initial bookkeeping |88|
| Extension object |200|
| Section map |136|
| Text |86216|
| Data |216|
| Rodata |2136|
| BSS |167208|
| Exported-symbol region |16|
| Init array |8|
| Temporary global-symbol table |4320|
| Export copy |16|
| **Peak consumption** |**260560**|
| **Remaining span / largest payload** |**1584 / 1580**|

Every ordered allocation fits the remaining modeled contiguous tail. The
nonrelocated rodata, symbol/string tables and section headers pass their aligned
peek checks at the established persistent-flash base 0x08100010. No copied-region
prepadding occurs. Assumptions remain the pinned non-Harvard 32-bit loader,
pristine pool, successful persistent peeks, and no additional/interleaved
constructor allocations. The account does not measure stack, fragmentation,
live free memory, transport growth, startup completion or WCET.

Local ELF symbols retain Runtime 166304 bytes, native sources 848 and the 208-byte
native dump-port object. Openers remain present and P5 abort-trace symbols are
absent, as expected for ordinary MATCH. Compared with D134's different default
M0 profile, payload is 1568 bytes smaller and modeled peak 1616 bytes smaller;
that comparison does not establish a fix for the default profile.

## Current packaged-loader import inspection

The prepared import script requires board Linux file access. After the parent
explicitly authorized a narrow read-only inventory and packaged-file check,
ADB inventory found the authorized serial 2629958581. The client automatically
restarted the **host ADB daemon** because server/client versions 40/41 differed;
the exact output is retained. No board service, MCU reset or upload was requested.

`collect_imports.py` then ran unchanged, exit 0. Its hash command and file-only
GDB command both returned 0. The packaged-loader hash matched the compile policy;
GDB itself hashed to
`8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`.
All 62 imports actually referenced by ELF relocations resolve to nonzero
`__llext_sym_*` export addresses. The local verifier independently reparsed that
captured GDB stdout and matched the exact used-import set. No missing import was
silently substituted from another profile's historical receipt.

GDB used `-nx -nh -batch` against the packaged ELF file with expression queries
only. It created no inferior or target connection and performed no MCU access.
This checks packaged exports, not the identity or state of a running MCU image.

## Evidence and limits

Compact evidence is under `P5_match_native_raw/`:

- `app/loader_account.json`, `app/ordered_account.json`: exact account and order.
- `account_run.json`, `account_validation_run.json`: actual exits and retained
  local verification command/source; corresponding stdout files preserve results.
- `import_inventory.json`, `import_run.json`, `import_exports.json`: actual
  inventory, script/hash/GDB exits, commands, tool/loader hashes and export values.
- `validation_index.json`: hashes of this report, retained raw files and model
  dependencies for separate review.

Accounting, current import inspection and final local verification returned 0.
No new firmware, tests, configuration, tool policy or ledger was edited. No
compile, upload, MCU operation, motor run, cleanup or whole-source snapshot was
performed during this task. The two earlier default-fit candidates remain
**UNADOPTED** with their 24-byte and 32-byte failed-fit evidence intact; no third
candidate was created. Default native fit, actual loading/free RAM/stack/WCET,
physical acceptance, motor-run permission and human phase gates remain separate.
