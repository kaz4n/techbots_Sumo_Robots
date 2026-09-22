# D-065 first host-run failure, 2026-09-23

Preserved initial receipt: P0_qtr_host_tests_20260923.txt. Independent author
ran46 methods:23 decoder methods passed;45 acquisition-fault subcases failed.
The opaque event oracle found one unexpected micros call after the failed sample
had already been cleaned up and stored. Fresh reviewer independently reproduced.

Cause: initial setup failure branch sampled micros and wrote header end_us before
returning. Frozen contract publishes header end_us only after200 acquisitions.
Per-sample total/failure timing is already retained, so the extra call is needless
and especially inappropriate after a detected clock failure. This is a source
mismatch, not a defective expectation. No test expectation is amended.

First repair: remove the single failure-path end_us=micros statement. Keep failed
sample/completed and complete0; leave header end_us0. Successful completion remains
unchanged. Before the first repair rerun, the author found its record-total fault
expectation had allowed an invalid header end_us contrary to the same contract.
Strengthen that new unlocked expectation: keep end_us0 on invalid total. The same
repair batch now samples a local final time and publishes end_us/complete only
when the total is valid. This strengthens rejection; it does not relax a failure.
Require focused rerun, new source hash, exact target compile/audit and
fresh reviewer approval. Initial compiled fb4248d9 image was never uploaded.

First repair rerun:50 methods,5 fault-subcase failures remain, all extra-clock
failures fixed. New failure concerns timeout_mask: code filled the complement
after every valid pass, so later BAD_LEVEL/POLL_GUARD/cleanup-CLOCK faults retained
a mask despite never reaching a deadline. Contract assigns that mask only to the
DEADLINE outcome; an incomplete acquisition cannot claim pins timed out.
Repair this distinct field-publication issue by moving timeout_mask assignment
inside the deadline branch. Keep early LOW history and fault results intact.
No expectation changes; preserve both runs in the original appended receipt.

Resolution: final50 cases PASS7.804s, independently reproduced PASS7.078s.
Existing8 config cases pass. Complete tooling suite306 tests PASS112.485s,
no failures or skips; receipt P0_qtr_tooling_20260923.txt. No open host-test issue.
Final source61d7a2d0 compiles on the actual board with exit0, still no upload at
this validation checkpoint. Initial and intermediate artifacts remain historical.
