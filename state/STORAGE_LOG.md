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

2026-09-24T22:14:55.246824+04:00 | D136 retention | Temporary synthetic fixtures used /dev/shm and unittest cleanup; no native rebuild or host object tree created. Retained small source/test freezes, unique first-failure logs and passing/review receipts for reproduction. Native MATCH evidence42files396062logicalbytes remains needed. No whole new checkout, no deletion retry for earlier denied batches.

2026-09-24T22:23:40.901462+04:00 | P7 document retention | Three small Markdown operator templates plus compact review/local-check receipts are needed for review, printing and resumption. No compiler tree, downloaded package, PDF duplicate, boardbuild or temporary fixture created. No disposable generated artifact remains from this task; prior denied cleanup batches untouched.

2026-09-24T22:49:05.366453+04:00 | D138 normal_first | Kept small unique compiler-failure log/JSON and678input hashes; runner released only owned /dev/shm build scratch. C: fell to745037824B while build scratch was9.8MiB/swap0; read-only diagnosis underway, no cause or deletion assumed. Prior denied batches untouched.

2026-09-24T22:52:39.200325+04:00 | Read-only storage investigation | Since22:38,61modifiedprojectfiles entirecurrent sizes4,244,148B includingexisting3.18MBGitindex; insufficienttoexplain~1GBdrivefall. Recent WSLcrashdumps16,617,472B; pagefile19,677,765,632B timestamp22:43:38 butnoearlierbaseline. WSLswap0; exactcauseunknown. No unrelateddeletion/systempagingchange, priorblockedbatchesuntouched. ContinueownedRAMscratch/board-sidebuilds andcompactreceipts.

2026-09-24T23:07:21.492846+04:00 | D138 native cleanup | Removed only233 .o/.d/.a files (7,355,110B) in newboardrun04b266d5/build after retaining75compactevidencefiles/checkedELF (1,278,010B) and rehashing4retainedremoteartifacts. Boardcleanup exit0. Automaticapproval rejected localRemove-Item of verifiedbuild/stage/app beforeprocesscreation: onlyreason blocked by policy.102files753,087B remain; noretry/circumvention. Raw cleanup receipts retained in P7_readiness_native_raw. Earlier85.48MB/1.70MBdenialsuntouched.

2026-09-24T23:13:03.869573+04:00 | D138 finalhost retention | normal_retry1/configured_first/configured_retry1/full_first/configured_final/sanitizer_final/configured_sanitizer_final runners each archived compactreceipts thenreleasedowned /dev/shm build/copytrees. Equivalencepreprocessor scratch also released. Unique originalfailures, independentoracles,687inputhashes, checkednativeELF/reviewremainneeded. C:653561856B latest; no extrauserfile/pagingchanges orcleanupretry.

2026-09-24T23:38:12.327347+04:00 | D139 retention and cleanup | Retained86 compact raw files1708702B plus final index/report/review; one local final ELF and checked remote debug/temp ELF/ZSK are required negative-fit evidence. Removed only233 disposable .o/.d/.a files7369554B from new board run52b4ba3a after exact selection/path validation; exit0 and four retained artifacts rehashed unchanged. Independent synthetic staging tests released only their owned RAM fixtures. Local stage102files753087B remains exact; no deletion retry and older blocked batches untouched. C:599363584B free at check. No duplicate checkout or local native object tree.

2026-09-24T23:47:08.429572+04:00 | D140 source retention | Retained66 compact installed-source/read-only command records168157B plus three official source files9932B and small manifests/review. These are required provenance for pending Static feasibility design. No binaries copied, package installed, image built/processed or cleanup performed. Original failed text transfer retained; no duplicate checkout, denied-cleanup retry or unrelated deletion.


## 2026-09-25T00:00:01.834775+04:00 - Storage shortage: preserved evidence, recovered 337.4 MiB

The user requested deletion of unused files. A separate read-only audit identified
154 downloaded Arduino installation archives, totaling 4,571,947,977 bytes
(4.26 GiB), outside installed packages. Automatic approval review rejected the
exact-file deletion batch before process creation; its only stated reason was
"blocked by policy". Zero files were deleted and no retry occurred. The manifest
and retained CLI/ADB hashes are in analysis/storage_cleanup_20260924_archive_cache.json.
Earlier denied host/snapshot/stage cleanup targets were not touched.

The safe alternative was transparent per-file Windows LZX compression of retained
historical JSON/JSONL/TXT evidence. The pilot recovered 6,885,376 allocated bytes;
the subsequent 128-file batch recovered 346,910,720 bytes. Combined recovery is
353,796,096 bytes (337.4 MiB), with no content or logical-size change. The main
batch's physical allocation fell from 557,920,256 to 211,009,536 bytes. Source,
binaries, tools, mutable ledgers and Git history were excluded. No archive copies
or build outputs were created for this cleanup.

A separate context rehashed every completed file and verified sizes, mtimes and
physical allocation: zero mismatches. All 154 blocked cache archives and both
installed tool hashes remain intact. Two representative compressed records were
also read and SHA-256 checked through WSL, exit 0. C: had 899,932,160 bytes free at
independent review; global free space can change independently of this task.

