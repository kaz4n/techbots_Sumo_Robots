# D155: fixed host startup launcher

Host implementation/testing only. Native execution is a later, identified inert
run under the user's bare-board permission. Preserve all frozen D141-D154
helpers, expectations, production files and existing artifact trees.

Implement one `P7_static_startup_raw/startup_run.py`, with no import-time I/O.
Use the existing pinned runner/Probe/board adapter initialization pattern from
read_native_init.py, without invoking its main or consumed scope. Original
D144 run f0220228320c4b2aa20c3e5e8264c813 remains the artifact identity;
this operation is static-fcddbd8e-run01, board2629958581, sourcefcddbd8e.
Local output is fixed P7_static_startup_raw/native_run01, created exclusively.

Reuse pinned bytes of D153 collector, D154 uploader, D152 decoder and the
descriptor helper. Two inline combined JSON/zlib payloads, each hash-checked
before imports, supply exact modules/bindings. Capture loads only the checked
existing p0_capture.py885c4e42 parser in memory; call its loader_image function.
No installation, firmware/source copy, compile, extra reset or recovery retry.
Size final Windows ADB commands (list2cmdline/shlex/UTF16, including terminator)
at <=30000 before any claim. Public `build_command(action,payload)` accepts only
upload/capture and exact bytes, returns the fixed remote argv list (no I/O),
embedding its computed SHA256; reject oversized final commands. Bootstrap must
not execute upload/capture merely through import. Public `main(argv=None)` parses
arguments before calling public `native_run(reviewed_head)`; tests may mock the
latter, which production always binds to the fixed implementation.

Native entry requires explicit `--execute --reviewed-head <40-lowercase-hex>`;
default/unknown/missing arguments fail without board I/O. A later committed run
scope binds that reviewed HEAD plus launcher/source/test/review digests; this
host contract is not a run grant. Require exact current HEAD, clean tracked
files, unchanged scoped inputs, pinned ADB and runner's17local/103source/102stage
checks initially, immediately before each native dispatch and in finalization.
Never reinterpret compile_only=True as upload permission.
The later fixed `native_run01_scope.json` is committed and must exactly match
its bytes at HEAD. Schema `static-startup-run-scope-v1`; exact keys schema,run_id,
board,source_sha256,files. Its files map pins the launcher, independent tests,
contract, design review and final scoped review at their fixed paths. It need
not contain its own commit hash: CLI reviewed-head identifies the actual commit
containing this scope, preventing a self-referential hash. Frozen D144-D154
dependency/receipt hashes stay fixed in the launcher, independent of this scope.

Initialize original D144 identity, directory claim and eight FileRecords from
the existing three hash-bound receipts. Fresh Probe.remote_postcheck and
installed_pins validate packet/source/boot/26installed files. Reuse the exact
two F166 file-only inventory argv from their hash-bound receipts (no CLI query),
requiring status COLLECTED, empty stderr, matching identity and unchanged
relevant files, directory contents and metadata projections. Ignore only
timestamp/ctime fields that are not part of those observed prerequisite pins;
do not weaken fixed paths, hashes, bytes, modes, entry types or required absence.
One prerequisite round before upload, another before conditional capture, and
independent final checks; no old top-level collector is rerun.

Persist exclusive, file-fsynced local inputs and separate upload/capture attempt
records BEFORE their dispatch, containing target/source/reviewed HEAD, exact
command identity and original packet identity. Output mkdir consumes this host
attempt, including partial claim failure. Never overwrite or reuse it. Capture
attempt links the accepted upload report hash. Existing numbered transport
receipts remain raw evidence; flush them before final successful completion.

Upload dispatch once with remote budget180s/120s child/+5sreap already enforced
by D154; host timeout195s. Require exact fixed report schema/run/source, status
UPLOADED, attempts exact int1, subprocess exact returncode int0/timed_out False/
reaped True, text streams, first_error None and empty postcheck_errors. Allow
up to16MiB encoded upload reply for JSON-escaped bounded diagnostic streams;
capture reply max1MiB. Transport/parse/schema/aftercheck failure means FAILED or
UNKNOWN, never upload success or permission to capture; retain original result.

Only a clean upload AND clean intermediate checks permit the separate D153
capture dispatch once, host timeout630s. Preserve COLLECTED/FAILED independently
of decoder RUNNING_COUNTER_ADVANCED/NO_RUNNING_PROGRESS/SAMPLED_FAULT and other
statuses. Require exact fixed report identity and successful18command/18read/
713656byte counts for collected evidence; require exact D153 report keys, exact
integer counts (no bool), first_error None, empty postcheck_errors, and non-None
analysis meeting the frozen support.check_analysis shallow contract. Require
18 ordered read records matching D152 names/addresses/sizes and fixed basenames,
lowercase SHA256 hashes, finite ordered timestamps and the recorded >=2s wait.
Public check_upload(report) and check_capture(report) are raising validators;
their return value is unspecified. Do not treat collection as startup success.
D153 retains raw files and command receipts on the board; do not make
another local binary copy. Record that remote evidence path explicitly.

All permitted final source/packet/dependency/prerequisite/local/HEAD checks run
independently even after a failure, preserving first error and later failures.
No later upload/capture dispatch on uncertainty; bounded Linux-file final checks
remain permitted. Persist a fsynced final receipt; if
persistence fails, raise and do not report success. No retries or fallback.

Expose `orchestrate(operations)` with exact callback keys: `admit`, `claim`,
`local`, `packet`, `installed`, `prerequisites`, `intent`, `upload`, `capture`,
`finish`. First admit() then claim(); on either failure, raise without native
dispatch (a partial claim still consumes the output). Then check callbacks
local/packet/installed/prerequisites, intent('upload',None), upload() and strict
check_upload(report); repeat checks, intent('capture',upload_report), capture()
and check_capture(report). Each intent precedes incrementing its attempt and
dispatch. A failure stops that sequence. Finally independently call all four
checks, then finish(result). finish persistence failure raises. Return result
keys exactly status,upload,capture,first_error,postcheck_errors,upload_attempts,
capture_attempts; status COMPLETED only with no errors and collected capture,
otherwise FAILED. first_error is None or {type,message}; later checks append
{check,type,message}. Preserve received reports, including failures. Exceptions
before a report leave that report None and its attempted outcome unknown.
COMPLETED means evidence collected, not necessarily observed startup progress.
Tests cover lost/nonzero upload, malformed/failed reports, intermediate failure,
capture fault/no-progress, independent final failures, claim/persistence failure,
HEAD/source drift, overlong payload rejection and default CLI refusal. Native
operations use only fixed callbacks; injected operations are host test seams.
Independent tests freeze before first implementation execution; scoped reviewer
checks actual source/receipt. Small RAM fixtures/Python-B only; no target run.
