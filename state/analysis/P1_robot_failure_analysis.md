# First Robot validation failures and disposition

2026-09-23 Asia/Dubai. Original failures are retained, not overwritten.

1. P1_robot_host_20260923.txt: build exit2 because new unlocked
   test_robot_qtr_warning.cpp omitted initializer_list for braced range loops.
   Added exactly that standard include, without modifying any predicate. The
   independent author recorded old/new hashes in its QTR report. Build run2
   succeeds; no established locked test was touched.
2. P1_robot_host_20260923_run2.txt: CTest exit8.876 cases,875 pass; seven
   assertions fail in the10000-stream locked property, all contract_faults==0
   versus SCRIPT_START2. This is a legitimate unknown-bearing policy gap, not
   an R1/R5/R6 motion bypass: prior source safely inhibited.

Diagnostic replay using the same fixed seed0x36a891d5 reached stream212:

| Observation | Time(us) | Confirmed line/opponent | Raw yaw | Outcome |
|---|---:|---|---:|---|
| sample0 |5164000|0 /0|-4|OPENER, no contract fault|
| sample1 |5364000|0 /56 (both sides plus rear-left)|269|OPENER exit tries DEFEND, then STOPPED/SCRIPT_START|

Battery was finite11.7V; all required freshness/application contracts held.
D-026 correctly leaves bearing invalid when both sides first conflict and no
prior bearing exists. DefendTurn.start correctly rejects a missing bearing.
Robot had no explicit pending-ambiguity policy. The test's broad no-fault
expectation surfaced that omission; its failure alone did not authorize relaxing
the strict component API or choosing an invented direction.

D-061/34c48d0 explicitly chooses bounded zero-demand DEFEND waiting under D-051,
before replacement source and independent focused regressions. The existing800ms
deadline starts on first ambiguity and survives later valid capture; front/clear,
edge/STOP and genuine invalid-context validation retain priority. Component
DefendTurn API/source and all existing locked cases remain unchanged.

First implementation of this chosen policy is frozen at fsm_robot.cpp
b8e7d3f5d0e7e5896beb1abd08715ee092f6c21c7ad6d9df9eb74a42fb1e219b,
fsm.h4ffb1cccaf44b21dd49a99892cadbbb6f7e21fc1f2cccbbe11a406cabc6555b9.
Strict C++17 syntax passes; fresh reviewer narrow source review passes. Runtime
closure still requires the unchanged property and independent D-061 cases.

Diagnostic tooling limits are also retained in P1_robot_failure_trace_20260923.txt:
the first command failed because rg is unavailable inside WSL; a second Bash-c
argument reconstruction produced an empty object argument. A saved local Bash
script using find avoided that quoting issue and reproduced the trace, exit0.
Its one diagnostic case is not counted as production validation. No source fix
was attempted during those diagnostic command failures. The actual policy repair
is the first behavioral correction attempt for this runtime issue.

Pre-runtime review then found a D-061 deadline defect: an actual escape-exit
brake tick selected ambiguous DEFEND but deferred its timer start until the next
executor call. The existing contract anchors the first selection, so a sparse
next call could extend the wait. Moved pending-interval initialization into
routeNormal before its forced-brake return. Fresh review confirms the correction;
independent exact/sparse escape-exit regressions are being added. This was a
review finding before the first D-061 runtime check, not a changed requirement
or a locked-test amendment. Intermediate tooling116/39.157s is retained; final
source maps and controlled tests must be rechecked after this source change.
