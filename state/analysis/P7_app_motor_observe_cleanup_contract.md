# D196 exact last-upload scratch cleanup

26 September 2026. Prepare a new, narrowly authenticated cleanup of the three
D190 upload copies now in `/tmp/remoteocd`. D191's earlier cleanup succeeded
for D184 copies and is consumed; never rerun it. Preserve every historical
source, test, contract, failure, receipt and owner. This contract records the
new software scope and expected bytes; it does not claim staging or execution.

Add only these two implementation files beneath
`state/analysis/P7_app_motor_observe_run_raw/`:
`cleanup_remoteocd02.py` and `cleanup_root03.py`. Derive them by the exact
count-checked substitutions below, without changing any operational guard.
No generic cleanup framework, arbitrary path, CLI argument, process exemption,
credential policy or new dependency is admitted.

## Fixed provenance

All paths below are relative to the repository. Check these original bytes
before transformation. Preserve their exact LF source bytes; do not normalize
newlines, rewrite historical files or execute cleanup during preparation.

| Fixed input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_fault_run_raw/cleanup_remoteocd01.py | 7873 | 23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95 |
| state/analysis/P7_app_motor_fault_run_raw/cleanup_root02.py | 9592 | 4192f23ea49705a0af691953e6aec3c1f9da66c7cc1897ca3f5d49fba9fc5388 |
| state/analysis/P7_static_link_probe_raw/static_remote.py | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |
| state/analysis/P7_app_motor_observe_abi_raw/upload_scratch_inventory01.json | 3216 | 20db3c251a907d6b143afc11a05c44780ba3a09d85e3202ad05878225f4a06f2 |
| state/analysis/P7_app_motor_fault_compile_raw/native_static01/artifacts.json | 9597 | 57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce |

The artifact receipt binds the retained D190 package at both the build and
export paths. Use the build original below; do not redirect to the new D193
observer image. The inventory is read-only evidence, not process-use evidence
or a deletion receipt. It reports the unchanged boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, UID1000, directory device34/inode869,
and these exact copies:

| Scratch basename | Bytes | SHA256 | Retained original |
|---|---:|---|---|
| app_motor_fault.ino.bin-zsk.bin | 95328 | deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c | /home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino.bin-zsk.bin |
| flash_sketch.cfg | 680 | 38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd | /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf |

Total scratch payload is2399736 bytes. Configuration and loader pins/retained
paths are unchanged. Initial runtime inventory still establishes full child
stat stamps; every remaining child must match those stamps before each unlink.
The observed inode869 replaces only the obsolete directory inode33 assertion.
Fresh runtime identity, content and use checks remain mandatory.

## Exact recipe derivation

Starting from the fixed7873-byte cleanup_remoteocd01.py, apply these four
ordered substitutions, requiring each old fragment to occur exactly once:

1. Replace `D184` with `D190` in the provenance comment.
2. Replace the complete four-line payload pin block below with the following
   two-line block. Both blocks include the final LF after the comma.
3. Replace `info.st_ino == 33` with `info.st_ino == 869`.
4. Replace `d190-exact-scratch-cleanup-v1` with
   `d196-exact-observer-scratch-cleanup-v1`.

Old payload block:

```python
    'motor_fault.ino.elf-zsk.bin': (29836, 'b4416792a5bc228f34712fad9199a07c3c480aace979faa88aa12b50288b0a79',
        '/home/arduino/sumox26_codex_build/motor-fault-active01/_app_builds/native-app-v1/'
        '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36/bench-default/'
        '3aafdd0129f64799b4db51efe78e5c44/build/motor_fault.ino.elf-zsk.bin'),
```

New payload block:

```python
    'app_motor_fault.ino.bin-zsk.bin': (95328, 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c',
        '/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino.bin-zsk.bin'),
```

Required new recipe identity:7735 bytes, SHA256
`1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a`.

Keep the reviewed wrapper's one private observer projection unchanged:
replace exactly one
`                except FileNotFoundError:\n                    continue\n`
with
`                except FileNotFoundError:\n                    raise\n`.
The resulting in-memory recipe must be7732 bytes, SHA256
`b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1`.
Do not write this projected recipe over either source. Missing cwd/FD now
reaches the inherited outer PID-existence recheck: only a departed PID may be
ignored; missing metadata for a surviving PID remains a failure.

## Exact wrapper derivation

Starting from the fixed9592-byte cleanup_root02.py, apply only these ordered,
count-checked substitutions. The first row changes a comment, not admission.

| Old bytes | New bytes | Count |
|---|---|---:|
| # Runs the pinned exact cleanup only after a human starts this wrapper with sudo. | # Runs the pinned exact cleanup only through task-authorized sudo authentication. | 1 |
| cleanup-app-inert-root02 | cleanup-app-observe-root03 | 1 |
| cleanup_remoteocd01.py | cleanup_remoteocd02.py | 4 |
| 7873 | 7735 | 1 |
| 23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95 | 1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a | 1 |
| 51286ad414794e82f3161bed16cbb47dca421e831316e053a7eab967469f602e | b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1 | 1 |
| d190-human-root-cleanup-v2 | d196-authenticated-observer-cleanup-v1 | 1 |

Required cleanup_root03.py identity:9606 bytes, SHA256
`a089cc3bac9d8df3ffe53947e22b1bb4ffa139a733c7ebb1f5ba62e6d5bd804f`.
The unchanged helper remains33321 bytes/SHA8ba9b190... and the only other
dependency. Every source byte not covered by these replacements stays exact.

