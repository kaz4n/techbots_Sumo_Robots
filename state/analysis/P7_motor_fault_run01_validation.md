# D184 actual inert diagnostic

25 September 2026, Asia/Dubai. TARGET-UPLOADED / HARDWARE-OBSERVED.
This isolated run completed; the earlier full-application fault remains unresolved.

Reviewed execution commit133f77bc binds scopee9fb5248 and the unchanged D179
caller. Local check-only and actual execution each exited0. Exactly11 transports
returned0 with empty stderr: three admission checks, one upload, three checks,
one capture and three final checks. No retry, extra reset or compilation occurred.
Caller result is COMPLETED; local, prerequisite, transport and finalization error
arrays are empty. Source/scoped files remain unchanged. See
[invocation](P7_motor_fault_raw/run01_invocation.json),
[caller result](P7_motor_fault_raw/native_inert_run01/result.json) and
[scope review](../reviews/P7_motor_fault_run01_review.md).

## Observed result

Source8f592937/raw ELFf9460a16/packagedb4416792 is the D172 dynamic/default-wait
diagnostic: MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1. Upload reports one
child, exit0/reaped/no timeout. Capture reports20 reads totaling592640B; the four
before/after loader/sketch comparisons pass. Both relocation brackets identify
one unchanged node and BSS536959144 (2632B).

The two2592B Runner snapshots are identical, SHA256
8805ee82be780f1d2b55acac0f9c21ae8c5fd313f2fb20ba48a1bc74b3665548.
The D174 decoder reports:

- COMPLETE, failureNONE, successful begin and four consumed applications.
- All four receipts applied_valid=true, motors_enabled=false and both duties0.
-41 retained callbacks; each completed/returned true with valid timing.
  No rejected/overflow/first-failure/timing-fault indication.
- Final halt fresh, attempted and inhibition_confirmed, with timing_valid=true.
  Gate fault6 is the public STOPPED enum, expected after this explicit halt.
- All six recorded settle callbacks report130us. These are six instrumented
  observations, not a worst-case bound or a whole application tick measurement.

Exact decoded fields, including otherwise-unused slots, are retained in
[decoded.json](P7_motor_fault_raw/retrieved_inert_run01/decoded.json).
Structural decoding and repeated identical samples do not prove atomicity;
coherence remains UNPROVEN. These are software/register-level observations,
not electrical EN/PWM measurements or permission to energize motors.

## Retrieval and provenance

One later file-only query retrieves the exact full upload report1887B, full
capture report4674B and both raw snapshots2592B each:11745B total. All four
sizes/hashes match their admitted envelopes, with independent closing rereads
and matching full before/after boot identity. There was no new MCU read.
The exact bytes are Base64 in
[raw retrieval](P7_motor_fault_raw/retrieved_inert_run01/0001-read-saved-results/stdout);
no second binary copy was created. Other original capture files remain in the
fixed board capture directory referenced by the report, with their hashes.

Board wallclock reports approximately06:07-06:10UTC while the laptop is near
12:00-12:04UTC. Retain both clock domains without cross-clock ordering claims.
Board monotonic durations are8.853s upload,180.037s capture and2.0004s explicit
sample gap. No clock setting was changed. The earlier local ADB daemon restart
and initial stderr assertion are retained in the separate admission receipts.

The ordinary Git whitespace check flags exact retained CRLF receipt bytes
(exit2); the CRLF-aware check passes(exit0). Raw staged bytes match working
files, and no instrument output was edited to satisfy formatting checks.

## Remaining work

This isolated dynamic diagnostic did not reproduce D160/D161's earlier static
full-app IO failure. Different image, startup/runtime work and boot preclude a
claim that the old fault is fixed or its cause established. No150us limit,
wiring, pin, setup grant, behavior or locked assertion changed.

The run scope and native owner are consumed. Preserve them and the board's
saved capture; do not repeat this run automatically. Next qualify the current
D180 main-app source through the existing compile-only path using a fresh stage
that preserves prior denied cleanup paths. Default-memory fit, native full-app
startup, complete RAM/stack/WCET, physical results and human gates remain open.
Separate actual-evidence review PASS, no material finding: [review](../reviews/P7_motor_fault_run01_actual_review.md), SHA2562e5ba8ac32244cdbea177b2afe94ac54d274fdbb1b19d2bff55eb2bb01cadd5a.
This is a separate reused same-model context, not a fresh phase-gate review.
