# D170 explicit fresh staging review

2026-09-25, Asia/Dubai. Separate fresh-context, same-model, read-only reviewer; no cross-model or human-approval claim.
Scope: tools/board_tool.py against 7d5fb453, clarified contract 539cf1c6, final independent tests 7b3efe58 and root-executed receipts.
Read AGENTS.md, current D170/PROGRESS and schedule. Production SHA256 73f14c294903d58fb8540739197aa98d2d400fc0fbdd10723bb10047b1eb35ce.

BLOCKER: none in this bounded change.
MAJOR: none open.
MINOR: none open.

- tools/board_tool.py:246 rejects non-directory, symlink and Windows reparse ancestry via lstat; checked ROOT/build/stage components are inspected before writes and rechecked after base creation.
- tools/board_tool.py:256 enforces exact str, portable bounded token and device-name exclusions; existing owners fail via lexists before resolution, containment is checked and owner mkdir is exclusive.
- tools/board_tool.py:277 claims a new owner only; destination/copy/config failures propagate while retaining partial evidence. Explicit mode contains no deletion, fallback or board invocation.
- tools/board_tool.py:283 is a verbatim extraction of legacy destination behavior; stage:297 preserves omitted/None behavior and all shared source-validation, layout and config-validation code.
- tests/tooling/test_fresh_stage.py:357 resolved fixture-only defect: Windows Python copy2 used CopyFile2 and bypassed the original copyfile injection. Installed stdlib confirms that branch; repair targets copy2 after actual copying and preserves every assertion. Original failed receipt/bytes remain at 0160d1a6.

Independently recomputed all 9 repaired freeze pins: exact. Production stayed unchanged through fixture repair.
Inspected fresh_stage_first.json: WSL 25 PASS/1 platform skip; Windows 16 PASS/1 fixture FAIL/9 privilege skips.
Inspected fresh_stage_repaired.json: WSL 25 PASS/1 platform skip; Windows 17 PASS/9 privilege skips. Actual Windows junction refusal PASS; WSL exercises skipped Windows symlink scenarios.
Inspected fresh_stage_regressions.json: all 91 unchanged methods PASS across five suites; owner 0/1 each 28 cases with 617259/617260 assertions; probe 0/1 each 2 cases/9 assertions.
Inspected fresh_stage_postcheck.json: retained D168 104 files/764049 B preserve byte/mtime digest df0fb658; original PROGRESS prefix unchanged; no fixture remnants, native commands or cleanup retries recorded.
Tests cover exact bench/app layout and hash, legacy sentinel preservation, invalid tokens/ancestry/owners, exclusive claim, retained copy/config failure, source refusal and legacy restaging.
Reviewer ran no tests, real staging, compiler, board or cleanup commands; only source/diff, fixture/receipt and local hash checks. Only this review file was written.

Verdict: PASS for D170 source and inspected host evidence only. No hostile concurrent-filesystem guarantee, target build, upload/reset, physical acceptance, motor-run permission or human gate is established.
Next: bind a separately identified fresh active artifact/capture scope using the explicit API; retained attempts and consumed native scopes stay untouched.
