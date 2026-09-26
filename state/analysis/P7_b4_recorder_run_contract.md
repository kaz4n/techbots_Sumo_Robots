# D219 fixed B4 recorder capture-only caller

D051 authorizes this bounded software integration. This contract adds no upload,
reset, halt, MCU write, privileged cleanup, motor permission or new firmware.
The current ordinary MCU image is expected to refuse before SRAM. D218 FINAL
review and accepted D214/D215/D216/D217 evidence are required before this caller
or its independent oracle is finally sealed. Native execution is separate.

## Public interface and fixed owners

New files are tools/capture_b4_recorder.py, this contract, and
state/analysis/P7_b4_recorder_run_raw/actions.py, preparation.json and derivation
receipts. Old sources remain immutable.
The caller exposes CaptureRun(reviewed_head, *, root=None), admit(), run() and
main(argv=None). CLI requires exactly one --check-only or --execute and
--reviewed-head with forty lowercase hex digits. Check-only performs local
admission; it creates no local/remote owner and makes no native call.

RUN_ID remains D218's b4-recorder-9044ebbb-capture01. Remote capture owner is
/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01.
Fresh staged-adapter owner appends -adapter, with leaf remote.py containing the
exact accepted tools/b4_recorder_capture.py bytes. Neither owner is reused.
Local exclusive owner is P7_b4_recorder_run_raw/native_capture01; scope is
P7_b4_recorder_run_raw/capture01_scope.json. No /tmp/remoteocd, root or sudo.

The scope has exact keys schema, run_id, board, source_sha256, expected_identity,
files; schema b4-recorder-native-scope-v1, board2629958581, source9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
Its closed files set is the caller, actions, preparation, contract, derivation,
independent test, oracle and final run review listed in plan01.json.
The root creates/commits this admission scope after host review. No fabricated
review or scope is emitted by the caller.

## Local admission and inherited machinery

Privately load the pinned accepted D212 caller and its pinned ancestors; retain
the accepted local ownership, checked ADB, head/scope/input checks, command
receipts, transport execution, timeout, first-error and closing mechanics.
The derivation lists exact unchanged functions and narrow metadata bindings.
No old caller is executed and no old consumed owner is reused.

Bind current B4 compile source manifest (130 pinned inputs), same ordinary
source mapping and source digest, current artifact/ABI/entry results and actual
reviews, D216 exact layout/decoder and D218 source/contract/plan/final review.
Preparation has exactly schema, run_id, source_sha256, bindings, files;
schema b4-recorder-run-preparation-v1, bindings exactly {capture: D218 binding}.
files is a closed provenance pin map of {bytes,sha256}. No caller-supplied
profile, source digest, read plan, mode, motor flag or alternative layout.

Require Python -B at startup and currently, a clean reviewed HEAD including the
scope, all source/dependency bytes unchanged, exact ADB executable/serial and
the bound UID1000 board identity/boot. Reject unrelated untracked files; only
the exclusive local result owner is allowed after claim. Retain current-source
inventory and staged-source capability checks. No source or tool mutation.

## Commands, staging and sequence

actions.py exposes:
- build_capture_command(sources, bindings): exact dict helper/support raw byte
  roles and exact D218 capture binding; returns fixed isolated Python argv.
- build_retrieval_command(helper_raw, expected_identity): exact pinned helper
  bytes and fixed identity; returns fixed read-only isolated Python argv.
- validate_capture_reply(reply): validate a complete successful returned capture
  before retrieval; ValueError on refusal, return the input report on success.
- decode_retrieval(packet, *, returned_raw, layout_raw): validate the fixed
  retrieval packet and call unchanged D218 decode_capture; return its report.

Use the accepted canonical JSON, bounded single-member BZ2 and canonical
base64/base85 framing. Payload <=196608 bytes; full Windows native argv <=30000
UTF-16 units including NUL; capture returned envelope <=65536. Validate all
inline helper/support pins before executing those bytes. The accepted action
bootstrap guards and closing helpers remain unchanged except explicit
capture-only selections and current metadata. No upload role or branch.

