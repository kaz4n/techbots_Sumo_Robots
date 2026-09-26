# Proposed D206 exact current upload-scratch cleanup

26 September 2026. This proposal prepares a fresh metadata-only derivative of
the reviewed D200 cleanup for the three copies left by D201's upload of the
D198 inhibited diagnostic image. D200/root04 is complete and consumed. Its
source, tests, failures, receipts and retained originals remain evidence.

This document defines proposed software scope and expected bytes. Adoption
under D051 belongs to the coordinator; this draft performs no staging,
authentication or cleanup. Existing user authorization for the scoped cleanup
does not need to be requested again. Actual invocation still requires the
source, host, staging and admission evidence described below. No new general
sudo grant, firmware operation or motor-run authorization is created.

The only future subjects are
`state/analysis/P7_motor_const_cleanup_raw/cleanup_remoteocd04.py` and
`state/analysis/P7_motor_const_cleanup_raw/cleanup_root05.py`. No subject is
written or executed with this proposal. The companion
`cleanup_derivation01.json` records exact fragments, counts and every
intermediate byte identity from local data-only transformations.

## Fixed lineage and current observation

All local paths below are relative to the repository. Verify complete bytes
before transformation and preserve LF endings. The pinned D200 contract's
operational and failure semantics are inherited except for the exact metadata
replacements in this document. No helper, branch, argument, predicate, import,
process exception or filesystem operation is added or removed.

| Fixed input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_settle_cleanup_contract.md | 16277 | 6cb02590369cdce1edd748987df363f99f336c9736dfd06e72906c4578457f47 |
| state/analysis/P7_motor_settle_cleanup_raw/cleanup_remoteocd03.py | 7740 | 6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d |
| state/analysis/P7_motor_settle_cleanup_raw/cleanup_root04.py | 9603 | 13f33327c5474d7c4dee56657a9d93b50e6fcdaee864e1855c916417a53c6290 |
| state/analysis/P7_static_link_probe_raw/static_remote.py | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |
| state/analysis/P7_motor_const_cleanup_raw/observe_admission01.py | 9769 | 462c0534826b19d0722f86c69444a61bc55309514d7741ce196f40292a85ecd8 |
| state/analysis/P7_motor_const_cleanup_raw/admission01.json | 24555 | addee38e4e6a4721b712ff861ded9ae4330b04a1b7f119632320805b4146b3a7 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json | 9648 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 |
| tests/tooling/test_motor_settle_cleanup.py | 12023 | afbc97d1bd310646505d6fdc61b21db26418d27163b44700faa23a52a4842f2b |

The saved nonprivileged inventory returned 0 with empty stderr, no first error,
local-input closure PASS and five remote closing checks PASS. It found
`expected_originals_match=true` and `exact_three_d201_copies=true`. Its recorded
directory is `/tmp/remoteocd`, device 34/inode 1452, UID/GID 1000, mode 16877,
nlink 2, with stable opening/closing full stamps. These are saved observations,
not permission to skip fresh runtime checks.

| Exact scratch basename | Bytes | SHA256 | Retained original |
|---|---:|---|---|
| app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 | /home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf |

Total payload is 2399928 bytes. The recorded child inodes are 1454, 1455 and
1453 in table order; each is regular, single-link and owned by UID/GID 1000.
The unchanged recipe captures complete child stamps afresh at runtime and
compares every remaining child before each unlink. It fixes directory inode
1452, without replacing those runtime stamps with older inventory values.
The package basename still contains `observe`; its retained owner is
`app-motor-settle-static01`. D203's 95368-byte/f15c7ce1 package is a different
image and is not a replacement for this admitted scratch copy.

Expected board identity remains user arduino, UID/GID 1000, home
`/home/arduino`, Linux 6.16.7-g0dd6551ae96b/aarch64, Python 3.13.5, boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, through ADB serial 2629958581.
The inventory did not inspect protected cwd/FD handles or root05 absence.
An empty recognized-compiler list does not establish process-use clearance.

## Exact subject derivation

Starting from the pinned 7740-byte D200 recipe, apply exactly these four
ordered substitutions, each with one old occurrence:

1. `D195` becomes `D201` in the provenance comment.
2. Replace the complete two-line package block below, including its final LF.
3. `info.st_ino == 1172` becomes `info.st_ino == 1452`.
4. `d200-exact-settle-scratch-cleanup-v1` becomes
   `d206-exact-const-scratch-cleanup-v1`.

Old package block:

```python
    'app_motor_observe.ino.bin-zsk.bin': (95360, '85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c',
        '/home/arduino/sumox26_codex_build/app-motor-observe-static01/build/app_motor_observe.ino.bin-zsk.bin'),
```

