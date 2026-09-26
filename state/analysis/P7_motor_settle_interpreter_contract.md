# D201 offline SETTLE interpreter contract — proposed for adoption

26 September 2026. This specifies a new local interpreter only at
`state/analysis/P7_motor_settle_run_raw/interpret_run01.py`. Preserve the old
D195 interpreter, maps, raw packets, receipts and failures. No implementation,
test execution, new MCU capture, native action or successful decode is claimed
by this contract. Root adopts the specification before independent tests and
implementation. Its author may prepare tests from these fixed interfaces without
reading the new implementation; freeze that oracle before implementation review
or execution. A future capture's packet hash is not known or invented here.

## Fixed evidence and limits

The immutable current field map is
`state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json`,
16346 bytes, SHA256
`0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd`.
It fits the fixed65536-byte map bound. Its schema is
`motor-settle-observed-decode-fields-v1`; selected_types16 and
selected_fields115 preserve all104 fields of14 prior structs and add the11
observed fields of two SETTLE structs. The pinned map, rather than Python or
host C++ layout, supplies every selected size, offset and window address.

| Provenance input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_run_raw/interpret_run01.py | 3516 | d6409ff5839abcea9f4edbf5c93f8fcf7bf1c27cdc907ba2b9f778bd3d017b26 |
| state/analysis/P7_app_motor_observe_compile_raw/abi_static02_decode_fields.json | 10447 | b96b6a3e7349baff471af3bb115c13ab2c1de07c6949a419ed3e9ed1afe16939 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/result.json | 905572 | 230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/abi.json | 5410 | 069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941 |
| src/hal/motor_settle_probe.h | 2366 | 2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8 |
| src/hal/motor_port_unoq.cpp | 19185 | f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e |

Those are provenance and independent-test inputs, not runtime imports or
permission to call their entry points. The new interpreter reads only its map
and supplied saved packet. It does not execute historical source, import the
native caller or project a transport framework. The old decoder's selected
little-endian field meanings are retained; its unchecked name-to-dict overwrite
and missing format checks are not requirements to preserve.

The fixed run is `app-motor-settle-117cc0e7-run01`; source SHA256 is
`117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`.
Use these names throughout this contract:

* PARENT = `/home/arduino/sumox26_codex_build`.
* UPLOAD = PARENT + `/app-motor-settle-117cc0e7-run01-upload`.
* CAPTURE = PARENT + `/app-motor-settle-117cc0e7-run01-capture`.
* RAW = repository `state/analysis/P7_motor_settle_run_raw`.

The packet bound is1048576 bytes. Its expected hash is a required explicit CLI
argument; there is no placeholder or mutable packet hash inside source. File
hashes are exactly64 lowercase hexadecimal characters, lengths and integer
metadata use exact Python int excluding bool, and byte arguments use exact
immutable bytes excluding bytearray/memoryview. Never treat bool as an integer.

## Public pure interfaces

Expose exactly these public work seams and the thin main:

```python
decode(kind, body, *, field_map_raw) -> dict
annotate_settle(report) -> dict
interpret(packet_raw, *, field_map_raw) -> dict
main(argv) -> int
```

The three pure seams perform no I/O, subprocess, sleep, device, credential or
filesystem operation, and do not mutate arguments. They return fresh containers;
mutating a returned dict/list must not mutate an input or another result.
Import defines constants/functions only, permitting read-only module-location
path resolution but no input reads, output creation or native dispatch.

`decode` takes an exact str naming one of the16 full struct names in the pinned
map, an exact bytes body of exactly that struct's mapped width, and exact bytes
field_map_raw. No public short aliases, scalar selector, address, offset, count,
alternate type or trailing bytes are accepted. Validate map bound, exact length
and hash before using its contents. Unknown struct names and short/long bodies
fail. A private bounded recursive decoder may use the fixed map's aliases:
Call, CountdownResult, HaltResult, LifecycleResult, Outputs, PreviousTick,
Result, RobotResult, RuntimeReport, SettleProbeSample, Snapshot and
TransactionReport. Result means motors::Result; CountdownResult means
countdown::Result. These are fixed aliases, not caller-supplied mappings.

