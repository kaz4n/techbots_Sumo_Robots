# D220 actual stage and one authenticated cleanup admission

FINAL PASS, 2026-09-26. Independent saved-source/data review by the same model with reused context; not human or cross-model approval. No device operation, test, credential handling or cleanup was executed by this reviewer. Prior reviews remain immutable.

RAW = state/analysis/P7_b4_app_cleanup_raw.

## Actual admission evidence

Independently checked exact receipt/source pins, strict duplicate-free outer/nested JSON schemas, actual hashes and complete before/after stamps:

- cleanup_absence01.json2365/d470e54b09f817200293e1a560b986732121a414deece9e7a5a46eccf340d1d3: ABSENT_OWNER_READONLY_CHECKED.
- cleanup_stage01.json2332/714b3a6fc8035a4f62016a1c0ea10ec6c2edc89fc55d1e43ef52cd72e420bf66: STAGED_CHECKED_NOT_EXECUTED.
- cleanup_stage_verification01.json9621/de1ccd539b5a0e696cc7f1dd5f138ce2abf911a8865b9052f10e676777843a6c: STAGED_FILES_VERIFIED_NOT_EXECUTED, return0, empty stderr, local input closure true, elapsed0.5172513s. Exact stdout SHA256 is1db1d368e6e88a8819c232a7a6ea9f067bfa601a00841d781cdeaa92b86f6b7c.

The absence/stage receipts have return0, empty stderr and unchanged local inputs. Their identities/source sets/scratch stamps agree with the independently reviewed verifier and original inventory97577771.... All five verifier input pins still match. Verifier preparation review3437/6dec2e4024796b705b320316e40ba492e4ef9b0e7c7973c2e695f196eaa96fbf remains applicable.

The fresh stage /home/arduino/sumox26_codex_build/cleanup-b4-app-root07 is dev66341/inode274504, UID/GID1000, mode0700, nlink2. Its complete before/after directory and file stamps agree. Exactly three0600 regular singly linked UID/GID1000 sources exist: wrapper9608/559c83d78ade592271e97b0bcd2c6621aed161c465019b8df15fbfaceb41c781, recipe7708/5fc2150f986814bec8d36409caf5f0e0d4303e5c2cdc96e08605f6e9f0dee574 and helper33321/8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8. Every staged size/hash equals the current local source. result_root07.json is absent in both snapshots.

Scratch directory dev34/inode2007, all three child hashes/full stamps and all retained-original full records agree with admission01 and across verifier reopening. The copied package is ordinary D21292944/7fa9d41d..., not B4. Board identity/boot remain exact; all real/effective/saved UID/GID triples are1000. The six ordered closing rows are exactly stage_reopen, scratch_reopen, originals_reopen, board_identity, credentials and root_descriptor_close, all PASS, with no first error. process_use_clearance remains false; this nonprivileged observation does not claim protected-handle clearance.

## Exact next operation

cleanup_authenticated_intent01.json1791/bed4004a546117605cbd0f9936f589c7e483194541d49914253f72a0c6194ffc binds these exact wrapper/recipe/source-review/verifier-review/actual-verification bytes. Its argv equals the accepted D211 intent after only stage, wrapper and result-name substitutions. Fixed ADB serial2629958581, shell-T and70s outer bound remain; full Windows argv including NUL is307 units.

The remote command is exactly:

```sh
set -C; sudo -S -p "" -H /usr/bin/python3 -I -B /home/arduino/sumox26_codex_build/cleanup-b4-app-root07/cleanup_root07.py > /home/arduino/sumox26_codex_build/cleanup-b4-app-root07/result_root07.json
```

The nonprivileged shell creates the result with no-clobber before sudo. Credential route is Windows no-echo console to native stdin only; no value is included in source, argv or this review. Within the parent's recorded existing user authorization, admit this one fixed invocation after the coordinator pins this final review and rechecks bound inputs. No general root command, second attempt, result overwrite or alternate owner is admitted.

The accepted preparation review6063/9523c8decd3a9a52d0088a4ec6cbb01446fd5bd3747d95b881beacb20f0bb13e establishes exact unchanged operational bodies. At use, the wrapper must verify sources, establish Arduino real/effective IDs with saved root, elevate only for each of three read-only protected scans, restore Arduino credentials before each unlink and permanently drop all saved UID/GID privileges in finally. The recipe rechecks exact inode, contents, remaining-file stamps, identity and originals; no retained-original fallback exists. Current verification is not a lock, so these runtime refusals remain necessary.

Successful transport alone will not establish cleanup success. Preserve the first attempt and independently retrieve/review the outer and raw nested result, three scan/restoration records, exact three removed names/content pins, scratch absence, retained originals/source stamps, final UID/GID triples1000 and all first/close/drop errors. The wrapper's dictionary/status check is not full nested-schema validation. No firmware, MCU, sensor, motor, physical or phase acceptance follows. Review sealed; writes stopped.
