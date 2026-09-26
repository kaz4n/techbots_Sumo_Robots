# D220 actual exact cleanup review

FINAL PASS, 2026-09-26. Separate saved-evidence/source review by the same model with reused context; not fresh-context, cross-model or human approval. I performed no native operation, test, source import, credential handling or cleanup. Prior preparation/admission reviews remain immutable.

RAW = state/analysis/P7_b4_app_cleanup_raw.

## Exact evidence

- cleanup_authenticated_transport01.json589/1fdcf7abe542af6a423ad5108b008e5f358ba6852f9f9413c16a06f5c0054b14: one admitted intent bed4004a... and final admission review46e3db77..., return0, empty stdout/stderr, no first error, local input closure true,0.9512768s.
- cleanup_root07_actual_result.json6325/437d1b301e686cf5137179e9d5fdd6ff4641992cda9fd7e0a988eae79e402f47.
- cleanup_retrieval_intent01.json40014/fa5616dfcb1d4a395f1595222393e209724f400f5320af2f5a94c6100e097e03; program24596/0019df9c695f65621c21fcda92abb70241f4b0ee371d840104b82bf0bc9aca01.
- cleanup_retrieval01.json16455/a5c8ee0f5f9376cdea00a85088dc110b1962885031d8df7b0e5de61bd7a4bc7b: return0, no stderr, input closure true,0.435869s; exact stdout SHA256 ce224f90c831af94995416d2162f04ccb9e35730a5ddc3eae61f5995b87406f9.
- cleanup_actual_closing01.json6041/19ec6822eafc77855237b50ff911d0c137e136f985ce46ff05bba9295997e030. All27 listed current file pins independently matched.

## Retrieval and provenance

Independently replayed all nine counted metadata substitutions, every intermediate byte count/hash and full reverse equality to accepted D211 retrieval. All six intent inputs matched; its decoded packet contains exactly the current wrapper, recipe and helper bytes. No operational read/descriptor/closing algorithm changed. The fixed isolated command has28007 Windows UTF-16 units including NUL,55s inner alarm and70s outer bound. This was reviewed after its single read-only execution under the parent's existing authorization; no prior preparation approval by this reviewer is implied.

The program reads only the root07 stage/result, retained originals and scratch absence. It retains descriptor-relative no-follow reads, regular-file/ownership/nlink/full-stamp checks, bounded result size, exact hashes, reopen comparisons and root closure. The stage directory compares stable identity fields against pre-auth admission because result creation legitimately changes its timestamps. It compares all source-file stamps in full. Actual before/after retrieval stage/result records are identical; source records match the accepted pre-auth verification, and all retained-original records match exactly.

The saved actual result equals the canonical-base64-decoded retrieval bytes byte-for-byte, including its final newline and hash. Strict duplicate-free parsing reconciled exact outer and nested schemas/keys, and cleanup_stdout parses exactly to cleanup_result. No first, close or privilege-drop error is present. Source pins and the private count-one missing-readlink projection agree with the accepted current recipe/wrapper. The authentication runner pins the admitted intent/review/inputs, creates exclusive invocation evidence before dispatch and supplies the credential only via native stdin; saved stdout/stderr are empty and no credential value is in the reviewed artifacts.

## Actual outcome and limits

The nested result reports REMOVED_EXACT_STALE_COPIES for exactly, in order: app.ino.bin-zsk.bin92944 bytes, flash_sketch.cfg680 bytes and zephyr-arduino_uno_q_stm32u585xx.elf2303728 bytes; total2397352 bytes. All pre-removal full stamps/hashes match admission and pre-auth verification. The removed directory is /tmp/remoteocd dev34/inode2007. The package is the D212 ordinary image7fa9d41d..., not the unflashed B4 package. directory_removed and originals_unchanged are true; both independent post-cleanup scratch-absence observations are true.

All three protected-scan records have exactly the expected before/during/after credentials and no errors. Each reports165 process names and3 same-UID processes whose handles were inspected, and equals its corresponding nested use_check. Before/after each scan UID/GID triples are[1000,1000,0]; during only effective UID becomes0. In the unchanged reviewed control flow, successful restoration returns before per-file identity/inventory checks and unlink, so the three deletions occur with Arduino real/effective credentials. Final UID/GID triples are all1000, with no permanent-drop error. Final supplementary groups were not separately observed; no such claim is made. Process scans retain their documented visibility/race limits and are not a general process lock.

Retrieval confirms unchanged board identity/boot, UID/GID triples1000 and six exact ordered PASS closures: stage_and_result_reopen, scratch_absence_reopen, originals_reopen, board_identity, credentials and root_descriptor_close. Originals and the root07 stage/evidence are retained. The consumed attempt/result cannot be reused. Earlier stale-inode preparation defects remain preserved and were corrected before invocation. This acceptance closes only the exact cleanup; it establishes no firmware/MCU change, physical acceptance, motor permission or phase gate. Review sealed; writes stopped.
