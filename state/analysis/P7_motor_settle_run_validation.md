# D201 inhibited SETTLE diagnostic

26 September 2026, Asia/Dubai. Objective: capture the separate SETTLE report in
the D198 static diagnostic image to distinguish the native callback's return
branch. This preparation does not yet establish a runtime cause or a repair.

## Prepared and verified

- Source `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`;
  static/default, MATCH0, MOTORS_ALLOWED0, diagnostic probe1. Source, grants,
  the 150 us limit and 4096-poll bound remain unchanged.
- D198 compile and D199 observed ABI/entry evidence are required provenance.
  D200 removed precisely the three verified stale upload copies; its completed
  result is pinned by the subsequent read-only admission.
- Native remote/actions/caller are exact 11/9/17 metadata derivatives. The
  independent suites preserve all 91 historical methods and 385 assertions,
  and add eight focused methods. All 99 passed on Linux. Windows passed 56
  and explicitly skipped 43 Linux descriptor cases, all covered on Linux.
  The old freeze's Windows prediction was a bookkeeping error: 11 inherited
  descriptor-free remote cases were already explicitly enabled.
- The first decoder runs executed 66 methods on each platform and retained
  17 failure events. Three implementation defects were corrected: after-flash
  boundaries, late count type classification, and read-row type classification.
  A parser-dependent deep-JSON fixture was corrected without adding a depth
  limit or weakening rejection; a controlled parser-failure case was added.
  The corrected 67 methods passed on both platforms with no skips. Original
  source, oracle and failures remain in Git and the first-run evidence folders.
- Admission02 was read-only and returned successfully at 07:27:30 UTC: exact
  board/boot identity, 19 current files, staged cleanup sources, retained
  originals, four absent paths and no recognized conflicting processes.
  Its observation does not replace the caller's fresh checks or prove absence
  of every possible process handle.
- Scope `1e1b1b589bfb7b0fa956829970dc49c5cc11d5a1c481496a051ed7688b749738`
  contains the fixed six keys and 11 reviewed input roles. Native host/source,
  scope, and decoder review are separate evidence boundaries.

## Evidence and next action

Evidence is in [P7_motor_settle_run_raw](P7_motor_settle_run_raw), especially the
independent/coordinator freezes, first and corrected host streams, preparation,
admission02 and scope. Reviews are in `state/reviews/P7_motor_settle_*_review.md`.
Initial implementation commit: `1df96c20`; first results: `b69cc011`; bounded
correction: `82a24b14`.

All four preparation reviews passed, including final decoder review `4656da08`.
Next: commit the prepared evidence, require a clean
HEAD, run check-only, then consume the single fixed inhibited upload/capture
owner. Retrieve only its saved receipts and SRAM files, interpret those exact
bytes, and independently review the actual outcome. Before that operation,
D195 remains the last flashed image. No motor-run permission or human gate
has been supplied; capture equality cannot establish coherent publication,
physical origin by itself, production WCET or robot acceptance.

## Actual inhibited collection

At clean reviewed HEAD `ff35c83e6d21d299dac14eb6fc5570d173a7772d`, check-only and execute returned 0. One upload, one capture and all 13 transports completed; no first error, postcheck error or closing error was recorded. Upload took 12.850 seconds; capture took 251.206 seconds, with 26 reads / 727432 bytes, the required 30-second and 2-second waits, and all four full flash comparisons true. The native owner is consumed.

A subsequent file-only retrieval verified 14 saved files totaling 17954 bytes, including closing rereads. Packet SHA `e32415b2ec6ea05f3056a68c116f71a2e502f9f815cfb7675d0a57c6b505860a`; decoded SHA `4d8383c3ceb7b0b02211e4933a1141e88d2bc65a336d3ffccd707d2040e6267e`. The fixed decoder returned 0 / DECODED with no format error; all six pairs agree, with coherence still UNPROVEN.

The saved SETTLE lifetime first failure is FINAL_DEADLINE (7), elapsed154us, poll_index5, fresh_mask7, valid7. Current is SUCCESS (1), elapsed132us, poll_index4, fresh_mask7, valid7. Both presence flags are1 and reserved fields are0; source-predicate annotations are CONSISTENT with no issues. The retained failure is not erased by the later success.

Observer is FROZEN / SETUP_FAILED, begin_ok=false, zero polling passes and zero epochs. Its 17-call complete trace records SETUP/SETTLE false at index10 (159us outer span), then EN-low/four zero-duty writes and SETUP/SETTLE true at index16 (137us outer span). This is initialization cleanup, not a HALT success. Gate remains uninitialized with IO fault; runtime has TRANSACTION fault. Both stored halt receipts have attempted=false and inhibition_confirmed=false. Runtime maximum_execution_us=0 is not a measured WCET: no control epoch ran.

This new observation localizes a saved rejection to the final154us-versus150us predicate; it does not identify why that duration occurred, establish coherent publication or physical timing/output qualification, or explain D195's separate application921 failure automatically. No limit, pin, grant or firmware behavior was changed in this run. Independent actual review `690a4164` passed for evidence integrity and observed setup failure; no material integrity issue remains.
