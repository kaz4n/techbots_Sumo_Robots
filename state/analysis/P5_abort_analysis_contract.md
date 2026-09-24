# D136 companion analysis for D135 qualified opener aborts

**ADOPTED under D051 as D136**, 2026-09-24. Separate design review passed against
draft fea16ebd with all three minor findings closed. All five decisions below
are adopted for offline P5 software preparation. This does not amend D135 or
authorize a board operation, configuration change, physical trial or gate.
Independent test expectations must be frozen before implementation execution.

## Scope and existing interfaces

Add one small read-only companion, provisionally `tools/analyze_opener_abort.py`,
following D130's `analyze_cohort(path)` and `main(argv=None)` interface. Leave
`analyze_target_loss.py`, `validate_csv_bundle.py`, D073/D074 schemas, firmware
and existing tests unchanged. Import and call the unchanged CSV validator; do
not create a shared analysis framework, transport service, dashboard or report
generator. No shell, network, board, compilation or program invocation.

Public pure seam: `decode_cue(value: int, mode: int) -> dict | None` returns
the exact five cue fields listed below for valid matching-mode D135 metadata,
otherwise None. Reject booleans, non-integers, values outside0..65535 and modes
outside1..6. It reads no files or current config. This allows the independent
full uint16 metadata oracle without65536 filesystem cohorts; end-to-end tests
still verify that the analyzer uses the same declared wire contract.

Proposed CLI: `python tools/analyze_opener_abort.py path/to/cohort.json`.
One positional local JSON path, one JSON report on stdout. Return 0 only when
cohort `timing_status` is PASS; return 1 for every other analysis result and
retain argparse's 2 for usage errors. A zero exit describes the declared,
source-bound logical timing dataset, never physical acceptance.

## Exact proposed cohort and source binding

Cohort keys are exactly `schema_version`, `mode`, `source`, `attempts`.
`schema_version` is integer 1; `mode` is one integer 1..6, representing one
tested opener, with LEFT and RIGHT treated as distinct modes. `attempts` has
0..10 entries in retained trial order. Each has exactly D130's `id`, `frames`,
`events`, `summary`, `manifest`; the manifest path may be null. IDs are unique
ASCII `[A-Za-z0-9_.-]`, length 1..96. No inferred file discovery or replacement
of omitted/excluded/failed attempts.

`source` has exactly these keys:

| Key | Accepted form and purpose |
|---|---|
| `firmware_revision` | Lowercase 40- or 64-hex revision declaration |
| `source_sha256` | Lowercase 64-hex staged-source identity declaration |
| `config` | Path to the exact historical `config.h` bytes |
| `config_sha256` | Lowercase 64-hex hash required to match those bytes |
| `flags` | Exactly `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1` or the same string with `MOTORS_ALLOWED=1` |

M1 is accepted as an offline declaration only; this adds no checked M1 native
deployment route. Flags with additions, omitted definitions, reordered tokens,
other profiles or MATCH=1 are unsupported in this first companion contract.
Report the accepted flags and their M value; each trace HEADER must match it.

Use a bounded, regular, nonsymlink config snapshot read (proposed 256 KiB),
descriptor/path identity checks and SHA-256 over its exact bytes. Read it once
and retain the verified hash and extracted values. Do not open today's repository
config, check out a revision, execute a preprocessor or infer historical values.

