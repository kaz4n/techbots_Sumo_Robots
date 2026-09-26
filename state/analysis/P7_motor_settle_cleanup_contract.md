# D200 exact current upload-scratch cleanup

26 September 2026. Prepare a new metadata-only derivative of the reviewed D196
cleanup for the three copies left by D195's upload of the D193 observer image.
The retained originals are still needed. D191 and D196 cleanups and their
owners are consumed; neither may be rerun. Preserve all historical source,
tests, failures, receipts, retained firmware and staging owners.

This contract records the proposed immutable software scope and expected
bytes. It does not claim root04 is absent, that staging/authentication occurred,
or that deletion is authorized by this document alone. Root will separately
decide adoption under D051 and the user's current continuation. No source,
test, native operation, credential action or deletion accompanies this draft.

The only future implementation files are
state/analysis/P7_motor_settle_cleanup_raw/cleanup_remoteocd03.py and
state/analysis/P7_motor_settle_cleanup_raw/cleanup_root04.py. Derive them by
the exact tables below; do not introduce a generic cleanup command, path
argument, process exception, new helper or altered operational predicate.

## Fixed inputs and current observation

All paths are relative to the repository. Check complete source bytes before
transformation; preserve LF endings and every byte outside the replacements.

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_run_raw/cleanup_remoteocd02.py | 7735 | 1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a |
| state/analysis/P7_app_motor_observe_run_raw/cleanup_root03.py | 9606 | a089cc3bac9d8df3ffe53947e22b1bb4ffa139a733c7ebb1f5ba62e6d5bd804f |
| state/analysis/P7_static_link_probe_raw/static_remote.py | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |
| state/analysis/P7_app_motor_observe_cleanup_contract.md | 12460 | 7258230a63f48e09401186b8ad3bed09f958006909610cea835926427a3609f6 |
| state/analysis/P7_motor_settle_cleanup_raw/observe_admission01.py | 9770 | e4db653bf71bb2201549ea0ade3d637521520d6e2e9747473cf52fd6688aaa83 |
| state/analysis/P7_motor_settle_cleanup_raw/admission01.json | 24558 | e95ebed4ee3d6441abccced02adbcc4857fe5f10418d94e158b009d3edecf922 |
| state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json | 9651 | 5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b |

The nonprivileged admission returned0 with empty stderr, first_error=null,
local-input closure PASS and five remote closing checks PASS. It observed
the unchanged board identity before/after: user arduino, UID/GID1000,
home /home/arduino, Linux6.16.7-g0dd6551ae96b/aarch64, Python3.13.5,
boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 through serial2629958581.
It observed /tmp/remoteocd as directory device34/inode1172, UID/GID1000,
mode16877, nlink2, stable before/after. It did not inspect protected cwd/FD
handles and supplies no process-use clearance. Empty compiler candidates
are not a substitute for the cleanup's authenticated complete same-user scan.

| Exact scratch basename | Bytes | SHA256 | Retained original |
|---|---:|---|---|
| app_motor_observe.ino.bin-zsk.bin | 95360 | 85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c | /home/arduino/sumox26_codex_build/app-motor-observe-static01/build/app_motor_observe.ino.bin-zsk.bin |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf |

The payload total is2399768 bytes. The admission observed each copy as regular,
single-link, UID/GID1000, with unchanged path/descriptor stamps and matching
retained originals. The child's observed inodes were1174,1175,1173 in table
order. As before, the recipe fixes the directory identity but obtains each
child's complete initial runtime stamp afresh and compares every remaining
child against it before each unlink; it does not replace those guards with
the nonprivileged inventory's older child stamps.

The D193 artifact receipt binds the retained observer package. Do not redirect
to D198's new95,520-byte/e4000781 package: it has not replaced these D195 upload
copies. No D198 artifact or source is removed by this cleanup.

## Exact recipe derivation

Starting from the checked7735-byte cleanup_remoteocd02.py, apply these four
ordered substitutions. Require each old fragment exactly once.

1. D190 -> D195, in the provenance comment only.
2. Replace the complete two-line payload block below with the new block,
   including its final LF.
3. `info.st_ino == 869` -> `info.st_ino == 1172`.
4. `d196-exact-observer-scratch-cleanup-v1` ->
   `d200-exact-settle-scratch-cleanup-v1`.

Old payload block:

```python
    'app_motor_fault.ino.bin-zsk.bin': (95328, 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c',
        '/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino.bin-zsk.bin'),
```

New payload block:

