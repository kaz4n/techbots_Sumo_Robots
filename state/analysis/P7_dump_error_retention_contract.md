# D178 preserve capture failures when error reporting cannot be saved

Host-only P7 log-preservation repair, under D051 and the user's explicit request
for continued development without hardware. D090 remains the governing receiver
contract (P2_dump_contract.md, receiver/frozen API); P7 task 7.2 needs truthful
saved-log failures. No firmware, transport command, schema, limit, pin or gate changes.

Reproduced defect: after a protocol failure, save_capture writes error.json
without guarding that write. A second ENOSPC exception replaces the public
CaptureError, the original failure message/code and the partial-directory path.
The CLI returns failure but loses those actionable diagnostics. Raw bytes remain.

## Narrow corrective contract

Keep existing primary-failure selection, including connection/wire precedence and
_receive_failure precedence, and existing error.json payload unchanged.
Once save_capture owns a partial directory and catches a capture failure:
- Try to write error.json exactly once, as today. No retry, alternate journal,
  cleanup, publication or new transport may follow that failure.
- If that journal write raises an Exception, retain the primary CaptureError
  code/message and original exception chaining. Return neither success nor a
  raw secondary exception. Do not catch BaseException (interrupt/termination).
- The raised CaptureError always names the existing partial directory and exposes
  partial_path as its string path. It retains connection_evidence exactly as before.
- CaptureError instances default partial_path and evidence_write_error to None.
  After a failed journal write, evidence_write_error is a dict with exactly type
  (exception class name) and message (str(exception)); otherwise it is None.
- Include the secondary write failure's type/message in the raised text after
  the primary diagnostic and partial path, explicitly saying the error report
  could not be saved. CLI stderr therefore exposes both failures and the path;
  exit remains 1. Do not claim the error report exists or is complete.
- Preserve retained raw files and any partially written journal bytes; no re-open,
  replacement, rollback or deletion. Successful captures and error writes remain
  byte/schema compatible. Validation/permission failures before ownership retain
  their existing behavior. Existing assertions and locked tests stay unchanged.

## Independent acceptance

Author a separate additive tests/tooling/test_dump_error_retention.py from this
contract/D090 public API and existing literal wire fixtures, without reading the
subject implementation. Freeze before first execution. Cover primary protocol,
input-generator OSError, preferred transport failure, connection evidence, bundle
or publication failure, journal OSError/serialization error, a partial journal
write, unchanged success/error JSON, one write/no retry/no publication on failure,
exception cause, partial bytes/path and CLI exit/stderr. Include a successful
synthetic offline capture and prohibit real network/process/device calls.
Use small owned RAM fixtures with Python -B. Coordinator will run new tests on
original source to preserve regression evidence, then bounded repair plus relevant
existing receiver/connection tests. Independent source reviewer checks real diff,
results and no changed established assertions. Synthetic injection is not actual
full-disk or hardware acceptance. No target build is required for a Python-only fix.
