# D206 actual stage and exact invocation admission review

26 September 2026, Asia/Dubai. Separate same-model reviewer.
**FINAL PASS; no open material finding.** The actual read-only stage evidence
is accepted. Within existing D206 authorization, this admits at most one exact
authenticated invocation bound below, followed by the exact read-only retrieval.
Actual cleanup success remains a separate result review.

This new file is the sole output. All earlier reviews remain immutable. The
reviewer inspected local saved bytes and sources only, using strict JSON,
hashes, AST data, decoded packets and literal derivations. No test, subject,
transport, credential, staging, process scan or cleanup was executed by this
reviewer. No credential value was read or retained.

## Actual stage evidence

The sole saved verification is
state/analysis/P7_motor_const_cleanup_raw/cleanup_stage_verification01.json,
9876 bytes, SHA256
7de3bb3a0d7a81feac727e1c7dc3a6d67e8d9519a7070c6c0a2eb051f3fc35f9.
It binds the reviewed verifier intent8776a33d82394e595bb57889166dadd1e4caef00674b57e971de7dc119afa731,
whose source preparation review isf7dadb77d65c6ea2eb91e2b01bbdf9f1032b80474a4fb9ebaaf02011358bfabb.
The call records14:02:23.917959 to14:02:24.412405 Dubai, return0, empty stderr,
null host first_error,0.4929774s elapsed and local_input_closure PASS.

Strict parsing rejects duplicate keys/nonfinite constants and found neither.
The parsed remote object has the complete expected field set, exact schema
d206-independent-stage-verification-v1, status
STAGED_FILES_VERIFIED_NOT_EXECUTED, null first_error and explicit
process_use_clearance=false. The six closing entries, in expected order, are
stage_reopen, scratch_reopen, originals_reopen, board_identity, credentials and
root_descriptor_close; every status is PASS.

All opening/closing stage, scratch, original, board and credential observations
are exactly equal. The full board identity matches the admitted inventory:
Arduino UID/GID1000, expected home/kernel/aarch64/Python and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. Real/effective/saved UID and GID triples
are[1000,1000,1000] at both ends. This was nonprivileged file observation,
not the cleanup's protected process-use scan.

The fresh stage is
/home/arduino/sumox26_codex_build/cleanup-app-const-root05,
device66341/inode273259, UID/GID1000, mode16832 (directory0700), nlink2,
size4096. Full stamps match the stage creation receipt5bcd2819 and the
reviewed verifier's fixed expected_stage. Its child set contains exactly:

| Source | Inode | Bytes | SHA256 |
|---|---:|---:|---|
| cleanup_root05.py | 273260 | 9601 | 1be147fe67bfafb60275ef1f741f05cfe2262be70c89b0eddbbfc3ec349837d4 |
| cleanup_remoteocd04.py | 273261 | 7738 | edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598 |
| static_remote.py | 273262 | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |

All are regular0600, single-link and UID/GID1000. All complete opening/closing
source stamps and hashes match; total source bytes50660. Result absence is
true on both no-follow observations. This evidence does not authorize replacing
an owner or overwriting a result created later.

Scratch device34/inode1452 and its complete three-file stamps/hashes equal
the independent inventory, absence/staging receipts and verifier literals.
The admitted payload remains2399928 bytes:95520-byte D201 package e4000781,
680-byte flash configuration38706cee and2303728-byte loader39d4a4fd. The
retained originals' complete path/descriptor identities and hashes also match
on reopen. The package remains under app-motor-settle-static01/build with
the app_motor_observe basename; there is no alternate original path.

All45 coordinator inputs and all seven verifier-intent inputs independently
rehash unchanged. The current selected ADB binary is6303744 bytes/SHA256
e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982,
matching the admitted inventory. Earlier source/host52LinuxPASS and
15WindowsPASS/37covered skips remain bound by final review
09b5bed31953e9b9175029ffea742adba3a21c7a7ae3dad8e462406ed56a7baf.

## One fixed authenticated invocation

The immutable intent is cleanup_authenticated_intent01.json under the same
raw directory:1406 bytes, SHA256
cee3ab13e599bddf33e9f8d0f945dd1f242910c03272d77e03b638413204bda1.
Its source, source/host review, verifier review and actual verification digests
all match the inspected bytes. Its prerequisite is this final stage review;
the coordinator must bind and enforce this review's final hash before dispatch.

