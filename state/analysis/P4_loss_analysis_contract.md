# D130: offline P4.2 target-loss analysis

Adopted under D051/D128 after D129 host verification and scoped review. This
read-only P4 software task supplies interval analysis, not firmware or tuning
changes, board operations, physical acceptance or a phase gate.

## Public interface and bounded input

`tools/analyze_target_loss.py` exports `analyze_cohort(path)` and `main(argv=None)`.
CLI takes one cohort JSON, prints one JSON report; main returns0 only when cohort
 timing_status=PASS, otherwise1; argparse usage errors retain2. Local read-only
files only, no shell/network/board/program calls. Reuse unchanged CSV validator.

Cohort exact keys: schema_version=1, opp_clear_ms=30, extra_margin_ms=5,
attempts=array0..10. Only these declared historical values are supported; never
read today's config as past run evidence. Each attempt has exact id, frames,
events, summary, manifest; id unique ASCII[A-Za-z0-9_.-] length1..96. Paths
nonempty strings <=4096chars; local absolute paths are accepted and relative
paths resolve against the cohort directory (including ../); manifest maynull.
UNC/network paths are rejected; no extra containment rule is invented.
Reject UNC prefixes and URI-style network paths in the cohort argument or any
declared path before file access; a declared path violation is a cohort schema
error (input_status INVALID), not a per-attempt file-validation result.
Reject duplicateJSONkeys, booleans/noninteger numbers, unknown keys, unsupported
values, >10attempts, nonregular/symlink cohort. Bounded cohort256KiB. Bind its
regular descriptor identity/size/mtime before/after bounded read.

Report schema_version1; input_status VALID/INVALID; evidence_status
COMPLETE/INCOMPLETE/INVALID; timing_status PASS/FAIL/INDETERMINATE/NOT_QUALIFIED;
required_attempts10, bound_us35000, qualified_attempts; minimum_lower_delay_us,
maximum_upper_delay_us (null if no qualified measurements); attempts; errors
(code,message). Always hardware_acceptance=false, transport_verified=false,
common_attempt_verified=false. input_status concerns cohort read/schema only.
A synthetic M1 declaration may pass arithmetic
but cannot prove hardware, motor permission, common run or physical behavior.

Attempt fields: id; qualification QUALIFIED/INCOMPLETE/INVALID/EXCLUDED/
NOT_EXERCISED/NOT_RECORDED; trace_status COMPLETE/INCOMPLETE/INVALID/EXCLUDED/
NOT_EXERCISED/NOT_RECORDED; motors_allowed (bool/null); source_start_us,
source_end_us, brake_decision_us, zero_applied_us (null if unavailable);
lower_delay_us, upper_delay_us (null if no valid full interval); timing_status
PASS/FAIL/INDETERMINATE/NOT_EVALUATED; exclusion_detail (integer/null); errors;
validation (unchanged validator report). Never silently discard an attempt.

## Snapshot binding and owner eligibility

Call unchanged validate_csv_bundle.validate_bundle on every bundle plus optional
D074 manifest. Format/consistency/manifest-invalid makes attempt INVALID.
Reopen only events/summary, bounded16MiB regular files with before/after identity
checks; bind exact parsed bytes, byte counts and row counts to accepted validator
hashes/counts. Retain accepted manifest declaration without rereading. Reject
changed evidence, including same-size bytes with restoredmtime. Do not claim
an atomic cross-file snapshot or verified origin. Preserve old tool/tests.

Qualification additionally requires SEALED phase3, epoch_token>0, go_seen1,
no reported loss/incomplete, valid manifest declaring closed, and traceHEADER
M1. Missing/open/unknown closure or M0 remains INCOMPLETE with diagnostic timing
retained. Explicit valid event markers contradicted by zeroepoch/go_seen are
INVALID. Every START requires positive epoch; every GO and every non-header
trace require go_seen1 and positive epoch, regardless ownerphase. Header-only
with go_seen0 may be a legitimate canceled countdown. Identical
frames/events/summary hash triples invalidate ALL reused
members, even different IDs. Hashes do not establish physical independence.
Qualification precedence: INVALID input/owner/duplicate first, then owner
INCOMPLETE (loss, unsealed/missing closure/M0 or missing GO for a candidate),
then trace classification. trace_status describes grammar/time only, so a valid
full M0 interval can have COMPLETE trace, INCOMPLETE qualification and diagnostic
PASS/FAIL. Never promote EXCLUDED or incomplete traces to QUALIFIED.
A closed, loss-free SEALED M1 HEADER-only record with positive epoch and
go_seen0 is legitimately NOT_EXERCISED for both trace and qualification.
Presence of GO and go_seen1 is required for a candidate, not this canceled-countdown
case. Other incomplete-owner conditions (loss, M0, closure, phase) still apply.

## Exact D129 trace grammar

