# D232 exact D228 upload-copy cleanup preparation

PREPARED, NOT EXECUTED. This package is a data-only derivative of the accepted
D226 cleanup. It preserves that recipe's ownership, source, byte, process,
descriptor, credential, deletion and closing guards. No staging, authentication,
cleanup, MCU action or credential handling was performed by the preparer.

The prior read-only admission is
`P7_recorder_next_cleanup_raw/admission01.json`, SHA256
`17cfc318c40cbe01b95f824bea001a7aa03359b94bbae54119fa21830f627b99`.
It observed `/tmp/remoteocd` device 34 / inode 6292, UID/GID 1000 on unchanged
boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, with exactly these three children:

| Copy basename | Bytes | SHA256 |
|---|---:|---|
| recorder.ino.bin-zsk.bin | 55104 | 91b6042a3f13e3650fc4b23892f88e69d4c0c56edebd6514662fa2d8cd8208c6 |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |

Total 2359512 bytes. The retained recorder original is
`/home/arduino/sumox26_codex_build/recorder-377911abefabd094/build/recorder.ino.bin-zsk.bin`;
the installed config/loader originals remain unchanged. Remove only these exact
single-link copies, then the directory only when empty. No recursive deletion,
installed/build-original deletion or broader cleanup is included. The observer
does not establish protected-handle clearance; the inherited authenticated
process checks remain mandatory and fail closed.

The fresh remote stage is
`/home/arduino/sumox26_codex_build/cleanup-recorder-next-root01`. Every old D226
stage/attempt stays consumed. The dispatcher ROOT is fixed to the isolated
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-next-cleanup-20260927` worktree;
MAIN stays untouched during subsequent execution. Fourteen exact inherited
matrix completion receipts are available there. Active native jobs must close
before execution; the remote recipe still independently checks process use.

`cleanup_derivation01.json` proves byte-for-byte reversal of recipe, wrapper,
four programs and dispatcher template to their exact D226 originals. Changes
are limited to observed file/directory data, original path, fresh stage, schema
labels, local evidence-root path and associated pins. The existing projection
that raises on a disappearing observed handle is unchanged. The helper remains
33321 bytes / 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8.
Preparation scripts and tests perform no native operation.

After source/delta review, root reads `native_dispatch_template01.py`, checks its
manifest pin, and replaces exactly one occurrence each of
`__PREPARATION_MANIFEST_SHA256__` and `__PREPARATION_REVIEW_SHA256__` with the full
lowercase SHA256 of `preparation_manifest01.json` and the accepted
`state/reviews/P7_recorder_next_cleanup_review.md`. Exclusively write the result
as `native_dispatch01.py`, verify reverse equality to the pinned template, and
retain its own pin. These two literal bindings require no new source review.

From the isolated worktree, root invokes the existing dispatcher as
`python -I -B state/analysis/P7_recorder_next_cleanup_raw/native_dispatch01.py <action>`
once per action, in order: `absence`, `stage`, `verify`, `authenticated`, `retrieve`.
Verification/retrieval bind only actual checked receipt metadata. Authentication
uses the inherited no-echo STDIN path and no-clobber result, never an argument,
environment value or saved credential. Every failure consumes its owner; no
automatic retry is added. Preserve first/closing errors and reconcile the saved
result, retrieved raw bytes, scratch absence and retained originals before
claiming cleanup. All ADB hash/serial, 70-second host timeout, 55-second remote
alarm, 65536-byte reply limits and credential transitions remain unchanged.

Host/delta acceptance does not prove deletion, clear current process use, admit
an upload or provide motor authority, physical acceptance or a phase gate.
