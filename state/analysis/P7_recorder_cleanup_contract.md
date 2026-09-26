# D226 exact recorder prerequisite cleanup preparation

Status: **PREPARED, NOT STAGED OR EXECUTED**. This package is a data-only derivative of the previously checked D220 cleanup. No board command, credential operation, source upload or deletion was performed by the preparation worker.

## Exact removal plan

Only the following three regular, single-link Arduino-owned children of `/tmp/remoteocd` may be removed, followed by that directory only when empty. The directory must remain device34/inode2281, UID/GID1000, on boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. No recursive removal, wildcard, symlink following, broad scratch cleanup or installed/build-original deletion is permitted.

| Temporary basename | Bytes | SHA256 | Original retained |
|---|---:|---|---|
| `app.ino.bin-zsk.bin` | 82912 | `84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28` | `/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin-zsk.bin` |
| `flash_sketch.cfg` | 680 | `38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c` | `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg` |
| `zephyr-arduino_uno_q_stm32u585xx.elf` | 2303728 | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` | `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf` |

Total candidate file bytes: 2387320. The fresh admission is `P7_recorder_cleanup_raw/admission01.json`, SHA256 `d031f0d079dddcce718aa60ef263f867385c9ad9d647b5fdd380de477fc07502`. It observed exact matching copies and originals but also the expected active matrix compiler. It is **not process-use clearance**.

## Preserved guards and source derivation

`cleanup_remoteocd01.py` changes only the source-package size/hash/original path, directory inode, provenance/schema labels and associated source pins. `cleanup_root01.py` changes only the fresh stage name, recipe basename/pin, projected recipe hash and schema label. Full byte-for-byte reverse proofs reconstruct the exact pinned D220 originals. `cleanup_derivation01.json` records every literal replacement/count and intermediate hash, including the four intent-program derivatives.

- Recipe: 7701 bytes / `f130f76cf0b644dfb53278387ff55a71e120bbb0b686f78ff906c97216536bab`.
- Wrapper: 9606 bytes / `9e12845ddf326447e6b8bf941b49707c575014484346d48fde0db769d967292a`.
- Projected recipe: 7698 bytes / `8e62047629eee0e0251917a2343f30c1be89d591ea1dcabac31209b516e2286e`.
- Unchanged native helper: `state/analysis/P7_static_link_probe_raw/static_remote.py`, 33321 bytes / `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.

The wrapper retains the exact credential transitions: root invocation, Arduino real/effective IDs with saved root, temporary effective-root elevation only for process observations, restored Arduino credentials before every unlink, then irreversible dropping of saved root credentials on exit. The original process-name scan and UID1000 cwd/FD checks remain bounded and fail closed. The existing single projection makes a disappearing observed handle raise instead of silently continuing. Other-user FD coverage is not claimed. Original files, copy bytes, directory identity, board identity and empty-directory checks remain unchanged.

## Concrete operations and deferred observations

All intents use exact ADB target `2629958581`, pinned host ADB SHA256 `e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`, 70-second host timeout, 55-second remote cleanup/observer alarm, and 65536-byte stdout/stderr bounds. Native dispatch must enforce those host bounds and preserve first errors plus closing evidence. Intents are structured plans; they do not themselves execute commands.

1. Wait for the main compile matrix to finish and require no active native compiler/uploader. Obtain independent preparation review before any staging. Preserve the original admission; repeat current checks through the prepared operations.
2. Execute `cleanup_absence_intent01.json` once using checked transport. It checks current scratch/original identities and requires the fresh stage owner absent. Its standalone remote program is `absence_program01.py`.
3. Execute `cleanup_stage_intent01.json` once. It creates only `/home/arduino/sumox26_codex_build/cleanup-recorder-root01` and exclusively writes the exact wrapper, recipe and unchanged helper with source hashes and closing checks. It does not run cleanup. `stage_program01.py` is the exact program embedded in the argv.
4. Bind `cleanup_verify_intent01.json` using the successful stage receipt: replace the single `__STAGE_IDENTITY_FROM_CHECKED_RECEIPT__` identifier in `verify_program01.py` with `repr` of its exact `/stage_identity` object. The scratch/copy/original observations are already fixed to admission01. Recheck receipt status, target, board identity, stage path, source pins and local input closure; require exactly the expected data keys/types. Build remote argv via the supplied prefixes and `shlex.join`, require the full Windows command below30000 UTF16 units, pin the finalized program/intent, then independently review and run the read-only verification. No actual stage inode is invented here.
5. After verification reports `STAGED_FILES_VERIFIED_NOT_EXECUTED`, bind its receipt and the reviews by hash to `cleanup_authenticated_intent01.json`. Recheck all source, ADB, review and verification pins. Exclusively create local `cleanup_authenticated_invocation01.json` before obtaining/passing authentication. Invoke its fixed remote no-clobber command once: `sudo -S` with an empty prompt, isolated Python, the exact wrapper, and `result_root01.json`. Credential input is no-echo STDIN only, never command text, environment, saved source or evidence; refuse any echo fallback. No TTY, automatic retry or reused owner is permitted. Failure consumes the attempt.
6. Bind `cleanup_retrieve_intent01.json` with the same checked stage identity and `__SOURCE_IDENTITIES_FROM_VERIFICATION_RECEIPT__` from verification `/stage_before/files`. Its standalone `retrieve_program01.py` preserves the old read-only retrieval checks: exact sources/result metadata, result raw bytes, scratch absence, retained originals and closing identity. Apply the same bounds, pin and review before running. Preserve partial/failed receipts and compare the original cleanup result; never infer cleanup from a successful host transport alone.

Verification and retrieval intentionally have no runnable `argv` until their real observation fields are bound. They are syntactically valid templates that fail on an unbound identifier; no remote deletion lies in either. The complete authentication argv and exact deletion scope are already reviewable. Existing consumed D220 paths are never reused.

## Focused local evidence

Five unique local methods passed: reverse recipe/wrapper/four-program proof, exact source/projection/current-original binding with corruption refusal, active compiler refusal before FD inspection, projected disappearing-handle refusal, and staging/authentication/deletion separation with bounds. `tests01` retained four passes and one fixture spelling mismatch: the inherited shell command uses double quotes for an empty sudo prompt while the fixture expected single quotes. The fixture now compares exact parsed tokens including the empty argument; only that failed method was repeated and passed in `tests02`. Production/intents were unchanged by the correction. Original test bytes and correction receipt remain.

No broad historical suite was repeated. No MCU/software source, D224/D225 artifact, existing observer/admission byte, main checkout or blocked staging path was changed. Preparation writes are confined to this new cleanup package and this contract. Flat final pins are in `P7_recorder_cleanup_raw/preparation_manifest01.json`; local checks do not grant board clearance or prove deletion.
