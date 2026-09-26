# D207 read-only admission program preparation review

Status: PASS, no material findings in the prepared source/data. This review admits the single specified nonprivileged read-only observation after D207 source/host acceptance. It does not claim that the observation occurred or that the board, files, free space or owner absences are currently verified. A successful actual receipt and independent actual-scope admission still precede any inhibited upload/capture.

The reviewer inspected these files only after the native oracle FINAL barrier closed. No tests, subject imports, device commands, authentication, compiler, upload, reset, MCU access or cleanup were performed. Only this new review file was written; historical reviews, failures, consumed owners and other contributors' files are preserved.

## Exact prepared inputs

| Item under `state/analysis/P7_motor_const_run_raw/` | Bytes | SHA-256 |
|---|---:|---|
| `admission01_readonly.py` | 23886 | `769933e9baa0c0b9fa61dc72017bd3585a8680f9e3238fe65b362a60fb2fc198` |
| `admission01_intent.json` | 34163 | `af1fbacd2835d983ce956e5a6927fd34071be9491dbe5eef49a4b4da1b9478d9` |
| `admission01_derivation.json` | 5868 | `5bd21fd8b5524afb0d019ae754f12ed2b0d1cf7e8180747d527d5833bce37993` |
| `preparation.json` | 9988 | `519a95f623e3c463842217cdb568cb1909941974b49c36453bfc8f8ea1f8449e` |

The D201 source template is `state/analysis/P7_motor_settle_run_raw/admission02_readonly.py`, 23871 bytes / `fecc2ba16719a287077fe009fa0ef8b586a6a4214240d6cac54a3467aa16fd33`. Its corresponding intent is 33571 bytes / `e9a304ff57b58f4da77ad731d4c976e3b8de7a3b9d7500958f978e1ab0e81d47`. These are the corrected accepted D201 admission02 lineage, not a substituted failed observer.

The accepted D206 result is `state/analysis/P7_motor_const_cleanup_raw/cleanup_root05_actual_result.json`, 6367 bytes / `3b8f035a6b282ada5a5fbf5992a5343d27a3dc245962ee7f64032757420e11e8`. Its independent actual review is `state/reviews/P7_motor_const_cleanup_actual_review.md`, 8082 bytes / `aaede1e1d8a0a8deef6b48de191abe76cf06bb2779f6ce4fa810c4467544e9c8`. The preparation uses this completed root05 evidence; it neither authorizes another cleanup nor reuses root04 evidence as current.

## Independent reconstruction

All local input byte/hash pairs in both the intent and derivation matched. The reviewer reconstructed the actual program from its pinned predecessor using exactly eleven changes, checking every one-occurrence replacement and every recorded intermediate before/after byte count and SHA-256:

1. Two D200/D201 comment labels become D206/D207.
2. Whole `pins`, compressed `packet`, and `files` assignment lines change to the current declared data.
3. The recipe name, cleanup stage, result filename, result byte length and result SHA-256 change to accepted D206 root05 values.
4. The consumed D201 run identifier changes to the fresh D207 run identifier.

The reconstructed full bytes equal the actual program. All remaining operational bytes are unchanged. AST inspection and literal decoding were data operations; none of the embedded sources was executed by the reviewer.

The embedded packet has exactly `cleanup_root05.py`, `cleanup_remoteocd04.py` and `static_remote.py`; its decoded byte/hash values match all three source pins and the accepted D206 staging intent. They are respectively 9601 / `1be147fe67bfafb60275ef1f741f05cfe2262be70c89b0eddbbfc3ec349837d4`, 7738 / `edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598`, and 33321 / `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`. The program checks packet identities before loading only the helper and recipe definitions. It never invokes the cleanup recipe or wrapper entry point.

The current preparation was independently reconstructed from D201 preparation through the adopted recursive identity/path replacements, the exact twelve current provenance byte/hash objects, two packaged-sketch pins and the raw-image pin. Canonical serialization exactly reproduces the 9988-byte file and expected hash. No digest-only provenance substitution remains.

The nineteen remote file pins equal the union of eighteen unique files in the current upload/capture bindings plus the fixed installed `p0_capture.py` parser (18880 bytes / `885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`). Seventeen installed/helper file records are byte-for-byte unchanged from the prior admission; only the two current build paths/pins differ. The raw image is 95352 bytes / `76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3`; the packaged sketch is 95368 bytes / `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7` under `app-motor-const-static01/build/`.

## Preserved observation boundary

The intent's argv prefix is the unchanged absolute installed Windows ADB executable, serial `2629958581`, `shell -T`. The remote argv is precisely `/usr/bin/env -i` with fixed HOME/USER/LOGNAME/PATH/LANG, then `/usr/bin/python3 -I -B -c` and the exact reviewed program text. The reviewer parsed the shell command as data and confirmed its final argument equals all 23886 source bytes. Windows command length, independently recomputed with `subprocess.list2cmdline` and UTF-16 code units including NUL, is 26145, below the 30000 limit. No command was dispatched.

Remote alarm remains 55 seconds; the outer intent allows 70 seconds. There is no credential input. Read-only root descriptor traversal and helper logical reads remain. The program verifies the expected Arduino UID/GID 1000 identity and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, reads the exact accepted root05 result through its hash, checks its successful status/no first error, rechecks the staged source hashes and retained original hashes, verifies all nineteen selected files, checks conflicting processes, requires at least 1073741824 available root-filesystem bytes and repeats the identity check. The root descriptor closes in `finally`.

The four required fresh absences are exactly `/tmp/remoteocd` and the `adapter`, `upload`, `capture` owners under `/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-...`. The scratch absence is checked before file verification and again with the owner list. No owner is created; the program has no upload/reset/compiler/MCU/cleanup dispatch. Its JSON stdout preserves the exact accepted cleanup result bytes in base64 together with the observed file/identity/absence/process/resource evidence.

These remain point-in-time observations. This program does not replace the native caller's full source/pin/scope checks, upload shadow-path checks, owner claims, later process/identity checks or closing verification. It does not confer permanent absence or reserve resources. No change to those admission guards is inferred from this preparation PASS.

## Disposition

After separate source/host acceptance, the coordinator may execute exactly the pinned intent once and preserve the original result and streams. Failure must remain failure without silent retry, changed pins, widened permissions or recycled owners. Success still requires actual-receipt review and a fresh exact committed scope before the one inhibited diagnostic attempt. No physical, motor, timing-repair or phase-gate claim follows.

Final review; STOPPED WRITES to this file after recording its external hash.
