# D206 absence and staging preparation review

26 September 2026, Asia/Dubai. Separate same-model reviewer, local read-only
data/source inspection. **FINAL preparation PASS; no open material finding.**
This accepts only one fixed owner-absence observation followed, if successful,
by one fixed exclusive staging operation. It does not accept actual staging,
protected process-use clearance, authentication or cleanup.

The accepted source/host review remains10091 bytes/SHA256
09b5bed31953e9b9175029ffea742adba3a21c7a7ae3dad8e462406ed56a7baf.
The preparation and source/host reviews are unchanged. This new file is the
sole output for this review. The reviewer ran no subject, oracle, test,
compiler, transport, credential, staging or device operation. Embedded packets
and saved argv were decoded as data, without executing their contents.

## Fixed plans

Both intents are under state/analysis/P7_motor_const_cleanup_raw/:

| Intent | Bytes | SHA256 |
|---|---:|---|
| cleanup_absence_intent01.json | 22926 | 40e8cdfd04c9877e4a1a564e225f8292f55eb3ca05f960e439d5d578ee88b64d |
| cleanup_stage_intent01.json | 23437 | 4a326fd560a72954ee720a4ddc6849b29676d0c773570f11d0a848e6c6403a8d |

The absence template is the pinned21530-byte D200 cleanup_absence01.json,
83913618afbb11a061c9d46e90402f58479808ea09ec354ff49d806b4b034a58.
The stage template is the pinned20649-byte D200 cleanup_stage_intent01.json,
09584e7a4dfe232705201c3f3f254736147813d43daed98fc98caddf673d74d9.
Their programs were extracted from saved argv with shlex.split as data.

For each plan, the reviewer reconstructed all five substitutions: complete
source-pin line, complete encoded packet line, one recipe-load basename,
fixed stage occurrences and fixed scratch inode. Every before/after length,
hash and occurrence count matches; reconstructed bytes equal the complete
current program. No other operational byte differs from its D200 template.

| Program | Bytes | SHA256 | Windows command units |
|---|---:|---|---:|
| owner absence | 18405 | 34d8d0d693aa5ad2499160eb1dcf04ae32af9dafac9c138f8dfac6c9a88f1bc0 | 19091 |
| exclusive staging | 18891 | d79325a963192ec39e5dff579798928823847b5d4c87d9c4360706b0a115d2f2 | 19589 |

The command sizes independently recompute from the saved argv. Each fixed
command uses the selected ADB binary, serial2629958581, shell-T, a minimal
remote environment and absolute /usr/bin/python3-I-B. Each retains the
55-second remote alarm and70-second transport bound. Neither contains sudo,
authentication material, a general privileged shell or firmware operation.

Both decoded packets contain exactly cleanup_root05.py9601 bytes/1be147fe,
cleanup_remoteocd04.py7738 bytes/edd1c8aa and unchanged static_remote.py33321
bytes/8ba9b190:50660 bytes total. Complete decoded bytes equal the actual
reviewed local files, and all three full pin lengths/hashes match. Packet
sources are length/hash checked before definitions are loaded. Only helper
and recipe definitions are loaded under non-main module names; neither
cleanup.main nor wrapper.main/execute is called.

## Bounded operations

The absence program checks the complete expected board identity, all three
retained originals and current scratch inventory at device34/inode1452 with
UID/GID1000. Its use of recipe.inventory is correctly limited to scratch
names. It opens the fixed build parent through the checked helper and calls
no-follow stat on cleanup-app-const-root05. Only FileNotFoundError establishes
absence; an existing owner, symlink or other error refuses. Parent full
identity must remain stable. Originals and board identity are checked again
before emitting ABSENT_OWNER_READONLY_CHECKED. The root descriptor closes in
finally. This operation contains no filesystem mutation.

The staging program independently repeats board, original and scratch checks.
It then exclusively creates cleanup-app-const-root05 with mode0700 under the
fixed checked parent; an existing owner fails rather than being reused.
Exactly three source files are created descriptor-relative with
O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC and mode0600. Each exact byte string is
written, flushed, fsynced, reread and compared, then checked regular,
single-link and UID/GID1000. The final directory child set must equal the
three source names. Directory and parent are fsynced, actual stage identity
is recorded, and originals/board identity close before
STAGED_CHECKED_NOT_EXECUTED is emitted.

No result file is created. There is no unlink, rmdir, recursive operation,
owner repair or fallback. No protected process handles are scanned and no
credential transitions occur. Source definitions include broader capabilities
but their uninvoked entrypoints do not run during these fixed programs.

## Required execution and later review

The coordinator must recheck the exact45 frozen local inputs and these two
intents before dispatch. Run the absence plan first and inspect its complete
saved output, return status and source/identity binding before permitting the
one staging attempt. Saved inventory and this preparation PASS do not prove
the stage is presently absent. Exclusive mkdir remains the decisive guard
against owner creation between observation and staging.

Save each first raw stdout/stderr/returncode and preserve partial failure.
An error, timeout or uncertain transport may leave an uncertain or partial
stage; do not repair, reuse, delete or automatically retry that owner. This
review authorizes no cleanup of such a partial stage.

After successful staging, derive the independent actual-stage verifier from
corrected D200 verification02, using its explicit staged-source read/hash
loop and newly observed stage identity. Never use failed verification01's
scratch-only inventory for staged source names. The fresh verifier and its
results require separate review, including exactly three sources, absent
result_root05.json, full source stamps/hashes, directory ancestry/ownership,
scratch/original bindings, identity/credentials and closing checks.

Authentication remains after separate actual-stage/admission review. Its
single fixed invocation, protected stdin credential channel, exclusive result,
three runtime use scans, first-error preservation, permanent privilege drop
and separate saved-result retrieval/acceptance remain governed by D206.
This preparation accepts no authenticated command or cleanup result.

No staging, deletion, reclaimed storage, process-use clearance, firmware/MCU
operation, motor-run permission, SETTLE remedy, physical acceptance or human
phase gate is claimed. Historical consumed owners and denied cleanup paths
remain untouched. The reviewer has stopped writes to all three final records.
