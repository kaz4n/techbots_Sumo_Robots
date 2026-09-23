# Preserved D105 first-run fixture failures

The original independently frozen C++ suite has SHA-256
130ea40315a3ffe812152bdb3526f7536277807922779334e8dbaedbc2c6c738 and is retained
as calibration_output_cases_v1_frozen.cc. Both first normal and sanitizer runs
passed 24 of 26 cases, with the same three failed assertions in two cases.
The full original outputs and source hashes remain in append-only command
receipts and runtime_run1.txt. MATCH passed 3 cases/342 assertions in both modes;
the isolated total-deadline case passed 47 assertions.

1. The test set the fake provider's qtr_fault flag and then assumed no intervening
   epoch could write. That flag affects the next LINE_ADVANCE callback; an epoch
   may still expose the preceding valid line before that asynchronous callback.
   The failure was writes=2 versus the assumed 1. The correction checks every
   actual epoch's decision input, receipt and context: the first actually invalid
   epoch must add zero writes and leave ACTIVE. A preceding still-valid epoch may
   offer at most once. Final CANCELLED, exact failure precedence and cancel-once
   assertions are unchanged.
2. The recorder-to-calibration arbitration test began MODE immediately after a
   real START release request. That request requires a new neutral arming span;
   the first MODE was therefore not a qualified menu action. The observed service
   was SENSOR_VIEW rather than the assumed QTR_CAL, and calibration could not
   start. The correction supplies 30 ordinary NONE epochs before the same two
   MODE gestures. Actual QTR_CAL selection, eight genuine requests, port poison
   and no further writes remain required.

The separate read-only reviewer /root/runtime_inert_review approved both fixture
repairs before the assertions/stimuli were changed. No production body was read
and no private owner state was seeded. No established or locked test changed.
Corrected C++ SHA-256:
536098a9cfc317dd9d688a1561c10ddcf24f169805dd5f56bf37459f01a9f691.
The harness and parser tests retained their initial hashes. The corrected run
uses a new isolated copy of the separately frozen memory candidate.
