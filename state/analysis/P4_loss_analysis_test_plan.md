<!-- Records the independent D130 Python oracle before its first execution. -->
<!-- Keeps synthetic interval arithmetic and file integrity separate from hardware. -->
<!-- Root freezes these files, runs the suites and retains every actual failure. -->
# D130 target-loss analysis independent test plan

2026-09-24. Derived from adopted `P4_loss_analysis_contract.md`, the D129 trace
contract, unchanged D073/D074 schemas and independent CSV/countdown fixtures.
No target-loss analyzer implementation, production firmware bodies or new worker
output was read. No Python test, analyzer, compiler, WSL or hardware execution
was performed by this author before freezing the oracle.

New files only:

- `tests/tooling/target_loss_fixture.py`: declared synthetic trace fixtures built
  from the existing independent byte encoder. No expected value comes from the
  analyzer. Unique ordinary fixtures differ in their source times/owner epoch.
- `tests/tooling/test_target_loss_analysis.py`: 41 unittest methods covering public `analyze_cohort` and
  `main` plus real CLI contract tests; unchanged validator reports remain visible.
- This plan: coverage, decisions and limits. Hashes are returned separately.

## Coverage

The suite covers ten distinct qualifying M1 attempts, empty/nine-attempt cohorts,
inclusive35000us boundaries, strict failure lower bound, straddling intervals,
FAIL-over-INDETERMINATE aggregation and qualified-only extrema. It preserves
diagnostic intervals for M0, loss, missing closure and incomplete cohorts without
creating a hardware or physical-acceptance claim.

Trace tests enumerate every legal unfinished prefix and exclusion shape; reject
duplicate, unknown, reserved, missing, reordered and post-terminal records;
check exact header metadata and ID1; and verify HEADER/START and source-pair
adjacency in complete event order. Ordinals must increase, while unrelated event
payloads/timestamps remain opaque. Frames, FIRST_NONZERO and STATE_CHANGE cannot
replace missing trace records. All six modes, timestamp0, natural wrap, equal
boundaries, half-range ambiguity and every ordered timestamp boundary are tested.

Owner tests cover every lifecycle class, every D074 reported-loss field, absent/
open/unknown/closed manifests, accepted partial declarations, M0 and all explicit
epoch/GO contradictions independent of owner phase. Invalid owners and reused
hash triples preserve trustworthy decoded trace status but clear every timestamp
and interval. Invalid validator/manifest or changed reread instead prevents
trusted trace decoding. Reused aliases and separate identical copies invalidate
every reused member, without silently dropping attempts.

Input tests cover exact historical values and schemas, bool/float/type errors,
duplicate JSON keys, malformed encoding, IDs and path limits, attempt count,
local absolute and parent-relative resolution, UNC/network rejection before
bundle access, exact256KiB cohort bound, missing/nonregular/symlink files and
oversized CSV members. Existing validator format checks are reused unchanged.

Snapshot tests change event/summary bytes after accepted validation while
preserving size and restoring mtime, alter accepted hash/byte/row metadata,
substitute symlinks with identical bytes, and inject descriptor type/identity/
size/mtime changes. Every postvalidation hook must actually run exactly once;
descriptor hooks must reach the relevant real before/after check. The helper
locates the actual public validator dependency by capability and exact source
path rather than assuming an import alias or a separate module instance. Both
module and directly imported public-function forms are supported. Manifest and
frames are deleted after accepted validation to prove they are not reread.
Actual stream reads must remain bounded; input bytes must remain unchanged.

Import/API quietness and a guarded subprocess verify no writes, external actions,
board-tool reads or live configuration dependence. CLI/main cover PASS, FAIL,
INDETERMINATE, incomplete and invalid reports; main returns an integer and CLI
returns0 only for qualified PASS. Help/usage and unsupported mutation/tuning/
upload options are checked. Test-side subprocesses launch only the local Python
CLI/audit guard; the analyzer is forbidden from launching external actions.

## Settled pre-freeze interpretations

A closed, loss-free SEALED M1 header-only cancellation with positive epoch and
`go_seen=0` is NOT_EXERCISED; other owner incompleteness still takes precedence.
UNC/network declarations fail cohort input validation before bundle access.
Whenever both START and GO exist, their ordinal order and unsigned release
anchor are checked even without a candidate. This analyzer adds no countdown
hold threshold. A GO after HEADER is normal; a GO after a non-header trace is
invalid. Missing GO prevents interval calculation and qualification.

Present source/decision prefixes are checked even for excluded/incomplete
traces. Diagnostic cancellation timestamps are not physical timing anchors.
Owner contradictions/reuse may preserve COMPLETE trace status while forcing
INVALID qualification and null timestamps/delays; untrusted decoding is INVALID.

## Execution and limits

Root should freeze all three hashes before running this suite and the unchanged
CSV/countdown suites under Linux/WSL. Symlink prerequisites are real requirements,
not skipped tests. Root retains original oracles and first-run failures before
any adjudicated correction. Existing tools/tests and all40 protected firmware
tests remain untouched by this task.

This is synthetic host evidence and interval analysis only. It cannot verify
hardware origin, atomic cross-file capture, physical independence, unseen whole
timer wraps, motor permission, first electrical transition, box-removal time,
wheel rest, ring retention, P4.2 physical success or a phase gate. No firmware,
config, wiring, board state or motor action is authorized by these tests.
