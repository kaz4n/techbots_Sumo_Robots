# Proposed D211 exact D207 upload-scratch cleanup

26 September 2026. UNADOPTED preparation after accepted D210 file-only entry
inspection and the fresh read-only inventory. This proposal binds the three
temporary copies from D207's upload of the D203 inhibited diagnostic image.
D206/root05 is complete and consumed; its sources, tests, failures, receipts
and retained originals remain evidence. Ordinary D208 firmware is unflashed.

Only the coordinator may adopt this scope under D051 and create the new
implementation after independent preparation review. This proposal performs
no subject import/execution, test, staging, authentication, process inspection,
deletion or device action. It creates no general privilege or motor-run grant.
Existing authorization is not expanded; source, host, staging and admission
evidence remain prerequisites to any single later invocation.

The only prospective subjects are
`state/analysis/P7_ordinary_app_cleanup_raw/cleanup_remoteocd05.py` and
`state/analysis/P7_ordinary_app_cleanup_raw/cleanup_root06.py`. Neither is written
by this proposal. The companion `cleanup_derivation01.json` records exact
literal fragments, counts, intermediate identities and saved inventory data.
Prospective bytes were computed in memory only. No private projection is
written over a source file.

## Fixed lineage and actual inventory

Paths in the following table are repository-relative. Preserve complete bytes
and LF endings before transformation. D206 operational/failure semantics are
inherited unchanged except for the literal metadata substitutions below.

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_const_cleanup_contract.md | 16120 | `25caada684cbf50964db02e3c8197fd75fdb6f0c448dd32df47067aa43c2c3ac` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_remoteocd04.py | 7738 | `edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_root05.py | 9601 | `1be147fe67bfafb60275ef1f741f05cfe2262be70c89b0eddbbfc3ec349837d4` |
| state/analysis/P7_static_link_probe_raw/static_remote.py | 33321 | `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8` |
| state/analysis/P7_ordinary_app_cleanup_raw/observe_admission01.py | 9768 | `a8e3b8b2cf19246e682288b3106bf18bb921a849681695b5e8461ffe3ed3807d` |
| state/analysis/P7_ordinary_app_cleanup_raw/admission01.json | 24552 | `ed68c4c8c31e16600950a689e362a0d83e3b839e5b46636230b703681e6d025b` |
| state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json | 9645 | `fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd` |
| tests/tooling/test_motor_const_cleanup.py | 9686 | `1f33e47b8e9e29342aee1fa19a65ad430bdfb5d7a863349b497f140deef39486` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_fixture_derivation01.json | 68656 | `1c6fc3bad5be218059ec6069ab1e5b810a06522089641b30b11208c2c3d205b7` |
| state/analysis/P7_motor_const_cleanup_raw/cleanup_independent_freeze01.json | 20685 | `9740a6e0fa34374cb7ba3b2c63bcde3fa100a10a75eeb4f038b8670b5ced943c` |

The inventory ran once at17:42:17.577058 to17:42:18.192828 Dubai, elapsed
0.6157435999484733 seconds. It returned0, empty stderr, null first_error and
local_input_closure PASS. Independent saved-data verification checked strict
duplicate-free JSON, raw stream lengths/hashes, the complete submitted program
against the pinned observer BODY, its embedded helper, both match flags,
directory/board closure, three matching original/copy pairs and five remote
closing checks. Program hash is
`59827ae85c73e342ed41f96c8b00b60741c8e846010bc0daedfe547752b1ed54`;
stdout is4496 bytes,
`cee7326d2b9bf568bb593fc5ce4ac28f01e3d151665e5d10567f529122685d40`.
Command length18656 UTF-16 units is within the unchanged30000 limit.

`expected_originals_match=true` and `exact_three_d207_copies=true` are separate
verified fields, not consequences of OBSERVED alone. The scratch directory
`/tmp/remoteocd` has device34/inode1732, mode16877, UID/GID1000, nlink2,
size100, mtime_ns=ctime_ns=1790418829759976512, with equal opening/closing
full stamps. The companion data retains the complete directory, file and
original records without rounding their nanosecond integers.

| Scratch basename | Inode | Mode | Bytes | SHA256 |
|---|---:|---:|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 1734 | 33188 | 95368 | `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7` |
| flash_sketch.cfg | 1735 | 33188 | 680 | `38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c` |
| zephyr-arduino_uno_q_stm32u585xx.elf | 1733 | 33261 | 2303728 | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

Each child has device34, UID/GID1000, nlink1 and the same mtime/ctime integer
as the observed directory. Total payload is2399776 bytes. Their retained
originals are, respectively:

- `/home/arduino/sumox26_codex_build/app-motor-const-static01/build/app_motor_observe.ino.bin-zsk.bin`
- `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg`
- `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`

The unchanged recipe binds directory device34/inode1732 and captures full
child stamps afresh at actual cleanup admission. It does not hardcode the
recorded child inodes or replace its per-unlink remaining-file checks with
older observations. Fresh staging/admission evidence must reconcile all saved
scratch/original records; any drift needs adjudication, not silent repinning.

Identity remains arduino, UID/GID1000, home `/home/arduino`, Linux
6.16.7-g0dd6551ae96b/aarch64, Python3.13.5, boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, ADB serial2629958581. No recognized
compiler candidate was found. Protected cwd/FD handles were UNINSPECTED:
this is not process-use clearance. Root06 stage/result absence is unobserved.

## Exact prospective subjects

Starting from the7738-byte D206 recipe, apply four ordered substitutions,
each with exactly one old occurrence:

1. `D201` becomes `D207` in its provenance comment.
2. Replace the complete two-line package block, including its final LF.
3. `info.st_ino == 1452` becomes `info.st_ino == 1732`.
4. `d206-exact-const-scratch-cleanup-v1` becomes
   `d211-exact-ordinary-scratch-cleanup-v1`.

Old package block:

```python
    'app_motor_observe.ino.bin-zsk.bin': (95520, 'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0',
        '/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin'),