Validate all event ordinals strictly increasing. Other codes keep existing CSV
format checks only, except START0/GO1 and TIMING10 below. START/GO if present
must be unique, mode1..6 matching summary.mode, value0; START time matches
summary.release_us. Every non-header trace requires one START then GO before that record in ordinal
order; missing GO makes trace INCOMPLETE with no delay, not a reconstructed GO.
A present GO after a non-header trace record is INVALID; HEADER normally
precedes GO and does not trigger this ordering rejection.
Whenever START and GO are both present, GO must follow START in ordinal order
and its unsigned release-relative offset must be below2^31, even without TIMING
or with HEADER only. This validates chronology, not the separate countdown hold.

No TIMING records =>NOT_RECORDED. TIMING present without HEADER =>INVALID.
Exactly one HEADER detail0 with value0x0101(M0) or0x0105(M1); it is immediately
after START in event order and equals START timestamp in all cases.
All other timing records require value1; code10
unknown/reserved detail/value is INVALID. WireID1 never substitutes a token.

Legal complete timing-detail sequences (ignoring non-TIMING records):
- [0]: trace NOT_EXERCISED; open ownership still makes qualification INCOMPLETE.
- [0,x], x6..10: EXCLUDED before source pair.
- [0,1,2,x], x5..10 or12: EXCLUDED after source pair.
- [0,1,2,3,11]: EXCLUDED for invalid expected receipt.
- [0,1,2,3,4]: full candidate; calculate only after all time/owner checks.
A proper unfinished prefix [0,1], [0,1,2], [0,1,2,3] is INCOMPLETE.
Duplicates, order violations, further records after terminal, missing interior
markers, or any other sequence are INVALID. Source1/2 must also be adjacent
in full event order. Never reconstruct missing source/decision/receipt from
frames, FIRST_NONZERO, STATE_CHANGE or later zeros. Canceled attempts cannot
be silently replaced. Code10/11 diagnostic exclusions are valid record grammar,
not evidence of measured delay; invalid clock cancellation times need not
establish a physical chronology.

## Time arithmetic and result

For a full candidate, use one unsigned32-bit release anchor. GO,S,E,D,A offsets
must be below2^31 and GO<=S<=E<=D<=A. HEADER equalsSTART timestamp. This admits
ordinary wrap and timestamp0 while rejecting ambiguous/backward offsets as
INVALID with no delay. Whole unseen wraps can alias the same uint32 values;
the files alone cannot detect those or prove physical elapsed time. Ordinal timing records may have timestamps
earlier than intervening decision events; do not sort raw uint32 timestamps.

Report interval[A-E,A-S]. PASS upper<=35000 inclusive; FAIL lower>35000;
otherwise INDETERMINATE. This is observed all-front-clear acquisition to matched
applied-zero receipt completion, NOT physical box removal, first PWMedge, wheel
rest, robot staying in the ring, or all ofP4.2. Retain a semantically valid
interval as diagnostic if M0, missingclosure, loss or cohortsize prevents
qualification; do not publish delay from any INVALID member, including owner
contradiction or duplicate bundle. Clear all source/decision/applied timestamps
and both delay fields, use NOT_EVALUATED, while retaining errors/validation.
Retain the decoded trace_status when separately trustworthy grammar/time checks
completed (for example, COMPLETE with an owner contradiction or reused bundle).
An invalid validator/manifest or unbound reread prevents trusted decoding and
uses trace_status INVALID. Qualification always remains INVALID in these cases.

For unfinished or excluded traces, check all present source/decision prefix
timestamps against the same START anchor: each offset below2^31, and existing
GO<=S<=E<=D in that order. Omit missing fields from this order, including GO;
missing GO still prevents qualification and interval calculation. A reversed or
ambiguous present prefix is INVALID even when it would otherwise be incomplete
or excluded. Exclusion-terminal timestamps, including10/11 diagnostic clock
cancellations, are not used in these prefix checks or to calculate an interval.

Exactly10QUALIFIED observations =>COMPLETE. Any INVALID member=>evidenceINVALID;
otherwise fewerqualified=>INCOMPLETE. Cohort timingNOT_QUALIFIED unlessCOMPLETE;
then FAIL if any intervalFAIL, elseINDETERMINATE if any straddles, elsePASS.
Qualified extrema exclude diagnostics. EXCLUDED/NOT_RECORDED/NOT_EXERCISED
members contribute no passing trial. No tuning or hardware acceptance follows.

## Verification

Independent spec-derived tests before implementation execution:10distinct
synthetic M1cohorts;35000boundaries andstraddles; wrap/zero/half-range;
alllegalprefix/exclusion/grammarcases; metadata/order/sourcepair adjacency;
owner/closure/loss/M0; duplicateIDs/bundles; exactschema/boundedregularfiles;
hash-bound reread mutation; CLIcodes; unchangedCSV/countdown suites and all
firmware hashes. Test and reviewer contexts stay separate from implementation.
