# D203 actual constant-metadata compilation review

26 September 2026, Asia/Dubai. Separate same-model reviewer, reused context
after source/host and admission reviews. Only this new review file is owned
and written. Inspection used saved receipts, command/source decoding as data,
hashing, Git reads and local source/stage comparison. No subject import,
test/compiler/device invocation, target-file retrieval or cleanup occurred
in this review. Earlier reviews remain immutable.

**PASS for the single completed D203 compile-only attempt and its recorded
source, tool, artifact and closing evidence. No open material finding.**
The new image is compiled and structurally validated. Actual report/global ABI,
helper instructions, target execution, timing improvement and physical/human
acceptance remain separate and unestablished.

## Exact attempt and source closure

Saved check-only and execute invocations both exited 0 with empty stderr at
reviewed HEAD `dbeec127ba651b6a4346f70aaf5b78bc79718ce0`. The execute command
uses the prescribed absolute native_static01 pycache prefix and Python-I-B.
Its parsed stdout exactly equals the saved result. The checked profile is
app_motor_observe.ino, static FQBN, default startup and exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`.
Serial `2629958581`, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, manifest
`1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95` and source
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2` agree across
intent, check output, result and admitted scope.

The scope remains
`c08195d7be2d78e2de19f6a1fe75776fc38c1dab5a16daafa21801378d17d07d`.
Independent rehashing confirms all 129 manifest pins, all ten scope bindings
and all 196 host-freeze inputs remain exact. Current HEAD still equals the
reviewed HEAD during inspection; Git reports no changed manifest path against
that commit. D202's already reviewed motor cpp is the only firmware change
relative to D198; no further source or safety-limit repair occurred here.

The fresh `app-motor-const-static01` local/stage/remote owners were used once;
source admission reports `reused: false`. The canonical remote sketch uses the
new source digest and app_motor_observe basename. All owners are now consumed.
The coordinator's elapsed invocation time is 369.3403463 seconds. The result
spans 08:52:08.553232 to 08:58:16.837195 UTC, with status COMPILE_CHECKED and
first_error null.

Paths in the following table are under `analysis/P7_motor_const_compile_raw/`.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| native_invocations01.json | 8980 | `d8b43e9561cb8a6193a5ee262dc4bae4cf06c65aa5ed15ef92e450390c3ec60a` |
| native_static01/result.json | 1605 | `323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7` |
| native_static01/artifacts.json | 9645 | `fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd` |
| native_local_closing01.json | 1153 | `cf3e16fb6884900e5ac662482118dc8a6a9fc14157978b6063c4965816f91135` |

## Executed lifecycle and saved process evidence

All 238 sequential transport directories independently reconcile with their
durable intents: matching argv, deadlines and command lengths, return code 0
and empty transport stderr. Command lengths were recomputed from the saved
Windows argv; the maximum is 29680 UTF-16 units including NUL, below 30000.
The categories are 111 identity checks, two initialization inventories, two
builtin inventories, one command-owner creation, one source admission,
108 pushes, two full source-set checks, nine checked subprocesses and two
artifact observations. There is no additional compiler, upload/reset or MCU
operation among the recorded endpoints.

Each of the nine child result envelopes matches its transport stdout and the
literal request packet recovered from the submitted program. Every child
reports COMPLETED, exit 0, reaped true, timed_out false, no error and the
unchanged five-second reap bound. All base64 child streams decode to the exact
saved child.stdout/child.stderr bytes; child stderr is empty throughout.
The fixed minimal environment and original checked CLI framing are retained.

Exactly one expanded-properties query uses the 60-second deadline and one
compiler uses 720 seconds; both specify jobs1 and the admitted paths, FQBN
and C/C++ flags. Their child durations are approximately 1.597 and 228.509
seconds. The seven remaining child commands are the expected CLI version,
resolved data/user directories, override checks and installed-pin hashes,
including closing repeats. No package installation or retry appears.

Query and compiler JSON both report success true, empty compiler_err and empty
upload_result. Their 318 distinct properties agree except extra.time.utc and
extra.time.local. Both identify arduino:zephyr 1.0.0, the correct static build
path, observer project and inhibited flags. Normalizing only LF/CRLF in the
local text renderings exactly reproduces the checked child stdout bytes;
original bytes remain in the saved base64 envelopes and child files.