The public callable interface is unchanged: require, credentials, error_record,
stamp, read_source, load_cleanup, enter_user, observe, drop_privilege,
unique_object, invalid_constant, run_original, execute and main retain their
existing signatures and behavior. Only the fixed source/stage/schema metadata
above changes. The original cleanup callable interface likewise remains exact.

## Preserved safety and evidence behavior

The wrapper initially requires real/effective/saved UID and GID all0, no extra
arguments, isolated Python-I-B, exact source pins and checked source ancestry.
Directory-FD traversal, O_NOFOLLOW/O_NONBLOCK, ordinary singly linked sources,
UID/GID1000 file ownership, exact sizes/hashes/stamps and all-descriptor closure
remain unchanged; a secondary close failure never replaces a primary error.

It sets supplementary groups exactly[1000], then real/effective UID/GID1000
while retaining saved0 temporarily. Only the projected processes() observation
temporarily raises effective UID0, and its finally restores/verifies UID1000.
All original identity/content checks and filesystem mutations run UID/GID1000.
Native process names,4096-PID/4096-FD limits, same-user cwd/FD use checks and
self-exclusion remain exact. No adbd exemption or unreadable-FD skip is added.
Elevated access denial still fails. Other-user FD coverage remains the original
explicit limitation; root observation is not a lock or a proof against races.

Before deletion, retain the exact complete board EXPECTED identity, boot and
helper pin; independently hash all three retained originals. Require precisely
the three scratch basenames, regular UID/GID1000 singly linked files, matching
bytes/hashes and directory device34/inode869. Preserve sorted three-unlink
order, process/use/identity/inventory checks before each unlink, full directory
identity comparisons, fsync, empty-directory-only rmdir and absence check.
Rehash all originals and recheck board identity at closure. No recursive or
fallback deletion is permitted. The recipe keeps its55-second alarm.

The wrapper preserves raw and partial cleanup stdout, strict JSON parsing,
the first error, removed list and independent privilege-drop errors. After
initial-root admission it always attempts both permanent real/effective/saved
GID/UID1000 drops and verifies them, including source/entry/scan/cleanup failure.
Any terminal drop error prevents success; no cleanup operation follows it.
The top-level schema becomes d196-authenticated-observer-cleanup-v1 and the
nested recipe schema d196-exact-observer-scratch-cleanup-v1. All other receipt
fields, status conditions and first-failure handling remain unchanged.

## Fresh staging and narrowly authenticated execution

Fixed new stage:
`/home/arduino/sumox26_codex_build/cleanup-app-observe-root03`.
It must be created exclusively and contain only cleanup_root03.py,
cleanup_remoteocd02.py and the unchanged static_remote.py, with exact pins and
UID/GID1000 single-link ownership. Preserve every old stage and result.
The separate fresh result owner is this stage's `result_root03.json`; create
it exclusively, never overwrite it. Staging/review are not deletion evidence.

Before one execution: freeze and pass independent controlled tests, complete
separate source review, inspect the current board/scratch/retained originals,
stage the three checked files, and independently verify actual staging plus
unchanged identity/source bindings. Runtime guards must still repeat their
checks. Missing/changed evidence fails; never silently retarget or repin.

The user's explicit continuation and previously supplied board authentication
are relevant authorization context for the current requested work. D191's prior
one-invocation approval is not a general sudo grant, and this contract does not
claim authentication or execution has occurred. Any actual invocation must be
specifically admitted for this immutable D196 scope and authenticate through
the existing bounded transport, never record a credential. Retain absolute
`/usr/bin/python3 -I -B`, the fixed new wrapper path, exclusive stdout receipt
and70-second outer bound. No other elevated command or mutation is authorized
by this cleanup scope. Do not retry automatically after failure, partial
deletion, authentication uncertainty or transport uncertainty; retain receipts
and inspect before deciding the next separately reviewed action.

## Independent validation and storage

Freeze a new oracle before its author reads the new source bodies. The reviewed
historical oracle is
`state/analysis/P7_app_motor_fault_run_raw/test_cleanup_root02.py`,37221 bytes,
SHA256225ef637e85dfe4ce1598e6744c781720b900905ea0c9c3bf0737d58b49e1559.
Reuse all37 original fixture methods/assertions through a private, checked
metadata projection only: new source directory/basenames/stage, recipe
length/hash/projected hash, receipt schemas and fixture directory inode869.
Preserve the original file and all first failures; do not weaken an assertion
to accommodate the new target. The original stat fixtures' snapshot semantics
and credential/proc mocks remain unchanged.

Supplement those retained assertions with exact independent reconstruction of
both new source bytes and the private observer projection; old directory inode,
old scratch basename, old payload length/hash/retained path must fail under the
new recipe. Check unchanged helper and all nonmetadata source bodies, fresh
stage/result names, exact three mutations as UID1000, root-only read scans and
permanent credential drop. No actual credentials, sudo, board call or cleanup
may occur in automated tests. Host fixtures establish software behavior only.

Record actual outcomes and preservation of retained originals separately.
Keep compact contracts, hashes, reviews and receipts; do not duplicate firmware
artifacts. Any release of staged source copies is a separate evidenced cleanup.
This work neither uploads/runs firmware nor changes configuration, motor-run
permission, physical acceptance, RAM/WCET claims or human phase gates.
