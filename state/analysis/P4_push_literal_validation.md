# P4 push-duration build admission validation

2026-09-24, Asia/Dubai. D132 implements copied-source validation before any
board operation. Its scoped admission tests pass. D133 repaired historical test
fixtures without changing production approvals; the repeated296-method suite
now passes with zero failures, errors or skips.

`tools/board_tool.py` validates the staged config immediately after copying it.
It requires one canonical unsigned decimal declaration with value0..100,
without fixed-width truncation. Expressions, duplicate/conditional declarations,
overflowing values, malformed text and ambiguous preprocessor spellings fail
with an identified error. Splices are rejected before comment removal; code-level
digraph directives are rejected after masking comments and quoted literals.
Missing/unreadable config is an explicit failure. The staged bytes, source
hashing, compiler flags, upload guards and shipped0 value stay unchanged.

Production SHA-256 throughout the actual executions:
`bfa5ce00cc0ad72772eca48a3efcbb7af09a1e71a4d56ac5c300c377a63ad702`.

## Results and failures

- New32-method admission suite: first execution failed only three app-layout
  subcases in one new method. Independent author and reviewer confirmed existing
  app headers belong under staged `src/app/`, while bench-local headers remain
  beside the sketch. The original oracle is retained in Git2bdc6eae and the
  failure in `P4_push_literal_raw/admission.txt/json`.
- Approved narrow correction preserves all32 methods and adds exact header-byte
  and no-app-root-duplicate checks. The unchanged production then passes all32
  methods in `admission_retry1.txt/json`. `oracle_correction.json` binds the
  original/corrected hashes; no locked assertion was changed.
- Separate-context same-model reviewer ran nine frozen contract methods and
  three lexical supplements: all12 pass. These probe every bounded decimal,
  source spelling and actual staged-byte corruption, without real board access.
  See `../reviews/P4_push_through_review_raw/private_literal_*_first_run.*`.
- Wider296-method regression: FAIL,80 failed subcases across24 methods;
  zero errors/skips. Eight failures are historical P0 positive-upload fixtures
  copying today's source against old approval keys. Seventy-two are19 D118
  methods whose shared fixture rejects changed `runtime_inputs.cpp` before tool
  use. All other272 methods pass. Original output is retained in
  `P4_push_literal_raw/regression.txt/json`.
- The preserved pre-D132 tool, with identical current source and approval keys
  in an isolated temporary root, reproduces all eight P0 subfailures across five
  methods. The unchanged D118 fixture reproduces its same source-hash error.
  `prior_tool_baseline.txt/json` retains the actual failed status. This supports
  a fixture diagnosis; it does not turn failed tests into passing results.

D133 restores the exact approved historical inputs in tests only. It preserves
current tools, every assertion, production approval keys and consumed run
records. Its contract is `P4_historical_fixture_contract.md`. The same296-method
rerun passed in224.289s, exit0, after independent static review. Receipt:
`P4_push_literal_raw/regression_retry1.json/txt`; runner command:
`TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python3
state/analysis/P4_push_literal_raw/run_tests.py regression regression_retry1
historical_fixture_freeze.json` from the repository root under WSL Ubuntu.

The106-input manifest includes all tooling test modules, unchanged production
pins and consumed run records. `final_binding.json` compares684 D131 inputs:
678unchanged, exactly six named D132/D133 changes. All41 protected source files
plus their .gitkeep are exact; shipped config is unchanged. The fixture adapters'
344 existing assertion calls are syntax-identical to2bdc6eae. P0 source bytes
come from fixed local Git commit1b1d77dc after both saved staged maps/aggregates
match; a full-history checkout is required. D118 reuses the existing exact91-file
staged archive. No permanent duplicate source archive was created.

The helper's pre-execution directory-entry issue was independently found and
fixed before freezing the successful run. Its final hash and review are in
`../reviews/P4_push_through_review_raw/historical_fixture_review.md`. No public
assertion was weakened. Final combined scoped review is
`../reviews/P4_push_through_review.md` (separate-context, same model).

These are host/script checks. No actual target compilation, upload, reset,
motor run, positive physical tuning, full-source WCET or human gate is claimed.
