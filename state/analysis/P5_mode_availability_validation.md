# D134 optional opener availability validation

Paused at user request,2026-09-24 13:09 Asia/Dubai. Active software phase P5 under D134;
physical acceptance and human gates remain pending. Contract27bc075a follows
reviewed proposalcf35d0a8. Original public tests/first build failure are retained
in425c8a97. No board compilation, upload, reset or motor run occurred here.

The change preserves six historical mode IDs and shipped availability1/1,
provides bounded menu skipping and direct-entry rejection for disabled optional
openers, and validates the actual staged config before remote activity. It adds
no object fields, motion command path, hardware grant or alternative strategy.

## Completed evidence

- `P5_mode_availability_raw/admission_first.{json,txt}`:60 Python methods PASS,
  comprising26 new availability,32 unchanged push-literal and2 registry methods.
- `regression_first.{json,txt}`:the same296 legacy tooling methods PASS,
 132.531s, no failures/errors/skips. Controlled substitutes and historical source
  fixtures test scripts; these are not successful board builds.
- `default11_focused_retry1_LastTest.log`:20 public C++ cases PASS in each M0/M1
  binary, including10,000 fixed-seed hold streams and actual MotorGate callbacks.
  The enclosing runner returned1 because its later independent probe failed;
  retain that distinction. The later `default11_full_retry2` passes all18 CTest
  targets (20.45s execution) plus corrected6 private cases perM0/M1, wrapper exit0.
- `../reviews/P5_mode_availability_review_raw/python_first.{json,txt}`:8 private
  Python methods PASS with external processes/network forbidden.
- Reviewer `layout_first.{json,txt}`:all four availability pairs under M0/M1
  match the fixed cf35d0a8 baseline sizeof/alignof for Menu28,Flank152,Wait216,
  Robot2640,Runtime166624 host bytes. This is not target-fit or live RAM proof.
- `binding_review.json`:all649 frozen inputs exact, all41 preexisting protected
  sources byte-identical, all57 registry assertion nodes unchanged, and original
 140971-byte PROGRESS prefix exact. Initial Git-blob versus CRLF working-file
  comparison used the wrong representation; the final check uses original
  prechange working-byte hashes and changes no source.

## Preserved failures and independently adjudicated corrections

`P5_mode_availability_first_failure.md` details the original compiler failure
(`last = {};` in a new fixture), corrected only to a typed default operand, and
the first focused run's new draft universal-edge-brake assumption. Original
draft/failures remain retained. The corrected case checks existing B4 brake,
moving and inhibited-fault rows, B6 slew/reversal, exact settled demands and
physical M0/M1 Gate receipts. No production or prior protected test was changed
to obtain those passes.

The first independent C++ run passed5/6 cases in M0 and then stopped. Its stale
snapshot stimulus omitted every observation in B3's final300ms snapshot window.
Separate spec-only author and reviewer confirmed the setup error. The original
private source and manifest remain `private_modes_first.cc` and
`private_freeze_first.json`, with the exact failed receipt. Correction introduces
a real final-window FC snapshot and explicit preconditions while retaining every
old routing/contact/fault/cap assertion. Independent M1 was not executed on the
failed first probe. Corrected private execution now passes6/6 perM0/M1 in the
full retry. The intervening full-build CMake failure, minimal source reassociation
and its scope are retained in P5_host_profile_integration_failure.md. All18 now
pass with that fix; positive-duration supplemental coverage is still pending.

## Remaining checks

The four-way sanitizer configuration matrix (including enabled optional
defaults4/6), positive20 configured timing supplement, final source binding and
scoped review closure remain required. The normal default18-target and corrected
private M0/M1 checks are complete. Preserve each
receipt under a new name and release owned build scratch after copying results.

Genuine native compile/loader fit, loaded RAM/stack, full worst-case tick below
800us and P5.1-5.5 physical trials remain pending. A disabled optional mode does
not establish a memory reduction or qualify another mode. Future reduced-source
validation must distinguish actual reduced checks from the unchanged all-six
capability suite; see P5_mode_availability_release_validation.md.
