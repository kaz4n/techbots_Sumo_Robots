# D-074 local CSV evidence validation contract - 2026-09-23

Selected under D-051 after the separate read-only bundle_contract_audit. Extend
offline B8 preparation only to checking local evidence files. No board connection,
transport, live owner/cursor, firmware/config change, dump command or phase pass.
Files passing this check are not authentic MCU data, a common attempt, a completed
transport, live IDLE permission, or physical200s/no-gap acceptance.

## Interface and limits

One standard-library Python module tools/validate_csv_bundle.py. Public API:
`validate_bundle(frames_path, events_path, summary_path, manifest_path=None)`
returns the report below. Paths accept str/Path. Input/path/decoding/schema errors
are reported, not uncaught exceptions. Import is quiet. Never import board tools,
read current firmware/config, open sockets, invoke subprocesses or write files.

CLI: `python tools/validate_csv_bundle.py --frames F --events E --summary S
[--manifest M]`. Emit one JSON report to stdout, exit0 iff format_integrity and
consistency both PASS. Missing optional provenance, loss and unfinished lifecycle
alone do not fail local validation. Exit1 for checked-file/schema/consistency/
manifest failures. argparse usage errors exit2; help performs no input reads.
No output/report file option, overwrite or repair mode. JSON keys sorted on CLI.

Read each CSV once in binary, streaming, with maximum16MiB per CSV and at most1023
bytes per physical line including LF. Enforce limit before retaining oversized
data; do not call unbounded read. Hash exactly the bytes read. No source mutation.
Require regular local files; reject directories and symlinks. Use the opened file
descriptor's fstat to check regular type and size; detect size/mtime_ns identity
changes across read as a failure, not a stable hash claim. This is a local snapshot
check, not an atomic three-file snapshot or adversarial filesystem guarantee.
Optional manifest max16384bytes, read once bounded; regular-file rules identical.

## CSV format integrity

Use exact D-07318/7/36-column headers and field order. On disk, persist LF but
omit the in-memory terminating NUL. ASCII only, LF required at every line end;
no CRLF, BOM, blank lines, quotes, whitespace or extra/missing fields. Exactly one
summary data row. Header-only frames/events are allowed. Schema_version exactly1.
Integers are canonical decimal:0 or nonzero-leading positive digits; signed
fields also allow minus followed by nonzero-leading digits. Reject +, -0, leading
zero, exponent, Unicode digits and out-of-range values. Every numeric token is
bounded by its wire width before conversion; no unbounded huge-integer parse.

Frame widths: ordinal u64, pack_status0..2, t_ms u32; state/mode/line_mask/opp_mask
u8; heading_cdeg i32; gyro_z_dps10/ax_mg/ay_mg i16; duty_l_127/duty_r_127 i8
(including-128); vbat_cv u16; flags u8; tick_max_us u16. raw_hex exactly50 lowercase
hex digits. Decode D-073/logframe.h little-endian two's-complement offsets and
compare every payload numeric value to raw bytes; status/ordinal are not encoded.
Event widths: ordinal u64,t_us u32,type/detail u8,value u16,raw_hex16 lowercase
digits. Require exact raw/numeric agreement. Do not validate payload enums/masks,
repair invalid status bytes, sort, deduplicate, unwrap time, constrain ordinal
sequence or check cadence. All caller-chosen u64 ordinals remain valid.

Summary widths: epoch_token,last_frame_token,ticks,overruns u64; release_us and
all counters/counts/tick_max_us u32; mode/phase u8; ten boolean fields exactly0/1
(ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,
go_seen,final_frame_missing,interrupted,terminal_exhausted,event_overflow,incomplete).
Keep all independently supplied values, including unknown mode/phase codes.

## Owner-summary consistency and interpretation

Format-valid files may still describe contradictory metadata. Separate these
consistency failures from formatter/file corruption. When all three formats pass:
- Retained frame/event row counts equal summary.frame_count/event_count.
- Lifetime frame_clamped/frame_invalid each >= retained counts of status1/2.
  With frame_overwritten0 require both equal. If overwrite counter <UINT32_MAX,
  sum of lifetime-minus-retained clamped/invalid counts cannot exceed overwrites.
  Saturated overwrites supply no finite upper bound. No fabricated accepted total.