Keep the compact pilot/batch/verification receipts under analysis/storage_compression_20260924_*.
They are needed to explain reclaimed allocation, content identity and exclusions.
Do not recompress based only on the Compressed attribute: successful LZX files
may report Archive alone. Use these receipts to identify completed paths. No
pending compression/compiler process remains; no denied action, system paging or
persistent virtual disk was changed.

2026-09-25T00:15:12.102192+04:00 | D141 retention | Kept 17 scoped raw/test/reference files totaling 100317 bytes plus small validation/review records. These bind reproducible policy checks, independent oracles and original failure evidence. No compiler tree, package, source snapshot or bytecode created. Reviewer removed one owned unexecuted duplicate private-test draft after the independent supplement was supplied (bytes not measured); original4-case negative probe retained. No denied cleanup retried. C: free 849965056 bytes; prior compression recovery unchanged.

## 2026-09-25 00:23 Dubai - Additional bounded cleanup

Removed four closed, preflighted non-WSL application crash dumps totaling
20,152,761 logical bytes. Exact paths, hashes, containment/age checks and verified
absence are recorded in analysis/storage_cleanup_20260925_crashdumps.json.
Both WSL crash dumps remain as potentially relevant failure diagnostics.
Also removed the independently checked, ignored generated cache
tests/tooling/__pycache__/test_reactive_timing.cpython-312.pyc (23,615 bytes).
Its tracked source remains unchanged at SHA256
4b9e896fdc5112246f8db1a669e493819601d9d110bb625e2dfd5cbea784bc2a.
No recursive directory removal was used.

Transparent per-file LZX compression of 61 retained historical ELF artifacts
recovered exactly 50,286,592 allocated bytes (48 MiB). Their 181,958,268 logical
bytes, hashes and modification times remain unchanged. P7 artifacts, source
snapshots, tools and Git were excluded. Receipt:
analysis/storage_compression_20260925_elf.json. Independent verification is in
analysis/storage_cleanup_20260925_verification.json. Required ELF evidence was
preserved, not deleted or replaced with an archive.

C: free space was 942,456,832 bytes at a subsequent check; system activity also
affects this number, so it is not a measurement of deleted file allocation.
Earlier rejected Arduino cache/host/stage/snapshot removals were not retried.
No pagefile, virtual disk, installed tool, firmware or source was changed.
Retain these compact cleanup receipts; no duplicate checkout/build was created.

2026-09-25T00:40:30.855361+04:00 | D142 retention | Retained14 scoped raw/oracle/source files totaling102756 logicalB, plus small contract/review/validation/root receipts. They bind independent expectations, actual passing tests and original negative evidence. Fixtures were transient RAM bytes, including one16MiB+1 boundary buffer; no compiler tree, binary fixture, downloaded package, duplicate checkout or bytecode created. No denied cleanup retried; current C: check remains required before large work.

## 2026-09-25T00:51:41.569839+04:00 - Additional cache cleanup

Removed 92 regenerable pip HTTP cache files (8,740,886 logical bytes) and ten
ignored CPython bytecode files (645,923 bytes), totaling 9,386,809 bytes
(8.95 MiB). Exact bounded paths, original hashes and completion results are in
analysis/storage_cleanup_20260925_pip_http.json and
analysis/storage_cleanup_20260925_bytecode.json. Native PowerShell exact-file
removal followed containment, reparse, hash and exclusive-open checks. No
recursive removal or installed-package deletion was used. A separate context
verified all 102 files absent and all ten retained-source checks unchanged,
exit 0 and zero mismatches. Receipts were compacted after verification.

The npm download cache (61,099,871 bytes) remains: seven running npm/npx
launchers and recently modified cache metadata were observed. Its separate
_npx package trees also support running tools and were retained. Unidentified
temporary files, WSL diagnostics, earlier policy-denied cleanup targets,
source, unique evidence and saved P7 drafts remain untouched. No pagefile,
virtual disk, hardware or firmware change. C: free space fluctuates with other
processes; the last deletion receipt records 865,792,000 bytes free after pip
cleanup, not an exact allocation-recovery measurement.

2026-09-25T00:59:16.694247+04:00 | Runner draft retention | Retained two small Markdown interface drafts, one scoped design review and one compact local-pin/link/size-check receipt for the next implementation. Initial drafts are in a57265f5. No source snapshot, test fixture, bytecode, build tree, board operation or download was created. Existing compact cache-deletion receipts remain needed; no further cleanup candidate was confirmed.

2026-09-25T01:13:43.547866+04:00 | D143 bytecode cleanup | Removed two ignored app_build_policy CPython12/13 caches,33084 logical bytes, after exact-path/hash/exclusive-open checks; retained pinned source unchanged. Receipt analysis/storage_cleanup_20260925_policy_bytecode.json. Runner never deletes caches; direct loads bind source and nested frozen import requires absence with python -B. Prior denied paths untouched. No helper/test executed yet.

2026-09-25T01:22:01.1154607+04:00 | Remaining tools bytecode cleanup BLOCKED | Automatic approval review rejected the native PowerShell exact-file cleanup of remaining ignored tools/__pycache__/*.pyc before process creation, with only 'blocked by policy'. No file removed and no receipt command ran. Do not retry by another method. Previously successful cleanup receipts remain valid; required source/evidence unchanged.
