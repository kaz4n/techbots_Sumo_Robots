# Preserved D102 test-build failures

The first full build (d102_host, compiler exit2) rejected two newly added REQUIRE
helper checks at test_recorder_csv.cpp547 and test_tick_timing.cpp342 under the
unchanged DOCTEST_CONFIG_NO_EXCEPTIONS policy. Root initially associated the
failure with the separate new author's same harness issue and reran too early;
d102_host_final repeated the same failure before the implementation worker fix.
Both exact commands/exit2/compiler diagnostics remain in P2_app_build_raw.
No production test executed/falsely passed from either failed build.

The independent reviewer identified the exact two migrated-fixture calls. Worker
replaced only these new checks with read-success booleans, CHECK and explicit
return guards, preserving all original predicates and no-exception configuration.
Worker's isolated compilation of both corrected fixtures passes. Root now runs
full verification against these final bytes; do not retry a still-unchanged failure
or hide the earlier coordinator attribution error. D051 permits this ordinary
unlocked fixture correction; no locked-test or safety expectation changed.
