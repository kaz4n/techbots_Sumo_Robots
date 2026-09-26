# Recorder failure: passive status observation

Independent [actual review](../reviews/P7_recorder_failure_capture_actual_review.md)
is FINAL PASS. D230 completed one passive capture with full loader/sketch flash comparisons
passing before and after the SRAM reads. It narrows D228's failed delivery to
a reported native port failure at the start of dumping. The original native
error remains unavailable because later cancellation overwrites status.

At collector `26943377`, local check took 2.070 s and execution 209.534 s. Ten
transports, one capture and one retrieval completed without closing errors.
The native capture made 24 reads requesting 638,936 bytes, including two
684-byte status snapshots separated by at least two seconds. All 56 decoded
fields agree between snapshots; both remain non-atomic, coherence UNPROVEN.
The image comparisons bind these values to D228's actual recorder image.

Observed values:

| Field | Observed value |
|---|---|
| Runner | FAILED / DUMP |
| Native setup | OK; setup completed |
| Completed epochs | 202,480 |
| Missed releases / maximum lateness | 0 / 2 us |
| Maximum completed S..C duration | 484 us |
| Reset and service | reset_done and service_only true |
| Transfer | FAILED / PORT; 0 acknowledged bytes, frames and events |
| Native owner | initialized and poisoned; status POISONED |
| Native cleanup | cleanup_verified false |
| Session | 3997245574426120340, matches expected |

The final transaction is ABORTED, unfinished and timing-invalid. Its duration
is excluded from the reported completed-epoch maximum. These values do not
qualify full-loop timing, sensors, electrical inhibition, physical RAM or gates.
Zero transfer bytes does not rule out a partial UART packet already being sent.
Unverified cleanup does not prove that a register write did or did not occur.

The native failure path temporarily records its reason, but subsequent
Transfer cancellation calls poison again, replacing that reason with POISONED
and clearing packet progress. This is a source-confirmed diagnostic defect.
The next bounded software change should retain the first failure and cleanup
observations while preserving existing status, poisoning and ownership guards.
No timeout, ownership or register cause is inferred from the current record.

Raw statuses, exact identities, receipts and root closure are retained under
[P7_recorder_failure_raw/native_capture01](P7_recorder_failure_raw/native_capture01).
The original UART delivery remains FAILED. No reset, upload, UART operation or
cleanup occurred during this capture, and its owner is consumed. The loaded
image remains D228's inhibited recorder; D229's newer application was compiled
only. Native route audit also confirms the existing mon/write framing and
TCP7500 decoded route; no missing framing layer was identified.
