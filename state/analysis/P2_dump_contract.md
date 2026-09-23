# D090 bounded IDLE dump - host session and receiver contract

2026-09-23 delegated D051/D075. Extend B8/B13/B15 from formatted RAM rows to one
actual stream owner plus receive-only Linux/host capture. R1/R2/R3/R4/R7 unchanged.
The separately audited native backend must implement Port; an abstract callback
alone does not prove Bridge boundedness or hardware transport. No motor permission.

## Lifecycle and trigger

Transfer owns no recorder, Robot reset or motion path. Caller synchronously calls
Robot.step -> MotorGate -> AttemptRecorder.consume -> Transfer.step; no concurrent
source mutation. While between control ticks, step may pump using the same actual
latest RobotResult and its original decision_us. It must be marked fresh by its
original Robot.step; never call Robot.step twice to manufacture transport authority.
A decision age strictly below TICK_US is required before any write. New control
ticks take priority over pumping. Exact repeated now_us does no work. Consecutive
now gaps must be below half uint32 range; accumulate session/stall age safely.

Eligibility: actual final IDLE; gate phase IDLE; no start_release/GO; disabled
motors and exact zero duties; no contract/escape fault; service_menu with LOG_DUMP
selected. Require result.fresh and token nonzero. The current result token may
repeat with identical decision_us; a newer token must have forward decision_us.
Lower token, changed timestamp for same token or backward/half-range time fails.
During ACTIVE, skipping a result token cancels (unknown intervening state). A
nonfresh result cannot pump; if an active session receives it, cancel immediately.
Context/fault/STOP/reset cancellation wins before source reads, formatting or I/O.

A genuine fresh menu.request=LOG_DUMP starts once per result token only. No queued
request while ACTIVE, and ignored requests cannot replay after completion. Linux
capture is receive-only; this iteration adds no inbound RPC/request/reset command.
Start only from a nonzero SEALED or INTERRUPTED retained epoch. EMPTY/RECORDING/
DRAINING refuses without writing. A successful dump may still report incomplete,
interrupted or loss; no repair, omission or fabricated missing/final frame.

Bind source object, retained epoch, phase and exact summary/counts on start. Check
semantic snapshot equality before every read/write; detect replacement and any
observable owner mutation. Copy only one formatted line plus metadata, no payload
array copy or borrowed row pointer across calls. A new accepted START creates a
new epoch and cancels the old session before source reuse. Explicit onRobotReset
cancels the session before caller invokes recorder.onRobotReset/Robot.reset. It
never performs/reset-authorizes those actions itself. Physical MCU reset/reflash/
power loss has no RAM retention guarantee. STOPPED/terminal exhaustion cannot dump.
A separate local-only reset interaction still needs application implementation;
ordinary core software reset and recorder preservation are real existing APIs.

## Byte stream and progress

ASCII LF-delimited stream (no CR/NUL), canonical decimal numbers without leading
zeroes. Session id is the triggering Robot token, not a hardware identity.
Origin codes0 unknown,1 synthetic,2 hardware_reported are explicit caller claims.
Fixed first line:
SUMOX26_DUMP,1,session,epoch,origin,log_hz,frame_capacity,event_capacity,frames,events

Then exactly this order, each CSV payload retains its existing trailing LF:
SH,session,<exact csv::summaryHeader>
SR,session,<exact csv::summaryRow of frozen snapshot>
FH,session,<exact csv::frameHeader>
FR,session,<exact csv::frameRow ordinal0..frames-1, oldest first>
EH,session,<exact csv::eventHeader>
ER,session,<exact csv::eventRow ordinal0..events-1, insertion order>
END,session,frames,events,crc

CRC is unsigned decimal CRC32/ISO-HDLC (polynomial0xEDB88320, initial/final XOR
0xFFFFFFFF) over every exact byte preceding END, including BEGIN and all LFs;
END is excluded. No extra blank line. Empty payload collections still emit headers.
All summary/status/raw bytes and losses are preserved. No firmware/source hash is
invented or embedded; optional capture manifest declarations remain separate.

One step formats at most one line (fixed1152-byte storage inclNUL) and invokes the
write callback at most once with <=DUMP_PAYLOAD_BYTES(64) pending bytes. Callback
returns PENDING/0, PROGRESS/count in1..offered, or ERROR/0. Other combinations fail
PORT. Never advance offset/CRC twice or renew stall age on PENDING. Complete lines
advance the cursor only by acknowledged bytes; formatting a subsequent line waits
until a later step. Completion is SENT_UNCONFIRMED after END bytes are acknowledged,
not proof Linux received/saved them. Native may retain an encoded packet while
returning PENDING and finally acknowledge its whole payload once; repeated offered
bytes remain identical. No polling loop, heap, String or blocking lock in owner.

Total deadline DUMP_TOTAL_MS300000 and no-ack stall DUMP_STALL_MS2000 are development
bounds, not throughput measurements. Equality expires before I/O, even if ready.
Linux readiness loss cancels immediately. Port.cancel is bounded and may be called
on context loss even though no further log data is allowed. Native partial packet
cancellation may poison that native instance; Transfer never reinitializes it.
Terminal reports remain inspectable; a fresh later intent may start a new session
if the actual Port is usable. State/transport failures never mutate the recorder.

## Receiver and publication