```python
    'app_motor_observe.ino.bin-zsk.bin': (95360, '85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c',
        '/home/arduino/sumox26_codex_build/app-motor-observe-static01/build/app_motor_observe.ino.bin-zsk.bin'),
```

Required cleanup_remoteocd03.py:7740 bytes, SHA256
6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d.

The wrapper keeps exactly the reviewed one-occurrence private projection:

```python
PROJECTION_OLD = b'                except FileNotFoundError:\n                    continue\n'
PROJECTION_NEW = b'                except FileNotFoundError:\n                    raise\n'
```

Required private projected recipe:7737 bytes, SHA256
96d1197ec296906958f71c772102fdd34f7979525cde3e41222ee611025274c4.
Never write that projection over either source. A missing cwd/FD link reaches
the unchanged outer PID-existence recheck; only an actually departed PID may
be ignored. Missing metadata for a surviving PID and access denial fail.

## Exact wrapper derivation

Starting from checked9606-byte cleanup_root03.py, apply only these ordered
replacements, checking the old occurrence count at each step:

| Old literal | New literal | Count |
|---|---|---:|
| cleanup-app-observe-root03 | cleanup-app-settle-root04 | 1 |
| cleanup_remoteocd02.py | cleanup_remoteocd03.py | 4 |
| 7735 | 7740 | 1 |
| 1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a | 6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d | 1 |
| b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1 | 96d1197ec296906958f71c772102fdd34f7979525cde3e41222ee611025274c4 | 1 |
| d196-authenticated-observer-cleanup-v1 | d200-authenticated-settle-cleanup-v1 | 1 |

Required cleanup_root04.py:9603 bytes, SHA256
13f33327c5474d7c4dee56657a9d93b50e6fcdaee864e1855c916417a53c6290.
These three derived identities were computed from byte transformations only,
without source execution or writing the new implementation files.

The wrapper's first comment already describes task-authorized sudo; leave it
and every operational byte unchanged. The33321-byte static_remote.py remains
the sole other staged dependency. No runtime import of the admission observer
or this contract is introduced. Recipe/helper sources are authenticated by
the unchanged pins and descriptor-based source reader.

The recipe and wrapper public callables and signatures stay exactly D196:
require, credentials, error_record, stamp, read_source, load_cleanup,
enter_user, observe, drop_privilege, unique_object, invalid_constant,
run_original, execute and main on the wrapper; all existing recipe functions
remain intact. No new CLI or argument is accepted.

## Preserved operational and failure guards

Initial wrapper admission requires real/effective/saved UID and GID all0,
no arguments, isolated Python-I-B and exact staged source pins. Keep full
directory-FD traversal, O_NOFOLLOW/O_NONBLOCK, ordinary single-link source
files, UID/GID1000 ownership, exact lengths/hashes, all before/open/after
stamps, and all-descriptor close attempts. Preserve the first error when a
later close also fails; no permissive source-read fallback is allowed.

After loading the checked definitions, enter_user sets supplementary groups
exactly[1000] and real/effective UID/GID1000 with saved0 temporarily. Only the
original projected processes() callback temporarily raises effective UID0.
Its finally restores and verifies the Arduino credentials before control
can reach a deletion. All recipe identity/content checks and filesystem
mutations run UID/GID1000. Preserve native-process name checks,4096-PID and
4096-FD limits, exact self-exclusion and all same-user cwd/FD use checks.
No adbd exemption, unreadable-handle skip or signal/process action is added.
Root-only observation remains a read-only scan, not a lock; other-user FD
coverage retains the original explicit limitation and races remain possible.

Before mutation, retain exact complete EXPECTED board identity and boot,
unchanged helper pin, and independent content validation of all three
retained originals. Require exactly the three scratch names above, regular
UID/GID1000 single-link children and matching bytes/hashes, with directory
device34/inode1172. Preserve the sorted three-unlink sequence, authenticated
process/use scan before each unlink, board recheck, remaining-inventory/full
child-stamp comparison, directory identity comparison, fsync, and final
empty-directory-only rmdir/absence check. Rehash all retained originals and
recheck full board identity afterward. No recursive, fallback or additional
file deletion is allowed; the55-second alarm stays unchanged.

Once initial root admission succeeds, every exit attempts permanent saved/
real/effective GID and UID1000 drops independently and verifies the result,
including load, scan, privilege restoration, unlink and receipt failures.
Any terminal drop error prevents success; no cleanup operation follows it.
The user running the wrapper is not left with a saved root identity inside
the process. Wrong initial identity never permits cleanup or an elevation.

