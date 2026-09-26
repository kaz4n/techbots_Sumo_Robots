# D238 actual six-store result observation

One passive capture completed in204.585s after D237 receiver closure.
26read commands/639504bytes,10transports; all fullflash brackets match and
65decoded fields agree across the two non-atomic snapshots. Coherence remains
UNPROVEN. Capture/retrieval attempts1/1; first/postcheck/finish/transport error
lists empty. No reset, upload, UART writes or peripheral-register reads.

Runner and transfer are SENT_UNCONFIRMED, failure/reason NONE. Native statusOK,
initialized/attempted, inactive and not poisoned. First failure siteNONE with
cleanupNOT_ATTEMPTED/ownership_evaluatedfalse; no abort qualification follows.
Transfer records607508bytes,5001frames,8events,CRC2865663826. Both sessions
8582740024591403637 match. Actual receiver retained607448bytes:60bytes fewer.
D237 actual delivery remains FAILED for the absent opening envelope.

Runner345350epochs,missed0,maxcompletedexecution482us,maxlateness2us.
Synthetic callback enabledEN/nonzeroPWM/invalidcalls allzero. These are the
inhibited recorder scenario, not full physical-loop timing or motor qualification.
Packet start345766875 and lastpoll345776534 contextualize the final successful
packet; no timeout occurred in this attempt. No deadline cause is inferred.

Next: one separately identified attempt on unchanged accepted six-store source,
after exact stale upload cleanup. No decoder restart or repaired acceptance.
