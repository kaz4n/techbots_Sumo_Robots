# D211 actual cleanup review

Verdict: PASS for the single exact authenticated cleanup and subsequent read-only retrieval. The three admitted stale scratch copies, totaling 2,399,776 bytes, and their empty directory were removed; retained originals and staged cleanup sources remain unchanged. This is a file-cleanup result, not a firmware, runtime or physical qualification result. Separate same-model reviewer with reused context; local saved evidence and source inspected independently on 2026-09-26. No device call, test, subject execution or credential access was performed by this reviewer.

## Receipt and raw-byte binding

The admitted transport remains `cleanup_authenticated_transport01.json`, 769 bytes, SHA-256 `15afcd9c8afcb5e4742a806d64f6a5131b043d1c2c6f08d9b8c2fc3007dbdb39`: one recorded invocation, return 0, empty streams, no first error, 0.9395794 seconds, and local input closure PASS. Its exact intent and admission were separately reviewed in `P7_ordinary_app_cleanup_stage_review.md` (`7bbc22eee8254b448983069c3df5e07e1c2a6aca36dac16608b82a26cbfefd3a`). No retry is present in this reviewed chain.

`cleanup_retrieval01.json` is 16,916 bytes, SHA-256 `4be9c41bc5d9c79308942ef9ab39c82bd09b2ee5df2cb5fca6995f56de1ad980`. It binds the reviewed retrieval intent `a7474e48eba8fbb6f43295d720af5b5f3891659ece02ac435e550c3092c4cef2`; return 0, elapsed 0.4640263 seconds, null first error, empty stderr and local closure PASS. Recomputed stdout hash is `a88bca70eb05c5fda40abd4c690f0788b0940a51a8eed2024a609ff4e3a2b9d9`.

The exact retrieved `cleanup_root06_actual_result.json` is 6,376 bytes, SHA-256 `0930bc902f92c1eb7e03084abbb045c57690388949b98f62bb49d7b720d1c710`. Its bytes equal strict base64 decoding of the retrieval packet and match that packet's result size/hash. The saved board result is regular, single-link, UID/GID 1000, device 66341/inode 273935. The second read has the identical descriptor/full metadata, size, hash and raw bytes. No reserialized substitute was used for this comparison.

I parsed the raw result and nested `cleanup_stdout` with duplicate keys and non-finite constants rejected. Parsing the nested original stdout equals the complete `cleanup_result` object. The outer result has exactly the 13 expected keys and schema `d211-authenticated-ordinary-cleanup-v1`; the nested result has exactly the 13 expected keys and schema `d211-exact-ordinary-scratch-cleanup-v1`. Both statuses are `REMOVED_EXACT_STALE_COPIES`, both first errors are null, cleanup return code is 0 and privilege-drop errors are empty. There are no extra close/error fields hidden by a status-only acceptance.

## Deletion and privilege evidence

The nested target is exactly `/tmp/remoteocd`; its recorded original directory stamp equals the admitted device 34/inode 1732 directory. The complete three-file inventory equals the pre-authentication verifier's records. The removed list is exactly the sorted admitted names:

| Copy | Bytes | SHA-256 |
|---|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 95368 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |

The result records directory removal and retained originals unchanged. The later independent retrieval observes scratch absence twice, closing the gap between a cleanup status and the saved filesystem observation.

All three protected observations have exactly the expected before/during/result/after/errors fields. Before and after each scan, UID/GID triples are `[1000,1000,0]`. During each scan, UID is `[1000,0,0]` and GID remains `[1000,1000,0]`. Every observation has an empty error list and a result equal to its corresponding nested use check: 165 process names and 3 same-UID process handle sets checked. Source ordering requires the observer's successful finally restoration before returning to the per-file unlink. Therefore the observed successful restorations, together with the unchanged reviewed call order, support user-owned deletion; there is no separate per-unlink credential sample.

Initial UID/GID triples are all zero. Final UID/GID triples are all 1000, and both permanent-drop operations and verification have no recorded error. The supplementary-group evidence is narrower: unchanged source sets groups to `[1000]` and checks that value when entering the Arduino user state. The receipt does not contain a supplementary-group field, and the permanent-drop function does not call `setgroups([])`. No measured final empty-group claim is made.

The result's recipe/helper pins match the reviewed source. Its exact count-one missing-readlink `continue` to `raise` projection and projected hash `e90a5189a76d05bd7674d1bb771b9f480d59b5b26cc4a390109c47431a69d731` agree with the accepted root06 implementation. The scans retain their declared limitation: other-user descriptor sets are not inspected, and successful scans do not constitute a race-free lifetime guarantee.

## Closing evidence and scope

The retrieval packet has schema `d211-independent-cleanup-retrieval-v1`, status `SAVED_RESULT_RETRIEVED_POSTCLEANUP_CHECKED`, no first error, and exactly six PASS checks: stage/result reopen, scratch absence reopen, originals reopen, board identity, credentials and root descriptor close. Complete opening/closing stage, original, board and credential records match. The stage still has device 66341/inode 273931, mode 0700, UID/GID 1000; all three source file identities, bytes and hashes are unchanged from the pre-authentication verifier. Its timestamp change from adding the exclusive result is expected and is not treated as source drift.

Every retained original's full metadata and descriptor/content record equals the pre-authentication evidence. Board identity remains exact, including boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`; retrieval UID/GID triples are all 1000. All 69 coordinator-frozen local files were independently rehashed and remain unchanged.

No material actual-cleanup finding remains. D211 cleanup may be recorded complete for this exact owner, inventory and attempt. The saved sources and unique receipts remain retained. This result provides no new motor permission, hardware acceptance, phase gate, firmware flash, reset continuity or broader elevated-access authorization. Any later native runtime attempt still requires its own frozen scope and admission.
