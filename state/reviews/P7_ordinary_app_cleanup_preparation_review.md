# D211 ordinary-app cleanup preparation review

2026-09-26. FINAL PREPARATION PASS; no material finding remains. This is a
separate, same-model reviewer using reused project context, not a human or
cross-model review. The reviewed proposal is sufficient for coordinator
adoption and exact implementation preparation. It is not native cleanup or
authentication admission. No new cleanup subject exists at this review seal.

Review operations were local saved-file reads, strict duplicate/nonfinite-free
JSON parsing, hashing, AST/source-span inspection and literal transformations
in memory. No project subject was imported or executed; no test, compiler,
device call, staging, credential use or deletion was performed. Only this
review was written. Completed historical reviews and other agents' work were
preserved.

## Checked identities and derivation

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_ordinary_app_cleanup_contract.md | 17371 | `934945d6f26675e4f2d024d772c97cbf18e8fe000510a67ecda5586a1f45dac1` |
| state/analysis/P7_ordinary_app_cleanup_raw/cleanup_derivation01.json | 30865 | `96c12bcd19e94b86945908fd556591e9925c6b842a9e92b82ef0ee8787588694` |
| state/analysis/P7_ordinary_app_cleanup_raw/admission01.json | 24552 | `ed68c4c8c31e16600950a689e362a0d83e3b839e5b46636230b703681e6d025b` |
| state/analysis/P7_ordinary_app_cleanup_raw/observe_admission01.py | 9768 | `a8e3b8b2cf19246e682288b3106bf18bb921a849681695b5e8461ffe3ed3807d` |
| state/reviews/P7_ordinary_app_cleanup_inventory_review.md | 6826 | `c4327b1bb8c7cec0bddefec18ebf77d77f9d4249bf1983e04a4ebd31f8e580cf` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_remoteocd04.py | 7738 | `edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_root05.py | 9601 | `1be147fe67bfafb60275ef1f741f05cfe2262be70c89b0eddbbfc3ec349837d4` |

All 26 derivation input pins independently match actual file lengths and full
digests, including D206 accepted source/actual evidence, corrected staging
verification lineage, inherited oracle/fixtures, retained D203 artifacts,
D207 upload/actual review and the unflashed D208 artifact packet. The
derivation's contract identity matches the sealed contract. Its inventory
binding equals the saved raw inventory for every copied board, directory,
file, original, descriptor, timestamp, match flag and closing-check field.

The prospective subjects were reconstructed entirely in memory. Each counted
old fragment, before/after length and digest, and final identity matches:

| Prospective object | Bytes | SHA256 |
|---|---:|---|
| cleanup_remoteocd05.py | 7740 | `1a59d4b2fc12a0b74a81f65847d7384002423882bd42f5242a98774c8bc02958` |
| Private missing-link projection | 7737 | `e90a5189a76d05bd7674d1bb771b9f480d59b5b26cc4a390109c47431a69d731` |
| cleanup_root06.py | 9607 | `290a7236dc7cc5c6b679a72d5864fb99408dd21bbd30b7b8f3edf74c0fe10aa3` |

The recipe has exactly four count-one substitutions: provenance comment,
complete two-line package block including final LF, inode1452 to1732, and
result schema. The wrapper has exactly six substitutions with counts
1/4/1/1/1/1: stage, recipe basename, recipe length, recipe digest, private
projection digest and wrapper schema. Imports and function names/signatures
remain unchanged. Seven of nine recipe function spans and eleven of fourteen
wrapper spans are byte-identical; the remaining spans differ only by those
metadata substitutions. No operational predicate or error path was added or
removed. The private projection replaces exactly one inner missing-link
continue with raise and has the expected digest; it is not a file mutation.

With the unchanged 33321-byte static_remote.py helper
(`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`),
the three-source staging total is exactly 50668 bytes. Both proposed local
subject paths were absent. No remote stage identity is invented.

## Actual inventory and provenance

The prior observer's five metadata substitutions were independently rebuilt
from D206 and reconciled with its sealed preparation. Its complete transported
program, compressed helper and raw stdout length/digest match the saved
invocation. The program is hash
`59827ae85c73e342ed41f96c8b00b60741c8e846010bc0daedfe547752b1ed54`;
4496-byte stdout is
`cee7326d2b9bf568bb593fc5ce4ac28f01e3d151665e5d10567f529122685d40`.
The single saved call returned0 in0.6157435999484733 seconds with empty stderr,
null first_error, five remote PASS checks and local input closure PASS. The
18656-unit command retains isolated Python, fixed ADB serial, bounded alarm
and transport; no additional observer was run for this review.

Opening/closing board identity agrees: arduino UID/GID1000, expected home,
Linux6.16.7-g0dd6551ae96b/aarch64, Python3.13.5 and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. The exact observer asserts complete
nonprivileged UID/GID triples, although the reported identity object contains
UID/GID rather than those triples. Local ADB and helper pins also match.

Both expected_originals_match and exact_three_d207_copies are true. The
directory is /tmp/remoteocd, device34/inode1732, mode16877, UID/GID1000,
nlink2, size100, with equal full opening/closing stamps. All three copies are
regular single-link UID/GID1000 files on device34:

| Copy | Inode | Bytes | SHA256 |
|---|---:|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 1734 | 95368 | `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7` |
| flash_sketch.cfg | 1735 | 680 | `38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c` |
| zephyr-arduino_uno_q_stm32u585xx.elf | 1733 | 2303728 | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

The 2399776-byte sum is an observed payload total, not recovered storage.
Full integer nanosecond stamps and descriptor identities reconcile without
rounding. Each copy matches its retained original. The package original is
app-motor-const-static01/build/app_motor_observe.ino.bin-zsk.bin, device66341,
inode273237; its complete saved artifact identity agrees with the accepted
D203 compilation and D207 upload evidence. Loader/config originals remain
the exact installed core files. The unflashed ordinary D208 package is a
different 92944-byte image and is explicitly excluded.

The empty recognized compiler candidate list is only nonprivileged process
name/command evidence. Protected cwd/FD use was uninspected. Root06 remote
stage/result absence is likewise unobserved. Neither is inferred from return0,
the inventory review, D206 completion or current source hashes.

## Preserved safety and lifecycle meaning

The actual D206 recipe and wrapper were read against the proposed text. Exact
descriptor-relative ancestry, no-follow/nonblocking opens, regular/single-link
source checks, size/hash/full-stamp checks, close-all attempts and first-error
retention remain intact. The target is fixed; there is no recursive deletion,
additional basename, alternate retained owner or fallback hash/path.

The credential sequence is accurately preserved. Initial wrapper admission
requires root real/effective/saved UID and GID triples, no arguments and
Python-I-B. enter_user clears supplementary groups to1000 and installs
real/effective Arduino IDs while retaining saved root. Each of the three
protected read-only scans raises only effective UID, then restores and
verifies Arduino real/effective IDs before that unlink. Saved root remains
between scans. Finally, both full GID and UID triples are independently
dropped to1000 and checked even on admitted failure. A permanent drop before
the unlink loop would change this implementation and is not claimed.

The unchanged scan retains self exclusion, PID/FD bounds4096, native process
name rejection and same-user cwd/FD inspection. The private missing-link
projection permits a vanished process only after the outer existence check;
permission failure or missing metadata on a surviving process refuses.
There is no unreadable-handle exemption, signal or process mutation. These
scans do not lock the filesystem or cover every other user's descriptors.

Before each sorted unlink, the recipe rechecks identity, exact remaining
inventory/full child stamps and target directory identity after the protected
scan and credential restoration. The empty-directory removal, fsyncs, absence,
retained-original hashes/stamps and final identity checks remain unchanged.
The recipe binds the observed directory inode and captures child stamps
afresh; later admission must reconcile those with the inventory rather than
silently repin drift. The 55-second alarm and70-second transport stay bounded.

run_original retains strict JSON/return/status checks and raw partial stdout,
but has no separate nested-schema-success predicate. The contract correctly
places strict validation of both exact D211 schemas and all nested keys in
actual-result acceptance. That acceptance also requires exact removals,
three scans/restorations, initial/final credential evidence, permanent drop,
no errors, retained originals and full staged-source closure. Scratch absence
or transport success alone is insufficient.

## Oracle and subsequent admission boundaries

All 52 inherited D206 methods are required with their assertion/control-flow
meanings:37 core methods,10 metadata,2 focused and3 D206 supplements. The
recorded147 core assertion sites include four helper sites; metadata34,
focused9 and supplement12/21/7 accounting remains explicit. The historical
method inventory retains historical names/descriptions as provenance; current
negative-identity requirements unambiguously supersede their old image roles.
Independent oracle/fixture/input FINAL must precede its author's inspection
of new subjects. Host counts are predictions until first serial Linux/Windows
receipts and pin/resource closures are reviewed; any supplements need their
own frozen names/counts. No host result is asserted by this review.

The formerly unuploaded D203 image is now the valid D207 positive. Required
negatives retain D190/D195, use the now stale D198/D201 package and add the
unflashed ordinary D208 package. Old inode33/869/1172 refusals remain, with1452
added. Wrong retained owners remain fault/observe/settle/ordinary; const is
the positive owner. Current identities must never replace negative stimuli.
Old root05 source/stage/schema/result ownership cannot be reused.

The fresh stage is exactly
/home/arduino/sumox26_codex_build/cleanup-ordinary-app-root06, with exclusive
result_root06.json. Source/host acceptance precedes separately reviewed
absence/staging. Actual staging must provide fresh directory identity, three
complete source stamps/hashes, absent result and current scratch/original
checks. Corrected D206 verification ancestry uses a separate stage-source pin
table, retaining the D200 failed01 evidence and corrected02 semantics.
No staging/authentication/retrieval program is created or admitted here.

Separate actual-stage/authentication admission must precede at most one exact
protected-stdin invocation; no password enters argv, files or evidence, and
no general elevated shell follows. Partial or uncertain outcomes stop mutation
without automatic retry. Subsequent read-only retrieval must verify result
regularity/single link/ownership and complete raw nested acceptance. Stage
timestamp/size changes from result creation are allowed only with invariant
directory identity fields and unchanged full source stamps/hashes.

The author's two data-only prewrite construction refusals are preserved in
the derivation. One local reviewer comparison initially addressed artifact
bytes at the wrong JSON level; the corrected read-only comparison used
identity.bytes and reconciled the full retained identity. These caused no
subject/test/native execution or evidence modification.

No firmware change, ordinary-app upload, MCU observation, physical inhibition,
SETTLE remedy, RAM/WCET qualification or phase gate follows. Historical denied
cleanup paths and consumed owners remain untouched. Preparation PASS is final
for the exact proposal identities above; future evidence requires separate
review. Reviewer writes stop after sealing this file.
