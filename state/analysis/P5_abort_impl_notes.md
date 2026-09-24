# D135 scoped opener, codec and build-profile implementation

2026-09-24. Objective: implement the adopted qualified-abort observation hooks,
wire metadata admission and named inert wrapper while the coordinator owns
headers, Robot/Runtime integration and validation. No test bodies were read.

Modified source:
- `src/core/openers.cpp`: conditional current-call pulses at the existing DIRECT,
  Flank and WAIT HOLD predicates; saved-front-only and natural-terminal outcomes
  remain separate. Phase is captured before a detected abort terminates a script.
  Advancing primitives do not manufacture terminal outcomes. WAIT forwards its
  inner Flank pulse and clears retained pulses before every subsequent step.
- `src/core/logframe.cpp`: Event10 packing is available to either exclusive
  profile; P4 metadata remains unchanged. P5 uses its exact header/detail/value
  table and independent packed mode/phase/cause/mask/snapshot validation.
- `tools/board_tool.py` and `tools/app_build_policy.py`: admit only the named
  default-startup `opener_timing.ino` route with exact compiler-wide flags
  `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1`. Reuse existing sketch
  override and pinned-property checks; no upload allowlist entry or source key.
- `bench/opener_timing/opener_timing.ino`: actual NativeSources, UnoQPort and
  Runtime with empty SetupGrants, ordinary opener selection and exclusive-profile
  assertions. No local profile/MATCH/MOTORS definitions or new I/O.

Evidence: source diff inspected and `git diff --check` passed for the four
modified tracked source files. The new wrapper is23lines. No compiler, test,
network, board operation or commit was executed by this worker. The coordinator's
independent frozen validation is the next action; this note is not a PASS claim.

Required validation includes exact legacy/default/P4 layouts and behavior,
exhaustive P5 wire acceptance, actual predicate/phase pulses and terminal replay,
same-call phase advancement, deadline ties, snapshots, both mirrors and WAIT's
inner-phase forwarding. Tool tests must cover exact flags/properties, startup,
MATCH/conflicting profiles, source wrapper invariants, sketch overrides and
upload refusal. Robot/Runtime ownership, source chronology and applied receipts
remain the coordinator's implementation and independent test scope. Native fit,
clock qualification, physical10/10 trials and human gates remain unproved.
