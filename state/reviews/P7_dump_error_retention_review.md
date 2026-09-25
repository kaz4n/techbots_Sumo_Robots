# D178 independent source and evidence review

2026-09-25T12:44:37+04:00. Result: **PASS for the narrow host Python repair**.
No open material findings. Separate same-model reviewer context; not a cross-model
review, human phase gate, hardware acceptance or motor-run authorization.

Reviewed the full repository AGENTS.md, current P7 resume lines, PLAN section 3,
P7 task 7.2, D090 receiver/frozen API, relevant D113 failure-precedence contract,
D178 contract at 2393bb0c, actual source and test diffs through 3f73fd58, original
and repaired execution receipts, and the documented fixture adjudication.
Reviewer changed only this review file and ran no test/build/device operation.

## Exact reviewed inputs

- Final source commit: 3f73fd5837fb3eccc8a000c28e7f3cabc9c0613e.
- tools/dump_match.py SHA256:
  `baca4d79a6d6cbc53944a17e36faa1bc42223aa8195d734f65c70b4df935a651`.
- tests/tooling/test_dump_error_retention.py SHA256:
  `5223b06aa42ad7107490367c3cee48d9d038ab5527aee2e0c4599a4fe4ee862e`.
- D178 contract SHA256:
  `d1161b19ebf4014d677a186832136f15cca1373e79534c13c78ca2987d5678df`.
- Final run receipt, state/analysis/P7_dump_error_retention_final.json SHA256:
  `83306e43d3c02eac8cd0db95f62871dfcac4552d7f6748b5f0552b112dfc4be2`.
- Legacy run receipt, state/analysis/P7_dump_error_retention_legacy.json SHA256:
  `fc69a8c071e988159e5fab7ecfaa9aed58da682d04133fdb1545c73e66571a31`.

These hashes were independently read from the current files and matched their
freeze/run receipts. Diff against 2393bb0c confirms no changes to the established
test_dump_match.py, test_dump_connection.py or tests/locked files.

## Source findings

The extraction into _retained_failure preserves existing primary-failure selection:
connection failures defer to a saved wire failure, then _receive_failure retains
its existing precedence. The final raise still chains from the originally caught
exception. connection_evidence retains the same actual stream evidence.

CaptureError adds only the two default-None public attributes. After partial
ownership, partial_path is its string path. One guarded error.json write retains
the old payload and writer; an Exception from that operation becomes exactly the
type/message evidence_write_error dictionary. KeyboardInterrupt/SystemExit are
not caught. The raised text starts with the original primary diagnostic, includes
the code and partial path, then clearly says the error report could not be saved
with the secondary type/message. No retry, alternate journal, cleanup, reopen,
rollback or publication is added. Success and pre-ownership paths are unchanged.
The helper remains bounded and below the repository's function-length guideline.
The README accurately describes the retained evidence and failed-save diagnostic.

Two first-repair findings were reported independently before closure:

1. The source prepended the error code before the preserved primary-message
   prefix. Fixed in 3f73fd58 by placing the code after that message; the original
   frozen assertion remains unchanged and passes.
2. The new serialization fixture patched json.dumps while the unchanged writer
   uses streaming json.dump. It did not inject its claimed failure. The narrowly
   adjudicated fixture correction intercepts json.dump for error.json, writes and
   flushes a fixed prefix, then raises the same TypeError. It keeps the substantive
   primary/cause/path/secondary/no-publication assertions and now proves exactly
   one journal open with exact retained partial bytes. This corrects an unsupported
   test assumption; production serialization was not changed to fit it.

Original oracle 90471804, original-source failures b11f8d6e, first-repair results
and adjudication 011b2394 remain available. No established assertion was weakened.

## Evidence and limits

Coordinator-run receipts, inspected rather than independently rerun by reviewer:

- Original source: 13 methods, 11 error records and one failure; cascading subtest
  errors are retained and are not treated as 11 distinct defective behaviors.
- First repair: 13 methods, 11 passed and the two findings above failed.
- Final corrected oracle: 13 passed, zero failures/errors/skips. Covers primary
  protocol/input errors, transport and metadata precedence, connection evidence,
  publication failure, journal open/serialization/partial-write failures,
  BaseException propagation, retained causes/bytes/path, CLI diagnostics and an
  actual successful synthetic offline capture.
- Selected unchanged Python regressions: 45 passed, zero failures/errors/skips;
  DumpParserTests, relevant DumpCaptureTests, and all 14 ConnectionHostTests.
  The unchanged C++ producer roundtrip and firmware configuration registry methods
  were explicitly omitted. This is not a whole-firmware regression claim.
- Ordinary error.json bytes match the original exactly, SHA256
  `92939b6164b5b5db8e96b668f63bf73001c17131381eba01702079b712a0d9e1`.

The new fixture guards prohibit actual network/process/device calls; live capture
branches use mocks. Receipts report native calls zero, all five final task pins
and eleven prior D177 pins unchanged, and no remaining new RAM test fixtures.
The reviewer performed no cleanup and did not access any prior denied target.
Synthetic exceptions do not establish actual full-disk behavior or hardware
origin. No target compile, transport change, firmware change, physical measurement,
human phase pass, deployment authority or fresh motor permission follows.

Next action: coordinator may record closure of this host defect and resume the
existing disconnected-board handoff. Hardware-dependent work retains its prior
conditions.
