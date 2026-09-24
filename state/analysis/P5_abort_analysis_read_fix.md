# D136 ordinary-read and builtin declarator correction

2026-09-24 Asia/Dubai. Bounded source correction only; execution and acceptance
remain coordinator/reviewer tasks. Ownership is this note and
`tools/analyze_opener_abort.py`; no tests, firmware, configuration, tooling
dependencies, ledgers or review files were changed.

## Evidence before editing

The adopted contract permits ordinary unconditional reads of its seven uniquely
declared historical constants, while rejecting duplicate or unsupported
declarations. The second repair review identified two new cases: a read within
`alignas(MODE_ARC_ENABLED)` was rejected because the prefix alone omitted its
closing delimiter, and `unsigned short (TICK_US) = 2000U` escaped the finite
parenthesized-type predicate.

The inspected baseline SHA-256 was
`1c124dfe816f90faf694c1820376b6a6a5a0cf60f7e8d1e84558a82914195fd0`.
The coordinator reported independent freeze `3983610e`, two new methods with
338 subcases, 32 failing subcases on that baseline, and preserved receipts in
commit `16b750e4` before authorizing this edit. Those test bodies were not read
by this implementation author, and no test/analyzer execution was performed
here. Prior successful and failed source/receipts remain preserved.

## Exact source scope

- `_without_declaration_decorations` now receives the existing suffix and balances
  delimiters across both sides of the current identifier. The omitted identifier
  contains no delimiter. A decoration that closes beyond the prefix contains
  this occurrence as an argument/read, signaled by `None`. Unbalanced decoration
  still reports unsupported configuration; complete decorations preceding a
  declarator are stripped as before.
- `_extra_declarator` treats that explicit sentinel as an ordinary read. Its
  existing declaration checks continue for names outside decorations.
- `_parenthesized_declarator` now recognizes a finite sequence of builtin type
  keywords with cv qualifiers, including `unsigned short`, `short unsigned` and
  `long unsigned`. An ordinary variable identifier before `(` still cannot match
  this builtin sequence. This is a bounded lexical classifier, not a C++ parser
  or an assertion that arbitrary C++ input compiles.

The canonical `inline constexpr std::uint32_t NAME = <digits>U;` extraction and
its strict literal/declaration-prefix checks are unchanged. No report, wire,
source-hash, manifest, chronology, owner/loss or timing arithmetic changed. All
three touched functions remain below 60 lines.

First corrected source SHA-256, reported to the coordinator before execution:
`65cba907d3a425e24706b6ca44a6e4a671971d9c75f5955f7bfe46342cf9d5f1`.

## Handoff

Run the already-frozen independent methods and existing public/private checks
against the exact corrected hash, retain first outcomes, then review source and
receipts separately. This is the first correction for the newly reproduced
ordinary-read/type-head cases. No compiler, board, network or MCU operation was
performed; no target, hardware or phase acceptance follows.

## Qualified-type follow-up

The coordinator subsequently reported that the first corrected source passed
91 public/declaration methods and 19 private methods. Separate source review
identified trailing cv qualifiers, global `::` qualification and nested
parenthesis/pointer/reference forms as further finite declarator cases. Source
`65cba907d3a425e24706b6ca44a6e4a671971d9c75f5955f7bfe46342cf9d5f1`
remained unchanged during independent preparation. The coordinator reported a
new two-method, 156-subcase freeze `520413ab`, byte-exact test transfer and an
exit-1 first run with 42 failing subcases, preserved in `c7003e6c`, before
authorizing this follow-up. Those new test bodies were not read here.

Only `_parenthesized_declarator` changes in this follow-up:

- Replace standalone `const`/`volatile` tokens in its prefix with spaces, retaining
  token separation while allowing cv qualifiers around the type and pointer or
  reference tokens.
- Recognize a final run beginning with `(` and containing only whitespace, `(`,
  `*` and `&`; retain the count of opens and the existing exact closing/suffix
  requirement. This covers `(* const NAME)`, `(*(NAME))` and `(&(NAME))` without
  consuming another identifier.
- Permit an optional leading global `::` on the existing single qualified-type
  alternative. The remainder still must match exactly one qualified typename or
  a finite builtin-keyword sequence, with its pointer/reference tail. An ordinary
  variable identifier before an initializer remains outside that type-head match.

No decoration logic, canonical extraction, report, other module or test changes
are included. No parser framework or C++ compilation claim is introduced. First
follow-up source hash, reported before any execution:
`8e002c6f627e1cb39af94d244a3ba62b817967e9d0e8ceac7497f9f6eb52c4d2`.
The implementation author performed source reads/diff/hash checks only; frozen
test execution and final review remain with the coordinator and reviewer.
