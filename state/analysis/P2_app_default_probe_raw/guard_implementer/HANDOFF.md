# D118 standalone guard: first implementation handoff

Objective: implement the adopted7b364da5 guard contract without changing shared
upload policy or the nine-key inert manifest. Only production file changed is
`tools/app_default_run.py`, SHA256
`7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58`.

First bytes are preserved in `first_sources/app_default_run.py`;
`first_source_freeze.json` binds both contracts before any check/execution.
`first_static.json` records AST parse and compilation to a code object without
execution: PASS,29 functions, maximum38 lines. The module has not been imported
or executed by its implementer; no current test bodies were read. No board,
upload, MCU, firmware, manifest, shared-helper or ledger action occurred.

The route validates the exact request/environment/records/source map/current
local Git HEAD, stages and checks the91 source files, rechecks before transport,
uses unchanged core/sync/checked-build calls, retains the returned UUID artifact
directory, verifies exact ELF/ZSK hashes, then revalidates scope and stage before
an exclusive/fsynced attempt and one120-second upload. Actual upload outcomes and
local preparation/Git evidence have separate receipts. Import is passive.

Limits: static checks are not behavioral acceptance. Preparation inherits the
existing calls' incomplete wall-clock bounds. A timed-out upload may remain
indeterminate and consumes its attempt. Exact root-owned approval/run/review
records and a later run review remain prerequisites; no run is claimed here.

Next: coordinator executes the separately frozen independent fixtures and the
reviewer inspects this exact first source. Any coordinated repair must preserve
the first failure, exact diff and another source freeze before rerun.
