# D110 implementation handoff

Implemented finite battery capture only in `bench/vbat/vbat.ino`,
`bench/vbat/src/vbat.cpp`, `vbat_native.cpp` and private portions of `vbat.h`.
The added config include supports private fixed storage; public declarations
and `vbat_native.h` are unchanged. Root owns the separately added config count.

The default sketch uses false grants. Native holds one battery-only Reader and
forwards begin/read directly. The runner preserves actual native results,
first-fault priority, source-age cadence, saturating missed-release counts,
tentative-before-C capture and immutable publication. It adds no cleanup call
or claim that stopping callbacks disables ADC1.

`first_source_freeze.json` and `first_sources/` retain the initial bytes before
checks. The only subsequent source correction moved `sample_seen=true` before
clock A, following the literal contract. `second_source_freeze.json` and
`second_sources/` retain those current bytes plus root's configured snapshot.
Current CPP SHA256:
`b5fa7eea988e91a9b0fdb350b34fed982cef9893bde47e56c289e07a403c0475`.

`second_syntax.json` records strict C++17 `-Wall -Wextra -Wpedantic -Werror`,
no-exceptions/no-RTTI syntax success for all three translation units under six
temporary profiles: capacity128/1/0, period0, period2^31 and period=conversion1.
The actual config was not changed by these checks. The clock used a declaration
stub; no native linking or executable behavioral claim follows. Function-length
evidence is in `second_function_lengths.json`; every definition is under60 lines.

No independent test bodies were read, and no board or hardware action occurred.
Independent behavioral/native tests, target compilation/loader audit and review
remain with their respective owners. Physical ADC accuracy and WCET remain open.
