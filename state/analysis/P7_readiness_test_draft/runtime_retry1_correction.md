# D138 new Runtime-test compilation correction 1

The root's preserved `../P7_readiness_raw/configured_first.json` and `.txt`
record a compilation failure before execution: doctest rejects the direct
three-term `CHECK(a || b || c)` expression as too complex to decompose.

`test_readiness_runtime_retry1.cc` adds one enclosing parenthesis pair around
that complete expression. The three conditions, short-circuit evaluation,
assertion, test case, stimuli and other source bytes are unchanged. The original
`test_readiness_runtime.cc` (`e13f301d...`) and original `freeze.json` remain
unchanged. Production code and installed tests are not modified by this author.

A static scan of the newly authored corrected pure and Runtime files found
only two CHECK expressions containing logical operators. The corrected expression
is now fully parenthesized; the other already has its `&&` within the parenthesized
right-hand side of an equality comparison. P7_REQUIRE explicitly evaluates into
a bool before its CHECK. No other matching compile-only correction is needed.

The author read only the diagnostic, authored tests and public API material;
no production implementation was read and no corrected test was compiled or
executed. Separate review, installation and root rerun remain pending. Exact
identities are in `runtime_retry1_freeze.json`.
