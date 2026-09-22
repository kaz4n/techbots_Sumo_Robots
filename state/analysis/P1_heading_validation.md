# GO heading reference validation - 2026-09-23 Asia/Dubai

D-059 contract fd40a5b and numerical clarifications0a63190/6e57949 precede
independent tests. Root owns public interfaces and fsm.cpp implementation;
separate test-author uses specifications/public headers only. Existing FSM method
bodies, config values and established locked tests are unchanged. Implementation
and31 new cases are committed4671c8b. ca82293 also clarifies the existing escape/
opener entry comments: nominal coordinates are permitted, synthetic measurements
are not, and an escape's inward result uses its supplied coordinate domain.

HeadingReference preserves raw continuous yaw for Fusion while providing a
separate logical match coordinate. Missing-at-boot IMU retains nominal timed
fallback; first healthy recovery anchors without moving captured references or
restarting timers. Healthy malformed coordinates, unrepresentable differences
and a second distinct GO latch a fault which the future Robot must inhibit.
The helper itself neither writes motors nor claims complete Robot integration.

Separate reused read-only scoped review: ../reviews/P1_heading_codex.md. It found
one pre-build MAJOR: a negative non-tie near the antipode could round to excluded
-180 and then be remapped to+180, reversing the shortest-turn side. The corrected
conversion uses the closest interior negative float only for that narrowing case;
exact double antipode ties remain+180. The public contract and independent test
requirements explicitly preserve this distinction. No failed test was weakened.
Frozen corrected source SHA256:
9334be82f508064e554a322ac7c11be598da73ff49d0cf80fd09dfbf94bc25cb.

Current directional projection retains checked double(raw-origin) until after
angle reduction and small-bearing addition. Example: origin-1F/raw16777216F
has exact match16777217 although the published float is16777216; bearing+15
projects152 degrees. Canonical retained world input is (-180,180]. Read-only
invalid projections are finite zero/invalid and cannot mutate history or age.

The reviewer independently reconstructed all23 staged files per sketch before
approving these exact inert-source manifest entries:
- matrix 04441e9f3b22f61c6fd85afd64ab41bc66b5e36e234177561eefb495f9bcb29c
- timing bbf6c22fb99702e59c0c472c6145b025f2df08e5dd04d0664e7df3e31a343456
P1_heading_inert_proposed.json records each file hash. Six source files differ
from2a3714e: fsm.cpp/fsm.h/countdown.h/motion.h/edge.h/openers.h; other17 remain
unchanged. The prior four-file approved map was superseded by the comments-only
edge/opener clarification; the reviewer approved the final full maps separately.
An earlier proposal preceded the MAJOR fix and was never approved or installed.
Snapshot approval is source review only, not a target build or hardware result.

Normal and ASan/UBSan validation PASS807 cases/12,233,461 assertions, no failure
or skip, exit0. CTest1/1 passes1.85s; direct normal and instrumented binaries report
the same totals. Raw commands/outputs: P1_heading_host_20260923.txt and
P1_heading_sanitize_20260923.txt. The reviewer independently reran the released
normal binary: P1_heading_reviewer_host_20260923.txt, identical totals/exit0.
Both precision regressions pass. No implementation repair after the test freeze.

Tooling passes116/116 in39.114s initially, and again in40.767s with the final
comments-inclusive manifest; exit0 for both. Raw receipts:
P1_heading_tooling_20260923.txt and P1_heading_tooling_run2_20260923.txt.
The final rerun is justified
by the exact staged-byte change, not a weakened guard. New independent test SHA:
863dd145be8d6e81bcb39e692a061ddbfd529eb3552bacd8417caad66acbead3.

Final scoped review PASS with no open BLOCKER/MAJOR/MINOR. The original MAJOR
remains documented with its counterexample/fix and independent runtime closure.
The reviewer also rechecked exact source/stage/manifest bytes after all validation.
This is a reused separate Codex context, not a fresh or cross-model full gate.

Current USB get-state returned device/exit0. Actual board-side compile-only of
inert timing/default sourcebbf6c22 PASSED exit0, MATCH0/MOTORS_ALLOWED0:
74,008B program,33,964B globals for that inert sketch. Receipt:
P1_heading_target_compile_20260923.txt. No upload/reset/start requested; existing
uploaded matrix remains distinct. Complete app compilation is still outstanding.
While waiting for the quiet compile, an auxiliary read-only pgrep probe failed127
because ADB remote-shell quoting exposed its pipe; corrected quoted probe had no
matching process/exit1 as compilation finished. Neither was a compilation failure
or board mutation. Compile itself exited0 without repair or retry.
Raw provider continuity, sensor validity/freshness, actual MotorGate writes,
full-control WCET, complete Robot/app and every human phase gate remain pending.
