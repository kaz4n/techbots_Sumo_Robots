# D218 fixed B4 retained-recorder capture and local completion

This D051 engineering scope provides a capture-only component for an explicitly
qualified caller and a pure local capture-to-CSV component. It does not provide
upload, transport, a run launcher, motor permission, or physical qualification.
The currently loaded ordinary application must fail the B4 flash comparison
before the first SRAM read. Loading B4 M0 remains separate work.

## 1. Fixed inputs and ownership

Normative data is `P7_b4_recorder_capture_raw/plan01.json`. Its fixed bindings,
ordered read plan, dependency byte pins, D215 layout identity and D216 decoder
identity are part of this contract. There is one profile and one prospective
exclusive remote owner:
`/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01`.
No existing owner is reused or created during preparation.

Firmware source is 9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a,
ordinary app.ino, default startup, static linkage, MATCH=0, MOTORS_ALLOWED=0,
SUMOX_B4_STAND=1, and every other commissioning/probe macro zero. The fixed B4
flat sketch is 82912 bytes, SHA256
84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28.
D215 observed recorder::AttemptRecorder is 159200 bytes at 536954120.
No diagnostic Runner, freeze or terminal-state assumption applies.

## 2. Native public API and inherited boundary

`tools/b4_recorder_capture.py` exposes:
- `load_dependencies(sources)`: exact dict with exact str keys helper, capture,
  p0 and exact bytes values. Check all three declared sizes and hashes before
  executing any source privately. Return a namespace of the three modules.
  The caller supplies source snapshots; no source-data rereads or upload module.
- `fixed_bindings()`: detached JSON-compatible copy of the fixed binding.
- `read_plan()`: fixed tuple of (name, address, bytes) triples.
- `collect(dependencies, *, bindings, fs_root=Path('/'), executor=None,
  clock=None)`: invoke the accepted support._collect around a subclass of its
  Capture, with p0.loader_image. No sleeper or configurable run/profile/map.

Bindings have exactly schema, run_id, source_sha256, boot_id, uid, output, files,
loader_image. All nested keys, exact scalar types, paths, byte lengths and hashes
must equal plan01.json. Bool does not substitute for integer. Require Python -B.
Only Capture.profile_bindings, prepare_plan, gather and complete are overridden.
All other inherited Capture functions and support._collect are untouched source.
The helper, capture support and p0 input bytes are pinned exactly.

Inherited admission verifies board identity, five file bytes, derived loader,
process conflicts and output absence. Inherited exclusive directory/file writes,
before-command intent, bounded child execution, raw/receipt preservation, first
error, all final checks, fsync and descriptor closing remain unchanged. Capture
returns only after _collect's finally closes descriptors; an exception there
is not a successful return even if capture_result.json was already written.
The qualified caller must also close its own staged inputs before constructing
a successful returned envelope. No synthetic upload result is permitted.

## 3. Fixed passive reads and partial preservation

The plan has exactly 26 reads and 852624 requested bytes:
five before-loader chunks, two before-sketch chunks, before.lifecycle,
ten owner chunks, after.lifecycle, two after-sketch chunks and five after-loader
chunks. Flash chunk ceiling is 65536 bytes. Owner chunk ceiling is 16384 bytes:
nine full chunks and an 11744-byte tail. SRAM consists of twelve reads, 159440
bytes. Each read address is divisible by four and each SRAM range must pass
the unchanged p0.ram_range; lengths need not be divisible by four.

Compare complete flash image bytes after indices 4, 6, 20 and 25, against the
admitted loader and B4 sketch references. Both initial comparisons must pass
before SRAM index 7. No wait, sleep, polling, reset, halt, inferior call or
MCU write is introduced. MEM-AP-only config and all five file pins stay fixed.
Native report wait is None. Existing 600-second collection, 30-second child and
1-MiB stream limits remain; a future qualified outer caller retains 630 seconds.

The lifecycle bracket is 120 bytes at 537113200, inside the recorder owner's
last 120 bytes. Decode only epoch_token (offset 0, unsigned little-endian 8),
last_frame_token (offset 8, unsigned little-endian 8), and phase (offset 113,
unsigned byte). The same fields in the assembled owner use offset 159080.
Unknown phase values stay numeric. Other bracket bytes are raw only.
Observe before/body/after separately and publish per-field equalities for
before_body, body_after and before_after. Equality is not atomicity or common
attempt evidence. No phase causes sampling to terminate early.

Update analysis after every attempted read, including failure. Incomplete raw
files and command/result receipts are never removed, padded, decoded or described
as complete. The native analysis has exactly schema, flash, owner, lifecycle,
equalities and coherence:
- schema: b4-recorder-capture-analysis-v1; coherence: UNPROVEN.
- flash: four exact bool keys before_loader, before_sketch, after_loader,
  after_sketch, initially false.
- owner: None until all ten owner samples exist, then exactly address, bytes,
  sha256, chunks (536954120,159200,aggregate digest,10).
- lifecycle: exactly before, body, after, each None or a three-key integer dict
  epoch_token, last_frame_token, phase.
- equalities: exactly before_body, body_after, before_after, each None unless
  both observations exist, otherwise the same three keys with bool values.
A complete native result requires all four flash flags true, all 26 successful
reads/counts and complete owner/lifecycle/equalities. Inherited finalize still
requires no first error and successful closing checks before COLLECTED.

## 4. Pure local API, bounds and structural success

`tools/decode_b4_capture.py` exposes
`decode_capture(returned_raw: bytes, *, files: dict[str, bytes],
layout_raw: bytes) -> dict`. It conventionally imports unchanged D216 plus the
native module's pure constants/helpers; it never loads native dependencies or
calls collect. The native payload has no dependency on the repository tools
package or D216. Neither local decode nor dependency lookup performs source I/O,
writes, subprocess or transport. The caller supplies all evidence bytes.

