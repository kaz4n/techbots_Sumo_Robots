# D201 offline interpreter fresh-context review

2026-09-26. Reviewer owns this review only. Initial status: BLOCKED on two
implementation findings. No subject, test, transport or device execution was
performed by the reviewer. Initial source is 31143 bytes, SHA256
eb23a62a43379bc69d5cf894a8be4a606da4ea5c417d2d21aaa486dcaf892724.
The authoritative contract is 32296 bytes, SHA256
6007ec4e2e22cdf0e8f751790c49924b26b4adb8f9dfde5d5f6db2ed9bd7dff8.
Independent oracle freeze is 9361 bytes, SHA256
1722bb497d1cfd67e855050acf13d84998aacec75b734d58d16b82c6f93fec0e.

## Initial findings, retained before any repair

1. BLOCKER: `_flash` pairs `FLASH_KEYS` in the order before_loader,
   before_sketch, after_loader, after_sketch with boundaries 4, 6, 20, 25.
   The fixed plan requires after_sketch at 20 and after_loader at 25. This
   rejects valid failed prefixes after the sketch bracket and can accept an
   early after_loader assertion. Bind the last two flag names to their actual
   boundaries while preserving the two predicates and deterministic order.
   The independently frozen all-prefix and explicit flash-boundary cases cover
   the discrepancy. This finding was identified by source inspection.
2. BLOCKER: `_receipt_types` classifies malformed count member types as TYPE
   before `_counts` can inspect them. The deterministic-order paragraph
   explicitly assigns malformed counts to COUNTS; bool commands/reads in the
   frozen independent oracle expect that classification. Move exact-int member
   checks into the late COUNTS phase before arithmetic/comparison. Keep the
   named counts container TYPE and fixed key-set KEYS checks unchanged.
   This finding was identified by source/contract inspection.

Preserve the initial source, oracle and first host results. Neither finding
authorizes changing assertions, accepted inputs, receipt ownership, native
status or firmware. Final review awaits the coordinator's first serial host
receipts and a bounded implementation correction against the same contract.

## Evidence boundary

The interpreter reports saved-format DECODED, PARTIAL or REJECTED and source
predicate annotations only. It cannot upgrade a failed native capture, infer
publication atomicity or associate the lifetime first failure with a trace
stage/epoch. Coherence remains UNPROVEN. Physical cause, timing repair,
production WCET, motor-capable authorization and human gates remain outside
this review.