Decode u8/u16/u32/u64 and f32 explicitly little-endian, bool from exactly0 or1,
Call[64] as exactly64 mapped32-byte Calls, and u8[2] as exactly two unsigned
numeric bytes. Unknown kind or an out-of-bound mapped field fails. Reject
nonfinite decoded f32 at that field; do not reach JSON serialization with NaN
or infinity. Retain finite values, negative zero and unsigned integer values
without signed reinterpretation, rounding, saturation or unit conversion.
The public result contains every selected field, including all64 retained trace
slots and all count/rejected/overflow/timing/current/first-failure fields. Do not
invent omitted fields or trim the prefix array to manufacture complete history.
Recursion visits fields by ascending(offset,name), array elements by index.

Wrong Python argument types raise TypeError with three string arguments
`(stage, code, path)`. A malformed admitted byte input to decode raises ValueError
with the same three-argument shape. These are ordinary exceptions, not a new
exception framework. Paths below use slash-separated field/index names; the
root is `/`. The stable codes/order below apply. No raw input body or arbitrary
exception repr is included in an error message.
For decode argument type failures use window/ARG_TYPE at `/kind` or `/body`,
or layout/ARG_TYPE at `/` for the map. UNKNOWN_TYPE uses `/kind`; a whole-body
BODY_SIZE error uses `/`.

`annotate_settle` accepts exactly the decoded SettleProbeReport shape: current
and first_failure each have elapsed_us/poll_index u32 and reason/fresh_mask/
valid/reserved u8; has_current/has_failure are u8; report.reserved is a two-item
u8 list. Reject extra/missing keys, wrong Python types or out-of-range scalars
with TypeError/ValueError(stage=`annotation`, code=`ARG_TYPE` or `SHAPE`, path).
Semantically unusual but in-range bytes are observations to annotate, not
argument errors. Its output is specified separately below.

`interpret` accepts exact bytes packet_raw and field_map_raw. Wrong Python
argument types raise TypeError(`packet` or `layout`, `ARG_TYPE`, `/`). All other
input-data failures produce the REJECTED result below; programmer errors are not
silently converted to accepted or partial evidence. Hashes refer to the exact
received bytes. Preserve original buffers and parsed receipts, not a normalized
replacement presented as the source packet.

## Fixed windows and ordered read plan

Only the following six mapped windows are allowed, in this order:

| Name | Address | Bytes | Full type |
|---|---:|---:|---|
| trace | 536951180 | 2128 | motor_fault::TraceReport |
| report | 537119696 | 1168 | app_motor_observe::Report |
| runtime | 537117984 | 600 | app::RuntimeReport |
| transaction | 537115448 | 504 | app::TransactionReport |
| settle | 537121768 | 28 | motors::SettleProbeReport |
| gate | 536953520 | 88 | motors::MotorGate |

The report keeps before_abort.previous, the48-byte fsm::PreviousTick at
offset1120/address537120816. The old live previous window/address537115952 is
not admitted. Never discard the nested pre-abort value as if it equalled the
post-abort live record.

The fixed26-entry PLAN is five before.loader chunks at0x08000000 with sizes
[65536,65536,65536,65536,1536], two before.sketch chunks at0x08100000 with sizes
[65536,29984], six first windows, six second windows, two after.sketch chunks,
and five after.loader chunks. Flash addresses advance by65536 per chunk; window
addresses/widths are the table above. Flash names are
`before.loader.0` through `.4`, `before.sketch.0` through `.1`, then analogous
after names. SRAM names are first.NAME and second.NAME. For each index i the
only basename is `f'{i:02d}-{name}.bin'`; indices7..18 are the twelve SRAM files.
In particular11-first.settle.bin and17-second.settle.bin replace previous files.
The total requested bytes are727432; the six windows total4516 per sample.
No supplied address/name can alter PLAN.

## Packet, receipt and linkage admission

Use strict UTF-8 JSON with duplicate object keys and every nonfinite numeric
value rejected, including NaN/Infinity constants and overflow such as1e999.
A top-level scalar/list does not satisfy a dict
schema. Preserve string contents and numeric values; accept JSON whitespace/key
ordering without rewriting the source. Catch parser encoding/duplicate/constant/
depth/number errors as the relevant stable JSON code, not a partially parsed
dict with overwritten keys. No eval or permissive base64 decoding is allowed.

