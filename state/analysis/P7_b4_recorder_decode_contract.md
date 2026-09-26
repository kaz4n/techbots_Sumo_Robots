# D216: fixed B4 recorder byte decoding

Scope: one pure host decoder for the accepted D214 B4 app M0 artifact and its fresh D215 observed AttemptRecorder layout. No transport, upload, reset, MCU access, file output, firmware change, motor permission or hardware acceptance follows. The producer of owner bytes remains responsible for their capture and preservation. Layout binding does not prove their origin or coherence.

Public API: decode_recorder(body: bytes, *, layout_raw: bytes) -> dict. Module import uses the existing conventional tools.validate_csv_bundle dependency; the function performs no file, environment, process, clock or network I/O and does not mutate input bytes. Exact bytes types are required before other work; subclasses and other values raise TypeError. Limits are body <= 1,048,576 bytes then layout_raw <= 65,536 bytes; excess raises ValueError before hashing or parsing. For all bounded exact bytes inputs, the result preserves the original body in raw_owner and its SHA-256, even when admission or export is refused.

Only layout01.json (4443 bytes, SHA-256 f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d), transcribed from the fresh D215 observation, is accepted. Tests may replace fixed globals in an isolated loaded module for clearly synthetic fixtures. Production contains no option to trust arbitrary caller-declared layouts. The map binds source, artifacts and D215 ABI bytes, little-endian order, exact owner type/address/extent, three arrays and 35 scalar fields. All offsets are owner-relative and transcribed from fresh full layouts; no old native coordinates or synthetic offsets become production defaults. Map numbers are exact integers, not booleans; fields have explicit offset/bytes/kind. Geometry must fit owner extent, use fixed native widths and nonoverlapping interpreted extents. Scalars are unsigned raw integers or canonical native bool bytes. Native enum contents need not be recognized.

Arrays: frames_.payloads_ has 5001 entries of 25 bytes, frames_.statuses_ has 1251 bytes with four 2-bit physical-slot statuses per byte, events_.events_ has 4096 entries of 8 bytes. The 35 scalar fields are the 25 AttemptSummary leaves, six FrameBuffer indices/counters, three EventBuffer leaves and phase_. Decode only those nine native boolean leaves. highest_token_, stopping_token_, previous_state_ and terminal_seen_ remain uninterpreted raw bytes.

Refusal order is layout identity, map schema/binding/geometry, exact body owner length, all scalar decoding, native bool validation in declared field order, first/frame/event bounds, retained status validation, then CSV formatting validation. All scalar integers are available in native_values before validating booleans, preserving bool value 2 rather than coercing it. Require first_ < 5001, size_ <= 5001 and event size_ <= 4096. Never infer valid retained data from zeroed or stale array contents.

