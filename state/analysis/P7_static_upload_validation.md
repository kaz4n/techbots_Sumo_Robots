# D154 upload wrapper validation

IMPLEMENTED / HOST-TESTED / scoped review PASS, 25 September 2026 Dubai.
No native upload, reset, capture, compilation or production change occurred.

The fixed [contract](P7_static_upload_contract.md)7fa1c0f0 and
[bindings](P7_static_startup_raw/upload_bindings.json)a31bca78 constrain the
one-shot wrapper to the existing inert D144 packet. Current implementation
81668c79 is committed in4dffe29d. It retains process outcomes and the primary
failure even when later stream cleanup also fails.

| Check | Actual result | Evidence |
|---|---|---|
| Original independent suite | 53/55 PASS; two failures, exit1 | [Original receipt](P7_static_startup_raw/upload_first.json) |
| Implementation repair1, unchanged suite | 55/55 PASS,3.685s,exit0 | [Freeze](P7_static_startup_raw/upload_repair1_freeze.json), [receipt](P7_static_startup_raw/upload_repair1.json) |
| Reviewer supplemental cleanup cases | 3/3 PASS,0.205s,exit0 | [Freeze](P7_static_startup_raw/upload_private_freeze.json), [receipt](P7_static_startup_raw/upload_private_first.json) |
| Separate same-model review | PASS; both MAJOR findings resolved | [Review](../reviews/P7_static_upload_review.md)8efe48a3 |

The public author used the contract without reading this implementation. The
three supplemental cases were authored after code inspection and are labelled
accordingly. The reviewer reused the earlier design-review context; this is
neither cross-model review nor a phase-gate review. All frozen input hashes
remained unchanged during each recorded execution. No established assertions,
locked tests, contracts or frozen support functions changed in repair1.

Original source68ea5ee9 remains in4727ee2b. The first failures and independent
review found two related defects: generic exception-context traversal could
replace the outward process error with a handled timeout, and stream-close
failure could lose known process flags. The narrow repair records the process
boundary and outcome before cleanup. Negative evidence remains in74bef500.

Tests use controlled subprocess substitutes and small /dev/shm fixtures; they
are not successful Arduino builds or uploads. F165/F166 separately record
file-only dependency and CLI-initialization prerequisite observations in
[selection](P7_static_cli_selection.md) and
[initialization](P7_static_cli_initialization.md).

Next: compose the minimal host launcher, reusing D153/D154 and the existing
packet. Bind reviewed source/HEAD, original D144 receipts, actual dependencies
and fresh initialization checks; size the final inline commands and review
the precise inert run before native execution. No new source tree or firmware
copy is needed. Current-image startup, live memory/WCET, physical acceptance
and human gates remain pending.
