# D177 thin inert action composition (host preparation)

Implement only state/analysis/P7_motor_fault_raw/inert_actions.py. Reuse D175
upload_loader, D176 collect_motor_fault and the existing CompileOnce transport
when a later native caller is admitted. This file has no executable CLI, device
access during import/composition, staging, ownership directory creation or retry.
No existing implementation, locked test, scope manifest or source pin is changed.
The board is disconnected. Native execution and current board bz2 availability
remain unverified and require a later fresh identity/permission/source scope.

Constants: RUN_ID='motor-fault-8f592937-run01'; SOURCE=
'8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'.
Parent output '/home/arduino/sumox26_codex_build/'+RUN_ID+'-'+action.
Valid actions are exact built-in str 'upload' or 'capture'. Canonical JSON is
ASCII, sorted keys, compact separators, allow_nan=False, plus a single LF.

## Public command composition

build_command(action, sources, bindings) returns a remote argv list, no execution.
Sources is an exact dict of UTF-8 bytes: helper/support/upload for upload,
helper/support for capture. Each is nonempty; caller inputs remain unchanged.
Bind payload exact keys run_id,source_sha256,sources,bindings. Each source entry
is {'source':decoded UTF-8 text,'sha256':SHA256(original bytes)}. Bindings is a
JSON dict with exact selected schema fixed-motor-fault-<action>-v1, RUN_ID,
SOURCE and selected output. Deep validation of the remaining bindings is by the
reused public APIs before ownership; composition must not reimplement them.
Actual source and artifact origin are independently pinned by the native caller;
controlled tests may provide inert substitute modules. No arbitrary environment,
run ID, script path or action override is exposed.

Canonical payload <=196608 bytes, bz2.compress(...,compresslevel=9), canonical
base64 by default. If that actual Windows command exceeds30000 units, compose
a canonical base85 alternative prefixed b85: and recheck the same ceiling; reject
if neither fits. Small existing commands retain identical base64 framing.
Self-contained exported BOOTSTRAP checks action/argv count, startup Python -B
AND current sys.dont_write_bytecode is True, strict canonical selected base64 or
b85:-prefixed base85, exactly one bounded BZ2 member (decompress max196609,
require <=196608/eof/no unused_data), SHA256 and closed JSON shape. Reject duplicate
keys and nonfinite JSON numbers. Check every inline source hash before executing
any source. Validate selected identities before module loading. Register modules
with deterministic names fixed_motor_fault_<role>, __file__='/__sumox__/<role>.py',
never __main__, in sys.modules before exec. Execute helper, support, then upload.

Fixed argv prefix:
/usr/bin/env -i HOME=/home/arduino USER=arduino LOGNAME=arduino PATH=/usr/bin:/bin
LANG=C LC_ALL=C /usr/bin/python3 -I -B -c <BOOTSTRAP> <action> <payloadSHA> <token>.
Actual Windows command uses ADB path and serial from compile_motor_fault.py:
[ADB,'-s','2629958581','shell','-T',shlex.join(remote_argv)]. Measure with
subprocess.list2cmdline(...).encode('utf-16-le')//2; reject >30000 units.
Source compression stays in memory; no temporary payload files or package install.

## Fixed bootstrap dispatch and bounded reply

Upload dispatch exactly upload.upload_loader(helper,support,bindings=bindings,
run_id=RUN_ID). No automatic capture/reset/compile from bootstrap.
Capture loads three existing installed modules in this order, using the helper's
logical_read(root_fd,absolute_path,limit) with a no-follow directory root '/':
parent /home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/
p0_capture.py 18880B 885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c
recorder_heap.py 11002B d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92
runtime_capture.py 28644B a4d58b3cbac8b0a3cf96ce6d4f53bc17e935b9aee9bc1c09809ee20ea806fdae
Read/hash-check all three before executing any installed module. Register the
real names p0_capture,recorder_heap,runtime_capture for their existing imports.
Call support.collect_motor_fault(helper,runtime_capture,p0_capture.loader_image,
bindings=bindings,run_id=RUN_ID); never call the legacy whole runtime collector.
Independently re-read/hash-check all three after an attempted initial read/import/
action, including failures; close the root descriptor. Retain the first exception
and every later check/close failure. No installed source is written or staged.

