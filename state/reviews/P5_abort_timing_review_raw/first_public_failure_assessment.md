# Independent assessment of D135 normal_first

Read-only review of `state/analysis/P5_abort_timing_raw/normal_first_LastTest.log`
and its JSON receipt. Root ran the tests; this reviewer ran no compiler/test.
M0:40 cases,37 pass,3 fail,10 failed assertions. M1:40 cases,33 pass,7 fail,
32 failed assertions. All42 assertion failures fall into three draft-only
expectation errors against unchanged pre-D135 safety/receipt behavior.

1. **STOPPED receipt status,20 assertions total.** New safety helper line9
   requires `motors::Fault::NONE` even after explicit/fault-induced STOP. The
   actual valid inhibited receipt returns enum6, `Fault::STOPPED`, by existing
   MotorGate::apply. This is deliberate reset-only terminal inhibition, not an
   application failure. Narrow correction: choose exact STOPPED when the result
   state/lifecycle is STOPPED, otherwise NONE. Preserve consumed/applied validity,
   full token, zero/EN-low, PWM quantization and all no-retry assertions. Do not
   broadly accept arbitrary faults or change Gate behavior.

2. **D049 pushed-out priority,4 M1 assertions.** DIRECT has previously applied
   positive forward wheels; FC becomes centered on the same observation as rear
   white in diagonal6/9. B4.3 and D049 explicitly place pushed-out pivot ahead of
   ordinary B4.2 diagonal-as-front brake. Thus a small forward pivot wheel with
   the other zero on reversal is legitimate on that first tick. The observed
   `0.04002` request and40/10 PWM pulses are consistent with separate channel
   periods and B6 slew, not evidence of edge priority failure. M0 has applied
   zero and therefore takes the ordinary braking row. Narrow correction: derive
   pushed-out qualification from the retained *actual preceding* receipt,
   current centered front and rear white, excluding fault masks; assert the
   EDGE/PUSHED_OUT marker, mirrored row direction, governor bound and actual
   PWM receipt. Keep the same stimulus/15-mask/all-mode sweep and ordinary
   front/fault zeros. Do not remove diagonals or suppress valid opponent input.

3. **Receipt ordinal overconstraint,18 M1 assertions.** Public robot helper
   lines33-34 requires APPLIED at event0. Logs show type2/detail3 there, the
   existing FIRST_NONZERO_DUTY receipt extension. D135's grammar ignores ordinary
   events while preserving their ordinals; it only requires receipt closure
   before current-decision events. Narrow correction: locate the single exact
   APPLIED event; permit only legitimate preceding prior-receipt events, verify
   their receipt timestamp/identity where serialized, and prove that current
   decision events follow it. Preserve its exact A/value, one-candidate count,
   all read/cue/handover suffix and no-retry checks. Do not reorder production.

The same ordering overconstraint exists in the original frozen private13 and in
configured Runtime public coverage; neither had run in this first result. Keep
them unchanged until their original execution evidence is retained or a separate
explicitly identified pre-execution oracle adjudication is adopted. This reviewer
has changed no test source or firmware. Existing accepted protected tests are
unaffected; this assessment applies only to the new, never-passed D135 drafts.

**Assessment: repair the unaccepted draft oracles narrowly after independent
author agreement; no production change is justified by these failures.** This
does not pre-judge future private/configured/sanitizer results or physical gates.
