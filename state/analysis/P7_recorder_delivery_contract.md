# D225 identified synthetic recorder compile and delivery caller

`tools/run_recorder_delivery.py` provides separate local check, compile and run
phases. No native invocation is admitted merely by having this source file.

```
python -I -B tools/run_recorder_delivery.py --check-only --attempt HEX32 --reviewed-head HEAD40
python -I -B tools/run_recorder_delivery.py --compile --attempt HEX32 --reviewed-head HEAD40
python -I -B tools/run_recorder_delivery.py --run --attempt HEX32 --reviewed-head HEAD40
```

Generate HEX32 once using `secrets.token_hex(16)` and retain it. Its first 16
hex digits identify a positive uint64 session (zero is refused). Local and board
owners are keyed by that session, so a different suffix cannot reuse it. Run
receipts retain the full attempt. The exact source commit remains current and
all source/helper bytes must match it; generated receipts under only this owner
are permitted. There is no automatic retry, changed token or second upload.

## Compile boundary

Reuse the checked D214 compiler loaded through the D222 bootstrap, with a private
recorder-specific source map and the original static ELF/TLS/package checks.
One query and one compiler invocation; single compiler process, static link,
default startup, MATCH0/MOTORS_ALLOWED0, recorder.ino only. Source input names and
bytes are compared with reviewed HEAD and checked on every inherited local
guard. Replace only the staged `recorder_run_identity.h` with the positive
session, explicit setup/MCU UART/ready-pad ownership grants and an untrusted
receive stream. `framing_clean` remains false. The complete staged bytes,
including generated identity, determine the source SHA-256.

The checked-in header and production app grants remain disabled/unchanged.
The recorder uses its existing inert motor callbacks and FIFO8 transport.
Staging uses one directory ADB push into a fresh, admitted source owner, with
complete local and board filename/hash checks before any compiler. Existing
board boot, CLI/dependency/override, conflict, disk and closing checks remain.
Two bounded source chunks carry only the pure artifact component extracted from
the reviewed caller; no upload or receiver function is in that component.
Checked loadable artifacts and unique failures are retained, never cleaned here.

## Run boundary

Run requires the exact successful compile outcome, all nine closing checks,
artifact metadata and identity; then rechecks board identity, installed
prerequisites, complete source tree and artifact bytes. Claim the one session
before any native run preparation. Reuse the original static uploader's
descriptor, identity, filename, process, directory, absence, resource and
subprocess lifetime checks with only a closed recorder static/M0 profile.
In particular `/tmp/remoteocd` must be absent; this caller never removes it.
The original baseline supplies installed-file pins, which are checked live;
only current checked recorder artifact paths/identities and boot/session differ.

Stage one bounded flat upload input packet, verify it before decoding, and run
the uploader's read-only admission before arming the receiver. This prevents a
known upload prerequisite failure from unnecessarily starting a long capture.
Arm the existing D113 TCP capture with expected-session validation and observe
its matching boot/ticket connection immediately before one exact upload. A TCP
connection does not claim router registration, readiness or clean framing.

The receiver has a 900-second remote deadline and 915-second host timeout,
covering upload, the real 200-second synthetic scenario and unchanged dump
deadline. Upload retains its original 120-second child/180-second owner budget
with a 240-second host bound. The run permits 960 seconds before bounded host
child termination, followed by at most 25 seconds to close the receiver thread.
Native progress is accepted immediately on a complete valid END. On an upload
failure the first error is retained and the already bounded receiver is allowed
to reach its natural deadline, preserving partial bytes and terminal metadata.
Last-resort host termination is explicitly indeterminate for remote TCP closure.
Its command owner latches closed under the same lock used to launch/register a
child, before killing registered children. A daemon worker cannot launch a late
observer after that latch; unresolved worker/remote closure is a failed result.
Receiver stdout/stderr are streamed to evidence files, with size/deadline checks
while the process runs and bounded reads after reaping, rather than unbounded
in-memory communication buffers.
There is no unbounded join, UART/router RPC, flush, service mutation, extra MCU
reset, or detached retry. Native upload necessarily includes its usual reset.

Store receiver command stdout/stderr, raw wire, complete CSV validation,
expected/observed/rejected identity, upload result, first error and all closing
errors. A valid CSV bundle alone does not complete this bench run. DELIVERED also
requires matching expected session and source/config/revision declarations,
SYNTHETIC origin, 5001 inhibited frames, eight known scenario events, SEALED and
no reported recording loss, no overruns, and recorded transaction maximum below
800 us. Event offsets and 40 ms frame bins permit up to 2 ms native jitter;
GO may not precede 5.1 seconds and STOP may not precede 200 seconds. The expected
type9/detail5/value1 readiness event at 4.5 seconds is retained and required.
Valid but incomplete, shorter or lossy captures remain saved as failed bench
outcomes. A delivered synthetic recording is target software evidence only;
sensor/motor qualification, physical WCET, match recording and human gates remain
separate. Parent controls actual board scheduling after current matrix closure,
fresh cleanup if needed, focused caller tests and independent source review.
