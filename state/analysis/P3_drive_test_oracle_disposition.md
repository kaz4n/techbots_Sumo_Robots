# D123 first-run oracle correction

The first full normal run compiled all six targets. All four established targets
passed; each P3 target passed 26 of 27 cases. The sole failing assertion in the
new, unaccepted draft safety test compared the current cycle's Robot token with
the preceding cycle's token after a duplicate decision clock was rejected.

This expectation contradicted the existing D095 public contract:
`P2_app_transaction_contract.md` lines 71–78 explicitly reset the current report
on open, preserve the previous receipt, and reject a duplicate before Robot runs.
The unchanged `tests/test_app_transaction.cpp` cases already test a blank current
result and the retained previous token. Production behavior was correct.

The independent test author and separate fresh-context reviewer each confirmed
the defect from that contract and established tests. The author completed the
initial, unaccepted oracle with this exact replacement:

```diff
- CHECK(rig.owner.report().robot.token == before.token);
+ CHECK(rig.owner.report().robot.token == 0U);
+ CHECK(rig.owner.previous().token == before.token);
```

CLOCK, no-decision and actual inhibited-output assertions remain unchanged; no
production repair or safety requirement change was made. All 35 preexisting
locked files remain byte-identical. This correction of a newly authored draft
before acceptance is not permission to amend any established locked test.

Original draft `bed2418c6dd7bc2f2840694e0cbd0f7daa6969b0fd90e4e4c88a10ecd2d86aa3`
and the failing normal run remain in `P3_drive_test_raw`. Amended draft:
`5bde79679c8af6a362686acf205ac2401837b49da88eac1eec7cfd82a77fea0f`.
Executable expectations are re-frozen before the focused rerun. No skipped case,
weakened threshold, invented receipt or hidden failure is used to report success.
