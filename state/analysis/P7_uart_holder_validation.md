# Current UART holder visibility

D223 completed one privileged read-only metadata observation on 26 September
2026. Two sweeps each covered 165 processes, 275 tasks and 3082 descriptor-stat
attempts without denied, vanished, replaced, capped or timed-out observations.
Including validation of the observer's own directory handles, 6180 FD metadata
stats were performed. Boot, device and router identities matched at both ends.

Only arduino-router PID 568 was observed holding /dev/ttyHS1, fd 7, exposed in ten
of its task tables. This does not mean ten independent opens or prove continuing
exclusivity. Device 239:1 is dev 6/inode 148; router starttime 1514 and executable
6095032 bytes, SHA-256 3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19.
Boot was 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, kernel 6.16.7-g0dd6551ae96b.

The [exact raw receipt](P7_uart_holder_raw/observation01.stdout) is 5459 bytes,
SHA-256 8380134796ac20aeab649e52ba4feacc22a75bc6dccd020ee7b69df8bc5c1be5.
Transport returned 0 in 14.381 s, with empty stderr and all five reviewed inputs
unchanged. No credential was saved. The observer never opened/read the UART,
changed services, sent RPC or touched firmware. Its consumed owner must not be
repeated as a freshness substitute.

[Source/host admission](../reviews/P7_uart_holder_review.md) and
[independent actual review](../reviews/P7_uart_holder_actual_review.md) are FINAL
PASS within this scope. The observer passed 16 focused tests on each host platform.
A new fixture initially announced FD9 without its synthetic metadata; the original
failure and source are retained. Its bounded correction preserves the changed-set
assertion. A separate Linux host self-process smoke test checked actual /proc
traversal with a synthetic boundary; it is not board UART evidence.

The previous protected-holder visibility gap is closed for these two samples.
Continuous exclusivity, clean framing and receiver readiness remain UNKNOWN.
Last-close/RX-DMA completion, positive router reopen and actual full synthetic
recorder delivery are separate next work; no setup grant, motor permission,
physical acceptance or human gate follows from this receipt.
