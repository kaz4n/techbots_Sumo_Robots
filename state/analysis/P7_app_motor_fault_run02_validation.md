# D190 actual inhibited full-app diagnostic

25 September 2026, Asia/Dubai. TARGET-UPLOADED / HARDWARE-OBSERVED.
The four-epoch diagnostic completed successfully. It did not reproduce or
resolve the earlier D160/D161 full-app MotorGate IO fault.

## Execution and provenance

The user supplied authentication for the prepared D191 cleanup. The unchanged
wrapper removed exactly three verified stale scratch files (2,334,244 logical
bytes), preserved their originals and permanently dropped privileges. Its
actual result and independent review are retained separately. No credential
was saved in the repository or passed as a command-line argument.

Fresh admission and separate scope review preceded execution at clean commit
`b3e584d1ce265f2c469ce0edc39bafe4121b65f0`. Both check-only and execute exited 0.
The existing caller issued exactly 13 transports, including one upload and one
conditional capture. All returned 0 with empty stderr; first-error, postcheck,
transport, prerequisite, local and finalization error collections are empty.
All 159 pinned inputs remained unchanged. No retry or additional reset occurred.
An earlier inline coordinator SyntaxError occurred before any statement or
native action; it is preserved in the invocation receipt.

The fixed image is source `21df6ae8`, static/default/MATCH0/MOTORS_ALLOWED0/probe1,
raw ELF `2f8dc9f1`, raw BIN `18598e13`, packaged image `deb40317` (95,328 bytes).
The upload reports one reaped child, no timeout, and 12.718 seconds. Capture
completed 26 passive reads totaling 727,088 bytes in 221.218 seconds. Complete
loader and sketch images matched their bound references both before and after
the SRAM samples. The six pairs of SRAM windows are byte-identical. They were
read sequentially: coherence remains **UNPROVEN**.

One subsequent file-only query retrieved the two complete reports and twelve
small SRAM files: 14 files, 17,913 bytes total. Every size and hash matches its
admitted report, with independent closing rereads and identical full board
identity before/after. Board 2629958581 and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 match this run. This retrieval made no new MCU
read. Raw bytes remain Base64-encoded in the exact retrieval stdout; no duplicate
firmware/debug image or separate binary copies were downloaded.

## Observed application result

The decoder uses D188's observed target field map, not an assumed host layout.
Its map SHA256 is `2da7da2188de1e49c12c43887e23a66125a819b3ee4a164d254178ef33adb726`.

- Diagnostic phase FROZEN, reason EPOCH_LIMIT; begin succeeded, pre-abort state
  was saved, and the final abort returned.
- Saved runtime: RUNNING, fault NONE, four epochs, zero missed releases, stored
  maximum execution 582 MCU-clock microseconds.
- Saved fourth transaction: finished, timing valid, fault NONE, token 4,
  consumed valid feedback, enable false and both duties zero. Its measured
  execution field is 560 microseconds; saved PreviousTick preserves that duration.
- All 41 retained callbacks were invoked, completed and returned true with valid
  timestamp ordering. No first failure, rejected call, overflow or timing fault.
  All enable requests were low and every PWM pulse request was zero.
- Final halt reports inhibition_confirmed and timing_valid. Gate STOPPED (6),
  final transaction ABORTED (6), and runtime TRANSACTION (4) follow the explicit
  diagnostic abort. They are not the initiating fault: the saved pre-abort state
  has no fault.
- initialization_complete=false is expected with this diagnostic's empty setup
  grants. No sensor, voltage, pin or wiring acceptance was inferred.

The six outer SETTLE callback spans are 152, 131, 153, 131, 131 and 131 microseconds.
These include work outside the native function's internally timed interval, and
all callbacks returned true. The outer 152/153 values do not by themselves prove
a violation of the unchanged 150-microsecond internal bound. Neither these six
samples nor the stored 582 maximum establishes worst-case tick timing or R4
qualification. The trace retains callbacks, not four complete historical
application receipts; the detailed saved receipt is the final fourth epoch.

## Evidence and remaining work

- [Invocation](P7_app_motor_fault_run_raw/run02_native_invocation.json) and
  [caller result](P7_app_motor_fault_run_raw/native_inert_run02/result.json).
- [Raw retrieval](P7_app_motor_fault_run_raw/retrieved_inert_run02/0001-read-saved-results/stdout),
  SHA256 `de869a1fdf1be03e30abead5ca02b5134c96085709d22d13429fcacf6c680eac`.
- [Observed fields](P7_app_motor_fault_run_raw/retrieved_inert_run02/decoded.json),
  SHA256 `fa8e070360b3fa840a9e9027a5f8ef1bce3bbfc91461779dd75602bb46571082`;
  [fixed offline interpreter](P7_app_motor_fault_run_raw/interpret_run02.py).
- [Independent actual review](../reviews/P7_app_motor_fault_run02_actual_review.md):
  collection/retrieval and separate raw-field interpretation both PASS, no
  material findings. These are reused same-model contexts, not a phase-gate review.

This is evidence of a bounded, inhibited application run. It supplies neither
electrical motor-output measurements nor physical acceptance, live RAM/stack,
worst-case timing, a human phase gate or motor-run authorization. Different
source and instrumentation also prevent attributing the historical fault to a
particular cause. No firmware source, safety limit, pin or locked test changed.

The run02 scope and all native owners are consumed. Do not rerun this launcher.
The next engineering task is to define a longer bounded inhibited observation
that can retain the first native failure without trace overflow, using this
successful four-epoch run as evidence. Preserve the current diagnostic and
150-microsecond bound; any new firmware needs independent tests, review, actual
artifact binding and a fresh native scope. Full release/physical gates remain open.