```

New package block:

```python
    'app_motor_observe.ino.bin-zsk.bin': (95368, 'f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7',
        '/home/arduino/sumox26_codex_build/app-motor-const-static01/build/app_motor_observe.ino.bin-zsk.bin'),
```

Required `cleanup_remoteocd05.py`: **7740 bytes**, SHA256
`1a59d4b2fc12a0b74a81f65847d7384002423882bd42f5242a98774c8bc02958`.

Preserve the one-occurrence private missing-link projection exactly:

```python
PROJECTION_OLD = b'                except FileNotFoundError:\n                    continue\n'
PROJECTION_NEW = b'                except FileNotFoundError:\n                    raise\n'
```

Required private projected recipe: **7737 bytes**, SHA256
`e90a5189a76d05bd7674d1bb771b9f480d59b5b26cc4a390109c47431a69d731`.
A missing cwd/FD link reaches the unchanged outer PID-existence recheck;
only a departed PID may be ignored. Missing metadata for a surviving PID and
permission failures refuse. The projected bytes exist only in memory.

Starting from the9601-byte D206 wrapper, apply six ordered substitutions:

| Old literal | New literal | Count |
|---|---|---:|
| cleanup-app-const-root05 | cleanup-ordinary-app-root06 | 1 |
| cleanup_remoteocd04.py | cleanup_remoteocd05.py | 4 |
| 7738 | 7740 | 1 |
| edd1c8aa44f8de82cbfe1d7333b6ce836396922f82eacbe89d87fa6bcf3eb598 | 1a59d4b2fc12a0b74a81f65847d7384002423882bd42f5242a98774c8bc02958 | 1 |
| 565acb3988bb0eba0c6865ac27daf5bbc277c85a67204f036bf098b3261b00be | e90a5189a76d05bd7674d1bb771b9f480d59b5b26cc4a390109c47431a69d731 | 1 |
| d206-authenticated-const-cleanup-v1 | d211-authenticated-ordinary-cleanup-v1 | 1 |

Required `cleanup_root06.py`: **9607 bytes**, SHA256
`290a7236dc7cc5c6b679a72d5864fb99408dd21bbd30b7b8f3edf74c0fe10aa3`.
The only other staged source is the unchanged33321-byte static_remote.py.
Expected staged source total: **50668 bytes**. All9 recipe and14 wrapper
functions retain names/signatures. All operational bytes remain unchanged
after these counted metadata replacements. No contract/derivation/observer
runtime dependency or new predicate is added.

## Preserved guards and credential ordering

Retain descriptor-relative traversal, O_NOFOLLOW/O_NONBLOCK, plain ancestry,
single-link ordinary source checks, exact source lengths/hashes, full
before/open/after stamps, all-descriptor close attempts and first-error
preservation. No arbitrary source, alternate retained path or hash fallback.

Initial wrapper admission requires all-zero UID and GID triples, no arguments
and isolated Python-I-B. After pinned source loading, `enter_user` sets groups
[1000], real/effective GID/UID1000 and saved GID/UID0. Each of three protected
read-only process observations raises effective UID0, runs the existing scan,
then restores and verifies Arduino real/effective IDs before that unlink.
Saved root remains between scans. Permanent real/effective/saved GID and UID
triples1000 are independently attempted and verified in `execute` finally,
after cleanup or any admitted failure. Moving the permanent drop before
unlink would change the reviewed recipe and is outside this scope.

Keep exact self-exclusion,4096 PID/4096 same-user FD bounds, native process-name
refusals and same-UID cwd/FD checks. No unreadable-handle skip, adbd exemption,
process signal or process mutation is introduced. Root scans are observations,
not locks. Other-user FD coverage and observation races remain limited.

Before mutation, recheck expected identity/boot, helper pin, three retained
originals, directory device34/inode1732, exact scratch names, content, regular
single-link UID/GID1000 children. Each sorted unlink follows a protected scan,
verified restoration, board recheck, remaining inventory/full-stamp comparison
and directory identity comparison, then fsync. Only the empty directory may
be removed, with parent fsync and absence verification. Originals and board
identity are checked again afterward. Preserve the55-second alarm. There is
no recursive delete, additional deletion or alternative scope.

Retain partial stdout, removed names, duplicate/nonfinite JSON refusal, first
errors and all close/restoration/drop fields. `run_original` still checks a
parsed object, return0 and REMOVED_EXACT_STALE_COPIES; it does not independently
reject a successful object solely on its nested schema. Actual acceptance
separately requires both exact D211 schemas, full expected fields, equal
parsed cleanup_stdout/cleanup_result, source pins and projection, three use
checks/restorations, correct initial/final credentials, empty error fields,
exact removed set, directory removal and retained-original/identity closure.
Transport0 or scratch absence alone cannot establish success.

## Fresh staging, admission and result

The sole proposed stage is
`/home/arduino/sumox26_codex_build/cleanup-ordinary-app-root06` and the sole
result is its `result_root06.json`. Require a new no-follow absence observation
and exclusive stage creation. Stage exactly cleanup_root06.py,
cleanup_remoteocd05.py and static_remote.py, with fixed bytes and ordinary
single-link UID/GID1000 files. Record its actual new identity; no stage inode
is invented here. Existing/uncertain owners are neither reused nor repaired.
Create the result exclusively with no-clobber behavior; never overwrite a
prior result. Root02/root03/root04/root05 and their results remain consumed.

Use D206's accepted stage-verification lineage: its explicit staged-source
read/hash loop has its own pin table and full opening/closing identities;
`recipe.inventory` is limited to scratch names. The intent
`state/analysis/P7_motor_const_cleanup_raw/cleanup_stage_verification_intent01.json`
is34505 bytes,
`8776a33d82394e595bb57889166dadd1e4caef00674b57e971de7dc119afa731`;
the accepted saved verification is9876 bytes,
`7de3bb3a0d7a81feac727e1c7dc3a6d67e8d9519a7070c6c0a2eb051f3fc35f9`.
Its ancestry includes corrected D200 verification02; preserve the failed
verification01 that incorrectly used scratch-only pins for stage sources.
Any extraction from saved argv uses shell parsing as data, never execution.
This proposal creates no staging, authentication or retrieval program.

Independent source/host reviews precede staging; independent stage/admission
review precedes one authenticated invocation. Verify exactly three staged
sources, absent result, fresh scratch/original records and all closing checks.
Use absolute `/usr/bin/python3 -I -B`, the fixed root06 wrapper, exclusive result
and unchanged70-second transport bound. Credentials travel only through
protected stdin, never argv, files, saved intents, logs or reports. No extra
elevated command or general root shell follows.

Preserve the first error and stop on partial failure or authentication/transport
uncertainty. No automatic retry or silent repinning. A separate read-only
retrieval/review must reconcile the raw result, strict nested acceptance,
scratch absence, every retained original and every staged source on reopen.
Result creation may change stage timestamps/size while device/inode/mode/
owner/nlink and full source stamps/hashes remain unchanged. The result must
be a fresh regular single-link UID/GID1000 file with stable path/descriptor
identity. Missing scratch cannot substitute for credential or original closure.

## Independent oracle requirements

The intended new oracle is `tests/tooling/test_ordinary_app_cleanup.py`.
Freeze it, its data-only fixture derivation and all inputs before its author
reads, hashes, imports or executes either new subject. Historical artifacts
remain immutable. Retain all **52 D206 methods**:37 credential/descriptor
methods with147 assertion calls including four helper assertions;10 metadata
methods with34 calls;2 focused methods with9 calls;3 D206 supplements with
12/21/7 calls. Record exact private fixture projections and preserve all
nonmetadata assertion/control-flow meanings. Any extra methods have separately
frozen names/counts; inherited52 is the minimum, not permission to remove cases.

The former negative D203-unuploaded95368/f15c7ce1 image is now the valid D207
uploaded image. The new positive binds that exact image and original path.
Preserve stale-image refusal using explicit noncurrent alternatives:

| Alternative | Bytes | SHA256 |
|---|---:|---|
| D190 | 95328 | `deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c` |
| D195 | 95360 | `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` |
| D198 image uploaded by D201 | 95520 | `e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0` |
| Unflashed ordinary D208 | 92944 | `7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad` |

The ordinary artifact packet is9281 bytes,
`275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0`.
Never mechanically turn a refusal into a current-image negative. Keep earlier
wrong basenames and inode33/869/1172 cases; add stale directory inode1452.
Refuse old root05 stage/result/source/schema identities. For retained-path
fallback refusals, preserve fault/observe alternatives and substitute the now
stale settle owner for the now valid app-motor-const-static01 owner; separately
refuse ordinary-app-static01. An unavailable current original must fail even
if another retained image exists. Use context-counted replacements to avoid
introduced-literal collisions and prove no assertion weakening.

Cover exact four-step recipe/six-step wrapper reconstruction, every intermediate
identity, unchanged remaining bytes, private projection, current inventory,
fresh root06 ownership, three-only unlink/rmdir behavior, protected read-only
scans, restoration before mutation, permanent drop on all admitted exits,
descriptor closure and first-failure paths. Source-schema drift refusal and
coordinator actual-result schema validation are separate requirements; do not
invent a runtime nested-schema predicate in the unchanged wrapper.

All host tests use controlled fakes and prohibit real credentials, sudo,
process handles, device calls and cleanup. After independent freeze and source
readiness, run Linux/Windows serially. The inherited component predicts52 Linux
passes and15 Windows passes with37 explicit Linux-only skips; supplement counts
must be frozen independently. Preserve initial failures, raw streams, closures
and skip reasons. Host success does not replace fresh protected native scans.

Keep compact evidence; any later removal of staged sources is separate. Never
touch historical policy-denied paths. Claim storage recovery only after actual
reviewed receipts, not this2399776-byte inventory. No compile, upload, reset,
MCU read, firmware change, SETTLE remedy, RAM/WCET qualification, motor-run
permission, physical acceptance or human phase gate is established here.
