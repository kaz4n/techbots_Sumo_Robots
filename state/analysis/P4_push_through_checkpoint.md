# D131/D132 working checkpoint after storage request

2026-09-24 Asia/Dubai. Base commit ac49d422; implementation and new tests are
present as uncommitted task-owned changes. Do not restart or discard them.
P4 software under D128 remains active; no new hardware action or human gate.

D131 Escape/Robot implementation preserves shipped duration 0. Recorded runs:
all 16 default host targets pass; copied-duration 20 and 100 ms M0/M1 tests and
private probes pass; configured 0 and 100 ms ASan/UBSan pass. Controlled tooling
149 methods and registry 2 methods pass; host layouts remain unchanged.
See P4_push_through_raw receipts and P4_push_through_first_failure.md. The first
20 ms M1 fixture stimulus was independently corrected; its original is retained.
Established locked tests were not changed.

The configured 20 ms timing/sanitizer run passed all 37 M0 cases and 36/37 M1
cases. The remaining frozen expectation led to an explicitly adopted D131
evidence-policy extension: deferred white excludes timing evidence, including
the first eligible arming observation. This source change is not yet validated.
The original D129 actual-escape policy was not an implementation defect.

Exact next work:

1. Read the current review. Guard the added white-only timing checks with the
   positive-duration configuration so default-0 STOP/white tie classification
   stays unchanged, as the stated contract requires. Preserve source/receipt
   precedence. This reviewer finding is still open.
2. Freeze the new independent tests/test_push_through_timing.cc (SHA-256
   493ef8b46e659fc40d8acb4204f36563b537a7dd824fe8de4418280cf4a8471e),
   updated CMake and intended timing-policy source/docs. Preserve the prior
   freeze first. Current freeze.json predates these changes; don't run it stale.
3. Ensure the private runner excludes the new public timing test object as well
   as the two original public test objects. Run configured20_timing_sanitize_retry1
   with duration20 flags configured,timing,sanitize,review; then old D129
   legacy_timing_sanitize with duration0 flags sanitize,legacy. The D131 runner
   uses one compiler process and archives results before scratch cleanup.
4. Bind final D131 source/results before modifying tooling. D132 implementation
   remains an unapplied patch in P4_push_literal_raw/implementation.patch. Its
   reviewer found a code-level %: preprocessor-digraph bypass; conservatively
   reject those directives after masking comments/quotes. Independent public
   and private tests plus the minimal old-fixture patch are already prepared.
   Freeze before first execution; archive only the small originals required.
5. Validate D132 admission and relevant tooling; finish fresh review, update
   acceptance packet/ledgers and commit bounded completed work. D131/D132 are
   not accepted merely because the tests or patches exist.

Review: ../reviews/P4_push_through_review.md. All raw failures/probes are retained.
No build was launched during the storage follow-up. Further deletion was denied
by tooling; see ../STORAGE_LOG.md. Check current free space before resuming.