Stage the adapter with the D212 exclusive UID1000 directory claim then one
checked ADB push. Require durable local staging intent, checked claim identity
and absence, one dispatch per stage step, stable local inputs/output and exact
remote adapter bytes before use. Inline helper/support; obtain p0_capture.py
from the accepted installed path
/home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/p0_capture.py
through the unchanged descriptor reader with exact18880-byte/885c4e42... pin.
Pass its raw bytes as D218's third source snapshot.

Open one bootstrap root descriptor. Check adapter and installed p0 before
calling D218 collect; finally independently recheck both and close root,
retaining the earliest error. report_origin becomes returned only if collect
returned after its inherited descriptor closing. Closing errors still make
the envelope unsuccessful. A durable-only fallback uses durable_unattributed
and can never authorize retrieval/decode success.

The successful command schedule is exactly ten calls:
adapter-claim, adapter-push; first CLI-initialization, CLI-builtin-files and
capabilities observations; capture; retrieve; final same three observations.
Each stage/capture/retrieve command is at most once, each prerequisite at most
twice, total at most10. Stage/read-only commands keep60s, capture630s. Fixed
allowlist is prepared before dispatch and sealed in local input state.
Retrieval has a predeclared fixed program, not a later arbitrary command.

After staging, perform local checks and all prerequisites, durably record the
capture intent, consume it once and call capture. There is no upload predecessor,
upload receipt or upload counter. Preserve the full envelope/transport streams.
Validate returned success before writing retrieval intent and consuming the
single retrieval call. Always attempt final local/prerequisite checks after a
claimed failure; preserve the original error and append later errors. Failed
staging/capture/retrieval/closing never reaches CSV decoding.
A missing response is uncertainty, not implicit success or a retry license.

## Native envelope, retrieval and completion

Capture envelope schema and exact key/type/closure requirements are D218:
b4-recorder-action-v1, action capture, fixed run/source, report_origin returned,
fixed capture_result path, actual full-result length/hash, no first/postcheck
errors. Require the full fixed COLLECTED report,26reads/852624bytes, no waits,
all four flash checks and fixed typed identities before deriving retrieval
eligibility. A noncurrent sketch fails the D218 flash-before-SRAM boundary.

The predeclared retrieval program reads only capture_result.json plus the
twelve D218 SRAM leaves in their fixed order. It bounds/parses the durable
report, requires complete fixed status/geometry and derives hashes only for
these exact basenames. It uses pinned helper.logical_read, checks every actual
length/hash, rereads all thirteen files with the same pins and checks identity
again before returning. No path supplied in a remote report can extend the
fixed owner/leaf set. Output is bounded by1MiB and60s.

Retrieval packet has exactly status, identity_before, identity_after, files,
closing_file_checks. status is FILE_ONLY_RESULTS_VERIFIED, both exact identities
must equal the bound identity, closing_file_checks is exact integer13.
files is an ordered list of13 records, exactly path,bytes,sha256,data_base64.
Each path must equal the fixed capture owner + expected basename; exact integer
sizes are report<=65536 and each SRAM's declared size, SHA is lowercase64hex,
base64 is canonical. Total decoded files <=262144. Duplicate/extra/missing/
reordered leaves, identity/closure changes, hashes or sizes refuse.
The local helper validates packet geometry and then passes exact returned_raw,
the13 retrieved bytes and the pinned layout bytes into unchanged D218.
Malformed bounded packet data refuses with ValueError before invoking D218;
D218 bounded refusals remain its raw-preserving report and stable error codes.
No evidence is authenticated as hardware merely because metadata matches.

Only after successful native envelope, retrieval and caller closing checks
invoke local completion. Require D218 bundle_status PASS for a completed
sequence. A D216 export REFUSED remains a distinct decoder outcome: preserve
the report and raw inputs and write no CSV; structural capture can still be
COMPLETED. A consistency finding in valid D216 output does not rewrite its CSV
or pretend loss/lifecycle/provenance passed.

Save exact returned envelope and retrieved13leaves under the fresh local
owner using exclusive writes and before/after owner checks. Save frames.csv,
events.csv and summary.csv only when unchanged D216 supplied all three bytes.
Save export.json as JSON-safe interpretation with byte payloads represented
by local-file names/length/hash references; the original bytes remain in
retrieved files/transport receipts. Do not duplicate the assembled159200-byte
owner when its ten exact chunks already preserve it. No overwrite of any leaf.
CSV writes are local evidence production, not native MCU operations.