Proposed supported extraction is deliberately narrow: read the unique,
unconditional decimal `inline constexpr std::uint32_t NAME = <digits>U;` declarations
for `TICK_US`, `ATTACK_ENTER_TICKS`, `MODE_ARC_ENABLED`, `MODE_WAIT_ENABLED`,
`LOG_HZ`, `LOG_EVENT_CAPACITY` and `LOG_FRAME_WINDOW_MS`. The suffix is contiguous
uppercase U or lowercase u: `1000U` and `1000u` are accepted; `1000 U` is not.
Permit surrounding-token whitespace as in D134, but no leading zero except
the single digit 0, sign, digit separator, other suffix or unsuffixed literal.
Use the existing D134 restricted-literal admission approach: ignore comments and
literal contents, reject splices/digraph directives or conditional/macro mentions
of these names, duplicates and expressions; never evaluate arbitrary C++.
Unsupported source spelling reports error code `UNSUPPORTED_CONFIGURATION`,
never a new status or a claim that the firmware is invalid. Values: TICK_US
1..2147483647, ATTACK_ENTER_TICKS
1..4294967295, optional-mode flags 0/1; this version requires 25 Hz, 4096 events
and 200000 ms frame window, yielding the D135 fixed 5001 frames. The last three
are profile identity checks, not permission to tune them.

Uniqueness applies to the supported declarations, not every identifier use.
Ordinary unconditional reads in other declarations are allowed: the current
config derives frame count from LOG_FRAME_WINDOW_MS and LOG_HZ. Conditional or
macro mentions remain unsupported. Do not reject that actual canonical config
merely because its supported constants are used elsewhere.

Mode availability uses that snapshot: 1..3 always available, 4/5 require ARC=1,
6 requires WAIT=1. A requested disabled mode is unsupported configuration.
Snapshot mode/threshold values appear in the report. No default taken from the
interpreter's current checkout may substitute for a missing value.

For qualification, each accepted D074 manifest must declare matching revision,
source hash, config hash, 25 Hz and 5001/4096 capacities. Null required identity
declarations make qualification INCOMPLETE; nonnull disagreement is INVALID.
The config hash is locally checked; the source/revision/profile relation to the
deployed image remains a caller declaration. A source hash is not a signature,
proof of compilation, proof of producer semantics or proof of hardware origin.
Report this distinction as `binding_status=DECLARED_MATCH` when all comparisons
pass, otherwise INCOMPLETE/INVALID. Preserve the manifest's original declaration.

All path/schema rules follow D130: paths nonempty <=4096 characters, local
absolute paths accepted, relative paths including `../` resolved against the
cohort directory, UNC and URI paths rejected before any declared-file access.
Reject duplicate JSON keys, unknown keys, booleans in integer fields, noninteger
numbers, unsupported values and >10 attempts. Cohort limit 256 KiB; regular
nonsymlink bounded read with before/after identity checks. Preserve validator's
16 MiB CSV and 16 KiB manifest limits. These are local bounded inputs, not a
new filesystem-containment policy.

## Validated bytes and owner qualification

Call `validate_csv_bundle.validate_bundle` for every supplied attempt, even
when another attempt fails. Format/consistency failure or invalid supplied
manifest makes the affected attempt INVALID. Reopen events and summary using
D130's bounded regular-file/identity/hash/byte/row binding to the validator's
accepted snapshot. A same-size rewrite with restored mtime must still fail
the hash binding. Retain the accepted manifest without a second read. No claim
of an atomic cross-file snapshot follows.

Qualification requires a valid COMPLETE trace or explicit HANDOVER_FAILED
observation, SEALED owner phase 3, positive epoch token, explicit GO and
`go_seen=1`, no reported loss and aggregate `incomplete=0`, a valid manifest
declaring `closed`, matching source binding, and M1. Absent manifest or valid
`unknown`/`open` closure,
unsealed ownership, any validator loss, M0, missing source declaration or
missing GO makes qualification INCOMPLETE while valid diagnostic results remain.
An invalid supplied manifest (including null or missing required closure) stays
INVALID under the unchanged D074 validator. An aggregate incomplete flag with
no supporting detailed loss likewise retains that validator's consistency result.
No single loss field is waived, including upstream event overflow/invalid,
malformed batches, rejected events, overwritten frames and missing final frame.
A visible success suffix cannot repair loss earlier in the same attempt.

