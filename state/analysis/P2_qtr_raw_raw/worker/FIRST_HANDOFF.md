# D109 first implementation freeze

Owned source only: `bench/qtr_raw/qtr_raw.ino`, `src/qtr_raw.cpp`,
`src/qtr_raw_native.cpp`, and private additions to `src/qtr_raw.h`.
The frozen public native header and root-owned README remain unchanged.
No author test bodies, shared implementation, configuration, tooling, ledger,
old tests or hardware operations were involved.

`first_sources/` preserves all five bench source/header files before checks or
fixes. `first_source_freeze.json` records their SHA256 values plus the adopted
contract/config hashes. Main source is
`54b0a21b7b2867d9f816f476bec2b8cddf7b6ca7f902b7e682ccce2a9bceed33`.

Strict C++17 syntax passed for all three translation units with temporary
capacity128,1,0 source copies, `-Wall -Wextra -Wpedantic -Werror`, and only a
minimal Arduino micros declaration. This is syntax evidence, not native linking
or target evidence. `first_syntax.json` preserves every command/result. Whitespace
checks pass; `first_function_lengths.json` finds42 functions, maximum27 lines.
The five source hashes remained unchanged after these checks.

The runner retains fixed immutable captures, distinguishes shared raw validation
from wrapper chronology, hides tentative slots until valid C, and preserves
separate one-shot cancellation evidence. Native owns one Reader; actual sketch
grants default false. Independent runtime/binding tests and root target builds
are still pending. No physical, loader, full invocation WCET or gate claim.
