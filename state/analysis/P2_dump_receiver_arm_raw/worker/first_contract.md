# D113: observable Monitor connection

Adopted2026-09-24 under D051/D075 after two separate preflights.
Implementation/independent execution/review are next; no board action yet.
Add one opt-in connection ticket to existing tools/dump_match.py and one bounded
observer. It supplies sampled evidence that this capture's TCP connection was
established before a separately reviewed autonomous transmit window. It is never
router registration, UART framing_clean/exclusivity, MCU permission, successful
delivery or hardware acceptance.

## Existing seam and smallest choice

board_tool.py:81-87 runs a blocking subprocess.run with the existing strict
SSH/ADB command construction. LiveCapture iteration (dump_match.py:315-348)
cannot expose stdout until completion. The current remote receiver connects,
receives and base64-encodes exact bytes (:288-310).

| Approach | Required work | Assessment |
|---|---|---|
| Stream a distinct connection marker | A Popen/streaming transport seam, concurrent bounded stdout/stderr draining, marker/data distinction, timeout/cancel/reap and Windows/SSH/ADB checks | No remote receipt files, but broader process/transport work than the requested observation. Printing a marker inside current board.remote is insufficient. |
| Exclusive remote connection receipt | Optional nonce/receipt writes in the existing receiver and a one-shot read-only observer through board.remote | Recommended: unchanged data path, no second transport, background manager or reservation command. |

Concrete consumer: generate a fresh random UUID, start the existing capture as
an ordinarily managed task, and query that exact ticket from a second task.
The tool does not launch a transmitter or background itself. Proposed usage:

```
python -c "import uuid; print(uuid.uuid4().hex)"
python tools/dump_match.py --connection-ticket <fresh-32-lowercase-hex> --output-dir logs/run-new --timeout 330
python tools/dump_match.py --observe-connection <same-ticket>
```

The capture command remains running while observation occurs. Two modes suffice;
there is no reservation lifecycle or general session framework. Public additions:

```
live_chunks(target, timeout, *, connection_ticket=None) -> LiveCapture
observe_connection(target, connection_ticket) -> dict
```

LiveCapture construction stays passive. No ticket preserves all current API,
CLI, board.remote invocation shape, timeout+15, fragment handling and output
behavior. --input cannot combine with either new option. Observer mode accepts
only its ticket and uses current validated SUMO transport/target. Invalid ticket,
mode combination or local capture path is argument error2 before any transport.
A valid observation exits0 regardless of state; operational failure exits1.
CONNECTED must be read from the result, never inferred from exit0.

## Ticket identity and honest freshness limit

Accept exactly32 lowercase hexadecimal characters representing a caller-generated
fresh random128-bit UUID. The caller must generate a new ticket for every capture
attempt; never recover one from an old directory, rerun or partial result.
The remote path is derived only as `/tmp/sumox26-dump-connection-<ticket>`.
No user-selected remote path, PID, address, port or command is accepted.

Before connecting, exclusively create this mode0700 directory and a mode0600
claim.json. Existing directory/file/symlink refuses before socket connection,
including a prior expired or failed capture. Never delete, overwrite, reuse or
repair it. Verify real /tmp ancestry, no-follow directory access, actual owner,
mode and directory device/inode. Each capture may claim the ticket once only.

A new exclusive claim proves this invocation did not reuse that path. An observer
queries the original claim named by the UUID; it cannot infer an attempted new
invocation if a caller wrongly reuses an older still-live UUID. It must report
that original identity/time unchanged, not label it a new capture. Binding a
newly generated UUID to the current running capture is a caller obligation.
Expired/dead/terminal receipts never yield CONNECTED. Stronger proof against an
intentionally misbound live UUID would need an additional independent claim
identity/handshake and is outside this minimal feature.

claim.json records schema_version1, ticket, transport/target declarations,
actual board boot ID/UID, directory device/inode, receiver PID/start ticks,
claim UTC/monotonic times and overall monotonic deadline. These target strings
bind the request; they do not authenticate MCU identity. Remote deadline remains
script-start plus the existing timeout (1..3600s); receipt work consumes this
budget. Remote evidence-file writes are new Linux bookkeeping authorized only
by eventual adoption, not by the earlier read-only inventory.

