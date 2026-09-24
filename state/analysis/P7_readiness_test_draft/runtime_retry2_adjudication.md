# D138 new Runtime-test expectation correction 2

The first executed configured suite preserved in
`../P7_readiness_raw/configured_retry1.{json,txt}` and its LastTest log reported
30/31 passing cases in each motor build. The only failure was the new Runtime
test's expectation that `low_battery` remained false immediately after its valid
ADC input changed from 11000 to 9000 while the Robot stayed in IDLE.

## Independent specification finding

- `state/analysis/P1_robot_contract.md:104-106` requires warning onset on a
  strict-under-threshold valid IDLE sample, with valid non-low rearming.
- `docs/BEHAVIOR.md:558` defines the low-battery detection as vbat below WARN
  in IDLE. It specifies no warning-filter delay.
- `docs/BEHAVIOR.md:291` and `src/core/governor.h:39-43` assign the one-second
  filter to governor duty compensation, not warning detection.
- The established case `tests/test_robot_events.cpp:362-386` tests immediate
  warning episodes and non-low rearming. `tests/test_power_inputs.cpp:322-341`
  exercises retained input through the separate Governor voltage filter.

Therefore the warning must be true on the first admitted low IDLE sample. The
original false assertion imported an unsupported filtered-warning policy. This
finding uses specifications, public headers and existing tests only; no companion
implementation was read. Root adopted the bounded correction after separate
review. The D138 pure fault-mask/threshold tests separately exercise marker
independence with conflicting voltage and diagnostic-bit inputs.

## Exact bounded correction

`test_readiness_runtime_retry2.cc` derives from unchanged retry1 `e0714344...`.
Only the configured test case is renamed; its erroneous false warning assertion
becomes a true warning assertion, preceded by explicit IDLE, valid-battery and
accepted-raw-9000 preconditions. All marker3, no-R, initial non-low, low-observed,
zero-receipt and no-motion assertions remain. Every other case is byte-identical.
All changes occur within `APP_TEST_CONFIGURED_BUTTONS`; no ordinary source text
outside that block changes. Original drafts, retry1, freezes and failure receipts
remain unchanged. Current installed tests and production were not modified.

The author has not compiled or executed retry2. Root owns installation and rerun
after the ongoing default matrix ends. `runtime_retry2_freeze.json` records exact
identities and preserved evidence.
