# D-073 validation failures and environment - 2026-09-23

First normal build failed (compiler/make exit2; enclosing runner exit1) because
doctest2.4.12 refuses decomposing unparenthesized `||` expressions. The independent
author inspected the full retained normal_build.txt receipt and wrapped complete
predicates at test_recorder_csv.cpp lines123,134,154 in parentheses. No predicate,
assertion, test case or production code changed. This first repair passes the full
normal suite:993cases/16989315assertions, zero failures or skipped cases.

Independent author used only the frozen contract, public headers and prior tests;
the author did not read implementation .cpp files. The separate reviewer checked
the repaired tests and reproduced all18 CSV cases/1321502assertions. Original
failure receipt is retained, not replaced by the successful retry.

Disk space on C: was approximately35MiB before sanitizer work. To avoid a failed
link, removed only the previous generated build/host-sanitize/sumox26_tests
executable (41368512B), after resolving and checking its exact absolute directory,
basename and untracked status. All source, object files, target artifacts and prior
validation receipts were preserved. The old executable SHA/path/size is retained
in generated_binary_cleanup.json; available space rose to approximately77MiB.
The same sanitizer target is rebuilt for this task. This is build cleanup only,
not an evidence deletion, source change or board action.
