# D157 upload file limit validation

IMPLEMENTED / HOST-TESTED / scoped review PASS. No new board attempt.

Commit 3787649f adds upload_loader with a per-instance child file limit of
2,303,728 bytes. Legacy upload retains its original limit; frozen D153 remains
unchanged. Both diagnostic streams still require fewer than 1,048,576 bytes
for acceptance; their transient physical file ceiling is now 2,303,728 bytes.

The independent companion was authored from the contract and frozen before
execution. Existing tests were not edited:

- Legacy: 55/55 PASS, 3.595 seconds, exit 0.
- New loader entry: 59/59 PASS, 3.698 seconds, exit 0.
- All nine source/contract/oracle/support hashes match before and after each run.
- Separate real parent/descendant copy regression: 4/4 PASS, 0.393 seconds.

Commands and complete output are in P7_static_startup_raw/loader_limit_freeze.json,
loader_limit_legacy_first.json and loader_limit_first.json. The three records total
18,576 bytes. WSL fixtures used /dev/shm; a subsequent root find observed no
sumox_upload_contract_* directories. Python -B avoided bytecode.

Separate same-model review reused the design context: reviews/P7_upload_file_limit_review.md,
SHA256 fc1b241408f83607c69949d04e02a8ebdf9fea8abe302fd170bd70c8186ad851.
It verifies the actual small diff and receipts, with no material findings.
This is not fresh-context phase-gate or cross-model review.

D156 remains FAILED and consumed. D155 intentionally still pins the old uploader
and refuses the changed module. A fresh identified scope must select the new
entry explicitly, provide distinct ownership, and handle the known partial
/tmp/remoteocd file before any later upload. No retry, reset, capture, production
firmware/configuration/locked-test change, physical acceptance or human gate
follows from this host correction.
