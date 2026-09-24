# Narrow correction of the new private receipt-order oracle

Root authorized this correction after preserved `normal_retry1_private` results:
M0 passed13/13; M1 passed12/13 and failed only the two ordinal0 assertions in
the prior-receipt/current-STOP case. The independently adjudicated public issue
is identical: FIRST_NONZERO_DUTY is a legitimate earlier event from that same
prior receipt. There is no corresponding production change.

Preserved byte-for-byte before editing: `private_spec_probes_first.cc`,
`freeze_first.json` and `run_private_first.py`. The original source remains
SHA256 `06a74b56981222d6476c9f3042cc1675c4aa8765b21c4896fb64f387932c7ac1`.
Original execution JSON/text receipts remain unchanged.

Only one case and its required `<cmath>` include changed. The unique APPLIED
event, exact prior A, no INTERRUPTED, current STOP/EN-low and nonempty batch
assertions remain. APPLIED value1 is now explicit. It may appear at index0 or1;
index1 requires exactly the FIRST_NONZERO_DUTY event from the captured prior
full-token, valid/enabled receipt. The predicate must agree with actual nonzero
wheels; its timestamp must equal prior A/D, its wheel mask and signed rounded
duty bytes must be exact, and applied signs/magnitudes must fit the pending
governed request. No STOP/state/fault/current event may precede APPLIED.

All other12 cases are byte-identical. The active runner changes only its private
source hash binding; case count13 and all link/exclusion/receipt safeguards remain.
`freeze.json` identifies this post-failure correction while `freeze_first.json`
preserves pre-implementation independence provenance. No compiler was run here.

Corrected private source SHA256:
`f9eb1025f49238d985c7f5adf9c433cf3272433049deea09d6e92de23c8487ca`.
Next: root refreezes the full input manifest and runs the corrected13 M0/M1.
