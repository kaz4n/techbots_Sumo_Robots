# D138 informational READY and battery status

2026-09-24 Asia/Dubai. **IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.** Original P7.2,
B13 and the adopted [contract](P7_readiness_contract.md) define the scope.
D138 observes existing START admission and the actual applied, inhibited IDLE
context; it adds no motion permission, setup grant, pin or control input.

Public interfaces are committed in36a96bd2. First implementation and independent
test source are retained in d19f8964. The fresh same-model test author read the
contract/public headers/fixtures, not companion implementation. Its frozen draft
contains19 pure/core and10 Runtime cases; configured Runtime cases use synthetic
button windows in an isolated copy. They are not electrical measurements.

The initial normal build failed before test execution on `memset` of a new test
Guard containing a non-trivial Frame (`-Werror=class-memaccess`). Original
[freeze](P7_readiness_raw/freeze.json), [receipt](P7_readiness_raw/normal_first.json)
and [compiler output](P7_readiness_raw/normal_first.txt) are retained. The independent
author replaced only that initialization with typed array fills. A second new
test required parentheses around an unchanged doctest disjunction; its original
[failure](P7_readiness_raw/configured_first.json) is also retained.

The first configured execution passed30/31 cases per variant. Its only failure
was a new test's unsupported assumption that the IDLE battery warning waits for
the governor's voltage filter. The spec-only author and separate reviewer both
confirmed B14's immediate warning and the established Robot tests. The corrected
new case requires the warning plus explicit IDLE, valid voltage and raw9000
preconditions, preserving marker/no-R/zero-output checks. Original source and
[failed execution](P7_readiness_raw/configured_retry1.json) remain;
[adjudication](P7_readiness_test_draft/runtime_retry2_adjudication.md) records scope.
No firmware, established assertion or protected test was changed to obtain a pass.

## Executed evidence

| Check | Actual result / receipt |
|---|---|
| Focused ordinary M0/M1 |20cases /22118assertions each PASS; [normal retry](P7_readiness_raw/normal_retry1.json) |
| Full ordinary regression and profile suppression |All22CTest targets PASS,26.97s execution; [full run](P7_readiness_raw/full_first.json) |
| Configured public and private M0/M1 |29public+2private cases each PASS;104489/104854assertions; [configured final](P7_readiness_raw/configured_final.json) |
| Ordinary sanitizer M0/M1 |20cases each PASS, ASan/UBSan; [receipt](P7_readiness_raw/sanitizer_final.json) |
| Configured sanitizer M0/M1 |31cases each PASS, ASan/UBSan; [receipt](P7_readiness_raw/configured_sanitizer_final.json) |
| Exact MATCH compile-only |PASS on UNOQ; [native validation](P7_readiness_native_validation.md) |
| Source/ABI/loader/import model |Conditional peak261280B,864Bspan/860Blargest payload;62imports;16type sizes/alignments and72legacy offsets unchanged |
| Independent software review |[Fresh-context same-model review and scoped verdict](../reviews/P7_readiness_review.md); no cross-model or human gate claim |

The full run froze683inputs. The final configured-only test correction changes
no ordinary compiled code: four `g++ -E -P` executions prove byte-identical M0/M1
translation before/after in [equivalence evidence](P7_readiness_raw/default_equivalence.json).
All other full-run inputs are unchanged. Final focused runs freeze687inputs in
[the final manifest](P7_readiness_raw/freeze_final.json). The native source matches
all103frozen src inputs and102staged files; host-test corrections cannot alter it.

Reproduce the captured host profiles with
`wsl -d Ubuntu -- env TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python3 -B state/analysis/P7_readiness_raw/run_host_final.py <new_label> <flags>`.
Use `configured,private`, `sanitize,private` or `configured,sanitize,private`.
The runner verifies frozen input bytes, uses one compiler in owned RAM scratch,
preserves output/exit status and releases scratch. Labels cannot overwrite earlier
receipts. Byte freezes describe the original working inputs; preserve their exact
bytes when reproducing rather than silently accepting newline-converted copies.

Updated operator-document links, unchanged protected sources and final source
binding are checked separately in the retained closure receipt. The review
report owns its scoped verdict; this packet does not substitute for a phase gate.

## Physical and release limits

R is a live blinking informational symbol, not countdown::READY or permission to
run motors. The exact threshold pixel reports the accepted floating-point voltage,
not calibrated physical accuracy. Unbound legacy display samples retain their
original pixels. M0 Runtime never supplies READY; pure rendering stays independent
of the build configuration.

The display occurs before tick completion C. A terminal Runtime failure can leave
the last physical frame; the operator must observe continuing blink alternation.
This does not prove subsequent health or electrical inhibition. Native matrix
normal-startup/exclusive ownership versus MATCH Immediate startup remains open.
Production source grants and button windows remain unqualified/default-off.

Actual optics, battery accuracy, complete tick timing/stack, full rearming,
same-boot log preservation/dump and human gates remain pending under
[SC-AP](spec_conflicts.md). No upload, motor run, tuned value or physical result is
created by this task. D138's modeled864-byte span is720bytes less than prior MATCH;
the three added metadata bools occupy existing padding. The native model assumes
a pristine contiguous pool and its documented loader premises; it cannot prove
live allocation/stack behavior or qualify default/M0. The separate remaining
default-profile software qualification is the next task after this closure.