## Exact CONNECTED meaning and receive flow

Connect only to127.0.0.1:7500 with timeout<=min(10s, remaining overall budget).
After create_connection returns, check the budget again. At/after deadline,
close/fail TIMEOUT without a connected receipt. Before first recv, atomically
publish exclusive connected.json containing the matching claim identity,
event TCP_CONNECTED, actual local/peer endpoints, socket fd/inode, connected
UTC/monotonic times and unchanged deadline. Publication failure closes this
receiver's socket and fails capture; do not proceed invisibly.

All JSON files are immutable, <=4096bytes, strict schemas, no duplicate keys or
trailing data. Atomically publish complete files without replacing existing
names, within the verified directory. A bounded fixed set of private temporary
files is permitted; partial JSON must never become a valid connection record.
No receipt field supplies an unchecked filename, loop bound or shell argument.

**CONNECTED is only a completed, currently sampled TCP connection.** The router
accepts a client and subsequently inserts it into its Monitor map; TCP connect
success does not acknowledge that insertion (cached pinned monitor-api.go:44-60).
The source exposes read-only mon/connected (:78-89), but it returns only
len(sockets)>0. The already-established USB socat client can make it true. None
of the four registered Monitor methods (:39-42) identifies registration of this
exact receiver. Return router_registration="UNKNOWN" and never substitute an
elapsed delay, empty queues or aggregate flag. No router RPC is added or sent.
A later transmit run must address that race or treat initial byte loss as failure;
this feature alone cannot promise the router is ready to deliver every byte.

The Monitor connection is receive-only: no application payload/probe/handshake
is sent. Connection metadata is out-of-band; stdout still contains only existing
base64 fragments. wire.txt, CRC and Parser receive only actual Monitor payload.
Preserve16MiB decoded/1151-byte line limits, exact CR/LF handling, receiver EOF/
END behavior, remaining-time recv bounds, and full existing parser/CSV checks.
Do not reset the deadline on attachment or data progress.

## One bounded live observation

observe_connection performs one board.remote query, outer timeout<=5s, without
retry/poll loops. Read only the fixed ticket directory and this claimed process's
relevant /proc metadata. Validate no-follow path/owner/mode/device/inode, exact
record schemas/identity, current boot/UID, endpoint and monotonic ordering.
Transport/target must match. No environments, credentials, broad command lines or process signals.
The bounded namespace TCP-table read below is permitted solely to locate the
claimed inode/endpoints; unrelated rows are neither exposed nor retained. Never create missing records or connect a
socket during observation; local cached metadata cannot substitute for the query.

Return state plus exact command outcome, host query start/end UTC, board observed
monotonic/UTC time and validated original claim/connection identities:

- PENDING: directory/claim not yet published, or matching live claimant has not
  published a connection, before deadline. Missing directory is not recreated.
- CONNECTED: matching connected record before deadline, no terminal record, live
  non-zombie PID with exact start ticks, and its exact fd/inode remains an
  established TCP connection with the recorded endpoints.
- TERMINAL: valid terminal record; never CONNECTED even if connected.json remains.
- EXPIRED: no terminal record and deadline reached; never CONNECTED.
- UNKNOWN: required live metadata unavailable or claimant/socket disappeared
  without terminal evidence. Never treat uncertainty as attachment.

Malformed or mismatched identity is CaptureError, not PENDING. After validation,
terminal has priority over expiry; expiry has priority over live states. No
connected record means no CONNECTED. Missing directory before a claim gives no
remote deadline; caller must bound its overall polling wait independently.
Every result explicitly keeps router registration unknown and hardware/MCU
permission false. Observation is sampled, not atomic or a continuing lease;
the socket may close immediately afterward. Report its bracket, never a sticky
ready bit, and require the caller's capture task still be running.

## Completion and failure evidence

On normal completion/caught failure, close only this receiver's socket, then
publish exclusive terminal.json with the claim identity, closed UTC/monotonic
times, observed byte count and END_OBSERVED/EOF/TIMEOUT/ERROR reason. Connection
failure may have claim/terminal but no connected record. END_OBSERVED is not CRC
or file-validation success. Terminal publication failure fails opt-in capture,
including after an apparently valid END; preserve the actual error and prefix.

