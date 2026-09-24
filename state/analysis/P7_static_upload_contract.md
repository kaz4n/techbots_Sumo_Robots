# D154: one-shot inert upload wrapper, host scope

Implement and independently test only `P7_static_startup_raw/upload_remote.py`.
No native invocation is authorized by this contract. Preserve production, frozen
D141-D153 modules, contracts and tests. Later host/run admission must bind reviewed
HEAD/source, the D144 packet and this wrapper, and close CLI initialization
prerequisites before permitting one identified inert upload. No compile or retry.

## Interface and dependencies

`upload(helper, support, *, fs_root=Path('/'), executor=None, clock=None) -> dict`.
`helper` is the frozen static_remote module; `support` is frozen capture_remote.
Reuse its stateless JSON, validation, error, clock-independent process wait/stop
and output-limit functions; do not instantiate Capture, change either module's
globals, subclass it or call collect. Import standard library only, no import
side effects. Optional root/executor/clock are controlled host-test seams only.

The caller supplies module-global BINDINGS from checked upload_bindings.json.
Exactly keys schema,run_id,source_sha256,boot_id,uid,output,files,directories,absent.
Schema fixed-static-upload-v1; source fcddbd8e full digest; run_id
static-fcddbd8e-run01; uid exact integer1000; boot lowercase UUID; output the fixed
direct child `/home/arduino/sumox26_codex_build/static-startup-fcddbd8e-run01-upload`.
Require Python-B. All strings exact str; pin sizes exact positive int <=64MiB,
SHA256 lowercase64hex, normalized absolute POSIX paths without dot/dotdot or
empty components. Files has exactly the17 roles in the supplied binding. Each
pin exactly path,bytes,sha256; paths unique. Directory map has exactly the three
paths in that binding, each list of unique safe component names (1..64 entries).
Absence list exactly the14 fixed paths in that binding, no duplicates. Trusted
source/bindings hashes establish native values; fixtures may replace file sizes
and hashes and directory entry names without creating real tool binaries.

The exact argv is constructed from fixed constants, never caller-supplied argv:
`/usr/bin/arduino-cli --config-file /dev/null upload --fqbn
arduino:zephyr:unoq:link_mode=static --input-file <D144 build>/app.ino.bin
<existing sourcefcddbd8e sketch directory>`.
Use the exact existing paths from P7_static_upload_route.md. Require cli/raw/
sketch role paths to equal these fixed selections. The raw selector is93080B
in real bindings; the actual sibling flat package is93096B. Host fixture sizes
may be smaller. This wrapper never invokes a compiler, reads MCU memory, runs
capture, restores, erases evidence or offers alternate commands/output paths.

## Admission and ownership

Use frozen descriptor helpers directory/child_directory/logical_read/read_file/
identity/directory_id. Require UID1000, userarduino, home/home/arduino,
Linux/aarch64 and exact boot. Check all17 exact file hashes/sizes, three complete
directory entry-name sets (bound enumeration at64; all expected entries actual
directories, no symlinks), all14 absences, and /dev/null nonsymlink character1/3.
An absence means no entry, including dangling symlinks. Missing ancestors mean
absence only after checking existing ancestry; do not swallow permission/path
drift errors. Require /tmp/remoteocd absent before upload only.
Sample /proc for conflicting exact comm openocd,remoteocd,arduino-cli before
launch, at most4096 numeric entries. Disappearance is allowed only if its process
entry is now absent. This is not a kernel-wide lock or exclusivity proof.

Open fs_root and checked parent. Exclusively mkdir fixed output0700, retain its
descriptor/device/inode and parent identity. Once mkdir succeeds, this attempt
is consumed even if fsync or subsequent claim persistence fails. Never enter a
preexisting output directory or overwrite it. Through retained directory fd,
write exclusive O_NOFOLLOW upload_attempt.json, flush/fsync file and directory,
before a process can launch. Record bindings, exact argv/environment, boot/run/
source/time. New operations check complete pathname and held-descriptor identity.
Failure/finalization records may use the original held fd after path drift;
never write a replacement directory. All record and stream files O_EXCL0600.

