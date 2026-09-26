# D211 absence and staging preparation review

FINAL PREPARATION PASS, 26 September 2026. The two fixed intents are ready for the coordinator's one read-only absence observation followed, only on accepted success, by one exclusive three-source staging call. This review does not establish owner absence, actual stage identity, protected-process clearance, credentials or cleanup success.

Separate same-model reviewer with reused context. I read and compared saved data/program text, parsed shell arguments and AST, decompressed source packets as data, and recomputed hashes/counts. No submitted program or subject was imported/executed; no test or device call occurred. Only this review was written.

## Exact inputs and reconstruction

Paths abbreviated RAW are state/analysis/P7_ordinary_app_cleanup_raw/. Source/host review is state/reviews/P7_ordinary_app_cleanup_review.md,9123B/f033655ea6d72c14b092958e73b885887e56d3b57ad1f4fcb198365103dc1713. Adopted contract remains17371B/934945d6f26675e4f2d024d772c97cbf18e8fe000510a67ecda5586a1f45dac1.

| Intent | Bytes | SHA-256 |
|---|---:|---|
| RAW/cleanup_absence_intent01.json | 23336 | cde5399169f34b3b659d94ef461f6f90fd05a99ed36c95c6b7357945f2eb60ee |
| RAW/cleanup_stage_intent01.json | 23843 | ae4f9feb56df5197b5cc3ec41fd482f7cffede5d67f5315cad4411f18984697f |

The D206 template intents are cleanup_absence_intent01.json,22926B/40e8cdfd04c9877e4a1a564e225f8292f55eb3ca05f960e439d5d578ee88b64d, and cleanup_stage_intent01.json,23437B/4a326fd560a72954ee720a4ddc6849b29676d0c773570f11d0a848e6c6403a8d, under P7_motor_const_cleanup_raw.

For each I reconstructed all five ordered steps and checked every before/after length/hash and occurrence count: complete source-pin assignment; complete compressed packet assignment line; recipe04→05; fixed root05→ordinary-root06 stage references; scratch inode1452→1732. The packet step identities describe the complete assignment line, not merely the base64 token. No other program byte differs. The new absence program is18391B/a9b3072eec83856f81ca48ee37d7063211fbafb674819728049b9dde380176b4; stage program18880B/fec18c3a11ea42716f9a1ba02535ed1829161f23e7a5e663b6dc498f24308b1a.

Both packets have exactly three entries totaling50668 uncompressed bytes, byte-identical to the reviewed sources:
cleanup_root06.py9607B/290a7236dc7cc5c6b679a72d5864fb99408dd21bbd30b7b8f3edf74c0fe10aa3;
cleanup_remoteocd05.py7740B/1a59d4b2fc12a0b74a81f65847d7384002423882bd42f5242a98774c8bc02958;
static_remote.py33321B/8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8.

## Command and operation boundaries

The complete native argv prefixes match the accepted templates: fixed local adb.exe, serial2629958581, shell -T, env -i with fixed Arduino HOME/USER/LOGNAME/PATH/LANG and absolute /usr/bin/python3 -I -B -c. Recomputed Windows command lengths including NUL are19078 and19579 UTF-16 units, within the unchanged30000 ceiling. Both retain70s outer timeout and55s remote alarm.

Each program verifies all three payload hashes/sizes before use. It loads the pinned helper and recipe under fixed module names; the recipe's guarded main is not invoked. The root wrapper is packet data only, not imported. Neither plan calls recipe.cleanup, recipe.processes, sudo, privilege setters, unlink/rmdir, a firmware tool or an MCU operation.

The absence program checks exact full identity/boot and current retained originals; opens current /tmp/remoteocd, requires device34/inode1732 and UID/GID1000, and inventories its exact three current copy names/content/single-link identities. It opens the checked build parent, records its full stamp, requires no-follow stat of cleanup-ordinary-app-root06 to fail with FileNotFoundError, and rechecks the parent stamp. Originals and full identity are checked again before a read-only ABSENT_OWNER_READONLY_CHECKED receipt. No filesystem mutation call occurs in this program.

The stage program repeats identity/original/scratch admission, then mkdir of the sole fixed cleanup-ordinary-app-root06 owner requests0700 and refuses an existing owner. Within its checked descriptor it creates only the three named files using O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC and requested0600. Each write must be complete; flush/fsync and descriptor-based readback equality follow, with ordinary single-link UID/GID1000 checks. Exact directory names, directory/parent fsync and the actual new stage identity are recorded. Closing original/board checks precede STAGED_CHECKED_NOT_EXECUTED. It creates no result_root06.json and performs no cleanup. Requested modes are not substituted for actual later mode observations.

## Acceptance limits and next step

No material plan finding remains. Preserve complete argv/streams/return code and initial/closing evidence from each actual call; a successful plan review is not a successful remote call. Inspect the actual absence result before staging. Exclusive creation still guards the gap between calls; an existing or uncertain owner is not reused.

These inherited programs record the scratch inventory before their operation and recheck retained originals/board afterward; they do not claim a post-stage scratch reinventory or protected-process scan. Consequently the separately required staged verification must reopen the actual new stage and all three sources, compare its observed device/inode/mode/owner/link identity and full source stamps/hashes, verify exact names/absent result, and freshly reconcile scratch/original records and full identity. No stage inode is predicted here.

A partial stage, timeout or uncertain transport stops the sequence and preserves the consumed/partial owner; no rollback, repair or automatic retry is authorized by these intents. Authentication and exact cleanup invocation require the separate actual staging/admission review. Protected handles remain uninspected until that later authorized root-assisted observation. No deletion, storage recovery, upload, firmware change, physical qualification or motor permission follows this preparation PASS.
