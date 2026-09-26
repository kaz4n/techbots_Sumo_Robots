# D195 actual inhibited observation, 26 September 2026

The longer observation reproduced a native SETTLE callback failure at application
921. The diagnostic froze and retained that first failure. Its exact internal
rejection branch remains unknown. No safety limit or production behavior has
been changed in response to this result.

## Execution and collection

At reviewed clean HEAD `10be312678a9ee41adc660cd197b0d7f82f9daaf`, check-only and
the single execute invocation returned zero. The fixed caller completed its
13 transports, one upload and one passive capture, with no first or closing
errors. The latest flashed image is now D193 source `3a08ddeb`, static/default,
MATCH=0, MOTORS_ALLOWED=0, SUMOX_MOTOR_FAULT_PROBE=1; raw BIN `f1df5e7f`
(95,344 bytes), packaged image `85b05c56` (95,360 bytes).

Capture completed 26 reads totaling 727,152 bytes in 251.231 seconds. Loader and
sketch hashes matched the admitted originals both before and after the SRAM
samples. The recorded waits were 30.000401 seconds before the first SRAM sample
and 2.000381 seconds between sample groups. All six SRAM pairs are byte-identical;
these sequential reads do not establish atomic coherence.

A subsequent file-only query retrieved two complete reports and twelve saved
SRAM windows: 14 files, 18,017 decoded bytes. All admitted hashes, identities and
closing rereads matched. This made no additional MCU read. Board serial
2629958581 and boot 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 remained bound throughout.
No full firmware/debug binary was downloaded.

## Observed failure

- Observer FROZEN / CALLBACK_FAILURE, 921 epochs and 115,539 polls. Its finite
  10,000-epoch and 10,000,000-poll limits were not reached.
- First failing callback: APPLY / SETTLE, application 921, invoked and completed,
  returned false. Its outer timestamp span is 154 microseconds.
- Trace retained 64 successful prefix calls and counted 5,485 omitted calls:
  5,549 completed wrapped callbacks in total. Overflow is explicit; first failure
  and latest callback are independently retained. Intermediate cleanup outcomes
  cannot be reconstructed from this truncated prefix.
- Saved pre-abort runtime remained RUNNING / NONE. Its completed epoch 921 had
  a consumed but invalid motor receipt with IO fault. Requested motor enable
  and both duties were zero. Initialization grants remained absent.
- The completed instrumented transaction and stored maximum measured 859
  microseconds, with zero recorded missed releases. This sample exceeds the
  800-microsecond target; it does not establish production worst-case timing.
- Explicit diagnostic abort then produced the final runtime/transaction fault
  states. Those final labels are consequences, not the initiating fault.
- Final HALT / SETTLE also returned false, with a 153-microsecond outer span.
  The halt receipt has `inhibition_confirmed=false`. Software did not confirm
  inhibition; no electrical output measurement was taken.

A retained successful SETUP / SETTLE also spans 154 microseconds. The outer
wrapper spans include work outside the native internal timed interval, so they
cannot identify a violation of the unchanged 150-microsecond internal guard.
The next useful observation is the exact native rejection branch and the already
available internal elapsed/poll/freshness values. Do not widen the guard based on
these outer timings.

## Evidence and boundaries

- [Caller result](P7_app_motor_observe_run_raw/native_inert_run01/result.json),
  60,754 bytes, SHA256
  `4fc33583c34cd4ced88bc297098830baa7faca86c7b1d55f63fba8ecc3de21c5`.
- [Raw saved-file retrieval](P7_app_motor_observe_run_raw/retrieved_inert_run01/0001-read-saved-results/stdout),
  27,525 bytes, SHA256
  `3bb9425f39ba71ef796308e8d94b670158f7785eded44849f7ba82515f4e1c90`.
- [Decoded fields](P7_app_motor_observe_run_raw/retrieved_inert_run01/decoded.json),
  SHA256 `c37a3069f0e6eac6707ee579d9d82459cbe6dec685aa937feceececffe2ef5fe`;
  [fixed interpreter](P7_app_motor_observe_run_raw/interpret_run01.py) uses the
  actual D194 ABI02 field map `b96b6a3e`, not a host layout.
- [Scope review](../reviews/P7_app_motor_observe_scope_review.md) and
  [actual review](../reviews/P7_app_motor_observe_actual_review.md).

The separate same-model raw decoder agrees with all twelve decoded window
trees. Final collection/provenance review f8779db4 PASS verifies all 159 admitted
inputs, 128 compile pins, 107 installed-source files and 2,020 decoded scalar
occurrences; see the linked actual review. This is an instrumented inhibited firmware observation, not a root-cause
repair, electrical acceptance, live RAM/stack or production WCET qualification,
motor-run authorization, release readiness or human phase gate.

D195 run01, its upload/capture/adapter owners and D196 cleanup root03 are
consumed. Never replay them. Any next firmware needs new source/artifact/ABI,
entry and exact native scope evidence. Newly created upload scratch must be
observed and separately bound before any later cleanup.
