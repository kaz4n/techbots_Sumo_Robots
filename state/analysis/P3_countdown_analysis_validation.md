# D127 countdown analyzer validation

2026-09-24, Asia/Dubai. IMPLEMENTED / HOST-TESTED. Contract commit `eca1c7cf`;
prior firmware commit `6b4c353b`. No firmware or board operation in this slice.

`tools/analyze_countdown.py` evaluates the existing P3.1 criterion from up to
50 explicitly identified recorder bundles. It retains exact receipt-derived
FIRST timing, wrap semantics, the 5.1 s minimum and strictly-under-5 ms spread.
The unchanged CSV validator establishes accepted byte snapshots; bounded rereads
bind calculation to those same bytes. Missing/loss-bearing/open evidence never
becomes a qualified cohort. All results retain hardware_acceptance=false.

## Executed verification

- Full WSL suite: 71 methods PASS, exit 0: 33 new independent contract methods
  plus all 38 existing CSV-validator methods, including actual C++ formatter
  integration and real symlink substitution checks. Python 3.12.3.
- Separate reviewer: seven private methods PASS on WSL and native Windows,
  including 108 FIRST payload partitions, three 50-bundle boundary cohorts,
  duplicate-bundle groups and post-validation replacement with restored mtime.
- All 38 established locked files, the validator and all prior firmware sources
  remain unchanged. No new locked test is introduced by this host-only tool.
- Production analyzer hash remains its first version:
  `1a91b857417c697bf23641f05d9d768289f8db33f154cfa05537b9eebaed9e02`.

The original public oracle had an inactive fault-injection hook: it patched a
different validator instance. Linux first ran 71 methods with four failures;
Windows ran 33 with those failures plus missing symlink-creation privilege.
The independent author corrected only this new unaccepted helper/import,
retaining all assertions and additionally requiring exactly one dependency and
one hook invocation. The reviewer approved that correction. The first corrected
full WSL run passed. See `P3_countdown_analysis_first_run.md` for failure analysis.
The full public Windows suite is not claimed as passing; private regular-file
tests did pass natively. No symlink assertion was skipped or weakened.

Original test hash `56d8b61f` and accepted corrected hash
`ec9167bd57584f48e8f87c1238a834dd6bf5cfeb473a64f0d9a1d6b5d0ee510f`
are both archived. Independent fixture `6959b8a8` is unchanged. All commands,
versions, exit statuses, original/corrected snapshots and logs are in
`P3_countdown_analysis_raw/`; the separate same-model review is
`../reviews/P3_countdown_analysis_review.md`. This is not cross-model review.

Usage and the placeholder-only schema example are in
`../../docs/countdown_analysis.md`. The tool does not generate physical trial
data. Caller-declared closure/build/origin and arithmetic success do not verify
transport, common physical origin, 50 distinct motor runs or a phase gate.

## P3 disposition and next work

D123/D125/D126 provide the required P3 software trial paths; D127 adds the
missing countdown analysis. `P3_software_acceptance_packet.md` maps these to
all seven original physical criteria. Real P3.1-3.7 data, tuning approval and
human gate remain pending under the user's hardware-at-the-end scheduling.
The next software gap is P4 reactive GO routing with openers disabled, followed
by the exact timing evidence described in SC-AO. No real gate or deadline is
modified by preparing the next software phase.