The saved retrieval packet has exactly these keys:
`status, identity_before, identity_after, files, closing_file_checks`.
status must be FILE_ONLY_RESULTS_VERIFIED. Both identities must equal this
exact typed mapping: user arduino, uid1000, gid1000, home /home/arduino,
sysname Linux, release6.16.7-g0dd6551ae96b, machine aarch64,
boot_id55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, python[3,13,5]. This is declared
retrieval evidence, not an independent proof of hardware origin or serial.
files is a list of2..14 rows; closing_file_checks is an exact integer equal
to its length. Each row has exactly path/bytes/sha256/data_base64, with exact
str path and encoded data, positive bounded int bytes, and the hash syntax above.

Only UPLOAD/upload_result.json, CAPTURE/capture_result.json and the twelve
fixed SRAM paths are allowed. Compare complete literal paths. Reject duplicates
before inserting any dict entry, including two identical paths; never strip a
path to its basename or normalize traversal. Both JSON receipt paths are
required. Other saved flash, partial-child or old previous files are not valid
interpreter windows; their original evidence remains separately retained.

For each admitted file, validate strict canonical base64 (decode with validation
and require re-encoding to reproduce the string), exact decoded length and hash.
The enclosing packet bound limits these reads; a reported file size cannot
exceed1048576. Retain the original packet outside the result; verified_files
contains path/bytes/sha256 references to that packet, not rewritten payloads.

Parse and retain upload_result and capture_result independently as soon as their
verified JSON bytes have been parsed. Retain the parsed value even if a later
shape/identity check rejects it. Both receipts use the fixed run_id and source.
Their schemas are app-motor-settle-upload-result-v1 and
app-motor-settle-capture-result-v1.

Upload has exactly attempts, finished_monotonic, finished_utc, first_error,
postcheck_errors, run_id, schema, source_sha256, started_monotonic, started_utc,
status, stderr, stdout, subprocess. Require attempts1, status UPLOADED,
first_error null, empty postcheck_errors, string stdout/stderr, and exact
subprocess {reaped:true, returncode:0, timed_out:false}, with exact types.
The captured decoder scope assumes this successful upload receipt; an absent
capture following failed upload is separate retained evidence, not a partial
SRAM capture to fabricate. UTC fields are nonempty strings preserved without
clock conversion. Monotonic fields are finite int/float excluding bool, finish
at least start; they do not prove wall-clock accuracy.

Capture has exactly analysis, counts, finished_monotonic, finished_utc,
first_error, postcheck_errors, reads, run_id, schema, source_sha256,
started_monotonic, started_utc, status, wait. analysis has exactly coherence,
flash, pre_sample_wait, schema, snapshots; schema is
app-motor-settle-capture-analysis-v1 and coherence is UNPROVEN. flash has exactly
before_loader/before_sketch/after_loader/after_sketch with actual bool values.
counts has exactly commands/reads/requested_bytes, all nonnegative exact ints.
reads and snapshots are lists. Each row has exactly name/address/bytes/sha256/
file, with name and file exact str, address/bytes exact int and hash syntax above.

Capture first_error is null or exactly {type,message}, both strings with nonempty
type. Each postcheck_errors row has exactly {check,type,message}, all strings,
with nonempty check/type. Preserve every row in original order. Capture UTC and
monotonic fields use the upload rules. A null or malformed final timestamp in
this saved final receipt is a format failure; it is not filled from the laptop.
The inherited timestamp guard retains its latest valid monotonic value on clock
failure and records that failure rather than manufacturing a later timestamp.

Let R=counts.reads and C=counts.commands. Require0<=R<=C<=26, C either R or R+1,
reads exactly the ordered PLAN[:R] tuples, and
requested_bytes=sum(size for PLAN[:C]). Require each file name to equal its
fixed indexed basename and every hash to have valid syntax. A failed attempted
child may increment C without entering reads. No gap, reorder, duplicate or
raw body from that failed child is promoted to a successful read.
snapshots must equal, field-for-field and in order, the SRAM read-row copies
whose PLAN indices are7..18. The saved file set must be exactly the two receipts
plus these snapshot paths. A declared snapshot missing its body rejects; a
never-read tail is handled by the partial rule. For every snapshot, file-row
bytes/hash and actual decoded body must agree with its read/snapshot metadata
and current mapped address/width. A matching digest alone does not repair an
incorrect address, name, type or byte extent.