Keep raw/partial cleanup stdout, strict duplicate/nonfinite JSON refusal,
first failure, removed-name list, independent close/restoration/drop errors,
all output fields and success conditions. Only the nested and outer schema
strings become d200-exact-settle-scratch-cleanup-v1 and
d200-authenticated-settle-cleanup-v1. No receipt can be treated as successful
solely because a transport exited0 or some files became absent.

## Fresh staging and one scoped authenticated action

Proposed fixed stage:
/home/arduino/sumox26_codex_build/cleanup-app-settle-root04.
The current admission did not check its absence. Require a fresh absence
observation before exclusive creation; an existing/uncertain path is not
reused or repaired. Before result creation, stage only cleanup_root04.py,
cleanup_remoteocd03.py and the unchanged static_remote.py, each with its
checked exact bytes, ordinary single-link UID/GID1000 ownership and verified
ancestry. Independently verify actual staging and source identities.

The result owner is that fresh stage's result_root04.json. Create it
exclusively with no-clobber behavior; never overwrite a prior result or reuse
root02/root03. Runtime guards repeat their checks even after all host/source/
staging reviews pass. Any changed boot, inode, bytes, source or use evidence
fails; do not silently repin the contract to make an action proceed.

Before one actual invocation: freeze/pass independent controlled tests,
obtain separate source review, inspect fresh scratch/original/board bindings,
check/claim/stage only this owner, and review the staged inputs. The user's
current explicit continuation and prior board authentication are relevant
context for root's scoped admission; neither a historical cleanup approval
nor this contract supplies a general sudo grant. Actual authentication and
the immutable D200 invocation must be specifically admitted by the coordinator
within the user's authorization, with no credential in receipts or chat.

Retain absolute /usr/bin/python3 -I -B, this fixed wrapper path, exclusive
stdout receipt and70-second outer bound through the existing transport. Do
not add any other elevated command, general root shell or privilege change.
Do not automatically retry after a failed/partial cleanup, authentication
uncertainty or transport uncertainty. Preserve the receipt, stop mutations
and inspect before a separately reviewed next action. A missing scratch
directory after uncertainty does not prove unchanged retained originals or
successful permanent privilege drop.

## Independent oracle and evidence limits

Freeze the new oracle and inputs before its author reads the new implementation.
The historical37 core fixture methods/assertions are in
state/analysis/P7_app_motor_fault_run_raw/test_cleanup_root02.py,37221 bytes,
SHA256225ef637e85dfe4ce1598e6744c781720b900905ea0c9c3bf0737d58b49e1559.
D196's retained-core-plus-delta oracle is
tests/tooling/test_app_motor_observe_cleanup.py,14429 bytes, SHA256
18b150d239ba34aca30ce8b436036532a15e2c5aacb53ccf1166f51a68a831c0.
Preserve both files and all historical failure/adjudication evidence.

Reuse applicable assertions through a checked private fixture projection:
new source directory/basenames/stage/result/schema identities, recipe length/
hash/projected hash, directory inode1172 and current payload metadata. Retain
all37 credential/source/proc/deletion/first-error/closure assertions, including
the unchanged stat snapshot semantics. Preserve D196 delta assertion meaning
with explicit D200 metadata; identify each inherited method and transformation
in the new freeze instead of claiming old fixed metadata describes D200.

Add independent exact four-step recipe and six-step wrapper reconstruction,
private observer projection identity and unchanged nonmetadata source checks.
Old inode869, old D190 payload basename/size/hash/retained path, old wrapper
stage/schema and D19895,520-byte/e4000781 image substitutions must refuse.
Check current helper pin, three and only three unlinks plus empty rmdir as
UID/GID1000, protected same-user observation under effective UID0, restoration
before mutation, permanent UID/GID1000 on all admitted exits, first-error
preservation and fresh owner/result names. Never exercise actual sudo,
credential transitions, board operations or cleanup in automated fixtures.

Run the host platforms serially after freeze, preserve their actual counts,
explicit platform skips, first failures and all input hashes. Host/source
review does not establish current process-use clearance; the authenticated
runtime scan is still mandatory. No test assertion may be weakened to fit
an unexpected source or fixture result.

Keep compact source/provenance/review/result evidence rather than duplicate
firmware. Any later removal of staged source copies is separate evidenced
cleanup. Record any actual removal and retained-original checks separately.
This scope neither uploads/runs firmware nor changes motor-run permission,
electrical acceptance, fault diagnosis, RAM/WCET claims or human phase gates.
