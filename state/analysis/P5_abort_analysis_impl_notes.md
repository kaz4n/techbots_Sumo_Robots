# D136 opener-abort analyzer implementation notes

2026-09-24. Initial implementation is **written, not executed or validated**.
The parent owns execution of the independently frozen74 public and19 private
cases. Their bodies were not read by this implementation author.

## Objective and scope

Implement the adopted `P5_abort_analysis_contract.md` as one local read-only
companion, `tools/analyze_opener_abort.py`, with the public `decode_cue`,
`analyze_cohort` and `main` seams. Existing D130 tooling, CSV validator/schema,
tests, firmware, configuration, CMake and ledgers are unchanged.

Contract bytes SHA-256:
`be0de4d832b5794a96e1d87e35234c7291e0d63f68dba30e2d0b6cdb72c79c46`.
First implementation bytes SHA-256, returned to the parent before any execution:
`9891c3eaa8a283d918d1e253a691c55c3d7d8ad3b9574eefcc14452f1e8b7843`.

## Implemented structure

- Reuse the small D130 local-file/report pattern and import only the unchanged
  `validate_csv_bundle.py` companion. The new tool contains no shell, subprocess,
  network, board or compilation invocation and no shared analysis framework.
- Admit the exact cohort/source schema and reject nonlocal paths before any
  declared-file reads. Bound cohort/config reads, verify descriptor/path identity,
  hash the historical config once and retain its verified literal values.
- Mask C++ comments/literals and track preprocessor nesting without evaluating
  C++. Extract the seven canonical decimal declarations, permit ordinary reads
  in other declarations, and reject unsupported declarations, macro/conditional
  mentions, splices, digraph directives, duplicates and unsupported profile values.
- Validate every supplied bundle even if the source descriptor's configuration
  fails. Reopen events and summary against accepted hashes, byte counts and rows;
  retain the validator's accepted manifest without a second manifest read.
- Decode the D135 cue table independently from the published contract, including
  DIRECT snapshot restrictions, SIDESTEP outer masks, ARC phases and WAIT's
  inner SIDESTEP_R interpretation. No producer or Fusion logic is executed.
- Check complete event ordering, START/GO owner agreement, exact HEADER/profile,
  admitted timing grammar, decision-suffix adjacency and read-anchored modular
  chronology. Reads may precede GO; decisions may not. Receipt/source-failure
  diagnostic times do not establish elapsed measurements.
- Preserve separate wire, logical, elapsed and qualification outcomes. Source,
  owner, manifest and duplicate contradictions invalidate evidence; loss, M0,
  absent declarations and unconfirmed closure disqualify otherwise valid
  diagnostics. HANDOVER_FAILED remains an evaluated logical failure when eligible.
- Aggregate only qualified COMPLETE elapsed values and preserve trusted logical
  failures. Hardware-reported PASS is only ELIGIBLE for separate physical review;
  all four acceptance/verification booleans remain false.

Functions are deliberately bounded and split by source admission, wire decoding,
owner qualification and aggregation. This is a source description, not a passed
test or claim that the implementation meets every contract requirement.

## Evidence and next action

The author read the adopted D136 contract, the D135 contract's published metadata
table, existing D130 analyzer, unchanged D074 validator/schema and D134's pure
restricted-literal patterns. No new test body was read. The first implementation
was not imported, syntax-compiled, executed or tested before its hash was returned.
The parent can now run the frozen independent tests and source review. Retain any
first failure before a bounded implementation correction; do not edit or weaken
the independent or existing test expectations.

The separate native optimization loop is stopped: candidate1 and candidate2
compiled but failed the conditional loader model by24 and32 bytes respectively.
Both are preserved in `P5_default_fit_experiment.md` and its raw evidence. This
analyzer implementation neither repairs nor clears that target-fit blocker and
does not provide physical timing, deployment authorization or a phase gate.
