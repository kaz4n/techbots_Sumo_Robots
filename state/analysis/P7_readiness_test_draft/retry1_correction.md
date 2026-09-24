# D138 new-test compilation correction 1

The original independent test and `freeze.json` remain unchanged. The first
root compile receipt, `../P7_readiness_raw/normal_first.json` and `.txt`, records
`-Werror=class-memaccess` at the whole-Guard memset in the new test; no test ran.
`ui::Frame` has a default member initializer, so directly writing the enclosing
class representation triggers this diagnostic under the existing strict flags.

`test_readiness_retry1.cc` changes only that one initialization statement into
three fixed-size range fills: nine guard bytes, all 104 frame pixels and eleven
trailing guard bytes each receive `0xa5U`. Every assertion, stimulus, expected
pixel, case and guard sentinel is unchanged. No production file, established
test/helper, configuration, compiler flag or original freeze was changed.

This correction was derived from the compiler diagnostic and the public frame
type, without reading production implementations. The author has not compiled
or executed this corrected test. Separate review and root installation/execution
remain pending. `retry1_freeze.json` records both source hashes and preserved
first-failure receipts.
