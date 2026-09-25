# D178 offline capture failure retention validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED. Board disconnected;
no device commands, downloads, compiler work, firmware or physical gate changes.

## Outcome

`tools/dump_match.py` preserves its selected primary CaptureError even when the
single error.json write fails. The exception exposes the partial path and separate
journal error, keeps its original cause/connection evidence, and reports both
failures through CLI stderr. It leaves raw and partial journal bytes in place.
Successful capture, primary-error precedence and normal journal bytes are unchanged.
Interrupts are not swallowed; capture is neither retried nor published on failure.

Source: `3f73fd58`, SHA256
`baca4d79a6d6cbc53944a17e36faa1bc42223aa8195d734f65c70b4df935a651`.
Independent oracle SHA256
`5223b06aa42ad7107490367c3cee48d9d038ab5527aee2e0c4599a4fe4ee862e`.
Only one newly authored fixture was corrected after independent adjudication;
all established/locked tests are unchanged. See the retained failure analysis.

## Observed validation

- New oracle: **13/13 PASS**, 0 errors/skips, 0.263 s, process exit 0.
- Existing receiver checks: **45/45 PASS**, 0 errors/skips, 1.172 s, exit 0.
  Includes DumpParserTests, DumpCaptureTests and all ConnectionHostTests.
  The unchanged C++ producer and firmware-config registry methods were outside
  this Python error-handler verification; they were not run or counted as passed.
- WSL Python 3.12.3, Python -B, TMPDIR=/dev/shm. Test doubles prohibit actual
  network/process/device access. Tiny owned fixtures were removed by their contexts;
  final new-test scratch count 0. Injected ENOSPC is synthetic, not a full-disk trial.
- The ordinary error.json bytes match the original source exactly: SHA256
  `92939b6164b5b5db8e96b668f63bf73001c17131381eba01702079b712a0d9e1`.
- All 5 final task pins and all 11 prior D177 pins remain exact. The first
  140971 historical PROGRESS bytes retain SHA256
  `1dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77`.

Actual runner: PowerShell passes an in-memory unittest driver to
`wsl -d Ubuntu -- env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/dev/shm python3 -B -`.
It runs the frozen new test module; a separate driver selects the three legacy
classes with only the two unrelated methods named in the legacy receipt omitted.
The final driver compares pre/post hashes and the original journal bytes.
Equivalent focused rerun from the repository:
`wsl -d Ubuntu -- env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/dev/shm python3 -B -m unittest tests.tooling.test_dump_error_retention`.

## Preserved evidence

All names below are under state/analysis/ with prefix `P7_dump_error_retention`:
`_repro.json` (3228df7f), `_freeze.json` (90471804), `_first.json` (b11f8d6e),
`_repair_freeze.json` (cb4c0d73), `_repair1.json` and `_failure.md` (011b2394),
`_final_freeze.json` and `_legacy.json` (3f73fd58), and `_final.json`.
Original source failure and new-fixture failure remain reproducible from Git.
Eight compact JSON receipts total 46936 bytes. No duplicate build/source snapshot.

Separate fresh-context same-model review: **PASS**, no open material findings;
commit `7649fb58`, state/reviews/P7_dump_error_retention_review.md, SHA256
`baa7be36316199c8bbd78875c259e4dab672d3bd5d7cd7aad9607594a6669e60`.
This is a scoped code review, not cross-model review, a physical test or a human gate.

## Resume and storage

D177 inert command preparation remains checked and unchanged. The next native
work still needs fresh board identity/artifact/prerequisite checks and a reviewed
minimal caller before its inert upload/capture; no old scope may be reused.
Physical sensors/motors, startup/RAM/WCET, full acceptance and release remain pending.
Do not start gated P6 plotting as a substitute for those requirements.

Automatic approval review blocked cleanup of the explorer's exact Windows temp
folder C:/Users/narut/AppData/Local/Temp/sumox-offline-error-cyeoj212. Its remaining
input.wire is 2 bytes. Preserve it and do not retry through another path. All prior
denied targets remain untouched. C: free space observed 647581696 bytes at12:44Dubai;
this fluctuates independently and is not a cleanup saving.
