# D207 fresh admission and exact native scope review

Status: PASS for the fresh saved admission and exact prepared scope, conditional on the subsequent committed clean-HEAD and successful local check-only checks. No material finding. This accepts preparation for one fixed MOTORS_ALLOWED=0 diagnostic attempt; it is not a record of upload/capture execution or runtime acceptance.

The reviewer performed local read/hash/JSON/AST-data checks only. No subject or oracle was imported/executed, no test/compiler ran, and no device/authentication/cleanup operation was performed. Only this new review file is owned. Earlier final reviews, original failures, consumed owners and other contributors' work remain unchanged. Clean-HEAD qualification is deliberately not claimed while the coordinator is still assembling the review/state commit.

## Actual observation and identities

`RAW` means `state/analysis/P7_motor_const_run_raw`.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `RAW/admission01_attempt.json` | 2709 | `8218efd3f0d180a93d24bebe4c3b27e6a4992f688bf3ae0480323d6e6ad886c6` |
| `RAW/admission01.json` | 3040 | `e65fc7b18b12361625db438fc0e6f72ad0a12ab75fd9f2f9e6578676ab97a645` |
| `RAW/admission01_stdout` | 12681 | `9a84758f0c6294fbb591626a7bec3ab591ebdbe44505deb5479ba9e20b239b6c` |
| `RAW/inert_run01_scope.json` | 1875 | `23c1fcf6ddb371d5e7c641bab67b78c927ac541b4090cc390942de90bd86f700` |

The saved call began at `2026-09-26T14:29:32.596234+04:00`, records exactly one read-only native invocation, returned zero in 0.9316496999235824 seconds and has empty stderr with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. Its outer timeout was 70 seconds. The attempt fields all equal their final-receipt counterparts, the stdout/stderr lengths and hashes match the actual files, and the changed-input list is empty. All thirteen actual-invocation local pins were independently rehashed and match.

The intent remains 34163 bytes / `af1fbacd2835d983ce956e5a6927fd34071be9491dbe5eef49a4b4da1b9478d9`, and its reviewed program remains 23886 bytes / `769933e9baa0c0b9fa61dc72017bd3585a8680f9e3238fe65b362a60fb2fc198`. The immutable source-preparation review is 7361 bytes / `1efb9d308473a5c57f0d3808fdeaaec0c6ee8245853aaa108a1e72e1d46858f6`. This actual call used that prepared read-only boundary, not a new program or cleanup invocation.

The reviewer strictly parsed saved JSON with duplicate-key/nonfinite-constant refusal. The observation has the expected seven keys and status `CLEANUP_RETRIEVED_AND_NEXT_RUN_FILES_CHECKED`. Its identity equals the contract and scope: Arduino user, UID/GID 1000, `/home/arduino`, Linux `6.16.7-g0dd6551ae96b`, aarch64, Python 3.13.5 and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. The transport/scope board serial is `2629958581`.

All nineteen unique observed file records exactly equal the intent's complete file dictionary, including paths, lengths and SHA-256 values. They comprise seventeen unchanged installed/helper records and the two current build artifacts. The raw image is 95352 bytes / `76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3`; the packaged sketch is 95368 bytes / `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7` under `app-motor-const-static01/build/`.

The exact four observed absences are `/tmp/remoteocd` and the fresh `app-motor-const-4bc3a2e6-run01-adapter`, `-upload` and `-capture` directories under `/home/arduino/sumox26_codex_build`. The recognized process-conflict list is empty. Saved resources are 13914370048 available root-filesystem bytes, 3190931456 available RAM bytes and 1924096000 available tmp bytes; the required 1073741824-byte root threshold was exceeded. The reviewed program repeats identity and scratch-absence checks and closes the root descriptor in `finally`. These observations do not reserve paths or resources; the caller's later live checks remain necessary.

The retrieved cleanup object's base64 is canonical; decoded bytes exactly equal the accepted D206 root05 result, 6367 bytes / `3b8f035a6b282ada5a5fbf5992a5343d27a3dc245962ee7f64032757420e11e8`. Its immutable independent actual review remains 8082 bytes / `aaede1e1d8a0a8deef6b48de191abe76cf06bb2779f6ce4fa810c4467544e9c8`. The program also verified the three root05 staged-source hashes and retained original pins before successful output. This closes the current cleanup prerequisite; it does not reopen root05 or authorize a further deletion.

## Exact scope and provenance

The scope has exactly the six declared top-level keys and the exact eleven declared file roles. All eleven SHA-256 values match their actual files:

