# D190 actual run02 review

25 September 2026. PASS within collection and decoded-observation scope;
no material findings. Two separate reused-context same-model agents performed
local read-only review. Neither called the board, edited files or ran the
subject interpreter/tests. This is not a human or cross-model phase-gate review.

## Collection and retrieval: fresh_review

Independently inspected all 13 intent/result command pairs, pinned argv hashes,
timeouts and empty-stderr/exit0 transports. Exactly one upload and one capture;
all lifecycle, postcheck and closing-error arrays empty. All 159 input hashes
remain current. The 44 saved Git checks preserve reviewed HEAD b3e584d1, clean
tracked files, the exact committed scope and only the claimed untracked owner.
Three prerequisite rounds agree; 107 target source records and adapter a77fb7d4
remain stable. Capture bindings and inline helper bytes match their fixed pins.

Exact capture: 26 reads/727088 bytes, 221.21832 seconds and explicit sample pause
2.00038 seconds. All four expected-image brackets pass; seven before/after flash
segment hash pairs agree. Coherence remains UNPROVEN. Full upload reports one
reaped, non-timeout child, exit0/empty stderr; the OpenOCD extra-sector erase note
is retained and does not indicate failed upload.

Retrieval contains exactly14 files/17913 bytes. All hashes match intent, full
reports match their envelopes, and twelve raw SRAM blobs match capture pins.
Full opening/closing identity agrees. Inspected retrieval code reads saved
files only, using unchanged helper8ba9b190. No extra MCU read or reset follows.
The coordinator parse error is preserved and occurred before native invocation.

## Decoded observations: run02_audit

Independently decoded the raw Base64 bytes with stdlib struct and the observed
D188 field map, without reading or executing interpret_run02.py. Every selected
field in all twelve windows matches decoded.json; all six raw sample pairs are
byte-identical. Embedded14file size/hash checks also pass.

Diagnostic FROZEN/EPOCH_LIMIT; begin succeeded. Saved pre-abort runtime is
RUNNING/NONE, epochs4, missed0, maximum_execution_us582. The fourth transaction
is finished IDLE/NONE with valid consumed token4 feedback and zero outputs.
S/D/A/C timestamps are430413/430468/430955/430973us, duration560us; saved PreviousTick
preserves both application and duration validity. Trace records41 successful
invoked/completed callbacks in setup11/application4x6/halt6 order, no rejection,
overflow, first failure or timing fault. Every enable request is low/PWM pulse0.

Final runtime FAULT/TRANSACTION, transaction FAULT/ABORTED, gate STOPPED and
withdrawn previous-feedback validity follow explicit abort. Halt confirms
inhibition with valid timestamps431022..431299us. Empty setup grants explain
initialization_complete=false. These final fields do not identify a new fault.

Outer SETTLE spans152/131/153/131/131/131us all returnedtrue. Trace brackets include
invocation/bookkeeping; native timer starts after entry/prechecks and ends before
return. Outer152/153 do not prove violation of the internal150us threshold;
the exact internal elapsed values were not retained. Four epochs/max582 do not
qualify WCET or electrical output. Validation prose correctly distinguishes
41callbacks from the single detailed fourth-epoch receipt and does not call
the historical D160/D161 fault resolved. No source change is justified by these
samples alone. This agent did not audit cleanup/transport/159pin claims.

## Exact reviewed receipts

Paths below are relative to analysis/P7_app_motor_fault_run_raw/.

| Artifact | SHA256 |
|---|---|
| native_inert_run02/result.json | 6966085d810f9733e285df7d6faefe09ad8d1165d786378f06132c31a952ff88 |
| native_inert_run02/final_checks.json | e8c3c007102eaf489de57ef2aec4453ac06bed62b20044692a419224611d306b |
| native_inert_run02/0010-capture/stdout | 4de266780871c9dcede6eb72967467180f911665aa2ffdb4a5ec970bd40ba604 |
| run02_native_invocation.json | 240145f04c5873e55ba1702e9cacbd823d563384d8b2cde30454405fbd25bf2d |
| retrieved_inert_run02/0001-read-saved-results/stdout | de869a1fdf1be03e30abead5ca02b5134c96085709d22d13429fcacf6c680eac |
| retrieved_inert_run02/decoded.json | fa8e070360b3fa840a9e9027a5f8ef1bce3bbfc91461779dd75602bb46571082 |

Collection/interpretation integrity does not establish atomic snapshots,
physical qualification, sustained application acceptance or a phase gate.
