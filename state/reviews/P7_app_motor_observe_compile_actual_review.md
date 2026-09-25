# D193 actual static observation compile review

26 September 2026, Asia/Dubai. **PASS: TARGET-COMPILED / RECEIPTS REVIEWED**, no
material finding within this compile-only scope. This is not an upload, runtime,
ABI/entry, physical acceptance or phase-gate verdict.

Reviewer `/root/fresh_review`: separate same-model reused context. The reviewer
independently read the completed intent, invocation, all 236 transport records,
all nine checked-child packets/streams, query and compile metadata, source and
installed-pin observations, initial/final prerequisite inventories, artifact
packets, final result and current bound inputs. Only local data inspection was
performed; no subject import/execution, test, compiler or device call. This review
document is the only file written by the reviewer in this scope.

## Binding and execution

The [actual invocation](../analysis/P7_app_motor_observe_compile_raw/native_static01_invocation.json)
binds check-only exit0 and execute exit0, both with empty stderr, to reviewed HEAD
`b5f589c58cf08b312a743a911505386ab04f0df2`. Execute used Python -B and its isolated
selected owner pycache prefix; that pycache remains absent. Its decoded stdout
equals the saved [final result](../analysis/P7_app_motor_observe_compile_raw/native_static01/result.json).
The attempt ran from `2026-09-25T21:21:40.893975+00:00` through
`2026-09-25T21:27:31.341220+00:00`; outer invocation elapsed 351.373 s.

The manifest remains SHA-256
`aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e`.
All 128 current working-byte pins match, including the original immutable
dependencies and launcher 70e1f016 / contract 0301726f. All are consistent with the
reviewed commit, retaining the previously adjudicated CRLF representation of
`tools/app_build_pins.json`; this is not a new input change. The exact source
digest is `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0`.
The reviewer reproduced that digest from the actual 107 staged files, whose
hashes equal the manifest-derived mapping, staged_files.json and both remote
source-set observations. Only those 107 destinations were pushed, once each.
Canonical source admission recorded reused=false.

Intent, invocation, query, compiler and artifact packets consistently identify:

- `app_motor_observe.ino`, `arduino:zephyr:unoq:link_mode=static`, default startup;
- exact flags `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`;
- remote owner `/home/arduino/sumox26_codex_build/app-motor-observe-static01`;
- new digest-bound source child `/app_motor_observe`;
- board 2629958581 and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

All 236 numbered transports are present, contiguous, exit0 and have empty
stderr. Each intent matches its result command/deadline fields. Independently
recomputed Windows command lengths match their records and remain at or below
29,682 UTF-16 units including NUL, under the 30,000-unit limit. Their labels are
110 identity checks, 107 source pushes, two source sets, nine checked commands,
two initialization inventories, two builtin inventories, one command-owner
claim, one source admission and two artifact observations.

The nine checked children all report COMPLETED, exit0, no timeout and reaped=true.
Recorded base64 streams match their byte counts and saved child streams; child
stderr is empty. Exactly one properties query and one compiler invocation occur.
The actual argv uses `/usr/bin/arduino-cli --config-file /dev/null`, jobs1,
the two exact C/C++ flags, discovery-phase override and the scoped paths.
The query deadline is 60 s, compile deadline 720 s, and both retain 5 s reap.
Actual child elapsed times are 1.594 s and 229.164 s respectively. No upload
argument occurs.

## Metadata, dependencies and closing checks

Both actual CLI JSON responses report success=true, empty compiler_err and an
empty upload_result. Each has 318 unique properties. The reviewer independently
expanded the pinned 84-property static reference with the declared project,
flags, build and data paths; all 84 controlled properties match in both replies.
The 17 fixed metadata fields, matching board/build platform arduino:zephyr 1.0.0,
static link, wait/default boot and absent external libraries also match. The
only query/compile property differences are extra.time.local and extra.time.utc,
reflecting their separate invocation times; controlled properties do not differ.

All 18 installed platform/compiler hashes match current pinned expectations both
before and after compilation. The initialization and builtin inventories are
identical at opening and closure and equal their retained baselines after the
declared boot binding. Full prerequisite identity records UID/GID 1000, arduino,
home `/home/arduino`, Linux aarch64 and Python 3.13.5. All 110 identity observations
retain UID 1000, the same boot/CLI hash, no conflicts and target free space above
1 GiB. Override checks complete with empty streams.

The result records exactly eight independent PASS closing checks, each with no
error: local, identity, initialization, builtins, remote_sources, installed_pins,
overrides and artifacts. first_error remains null. Subsequent untracked ABI
preparation files are outside this completed manifest/attempt and are not
treated as inputs to the completed compiler invocation.

## Artifact evidence

The [artifact packet](../analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json)
is exactly equal to both initial and final artifact observations, including
file identities and hashes. All eight files are recorded regular. Seven build
aliases, artifact hashes and sizes agree across the packet and unchanged native
validator report. The exported flat package equals its build copy in hash/size.
Loader/TLS hashes match their fixed expectations; loader, tls_source and files
postchecks all PASS. The recorded layout status is
STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS, with underlying
STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS and no weak undefined symbols.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Raw ELF | 172648 | `2fd70da8edc66daa9c54162c028857692d07a1e8c7f960db8384ec7886f30e24` |
| Debug ELF and temp ELF, each | 1837380 | `33e3b34dc11ee5be56b8b94bca168eb0bdff5de3e4721fcf7ac9e8c015047324` |
| Flat package, build and export | 95360 | `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` |

CLI reports 95,360 program bytes and 170,868 global-data bytes, with 91,276 nominal
bytes remaining. The structural validator separately reports a 91,280-byte RAM
tail, 208-byte data copy and 170,632-byte BSS zero span. These are distinct recorded
compile/layout quantities, neither a measurement of free live RAM nor proof of
stack/heap margin, loader success or WCET.

## Receipt identities and limits

All paths below are under `state/analysis/P7_app_motor_observe_compile_raw/`.

| Receipt | SHA-256 |
|---|---|
| `native_static01/result.json` | `24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b` |
| `native_static01/artifacts.json` | `5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b` |
| `native_static01/intent.json` | `bcc2a4e6d4319bccd4c3f4d8ded8698bc27fadd48ee59e73dd9685fdaeb55291` |
| `native_static01_invocation.json` | `c4fffb22b8f9322b435f6fc7eabe7ea8330542d6046a83556ef3f05266320463` |
| `native_static01/staged_files.json` | `884c36887875a9710cff503246dceda1a6de9d7ca0aa5546dd98dac21c70d8b6` |

The [source/host review](P7_app_motor_observe_compile_review.md) closes the prior
host conditions; final caller receipts show Linux 59 PASS and Windows 59 with
56 PASS / 3 platform skips, unchanged pins. The original Windows fixture failure,
source repair and coordinator Git-byte precheck remain preserved. They are not
failures of this actual compiler attempt. The [prepared scope review](P7_app_motor_observe_compile_scope_review.md)
remains a separate dated preparation record.

This is an independent audit of recorded native compile and validation evidence.
The reviewer did not download/reparse the board-resident ELF or rerun validators.
The local/remote compile owners are consumed and must not be retried. No firmware
was flashed, no MCU memory read/reset occurred, and this compile does not resolve
the original intermittent native fault. New file-only ABI and entry observation
must derive layout and addresses from these exact new artifacts before any
separately reviewed inert run. Physical acceptance and human gates remain open.