Keep current transport_outcome fields and partial evidence. Opt-in capture/error
metadata additionally stores the ticket, validated remote records and exact
bounded retrieval command outcome; non-opt-in/offline entries are null.
Retrieve bounded final metadata after the receive command through board.remote,
with <=5s outer timeout. Failure to verify required opt-in records fails capture
instead of omitting evidence. Publication still requires remote exit0 plus all
current Parser/bundle checks. A valid attachment never substitutes for valid END.
Total local waiting is bounded by existing timeout+15 plus at most5s for final
metadata; no retry. Original no-ticket timeout semantics remain unchanged.

Host timeout/cancellation does not prove killing a local SSH/ADB child terminated
the remote process. The receiver retains its own receive deadline and closes its
socket on normal Python unwinding; missing terminal evidence remains UNKNOWN/
EXPIRED. No extra kill, service action, reset/upload, UART open/read/write/flush
or router RPC is permitted. Never reconnect for repair or reuse a failed ticket.
This cannot interrupt every stuck OS syscall or guarantee finally after forced
termination. Leave the bounded claim/connected/terminal files and at most three
publication temporaries for review, each<=4096bytes; no automatic deletion or
recursive cleanup. There is no daemon or reservation-only process to clean up.

## Independent acceptance and later optional smoke

Keep existing tests and assertions unchanged. test_dump_match.py:349-428 covers
legacy remote shape, timeout+15, fragments/CR, failed prefix and exact outcomes;
:301-311 proves offline starts no process/network. New independent tests freeze
this opt-in contract before execution and cover fresh/colliding/reused tickets,
path/symlink/owner/inode/boot/nonce/PID-start/fd-reuse checks, early data and exact
bytes, connect->atomic connected->recv order, zero application sends, observation
states/priorities, malformed/oversize/partial metadata, source death, deadlines,
terminal/retrieval failures, valid END plus failed transport remaining partial,
and unchanged offline/no-ticket behavior. Use controlled transports/local fixtures;
no production-board test is implied. No private test can prove atomic attachment
or full OS/firmware WCET.

A later separately reviewed benign bare-board smoke may start capture with a
fresh ticket, observe its TCP identity, and let it time out without a transmitter.
Expected result: CONNECTED evidence followed by capture failure/no END and retained
partial receipts. Existing socat remains separately visible and unchanged. Such
a smoke would qualify attachment only, never UART clean framing, exclusivity,
native transmitter setup, data delivery or MCU authority. It is not performed or
authorized by this draft.

## Exact schema appendix

All listed keys are required; no others are permitted. JSON integer means a
nonnegative integral JSON number, never bool or float, bounded by UINT64_MAX
unless a narrower bound is listed. Timestamps ending `_ns` use the board's single
monotonic clock. UTC strings have `YYYY-MM-DDTHH:MM:SS.ffffffZ` syntax and valid
calendar values; UTC is diagnostic and need not increase after wall-clock changes.
Ticket is exactly 32 lowercase hex characters. No UUID version-bit constraint is
added. Boot ID is the actual canonical lowercase hyphenated Linux boot UUID.

`claim.json` has exactly:

| Key | Type / constraint |
| --- | --- |
| schema_version | integer 1 |
| ticket | ticket string |
| transport | `ssh` or `adb` |
| target | exact validated request target string |
| boot_id | boot ID string |
| uid | integer <= UINT32_MAX |
| directory_device | integer |
| directory_inode | positive integer |
| receiver_pid | integer 1..INT32_MAX |
| receiver_start_ticks | integer |
| started_monotonic_ns | integer, sampled at script start |
| claimed_utc | UTC string |
| claimed_monotonic_ns | integer >= started_monotonic_ns |
| deadline_monotonic_ns | started_monotonic_ns + requested timeout seconds * 1000000000 |

Claim publication requires claimed_monotonic_ns < deadline_monotonic_ns. The
addition must be representable. Timeout remains 1..3600; it is not renewed.