The 108 push destinations independently cover exactly the local stage map,
with no duplicate or foreign path. Every local staged hash equals the admitted
mapping; both initial and final remote source-set receipts equal that map.
The local stage contains 108 files / 781200 bytes. Independently hashing sorted
destination names, NUL separators and raw contents reproduces the exact source
digest above.

All 111 compact identity observations agree on UID1000, arduino user, boot,
CLI hash and empty process conflicts. The smallest observed home free space is
13,914,472,448 bytes, above the guard. Initial/final full initialization and
builtin inventories are identical, including their identity records. Combining
their file hashes, the two equal 18-file installed-pin outputs, CLI identity
and TLS observation independently covers all 28 installed admission inputs
with no omission or mismatch. Both override subprocesses succeed.

All eight independent final checks are PASS with null errors: local, identity,
initialization, builtins, remote_sources, installed_pins, overrides and artifacts.
The successful compiler alone is not being used as the acceptance criterion.

## Artifact and structural evidence

The initial and final artifact responses are exactly equal as parsed JSON and
match artifacts.json, including all eight file identities, installed loader/TLS
identities, first_error null and three PASS postchecks. Data-only unpacking of
both submitted compressed payloads verifies their recorded payload hashes and
the exact 6893-byte projected observer
`914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a`.
Its four UTF-8 source dependencies match frozen projected adapter `e3d23d5c...`,
base validator `d30372dd...`, extension `cd52a29a...` and helper `8ba9b190...`.
The reviewed validators were not replaced by unchecked code.

All seven artifact aliases, sizes and hashes agree between outer file records,
adapter report and inherited validator report. The build and exported package
size/hash agree; the validator checks full package equality and structure.
Debug and temporary ELF identities have equal byte sizes/hashes. The saved
statuses are STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS and
STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS. The six-symbol native TLS report exactly
equals D198, with loader `39d4a4fd...`, TLS source `68bb1476...` and no weak
undefined symbols.

This reviewer inspected saved validator results and the exact submitted
validator bytes. The target binaries were not downloaded or independently
parsed locally; actual symbol/layout/instruction queries remain future work.

| Target artifact | Bytes | SHA256 |
|---|---:|---|
| Raw ELF | 172600 | `390b69c1f35dd85a56462e562561e16b4659c0e31aa44d99aaf5b87e4ccd7e13` |
| Debug/temporary ELF | 1838360 each | `b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066` |
| Raw binary | 95352 | `76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3` |
| Build/exported package | 95368 each | `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7` |
| Packaged ELF | 172600 | `5416c121deb8ff3cb0a27a3d8d150981fe945c5ab818fe3da788744f4980db7f` |
| Link map | 449499 | `23416a129a832bbbc4738814a7a1326a62f5e5f9e879d925ab7620e3ab1b88a3` |

Compared with saved D198, .text decreases by 128 bytes and .rodata by 24 bytes;
.init_array, .data and .bss sizes are unchanged. Raw binary and flat packages
each decrease by 152 bytes, raw/packaged ELF by 240 bytes, debug/temporary ELF
by 700 bytes and map by 2501 bytes. These are observed file/section differences,
not proof that a particular division dispatch disappeared or became faster.

CLI accounting reports 95368 program bytes and 171892 global-data bytes,
leaving 90252 of its 262144-byte limit. Structural validation reports a
90256-byte RAM tail, 208 copied data bytes, 170664 zeroed BSS bytes and a
171680-byte .bss section, unchanged in size from D198. Data load addresses move
with the shorter flash image; no old target layout/address is adopted here.
Neither CLI accounting nor section arithmetic measures live free RAM, stack
usage, WCET or runtime reliability.

## Closing disposition and next evidence boundary

The local closing receipt agrees with the independently recomputed source,
stage, manifest/scope/freeze closure and section deltas. The retained native
evidence count independently matches 1004 files / 1,698,674 logical bytes.
Its local free-space observation is 16,995,299,328 bytes. Checked target
artifacts remain on the board for the next bounded file-only inspection;
no source/target copy or cleanup is introduced by this review.

The single compile-only attempt is accepted and consumed. Next observe the
new artifacts' actual report/global ABI, initialization and helper instruction
emission under a separately fixed file-only scope before any separately
reviewed inhibited runtime attempt. This success does not explain D201's
first deadline failure, establish timing benefit, flash new firmware, grant
motor-run permission, qualify hardware or pass a human phase gate.
