# D199 SETTLE report ABI inspection preparation

The file-only inspection wrapper passes 66 independent Linux tests and 64
Windows tests. One Windows symlink-privilege skip and one Linux FIFO skip are
both covered on Linux. All 192 frozen inputs remained unchanged. This is host
validation; the new image's target report has not yet been observed.

## Scope and source

Contract `dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956`
binds the D198 source117cc0e7, manifestaa314548, result9b7f0c44 and artifact
receipte18384c1. Wrapper inspect_static_abi.py is 16,106 bytes, SHA256
`0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea`.
Fourteen checked substitutions preserve the D194 ABI02 lifecycle while adding
three used types and 62 expressions: 23 subjects, 223 expressions and all eleven
Runner windows. The separate report must match observed fields/enums, one local
28-byte object, alignment four, the checked initialized BSS and no Runner overlap.

The wrapper preserves the five bootstrap functions, raw receipts, original-first
private composition, Windows descriptor exception, four bounded file commands,
all remote/local closing checks and first-error handling. It neither compiles
nor uploads firmware, resets the board, reads MCU memory or accesses credentials.

Initial contract a0e96100 is preserved in d04234dc. Before implementation, review
removed six queries for unused constexpr constants whose debug visibility is
not guaranteed. Validity masks remain pinned-source semantics, not fabricated
target answers. Used types, valid-field width/offset and reason values remain
mandatory observations. This is not a fallback after a failed device query.

Initial source6faa240e is preserved in f4c8c6aa. Static review caught three echo
literal sites producing actual LF rather than literal backslash-n. The bounded
three-backslash correction occurred before any tests or native execution.

## Independent tests and fixture correction

The test author froze the oracle before reading, hashing or importing the new
implementation. It retains 46 selected behavioral methods and adds 20 methods.
The freeze explicitly identifies inherited methods, excluded historical-only
metadata tests, current metadata projection and synthetic packet changes.
Tests cover actual private loading/preparation/closure, strict marker parsing,
every new numeric field/reason, duplicate symbol identities, BSS boundaries,
raw preservation and error paths. Synthetic addresses are not target evidence.

The first 66-test round passed on Linux and passed with the same two Windows
skips. Review then identified a fixture coverage regression: the appended report
redirected an inherited final-row duplicate-Runner subcase to the report. Commit
e3e69d9e preserves that oracle, first passing receipts and original freeze.
The independent author restored the Runner's final-row position and selected
the report by its exact symbol in its new test, adding a uniqueness assertion.
All prior assertions and 66 methods remain; the implementation is unchanged.

Final oracle is 30,983 bytes, SHA256
`96763b42d61b80654503f4093d32ac3b174ab2152fdfb795b3801304e4e2b252`.
Independent freeze02 is `46c51e3f3fffaaa83a37cc9cfe91a045b0b6c219d925a730918ea327330bd661`;
coordinator freeze02 is `89cb2daf4b9e3098e07fff66a21ff5ba8ae32cf5810c2ddb10803b2690687cf7`.
Final Linux result is `98fd35bd42a9a27f1514fb786675cbda3667adf1fb238d20cb9fe49c4b795d54`;
Windows result is `218d732cc730b885e8351e0b05e1f56779560b7a48c3cbfdeb7fbf0ba898ad63`.
[Host closure](P7_motor_settle_compile_raw/abi_host_closing01.json), SHA67b640ce,
records all 192 stable pins and zero owned fixture remnants on both platforms.

## Next action and limits

The independent source/host review is
[P7_motor_settle_abi_review.md](../reviews/P7_motor_settle_abi_review.md).
After a clean reviewed HEAD and check-only admission, execute the fixed new
native_abi_static01 owner once. Preserve any failure without an automatic retry.
Then derive entry ranges from this image's actual symbol table and inspect the
publication instructions before a separately reviewed inhibited capture.

D195 remains the latest flashed diagnostic. The internal SETTLE cause, a repair,
production RAM/stack/timing, physical acceptance and human gates remain open.
The 150-us and 4,096-poll limits and all firmware/configuration bytes are unchanged
by this inspection work.