Emit exactly one canonical JSON object <=65536B, exact fields:
schema='motor-fault-action-v1', action, run_id, source_sha256, report,
remote_result_path, full_result_bytes, full_result_sha256, first_error,
postcheck_errors. Fixed result basename upload_result.json/capture_result.json
under selected output. Report is the public API result; omit ONLY stdout/stderr
from the TOP-LEVEL returned upload report to keep transport bounded. Those fields
are siblings of subprocess; no nested stream fields exist. Full result and raw
streams stay remotely retained by those APIs. Full bytes/hash bind the canonical
original report before omission; when no report exists those fields and report
are None. Errors: {type,message}; subsequent errors add check. Partial/failed
reports remain visible; no fabricated success. Pre-payload validation failures
may raise without an envelope; a transport failure never admits capture. Oversize
reply raises instead of emitting a success response or silently truncating data.

## Public reply admission

validate_reply(action, reply) returns None or raises ValueError; pure/no mutation.
Require exact envelope keys/identity/path, no first/postcheck errors, dict report,
positive integer full_result_bytes <=16777216, lowercase64hex result digest.
Reject bool-as-int and NaN/infinity where numbers are specified.
Common report keys: schema,run_id,source_sha256,status,started_utc,finished_utc,
started_monotonic,finished_monotonic,first_error,postcheck_errors. UTC fields are
nonempty strings; clock values finite and >=0, finish>=start. No report errors.
Upload adds exactly attempts,subprocess: schema motor-fault-upload-result-v1,
status UPLOADED, attempts integer1, subprocess exactly returncode integer0,
timed_out literalFalse,reaped literalTrue. Duration strictly <180 seconds.
Capture adds exactly counts,wait,reads,analysis: schema motor-fault-capture-result-v1,
status COLLECTED, duration strictly <600 seconds. Full canonical returned capture
report bytes/hash must match the envelope (nothing is omitted from capture).
Analysis exact schema,flash,relocation,snapshots,coherence from D176, all four
flash flags literalTrue and coherence UNPROVEN. Relocation before/after identical,
exact node_address,bss_address,bss_size,visited_nodes; N=1..3 unique4-aligned
SRAM node addresses, selected node in list, BSS2632B/8-aligned and within
0x20000000..0x200C0000. Each node's196B extent is in that same half-open region.
Counts exactly commands=reads=18+2N, requested_bytes=592248+392N.
Read metadata exact name,address,bytes,sha256,file; addresses and byte counts
are built-in integers, names/files/hashes are strings. Exact D176 successful ordered
sequence, addresses/sizes, hash shape and zero-based basename. Relocation lists
at0x200017bc; node order from visited_nodes; two snapshots at BSS+0/2592B.
Corresponding before/after loader chunks, sketch, list and node read hashes must
match; each list hash must also match its same-side list-confirm hash. Diagnostic
snapshot hashes may differ. These enforce D176 raw-bracket equality in the reply.
Analysis snapshots exactly those two entries. Wait is existing D176 exact shape
requested_seconds,before,after; requested=2, finite actual
elapsed>=2; entire interval within the enclosing capture report. No lifecycle,
terminal state, contact, motor readiness, atomicity or physical-gate inference.

## Public conditional sequencing

run_actions(operations) uses exactly six callable keys:
local, prerequisites, intent, upload, capture, finish. Caller already owns a fresh
local native scope; this utility cannot claim or reuse one itself.
For each action in upload,capture: local(); prerequisites(); intent(action,
predecessor), then increment that action's attempt count once, call action(),
store its raw envelope, validate_reply. Predecessor is None for upload and the
successful checked upload envelope for capture. Any error stops new actions;
no retries, capture only after checked upload success. Regardless of failure,
run local and prerequisites independently once more, preserving all errors, then
finish(report) exactly once. Report keys schema='motor-fault-sequence-v1',status,
upload,capture,upload_attempts,capture_attempts,first_error,postcheck_errors.
Initialize envelopes None/counters0; status COMPLETED only after both checked
actions and all final checks succeed, otherwise FAILED. Preserve raw replies
when validation rejects them. First error {type,message}; later check failures
{check,type,message}. If finish raises, change status FAILED, preserve primary
and finish diagnostics, attach sequence_result to the raised exception; never
retry finish or lose the earlier failure. No device call exists in this function
except explicitly supplied callbacks; native caller must pin/wrap those callbacks.

## Independent host acceptance

Write/freeze a separate contract-derived oracle without reading this module's
implementation. Test command shape/actual size, both action dispatches, source
hash/order/imports, bounded framing/duplicate/nonfinite rejection, installed module
before/after checks on failures, compact output/remote full result digest, strict
successful receipt admission plus malformed/failure reports, conditional capture,
failures in each step/independent final checks/finish precedence and no retries.
Use controlled modules/readers/executors only, Python-B and owned RAM scratch.
Production source composition must separately fit the actual Windows ceiling;
no target/source rebuild or bytecode. Freeze source/tests before first execution,
retain negatives, obey the two-fix escalation rule and obtain a fresh read-only
same-model review. This contract authorizes host preparation only.