- Current `preparation.json`, `run.py`, `actions.py` and `remote.py`.
- The three fixed native oracle files for caller, actions and remote.
- The adopted run contract and its normative derivation companion.
- The separate final caller and remote source/host reviews.

There is no extra role, omitted native role, alternate source, stale D201 owner or permissive wildcard. Scope schema is `app-motor-const-native-scope-v1`; run is `app-motor-const-4bc3a2e6-run01`; source is `4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`. Board and complete expected identity match the actual admission. The selected interpreter/map, admission and host-closure gates are separately accepted here as coordinator prerequisites; changing the caller's exact eleven-role schema to add them is neither necessary nor authorized by this review.

Current preparation remains 9988 bytes / `519a95f623e3c463842217cdb568cb1909941974b49c36453bfc8f8ea1f8449e`. Its twelve provenance byte/hash objects equal the normative companion and all actual files. The 129-file source manifest is exact, and all 129 current source hashes were independently checked without mismatch. Current compile/artifact/ABI/entry machine statuses are `COMPILE_CHECKED`, `ARTIFACTS_CHECKED`, `STATIC_ABI_OBSERVED` and `STATIC_ENTRY_OBSERVED`; relevant first errors are null. The three pinned actual reviews accept their respective file-observation scopes with explicit runtime/physical limitations.

The accepted compile flags remain `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`, FQBN `arduino:zephyr:unoq:link_mode=static`, default startup and current source identity. No match/motion grant, changed 150 us / 4096-poll settle policy or altered runtime limit is introduced. Both local owners `RAW/native_inert_run01` and `RAW/retrieved_inert_run01` were absent at review time.

## Final source and host gates

The final caller/actions review is 18018 bytes / `74083d6ee869f9dd9bddfa6729e9d6b94c5b908ee0b718490e67af379e5b6f11`; remote review is 7744 bytes / `316fec95694fe5210048b09e430fd57f19e9ec27b8aecc32d6f2cb7dde481975`; interpreter/map review is 10684 bytes / `f4fd1bc852c7a4bdeef294950397b6f6a962a11ec96f847b38c1818ff6bacbba`. Each is final PASS in its stated source/host scope with no open material blocker. The caller review was read, including its admission/claim boundary, thirteen-transport one-shot sequence, continuous Git/pin checks, failure consumption and documented limitations.

The independent saved-receipt closures are `RAW/native_host_closing01.json`, 52838 bytes / `eeccfad26bc2e9e89b7e79d3355a38d7e486b2ac7c250ede01c787b71021b0ed`, and `RAW/interpreter_host_closing01.json`, 30769 bytes / `d331a41bf4304e3cde7c6c95778902ba8721c68b1be70af57a112319326f81b5`. The reviewer independently checked every referenced current intent/result/stdout/stderr file hash, compared intent fields to result fields, parsed every method name/outcome from all eight complete test streams, and compared these rows to the summaries.

The native suites total 106 Linux PASS and 62 Windows PASS with 44 explicit skips covered on Linux. Decoder has 70 PASS on each platform, no skips. All eight return zero within their 600-second bounds, without timeout or changed input, and preserve their coordinator freezes. Native coordinator/independent pins close at 302/290; decoder coordinator/independent pins close at 184/177. Saved fixture inventories report no scoped remnants. The known leading apostrophe in the native summary's displayed skip-reason strings is clerical; raw method identities, outcomes, counts and covered assertions are correct, as explicitly documented in the final caller review. No rerun or summary rewrite is required.

## Disposition and remaining execution gates

Accept the fresh read-only observation and this exact scope for one subsequent inhibited attempt under D207. The coordinator must first commit the complete evidence/reviews/state checkpoint, establish an actual clean reviewed HEAD, retain the writer hold, and obtain a successful local `--check-only` using that full forty-character HEAD. This review does not supply a guessed HEAD or predeclare that check successful. Execute only the same pinned caller/scope against that HEAD with fresh live prerequisite checks and exclusive owners. Any failed/uncertain claim, dispatch or closure must remain recorded and consumed; no automatic retry, repinning, widened command or owner reuse follows from this PASS.

Successful transport/upload/capture would still require separate saved-result retrieval, strict decoder handling and independent actual review. A setup success alone would not prove the prior deadline fault cured or later epochs completed. Coherence remains UNPROVEN; no motor-run permission, measured physical fact or human phase gate is manufactured.

Final review; STOPPED WRITES after recording this file's external hash.
