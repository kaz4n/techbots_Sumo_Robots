# D114 identified upload guard review

**PASS for the scoped guard source review: no BLOCKER, MAJOR or MINOR finding.**
This is a separate reused-context, same-model review of coordinator-owned guard
code. The reviewer authored `ui_adc_capture.py`, did not author this guard, and
does not count this report as an independent review of the capture implementation.
No human gate, upload approval, electrical qualification or executed run follows.

Reviewed exact identities:

- `tools/ui_adc_run.py`: `1aa109a2ed068ed4d21dc442aa9195b516f8df264c5a04a0b71a75949cb5d8e8`.
- `tools/board_tool.py`: `d1fda9649a30679ed9282d3b03e7a244f8c21ea51b3ded2ad6f7a83c4fb9fcc7`, diff against `bfd4f25`.
- Run contract: `b37fb854e72c02ec4b8d88cfffd67943d2a377633ccae9d9d954420f7d817c7a`.

## Findings checked

`ui_adc_run.py:39-46` admits only the fixed identifier, literal probe name,
default startup, inert upload combination. `board_tool.py:293-327` runs those
checks before target lookup/staging/transport. Absent Namespace members preserve
the prior route; ordinary probe compile-only remains available and generic probe
upload remains refused. Existing MATCH, Immediate and profile refusals remain.

`ui_adc_run.py:49-114` checks real root/regular files and nonsymlink ancestry
below root, rejects consumed attempts/outcomes including dangling links, bounds
each receipt to65536bytes, and uses the existing duplicate/nonfinite-rejecting
JSON decoder. Schema version is actual integer1. Exact fields, values, approval
bytes and all eleven file hashes bind the scope. These are workspace receipts,
not signatures protecting against a hostile editor.

`board_tool.py:329-356` loads that scope before staging, preserves actual staged
source verification and the checked compile path, and uses its returned fresh
artifact directory. `ui_adc_run.py:117-134,174-178` checks the same scope both
before and after remote hash verification, the literal source/default/32-hex-UUID
path, fixed board folder, sibling build ELF and artifact ZSK. The passive capture
input directory is not accepted as an upload source.

`ui_adc_run.py:141-187` exclusively creates, flushes, fsyncs and closes the fixed
attempt record before the one upload call. A failed launch cannot release or
reuse it. The upload uses capture=True and120s timeout, with no explicit second
reset, retries or capture/Monitor calls. Returned nonzero status preserves its
original stdout/stderr in CalledProcessError; timeout/OSError/uncertain failures
propagate and retain a separate outcome when writable. Outcome-save failure is
also failure. `board_tool.py:364-371` has no generic-upload fallback after the
identified route succeeds or throws.

## Evidence and limits

The independent guard author's final22 controlled methods pass on these exact
source hashes: `P2_ui_adc_probe_raw/guard_author/validation.json`. Final test hash
is `4cd63920370c23f6ec4b538a353c6f7dc2277bc2e032ad3fdc7eeee342e3e130`.
The first run's one mocked-stage basename failure is preserved; the approved
correction changes only that fixture basename, preserving expected paths and
assertions. This reviewer read receipts/output, not test bodies, and did not
rerun them or operate a board.

The retained AST comparison proves23 existing board functions unchanged against
`bfd4f25`, including staging, transport, checked compile, source hashing, runtime
artifact verification and policy preflight. Only `flash`/`main` changed and
`flash_profile` was added. Source inspection confirms unchanged legacy refusal
and upload branches when the new option is absent; catching SubprocessError now
also reports the new finite upload timeout. The full old145 regression execution
is separate coordinator evidence, not claimed from static equivalence alone.

At review, the original eight manifest entries were byte-identical in value and
the new probe key was absent. Live run record, approval, attempt and outcome
were all absent. Syntax parsing passes; maximum function size is24 lines in the
guard and51 in board_tool. Exact snapshots, diff, hashes, absence observations
and AST comparison are in `P2_ui_adc_probe_raw/guard_reviewer/`.

Next is coordinator integration of this result with independent capture/source/
target evidence and established regressions. Any future approval must hash the
then-final manifest and reviewed files; this report does not create the live
approval or authorize a hardware command.

## Completed established-regression binding

The coordinator's `P2_app_build_raw/ui_adc_guard_prior145.json` records exit0
for the nine established policy modules; its paired `.txt` records **145 tests,
50.727seconds, OK**. The command completed at2026-09-23T22:17:56.777518Z.
The reviewed guard1aa109a2 and boardd1fda964 hashes remain unchanged. This closes
the pending established-regression reference above without a reviewer rerun.
Exact receipt/output and amended report hashes are in
`guard_reviewer/prior145_binding.json`; the earlier review/result remain preserved.
The separate22-method guard pass and source-review verdict remain unchanged.
Any later manifest addition/final approval still needs its own exact binding;
this addendum creates neither a live run record nor hardware permission.
