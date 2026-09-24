# D153 passive collector validation

IMPLEMENTED / HOST-TESTED / scoped review PASS, 25 September 2026 Dubai.
No MCU read, upload, reset, compiler or production-source change.

Current [contract](P7_static_capture_remote_contract.md)0371739e and fixed
[bindings](P7_static_startup_raw/capture_bindings.json)c2c87df6 define the existing
packet's18-read/713656-byte collection. Source1aa602d0 in5f85268f enforces exclusive
durable ownership, exact process arguments, reference checks before RAM sampling,
deadlines/process-group cleanup and independent failure finalization.

| Validation | Actual result | Evidence |
|---|---|---|
| Independent spec-derived suite | 46 methods PASS,2.569s,exit0, first run | [Freeze](P7_static_startup_raw/remote_freeze.json), [receipt](P7_static_startup_raw/remote_first.json) |
| Reviewer supplemental boundaries | 4 methods PASS,0.153s,exit0, first run | [Freeze](P7_static_startup_raw/remote_private_freeze.json), [receipt](P7_static_startup_raw/remote_private_first.json) |
| Separate fresh-context same-model review | PASS; no open findings | [Review](../reviews/P7_static_capture_remote_review.md)eed7414d |

All frozen inputs stayed unchanged. The additional cases cover the4096/4097
process-entry boundary, immediate pre-launch timeout reduction and primary-error
preservation through context cleanup. They were authored after source inspection
and are not represented as spec-only independent tests. Both suites use WSL
Python-B with small controlled /dev/shm fixtures and process substitutes. Final
fixture check found zero remaining sumox_capture_contract_* directories.

Original unexecuted sourceb099e4d9 is preserved ind5c8d6d6. Inspection found a stale
default-wrapper timeout before stream setup and possible primary-error loss at
context exit; coordinator also required clock-failure receipt retention. These
were repaired before test freeze/first execution, without changing an established
oracle. Draft test clarifications followed the contract before their freeze.

Independent safe preparation also verified explicitly empty CLI configuration:
[route refinement](P7_static_upload_route.md) and F162 retain both the initial
incorrect top-level projection and corrected nested data/user directories.
Three read-only CLI queries exited0; they did not upload or touch the MCU.

The existing board-side p0_capture.py is18880B/SHA885c4e42, newly file-verified in
[installed_loader_helper.json](P7_static_startup_raw/installed_loader_helper.json).
Reusing its hash-checked loader_image avoids another installed copy. A local
[payload sizing estimate](P7_static_startup_raw/transport_sizing.json) leaves7058
UTF16 command units under the30000 ceiling; it is not the final bootstrap or a
transport test. Exact source bytes and real bootstrap length must be checked in
the next task. The initial full-module sizing prototype exceeded that ceiling;
no payload file or board command was created for either estimate.

Next: implement/test/review the host coordinator and one-shot upload wrapper,
binding current source/HEAD, D144 objects, installed tools, isolated CLI config
and exact selected core/recipe. Reuse the reviewed collector and existing packet;
then separately record/run the precise inert upload and conditional capture.
The collector alone is no native grant, source provenance, live startup evidence,
kernel-exclusive lock, quiescence proof, free-memory/WCET measurement or gate.
