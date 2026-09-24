# Storage retention and cleanup history

User instruction, 2026-09-24: evaluate generated data after saving it; remove it
when it is no longer needed and retain a small cleanup history. The operational
rule is in root AGENTS.md. This log records batches, not a copy of each artifact.

| Dubai time | Action and reason | Result |
|---|---|---|
| 2026-09-24 10:23 | Removed inspected closed RDP traces, old Python crash dumps, previous temporary analysis artifacts and rebuildable host outputs; compressed state evidence. | Completed in 43319eec. All 21,145 evidence hashes unchanged. Recorded C: free space approximately 90 MiB to 3.33 GiB. See analysis/DISK_CLEANUP_20260924.md. |
| 2026-09-24 11:18 | Losslessly compressed existing build artifacts during renewed space pressure. | 216,809,111 logical bytes stored in 108,968,676 bytes; all 5,552 file sizes/hashes unchanged. Receipts: analysis/P4_push_through_raw/build_before_compression.json and build_after_compression.json. No deletion. |
| 2026-09-24 11:27 onward | Reviewed remaining old host outputs and new retention instruction. | 85,484,611 logical bytes identified as disposable; independent exact path list in reviews/P4_push_through_review_raw/storage_recommendation.md. Automated approval rejected the batch and a narrower three-executable deletion, with reason only "blocked by policy". No additional files deleted. Pending cleanup, not reclaimed space. |
| 2026-09-24 12:20 | D132/D133 retained compact failure/success receipts and reused Git plus the existing D118 source archive. | Test-owned TemporaryDirectory scratch was released by the completed runners; byte count was not measured. New jobs used TMPDIR=/dev/shm and disabled Python bytecode. No persistent duplicate source archive or new target build. Earlier blocked85MB cleanup was not retried. C: free approximately2.6GB before completion; free-space changes also include system work. |

C: had 4,633,726,976 free bytes at 11:27. The system-managed pagefile was
20,132,057,088 bytes at 11:18 and 17,924,820,992 bytes in this follow-up. Its
changing size contributes to storage fluctuation; these observations do not
explain the entire original 9 GB decrease. No paging setting, virtual disk or
running user application was changed. Compressed logical deletion sizes are not
the same as physical bytes recovered, and free-space changes include system work.

Retain the exact referenced RM0456 PDF, checked target ELFs, app receipts,
historical source copies and required evidence. Do not remove entire staging or
evidence directories merely because they are large. The D131/D132 work remains
in progress; its unresolved failures, patches and independent tests are needed.

For each future batch, record time, exact path or bounded path group, why it is
disposable, logical size, actual operation/result and measured free space when
useful. Verify retained evidence before removing a redundant copy. Use small
receipts; do not create another full manifest just to delete known bytecode or
reproducible objects. Do not retry a denied deletion through another mechanism.

| 2026-09-24 13:09 | D134 pause: retained unique failure/success logs, original private oracle and compact hashes; saved four incomplete D135 draft files for resumption. | All completed D134 runners, including full18/private6perM PASS, report owned RAM scratch released. No byte count was measured. No newtargetbuild or permanentduplicate sourcearchive. C: free approximately2.6GB before pause; older blocked85MB deletion not retried. Remaining sanitizer/supplement runs were not started. |

2026-09-24 15:21Dubai: five resumed D134 validation runners archived compact logs/JSON then released their own TemporaryDirectory scratch under /dev/shm (each receipt scratch_released=true). No retained source/evidence or prior policy-denied85.48MB was removed. Current native work retains only scoped receipts/needed ELF artifacts; check capacity before further builds.

2026-09-24T15:32:56.340156+04:00: native-build worker verified243disposable local duplicate staging/receipt files,1,696,900logical bytes, exactowned state/analysis/P5_native_compile_raw/source_snapshot/build. Automaticapproval policy rejected Remove-Item cleanup with only "blocked by policy"; no deletion/retry occurred. Exactpreflight/retainedduplicate bindings in cleanup.json; these generatedduplicates remainlocally untracked, excludedfromnewcommits. Retainoriginalsnapshot/checkedELFs/receipts/index. Earlier85.48MBrejection not retried. C:free2,491,174,912B atworkercompletion.

2026-09-24T15:52:18.7094634+04:00 | D135 host matrices full_retry2/configured_first/sanitizer_first/configured_sanitizer_first | Removed only four runner-owned completed /dev/shm temporary build trees after exact command/log/LastTest/private receipt retention; each JSON confirms scratch_released/source_verified_after_run. Bytes not measured. Prior denied batches untouched; current follow-up scratch remains needed.
2026-09-24T15:57:51.3256967+04:00 | D135 layout_retry1 and faults_first | Both runner-owned /dev/shm build/copy trees released after compact receipts. Layout reports exact scratch bytes; faults bytes not measured. First layoutattempt allocated no scratch/compiler. Prior denied deletions unchanged.

2026-09-24T16:10:54.406100+04:00 | Pause retention | Kept32 MATCH qualification files totaling354055 logicalbytes (checkedELF/receipts/manifests/scripts) plus compact analyzer first-run/failure/review evidence. Needed for offline resumption and source-bound review; no extra snapshot or cleanup attempted. Earlier denied batches remain unchanged.