`connected.json` has exactly `schema_version`, `claim`, `event`, `local_address`,
`local_port`, `peer_address`, `peer_port`, `socket_fd`, `socket_inode`,
`connected_utc`, `connected_monotonic_ns`. Version is 1; claim is an exact embedded
copy of the validated claim object; event is `TCP_CONNECTED`; both addresses are
`127.0.0.1`; local_port is 1..65535; peer_port is 7500; fd is 0..INT32_MAX;
inode is positive. claimed <= connected < deadline. This nested claim copy is
small enough for the existing 4096-byte per-record bound and avoids a new digest
or claim-identity mechanism.

`terminal.json` has exactly `schema_version`, `claim`, `closed_utc`,
`closed_monotonic_ns`, `observed_byte_count`, `reason`. Version is 1; claim is the
same exact validated object; reason is `END_OBSERVED`, `EOF`, `TIMEOUT`, or
`ERROR`. closed >= claimed and, when present, closed >= connected. closed may
reach/exceed deadline, including normal close/publication overhead. Byte count
counts actual socket bytes returned, including a final failing fragment, and
never synthetic receipt/base64 bytes. It does not assert Parser acceptance.

Remote observation stdout is one strict JSON object, at most 16384 UTF-8 bytes,
containing exactly `state`, `observed_utc`, `observed_monotonic_ns`, `claim`,
`connection`, `terminal`. Records may be null as specified below. Remote stdout
must not contain a diagnostic prefix or extra object. This cap accommodates three
4096-byte records plus the fixed envelope. Host command outcomes retain bounded
stderr as already specified by D090; remote_argv remains the exact actual argv.

Public `observe_connection(target, ticket)` returns a dict with exactly:

```
schema_version: 1
ticket: string
state: PENDING | CONNECTED | TERMINAL | EXPIRED | UNKNOWN
error: null
router_registration: "UNKNOWN"
hardware_permission: false
mcu_permission: false
query_start_utc: UTC string
query_end_utc: UTC string
observed_utc: board UTC string
observed_monotonic_ns: board integer
claim: claim object | null
connection: connected object | null
terminal: terminal object | null
command_outcome: exact D090 outcome object
```

