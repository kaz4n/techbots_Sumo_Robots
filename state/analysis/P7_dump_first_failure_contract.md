# D231 native UART first-failure retention

The D230 passive observation retained a poisoned port after a failed transfer,
but the original native reason was unavailable. In the existing implementation,
`fail(reason)` restores the reason after abort, then the real `Transfer::fail`
cancels the port again and replaces `status()` with POISONED. This change repairs
that loss of evidence. It does not establish the original cause or fix an
assumed timeout.

Append one eight-byte `FailureRecord` to `UnoQDumpPort`, exposed through the const
`firstFailure()` accessor. `site == NONE` means no terminal record. The first
failed setup/write or explicit cancellation captures the original reason and
call site, plus packet offset, packet size and payload size before poison clears
them. All sizes fit the existing 79-byte packet / 64-byte payload bounds.
Existing NativeStatus values, status(), setup returns and poison behavior remain.

Sites distinguish setup, FIFO ownership/readback, write admission, transmit and
completion ownership/readiness, each existing deadline check, ordinary CANCEL
and REPEATED_BEGIN. Ordinary cancellation records reason OK and its explicit
site; it is not presented as a native transmission fault. Readiness polling alone
does not create a terminal record. A direct setup refusal retains NOT_ATTEMPTED
cleanup; later cancellation must not replace that first observation.

The first record includes the first cleanup disposition: NOT_ATTEMPTED,
SKIPPED_POISONED, SKIPPED_CONTEXT, SKIPPED_OWNERSHIP, VERIFIED or READBACK_FAILED.
It records whether the existing cleanup ownership query was evaluated and, if
so, its returned NativeStatus. NOT_INITIALIZED with ownership_evaluated false is
only the unevaluated sentinel. FIFO setup uses its existing evaluated
ownedState result; normal abort uses its existing ownership result and CR1
readback. No new peripheral read, clock call, loop, retry, grant or recovery is
introduced. The record is filled only for the first event; all later ready,
write, cancel and begin calls preserve every field.

The record is diagnostic and non-atomic. A const reference does not establish a
coherent live MCU snapshot. It does not prove how many submitted bytes shifted
on the wire or were received/acknowledged remotely. Native packet offset and
Transfer acknowledged bytes remain distinct quantities.

Use the existing independent mapped-register fixtures and normal/ASan/UBSan
variants. Preserve their exact packet/clock/IRQ/foreign-write assertions. Extend
the legacy fixture for partial packet faults and repeat retention; extend FIFO
setup fault cases for skipped/verified/failed-readback cleanup. Exercise the real
Transfer error-then-cancel path using the existing retained recorder fixture,
including READY_LOW, READY_ERROR, ownership loss, synthetic timeout, failed
cleanup readback and ordinary Transfer abort. This is source/host preparation
only; compilation, fit, actual diagnostic ABI and any fresh native run remain
root-owned later actions.
