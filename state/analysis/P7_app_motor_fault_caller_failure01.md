# D189 caller first-run failure

The first frozen sources actions509b15a3/run332a30e9 and independent oracles
2035499e/83c5fea6 executed after caller_freeze01.json (139 pins).
Actions: 13/13 PASS, 0.947 seconds. Caller: 19/20 PASS, 152.037 seconds;
only preparation-mutation subcase4 failed: local admission accepted an all-zero
upload sketch SHA in an otherwise scope-consistent preparation fixture.
Original receipts actions_test01.json/run_test01.json remain immutable; all139
pins unchanged. No fixture or locked-test amendment is requested.

Cause: local preparation checked shape/source/boot and pinned provenance, but
only the later remote adapter enforced exact artifact bindings. The contract
requires malformed binding refusal before local claim and staging. Add a small
exact local projection/check using pinned historical bindings and explicit new
identities/artifact values. Keep the remote checker and original tests intact.
Separate reviewer and independent test author are adjudicating the failure.
No native staging/upload/reset/capture occurred. The fresh separate read-only
admission01.json observes matching19files, stable Linux identity and absent
future owners. Command composition01 measures29667/28705Windows UTF16units.