New package block:

```python
    'app_motor_observe.ino.bin-zsk.bin': (95520, 'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0',
        '/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin'),
```

Required `cleanup_remoteocd04.py`: **7738 bytes**, SHA256
`edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598`.

Preserve the wrapper's exact one-occurrence private projection:

```python
PROJECTION_OLD = b'                except FileNotFoundError:\n                    continue\n'
PROJECTION_NEW = b'                except FileNotFoundError:\n                    raise\n'
```

Required private projected recipe: **7735 bytes**, SHA256
`565acb3988bb0eba0c6865ac27daf5bbc277c85a67204f036bf098b3261b00be`.
Do not write this projection over either source. A missing cwd/FD link reaches
the unchanged outer PID-existence recheck; only a departed PID may be ignored.
Missing metadata for a surviving PID and access denial fail.

Starting from the pinned 9603-byte D200 wrapper, apply exactly these six
ordered substitutions with the stated counts:

| Old literal | New literal | Count |
|---|---|---:|
| cleanup-app-settle-root04 | cleanup-app-const-root05 | 1 |
| cleanup_remoteocd03.py | cleanup_remoteocd04.py | 4 |
| 7740 | 7738 | 1 |
| 6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d | edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598 | 1 |
| 96d1197ec296906958f71c772102fdd34f7979525cde3e41222ee611025274c4 | 565acb3988bb0eba0c6865ac27daf5bbc277c85a67204f036bf098b3261b00be | 1 |
| d200-authenticated-settle-cleanup-v1 | d206-authenticated-const-cleanup-v1 | 1 |

Required `cleanup_root05.py`: **9601 bytes**, SHA256
`1be147fe67bfafb60275ef1f741f05cfe2262be70c89b0eddbbfc3ec349837d4`.
All 9 recipe and 14 wrapper function names/signatures remain unchanged; their
operational bodies change only at the listed fixed metadata literals. Keep
the initial task-authorized-sudo comment. The unchanged 33321-byte helper is
the only other staged dependency. No runtime dependency on this contract,
derivation receipt or admission observer is added.

## Preserved execution and failure semantics

Retain all D200 descriptor traversal, O_NOFOLLOW/O_NONBLOCK, ordinary
single-link source checks, exact source lengths/hashes, directory ancestry,
before/open/after stamps, and all-descriptor close attempts. Preserve first
errors when later closes fail. No path/content fallback is permitted.

Initial wrapper admission requires UID and GID real/effective/saved triples
all 0, no arguments and isolated Python -I -B. After checked source loading,
`enter_user` establishes supplementary groups [1000] and real/effective IDs
1000 while retaining saved IDs 0. Each of exactly three protected process
observations temporarily raises effective UID to 0, then restores and verifies
the Arduino credentials before the corresponding user-owned unlink. The
saved root identity remains between scans. The permanent real/effective/saved
GID and UID drop to [1000,1000,1000] occurs independently in `execute`'s finally
block after cleanup or any admitted failure, with verification and error
preservation. This is the existing D200 sequence; moving the permanent drop
before unlink would change the reviewed operation and is outside this scope.

Retain the 4096-PID/4096-FD bounds, exact self-exclusion, all recognized native
process-name checks and same-user cwd/FD checks. No unreadable-handle skip,
adbd exemption, signal or process action is introduced. Root-only work is a
read-only observation, not a lock. The inherited other-user FD limitation and
possible races remain explicit.

Before mutation, require the complete expected identity/boot, fixed helper
pin, all three retained-original hashes, exact scratch names, regular
single-link UID/GID 1000 children and device 34/inode 1452. Preserve the sorted
three-unlink sequence: protected scan, restored credentials, board recheck,
remaining inventory/full-stamp comparison and directory identity comparison
before each unlink, then fsync. Only an empty directory may be removed by
rmdir, followed by absence verification. Rehash retained originals and recheck
the full board identity afterward. The 55-second alarm is unchanged. No
recursive deletion, alternate retained path or additional deletion is allowed.

Keep raw/partial stdout, removed names, strict duplicate/nonfinite JSON
refusal, first errors, close/restoration/drop errors and every output field.
The wrapper's `run_original` still requires a parsed object, return code 0
and status REMOVED_EXACT_STALE_COPIES. It does not independently reject an
otherwise matching object solely because of its nested schema. No new runtime
schema predicate is introduced. Actual acceptance must separately validate
both exact D206 schemas, complete expected field sets, matching parsed
cleanup_stdout/cleanup_result, source pins/projection, three use checks and
credential observations, initial/final credentials, no errors, exact removed
set, directory removal and retained-original/identity closure. Transport 0
or observed absence alone is insufficient.

## Fresh owner, staged review and one invocation