run() result has schema b4-recorder-sequence-v1, status COMPLETED or FAILED,
capture (returned envelope or None), capture_attempts, retrieval_attempts,
export (JSON-safe local completion or None), first_error, postcheck_errors;
inherited finish adds diagnostics and saves final_checks.json/result.json.
Attempt counts are exact integers0/1. Error records retain the accepted
type/message/chain mechanism; there is no new lossy error-code translation.
Success requires exact10 calls/closed dispatch sets and no diagnostic errors.
Failure preserves all produced files/receipts and has no automatic retries,
deletions or claims about unseen raw data. Remote partial files and command
receipts remain in their unique capture owner even when the local complete
bundle cannot be retrieved; no padding or fabricated tail is permitted.

## Evidence boundary and focused verification

The implementation is sealed before new independent oracle inspection.
Focused host fixtures exercise fixed source/scope admission, command framing
and Windows length, capture-only order and first-error closures, stale/ordinary
bindings, complete/partial envelopes, fixed retrieval descriptors and corrupt
packet refusals, output exclusivity and CSV suppression. Exact inherited-body
proof replaces rerunning all historical suites. Root owns first test execution.

D218 and D216 unknown origin/coherence/common-attempt/transport/hardware flags
remain unchanged. A completed caller is captured structural evidence, not
motor or sensor commissioning, a coherent snapshot, terminal freeze, loaded B4
permission, physical acceptance, timing qualification or a phase pass.

## Accepted dependency and public fixture clarification

D218 FINAL review is accepted: state/reviews/P7_b4_recorder_capture_review.md,
7924 bytes, e598b25b5707c9456cdda4e6d0143b9d3f2a4df66e567770b00926b64826c5e6.
plan02.json supersedes the preserved planning-only plan01.json. Initial contract
bytes are preserved as contract01.md; this clarification changes no native scope.

Both command builders return list[str]. validate_capture_reply takes an exact
dict and returns its report. decode_retrieval takes an exact dict packet plus
exact bytes returned_raw/layout_raw; input-schema refusal is ValueError.
CaptureRun.intent(action, predecessor) accepts only (capture, None).
retrieval_intent(reply) records a fixed intent bound to the actual capture hash;
retrieve() consumes that intent and calls query(retrieve, 1048576) once.
export_bundle(packet, reply) receives the exactdict returned by action/query;
returned_raw is canonical(reply), the same ASCII JSON/newline emitted by the
fixed bootstrap. Original stdout is preserved separately in transport evidence.
Its return equals the JSON-safe value saved in export.json. write_bytes(name,raw)
uses exclusive xb, flush/fsync and before/after output-owner checks.

Focused fixtures may subclass the existing admit/claim/stage/local/prerequisites,
write, action, query and finish seams to observe the actual run method; no
production bypass parameter exists. Real local export can isolate check_output
and local against an owned tempfile while exercising exclusive writes.
The closed scope remains eight files; D218 adapter/layout sources belong to
fixed/provenance inputs in fixed_bytes/fixed_pins, not extra scope keys.

The accepted D212 top-level action import is replaced once by the already
checked new action module before private execution. Named inherited methods
remain unchanged; private metadata constants bind fresh owners/provenance.
Local completion privately checks all four fixed source snapshots before any
execution: validate_csv_bundle, b4_recorder_capture, decode_b4_recorder and
decode_b4_capture. Only their literal from-tools imports resolve to this private
set. No added sys.path or global module-cache mutation is needed.

The compressed retrieval program exposes read_bundle(h,fd) for focused host
fixtures. It uses only h.identity and h.logical_read; globals are EXPECTED,
OUTPUT,RUN_ID,SOURCE,PLAN,COUNTS,REPORT_KEYS plus json/hashlib/base64/re and
require/unique/nonfinite. Success makes27 logical reads: initial report
discovery,13pinned reads,13closing reads, and two identities. Outer code owns
root open/close, preserves the earliest exception and bounds/prints the packet.
