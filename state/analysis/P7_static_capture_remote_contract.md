# D153 draft: fixed board-side startup capture

Host implementation/testing only until a separately reviewed source-bound native
run is recorded. Do not upload, reset, halt, compile or read the MCU in this task.
Implement only `P7_static_startup_raw/capture_remote.py`; root supplies immutable
`capture_bindings.json`. Preserve D152 code/tests and every production file.

## Trusted dependencies and interface

`collect(helper, decoder, loader_image, *, fs_root=Path('/'), executor=None,
clock=None, sleeper=None) -> dict` is the sole orchestration entry. It has no
module-import side effects or auto-running main. Actual calls use the frozen
static_remote helper, D152 decoder and pinned p0.loader_image function; the
coordinator captures/hashes those sources before loading them. The optional
filesystem root, process executor, monotonic clock and sleeper are controlled
host-test seams, never native command-line overrides. Import standard library only.

Bindings are supplied as module-global `BINDINGS` by the hash-bound launcher
before calling collect; no environment/file discovery of alternative bindings.
Tests may set synthetic bindings only inside their isolated module context.
The real bindings file defines exact run/source/boot/uid, output path, five
file pins, loader-image hash/size and sketch size. Verify that BINDINGS has exactly
those declared keys and types; bytes/uid are actual ints, hashes64lowercasehex.
The host must additionally verify current source/D144 packet and a known clean
new upload result before granting this separate capture. This collector alone
does not establish upload authority or source provenance.

Frozen helper operations `directory`, `logical_read`, `identity`, `directory_id`,
`read_file` retain descriptor-based no-symlink/path/ownership checks. Their logic
is already tested; reuse it rather than duplicate a filesystem framework.

Bindings schema: exactly `schema,run_id,source_sha256,boot_id,uid,output,files,
loader_image`. Schema is `fixed-static-capture-v1`, run_id is
`static-fcddbd8e-run01`; source is the fixed currentfcddbd8e full digest and
boot a lowercase UUID. `files` has exactly `openocd,config,swj,loader,sketch`,
each exactly `path,bytes,sha256`; paths are normalized absolute POSIX with only
letters/digits/underscore/dot/hyphen/slash and no empty/dot/dotdot component.
`loader_image` has exactly `bytes,sha256`; size263680 and fixedhashe9322826.
File sizes are positive and at most64MiB; sketch size93096. All strings require
exact str types. Full exact production values are in capture_bindings.json;
the launcher's reviewed hash is their authority, never caller/ambient discovery.
Tests may substitute per-file hashes/bytes to avoid copied tool binaries.
They may also substitute loader_image.sha256 for synthetic reference bytes while
retaining263680/93096 extents; only the hash-bound real bindings authorize native
references. `loader_image(raw_elf_bytes) -> bytes` has the frozen p0 interface.
Validate its result's exact bytes type, length and bindings hash.

## Admission and durable ownership

1. Reject wrong bindings shape, unsafe output name/path, or non-Python-B execution
   before filesystem mutation. The output must be the bindings' fixed direct
   child of `/home/arduino/sumox26_codex_build`, named
   `static-startup-fcddbd8e-run01-capture`. No alternative native output path.
2. Open fs_root directory; use helper.identity and require exact bindings boot
   and UID1000, userarduino, home/home/arduino, Linux/aarch64. Check all five
   regular-file contents by helper.logical_read against exact hash and byte
   length from bindings; no tool executes during these checks. Derive the loader
   reference from pinned ELF with loader_image and require263680B/SHAe9322826.
   Require the flat sketch93096B/SHA5f08afe0. File bounds are the exact pin sizes.
3. Require no process with comm exactly `openocd`, `remoteocd` or `arduino-cli`
   before the first memory command. Inspect at most4096 numeric /proc entries;
   process disappearance is allowed only if its entry is absent, other read
   failure aborts. This is a sampled conflict check, not a kernel-wide lock.
4. Through the checked parent descriptor, mkdir the exact output once0700,
   refusing any preexisting entry. Open/check it through helper.child_directory.
   Retain its device/inode; every later operation must observe the same identity.
   Create/fsync `capture_attempt.json` exclusively, then fsync its directory.
   Record run/source/boot, the full bindings, exact plan and UTC time. No reuse,
   deletion, overwrite, recovery reset or retry after this point.
   All own record/stdout/stderr creation uses O_EXCL|O_NOFOLLOW and the retained
   directory descriptor. Once mkdir succeeds the directory is consumed even if
   claim creation/fsync fails; attempt independent finalization in that case too.
   No finalization enters or modifies a preexisting output directory.

## Exact finite collection

Use decoder.read_plan verbatim:18 reads/713656 bytes from the D152 contract.
No arbitrary addresses, whole-object reads, heap walk or metadata executables.
The clock starts on entry; finite600s collection launch/wait budget, each process timeout is the smaller
of30s and remaining budget. Check the budget around every bounded operation.
After first.transaction and before second.runtime, record exactly one requested
2s sleep and actual monotonic before/after times; require at least2s elapsed and
positive remaining budget afterward. No wall-clock assumptions or busy waiting.

For read index00..17, exclusively fsync a planned `NN.command.json` before launch.
The only executable argv is:

`[OPENOCD, '-f', CONFIG, '-c', 'dump_image {OUTPUT/NN-NAME.bin} 0xADDRESS SIZE', '-c', 'shutdown']`

OPENOCD/config are the pinned absolute bindings paths; NAME/address/size are
the next immutable plan item. cwd is /home/arduino. Output path is first absent.
Use a fixed minimal subprocess environment HOME/USER/LOGNAME/PATH/LANG, with
HOME=/home/arduino, USER=LOGNAME=arduino, PATH=/usr/bin:/bin, LANG=C.UTF-8.
No shell, MCU write/reset/halt command or connection server is added.
Check retained parent/output identity immediately before each process launch and
after accepting its raw output. OpenOCD itself accepts a pathname; these checks
detect drift but do not establish a kernel-wide exclusive filesystem lock.

`execute(argv, stdout_path, stderr_path, timeout)` is the injected seam. The real
default creates exclusive stdout/stderr files, uses Popen(start_new_session=True,
stdin=DEVNULL,cwd/environment above), and Linux RLIMIT_FSIZE1MiB per output in the
child. On timeout terminate the entire owned process group with SIGKILL and reap
the child with a bounded5s wait. Preserve timeout/unknown completion instead of
claiming the child or MCU is quiescent. Do not kill unrelated processes.
Return exact keys returncode, timed_out, reaped; exact int-or-None and bool types.
Known success requires returncode0, timed_outFalse, reapedTrue, both regular
output files strictly smaller than1MiB. Unexpected spawn/kill/reap errors are
failures and preserve the first error. Never retry the command.
Output files are `NN.stdout` and `NN.stderr`, next to each command/result record.

Read raw output only through the owned directory descriptor. Require exact
length, regular/no-symlink file, compute SHA256, preserve raw bytes on disk.
Write a separate exclusive/fsynced `NN.result.json`, recording actual subprocess
result or exception, start/end UTC/monotonic, stdout/stderr text and raw size/hash
when available. Nonempty OpenOCD stderr may be normal diagnostics; returncode,
timeout, file integrity and image identity govern acceptance, not silence.

After the first seven complete reads compare both full flash images against the
references BEFORE any RAM read; mismatch aborts without manufacturing a D152
complete-capture result. Continue to all18 only after that comparison passes.
Never decode RAM on an incomplete capture. After18, call decoder.analyze_capture
once with the exact triples and reference bytes. A resulting fault/no-progress/
flash-mismatch status is retained honestly; collection completion is separate
from successful startup.
Require the returned object to have exactly the six D152 keys: flash, observation,
runtime, transaction, epoch_delta, errors. Flash has exactly the four named bools;
observation is one of the five D152 status strings; epoch_delta is None or an
actual uint32 int; errors a list of strings; runtime/transaction each list of
two dicts, or empty only for FLASH_MISMATCH. A malformed return fails with
analysisNone. The hash-bound already-tested D152 decoder owns field semantics;
do not write a second decoder or claim this shallow check independently proves it.

## Finalization and tests

Always attempt independent five-file and identity/directory postchecks after an
attempt was created, even on failure; append errors without replacing the first.
No postcheck executes tools or reads the MCU. Preserve all partial outputs.
Exclusive/fsynced `capture_result.json` contains status COLLECTED only after all18
commands/reads, valid decoder return and clean postchecks; otherwise FAILED.
Include run/source, counts, timings, all read hashes, the first error (type/message),
postcheck errors and analysis (None until complete). Return the same report; a
failure to persist the result raises instead of returning a success. Unexpected
exceptions before the claim may raise with no operation; an existing output
directory is never entered/modified. The launcher records transport uncertainty.

Report keys are exactly `schema,run_id,source_sha256,status,counts,started_utc,
finished_utc,started_monotonic,finished_monotonic,wait,reads,first_error,
postcheck_errors,analysis`. Schema is `static-capture-result-v1`. Counts keys are
`commands,reads,requested_bytes`; commands/requested_bytes increment immediately
before executor launch after planned receipt persistence, reads only after exact
raw acceptance. `reads` items have `name,address,bytes,sha256,file`. `wait` starts
None, then records `requested_seconds,before,after` (after may be None on error).
First error is None or `{type,message}`; postcheck errors are `{check,type,message}`.
Never return COLLECTED with fewer than18 reads/commands or changed references.
Independent postchecks must run all five file checks, identity and directory
identity even when an earlier one fails. Their finite file checks are attempted
after the collection deadline and cannot launch further MCU commands. A timeout
may add at most5s of child-reaping effort; unknown/unreaped child status does not
prove that all MCU activity has ended or that the target is quiescent.

Independent spec-derived tests freeze before implementation execution. Test exact
argv/order/extent, identity/pin/parent drift, existing output, durable claim before
first call, command exception/nonzero/timeout/unreaped/malformed results, absent/
short/oversized/symlink reads, mismatch suppressing RAM, exact wait/deadline,
fault/no-progress collection, independent finalization errors and no second attempt.
Use in-memory process substitutes and a small isolated temporary filesystem;
release owned test scratch afterward. Exercise the real process wrapper with
controlled Popen/group substitutes, never an actual OpenOCD process.
