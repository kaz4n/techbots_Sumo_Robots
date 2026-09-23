# D113 draft: observable Monitor connection

Draft only, 2026-09-24. No implementation, adoption, board action or D112 change.
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
Transport/target must match. No environments, credentials, broad command lines,
unrelated sockets or process signals. Never create missing records or connect a
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
