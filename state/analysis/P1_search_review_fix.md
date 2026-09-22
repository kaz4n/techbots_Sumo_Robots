# SEARCH pre-build review finding — 2026-09-22

Reviewer p1_next_task_audit, separate reused read-only context. MAJOR found in
uncommitted src/core/fsm.cpp:109 (original pre-fix line numbering), Search::start.
Expression normalizedHeading(context.world_bearing_deg - heading) subtracts
floats and narrows the normalized result before selecting direction. For finite
heading180.0F/world1.0e-6F, the B7 Turn's double error selects LEFT but SEARCH's
rounded antipodal error selects RIGHT. That violates the committed requirement
to capture the same shortest-turn direction for the following scan.

Action: implementation owner instructed to subtract/normalize in double and
select sign before narrowing; preserve legacy helper behavior and other modules.
Independent spec/header-only author adds mathematical near-antipode, mirror and
exact-tie regressions without reading source. No host build/test has run for this
batch yet; this is a static-review correction, not a failed test repair. No test
assertion or requirement is weakened. Final verification follows in batch evidence.

Resolved before the first build: subtraction, fmod, normalization and sign
selection all use double. Reviewer verified exact source lines110-114 and the
independent mathematical regression, including mirror and exact tie. All540
cases/11,937,972 assertions subsequently passed ASan/UBSan with exit0. No failing
test repair cycle occurred. Source hash and final review are in the review record.
