# B4 application entry inspection

The fixed B4 entry checker reuses the accepted ordinary-entry algorithms and
the current B4 ABI reader. It binds the D214 motor-disabled image and all 155
source inputs, with 64 selected function groups, 77 aliases and 10,488 bytes.
The four file-only tool calls contain 129 GDB expressions. No compiler, upload,
reset, MCU access or motor-run permission is part of this inspection.

The first Linux test invocation stopped in independent fixture setup before
subject import: the fixture compared a hash dictionary with the new binding's
two-item identity list. That zero-test failure, original test and original
oracle are retained. The repair normalizes only the two explicit identity
formats; all eight test methods and assertions are byte-identical. The checker
source was unchanged. The known setup failure was not repeated on Windows.

The corrected focused suite passed eight tests on each platform, without skips.
All 169 frozen inputs remained unchanged. Root closure
`P7_b4_app_compile_raw/entry_host_closing01.json` reconciles all 16 accepted
outcomes and the saved first failure. Its hash is
`b29e8d7ce7f51641ffa95749efdaae749f3b7834084fa311725635ae852531c2`.

Checker: 18,983 bytes,
`b21582816f26b3dbc7e2ca961d186840aed5606ee50b3426f9c5187fa00362bc`.
Binding: `fb2ab19d0cd0337f7d74a9578eee58d2e0029bf8a45ad6851a9ddbf558c79d55`.
Contract: `bcc3072ccb1a219c3cf70ab92ce78d6e140fb4b619b2a370fc56d112a6daa543`.

The concrete native scope is `entry_native_scope01.json`, hash
`4b0a7303a263dcaa6f0d68e7c156ee907352861c3727a83581ed20b2819a278f`.
Its execution follows final independent review and a clean committed snapshot.
The initializer bytes remain expected until the actual file observation.
Seven B4 strategy interiors are outside this selected-instruction scope.

This work does not establish a closed call graph, live RAM contents, initialized
WCET, electrical inhibition, a completed B4 sequence or physical acceptance.
The latest verified loaded firmware remains the ordinary inhibited D212 image.

Actual outcome: the single file-only attempt subsequently passed independent
review `e2bf58f4`. See [actual validation](P7_b4_app_entry_actual_validation.md).
The initializer expectation is now observed in that exact compiled image.