Independent comparison with the consumed D200 intent5f78e1dc proves exactly
three command substitutions: cleanup-app-settle-root04 becomes
cleanup-app-const-root05 at two occurrences, cleanup_root04.py becomes
cleanup_root05.py once, and result_root04.json becomes result_root05.json
once. Every other argv byte and the70-second bound remain unchanged.

The fixed selected ADB/serial2629958581 shell-T command uses set-C no-clobber
redirection and sudo-S with an empty prompt, -H, absolute /usr/bin/python3,
-I-B and only the exact root05 wrapper. Output is exclusively redirected to
the same stage's result_root05.json. No general privileged shell, extra
elevated command, source argument, firmware action or retry is admitted.
The result is created by the Arduino shell; its later ordinary single-link
UID/GID1000 identity must still be independently checked.

Credential transport is the existing Windows no-echo console to native stdin
only. The credential is not in argv, this intent or any review, and must not
be saved in files, logs, transcripts or receipts. The existing user delegation
and specific D206 scope supply authorization; this review neither creates a
general sudo grant nor changes motor-run permission.

The wrapper must repeat every reviewed guard. Exactly three protected read-
only process scans restore verified Arduino effective credentials before
their respective user-owned unlinks, retaining saved root between scans.
Permanent UID/GID triples1000 are attempted independently and verified in
finally. Scratch identity/content/use drift, unreadable surviving handles,
restoration or drop failures remain refusals. No observation is a lock;
other-user FD/race limitations remain explicit.

Use fresh exclusive local evidence owners and record at most one native
attempt. Preserve all raw streams and first errors. On authentication,
transport or partial-cleanup uncertainty, stop mutation and do not retry,
repair a stage or infer success from absence. Old roots02/03/04 and denied
cleanup paths remain excluded.

## Prepared read-only retrieval

The reviewed retrieval intent is cleanup_retrieval_intent01.json:34045 bytes,
SHA2564c2c6f1d24730a0a826d66f5712c896e231410f63adaeae4ea883d5dbab7d9ca.
Its program is24635 bytes,
557c5c41f1ba05c394e2039c7df56744eabdea3943b29059eed38be35ad9bf4d,
with independently recomputed28045 Windows command units. All five fixed
inputs rehash correctly.

The reviewer reconstructed all nine substitutions from the D200 retrieval
receipt46397 bytes/b7b776c998ace2c3e8e44e6208db298298c935b587ad5bbdbf172f843aa35c06:
complete source-pin/packet lines, three current stage/source/original
assignments, and recipe/stage/result/schema literals. Every occurrence count
and intermediate identity matches; all remaining operational bytes are exact
historical code. Its decoded three-source packet equals the reviewed local
files. Its stage, complete source and original expectations equal this actual
verification's accepted snapshots.

After the single authenticated attempt, this permits one fixed read-only
retrieval using the same minimal environment/absolute Python-I-B,55-second
alarm and70-second transport bound. It invokes no cleanup/main/credential or
process action. It requires exactly the original three sources plus the new
result, with unchanged stage device/inode/mode/owner/nlink. Stage size and
timestamps may change through result creation; they must stay fully stable
during the retrieval and reopening. Every source's complete stamp and hash
must still equal its accepted pre-cleanup record.

The result must be regular, single-link, UID/GID1000 and positive-sized at
most65536 bytes. Descriptor/path identity, raw length and hash are captured;
its exact bytes are retained in base64 before later absence/original checks.
The program checks scratch absence via no-follow stat, reopens retained
originals against their full expected records, reopens the source/result
snapshot and checks raw equality, and closes full board identity/credential
triples. Six closing checks include descriptor close. First errors remain
visible and later close errors cannot replace them. An incomplete result or
remaining scratch causes failure; it does not trigger mutation or retries.

The65536-byte reply bound and existing first-error behavior remain unchanged.
Retrieval success means the saved file and post-cleanup file conditions were
observed; it does not independently parse/admit the nested cleanup schemas.
The subsequent actual-result review must strictly parse both exact D206
schemas, complete field sets, matching cleanup_stdout/cleanup_result, source
and projection pins, exactly three observations/use checks, scan/restoration
credentials, no errors, permanent drop, exact removed set, directory removal
and original/source closure. Transport0, retrieval status or scratch absence
alone is insufficient.

No authenticated attempt, cleanup result, reclaimed storage, firmware/MCU
operation, SETTLE remedy, physical qualification or phase gate is claimed by
this review. The reviewer has stopped writes after this final admission and
retrieval-preparation record.
