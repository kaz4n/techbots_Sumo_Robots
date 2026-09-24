# D130 target-loss analyzer scoped review

Date: 2026-09-24 Asia/Dubai. Reviewer: separate fresh-context same-model Codex
reviewer, independent of the implementation and public test author. This is not
cross-model or human review. Review edits are confined to this report and
`P4_loss_analysis_review_raw/`. Production, public tests and shared ledgers are
outside the reviewer's ownership.

Status: PASS for the bounded D130 offline analyzer. No open BLOCKER, MAJOR or
MINOR. The first frozen production and public oracle pass, all 13 private methods
pass, and the final reviewed source/oracle/baseline bindings match. This is
software analysis evidence, not physical P4.2 acceptance or a human phase gate.

## Scope and authority

The reviewed scope is the read-only D130 offline interval analyzer adopted by
D051/D128/D130, using D129 event evidence and the unchanged D074 CSV validator.
AGENTS, current handoff/progress/decisions, P4 prompt and D129/D130 contracts were
loaded. The current date is Thursday 24 September: the 28 September scope cut
and 1 October 21:00 freeze have not yet arrived. P4 software scheduling does not
prove P0-P4 physical acceptance, target qualification, motor-run authority or a
human phase gate. No board, network, upload, reset or motor action is performed.

## Independent expectations

`private_freeze.json` binds the adopted clarified contract `064b527f7c43` and
spec-derived private oracle `b0673d688162`, frozen before analyzer execution and
before reading public test bodies. The oracle has 13 test methods with multiple
adversarial subcases. It uses independently generated D073 CSV wire bytes and
D074 manifests; all fixtures are synthetic.

The plan covers ten distinct qualified attempts; inclusive 35,000 us bounds,
straddles and failures; uint32 wrap, timestamp zero, equality, reversed and
half-range time; every legal trace grammar family and representative forbidden
shapes; START/GO identity and ordinal placement; source adjacency; arbitrary
unrelated events; prefix time checks while ignoring exclusion-terminal times;
owner contradictions and reused-bundle invalidation with trusted trace retention
and timestamp/delay scrubbing; M0/loss/open-owner diagnostic retention; exact
cohort schema, local relative paths, network rejection, symlink/size limits and
CLI results; and same-size restored-mtime evidence mutation plus retention of
the accepted manifest without rereading.

Clarifications adopted by the coordinator before execution are consistent with
the contract: START/GO chronology is checked even without a trace; a closed
loss-free positive-epoch M1 canceled HEADER is NOT_EXERCISED despite go_seen0;
and declared network paths are cohort-schema errors. These do not create
physical-origin, atomic-snapshot or common-attempt guarantees.

## Findings

No open BLOCKER, MAJOR or MINOR.

## Static source review

Reviewed first implementation `tools/analyze_target_loss.py` SHA-256
`b22293705fdc00436354b41febd50f39d6b73c22b3ce913681e47306bb69a3ba` and documentation
`docs/target_loss_analysis.md` SHA-256
`6a375f7f5032ed033844d4a5391a9d16131fe1a53873154d266a49416d3c71cb`.

- Lines 16-19 load the exact sibling unchanged CSV validator. Lines 334-345
  retain its returned report and decode only accepted hash-bound events/summary.
  No frame/manifest reread upgrades provenance or asserts an atomic snapshot.
- Lines 48-134 enforce local paths, exact cohort schema, historical values,
  regular bounded reads and descriptor/path identity checks. Lines 170-176 bind
  reopened bytes, hash and row count to the accepted validator report.
- Lines 203-268 enforce all-event ordinal order, unique START/GO payloads,
  release identity, complete trace grammar, HEADER position, source adjacency
  and common unsigned-anchor chronology. Exclusion-terminal timestamps are
  excluded from prefix arithmetic; ordinary wrap and timestamp zero survive.
- Lines 271-326 keep interval arithmetic separate from owner qualification.
  Missing GO never synthesizes a delay; M0/loss/closure remain diagnostic;
  explicit owner contradictions invalidate while preserving trusted trace
  classification. Lines 160-167 scrub every invalid timing field and delay.
- Lines 352-382 invalidate every duplicate hash-triple member and compute
  extrema from qualified attempts only. Exactly ten are needed for complete
  evidence; cohort FAIL precedes INDETERMINATE, which precedes PASS.
- Lines 137-145 keep hardware, transport and common-attempt acceptance false.
  The entire source contains no shell, network, board, subprocess or file-write
  execution path. CLI status is tied to cohort timing PASS at lines 401-408.
  Documentation distinguishes the observed acquisition/receipt interval from
  removal time, first PWM transition, mechanical rest and physical P4.2.

## Private execution

The frozen 13-method oracle passed on its first Python execution (0.148 seconds).
The initial inline WSL launcher then failed while formatting/exiting its shell
status: `exit: : numeric argument required`. The original log and status artifact
are retained as `private_linux_initial.*`. This was a launcher failure after
Python reported OK, not a production/test failure. Only the launcher changed:
`run_private.sh` is a literal script that avoids PowerShell/WSL interpolation.
The unchanged oracle and unchanged production reran with all 13 methods PASS
(0.149 seconds), `private_linux.exit` equal to 0 and tool exit 0. No assertion,
expected result, fixture or production change was made to obtain that result.

Both runs used WSL Python, `TMPDIR=/dev/shm` and `PYTHONDONTWRITEBYTECODE=1`.
The reviewer held the coordinator-assigned serial WSL slot and released it
immediately after the confirmed run. Real symlink rejection, post-validation
same-size/restored-mtime replacements and accepted-manifest no-reread were all
exercised without skips. Generated data were temporary synthetic fixtures.

Read-only Git scope checks found no changes to `src/`, `tests/locked/`, the CSV
validator or countdown analyzer.

## Public oracle and final binding

After private expectations were frozen and executed, the reviewer inspected the
public fixture, all 41 new test methods, test plan, frozen hashes and runner.
The public oracle derives expected interval/qualification results from the
contract and independent CSV fixtures. Its mutation hooks require actual
invocation; descriptor probes reach actual read checks. CLI subprocesses run
only local Python test targets. There are no skips or weakened assertions.

`state/analysis/P4_loss_analysis_raw/first.json` records Python 3.12.3, exit 0,
and the exact command for the first public execution. Its `first.txt` reports
112 methods PASS (41 new analyzer, 33 unchanged countdown, 38 unchanged CSV) in
6.906 seconds. No public oracle or production repair was needed. The first
six-file public freeze is unchanged: analyzer `b2229370`, docs `6a375f7f`, new
test `83d86d6a`, fixture `33291a25`, plan `1d9875d0`, contract `064b527f`.

The reviewer independently recomputed 694 final bindings at 10:47:29 Dubai:
648 prior tracked files, all six public frozen files and all 40 protected locked
files. Every hash matches; `baseline_binding.json` records zero failures.
`evidence_bindings.json` binds reviewer inputs and receipts. Full firmware tests
were not rerun for this offline-only tool because firmware and all prior tracked
code are byte-identical; unchanged CSV/countdown suites are the relevant
regression checks. No target compile or hardware test is claimed.

## Verdict

PASS for D130's offline interval analyzer and its bounded synthetic host tests.
No hardware acceptance, target qualification, motor-run permission or GATE P4
follows. Physical trials and deferred target/native qualification remain open.
