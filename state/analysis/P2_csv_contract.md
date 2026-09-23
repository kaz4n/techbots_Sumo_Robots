# D-073 offline recorder CSV contract - 2026-09-23

Selected under D-051 following independent read-only audit. Extend D-068 only
to pure offline formatting for B8. No live owner integration, cursor, transport,
dump command, Arduino/API call, upload, gate or physical acceptance is included.
P2 needs frames/events CSV; this component alone cannot satisfy B8 or IDLE policy.
SEALED is not current core IDLE; incomplete=false is not a finished/no-gap run.

Public API is src/hal/recorder_csv.h, fixed before independent code/tests.
Format one header or row per call. Caller owns destination; no heap, clock, I/O,
exceptions, dynamic strings, locale, float formatting or unbounded work. Numeric
conversion uses bounded loops (at most20 decimal digits). Source is read-only;
caller guarantees non-overlap and no concurrent mutation. No whole-owner copies.

ASCII CSV version1 uses decimal integers without spaces, plus lowercase fixed-
width raw hex. Every successful line ends LF then NUL; size includes LF, excludes
NUL. No quoting needed. MAX_LINE_BYTES1024 includes both. Null destination always
INVALID_ARGUMENT; capacity0 on nonnull is INSUFFICIENT_CAPACITY. Unknown frame
PackStatus is INVALID_ARGUMENT (check before capacity); known OK0/CLAMPED1/INVALID2
are retained. Every failure size0 and, if writable, destination[0]=NUL only;
other destination bytes unchanged. Insufficient capacity never yields a prefix.
Capacity including the final NUL is sufficient exactly; one byte less fails.

Frame header, fixed order:
`schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex`

Frame row: schema1, caller ordinal (uint64), numeric PackStatus, then all25 wire
bytes decoded at logframe.h documented offsets in exact integer units. Decode
signed two's complement using defined arithmetic incl INT32_MIN, INT16_MIN and
raw duty -128. Do not clamp, repair, validate masks/enums or re-pack. Raw hex is
exactly50 digits in stored byte order. Even INVALID data is retained; the supplied
status and raw codes are evidence, not a claim of valid physical measurements.

Event header:
`schema_version,ordinal,t_us,type,detail,value,raw_hex`
Event row schema1/ordinal, exact little-endian t_us/type/detail/value and16-digit
raw hex. All possible bytes retained including unknown type; no semantic filter.
Caller controls insertion order; never sort or unwrap timestamps/equal times.

Summary header, fixed order:
`schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,incomplete`

Summary row exports every AttemptSummary field plus phase, retained counts,
frame/event loss statistics and aggregate incomplete from SummarySnapshot.
Booleans decimal0/1; enums their uint8 representation. Preserve independently
supplied values even when inconsistent; formatter does not invent missing facts
or recompute completeness. captureSummary copies every field from const owner
under caller exclusive access; it never clears, advances, authorizes or mutates.
EMPTY/RECORDING/DRAINING/SEALED/INTERRUPTED must remain distinguishable. Rate/
firmware/target manifest and dump session protocol remain future design work;
this schema must not be presented as a complete transported evidence envelope.

Independent tests derive literal byte/CSV fixtures from this contract and public
headers only. Cover all headers/column order, signed extrema, unsigned maxima,
all known status and unknown rejection, arbitrary invalid bytes/raw retention,
exact-fit/short/null/zero buffer and guards, repeated const reads, wrap/equal
timestamps, all snapshot fields with distinct values and uint64 extremes,
capture from real empty/recording/sealed/interrupted owner examples, no source
mutation. Use fixed-seed byte streams with independent scalar parsing to check
lossless round trip. Preserve existing locked/tests/config unchanged.

Coordinator owns header/CMake/state/source manifests. Separate author owns tests;
worker owns recorder_csv.cpp only. Fresh same-model read-only reviewer checks
actual diff, bounded work, independent tests and exact existing inert hash
replacements. No new allowlist entry or upload authority. Host normal+sanitizer
and applicable controlled tooling must pass. No target/physical result implied.
