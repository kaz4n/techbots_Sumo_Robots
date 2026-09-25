# D181 preserve compiler failure across receipt-write failures

25 September2026, software-only continuation under D051. The current public
tools/board_tool.py capture_app_command catches CalledProcessError, then writes
stdout/stderr receipts. A synthetic stdout ENOSPC replaces exit43 with exit2,
omits the stderr write and hides the original compiler failure in main's message.
This is a concrete offline defect in P0 error propagation/P7 build evidence.

Scope: tools/board_tool.py only, additive independent tests and compact evidence.
No command, transport, argument, build/upload permission, source pin, firmware,
locked-test or target behavior change. Historical D179 pins remain unchanged.

## Corrective contract

Preserve public signatures, explicit-runner selection, successful result identity
and successful raw-receipt bytes. Keep the command receipt BEFORE dispatch;
its failure still prevents any runner invocation. No retry or cleanup.

After a captured command fails with CalledProcessError (raised by the runner or
constructed from its nonzero CompletedProcess):
- Re-raise that same primary object. Preserve returncode, cmd, stdout, stderr,
  cause and context. main must return that compiler exit code, not a secondary
  receipt error code. The normal final ERROR diagnostic names the primary error.
- Attempt each existing stdout.json/stderr.txt write independently exactly once,
  in that order, with the unchanged text/UTF8/None-to-empty treatment.
- Catch Exception from those writes, not BaseException. Attach
  evidence_write_errors as a list of dicts with exactly path,type,message,
  ordered by attempted stream; use string path/class name/str(exception).
  The list is empty on an ordinary failed command whose receipts were saved.
- The failure diagnostic identifies the receipt directory and each failed path,
  exception type/message, and says it could not save that output. Do not claim
  both files were saved. Retain any partial bytes; never reopen/retry/delete.
- Diagnostic stderr can itself fail: make these error reports best-effort, and
  retain such Exception details on diagnostic_write_errors (list of type,message
  dicts on the primary error). Preserve the primary exception/CLI code even then.
  Do not catch BaseException. An unavailable console cannot promise visible text.
- On a command success, receipt-write failure must still fail explicitly; do not
  return success or create a verified build receipt. This task does not change
  successful-path receipt ordering/error semantics.

main's existing caught-error diagnostic uses the same best-effort reporting so
the selected error's exit status survives a failing stderr writer. Existing
non-CalledProcessError failures keep exit2. No new exception class, journal,
alternate output path, command or receipt schema. Exception metadata is in-memory.

## Independent validation

Author tests/tooling/test_compile_error_retention.py from this contract and the
existing public test_compile_executor tests, without reading board_tool.py.
Freeze before running against the original source. Use in-memory controlled
runner/file-output failures and, where needed, tiny owned /dev/shm fixtures.
Python-B; no subprocess/device/network calls, no actual compilation or source
copies. Cover raised and returned command failures, None/raw streams, each/both
write failures, partial write retention, exception identity/cause, main exit and
diagnostics, diagnostic-write failure and BaseException propagation, command
receipt failure before runner, unchanged successful capture and success-write
failure refusal, one runner/no retries. Retain initial failing output, then apply
a bounded source repair and run relevant unchanged test_compile_executor cases.
Separate fresh-context same-model reviewer inspects actual diff/results.
These are synthetic script tests, never target/build/physical acceptance.
