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

2026-09-25T01:26:57.645290+04:00 | D143 evidence retention | Retain32 test/fixture/freeze/receipt/handoff files totaling165864logicalB plus scopedsource/contracts/reviews/validation. Each supports reproduction or originalfailure evidence. Author verified zero Windows sumox_runner_* and WSL /dev/shm sumox_remote_* leftovers after normal cleanup; no persistent binaryfixture/compiler tree/bytecode created. Laterremainingtoolsbytecode deletion was blocked beforeexecution; no retry. Latest C: observation770945024B free, not a reservation.

2026-09-25T01:35:17.972285+04:00 | D144 retention | Retain31 native command/launcher/input/result files448375logicalB pluscompactcheckedreceipt/validation/review. They preserve actualfirstnegative outcome and completeargv/output provenance. No duplicateWindows compiler tree or binaryfixture; no localELF wastransferred afterstructuralrejection. Remote7artifacts/exportremain required fordiagnosis. No additionaldeletion or deniedactionretry.


## 2026-09-25T01:45:58.751607+04:00 - Bounded storage follow-up

A separate read-only audit identified119 old ignored Python caches in four directories,1945273 logical bytes, with tracked sources intact. Automatic approval review rejected the exact-file PowerShell deletion before process creation with only "blocked by policy". No files were removed, no deletion receipt was created and no retry was made. These four candidate directories now join the prior denied targets: tests/tooling/__pycache__, tests/fixtures/__pycache__, tests/fixtures/app_build_overrides/__pycache__, state/analysis/__pycache__.

Transparent LZX compression of22 separately checked immutable historical P2 evidence files recovered3436544 allocated bytes (3.28MiB). All hashes, logical sizes and modification times are unchanged. Receipt: analysis/storage_compression_20260925_small_elf.json. No content was deleted. Independent verification is recorded separately. C: free after compression108322816B; this is an observation, not a reservation. No source, Git history, installed tools, paging or virtual disks changed.

2026-09-25T01:47:55.543075+04:00 | D145 retention | Keep7 diagnostic files577656logicalB pluscompactsource/review/validation/receipt. One170616B ELF binds exactoriginalnegativeartifact; originalreadreceipt preservesactualtransport, complete readelf output supports independentcomparison. No duplicatecompiler tree/checkout/bytecode; productionunchanged. Separate review verifiedallreceipt/sourcebindings. No deniedcleanupretry.

2026-09-25T01:57:12.617230+04:00 | D146 retention | Retain7 observed files3560018B, two small diagnostic compositions and compact notes/review. Reused existing target build; transferred only one of byte-identical debug/temp ELFs, avoiding1764708B duplicate. Full disassembly remained in memory. Required source/map/object/receipt preserved; no temporary build/cache or denied deletion retry. Global free space fluctuated independently toabout600MB; recheck before material work.

2026-09-25T02:01:55.701741+04:00 | D146 new evidence compression | Three required immutable observed files (debug ELF, map, original read receipt) compressed transparently with LZX. GetCompressedFileSizeW-reported storage fell818141B; all hashes, sizes and mtimes unchanged. Receipt analysis/storage_compression_20260925_tls_evidence.json. These records remain necessary; no deletion, duplicate artifact or denied-action retry. No claim that global C: free-space changes equal this delta.

2026-09-25T02:05:56.567390+04:00 | D147 retention | Retain19 frozen test/fixture/plan and actual command-output/receipt files totaling43907B plus small source/contract/review/validation. One transient16MiB fixture exercised bounds in RAM; no persistent binary fixture, compiler tree, checkout or bytecode created. Retain original private CLI usage failure alongside corrected result. No denied cleanup retry.


## 2026-09-25T02:14:29.072366+04:00 bounded disposable-file follow-up

