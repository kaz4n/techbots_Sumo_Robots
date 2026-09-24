# D135 bounded new-draft correction review

Read-only review of the correction diff against preserved first oracles/results
in b0540500/2d924f1f. No production, private13 or established protected test edit
was made by this reviewer; no compiler/test run here.

**PASS for this bounded new-draft correction; no open scoped finding.**

- `physical` now demands an explicit exact expected status. Only scenarios
  already asserting STOPPED pass `Fault::STOPPED`; others still require NONE.
  It adds consumed/valid receipt checks and preserves token, EN, zero, signed
  quantization and all PWM-channel assertions. It does not accept arbitrary faults.
- The15-mask/all-mode edge stimulus is retained. The added pushed-out predicate
  uses the actual prior applied duties, verifies centered FC and expected DIRECT
  M1 qualification, excludes all fault masks, and demands exact PUSHED_OUT flag
  equivalence. Ordinary front/diagonal brakes remain zero when not qualified;
  fault masks remain inhibited. Direction/slew/reversal and the extra40ms exact
  mirrored0.80 vector are independently specified B4/B6 checks, including Gate
  PWM quantization. No mask or valid opponent stimulus was removed.
- `receiptPrefix` is bounded by the retained batch and does not merely search
  through arbitrary earlier events. It allows at most one FIRST_NONZERO_DUTY,
  then at most one FAULT9 before the unique requested trace result. First-duty
  metadata is tied to the prior full token, enabled receipt, A, request bounds,
  wheel bits and rounded signed duty bytes. FAULT9 accepts only documented
  nonzero bits0..2 and the receipt/current timestamp rule; successful APPLIED
  forbids timing-invalid bit4. Current state/edge/contact or unrelated fault
  events in the prefix fail. This is an adequate narrow replacement for the
  unsupported global-ordinal0 assumption.
- Robot, Runtime and invalid-receipt call sites retain exact result counts,
  timestamps/values, full-token checks and no-retry assertions. Test counts and
  scope remain unchanged; the plan accurately records the three failure classes.

First corrected execution is pending. This review neither replaces first-run
failure receipts nor qualifies implementation behavior, native fit or a gate.