Wait records are null or exactly {requested_seconds,before,after}. Nonnull pre
wait has requested_seconds30; separation wait has2 (exact ints). before is finite
numeric excluding bool; after may be null for a failed wait or finite and at
least before. Both finite values must lie within capture start/finish. No
duration is inferred when after is null. If R<7, pre wait must be null; if C>7,
pre wait must be nonnull/completed with after-before>=30. If R<13, separation
wait must be null; if C>13, separation wait must be completed with duration>=2.
Whenever both records exist, pre.after if finite must not exceed wait.before.
At the boundary R=C=7 or13, retain a null, incomplete or completed wait, including
a too-short failed wait, without inventing a subsequent read.

Flash comparison boundaries are4,6,20,25. A true flag requires its boundary read
to exist (R>index). If C>index+1, that comparison must have passed before any
later command, so its flag must be true. At the boundary a false flag may describe
a failed comparison or a failure before comparison; it is retained. Flash bytes
are not in this saved packet, so the interpreter never claims to recompute the
whole flash comparison from chunk digests alone.

Complete format admission requires status COLLECTED, R=C=26, total727432,
all12 snapshots/14 saved files, all four flash flags true, first_error null,
empty postcheck_errors, both completed waits in order, and elapsed capture time
less than600 seconds. Before/after hashes for every corresponding flash chunk
must agree. These checks establish a consistent saved representation only.

Partial admission requires status FAILED with a nonnull first_error, the same
fixed prefix/count/file linkage, and0..12 snapshots/2+N saved files. It may retain
all12 snapshots when later flash comparison or final postcheck failed; FAILED
is never upgraded because all windows exist or repeat. Preserve differing flash
hashes and failure records in such a valid failed representation. A failed
receipt need not satisfy the600-second success budget or successful wait
durations before an unattempted next read. Unknown status or a claimed complete
receipt missing evidence rejects rather than silently becoming PARTIAL.

## Deterministic decode result and errors

The result has exactly schema, status, retrieval_sha256, field_map_sha256,
coherence, upload_result, capture_result, decode_first_error, verified_files,
windows, settle_annotations and repeated_fields_equal. schema is
motor-settle-observed-fields-v1. status is DECODED, PARTIAL or REJECTED; DECODED
is format status only, even if semantic annotations are INCONCLUSIVE.
coherence is always UNPROVEN. No PASS, runtime-qualified or WCET result exists.
upload_result/capture_result are fresh deep copies of their parsed original
receipts when available, otherwise null. Their first_error/postcheck/loss fields
are never edited, replaced or folded into the decoder error.

verified_files is an ordered list of verified path/bytes/sha256 dicts. windows
maps successfully decoded snapshot names to full selected-field dicts;
settle_annotations has corresponding first.settle/second.settle entries only
when those windows decoded. repeated_fields_equal has exactly the six base
window names; each value is equality of decoded selected fields if both first
and second decoded, otherwise null. Equality never changes coherence or proves
publication atomicity, completed history or capture success.

decode_first_error is null for DECODED/PARTIAL, otherwise exactly {stage,code,path}
for the first format/data error. It contains stable strings, not a stack trace,
clock value or platform-dependent native exception text. Retain already verified
file references, parsed receipts and prior successfully decoded windows on
REJECTED. Stop interpretation at that first failure; do not repair, skip an
invalid window or fill an unread window. Original packet bytes remain untouched.

Check in this deterministic order:

1. Python argument types (packet then map for interpret; kind/body/map for
   decode), map bound/exact pin/strict JSON, then packet bound/strict JSON.
2. Packet key set, status, before/after identities, file count and closing count;
   then file-row metadata/allowed full paths/duplicate paths in input row order,
   and presence of both required JSON receipts.
3. Verify/decode/parse upload JSON, then capture JSON, appending each successful
   verified file reference immediately; retain each parsed receipt immediately.
   Then validate receipt key sets; value types in the listed top-level field
   order (nested schemas in their listed order); schema/run/source identities;
   upload success conditions, error shapes and clocks; capture error shapes
   and clocks; capture counts/read prefix, snapshot equality, expected saved
   file set, waits, flash flags and finally complete/partial status conditions.
   Type checks do not perform clock/range/status predicates early. Use the code
   for that later predicate, so malformed counts use COUNTS, wait conditions
   use WAIT, and a claimed COLLECTED/FAILED status contradiction uses STATUS.
