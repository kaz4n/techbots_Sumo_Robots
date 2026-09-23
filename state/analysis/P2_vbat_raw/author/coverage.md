# D110 independent author coverage

The test oracle comes from the adopted D110 contract, public vbat/power interfaces,
existing config and D078/D086/D093 contracts. No production implementation body
was read. The author retains D104-D109 context and shares the same model as the
other agents; this is separate-context implementation independence, not fresh
whole-repository or cross-model review. Executable tests were frozen before use.

The source declares31 ordinary/special cases and two actual Native/default-sketch
cases. Multiple loops/subcases test distinct stimuli; category counts are not
claimed to be individual production requirement counts. Every Sample and Capture
member is compared explicitly; float bit copies preserve actual diagnostic NaNs
and negative zero without relying on struct padding.

- Passivity covers constructors, copied ports, null context/stateless callbacks,
  default grants, prebegin/repeated/terminal calls and capture bounds. Disabled
  precedence and all three absent callbacks are checked with no clock/native call.
- Setup exercises every known non-OK Status with every Shutdown and both ready
  values, unknown enums, contradictory OK shape and first-cause priority with
  failed A/C. Exact setup/read/poll brackets and timing counts are observable.
- Acquisition checks raw0/16383, exact nominal scaling, negative zero, repeated
  equal numerical conversions, nonfinite/scaling/range/enum errors, and all known
  failure statuses/shutdowns. Failed diagnostic payload is preserved unchanged;
  success-only constraints are never incorrectly applied to native failure.
- The public report is inspected from the actual A clock callback to verify that
  the returned sample/sample_seen and cleared acceptance/timing flags are already
  visible before the closing observation. No private state is accessed or seeded.
- Successful source brackets, reversal/future/past fields, spans0/99/100/101,
  exact S/A/C, natural wrap, reverse/half-range clocks and aggregate operation
  closure are checked. Invalid A/C suppresses later clocks and publication.
- Cadence cases check first/immediate, P-1/P/2P-1/2P/3P+1, one read per due poll,
  early-poll history and timing preservation, exact missed_before/cumulative
  counts, failed-read skips, delayed C reanchoring and no second skip calculation.
  Previous source age remains active through S/A/C and cannot be rescued early.
- All128 slots retain exact values and stable addresses through every subsequent
  append and terminal pulse clearing. Capacity1 runs applicable cases; capacity0
  executes only passive/missing/config cases. Bad C hides the tentative slot and
  keeps prior history. Heap wrappers cover construction/setup/read/destruction
  and every ordinary complete append.
- Eleven invalid-config profiles cover zero/half-range period, zero/too-large
  conversion, exact2.4F/next-above3.6F/NaN/infinite reference, and below1/NaN/infinite
  divider. Five valid profiles cover next-above2.4F,3.6F, divider1, conversion=period,
  and unused maximum-age0, proving that no retention-age dependency was added.
- The adopted period=conversion=1 profile executes missed-release arithmetic
  through exactly UINT32_MAX and one attempted overflow in five public captures.
  The period=HALF-1 profile accumulates source half-range through early polls,
  using individually admitted deltas. Both special profiles run normal/sanitizer.
- Counted Reader methods execute the actual Native binding, detecting any call
  to beginWithButtons/readButtons and proving one stable battery-only owner.
  Actual default sketch setup plus10000loops is executed and must make no callback.
  Native constructors, port factories and destruction remain passive.
- Three forbidden MATCH/MOTORS profiles must fail actual sketch static assertions.
  The existing registry source is checked as raw bytes against the author-owned
  pre-addition snapshot; only the coordinator's one literal128 line is permitted.
  The unchanged D106 wrapper runs all18 original checks, its original three wrong
  D096 profiles, and a copied battery-capacity129 refusal using the old assertion.

Native and config profiles intentionally select only their relevant cases; these
filters are recorded in exact command receipts. The native prefix filter is
case-insensitive in doctest: it executes the two intended binding/sketch cases
plus the ordinary native-read-failure case, for an observed3 cases/911 assertions.
This harmless additional execution is retained without changing the frozen tests.
Other impractical saturation
branches remain source-reviewed. No GPIO/ADC acquisition, hardware permission,
native timing, multimeter error, physical clock fidelity or human phase gate is
established. Default-false execution does not claim to collect voltage data.