START with zero epoch, or GO/non-header TIMING with zero epoch or `go_seen=0`,
is an INVALID owner contradiction regardless of owner phase. Header-only
countdown cancellation can be valid grammar with `go_seen=0`; it remains
INCOMPLETE under D135's unfinished-prefix rule, not a qualified trial.
An identical frames/events/summary hash triple invalidates every reused member,
even with different IDs. Different hashes do not establish independent trials.

Precedence: invalid bytes/schema/owner/binding/duplicate first; then incomplete
owner/loss/M0/binding; then trace disposition. Keep trace validity, diagnostic
timing and qualification separate. INVALID clears published decoded endpoint
times and elapsed arithmetic; errors and the validator report remain. A
separately trusted trace classification may remain COMPLETE when later owner
or duplicate checks invalidate qualification, following D130.

## Exact D135 wire interpretation

All event ordinals strictly increase. START type 0 and GO type 1, if present,
are unique; detail is mode 1..6 matching cohort and summary, value is zero.
START timestamp equals `summary.release_us`. HEADER is type 10/detail 0,
value exactly 0x0201 M0 or 0x0205 M1, immediately following START in full event
order with the identical timestamp. A P4 header/detail is INVALID in this tool.
Other event codes retain unchanged CSV checks; never reconstruct missing cues,
GO, application receipts or timing from frame/state/duty values.

Validate details/values exactly as D135: 16/17/20/23/24 require value 1;
19 requires state 5, 6 or 7; 21/22 require value 1 or 2; 25 requires state 0..11.
18 decodes mode bits 0..2, phase 3..5, cause 6..7, mask 8..14 and snapshot bit
15. Mode must match the attempted mode. Validate against the full independent
D135 mode/phase/cause/mask/snapshot table, including SIDESTEP outer masks,
ignored PIVOT front, ARC's narrower phases, DIRECT snapshot rules and WAIT's
inner SIDESTEP_R phases retaining mode 6. Do not rerun Fusion or an opener.

| TIMING detail sequence | Trace status and diagnostic result |
|---|---|
| No TIMING records | NOT_RECORDED; no result |
| `[0]`, `[0,16]`, `[0,16,17]`, `[0,16,17,18]`, `[0,16,17,18,19]` | INCOMPLETE; no elapsed result |
| `[0,16,17,18,19,20]` | COMPLETE; logical handover check and A-D arithmetic |
| `[0,16,17,18,25]` | HANDOVER_FAILED; logical FAIL, no applied time or elapsed |
| `[0,16,17,18,19,24]` | EXCLUDED; invalid-receipt terminal, no elapsed |
| `[0,21]`, `[0,22]`, `[0,23]` | EXCLUDED; preserve snapshot/natural/interrupted/source detail |
| `[0,16,17,18,22]` | EXCLUDED; final preemption |
| `[0,16,17,18,19,22]` | EXCLUDED only for value 2 STOP_FAULT |

Unknown metadata, missing interior records, duplicates, further TIMING records
after a terminal, >6 TIMING records or any unlisted order are INVALID. No
retry candidate is recognized. Full-order adjacency is required for the
qualification decision suffix `[16,17,18,19]`, `[16,17,18,25]` or
`[16,17,18,22]`, and every retained prefix thereof. Receipt terminal 20/24,
or later exhaustion terminal 22 following 19, need not be adjacent to 19.
CSV omits batch boundaries, so the analyzer cannot prove the suffix followed
every ordinary event of that exact decision or that a receipt preceded every
ordinary event of its receive batch. Do not invent such boundaries from times.

GO must precede every non-header trace record in full ordinal order. An absent
GO makes an otherwise valid trace INCOMPLETE with no arithmetic; a present
GO appearing later is INVALID. No timing record is reordered by timestamp.

