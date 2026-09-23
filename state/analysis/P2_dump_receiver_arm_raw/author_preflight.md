# D113 independent public-contract preflight

2026-09-24. Reviewed draft SHA-256
`e24b276b89e84032f5df0edf24f564c0624abe26fe359fcc89ab67b86588cb8f`.
This is a recommendation to the coordinator, not adoption or executable tests.
The reused independent test-author context read the full draft, D090 public
`P2_dump_contract.md`, and existing `test_dump_match.py` expectations. It did not
read `dump_match.py`, `board_tool.py`, or other production implementation bodies.
No production, tests, configuration, shared ledger, or board state was changed.

## Finding

The two-mode design is appropriately bounded. Fresh caller ticket, exclusive
claim, exact original identity, sampled TCP evidence, terminal/expiry precedence,
and UNKNOWN router registration avoid a sticky or stale readiness claim. There
is no MCU command path. No reservation command, streaming transport, daemon,
retry framework, or new remote API is needed.

Before independent executable tests freeze, adopt literal record/result schemas
and three narrow outcome rules: live identity disappearance versus invalid stored
identity, incomplete claim publication, and required final evidence on success
versus failure. The proposed appendix below is an independently authored minimal
choice; the coordinator may choose different literal names before adoption.

## Proposed exact schema appendix

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

## Proposed state and failure rules

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

## One remaining coordinator-owned literal to freeze

The draft says preserve the existing receiver's END behavior, but public D090
docs/tests do not state its exact raw END detection predicate. The author will
not infer it from production. Please state the existing predicate as public
behavior before remote-script tests freeze. The coordinator has now selected the
opt-in deadline equality rule: check before connect/recv and after each return;
emit all returned recv bytes to the actual prefix, then now >= deadline fails
TIMEOUT even if that return includes END, with no further recv. Default/no-ticket
semantics remain unchanged. If the existing predicate merely sees
an END-prefixed complete line, END_OBSERVED remains only that fact; Parser alone
decides CRC/framing success. Terminal closed time can be later than that accepted
observation and does not retroactively relabel it.

## Test reachability and limits

Independent host tests can exercise full CLI/API validation, passive construction,
actual generated receiver/observer bodies with controlled clock/socket/filesystem/
process fixtures, zero send calls, exact fragment bytes, deadline equality,
publication and retrieval failures, lifecycle priority, reuse and replacement,
all strict schema branches, and unchanged D090 outcomes. Stored record identity
and live process/socket identity are distinct test stimuli. No private production
state mutation, real Monitor connection, or new public testing framework is needed.
Race-free continuous attachment, delivery to the router's per-client map, stale
UART exclusion, OS WCET, remote-child killing, and physical MCU readiness remain
unproved. This preflight alone is not runtime or hardware validation.
