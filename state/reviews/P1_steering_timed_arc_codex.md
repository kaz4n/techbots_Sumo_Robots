# Separate scoped review: steering and TimedArc — 2026-09-22

Separate read-only Codex agent p1_flank_stop_review inspected dc42029 through
the frozen working tree. Coordinator saved returned findings. Not cross-model
or a full P1 gate. Verdict: **PASS, scoped review**.

BLOCKER: none. MAJOR: none open. MINOR: none.
Resolved MAJOR at tests/test_front_steering.cpp:255,277,292,304: unsupported
REQUIRE assertions changed to CHECK, preserving all predicates/subsequent checks.
Verified D-036 rows, centering/contact eligibility, profiles, wheel bounds,
mirrored requests and invalid zeros. Verified D-037 arc validation, finite bounds,
exact/adjacent deadlines, cumulative wraps, restart/reset and terminal zero latch.
Reviewed17 steering and19 arc cases, including exhaustive discrete inputs and
10000 mirrored arc cases. All established locked blobs/config unchanged vs dc42029.

Independent tools/test_host.sh and complete binary: exit0;419 cases/10,226,416
assertions, zero failures/skips. Coordinator sanitizer receipts reviewed with
same totals/exit0. Both complete23-file inert snapshots reconstructed; staged
bytes verified against reviewed originals. Approved manifest refresh only:
- bench/p0_matrix:7f488b831998820ef3a95ba295b254e28803a1cfb75693b245fcd0f80a547333
- bench/p0_timing:5b871dba27e1315fcb1d3154d535b0dec9c93de06ce111782f3411c8b88e1b87

Existing upload restrictions remain. Full Robot arbitration, re-flank sequencing,
R1/R5 actuator integration, target compilation and physical timing remain unproved.
No hardware action occurred; reviewer edited no source, tests or state files.
