# D130 offline target-loss analyzer validation

IMPLEMENTED / HOST-TESTED / fresh-context scoped review PASS, with no open
BLOCKER, MAJOR or MINOR. No firmware, target, transport or physical result
is implied. Active software phase remains P4 under D128.

`tools/analyze_target_loss.py` consumes existing local CSV evidence and an exact
bounded cohort schema. It binds reopened bytes to the unchanged CSV validator's
accepted hashes/counts, validates D129 trace grammar and common-anchor chronology,
then calculates `[A-E,A-S]`. Ten qualified intervals produce PASS, FAIL or
INDETERMINATE against35000us. Missing, excluded, M0, lost, unclosed and contradictory
evidence cannot supply a passing cohort. All reports keep hardware acceptance,
transport verification and common-attempt verification false.

## Actual validation

Independent author froze41 spec-derived unittest methods and synthetic fixtures
without reading the analyzer. Root retained the original source, docs, tests,
fixture, plan and contract before first public execution in
`P4_loss_analysis_raw/original/` with `original_freeze.json`.

Command: `wsl -d Ubuntu -- env TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python3
state/analysis/P4_loss_analysis_raw/run_analysis.py first`.

- **112 methods PASS on first execution**, exit0:41 new,33 unchanged countdown,
  38 unchanged CSV. No skipped cases or implementation/oracle repairs.
- **13 independent private methods PASS**, including multiple grammar/time
  subcases, real symlink checks and same-size/restored-mtime mutation.
- All648 prior tracked firmware/tool/test/build inputs and all40 protected
  test/support files remain byte-exact. The tracked `.gitkeep` is also retained.
- Frozen new source `b22293705fdc00436354b41febd50f39d6b73c22b3ce913681e47306bb69a3ba`
  and test `83d86d6a45afdf9247e53aa8d54479a3f712d2302ae4e9e1e151bc4f28963647`
  remain unchanged after execution. Full hashes and commands are in the raw files.

Coverage includes exact/bound-adjacent/straddling intervals, wrap/zero/half-range,
all legal trace families and incomplete prefixes, ordering/pair adjacency,
metadata, owner/closure/loss/M0, canceled countdowns, duplicate IDs/bundles,
bounded regular-file reads and descriptor changes, hash-bound reread changes,
schema/network rejection before access, quiet read-only behavior and CLI exits.
Injection tests require the hook actually to execute; inert mocks cannot pass as
evidence of a mutation check. Fixtures are synthetic and supply no physical trial.

The reviewer's first inline launcher recorded passing tests but failed its shell
exit-status expression. That wrapper-only failure is retained. A literal review
launcher reran the unchanged source/oracle and recorded Python/tool exit0. This
was not a production failure or a silently replaced oracle. The fresh reviewer
owns only `../reviews/P4_loss_analysis_review.md` and its raw artifacts; this is a
separate same-model context, not cross-model review.

Root runner/binding evidence: `first.json`, `first.txt`, `baseline.json`,
`prior_locked.json`, `freeze.json`, `original_freeze.json`, `final_bindings.json`.
No C++ rerun was needed: no firmware or existing executable/test input changed.

## Use and remaining work

Usage/schema and explicit interpretation limits: `../../docs/target_loss_analysis.md`.
The CLI reads existing records; it does not generate a favorable missing trial,
rewrite evidence, change a tunable or contact the board. It evaluates recorded
acquisition-to-receipt timing, not physical box removal, PWM transition or rest.

Physical P4.1-4.7, D129 target/native fit, full-source WCET and gates remain pending.
Next software dependency is P4.4's bounded push-through behavior; its original
default stays0. `P4_push_through_options.md` is preparation only, not an adopted
behavior change. No positive tuning or motor-run permission follows.
