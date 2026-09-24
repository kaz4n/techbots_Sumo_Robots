# D131/D132 working checkpoint - user-requested pause

**Latest checkpoint: 2026-09-24, 11:40 Asia/Dubai.** The user
explicitly paused for network disconnection. No build, test process or board
operation remains running. Test-author/reviewer turns were interrupted. Resume
only when the user resumes the goal. This latest section supersedes the older
step list below, retained as the preceding checkpoint.

D131 validation is finished at host scope: configured20/timing1 ASan/UBSan passes
42 public and14 private cases per M0/M1; oldD129 sanitizer passes30 per M0/M1.
Both new white-only predicates are gated on positive duration, preserving the
default0 STOP/white classification. All684 frozen inputs and40 prior protected
files were verified before the D132 change; final_binding_before_D132.json binds
that state. Shipped config remains exact0. Final review still depends on D132.

D132 patch is now applied to tools/board_tool.py, SHA-256
bfa5ce00cc0ad72772eca48a3efcbb7af09a1e71a4d56ac5c300c377a63ad702.
The three old tooling files received only four canonical-config fixture additions;
originals are in P4_push_literal_raw/original. New32-method oracle is frozen as
fc1ca53858d5f55d3d6d08de5ac766cbf3c6e574811fb7c00e127851625f1caa.
The first admission run finished with three failing subcases in one new method:
app stages at0/20/100 expect output/local.h, which is absent. All other31 methods
pass. Exact failure and hashes: P4_push_literal_raw/admission.txt/json and freeze.json.
No fix or oracle amendment has been made; no broader D132 regression/private run
has started. This is a failed run, not D132 acceptance.

**First task on resume:** independently adjudicate that app-header layout
expectation against the required existing staging layout (the author had only
just received this task when interrupted). Inspect the source separately as
coordinator/reviewer. Preserve the original frozen oracle/failure before any
justified new-test correction. Then run the admission retry and focused regression
runner, reviewer12 private methods, finalize source bindings/review and ledgers.
Do not repeat passed D131 matrices without a relevant source change. Target fit,
full-source WCET, physical trials and human gates remain pending.

---

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