4. Verify snapshot bodies in fixed PLAN order, checking base64/size/hash then
   read/file linkage and decoding by ascending field offset/name. Append the
   verified file reference before field decoding. On a SETTLE window, annotate
   only after successful complete28-byte structural decode.
5. Compute available equality indicators and final status. A semantic issue is
   not a new decode_first_error and does not erase decoded fields.

Stable stage/code vocabulary (code checks within a row follow the order shown):

| Stage | Codes |
|---|---|
| layout | ARG_TYPE, MAP_SIZE, MAP_HASH, JSON, SHAPE |
| packet | ARG_TYPE, PACKET_SIZE, JSON, KEYS, STATUS, IDENTITY, FILE_COUNT, CLOSURE_COUNT |
| files | ROW_KEYS, ROW_TYPE, PATH, DUPLICATE_FILE, MISSING_FILE, BASE64, FILE_SIZE, FILE_HASH, FILE_SET |
| upload | JSON, KEYS, TYPE, IDENTITY, STATUS, ERROR_SHAPE, CLOCK |
| capture | JSON, KEYS, TYPE, IDENTITY, STATUS, ERROR_SHAPE, CLOCK, COUNTS, READ_PLAN, SNAPSHOTS, WAIT, FLASH |
| window | ARG_TYPE, UNKNOWN_TYPE, BODY_SIZE, FIELD_MAP, INVALID_BOOL, NONFINITE_F32 |
| annotation | ARG_TYPE, SHAPE |

JSON means any strict UTF-8/JSON parse failure, including duplicate keys and
nonfinite constants; no separate parser-specific code is needed. A file metadata
path uses `/files/INDEX/FIELD`; missing/extra files use their complete required
path. Receipt paths use `/upload_result/...` or `/capture_result/...`; snapshot
field errors use `/windows/first.NAME/FIELD/...`. Standalone decode uses `/`
followed by the selected field path. Structural annotation argument errors are
programmer/fixture misuse; correctly decoded28-byte samples do not raise them.

## Numeric-preserving SETTLE annotations

The observed enum numbers are NONE0, SUCCESS1, NULL_CONTEXT2, PRECONDITION3,
INITIAL_BANK4, POLL_DEADLINE5, POLL_BANK6, FINAL_DEADLINE7 and POLL_LIMIT8.
Elapsed-valid1, poll-valid2, fresh-valid4 and allowed-mask7 are pinned source
semantics, not GDB-observed constants. The150us threshold and4096-poll limit
describe the existing compiled source, not new settings or measured guarantees.

annotate_settle returns exactly raw, current, first_failure, issues and status.
raw is a fresh full numeric report copy. Each sample annotation has exactly
presence, reason_label, available and status. presence is ABSENT for0, PRESENT
for1, UNKNOWN otherwise; reason_label is the known enum name or null, without
changing the numeric reason in raw. available has exactly elapsed_us, poll_index
and fresh_mask. For presence0 all are false. For invalid presence all are null;
validity bits cannot create availability. For presence1 each is the bool of its
encoded validity bit, explicitly an encoding annotation rather than proof of
coherent measurement. Preserve the complete valid/fresh/reserved bytes in raw.

A presence0 sample is always UNAVAILABLE, even when its payload is nonzero.
Do not require zero payload, validate its branch predicates, or label it a
failure: capture may precede presence publication. Presence-invalid samples
are INCONCLUSIVE with no branch predicates inferred. For PRESENT samples use
the following completed-source predicates, only checking a measured scalar's
range when its corresponding validity bit is set:

| Reason | Expected valid | Elapsed condition | Poll condition | Fresh condition |
|---|---:|---|---|---|
| NULL_CONTEXT/PRECONDITION/INITIAL_BANK | 0 | stored0 (unavailable) | stored0 (unavailable) | stored0 (unavailable) |
| SUCCESS | 7 | <150 | <=4095 | 7 |
| POLL_DEADLINE | 7 | >=150 | <=4095 | <7; poll0 with both relevant bits valid requires fresh0 |
| POLL_BANK | 7 | <150 | <=4095 | <=7 |
| FINAL_DEADLINE | 7 | >=150 | <=4095 | 7 |
| POLL_LIMIT | 7 | <150 | exactly4095 | <7 |

