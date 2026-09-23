# D103 independent test author correction receipt

The author read the public frozen contract, public headers and existing fixtures,
never production implementation bodies. All original failed outputs and source
hashes are retained. No existing test, protected source or shared ledger changed.

- `run_1790187147838055319`: initial compile refused doctest's bare bitwise and
  logical expression decomposition. Parenthesized/explicit boolean checks preserve
  each predicate; freeze02 records the corrected source.
- `run_1790187185360734983`: 31/33 cases passed. The next-S clock test expected
  Transaction to clear an earlier completed report even though Runtime rejected
  its new clock before Transaction.open. D103 requires no invented completion,
  not erasure of an existing successful one. The corrected assertion retains the
  exact old C and token, requires Runtime FAULT and fresh=false, and proves no
  subsequent I/O. The same run exposed pending-age tests' incomplete oracle.
- `run_1790187256659436547`: source-start gap alone still predicted success;
  33/34 cases passed. Added actual source and decision diagnostics.
- `run_1790187282052084553`: diagnostic-only multi-argument CAPTURE did not compile;
  this doctest version supports one argument. Split into independent captures.
- `run_1790187320423737121`: complete evidence identifies pending source2158000,
  old D2158010 and C2158017. Pending S2162999 gives first source2162999..2163004,
  new D2163014: source gap4999 but decision gap5004. S2163000 gives first
  source2163000..2163005, D2163015: source gap5000 but decision gap5005. Runtime
  TRANSACTION fault and actual reset-fresh pulse are expected: D087
  `P2_button_routing_contract.md`, Robot admission and continuity, requires
  **both** source-start gap<=5000 and previous accepted decision delta<=5000.
  D103's Source-continuity clarification preserves that inherited rule across
  reset. The additional real A0 callback costs5us after A1; no private state or
  timestamp was forged. Root and independent reviewer confirmed this oracle.
- Freeze06 separates pending S admission from first-source/decision admission.
  Real A0 callback work0 gives successful4999/5000 boundaries. Work5 gives the
  expected decision-continuity fault after accepted reset. Exact source gap,
  actual battery callback count and decision gap=age+work are asserted. All34
  cases/6044 checks and the real postmatch strict receiver roundtrip passed in
  `run_1790187361928584298`.
- Freeze07 additionally includes S ages4995 and4996 with the same actual5us A0
  callback, proving exact decision gaps5000 (success) and5001 (terminal). This
  extends boundary coverage without weakening any existing expectation.

An assertion-backed public path was added for true INTERRUPTED recording:
actual RECORDING or DRAINING -> Transaction.abort -> INTERRUPTED and terminal
FAULT, then passive guard refusal. It does not pretend that interrupted evidence
can be paired with a healthy Transaction after an abort.

Unreachable bounded public states: UINT64_MAX token exhaustion and a healthy
Transaction with externally mutated/forged recorder/receipt are not injectable
through these public interfaces. Those code-path properties require source
review or established lower-owner tests, not hidden fixture mutation. The native
UART poisoning check supplies a POISONED setup callback and proves no retry or
reconstruction; it does not execute native UART hardware. Host callback timing
does not prove measured target latency, source readiness or physical A1 decoding.