Separate read-only inspection found no new safe deletion candidates: no task-owned
Windows Temp remnants, no repo temporary/partial files outside prior excluded
paths, no new top-level build artifacts, and logs contains only .gitkeep.
Prior denied cleanup paths and active npm caches were excluded, not retried.
Current D148 sources/receipts and D145-D147 evidence are required and retained.
No files were removed in this follow-up. C: free was677650432B at02:11Dubai;
this is a current observation, not a cleanup-recovery claim. D148 reuses existing
board artifacts in memory and returns compact reports instead of binary copies.


## 2026-09-25T02:22:35.566328+04:00 native evidence retention

D148 kept126085B of actual command/input/result/launcher receipts and a small
closure index; no duplicate board binaries or staging/compiler tree. The focused
local entry audit retained one101536B receipt plus its note/review. Two larger
trial captures stayed in RAM and wrote no files. These compact artifacts remain
necessary review/reproduction evidence. No cleanup candidate is introduced; all
local Python used-B. C: free573599744B at02:21Dubai, a fluctuating system value.


## 2026-09-25T02:27:56.075972+04:00 ABI receipts and compression check

D149 retained478121B across seven command/input/result files plus a small launcher;
full original GDB output exists only inside0003.json, not as a duplicate stdout file.
These are required actual observation/review evidence. Seven recent immutable
native read/entry receipts were checked with compact.exe /c /exe:lzx /i /q /a.
The command exited0 but reported zero files recompressed, and measured storage
was unchanged: **0 additional bytes recovered**. Every SHA256, size and mtime
remains exact; no files were deleted. Receipt: analysis/storage_compression_20260925_native_reads.json.
Their preexisting compressed allocation was already smaller than logical size.
C: free526831616B after this check; do not attribute system fluctuations to cleanup.

2026-09-25T02:30:41.957002+04:00: bounded native-reference audit retained one74101B receipt plus concise note/review;1.65MB full disassembly remained in memory and was not written. These are required next-step evidence. No new temporary files or cleanup candidates remain.


2026-09-25T02:41:18.278504+04:00 | P2 matrix host-output cleanup BLOCKED | Separate read-only audit identified111 ignored/untracked completed host outputs (109 objects, two executables),43292808 logical B/18567168 allocated B under state/analysis/P2_matrix_raw/review/build. These paths are disjoint from earlier denied batches. Native PowerShell exact-file deletion was rejected before process creation: automatic approval review stated only "blocked by policy". Zero files deleted; no cleanup receipt command ran. Do not retry these targets by another deletion method. Keep test logs, source snapshot and native evidence intact. Any transparent compression is a distinct content-preserving operation.

2026-09-25T02:42:02.419308+04:00 | Matrix outputs content-preserving compression | After deletion was blocked, transparent LZX compression (compact /c /exe:lzx /f /i /q /a) of the111 exact files returned0 in four batches. Hashes, logical sizes and modification times remain exact. Allocated storage fell18567168 to10072064B:8495104B (8.10MiB) recovered without deleting content. Retain compact receipt analysis/storage_compression_20260925_matrix_objects.json; repetitive directory output replaced by its hash/count and final command summaries, no duplicate inventory. C: free456372224B afterward; system activity affects the global value.

2026-09-25T02:47:25.484559+04:00 | Git internal storage cleanup | Incremental repack -d -l with one thread/16MiB window/8MiB delta cache exited0. Packed5625 loose objects; refs, HEAD and reflogs unchanged; new pack verification and connectivity check PASS. No full/aggressive pack, expiry, history rewrite or source/evidence deletion. Git-reported loose+pack storage fell by43829248B (41.80MiB); C: free rose426369024 to475836416B, including unrelated system/metadata effects. Retain2124B compression receipt and compact analysis/storage_repack_20260925.json. Prior blocked cleanup paths were untouched.

2026-09-25T02:50:29.998683+04:00 | Native dispatch retention | Retain compactGPIO/PWM/RCC selectedinstruction/type receipts and actualD150negative/D151numericread outputs. D151eightfilepacket93015B, no newELF/sourcecopy/compiler tree/bytecode. Entire1.65MBdisassembly and24MBdebugtext stayedinmemory; repetitionnotcopiedtodisk. D150failedby-namequery remainsusefulnegativeevidence. Keepnewclosureindex andscopedreports forreview/resume. No additionaldisposableoutputcreated.