Check HANDOVER value against normal current-mask routing, independently of
the recorded triggering cause. No front requires state 7 DEFEND_TURN, including
valid side/rear cues. Any front normally requires 5 TRACK, even when the cause
was side/rear during ignored-front PIVOT or WAIT HOLD. Under a source-bound
ATTACK_ENTER_TICKS=1, centered front patterns 2,3,5,6,7 require state 6 ATTACK;
front patterns 1/4 still require TRACK. For larger thresholds this fresh
handover requires TRACK. This checks a public B5/D034 necessary result; it
does not prove actual routing or qualification execution. Contradictory
HANDOVER success metadata is INVALID, not a fabricated HANDOVER_FAILED event.
An explicit detail 25 remains logical FAIL even if its numeric state could
otherwise be correct: missing routing or wrong token can fail with that state.

## Chronology and elapsed arithmetic

When START and GO both exist, require their full ordinal order and
`(GO-START) mod 2^32 < 2^31`, including header-only/no-trace attempts. This
checks chronology, not the separate countdown hold. When QUALIFIED detail 18
is present, its decision D must not precede GO under the same below-half-range
unsigned rule.
The read pair can precede GO: a DIRECT cue on the GO decision is explicitly
legal. Never import D130's `GO <= source_start` rule into P5.

Use R_s as the common unsigned anchor for every available source/decision
prefix. Require `0 <= R_e-R_s <= D-R_s < 2^31`; COMPLETE adds
`D-R_s <= A-R_s < 2^31`. Missing prefix endpoints are omitted, not inferred.
HANDOVER 19 and HANDOVER_FAILED 25 must equal QUALIFIED 18's D; final-preemption
22 directly after 18 has that same D. Terminal INVALID_SOURCE/INVALID_RECEIPT
timestamps describe an observed failure and do not establish a usable elapsed
measurement; do not require the failed clock itself to prove a sound epoch.
Later exhaustion 22 is not an APPLIED timestamp.

For COMPLETE with valid wire times and matching HANDOVER, report
`elapsed_us=(A-D) mod 2^32`. PASS iff elapsed_us <= historical TICK_US,
inclusive; otherwise FAIL. Keep actual late values, including 1001 us or much
later valid values; no clamping, deadline stop or INDETERMINATE interval is
introduced. R_s/R_e bound the current admitted acquisition, not the acceptance
origin or the age/onset of a debounced or held effective cue. B5 hysteresis may
retain effective bits from older detections; this stream reconstructs neither
their first detection nor physical onset/age. Add no effective-cue age threshold
or GO-to-read constraint. Timestamp zero and ordinary wrap are legal.
Ambiguous/backward offsets are INVALID.
Unseen whole wraps can alias timestamps and cannot be disproved from the wire.

Wire fields omit T, C, next T/D, full 64-bit request token, pending ownership,
actual route invocation and acknowledged EN. Full epoch chronology, same-token
routing/application and M1 EN are producer-enforced, source-bound claims,
not independently reconstructed conclusions. Equal D means one logical
observation, not zero computation. No physical box/electrical onset, PWM-edge,
mechanical response, target fit, calibrated clock or full-tick WCET is measured.

## Proposed exact report and aggregation

Top-level keys: `schema_version` (1), `input_status` (VALID/INVALID),
`evidence_status` (COMPLETE/INCOMPLETE/INVALID), `timing_status`
(PASS/FAIL/NOT_QUALIFIED), `mode`, `source`, `required_attempts` (10),
`qualified_attempts`, `passing_attempts`, `logical_failures`,
`minimum_elapsed_us`, `maximum_elapsed_us`, `attempts`, `errors`,
`declared_physical_trials_status` (ELIGIBLE/NOT_QUALIFIED), and the constant
false fields `hardware_acceptance`, `transport_verified`,
`common_attempt_verified`, `producer_semantics_verified`.

`input_status` concerns cohort read/schema only. On cohort read/schema failure,
use input/evidence INVALID, timing NOT_QUALIFIED, mode/source null, attempts
empty, all three counts 0, both extrema null and physical status NOT_QUALIFIED.
After schema admission input_status stays VALID and mode retains the integer
cohort mode, including subsequent source/config or attempt failures.

