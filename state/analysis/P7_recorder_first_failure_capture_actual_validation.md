# D233 passive first-failure observation

One capture at collector3c9f11f5 completed in214.372s;24read commands requested
639496B. Full loader/sketch comparisons pass before and after,12 raw status
leaves decode to64equal fields. Coherence remains UNPROVEN. Capture/retrieval
attempts1/1, no first_error or postcheck_errors. Actual capture_result.json
SHAa1641460b6fc99655f7a66a75f908d2e40555a26d7763d6e2e3d0a0c02bd53bd.

Both samples retain original TIMEOUT at STORE_DEADLINE, packet_offset7 of74,
payload59. This is seven submitted TDR writes, not7received bytes. No complete
payload was acknowledged. The diagnostic does not directly identify the80us
step versus100ms packet branch. First cleanup evaluated ownershipOK, attempted
CR1zero, and recorded READBACK_FAILED. Its precise readback was not retained;
do not infer a register value or a cured cancellation path.

RunnerFAILED/DUMP,setupOK,202479completed epochs,missed0,maxcompletedS..C482us,
maxlateness2us. TransferFAILED/PORT; nativePOISONED/initialized/attempted, inactive
and cleanupunverified. Both session values572412568535289530match expected.
Motor callback reportenabledEN0/nonzeroPWM0 is synthetic callback evidence.

This consumes the capture owner. No reset/retry/reflash or UART write occurred.
Latest compared image is D233source29cb1e76/packageb13a32b5, distinct from later
D234 source integration. LiveRAM/full-loop timing, delivery/cancellation and
physical/human qualification remain open. Independent actual reviewcf1ba387 is PASS for this bounded observation scope.
