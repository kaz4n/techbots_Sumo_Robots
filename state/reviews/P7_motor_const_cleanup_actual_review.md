# D206 actual cleanup review

26 September 2026, Asia/Dubai. Separate same-model reviewer.
**FINAL PASS: exactly the three admitted D201 scratch copies were removed;
retained originals and staged sources are unchanged. No open material finding.**
The root05 owner/result and authenticated attempt are consumed. No retry or
reuse follows from this result.

This new review is the sole owned output. Review used local saved bytes,
strict JSON parsing, hashes and comparisons with the previously reviewed
sources, stage snapshots and fixed intents. The reviewer executed no subject,
test, compiler, device call, credential transition, process scan or cleanup,
and did not access a credential value. Earlier reviews and all historical
attempts, failures and receipts remain unchanged.

## Exact actual evidence

All paths below are under state/analysis/P7_motor_const_cleanup_raw/.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| cleanup_authenticated_intent01.json | 1406 | cee3ab13e599bddf33e9f8d0f945dd1f242910c03272d77e03b638413204bda1 |
| cleanup_authenticated_transport01.json | 548 | 48cfa2de7174f9cdab121664b893eb0e9fa1852b19cfde99903ddb505a2dfb31 |
| cleanup_retrieval_intent01.json | 34045 | 4c2c6f1d24730a0a826d66f5712c896e231410f63adaeae4ea883d5dbab7d9ca |
| cleanup_retrieval01.json | 16957 | d45d5447fd006bb731e011ac8bc8ab6cd74cd3de406ebc5afc566bcaa6cff496 |
| cleanup_root05_actual_result.json | 6367 | 3b8f035a6b282ada5a5fbf5992a5343d27a3dc245962ee7f64032757420e11e8 |

The transport binds the exact authenticated intent and final admission review
6c730950623db98d9475ea2ffbde0b04b2f6600bc7469c427a6a7b230df62395.
It records native_invocations=1, return0, empty stdout/stderr, null first_error
and local_input_closure PASS. Its saved envelope spans14:06:03.440853 to
14:06:17.154730 Dubai, including host credential input; this interval is not
a measured cleanup runtime. The fixed command retains no-clobber output,
sudo-S, absolute Python-I-B and the70-second bound. Credential handling is
recorded as Windows no-echo console to native stdin only; no value is present
in the inspected intents, result or transport receipt.

The separate read-only retrieval binds that actual transport and the reviewed
retrieval intent. It returned0 in0.6386513s, with empty stderr, null first_error
and local_input_closure PASS, from14:06:35.377221 to14:06:36.016721 Dubai.
The raw6367-byte local result exactly equals the decoded descriptor-read
base64 payload in the retrieval reply. The retrieved file's length/hash and
the outer saved_result metadata agree exactly.

## Strict result acceptance

Strict parsing of the outer result, nested cleanup_stdout and retrieval
reply found no duplicate keys or nonfinite constants. The complete expected
outer and nested field sets match. The exact schemas are
d206-authenticated-const-cleanup-v1 and d206-exact-const-scratch-cleanup-v1.
Both status fields are REMOVED_EXACT_STALE_COPIES; cleanup_returncode is the
integer0. Parsed cleanup_stdout equals cleanup_result exactly. Both first_error
fields are null; privilege_drop_errors is empty and no close-error field is
present. Acceptance therefore goes beyond the unchanged wrapper's narrower
object/returncode/status predicate.

The exact sorted removed list is:

| Scratch basename | Bytes | SHA256 |
|---|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |

Total removed payload is2399928 bytes. The actual directory_before equals
the accepted full device34/inode1452 stamp; files_before equals all three
complete accepted child stamps/hashes from stage verification7de3bb3a.
directory_removed and originals_unchanged are both true. The checked source
allows only these three sorted descriptor-relative unlinks and empty-directory
rmdir. No recursive or alternative-path deletion is admitted by this result.
The package is the D198 image uploaded in D201 and retained under
app-motor-settle-static01/build, not the unuploaded D203 image.

The source pins exactly match the reviewed recipe7738/edd1c8aa and unchanged
helper33321/8ba9b190. The one-occurrence private projection has the exact
before/after missing-link fragments and digest
565acb3988bb0eba0c6865ac27daf5bbc277c85a67204f036bf098b3261b00be.
The reviewed wrapper1be147fe was also preserved with its full staged stamp
and hash in the independent retrieval.

## Credential sequence and use evidence

Initial real/effective/saved UID and GID triples are[0,0,0]. Exactly three
observations have their complete expected fields, no errors and results
identical to the corresponding nested use_checks. Each reports165 process
names and3 same-user handle sets. Before and after every scan, UID/GID triples
are[1000,1000,0]; during each scan UID is[1000,0,0] and GID remains[1000,1000,0].
The pinned control flow returns from this verified restoration before each
unlink. The receipt plus that reviewed ordering supports user-owned mutation;
it is not an independent syscall trace.

Final UID and GID triples are both[1000,1000,1000], with no permanent-drop
error. Thus the cleanup process's saved root identity was removed according
to the checked code and saved result. The inherited limitation remains exact:
other-user FD coverage is not established, and process observations can race.
These successful checks are not a global lock or clearance for a later task.

## Independent post-cleanup closure

The retrieval has the complete expected field set, exact schema
d206-independent-cleanup-retrieval-v1, status
SAVED_RESULT_RETRIEVED_POSTCLEANUP_CHECKED and null first_error. All six named
closing checks PASS: stage_and_result_reopen, scratch_absence_reopen,
originals_reopen, board_identity, credentials and root_descriptor_close.
Both no-follow scratch-absence observations are true.

The stage remains device66341/inode273259, directory0700, UID/GID1000,
nlink2 and size4096. Its mtime/ctime changed from1790416789195859820 to
1790417177351535349 as expected from result creation; the complete directory
stamp remains stable during retrieval/reopen. The exact three sources have
unchanged complete stamps/hashes from pre-cleanup verification, with source
inodes273260/273261/273262 and total50660 bytes. No staged source removal is
claimed or authorized here.

The new result is an ordinary single-link UID/GID1000 file, device66341/
inode273263, with stable full opening/reopen identity. Its path stamp and
descriptor identity agree on size6367, device/inode and timestamps. Its hash
is the exact saved raw-result hash above. The checked reader requires the
stage child set to be precisely the three sources plus result_root05.json.

Each retained original's full path stamp, descriptor identity, length and
hash matches both the pre-cleanup verification and post-cleanup reopening.
The original package remains at its exact settle build path; installed
configuration and loader remain at their exact core paths. Full board identity
is unchanged, including boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. The retrieval
observer's real/effective/saved UID/GID triples remain1000 before and after.

All45 coordinator-frozen inputs and all five retrieval-intent inputs
independently rehash unchanged. Actual transport/result/source bindings and
the complete post-cleanup file evidence agree; no retry or guard relaxation
was needed. This establishes exact removal of2399928 payload bytes from the
target scratch directory, not a measured host free-space increase.

The cleanup is complete within D206. Root05 and its result remain consumed
evidence; later staged-source cleanup is a separate scope. This result does
not flash/reset/read the MCU, change firmware or motor-run permission, prove
a SETTLE remedy, qualify RAM/WCET or physical behavior, or pass a human phase
gate. The reviewer has stopped writes after this final actual-result record.
