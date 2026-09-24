# Offline countdown analysis

`tools/analyze_countdown.py` evaluates P3.1 using existing local recorder CSV
bundles. It checks 50 receipt-derived first-nonzero duty intervals against the
declared historical 5000 ms countdown plus 100 ms margin. Every interval must
be at least 5,100,000 us, and the cohort spread must be strictly below 5000 us.
It reads files only and never changes firmware, configuration or evidence.

Run from the repository root:

```text
python tools/analyze_countdown.py path/to/cohort.json
```

The public Python API is `analyze_cohort(path)`. The CLI prints one JSON report
and exits 0 only when `timing_status` is `PASS`. Other analysis outcomes exit 1;
invalid CLI usage exits 2. Paths in the cohort resolve against its directory.
The tool does not read today's configuration to infer settings for older runs.

This is a **synthetic schema illustration**, with placeholder paths and no
trial observations or fabricated results:

```json
{
  "schema_version": 1,
  "countdown_ms": 5000,
  "countdown_margin_ms": 100,
  "attempts": [
    {
      "id": "synthetic-example-01",
      "frames": "synthetic-example/frames.csv",
      "events": "synthetic-example/events.csv",
      "summary": "synthetic-example/summary.csv",
      "manifest": null
    }
  ]
}
```

The referenced files are not supplied by this example. A real cohort identifies
each attempted run explicitly; do not relabel synthetic files as hardware data.
Zero through 50 entries are accepted, but only 50 qualified, unreused bundles
can produce a complete timing result. IDs must be unique ASCII identifiers of
1 through 96 characters, using letters, digits, underscore, dot or hyphen.
Paths are nonempty strings of at most 4096 characters; only `manifest` may be
null. Extra or duplicate JSON keys and unsupported hold settings are rejected.
The cohort must be a regular local file of at most 256 KiB, not a symlink.

Each bundle first passes the unchanged D074 CSV validator. Events and summary
are then reopened with bounded reads and file-identity checks, and their exact
bytes, hashes and row counts must match the validated snapshots. The already
validated manifest is retained without another read. This is not an atomic
cross-file snapshot or proof that all files came from one physical attempt.

The relevant markers are START_RELEASE (type 0), GO (type 1), and
FIRST_NONZERO_DUTY (type 2). Each must occur once in that ordinal order. Event
ordinals must increase strictly. START/GO mode and START time must agree with
the owner summary. FIRST's wheel mask preserves actual nonzero duty even when
its encoded duty byte rounds to zero; packed zero is not grounds to discard it.
GO and frames never substitute for receipt-derived FIRST.

Unsigned timestamp offsets handle an ordinary 32-bit wrap. Offsets at or above
half the counter range, or FIRST preceding GO, leave chronology incomplete and
do not produce an early-delay conclusion. Equal timestamps remain valid. When
GO is missing but START and FIRST form a valid interval, that interval remains
visible as a diagnostic while the attempt stays incomplete.

Qualification requires SEALED owner phase 3, a positive epoch, an observed GO,
no reported loss or incomplete data, and a valid manifest declaring `closed`.
Absent, open or unknown closure prevents qualification. Sealed complete markers
with a zero epoch or unobserved GO contradict the owner. Reusing an identical
frames/events/summary hash triple invalidates every occurrence, even under new
IDs. The report retains each attempt and its unchanged validator report.

`input_status` describes the cohort schema. `evidence_status` distinguishes
complete, incomplete and invalid evidence. `timing_status` is `NOT_QUALIFIED`
unless all 50 attempts qualify; it then becomes `PASS` or `FAIL` from the hold
and strict spread tests. Cohort minimum, maximum and spread use qualified
observations only. A valid observed early interval remains visible in its
attempt even when missing closure, loss or cohort size prevents qualification.

Caller-declared closure and origin are not transport or hardware verification.
Synthetic evidence can pass the timing arithmetic. The report always leaves
`common_attempt_verified`, `transport_verified` and `hardware_acceptance` false.
A timing pass does not measure physical wheel motion, establish a calibrated
clock, tune the robot, or pass a human phase gate.