An admitted source descriptor whose config read, identity/hash check, extraction,
supported-value check or mode-availability check fails makes source binding and
cohort evidence INVALID and timing NOT_QUALIFIED, even for an empty cohort.
Validate every supplied schema-valid bundle through the unchanged CSV validator
and retain each report; no early source failure may skip those bundle checks.
In this source-invalid path every attempt has qualification/binding/trace INVALID,
logical/timing NOT_EVALUATED, null decoded fields including motors_allowed, and
its validation/errors retained. All three counts are 0 and both extrema null.
Do not decode timing against unknown configuration or substitute current config.

`source` is null when no source descriptor could be accepted; otherwise its
exact keys are the five input descriptor keys, `config_values`, and
`binding_status`. `config_values` is null before successful extraction, or an
object with the seven literal uppercase config names as its exact keys.
Partial extraction is not published. A later mode-availability failure retains
the already extracted supported values while marking the source INVALID.
Source-level binding_status is DECLARED_MATCH after config verification and
descriptor admission, otherwise INVALID; per-attempt binding additionally
compares the accepted manifest and can be INCOMPLETE. These statuses do not
assert source-to-image verification. `errors` entries have `code` and `message`
as in D130.

Attempt keys: `id`, `qualification` (QUALIFIED/INCOMPLETE/INVALID/EXCLUDED/
NOT_RECORDED), `trace_status` (table above or INVALID), `motors_allowed`,
`binding_status`, `read_start_us`, `read_end_us`, `qualified_us`,
`handover_us`, `applied_us`, `elapsed_us`, `cue` (null or exact `mode`,
`phase`, `cause`, `effective_mask`, `snapshot_front_present`), `handover_state`,
`logical_status` (PASS/FAIL/NOT_EVALUATED), `timing_status`
(PASS/FAIL/NOT_EVALUATED), `terminal_detail`, `terminal_value`, `errors`,
`validation` (unchanged validator report). Absent numeric/decoded fields are
null. COMPLETE gives logical PASS and arithmetic PASS/FAIL; HANDOVER_FAILED
gives logical FAIL and timing NOT_EVALUATED. Other terminals provide neither.
`motors_allowed` is a boolean only after an exact P5 HEADER was decoded from
bound, valid bytes; otherwise null. Never infer it from cohort flags. A trusted
decoded HEADER may remain available after a later owner/duplicate invalidation,
but INVALID always sets logical/timing NOT_EVALUATED and clears endpoint times
and elapsed. Source-invalid handling above takes precedence.

For a valid completed grammar, terminal_detail/value retain the final pair:
20/1 for COMPLETE,25/actual-state for HANDOVER_FAILED, and the diagnostic pair
for EXCLUDED. Unfinished prefixes and no trace have null terminal fields.
handover_state retains the observed state from either19 or25; it is not inferred
from the cue. These fields describe observed metadata, not physical success.

`qualified_attempts` counts qualification QUALIFIED. `passing_attempts` counts
only QUALIFIED attempts with both logical_status PASS and timing_status PASS.
`logical_failures` counts trusted logical_status FAIL diagnostics whose
qualification is not INVALID, including M0, loss or closure-incomplete attempts;
retain that count when another member prevents cohort qualification. These
diagnostics do not contribute qualified or passing attempts unless independently
eligible under all qualification rules.

Any INVALID member makes cohort evidence INVALID. Exactly ten eligible M1,
closed, loss-free, bound COMPLETE or HANDOVER_FAILED observations make
evidence COMPLETE; otherwise INCOMPLETE. Qualified means evaluable evidence,
not a passing attempt. An explicit, otherwise eligible HANDOVER_FAILED counts
as an evaluated failure, never as a missing favorable measurement. Cohort
timing is NOT_QUALIFIED unless evidence COMPLETE; then any logical or elapsed
FAIL yields FAIL, otherwise PASS. Retain `logical_failures` even when another
attempt prevents cohort qualification. Extrema use qualified COMPLETE elapsed
measurements only; null when none exist. M0 may retain per-attempt arithmetic
diagnostics but cannot qualify or produce a cohort PASS.