Before any hash/parse, require exact bytes for returned_raw/layout_raw, exact
dict for files, exact str keys and exact bytes values. Wrong types raise TypeError.
Limits: returned_raw <=65536, layout_raw <=65536, <=13 file entries, each key
<=96 characters, each file <=65536, total file bytes <=262144. Excess raises
ValueError. These programmer/resource errors do not promise a returned copy.
All bounded malformed or partial evidence instead returns REFUSED with copied
raw files, raw reply and raw layout retained. JSON syntax/UTF-8/duplicate keys,
non-finite numbers, too-deep nesting and standard parser exceptions are refusals.
No arbitrary configured limits or wider transport cap.

Complete files are exactly these thirteen basenames:
capture_result.json; 07-before.lifecycle.bin; 08-owner.0.bin through
17-owner.9.bin; 18-after.lifecycle.bin. Unknown/missing leaves refuse.
The exact returned envelope keys are schema, action, run_id, source_sha256,
report, report_origin, remote_result_path, full_result_bytes,
full_result_sha256, first_error, postcheck_errors. Require schema
b4-recorder-action-v1, action capture, fixed run/source,
report_origin returned, fixed output/capture_result.json, first_error None,
postcheck_errors [], and the actual durable report length/hash. The embedded
report must equal the parsed durable report with exact JSON value types.
A durable_unattributed result is always refused.

The exact native report keys are schema, run_id, source_sha256, status, counts,
started_utc, finished_utc, started_monotonic, finished_monotonic, wait, reads,
first_error, postcheck_errors, analysis. Require the fixed result schema
b4-recorder-capture-result-v1, fixed run/source, COLLECTED, first_error None,
postcheck_errors [], wait None, finite exact int/float monotonic timestamps
with 0 <= finished-started <600, nonempty parseable timezone-aware ISO UTC
timestamp strings ordered start <= finish, and exact integer counts
commands=26, reads=26, requested_bytes=852624. Bool timestamps/counts refuse.

Each read record has exactly name,address,bytes,sha256,file: exact strings and
exact nonnegative integers, lowercase 64-hex hash, exact ordered plan identity
and '{index:02d}-{name}.bin'. Every SRAM file length/hash must match its record.
All before/after flash per-chunk hashes must agree and all four native flash
flags must be true. These supplied hashes/flags are qualified structural
evidence, not independently retrieved complete flash bytes or hardware proof.

Assemble only the ten verified owner chunks in ordinal order. Recompute owner
digest and all lifecycle/equality fields from supplied bytes and require exact
native analysis equality, including exact bool/integer types. Require exact
D216 layout byte hash before decoding. No unused bracket fields are interpreted.
Call unchanged D216 only after this complete successful bundle validation;
D216 export/format/consistency/loss/lifecycle/provenance remain distinct.
D216 export refusal is retained as a nested decoder result and does not turn a
structurally valid capture into a capture-bundle failure.

## 5. Local report and refusal order

Return exactly schema, bundle_status, errors, raw_returned, returned_sha256,
raw_layout, layout_sha256, raw_files, file_hashes, raw_owner, analysis, decoder,
coherence, body_origin, common_attempt_verified, transport_verified,
hardware_acceptance. Schema is b4-recorder-capture-decode-v1; status PASS or REFUSED.
errors is a list of {code,message}; it is empty for PASS. The raw-files dict is
a new container and bytes are immutable; caller mutation cannot remove retained
entries. file_hashes maps each supplied basename to its SHA256. raw_owner is
None until all owner leaves pass length/hash checks, then exact concatenated
bytes; analysis and decoder are None until their respective checks succeed.

Refuse first at the relevant ordered boundary: JSON parsing (INPUT_JSON),
envelope schema/identity/closure (ENVELOPE), exact file selection (FILES),
durable report bytes/schema/timestamps/counts/embedded equality (REPORT),
ordered read records and SRAM bytes (READS), flash flags/per-chunk agreement
(FLASH), recomputed analysis (ANALYSIS), exact layout binding (LAYOUT).
Any standard parsing recursion/type/value/overflow failure is returned as
a bounded refusal, never an uncaught JSON-depth exception.
Only successful structural completion invokes D216. Nested decoder CSV outputs
are the sole CSV outputs; no output files are written.

Always coherence=UNPROVEN, body_origin=UNPROVEN and all three booleans
common_attempt_verified, transport_verified, hardware_acceptance=false.
The local function cannot authenticate who supplied a report. Successful local
hashes, returned-close metadata, equal lifecycle fields, sealed state or
incomplete=false cannot establish hardware origin, stable terminal state,
atomicity, motor behavior, WCET, physical acceptance or any phase gate.

## 6. Independent evidence and limits

Independent focused fixtures are authored before reading new implementation.
They cover pins/bindings and fixed plan; exact inherited support dependency;
early flash refusal; all26 reads and lifecycle comparisons; partial failure;
successful local assembly and unchanged D216 export; corrupt/missing/extra
files/records, closure/durable-only/flash mismatch, bounds/types/deep JSON and
raw preservation. No repeated inherited lifecycle campaign is needed when the
dependency bodies are byte-identical. Root schedules first host tests; workers
do not execute subjects or tests. Record actual compact 26-read report/envelope
fixture byte sizes below the unchanged 65536 cap, rather than assuming fit.

This component does not itself qualify the caller, stage or retrieve evidence,
load B4, run the board, clear faults, or prove a finished recording. Qualified
caller/native integration is later work. D215/D216 and all older code remain
unchanged. The derivation records exact dependency/input bytes and the bounded
new hook/host behavior; generated preparation files are not target observations.