The early-reason zero checks describe source-written literals, not observations
of zero duration/poll/freshness. A zero with clear valid bit remains unavailable.
POLL_BANK/POLL_LIMIT elapsed values are earlier loop-top observations; they are
not whole-call or return durations. Treat uint32 elapsed as the already-computed
unsigned subtraction, including wrap, without reconstructing a second duration.

issues is one ordered list of {code,path} dicts. Check has_current then
has_failure for NON_BINARY_PRESENCE; report reserved indices0,1 for
NONZERO_RESERVED; then current and first_failure in that order. For each PRESENT
sample check reserved (NONZERO_RESERVED), valid high bits (UNKNOWN_VALID_BITS),
fresh high bits (UNKNOWN_FRESH_BITS), unknown reason (UNKNOWN_REASON), NONE
(PRESENT_NONE), expected valid mask (VALID_MASK_MISMATCH), early-reason scalar
literals in elapsed/poll/fresh order (EARLY_NONZERO), then the corresponding
valid scalar branch predicates in that order (ELAPSED_CONDITION, POLL_CONDITION,
FRESH_CONDITION). For a present first_failure with NONE or SUCCESS, append
FIRST_FAILURE_NOT_FAILURE after those sample checks. Unknown/NONE reasons have
no invented expected mask or branch range. Absent/unknown-presence samples
retain payload numbers without running these PRESENT-only predicates.

Finally check report relationships in this order: has_failure1 with
has_current0 produces FLAG_RELATION at `/has_current`; a PRESENT current with
a known failure reason2..8 and has_failure0 produces FLAG_RELATION at
`/has_failure`. Such issues describe an inconclusive non-atomic observation,
not proof of a firmware defect. Later current SUCCESS with an earlier present
first_failure is valid and never clears or replaces that first failure.

A PRESENT sample is CONSISTENT if its sample checks have no issue, otherwise
INCONCLUSIVE. UNKNOWN presence is INCONCLUSIVE and ABSENT is always UNAVAILABLE.
Report status is INCONCLUSIVE if any issue exists or either presence is UNKNOWN;
otherwise UNAVAILABLE if both are ABSENT, otherwise CONSISTENT. Full-report
reserved nonzero therefore makes the report INCONCLUSIVE without changing an
absent sample's UNAVAILABLE status. CONSISTENT describes only these source
predicates; it never changes coherence. Issue paths are `/has_current`,
`/reserved/INDEX`, `/current/FIELD` or `/first_failure/FIELD` as appropriate.

Do not match the lifetime first failure automatically to an outer trace record,
token, epoch, APPLY or final HALT. This report has none of those identifiers.
Do not interpret unknown enum bytes as SUCCESS, discard nonzero reserved bytes,
coerce u8 presence to bool, mask off unknown bits or infer a physical cause.
The instrumented image's observations do not establish production timing/WCET.

## Fixed offline main and output ownership

main requires Python-B before any input/output work and argv of exactly two
exact strings: `['--packet-sha256', '<64 lowercase hex>']`. Reject every other
shape, option, uppercase hash, arbitrary path or missing-B call before reads.
There is no board, source, type, address, output or repair CLI.

Read only RAW/retrieved_inert_run01/0001-read-saved-results/stdout and the fixed
map path. Bound reads to limit+1 bytes and reject oversize before parsing; do
not read an unlimited file and check its size afterward. Read each once into
immutable bytes. Validate the expected packet SHA against that bounded buffer
before invoking interpret; mismatch raises ValueError(`packet`,`PACKET_HASH`,
`/`) and creates no output. This main-only code supplements the pure code table.
Map admission uses the constant exact pin above. No source file changes after
capture are necessary to supply a newly observed packet hash.

After interpret returns, create only
RAW/retrieved_inert_run01/decoded.json using exclusive creation; never overwrite
or remove an existing result. Write JSON with allow_nan=False, sorted keys,
indent2 and final LF, preserving the original raw packet and receipts. An
existing result or filesystem error propagates; no cleanup/retry is attempted.
main returns0 for DECODED,1 for PARTIAL and2 for REJECTED. These exit codes do not
adopt or qualify a native run. A small stdout receipt may contain only result
path, status and output SHA256; it must not replace the stored result. Invalid
CLI/-B calls raise ValueError with (`main`,`CLI` or `BYTECODE`,`/`) before I/O.

## Independent oracle obligations and boundaries