## Single bounded process

Clock starts on upload entry. Allow180s total admission/launch/wait budget;
CLI wait timeout min(120s,remaining), recomputed immediately before Popen after
opening streams/path checks. Finite file checks/receipt finalization may continue
after deadline but may not launch another process. Validate finite monotonic
nondecreasing numbers. Failure timestamps retain last valid value and report
clock error rather than losing earlier evidence.

Persist upload_command.json before launch. Executor seam:
`execute(argv, stdout_path, stderr_path, timeout)` returns exactly returncode
(actual int or None), timed_out(bool), reaped(bool). Default creates exclusive
upload.stdout/upload.stderr through owned fd, then Popen(shell=False,
start_new_session=True, stdin=DEVNULL,cwd='/home/arduino'). Fixed environment:
HOME=/home/arduino, USER=LOGNAME=arduino, PATH=/usr/bin:/bin, LANG=LC_ALL=C,
ARDUINO_DIRECTORIES_DATA=/home/arduino/.arduino15,
ARDUINO_DIRECTORIES_USER=/home/arduino/Arduino,
ARDUINO_UPDATER_ENABLE_NOTIFICATION=false. Inherit nothing else.
Use D153 limit_child_output and wait_child (1MiB per output; on timeout SIGKILL
owned process group plus bounded5s reap). Never kill unrelated processes.
Read both resulting regular files independently with the frozen helper; each
must be strictly smaller than1MiB. Preserve decoded text with replacement for
invalid UTF8. Nonempty stderr is allowed diagnostics. Never rerun on failure.
Known success requires exit0, timed_outFalse, reapedTrue, complete valid streams
and clean independent postchecks. Preserve process flags even when later work
fails; timeout or lost transport never establishes MCU or process quiescence.

## Finalization and output

Before claim, errors may raise without a result. After mkdir, preserve first
error and attempt every17 file check, every directory and absence check, identity,
null device, process-conflict and owned-directory check independently, including
after failure. Do NOT require /tmp/remoteocd absent afterward. Preserve helper
context-exit errors as additional failures rather than replacing the primary.
On claim failure without a usable held fd, attempt all possible postchecks and
raise the original error; never fabricate a persisted result.

Report exactly schema,run_id,source_sha256,status,attempts,started_utc,
finished_utc,started_monotonic,finished_monotonic,subprocess,stdout,stderr,
first_error,postcheck_errors. Schema static-upload-result-v1; status UPLOADED
only for one known successful execution and clean checks, otherwise FAILED.
attempts increments just before executor invocation (0 or1), not proof Popen
actually started. subprocess None until outcome, then the original exact mapping;
malformed returns fail without presenting a valid outcome. stdout/stderr None
until observed, then text. first_error None or {type,message}; postcheck_errors
list of {check,type,message}. Persist exclusive/fsynced upload_result.json and
return that same report; persistence failure raises. No automatic capture.

## Initialization boundary and tests

CLI initialization can create directories, download missing indexes/builtin
tools and migrate other installed metadata. updater=false does not suppress it.
The later native caller must inspect required existing data/download/package
directories, both indexes, indexed latest builtin tool versions and all installed
platform metadata before authorizing launch. F165 alone does not close this.
This wrapper supplies file-bound upload execution, not independent permission
or a complete host/CLI initialization admission policy. Its postchecks detect
pinned dependency changes but cannot undo CLI side effects. Upload intrinsically
copies to /tmp/remoteocd, may flash loader and sketch, resets and activates MCU;
these effects require explicit inclusion in the later single M0 run scope.

Freeze independent spec-derived tests before first implementation execution.
Cover exact argv/env/no second action, claim-before-execution, existing/consumed
output, pin/identity/override/version/null/process rejection, deadlines/default
Popen/group handling, nonzero/timeout/unreaped/malformed return, stream failures,
first-error preservation, independent postchecks and output path drift. Use
controlled process substitutes, never CLI/OpenOCD; Linux /dev/shm scratch,
Python-B and no persistent binary fixtures. Separate code/receipt review follows.
