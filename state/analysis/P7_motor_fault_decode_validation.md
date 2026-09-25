# D174 offline diagnostic decoder validation

IMPLEMENTED/HOST-TESTED,25September2026. Source68653597, decoder SHAf6e2fd36;
independent tests frozen7712ae0b, SHA b2995deadca8ffaafa1019b5ce51bab76f2e73cf878e26742fc3ac7722b52959.
The test author used only public headers, the contract and observed ARM ABI,
without reading implementation. A separate fresh-context same-model reviewer
inspected source and tests; its final disposition is in
../reviews/P7_motor_fault_decode_review.md. This is not cross-model/gate review.

First execution:22/22 unittest methods PASS,0.825s test runtime. Exact command:
`python -B -m unittest discover -s tests/tooling -p test_motor_fault_decode.py -v`.
All seven frozen input hashes unchanged before/after; no implementation or test
fix was needed. No native calls, builds, firmware/config/locked-test changes.
Raw command/stdout/stderr/status: P7_motor_fault_raw/decode_first.json.
Its started_at_dubai field was populated after command return: interpret it as
receipt-recording time, not a measured start timestamp. No hardware timing claim.

Coverage includes literal independent offsets for all64 Calls and4 Results,
all208 enum locations and367 boolean locations (including inactive/late slots),
all8 float locations, exact uint64 tokens, uint32 maxima and wrapped/reversed
timestamps, ignored padding/Port bytes, input type/extent refusal, all five
reported phases, absent flags, incomplete callbacks and preserved failure data.
The observed ABI manifest is hash-pinned; padding and callback pointers are not
interpreted. No callback or native transport is invoked by the decoder.

DECODED proves structural interpretation only. reported_phase retains the firmware
value; coherence remains UNPROVEN even for COMPLETE. This function establishes
neither capture origin, atomicity, electrical correctness nor the original fault
cause. All synthetic fixtures are host test data, not board measurements.

Storage: fixtures and transcripts are small; no generated binaries, staging,
dependency download, persistent scratch or Python bytecode is required. Retain
the independent source/freeze/result/review for reproduction. Next add the closed
exact-artifact inert profile to existing bounded upload/capture primitives; the
decoder alone grants no native operation or motor-run permission.
