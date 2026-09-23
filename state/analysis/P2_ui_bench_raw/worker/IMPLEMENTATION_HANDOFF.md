# D112 implementation handoff

Final second source freeze: the coordinator clarified callback-visible provenance
before independent execution. Move only `report_.sample_seen = true;` before
the A clock callback, immediately after saving the actual ButtonSample. No
validation or decoder work precedes A. Current ui_bench.cpp SHA256 is
`bc2def36d611f534112288dfca538ab36d51aff58d73c7e5e09eb1f0d9a7e70d`;
the other four source hashes below are unchanged. `second_source.diff`,
`second_source_freeze.json` and `second_sources/` preserve the exact change before
checks; all first-source evidence remains intact. `second_syntax.json` again
passes8 profiles with unchanged source hashes; `second_function_lengths.json`
again reports30 functions/max23 lines. The first target snapshot is superseded;
the coordinator owns separate corrected target builds.
`second_clarified_contract_binding.json` appends the exact2adfd435 contract
dependency after the coordinator's literal edit completed seven seconds after
the second freeze; the original receipt remains intact and all source hashes
match. This is a qualified dependency update, not an additional source revision.

Implemented the adopted finite A1 evidence bench in only `bench/ui/ui.ino`,
`src/ui_bench.cpp`, `src/ui_bench_native.cpp` and private Runner state/helpers
in `src/ui_bench.h` under that bench. The header adds config.h solely for fixed
private storage. Public fields/signatures and the Native header are unchanged.
No existing HAL/core/config/tool/test/README/ledger or hardware changes.

The Runner stores128 configured immutable raw/decoder records, uses actual
source-start cadence and bounded missed-release arithmetic, requires first1
then contiguous source sequence, and admits S/A/C with aggregate half-range
guards. Accepted A delivers the actual decoder even for native semantic failure;
bad A preserves older decode with decode_matches_sample=false. Publication
requires healthy C. Logical unconfigured/unknown/ambiguous/invalid diagnostics
are preserved without being promoted to valid button observations. Native binds
one Reader's beginWithButtons/readButtons. Default Grants{} performs no callback;
terminal calls do not invent ADC shutdown or recovery.

`first_source_freeze.json` and `first_sources/` preserve exact initial source
before checks. The initial checks required no fixes; the later coordinator
clarification and current hash are documented above. Initial frozen SHA256:

| File | SHA256 |
|---|---|
| ui.ino | be6dd812eac69d4d1df49a4bbc04378d799604a065ef27abdf22212b03a09139 |
| src/ui_bench.h | 881eceb27b8eb54654777529b50c8df49597a2303352f11f9b34695310e7094e |
| src/ui_bench.cpp | 9c0382c9693ffd8d256d41035c0fdcd4193985da6e54a2a518ebb2e877569050 |
| src/ui_bench_native.h (unchanged) | 74d66c0ff294ce09ff1a1eaa387c686b3726557cac19e2027e1f6e1c1144fee4 |
| src/ui_bench_native.cpp | a9bd1c4d71cb167a94953194435857c88823ffd755db89d80ed9dccb6a2381d0 |

Strict C++17 `-Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti`
syntax passes for all three owned TUs plus unchanged actual decoder across8
temporary config profiles: capacity128/1/0, TICK0/half-range, conversion0,
TICK=conversion1, and BUTTON_WINDOWS_CONFIGURED2. `first_syntax.json` records
argv/compiler/status and confirms every frozen source hash is unchanged.
`first_function_lengths.json` reviews30 functions, maximum23 physical lines,
all below60. Scoped Git whitespace check passed with only a CRLF-to-LF notice
on the private-header edit; source bytes were preserved.

No behavioral suite, target compile, native runtime or physical claim is made
by these checks. Independent test bodies/expected values were not read.
The coordinator owns the checked target route and full validation; independent
author/reviewer execution is the next action. No new upload authority exists.