Freeze a new oracle and its input pins before its author reads new interpreter
implementation. Synthetic bytes must independently demonstrate little-endian
widths, exact bodies, all115 selected fields, fixed aliases,64 trace slots,
u8[2], nested pre-abort PreviousTick retention, u64/uint32 maxima, finite f32 and
nonfinite refusal, strict bool0/1, immutable inputs/results, and no implicit
whole-history or coherence inference.

Cover every reason,149/150/151 boundaries, poll4095/4096, wrap-valued elapsed,
zero-validity versus measured zero, independent current/first_failure, later
current success, NONE before any publication, absent nonzero payload,
invalid presence with valid bits set, unknown reason/masks/reserved bytes,
ordered issue codes and every report-status distinction. Assert source-only
validity provenance separately from observed enum/layout metadata.

Packet fixtures must exercise exact full-path identities and same-basename
collisions, duplicate JSON/file/snapshot rows, unexpected/missing names, bool
metadata, malformed/noncanonical base64, length/hash mismatches, stale source/
run/map/window addresses, short/trailing bodies, fixed read order, C=R and R+1
partial prefixes, exact requested-byte sums, declared missing bodies versus
unread tails, failed waits, zero-window failure, full-window final failure,
complete success requirements, raw/parsed receipt preservation, equality nulls
and deterministic first-error retention. Test main's bounded one-time reads,
packet hash admission, no-I/O invalid CLI/-B behavior, and exclusive output.
No fixture may execute actual cleanup, credential, transport or device work.

Preserve first host failures; do not weaken an assertion to fit an implementation.
Root freezes source/oracle/review before serial Linux/Windows first execution.
The old one-off D195 decoder has no claimed independent suite; these are new
decoder checks, not an invented historical pass count. Actual native entry
review, capture admission/results and independent actual-byte interpretation
remain separately required. This offline task creates no physical acceptance,
motor-run permission, phase gate, runtime success or safety qualification.

## Pre-implementation error-code clarification

This narrows error classification only; all acceptance predicates above remain.
It was settled before the independent decoder oracle freeze or source execution.

- File-row metadata requires an exact int in1..1048576 and syntactically valid
  lowercase hash. Type, range or hash-syntax failure is files/ROW_TYPE at
  /files/INDEX/bytes or /sha256. After base64 decoding, length disagreement is
  FILE_SIZE and digest disagreement is FILE_HASH at that file-row field.
- Receipt root or named analysis/counts/flash/subprocess object with a wrong
  container type uses that receipt stage's TYPE at the object path. A dict with
  a missing/extra fixed key uses KEYS at the object path. Wait records and error
  records are the expressly separate exceptions below.
- A receipt first_error that is neither null nor a dict uses TYPE at
  /RECEIPT/first_error. A dict with incorrect keys or nested field types uses
  ERROR_SHAPE there or at its offending field. postcheck_errors not a list uses
  TYPE at that field; an invalid list entry (including a non-dict) uses
  ERROR_SHAPE at its indexed entry/field. A structurally valid nonnull upload
  error or nonempty upload postcheck list fails STATUS at the relevant field.
- A correctly typed upload attempts value other than1 uses STATUS at
  /upload_result/attempts. Correctly typed subprocess values differing from
  reaped=true, returncode=0 or timed_out=false use STATUS at the offending nested
  field; wrong Python types use TYPE. Run/source/schema string mismatches use
  IDENTITY; a status literal mismatch uses STATUS. Clock representation/range
  checks use CLOCK, including null, bool, nonfinite or empty UTC clock fields.
- Validate the complete wait/pre_sample_wait record in the late WAIT phase.
  Every wrong container, key set, scalar type, numeric bound/order or required
  duration uses capture/WAIT at the record or offending field path. A missing
  wait member within the outer capture/analysis object still fails its outer
  KEYS check. This retains null/partial boundary waits without reading ahead.
- Missing declared snapshot bodies use files/MISSING_FILE at the full required
  path, checked in fixed expected order. An otherwise allowed saved SRAM path
  outside the declared snapshot set uses files/FILE_SET at that extra full path,
  checked in input row order. Unknown full paths fail the earlier PATH check.
  Both JSON receipts remain required in upload-then-capture order.

No test should infer a new native status, rewrite a receipt or relax malformed
input because two rejection codes were previously plausible. Public paths not
further constrained above remain slash-separated and deterministic as specified.