- Compute detailed_loss as OR of missing_results,rejected_results,identity_rejected,
  malformed_batches,event_semantic_rejected,upstream_event_rejected,
  upstream_event_invalid,source_regressions,skipped_frames,frame_overwritten,
  frame_rejected_status,frame_clamped,frame_invalid,event_rejected,event_overflow,
  ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,
  final_frame_missing,interrupted,terminal_exhausted. In this owner-profile check
  require bool(incomplete)==detailed_loss. Do not include observed_results,
  ticks/overruns/tick_max_us/go_seen. Contradiction is consistency FAIL, while loss
  reporting still ORs detailed_loss, aggregate incomplete and retained bad statuses.
- Do not impose additional owner semantic rules or silently repair snapshots.

Lifecycle codes:0 EMPTY,1/2 UNFINISHED,3 SEALED,4 INTERRUPTED,others UNKNOWN.
This is reported owner state only. SEALED does not prove live IDLE or successful
recording. recording.loss is REPORTED if the above OR is true, otherwise
NONE_REPORTED; if any CSV format fails report UNKNOWN. No result says gap-free.

## Optional caller-declared manifest v1

Strict JSON object, duplicate keys rejected at every level; no extra/missing keys,
NaN/Infinity or bool-as-integer. Top-level exact keys:
schema_version,session_id,origin,firmware_revision,source_sha256,config_sha256,
log_hz,frame_capacity,event_capacity,target,closure,files.
schema_version integer1. Nullable fields (null means unknown): session_id matches
[A-Za-z0-9_.-]{1,96}; origin synthetic|hardware_reported; firmware_revision lowercase
hex40or64; source_sha256/config_sha256 lowercasehex64; log_hz/frame_capacity/
event_capacity integers1..UINT32_MAX; target nonblank printableASCII up to128chars.
closure required unknown|open|closed, describing a caller declaration only.
files has exact frames/events/summary keys, each exactly sha256 (lowerhex64) and
rows (u32). Hashes must match the complete supplied raw CSV bytes and row counts;
summary rows must equal1. Roles bind CLI files, never manifest-supplied paths.
If supplied capacities are nonnull, actual retained counts must not exceed them.
No derived200s/cadence/default-capacity check and no historical-config inference.

Absent manifest is ABSENT with closure UNKNOWN and evidence_kind UNKNOWN.
Valid manifest with any nullable field null is PARTIAL_DECLARATION; otherwise
DECLARED. Invalid manifest is INVALID, consistency FAIL; do not propagate its
provenance/closure assertions as accepted. Valid origin synthetic maps to SYNTHETIC,
hardware_reported to HARDWARE_REPORTED, null to UNKNOWN. Explicit provenance is
still caller-declared: hashes cannot prove authentic firmware or same attempt.

## Report

Always return keys: schema_version1, format_integrity PASS|FAIL,
consistency PASS|FAIL|NOT_CHECKED, errors (list of objects with category,code,message),
files (frames/events/summary -> {sha256,bytes,rows}, or null for invalid file),
recording ({loss,lifecycle,phase_code}; UNKNOWN/UNKNOWN/null on format failure),
provenance ({status,evidence_kind,closure,declared}; declared is accepted manifest
object or null; closure UNKNOWN|DECLARED_OPEN|DECLARED_CLOSED),
common_attempt_verified=false, transport_verified=false, hardware_acceptance=false.

Error category format/consistency/manifest; code uppercase snake-case nonempty,
message nonempty explanatory text. Tests need not prescribe every message/code.
Format failure makes consistency NOT_CHECKED unless a manifest itself fails,
which makes consistency FAIL. A supplied manifest may be structurally validated
but cannot be accepted unless all file hashes/counts are available and match.
Without manifest, consistency PASS requires all CSV formats and crosschecks pass.
Provenance remains DECLARED/PARTIAL if valid even when owner consistency fails;
these are distinct facts. No exceptions for invalid input become success.

## Independent evidence

Coordinator owns contract/decisions/docs/state; worker only validator module;
independent author only new tests/tooling/test_csv_bundle.py (no implementation
reads). Test exact literal fixtures, all ranges/booleans/raw offsets, arbitrary
codes/ordinals/wrap, status lifetime/overwrite/saturation, contradictory summaries,
all phases, malformed/truncated/oversize/changed files, manifest schema/hash/rows/
capacity/null/duplicates/types, CLI exits/import/no writes, and clearly labeled
synthetic200s25Hz/5001frame fixtures plus4096events. Preserve earlier tests/config.
Include a controlled host integration fixture that compiles the actual C++ CSV
formatter against its public header, emits files and validates them; no physical
claim. Independent expectations must not be generated from Python implementation.
Fresh read-only review and full relevant tooling checks precede completion.
