# Native power fixture whitespace normalization

Only trailing spaces/tabs, surplus blank EOF lines and checkout line endings were
normalized. All 29 scoped worktree files originally used CRLF; removing CRLF
from those bytes exactly reproduced their reviewed `e6b7060` Git blobs. All final
files use LF. Only five Git blobs differ: `cases.cc`, `ownership_cases.cc`,
`native_fixture.cc`, `stm32u5xx_ll_adc.h`, and `extract_bits.py`.

Before mutation, all 29 original worktree files and all 29 exact reviewed Git
blobs were saved in `fixture_normalization.before.zip`, reopened and compared
byte for byte. ZIP SHA-256: `8edf4a8dc3adbe140ddf31e924c280335232802c972a7afd33f07b2fc2d88927`.
`fixture_normalization.json` records every exact before/worktree, reviewed-Git
and after SHA-256, byte count, EOL count and verification result.

For existing lines, removing only trailing horizontal whitespace yields identical
line bytes. Backslash continuation status is unchanged at every line. C++ tokens,
assertions, field constants, fixture behaviors and vendor notices are preserved.
The extractor has one explicit additional two-line output formatting loop so
regeneration does not reintroduce the removed whitespace; its entire original
AST body is unchanged. This output-only addition is recorded verbatim in the
manifest rather than represented as a token-identical source edit.

Validation: extractor syntax compiles; rerunning it produces byte-identical
normalized outputs for all generated headers; scoped `git diff --check` exits 0.
`fixture_normalization.verify.json` retains command statuses and streams.
No driver/harness tests were repeated because no executable driver/test semantics
changed. Existing raw author/reviewer receipts, production, locked tests and
other agents' changes were not edited. No commit was made.