The command_outcome keys remain exactly `target`, `remote_argv`, `returncode`,
`start_utc`, `end_utc`, `timeout_seconds`, `timed_out`, `stderr`,
`stderr_truncated`. Query outer timeout is exactly 5 seconds (a deterministic
choice within the draft's <=5 bound); no retries. Query start/end equal the
outcome's start/end. A returned dict always describes an executed, successful
remote observation, not a local cache. Operational errors raise CaptureError;
its public `connection_evidence` attribute uses the same envelope with state null,
error exactly `{code: string, message: string}`, unavailable board times null,
and only records that actually passed validation retained. A partially validated
record is never inserted. Use `CONNECTION_TRANSPORT` for query launch/nonzero/
timeout failures and `CONNECTION_METADATA` for unsafe/malformed/inconsistent
records or required final evidence missing. `.code` remains the stable API.

Opt-in LiveCapture exposes `connection_evidence`, and save_capture writes that
same object under `connection_evidence` in capture.json/error.json. Offline and
no-ticket captures use null. This one envelope preserves the exact final query
outcome even when validation/retrieval fails, without a second transport API.
No public helper beyond the two proposed functions is required: tests can capture
board.remote argv and execute its actual remote Python body with controlled
standard-library/Linux fixtures after freezing expectations.

## State and failure rules

1. Validate existing path/record safety and stored identities before selecting a
   state. Unsafe ancestry/type/owner/mode/inode, malformed/oversize/duplicate-key
   JSON, inconsistent embedded claims, wrong request target/transport, or current
   boot/UID mismatch is CONNECTION_METADATA. An unreadable existing receipt is
   this error, not PENDING. A wholly missing directory or safely verified directory
   whose claim.json is not yet present is PENDING with all records null. Do not
   parse private publication temporaries. Connected/terminal without claim is an
   inconsistent record set, not PENDING. An abandoned empty directory can remain
   PENDING: without a published deadline, the caller's separate bound applies.
2. After valid records, TERMINAL wins, then EXPIRED at observed >= deadline. These
   states do not require live /proc metadata. In particular, a normally exited
   receiver's terminal receipt remains valid after its PID disappears. State may
   retain actual connection metadata while never claiming current attachment.
3. Before deadline, valid records plus absent/denied/unreadable live /proc data,
   zombie process, changed PID start ticks, or changed/missing socket fd/inode/
   endpoints/state yield UNKNOWN. This is loss of the original live identity,
   not proof the stored record was malformed. A live matching claim with no
   connected record yields PENDING. Only the entire matching established TCP
   observation yields CONNECTED. Missing claim cannot yield CONNECTED.
   Coordinator-selected bounded live check: read at most 1 MiB/4096 rows from the
   relevant IPv4 TCP namespace snapshot solely to find this inode/endpoints;
   retain no unrelated rows. A bound exhausted without a complete trustworthy
   check yields UNKNOWN. Compare PID start ticks and fd identity before/after
   the snapshot, and directory identity before/after the query. Identity loss or
   replacement during observation yields UNKNOWN, not a successful old snapshot.
   Initially unsafe paths or malformed stored records remain metadata errors.
4. Observer CLI prints the returned dict as one JSON object and exits 0 for all
   five states. Operational error prints the error evidence object and exits 1;
   diagnostic prose, if any, goes to stderr. Explicitly supplied capture-only
   options (input, output-dir, timeout, or manifest claims) combined with observer
   are argparse error 2 before transport. Capture ticket and observer ticket are
   mutually exclusive. Invalid public API ticket raises ValueError before I/O.
5. Final metadata query runs exactly once after the receive command returns or
   raises, including connect/claim failure and invalid payload. It does not retry
   or reconnect. Success requires receive exit 0, all existing Parser/bundle
   checks, and matching claim + connection + terminal with reason END_OBSERVED.
   Terminal death has priority over live evidence; a successful final query does
   not require the dead receiver's /proc state. Missing required records, EOF,
   timeout, or other terminal reasons never publish success even with a valid
   wire END. Failure before claim may retain all three null records; never invent
   a claim, terminal, identity or timestamp to complete the schema.
6. Existing receive/parser failure remains the primary error; a final query or
   record failure is retained additionally in connection_evidence. New metadata
   failure is primary only when no earlier capture failure exists. In particular,
   existing failed transport + valid END remains TRANSPORT. A metadata error must
   not suppress received wire prefix or change its bytes; keep the actual prefix
   in the partial directory even when there are no valid metadata records.
   Coordinator-selected delivery order: defer metadata-retrieval failure until
   received complete base64 fragments have been yielded; an earlier transport
   failure remains primary. Never replace its exact outcome with the query's.


## Coordinator-selected literal limits and precedence

This appendix resolves C1-C3 and supersedes any less-specific draft prose above.
Invalid public ticket is ValueError before I/O. Opt-in target must match the
existing transport's target syntax and be at most128 ASCII characters; timeout
is an integer (not bool)1..3600. These bounds apply only to the new path. With no
ticket, all existing APIs/argv/behavior remain unchanged.

The existing raw END observation is: append actual bytes to pending, split on LF,
retain the final incomplete part, enforce1151bytes for each complete line and
pending, then stop if any complete line starts with the exact bytes b'END,'.
No decoding or CRC validation occurs there. For the opt-in path, emit/flush every
nonempty returned recv chunk as one original base64 fragment before any
post-return checks. Then check now>=deadline first (TIMEOUT), then decoded total
>16MiB (ERROR), then line bound (ERROR), then END. EOF emits no fragment and is
EOF unless the post-return deadline is reached (TIMEOUT). Preserve recv size
min(65536,limit-total+1), so observed_byte_count can reach MAX_BYTES+1; local wire
retention still stops at MAX_BYTES and full Parser rules still apply. A thrown
socket timeout is TIMEOUT. All other caught receiver errors are ERROR. Once END
is accepted before deadline, later close/publication overhead does not reclassify
it. A terminal-file publication failure still makes capture fail. Closing a
socket is attempted once; if it raises, fail with ERROR and publish no terminal
record, because there is no acknowledged close. Preserve any earlier error too.

Every safety path uses no-follow directory handles. /tmp must be a real root-owned
sticky directory; the ticket directory must be owned by current UID and exactly
0700. Claim/connection/terminal are regular files, owner current UID, mode0600,
link count1, size<=4096. Read at most4097bytes to detect excess. Validate stable
file device/inode/size/mtime_ns/ctime_ns before/after each read. Atomic publication
uses no-replace rename of an exclusively created same-directory0600 temporary
through verified directory handles; no hardlink publication with a transient
second link. Never overwrite, fix modes or remove prior receipts. At most one
private temporary per each of the three immutable records; no recursive cleanup.
Initially unsafe or inconsistent paths/records are CONNECTION_METADATA. A
previously safe ticket-directory identity changing during a query yields UNKNOWN
with no claim of current attachment. Existing-record read failures are metadata
errors. Missing initial claim plus any connected/terminal file is inconsistent.

Remote claim setup samples script-start monotonic time before receipt work;
publication samples claimed time and requires it before deadline. Generated
transport/target/timeout are explicit validated command arguments. Current boot
and UID must match before accepting a claim. Inability to read boot/UID safely is
CONNECTION_METADATA. Each query samples observed monotonic/UTC at its conclusion;
retained started/claimed/connected/closed event times must be <=observed.
The deadline is excluded from that event-time rule: its exact derivation/range
and state-selection checks still apply, including a future live deadline. /proc stat data reads
are capped at64KiB each; process-start parsing accounts for spaces/parentheses in
comm. Live checking is limited to the one claimed PID, its recorded fd and one
IPv4 /proc/<pid>/net/tcp snapshot capped at1MiB/4096data rows. A missing/denied/
malformed/excessive live snapshot gives UNKNOWN. Require one exact established
(state01) inode/local/peer match, with PIDstart/fd and directory identities
checked before/after. Never return or retain unrelated table rows. State is a
sample over the reported query bracket, not an atomic lease.

Read optional connected and terminal records once each. If both are present,
validate their full identity/times before priority selection. TERMINAL precedes
EXPIRED, then live state. A later unobserved close/publication may race a returned
snapshot; it never grants a continuing right to transmit. Final capture success
requires a validated TERMINAL/END_OBSERVED result with all three records. Original
receive exception stays primary; otherwise malformed wire/Parser failure stays
primary over a deferred metadata failure. Perform the one final query before
yielding buffered fragments so its actual diagnostics exist even if Parser fails;
then yield all complete fragments, raise earlier transport failure, else deferred
metadata failure. No received fragment is withheld solely because query failed.
Record both exact receive outcome and connection_evidence separately.

One remote query failure emits only its actual operational error/evidence; no
success-shaped observation is synthesized. Host rejects oversized, extra, duplicate,
unknown-key, wrong-type or inconsistent remote JSON before accepting its records.
Verified records may remain in error evidence; unverified records never do.
Published capture/error metadata use the single connection_evidence envelope;
no-ticket/offline value is null. These are host tooling choices under D051/D075,
not a firmware protocol, tunable, upload permission or protected test amendment.

## Remote metadata-error delivery

The one additional remote stdout branch has exactly these keys: error,
observed_utc, observed_monotonic_ns, claim, connection, terminal. error has exactly
code="CONNECTION_METADATA" and message (string, at most512characters). Times are
actual board observations in the same formats; retained records are null or
wholly validated originals. This strict <=16384-byte diagnostic returns remote
exit0 only because the diagnostic was delivered successfully. Host recognition
raises CaptureError(CONNECTION_METADATA), fills state=null/error in the existing
connection_evidence envelope, and observer CLI exits1. It never becomes a valid
observation or CONNECTED. A response cannot have both state and error. Unexpected
shape/extra keys/types/code is itself CONNECTION_METADATA. Actual process launch,
nonzero exit or subprocess timeout is CONNECTION_TRANSPORT and does not promote
unvalidated stdout records. Do not infer metadata status from free-form stderr.

## Before-execution environment clarification

For the new ticket-capture and observer CLI paths only, missing/invalid configured
SUMO_TRANSPORT or the transport's required target is argument/configuration error2
before board.remote; no query has occurred and no command outcome is invented.
This includes invalid transport, missing/malformed SSH target and missing/malformed
ADB serial under existing syntax. No-ticket CLI behavior stays unchanged. Missing
executable or actual launch failure after a valid target/argv is an operational
CONNECTION_TRANSPORT failure with the actual intended command and host failure
times; remote observation times stay null. The author may add one new independent
unlocked case before first execution; all originally frozen assertions remain.
