<!-- Explains the D130 offline P4 target-loss analyzer and cohort schema. -->
<!-- Separates arithmetic qualification from physical trials and motor permission. -->
<!-- Examples are schema placeholders; independent tests provide synthetic verification. -->
# Analyze P4 target-loss timing

`tools/analyze_target_loss.py` reads existing local D073 CSV bundles and optional
D074 manifests. It prints one JSON report without changing evidence, firmware
or configuration. It never contacts a board or starts a program on one.

```text
python tools/analyze_target_loss.py logs/p4_loss/cohort.json
```

The Python interface is `analyze_cohort(path)`; `main(argv=None)` implements the
CLI. Exit status is 0 only for cohort timing `PASS`, 1 for every other analysis
result, and 2 for argparse usage errors. Input and evidence errors appear in
JSON as `errors` entries with `code` and `message`.

## Cohort input

This is a **synthetic schema placeholder**, not trial data or a recorded result.
The paths do not identify supplied evidence. A one-entry cohort cannot qualify
the required ten observations.

```json
{
  "schema_version": 1,
  "opp_clear_ms": 30,
  "extra_margin_ms": 5,
  "attempts": [
    {
      "id": "placeholder_01",
      "frames": "placeholder_01.frames.csv",
      "events": "placeholder_01.events.csv",
      "summary": "placeholder_01.summary.csv",
      "manifest": "placeholder_01.manifest.json"
    }
  ]
}
```

Those are the exact allowed keys. The historical configuration values must be
integers 1, 30 and 5 as shown; today's `src/config.h` is not past-run evidence.
`attempts` accepts zero through ten entries. IDs must be unique, 1-96 characters,
using only ASCII letters, digits, underscore, dot or hyphen. Each path is a
nonempty string of at most 4096 characters; `manifest` may instead be `null`.
Missing manifests prevent qualification without erasing valid diagnostic timing.

Relative paths, including `../`, resolve against the cohort file's directory.
Local absolute paths are accepted. UNC and URI-style network paths are rejected
before accessing the declared files. Such a path makes `input_status` INVALID,
as do duplicate JSON keys, unsupported values, booleans in integer fields,
noninteger numbers, unknown keys and more than ten entries.

The cohort must be a regular, nonsymlink file no larger than 256 KiB. The existing
[CSV validator](../tools/validate_csv_bundle.py) applies its exact CSV/manifest
schemas and limits: 16 MiB per CSV and 16 KiB per manifest. Events and summary
are reopened with bounded reads, descriptor/path identity checks and exact
SHA-256/byte/row binding to the accepted validator report. The accepted manifest
declaration is retained rather than reopened. This detects changed reread bytes
even when their size and modification time are restored; it does not establish
an atomic cross-file snapshot or physical origin.

## Trace and owner requirements

Event ordinals must increase strictly. START (type 0) and GO (type 1) must be
unique if present, use mode 1-6 matching the summary and value zero. START must
match `summary.release_us`. Whenever both exist, GO follows START in ordinal
order and its unsigned release-relative offset is less than half the uint32
range. This is a chronology check, not a countdown-hold measurement.

Timing events have type 10. HEADER detail 0 must immediately follow START in
full event order and have the same timestamp. Its value is exactly `0x0101`
(M0) or `0x0105` (M1). All other timing details require value 1. The wire value 1
does not independently encode or prove the producer's full receipt token.

| Timing-detail sequence | Trace result |
|---|---|
| No timing events | NOT_RECORDED |
| `[0]` | NOT_EXERCISED |
| `[0,1]`, `[0,1,2]`, `[0,1,2,3]` | INCOMPLETE |
| `[0,x]`, x = 6-10 | EXCLUDED before source acquisition |
| `[0,1,2,x]`, x = 5-10 or 12 | EXCLUDED after source acquisition |
| `[0,1,2,3,11]` | EXCLUDED for rejected expected receipt |
| `[0,1,2,3,4]` | COMPLETE, subject to chronology checks |

Other sequences, reserved metadata, duplicates or records after a terminal are
INVALID. Source details 1 and 2 must be adjacent in full event order. Every
non-header timing record needs an earlier GO. Missing GO makes an otherwise
valid trace INCOMPLETE without a delay; a GO recorded later is INVALID. HEADER
normally precedes GO. Other event codes receive the unchanged CSV checks only.

For a full trace, release-relative unsigned offsets must satisfy
`GO <= S <= E <= D <= A`, all below `2^31`. Ordinary wrap and timestamp zero are
valid. Unfinished/excluded traces check every present GO/source/decision prefix
field in the same order, omitting missing fields. Exclusion-terminal timestamps
do not enter the arithmetic. Records are never sorted by raw timestamp: a source
event can carry an earlier timestamp than preceding decision events. Unseen
whole wraps can alias identical uint32 values and cannot be ruled out by these
files alone.

Qualification requires a COMPLETE trace with M1 HEADER, SEALED phase 3,
positive epoch, observed GO, no loss/incomplete flags and a valid manifest
declaring `closed`. START with zero epoch, or GO/non-header timing records with
zero epoch or `go_seen=0`, is an INVALID owner contradiction regardless of phase.
A closed, loss-free SEALED M1 HEADER-only canceled countdown with positive epoch
and `go_seen=0` is legitimately NOT_EXERCISED. Other owner shortcomings take
precedence and make qualification INCOMPLETE.

Reusing an identical frames/events/summary hash triple invalidates **every**
reused entry, even with different IDs. Different hashes still do not prove
independent physical trials. The analyzer does not replace excluded attempts or
reconstruct missing evidence from frames, state changes, first duty or later zeros.

## Reading the report

For a COMPLETE valid trace, the observed delay interval is `[A-E, A-S]`:

- PASS: upper delay is at most 35000 microseconds, inclusive.
- FAIL: lower delay is greater than 35000 microseconds.
- INDETERMINATE: the interval straddles that boundary.

`input_status` concerns cohort reading/schema only. `trace_status` concerns
trace grammar/time. `qualification` additionally considers owner, loss, M0,
closure and duplicate evidence. Thus a complete M0 trace can retain diagnostic
PASS/FAIL arithmetic while qualification is INCOMPLETE. Incomplete ownership or
an undersized cohort does not erase otherwise valid timing diagnostics.

Any INVALID attempt clears source/decision/applied timestamps and both delays,
and uses timing NOT_EVALUATED. Separately validated trace status can remain
COMPLETE when later invalidated by owner contradiction or bundle reuse.
Invalid CSV/manifest or an unbound reread instead leaves trace status INVALID.
`validation` preserves the unchanged CSV validator report in each attempt.

Exactly ten QUALIFIED observations make `evidence_status` COMPLETE. Any INVALID
member makes it INVALID; otherwise it is INCOMPLETE. Cohort timing stays
NOT_QUALIFIED unless evidence is COMPLETE. For complete evidence, any FAIL wins,
otherwise any INDETERMINATE wins, otherwise the cohort passes. The reported
minimum lower and maximum upper delays use qualified observations only and are
null when none qualify. All supplied valid-schema attempts remain in the report.

This interval describes observed all-front-clear acquisition to matched applied
zero receipt completion. It does not measure physical box removal, the first
PWM transition, wheel rest or the robot staying in the ring. Even a synthetic M1
cohort passing all arithmetic has `hardware_acceptance`, `transport_verified`
and `common_attempt_verified` set to false. No tuning, motor-run authorization
or P4 gate follows. The exact specification is the
[D130 contract](../state/analysis/P4_loss_analysis_contract.md).