The sole proposed stage is
`/home/arduino/sumox26_codex_build/cleanup-app-const-root05`; its absence has
not been observed. Require a fresh no-follow absence check before exclusive
creation. Stage only cleanup_root05.py, cleanup_remoteocd04.py and
static_remote.py with exact reviewed bytes, plain single-link UID/GID 1000
files and verified ancestry. The expected source total is 50660 bytes.
Record the actual fresh stage identity after creation; do not invent or reuse
D200's stage inode. Existing or uncertain owners are not reused or repaired.

The sole result path is this stage's `result_root05.json`. Create it
exclusively with no-clobber behavior; never overwrite a prior result. All
root02/root03/root04 attempts and results remain consumed.

Use the corrected D200 `cleanup_stage_verification02.json` program semantics
(39917 bytes, SHA256
2c7a1ad2955f4835c05f289ca63bba25a210772c51cd65750ada997c7d4699bb):
an explicit staged-source read/hash loop with its own source pin table and
full opening/closing stamps. Keep recipe.inventory limited to scratch names.
The preserved verification01 failed because it used scratch-only PINS for
staged source names; do not copy that error or relabel its failure. Extract
historical programs from saved argv using `shlex.split(argv[-1])` as data,
then derive and review any fresh fixed metadata before use. This proposal
creates no staging or device script.

Independent stage review must verify exactly three sources and absent result,
fresh scratch/original stamps and hashes, identity/credentials and all closing
checks. Source and host reviews precede staging; stage/admission review
precedes the single authenticated invocation. Use absolute /usr/bin/python3
-I -B and the fixed root05 wrapper, an exclusive result and the unchanged
70-second transport bound. Supply authentication only through protected stdin;
never put it in argv, files, saved intent, reports or logs. No additional
elevated command or general root shell is admitted.

After one attempted invocation, preserve the first error and stop mutation
on partial failure, authentication uncertainty or transport uncertainty.
There is no automatic retry or silent repinning. A separate read-only
retrieval/review must verify the raw saved result, strict nested acceptance,
scratch absence and all retained originals and staged sources on reopen.
Allow the stage timestamps/size to change from creation of the result while
requiring unchanged device/inode/mode/owner/nlink and unchanged complete source
stamps/hashes. The result must be a fresh ordinary single-link UID/GID 1000
file with stable descriptor/path identities. Permanent-drop and retained-file
success cannot be inferred from a missing scratch directory.

## Independent tests and evidence limits

Freeze a new independent oracle and all its inputs before its author reads,
hashes, imports or executes the new subjects. Retain all 49 historical D200
methods: 37 credential/descriptor methods with 147 assertion calls, 10 metadata
methods with 34 assertion calls and 2 focused refusal methods. Historical
files and failure/adjudication evidence remain unchanged. Use checked private
fixture projections for current paths, source identities, schemas, inode and
package metadata; record every transformation and resulting identity.

The old oracle's "future D198" image is now the valid current copy because
the independently observed D201 upload changed the binding. Preserve its
refusal meaning by explicitly testing stale D190 (95328/deb40317), stale D195
(95360/85b05c56), and unuploaded D203 (95368/f15c7ce1) package alternatives.
Refuse old inode 1172, old root04 stage/result/source identities and wrong
retained paths. Preserve earlier stale-inode/basename cases where applicable.
Do not reinterpret a valid current package as a refused future image or weaken
any predicate to satisfy a result.

Include independent four-step recipe/six-step wrapper reconstruction, private
projection identity, unchanged nonmetadata bytes, exact current payload and
three-only unlink/rmdir behavior, elevated read-only scans, restoration before
mutation, permanent drop on all admitted exits, first-error preservation,
fresh owner/result, and emitted D206 schemas. Source-schema substitution
refusal and coordinator actual-result schema acceptance are separate checks;
do not claim the unchanged wrapper has a nested-schema predicate. All fixtures
use controlled fakes; no actual sudo, credentials, process handles, device or
cleanup may be exercised by host tests.

Run Linux and Windows host suites serially after the independent freeze. The
historical component predicts 49 Linux passes and 12 Windows passes with 37
explicit Linux-only skips; new supplements have separately frozen counts.
Preserve first failures, raw streams, input closures and platform skip reasons.
Host/source success does not replace fresh authenticated process-use scans.

Keep compact derivation, source, review and result evidence. Any later staged
source removal is a separate cleanup. Do not touch historical policy-denied
paths. Record actual storage recovery only after reviewed receipts establish
it. This scope does not compile, upload, reset or read the MCU, change firmware,
alter motor authorization, resolve physical acceptance, prove a SETTLE remedy,
establish RAM/WCET or pass a human phase gate.
