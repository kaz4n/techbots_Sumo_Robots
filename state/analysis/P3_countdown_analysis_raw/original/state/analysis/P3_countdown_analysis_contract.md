# D127: offline P3.1 countdown analysis

Selected under D051/D122. P3.1 requires 50 starts, every receipt-derived first
nonzero duty at least 5,100,000 us after qualified START release, with spread
strictly below 5,000 us. This tool evaluates those numbers without asserting
physical origin, transport acceptance, or a phase gate. No firmware changes.

## Public interface

`tools/analyze_countdown.py` exports `analyze_cohort(path)` and
`main(argv=None)`. CLI: `python tools/analyze_countdown.py cohort.json` emits
one JSON report, exit 0 only for timing_status PASS; otherwise exit 1.
Argparse usage errors retain exit 2. The tool only reads local files.
`main(argv)` returns the integer analysis exit code; `__main__` applies it.

Cohort JSON has exactly schema_version=1, countdown_ms=5000,
countdown_margin_ms=100, and attempts (0 through 50 entries). These explicitly
declare the supported historical hold configuration, rather than interpreting
today's config as historical evidence. Unsupported hold values fail explicitly.
Each attempt has exactly id, frames, events, summary, manifest. id is a unique
1..96-character ASCII alphanumeric/underscore/dot/hyphen string. The four paths
are nonempty strings (maximum 4096 characters), except manifest may be null.
Relative paths resolve against the cohort's directory. Reject duplicate JSON
keys, booleans where integers are needed, noninteger numbers, unknown keys,
invalid schema, more than 50 attempts and nonregular/symlink cohort inputs.
Cohort maximum is 256 KiB. No shell, network, board or external program calls.
Bind the cohort read to its regular-file descriptor with before/after identity,
size and modification-time checks, as for the bounded CSV snapshot reads.

Report fields: schema_version=1; input_status VALID/INVALID; evidence_status
COMPLETE/INCOMPLETE/INVALID; timing_status PASS/FAIL/NOT_QUALIFIED;
required_attempts=50; required_hold_us=5100000; spread_limit_us=5000;
qualified_attempts; minimum_delay_us, maximum_delay_us, spread_us (null with no
qualified observations); attempts; errors (objects with code and message).
Always include common_attempt_verified=false, transport_verified=false and
hardware_acceptance=false. A valid input schema can contain invalid evidence.

Each attempt reports id, qualification QUALIFIED/INCOMPLETE/INVALID,
release_us, go_delay_us, first_delay_us (null when unavailable),
hold_status PASS/FAIL/NOT_EVALUATED, errors and the unchanged validator report
under validation. An observed valid early interval remains visible even if
loss, missing closure or cohort size prevents qualification. Cohort min/max
and spread use qualified observations only. No attempts are silently discarded.

## Validated bytes and event semantics

Use unchanged validate_csv_bundle.validate_bundle for frames/events/summary
and optional D074 manifest. Failed format/consistency or invalid manifest makes
the attempt INVALID. Reopen only events/summary as bounded regular files with
before/after identity checks, and bind the exact parsed bytes, byte counts and
row counts to the validator's accepted hashes/counts. Reject changed snapshots.
Use the already validated manifest declaration; do not re-read it. The validator
and this tool do not claim an atomic cross-file snapshot or verified common run.

Require exactly one START_RELEASE(type 0), GO(1), FIRST_NONZERO_DUTY(2), in this
ordinal order. Missing markers are INCOMPLETE; duplicate markers, reordered
ordinals, invalid relevant payloads or owner disagreements are INVALID.
All event ordinals must increase strictly. Other event types retain validator
format checks and are not promoted into countdown timing evidence.
START/GO detail is mode 1..6 matching summary.mode; value is 0. START timestamp
matches summary.release_us. FIRST detail is wheel bitmask 1..3; its low/high
bytes represent signed L/R values excluding 0x80. An absent wheel bit requires
byte 0. A present bit may encode 0: quantization can hide an applied nonzero duty.
Never substitute a frame or GO for receipt-derived FIRST.

Unsigned offsets from START must be below 2^31 and GO_offset <= FIRST_offset;
equal timestamps are valid. Ambiguous/backward chronology is INCOMPLETE,
not an early-delay conclusion. This handles one ordinary timestamp wrap.
The tool cannot prove elapsed time across multiple unseen wraps.
If GO alone is missing, retain a unique valid START/FIRST interval and its hold
diagnostic, while qualification remains INCOMPLETE. If available GO/FIRST timing
is ambiguous or backward, retain release_us but clear both delay fields and use
NOT_EVALUATED; do not publish an apparent early interval from bad chronology.

## Qualification and cohort calculation

Qualification additionally requires SEALED owner phase 3, epoch_token >0,
go_seen=1, no reported loss or incomplete data, and a supplied valid manifest
declaring closed. Absent/open/unknown closure remains INCOMPLETE while retaining
diagnostic intervals. Sealed valid markers with go_seen=0 or epoch_token=0 are
owner contradictions and INVALID. Origin and build/config identities remain
declarations, copied through validation; synthetic data may pass arithmetic.

Identical (frames, events, summary) hash triples make every reused bundle
INVALID, even under different attempt IDs. No claim that hashes establish
physical independence follows. Exactly 50 QUALIFIED attempts produce COMPLETE;
any invalid attempt makes evidence INVALID, otherwise fewer qualified attempts
make INCOMPLETE. Timing is NOT_QUALIFIED unless COMPLETE, then PASS exactly when
every first_delay_us >=5100000 and spread_us <5000; otherwise FAIL. No tuning,
config edit, hardware acceptance or human approval follows from any result.

## Verification

Independent tests derive from this contract and frozen wire format, without
reading analyzer implementation. Cover 50 valid synthetic attempts, hold and
spread boundaries, wrap, zero timestamps, absent/duplicate/order/payload/owner
errors, small nonzero duty rounding to zero, loss/open recordings/closure,
duplicate IDs/bundles, unsupported config/schema/bounded files, changed bytes,
CLI exit behavior and explicit provenance limits. Preserve all existing tests.