New tools/dump_match.sh invokes Python capture over the existing strict SSH/ADB
transport. It receives TCP Monitor127.0.0.1:7500 on board Linux, sends no bytes or
motion/reset RPC, and uses explicit bounded connection/overall/line/file limits.
Also support --input PATH for an offline synthetic/recorded transport fixture;
never label this mode hardware validated. Implement a pure incremental Parser for
bytes with feed/finish so arbitrary TCP chunk boundaries are covered independently.
Strict wire order, exact session/epoch/capacity/count/rate/origin domains and CRC.
Reject malformed ASCII, oversize lines/stream, duplicate or missing records,
truncation, wrong ordinals and cross-session mixtures. Finish only on valid END;
trailing bytes are invalid. Bound total input at16MiB, line1151bytes excluding LF,
rows <=5001frames/4096events (configured advertised capacities must match these
current hard bounds or be lower; no trust in remote sizes). No arbitrary output
path from the sender. Apply existing CSV bundle validation to reconstructed files;
format/consistency failure is capture failure, reported loss/interrupted is retained.

Create a new unique local destination directory; never overwrite existing results.
Write frames/events/summary CSV, manifest and validation report into a sibling
partial directory; preserve it labeled partial on any failure. Publish by one
same-filesystem directory rename only after protocol and existing bundle checks
pass. Filename base YYYYMMDD_HHMMSS_mode<1..6> plus unique suffix prevents collision.
Manifest schema1 from D074: session_id binds local capture id+wire session;
origin from explicit wire declaration (offline input never upgrades it), closure
closed only after valid END, other firmware/source/config identities nullable
unless explicitly supplied by caller and validated. Record wire CRC/session/epoch,
receive mode/target and exact command outcomes separately; hashes do not authenticate
firmware or physical source. --input never contacts board; failed network never
fabricates complete files. No additional sensor connection requested.

## Verification

Independent expectations from this contract/public headers, not implementation.
Actual Robot/AttemptRecorder/menu and MotorGate trace must produce IDLE-only stream,
with stopped/refused and reset-preserved/canceled cases. Independent receiver parses
actual C++ stream and existing validator checks all retained rows/losses. Cover every
state/fault/lifecycle, token/time/deadline adjacent values/wrap, partial writes/stalls,
source replacement, cancellation mid-line, all record kinds/CRC, nonempty/empty
collections, incomplete/interrupted, 5001/4096 bounded synthetic stream and hostile
TCP fragments/truncation/CRC/session/path inputs. Native API/callback and real
installed target compile/ELF review remain separate obligations. No human gate or
physical200s/freeRAM/800us result follows from host tests or target compilation.

## Frozen API clarifications

Unsafe/nonfresh context cancellation has priority even at a repeated now_us;
otherwise exact repeated now does no work. request_unavailable cannot authorize
start. terminal_exhausted summary refuses NO_EVIDENCE even if caller suppliesIDLE.
Report.frames/events count completely acknowledged data rows (not declared totals);
bytes counts all acknowledged wire bytes includingEND; crc exposes finalized
CRC32 of acknowledged pre-END bytes. State/time/result/source/readiness failures
cancel ACTIVE; format/port/stall/total failures fail; invalidstart refuses.

Python tools/dump_match.py exports CaptureError(ValueError) with .code, Parser()
with feed(bytes)->None and finish()->Capture. Capture is immutable, with integer
session,epoch,origin,log_hz,frame_capacity,event_capacity,frame_count,event_count,
crc32,mode and bytes frames,events,summary. Parser validates exact wire framing,
CSV headers/raw-field consistency using D074, summary epoch/count/mode/phase3or4
and no terminal exhaustion. save_capture(chunks, output_dir, *, receive_mode=
'offline', target=None, firmware_revision=None, source_sha256=None,
config_sha256=None)->Path creates/publishes the new directory, applies complete
existing validate_bundle checks, preserves .partial evidence/error on failure.
Manifest origin remains wire-declared; offline capture cannot establish hardware.
CLI main(argv=None) returns0success/1capturefailure, argparse2invalidargument.
Options: --input PATH (no network), --output-dir PATH(defaultrepo/logs), --timeout
integerseconds1..3600(default330), optional --firmware-revision/--source-sha256/
--config-sha256 with strict D074 formats. Live uses existing SUMO_* env transport.
Validate all options before connection/publication. Connection<=10s, finite overall
deadline. No overwrite, symlink input/output ancestry or sender-supplied path.

Publication filenames are `<base>_frames.csv`, `<base>_events.csv`,
`<base>_summary.csv`, `manifest.json`, `validation.json`, `capture.json`, and
`wire.txt`. Invalid CLI paths (symlink/nonregular/nonlocal) are argument errors2;
protocol/read/transport failures after valid options are capture errors1.
The remote receiver base64-encodes individual received chunks only to preserve
exact raw bytes across the existing text-mode ADB/SSH wrapper. The host decodes
before protocol validation; this wrapper adds no sender data or network writes.
receive_mode accepts `offline`, `ssh` and `adb`. Existing output files or file
ancestors are invalid CLI argument2, before network access. Publication uses
Windows no-overwrite rename or Linux renameat2(RENAME_NOREPLACE); unsupported
hosts/filesystems fail with retained partial evidence, never fall back to overwrite.
The public publish(partial:Path,destination:Path) helper exposes this no-replace
boundary for independent tests. Verified primary references:
https://docs.python.org/3/library/os.html#os.rename and
https://man7.org/linux/man-pages/man2/rename.2.html (retrieved2026-09-23).

LiveCapture returned by live_chunks is iterable and records `outcome`; it is
written under capture/error.json `transport_outcome` (offline/plainfixture null).
Exact fields: target, remote_argv, returncode, start_utc, end_utc,
timeout_seconds, timed_out, stderr, stderr_truncated. The timeout_seconds field
is the outer process deadline (CLI+15), while remote_argv[-1] is the board's
overall receive deadline. Returncode is exact exitstatus or null for timeout/
process-launch failure. stderr is bounded4096characters with truncation flag.
