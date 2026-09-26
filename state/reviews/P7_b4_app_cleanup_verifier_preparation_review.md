# D220 independent staged verifier preparation review

FINAL PASS for one exact nonprivileged read-only verifier invocation, 2026-09-26.
Independent source/data review; no subject import, test, native command,
credential operation or cleanup was executed by this reviewer.

Reviewed intent: state/analysis/P7_b4_app_cleanup_raw/cleanup_stage_verification_intent01.json,
40000 bytes, SHA256 ddd04f0c483906a52c2dfecc0a34b68313ad58f8f1f723917ebed5012fd177b6.
Decoded program: 24297 bytes, SHA256
842efa1bb2c6c0a2a80b916bcc2c92f874f473a4dd4dd55e84da9edf39bf78f0.
Full Windows argv is independently recomputed as 27612 UTF-16 units including
NUL, below 30000. Fixed ADB bytes match admission01's executable pin; serial
2629958581, isolated environment/Python -I -B, 55-second alarm and 70-second
outer bound remain unchanged.

All five intent input pins and its D211 template pin matched current files.
Independently replayed all ten count-one substitutions, checked each before/after
byte count and digest, recovered the exact current program, and reversed all
steps to the exact D211 program. Changes are only source pins/packet, fresh
stage/scratch/copy/original metadata, recipe/owner/result names and schema.
The stage_snapshot, scratch_snapshot and original_snapshot operational bodies
retain their descriptor-relative no-follow reading, full stamps, exact hashes,
ownership/nlink requirements, reopen comparisons and root closing behavior.

The packet contains exactly the current cleanup_root07.py 9608/559c83d7,
cleanup_remoteocd06.py 7708/5fc2150f and unchanged static_remote.py 33321/8ba9b190.
Every decoded byte equals its local source. The program loads only the pinned
helper and recipe definitions under private module names; it never invokes
cleanup main or the credential wrapper, and has no file-write/unlink/privilege
operation. Reading these definitions does not grant cleanup authority.

Actual absence receipt cleanup_absence01.json is 2365 bytes /
d470e54b09f817200293e1a560b986732121a414deece9e7a5a46eccf340d1d3;
actual stage receipt cleanup_stage01.json is 2332 bytes /
714b3a6fc8035a4f62016a1c0ea10ec6c2edc89fc55d1e43ef52cd72e420bf66.
Both have returncode0, empty stderr, local_input_closure=true and exact stdout
hashes. Their parsed states are ABSENT_OWNER_READONLY_CHECKED and
STAGED_CHECKED_NOT_EXECUTED. Sources, board identity and three scratch-copy
stamps agree across both. The intended stage stamp is exactly actual
dev66341/inode274504, owner1000, mode0700; scratch is exactly observed
dev34/inode2007. All expected original/copy/stamp literals match admission01.

Admitted next is one invocation of this exact verifier only. It checks unchanged
UID/GID triples1000; exact three staged files and absent result_root07.json;
fresh scratch, retained originals and board identity before/after; and six
successful closing rows including root descriptor close. Require the returned
STAGED_FILES_VERIFIED_NOT_EXECUTED status, no first error, all six closure rows,
unchanged source pins and local closure before advancing. A failed invocation
consumes this attempt and must be preserved without silent retry.

This review does not admit authentication or deletion, establish protected
process clearance, or prove upload/firmware/sensor/motor behavior. Review of the
actual verifier result and a separate exact authenticated intent remains
required before cleanup. The preparation review is sealed; writes stopped.
