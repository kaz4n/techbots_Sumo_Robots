# P0 ADC validation failures and corrections

2026-09-23: first full tooling run and independent focused upload check found a
new coordinator-authored test expectation defect in test_p0_adc_upload.py. The
test searched for the naked flag string as an argv element, whereas the public
Arduino CLI contract wraps it in compiler.cpp.extra_flags= and
compiler.c.extra_flags= properties. Actual tool output used both correct full
properties. Two transport subtests failed; no implementation failure or board
execution was hidden. Corrected this new unlocked test to require both exact
full property strings. All default/match/compile-only/source-hash/error checks
remain. Initial full receipt: P0_adc_tooling_20260923.txt; final rerun separate.

Before any implementation or tests, the initial D-063 draft had assumed zero
was an API error. Installed source established signed negative errors and valid
zero. Contract correction14f52d0 followed draft7a88867 and preceded dependent
code/tests. This was a fact correction, not a repair of a failing behavior test.
