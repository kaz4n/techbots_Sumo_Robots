# P5 unchanged MATCH native evidence review

2026-09-24. **PASS — conditional pristine MATCH accounting and captured packaged
imports only. No material findings.** Independent of the native-evidence author;
this is a same-model, scoped local artifact review, not a human/cross-model review
or phase gate. No board/network/compiler action was performed by this reviewer.

## Verified evidence

All **42 indexed raw files (396062 bytes) and three dependencies** match their
indexed SHA-256 and byte counts, checked before and after the local review.
The index hash is
`e8950ba523b8f8f44b7ad8d7d8e9b969cb2e6d73b32d77cb954df4328fc54d1b`.
The reviewed report hash is
`131e2606ebf011eea628ccc7f6a615d1720eacabd326b11ca64a4b3607ef15f0`.

The source claim at `state/analysis/P5_match_native_validation.md:29` is supported:
the hashed working manifest has133 entries; all102 staged names map to it,
their current local bytes/lengths match, and independent staged-name/NUL/bytes
hashing reconstructs
`18cbf8bfd06168a5cef36af8c97d915c9df8d9c7578ea6e84522ea0b745f8e8d`.
The retained173820-byte ELF hashes to
`eae32ea373948ffcf8e24536819fdbc65288b9b2465d3071e606e38394b7ea72`,
matching the checked compile receipt. This does not re-establish a deployed image.

The actual-command journal contains exactly one successful original compilation.
It matches the archived command plus the recorded `--jobs 1` insertion, with
Immediate FQBN and exact C/C++ `-DMATCH=1 -DMOTORS_ALLOWED=1` flags. The discovery
flag is retained and no upload argument appears. The compiler's embedded output
states255752 payload bytes and6392 remaining; it also retains the low-memory
warning (`app/receipt/compile.stdout.json:2-3`) and an empty upload result at349.
These support the report's compile-only wording at23, not runtime execution.

## Independent arithmetic and imports

A separate direct ELF32/ARM decoder, without importing the author's loader model,
found16 sections and539 global function/object symbols. Applying the explicitly
pinned allocator assumptions from `state/analysis/P2_memory_loader_budget.md:24`
and38 gives255800 copied-region chunk bytes, including48 alignment/header bytes,
plus4760 bytes of bookkeeping/extension/maps/symbol/export metadata. Therefore:

`255752 + 4808 = 260560; 262144 - 260560 = 1584; 1584 - 4 = 1580`.

Every recorded allocation fits in order; region prepadding is zero. Nonrelocated
rodata, symbol/string tables and section-header peeks align at0x08100010.
Thus the report's1584 span/1580 payload at57 is consistent with the compiler's
6392 nominal remainder at40. These quantities describe different accounting;
neither is measured live free memory. Runtime166304, sources848 and dump-port208
are present; opener symbols remain and the stated abort-trace names are absent.
The different D134 default profile is1568 payload/1616 peak bytes larger, exactly
as reported; this does not establish a default-profile repair.

The independently decoded relocation set has62 used imports. All62 occur exactly
once in captured GDB stdout and resolve to nonzero addresses matching the stored
map. The packaged-loader hash agrees with the compile receipt:
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
The exact GDB argv has `-nx -nh -batch`, one file and only echo/value queries;
there is no target, inferior, run or upload command. The recorded host ADB daemon
restart is disclosed at `P5_match_native_validation.md:77`. This supports its
file-only import inspection at85/90, not the identity/state of a running MCU.

## Scope and reproducibility

The report explicitly retains pristine-pool, pinned32-bit loader, aligned peek
and no extra/interleaved constructor-allocation assumptions at59. Its opening
verdict at3 and closing limitations at109-112 make no default-fit, actual loading,
stack/live-RAM/WCET, upload, motor-run, hardware-acceptance or human-gate claim.
The ZSK value is a retained receipt hash; the local ELF was the binary directly
rehashable in this indexed bundle. No new ZSK/deployment verification is implied.

Local command, exit0:
`python -B state/reviews/P5_match_native_review_raw/check_evidence.py`.
The script only reads local inputs and writes its compact review result; indexed
inputs were unchanged afterward. It creates no binaries, snapshots or bytecode.

- `check_evidence.py` SHA-256:
  `6c17dc10bfe68dadd7fa315a88632890b2eb35b6eb92bc661593af46e44aadfb`.
- `check_result.json` SHA-256:
  `27f42bdbd8c8095027375c8a3ef32bdc9bd48a1761627cd585e9acdfa1d01686`.

No producer data, tests, implementation or shared ledger was edited. Only this
review and its compact local check script/result were added.
