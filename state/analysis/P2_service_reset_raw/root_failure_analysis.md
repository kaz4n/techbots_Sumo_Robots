# D103 boundary-test failure escalation

2026-09-23 Asia/Dubai. Independent test author preserves initial configured
failures in author/run_1790187185360734983 and corrected-oracle failure in
run_1790187256659436547. Production remains frozen at 1fbd7238; no locked test,
production threshold or predicate was weakened. Fresh reviewer notified.

The first test confused eligible next-S reset with successful first acquisition:
an actual reset may be followed by stale A1 and terminal Runtime failure. The
first correction compared the real source-start gap, but D087 independently
requires decision delta <=5000us (P2_button_routing_contract.md lines49-59).
The second failure is escalated to coordinator and separate reviewer, with public
S/D/A1/ADC chronology being captured before any further expectation change.

D103 inherits both continuity bounds. The addendum names them explicitly; it
does not lower a limit or make pending age alone sufficient. Test correction must
assert each actual delta and preserve reset-fresh/no-new-C on terminal failure.
If chronology satisfies both bounds yet fails, fix production rather than tests.
Pending diagnostic/reviewer disposition; original failed receipts remain.

Disposition: fresh reviewer independently read actual public chronology: oldD2158010, newD2163014/2163015, D gaps5004/5005 despite source gaps4999/5000. D087 requires both <=5000. No production defect. Final freeze07 preserves all expectations and adds positive zero-cost callback boundaries plus exact D5000/D5001 outcomes. See author/oracle_corrections.md; original failures retained.