Frame ordinal i reads physical slot (first_ + i) % 5001 and status (statuses_[slot // 4] >> (2 * (slot % 4))) & 3 for i in [0,size_). Status 3 in a retained slot refuses CSV. Unused slots, unused status lanes and stale bytes never cause a refusal. Events use exactly the retained prefix. CSV ordinals start at zero. Preserve every original packed payload byte in raw_hex, including unknown state/mode/event codes and signed duty -128. No repaired, clamped or guessed payload values.

Use the existing unchanged D073/D074 headers, wire structs, field ranges, pure row parser and owner consistency checker. Emit ASCII decimal, lower-case raw hex and LF. Export all three role byte strings only after all rows validate. Their file records contain bytes, rows and SHA-256. Summary has the exact 36 CSV fields: schema_version=1; 34 fields from observed scalars; incomplete=the exact OR of the existing 22 LOSS_FIELDS. Nonterminal lifecycle, go_seen, observed result counts and phase alone do not imply loss. Counter saturation values are retained without attempted repair.

Return the existing D074 format/consistency/errors/files/recording/provenance fields plus schema='b4-recorder-decode-v1', raw_owner, raw_sha256, layout_sha256, layout_binding, export_status, native_values, summary, csv, body_origin='UNPROVEN', coherence='UNPROVEN'. csv is always {frames,events,summary}, all None on any export refusal and all bytes on success. layout_binding is PASS only after map admission and remains separate from body admission. export_status is PASS/REFUSED; format_integrity PASS/FAIL; consistency PASS/FAIL/NOT_CHECKED. errors entries are exactly {category,code,message}. Map/body refusals are admission errors, malformed native bool/index/status are native errors, and inherited owner errors remain consistency errors. Valid CSV stays available even if owner consistency fails.

Decoded phase independently determines recording.phase_code and lifecycle: EMPTY for 0, UNFINISHED for 1/2, SEALED for 3, INTERRUPTED for 4 and UNKNOWN otherwise. loss stays UNKNOWN until a valid summary exists, then follows exact loss fields and inherited retained-status consistency. Summary becomes available after scalar/bool/index validation, before retained-status validation. An invalid native bool leaves summary None; a retained status 3 can therefore retain a valid scalar summary. Never equate SEALED with IDLE, success or completed robot action.

Provenance remains exactly {status:'ABSENT',evidence_kind:'UNKNOWN',closure:'UNKNOWN',declared:None}. common_attempt_verified, transport_verified and hardware_acceptance always remain false. Stable or equal sampled bytes, an ABI map hash or successful CSV parsing cannot establish atomic capture, common attempt, physical origin or hardware qualification.

Focused independent tests cover actual fixed-map binding and altered-map refusal, exact input boundaries/types, all 35 scalar widths/offsets, ring wrap/status lanes/event prefix, literal D073 goldens, unknown payloads and -128, all22 loss terms individually, saturation, nine bool refusals/raw preservation, retained status3 versus unused lanes, lifecycle/loss separation, existing owner consistency findings, strict raw-preserving refusal, and absence of decode-time I/O. No inherited native tool suite is repeated. Source/contract/map/dependency and test identities are recorded before root-controlled first execution.

## Fixed data and interface inventory

The supplied map is `state/analysis/P7_b4_recorder_decode_raw/layout01.json`.
Its separately reviewable transcription receipt is `map_derivation01.json`
(25482 bytes, SHA-256 86ec272d73f5a1243725480e44af4298e718f976cc2ba49b42752fa931d61ac0).
The exact owner is `recorder::AttemptRecorder`, 159200 bytes at 536954120,
alignment 8. Its address is binding metadata only; decoding never reads it.
Every interpreted offset is a directly observed comment in the complete owner
ptype block, independently cross-checked against its standalone parent layout.
This contract does not replace the separate D215 actual review.

Map top-level keys are exactly schema, binding, byte_order, owner, arrays, fields.
schema is b4-recorder-layout-v1; byte_order is little.
binding is exactly {source_sha256, artifacts_sha256, abi_sha256, profile},
with source 9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a,
artifacts 0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085,
ABI 25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc,
and profile b4-app-m0-static. owner is exactly {type, address, bytes, alignment}.
Array entries have exactly {offset, bytes, stride, count}; scalar entries
have exactly {offset, bytes, kind}, where kind is u8/u32/u64/bool.
Both entry dictionaries have the exact declared field-name sets.

The six frame scalar names are frames_.first_, frames_.size_,
frames_.overwritten_, frames_.rejected_status_, frames_.clamped_,
frames_.invalid_. The three event scalar names are events_.size_,
events_.rejected_, events_.overflowed_. The 25 summary names use summary_.
followed by epoch_token, last_frame_token, release_us, mode, observed_results,
missing_results, rejected_results, identity_rejected, malformed_batches,
event_semantic_rejected, upstream_event_rejected, upstream_event_invalid,
source_regressions, skipped_frames, ticks.ticks, ticks.overruns, ticks.max_us,
ticks.saturated, upstream_event_overflow, timing_incomplete,
recording_incomplete, go_seen, final_frame_missing, interrupted,
terminal_exhausted. The final scalar is phase_. Native validation follows this
declared order; fields remain in that order in the exact map.

Result top-level keys are exactly schema_version, format_integrity, consistency,
errors, files, recording, provenance, common_attempt_verified, transport_verified,
hardware_acceptance, schema, raw_owner, raw_sha256, layout_sha256, layout_binding,
export_status, native_values, summary, csv, body_origin, coherence.
schema_version is integer 1. files is always {frames, events, summary};
all entries are None before atomic export, then each has exactly
{sha256, bytes, rows}. summary has exactly one data row.
recording has exactly {loss, lifecycle, phase_code}; loss is UNKNOWN,
NONE_REPORTED or REPORTED. Native values are raw Python integers, including
bool bytes before validation. Report summary uses exact CSV names/integers.

Stable decoder error codes are LAYOUT_IDENTITY, LAYOUT_SCHEMA,
LAYOUT_GEOMETRY, OWNER_SIZE, NATIVE_BOOL, FRAME_FIRST_RANGE, FRAME_SIZE_RANGE,
EVENT_SIZE_RANGE, PACK_STATUS and CSV_FORMAT. The first four have category
admission; bool/index/status refusals have category native; CSV_FORMAT has
category format. Messages explain the failing member/condition but are not
a frozen wording API. Existing consistency codes are retained without changes:
RETAINED_COUNT, STATUS_LIFETIME, STATUS_WITHOUT_OVERWRITE,
STATUS_OVERWRITE_BOUND and INCOMPLETE_CONTRADICTION.

The decoder has no CLI, file exporter, capture adapter, inferred memory map,
fallback profile or motor permission API. Source creation follows this contract;
independent oracle authors receive the contract and actual map before inspecting
any decoder implementation. Root controls all first test runs and native work.