`declared_physical_trials_status=ELIGIBLE` requires cohort PASS and all ten
manifests explicitly declaring `origin=hardware_reported`; otherwise it is
NOT_QUALIFIED. ELIGIBLE is eligibility for separate physical review, never a
physical PASS. Synthetic M1 may pass the logical dataset arithmetic but cannot
satisfy physical 10/10. All acceptance booleans stay false in every case.

Each cohort covers one mode and all ten scheduled slots, retaining every
original failure/exclusion. Fewer than ten is incomplete; an exclusion is not
replaced by a favorable later attempt. More trials belong to a separately
identified later block retaining the original block and all attempts in the
external trial ledger. The tool cannot prove the submitted list is complete
or that ten distinct files are ten physical trials. P5.1/2/4/5, later qualified
ATTACK behavior, actual 10/10 provenance, physical permission and phase gates
remain outside this logical timing report.

## Independent acceptance oracles before implementation execution

Freeze spec-derived tests without implementation/test-author cross-reading:
all 65536 packed cue values against the literal metadata table; every legal
terminal/prefix and illegal detail/value/order; full-order suffix adjacency;
header/START/GO/owner/mode consistency; P4 rejection and unchanged D130/CSV
regressions. Cover GO-time DIRECT reads preceding GO, WAIT zero duty, snapshot
and natural exclusions, ignored-front side cues routed to TRACK, threshold 1
centered versus off-center routing, threshold 3, and explicit HANDOVER_FAILED
whose state happens to look correct.

Arithmetic: 999/1000/1001 us at TICK_US=1000, a different bound from the supplied
snapshot, valid late values, zero/wrap/half-range/reversed prefixes, equal
qualification/handover time, incomplete tails and invalid diagnostic clocks.
Data: exact JSON/schema/path/size rules, config hash/unsupported literals,
source declaration mismatch/nulls, every loss field, M0 and synthetic M1,
partial/open ownership, duplicates, mutation on bound reread, complete failed
ten-trial blocks and exclusions without substitution. CLI exit codes and
constant false acceptance fields must be independent assertions. No fabricated
physical run enters test output as observed evidence.

## Decisions adopted under D051

1. **Binding scope:** adopt hash-checked historical config plus matching declared
   source/revision/flags, with the relation to a deployed image explicitly
   unverified. Requiring signed/build receipt verification would be a separate
   bounded task; the current D074 manifest cannot supply that proof.
2. **Supported input subset:** approve the seven restricted canonical config
   declarations and exact M0/M1 flag strings. This is a proposed analyzer input
   boundary, not an amendment of D135's broader producer/config possibilities.
3. **Failure accounting:** approve otherwise qualified HANDOVER_FAILED as an
   evaluated trial failure, allowing a ten-attempt logical FAIL. Its absence
   of A must never make it a successful elapsed measurement or erase the FAIL.
4. **Missing markers and header-only:** approve D130-style absent-GO INCOMPLETE
   versus later-GO INVALID, and D135 header-only INCOMPLETE rather than D130's
   NOT_EXERCISED. Also approve checking GO-to-decision chronology without
   incorrectly requiring GO-to-read chronology.
5. **Physical declaration language:** approve ELIGIBLE only for ten reported
   hardware-origin passing records, with acceptance always false and external
   roster completeness/permissions/clock/producer review still required.

Next action: independent public/private test freeze, then bounded companion
implementation after the D135 frozen source-validation run finishes. Preserve
the reviewed draft and review in Git; adoption changes no producer semantics.