2026-09-25T03:06:32.969894+04:00 | Startup dependency retention | Three compact original JSON receipts total25486B plus small source-route/index notes; all needed for provenance and later run preparation. No binary/source/compiler copies or Python cache. C: free507236352B at03:05Dubai, global fluctuation not cleanup claim. Prior blocked cleanup targets remain untouched.

2026-09-25T03:12:05.758851+04:00 | D152 host retention and fresh disposable check | Retain66687B across9files in P7_static_startup_raw for original inventories, small pure code/frozen tests and actual host receipts; no binaries/source snapshots/compiler tree/bytecode. Independent read-only03:08check found zero new disposable repo/temp remnants since02:14; no deletion or denied-action retry. C: free513421312B at03:11Dubai. All new fixtures remained in memory.

2026-09-25T03:28:45.809989+04:00 | D153 bounded host validation retention | Rawstartupdirectory now23files/160225logicalB total, comprising small source/oracles/bindings and compact originalread/test receipts. Public46/private4 fixture suites used /dev/shm; finalreviewercheck observed zero sumox_capture_contract_* remnants. No compiler tree, binary/source snapshot, pycache or payloadfile. Inline source-sizing trials stayedinRAM; reuseexisting18880B boardutility avoids anotherinstallation. Requiredsource/freeze/actualresults/review retained; prior denieddeletions untouched. C: free449900544B at03:27, system-dependent, notcleanupyield.


## 2026-09-25T03:34:58.350778+04:00 - Requested storage follow-up

Transparent LZX compression of the idle user-provided root arduino-cli.exe
recovered **20,187,648 allocated bytes (19.25 MiB)**. Its SHA256
ba1890afcfc08524f76191b5cc801b0779cb25e81a5e6693eb0e26b50a3f3538,
37,865,984 logical bytes and modification time remain unchanged. The executable
is retained in place; no replacement download or archive was created. Receipt:
analysis/storage_compression_20260925_windows_cli.json.

Separate read-only audit found eight additional disposable cache files totaling
1,739,682 logical bytes: four inactive fwuploader package/firmware index files
under %LOCALAPPDATA%/Temp/fwuploader, and four ignored Python caches with tracked
sources retained. Native PowerShell exact-file removal was rejected before
process creation by automatic approval review, stating only "blocked by policy".
**Zero files were deleted; no retry occurred.** Exact paths are retained in
analysis/storage_cleanup_20260925_new_caches_blocked.json. These join the prior
denied targets. Preserve the historical inventory that mentions the bytecode.

No new compiler tree, binary/source copy, download, hardware operation, paging
change or virtual-disk change was made. Active npm/ADB tools and unknown temporary
files remain untouched. Only compact required cleanup records were added. Global
C: free space varies independently; do not attribute its full change to cleanup.

Separate read-only context rechecked all eight blocked candidates, four retained
sources and the compressed CLI: every hash/size/mtime unchanged and allocation
confirmed. Compact verification: analysis/storage_check_20260925_followup.json.

2026-09-25T03:38:33.159664+04:00 | P7 selection retention | Four compact original read-only inventory/failure/correction receipts total46,882B plus one concise source/observation note. These bind actual dependency selection files and preserve original negatives. No downloaded package, source/binary copy, compiler tree, bytecode or temporary directory; all retained data has provenance/resume purpose. Cleanup commit a5cf1af0 saved20,187,648allocatedB; no blocked deletion retried.

2026-09-25T03:50:08.003244+04:00 | D154 preparation retention | Two native file-only prerequisite receipts37387B and concise review note retained. The58MB library index and16MB builtin executables were hashed in board memory, never copied to host. First55-method synthetichost result retained (53PASS/2FAIL,9967B); temporaryfixtures use /dev/shm and Python-B. No compiler tree, dependency download or duplicate firmware/source snapshot. New wrapper/oracle/freeze records needed for nextstartup boundary; prior blocked cleanup unchanged.
