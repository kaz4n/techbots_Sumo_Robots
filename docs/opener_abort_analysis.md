# Analyze qualified opener handover timing

Usage follows [D136's exact contract](../state/analysis/P5_abort_analysis_contract.md);
implementation validation is pending. This offline
tool analyzes existing local recorder bundles. It never compiles, uploads,
connects to the robot, or grants permission to run motors.

```sh
python tools/analyze_opener_abort.py logs/opener-cohort.json
```

One cohort represents one mode and at most ten attempts in their original trial
order. Use separate cohorts for left and right. Keep failures and exclusions;
do not replace them with favorable later attempts. A passing result needs ten
qualified records. The original physical trial roster remains separate evidence.

The JSON descriptor below shows one diagnostic attempt. Replace the identity
placeholders with the recorded values and list every original attempt. Relative
paths resolve from the cohort file's directory; local absolute paths are also
accepted. Network/URI paths are rejected.

The schema rejects unknown/duplicate keys and booleans in integer fields. Attempt
IDs must be unique,1–96 ASCII letters/digits/underscore/dot/hyphen; paths are
nonempty and at most4096 characters. A null manifest is allowed for incomplete
diagnostics. Valid unknown/open closure or reported loss prevents qualification;
an invalid supplied manifest or inconsistent loss summary remains invalid.

```json
{
  "schema_version": 1,
  "mode": 3,
  "source": {
    "firmware_revision": "<40-or-64-lowercase-hex-revision>",
    "source_sha256": "<64-lowercase-hex-staged-source-hash>",
    "config": "source/config.h",
    "config_sha256": "<64-lowercase-hex-hash-of-these-config-bytes>",
    "flags": "-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1"
  },
  "attempts": [
    {
      "id": "direct-01",
      "frames": "direct-01/frames.csv",
      "events": "direct-01/events.csv",
      "summary": "direct-01/summary.csv",
      "manifest": "direct-01/manifest.json"
    }
  ]
}
```

Use the exact historical configuration, not today's checkout. The supported
subset contains unique unconditional canonical uint32 declarations for TICK_US,
ATTACK_ENTER_TICKS, MODE_ARC_ENABLED, MODE_WAIT_ENABLED, LOG_HZ,
LOG_EVENT_CAPACITY and LOG_FRAME_WINDOW_MS. Decimal literals need a contiguous
U/u suffix; expressions, macros and conditional declarations are unsupported.
Ordinary unconditional uses in other constants are allowed. This version requires
25 Hz, 4096 events and a 200000 ms frame window; it does not change those values.

The accepted flags are the exact displayed string or its MOTORS_ALLOWED=1
equivalent. M0 remains diagnostic and can never qualify a cohort. An M1
declaration is accepted only as recorded evidence; changing a declaration cannot
turn an M0 run into an M1 run or authorize any deployment.

The analyzer reuses the unchanged CSV validator, binds reopened event/summary
bytes to its hashes, and checks the declared source/config identity. A qualified
attempt must be sealed, closed, loss-free, source-bound and M1, with explicit GO
and the permitted D135 trace. Exact reused bundle triples invalidate every reused
entry. Different hashes still do not prove independent physical trials.

For a complete trace, it checks the recorded current-perception handover and
computes unsigned A-D: application receipt time minus qualified decision time.
PASS means A-D is at most historical TICK_US, including equality. An explicit
HANDOVER_FAILED is an evaluated logical failure, even without an application
timestamp. Late values remain visible. Missing tails, excluded traces and lost
events cannot be turned into successful trials.

| Output | Meaning |
|---|---|
| timing_status PASS | Ten qualified records all pass their logical/timing checks. |
| timing_status FAIL | Ten qualified records include at least one evaluated failure. |
| timing_status NOT_QUALIFIED | Evidence is incomplete or invalid; inspect each attempt and errors. |
| declared_physical_trials_status ELIGIBLE | A passing cohort declares ten hardware-origin records; external physical review is still required. |

The command prints one JSON report and exits0 only for timing_status PASS,
1 for other analysis results, and2 for usage errors. Hardware acceptance,
transport verification, common-attempt verification and producer-semantics
verification remain false in every report, including PASS.

The wire does not prove physical target onset, cue age, full-token ownership,
acknowledged EN, full tick WCET, clock calibration, deployed-image identity or
physical behavior. It relies on separately reviewed producer semantics for
omitted fields. Neither this report nor a source hash replaces those checks,
fresh run permission, the other P5 criteria, or the human phase gate.
