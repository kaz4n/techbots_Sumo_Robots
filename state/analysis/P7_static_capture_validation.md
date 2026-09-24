# D152 pure static capture validation

IMPLEMENTED / HOST-TESTED / scoped review PASS, 25 September 2026 Dubai.
This prepares observation of the current inert static packet; no MCU operation
or production static admission occurred.

- Contract58959d7c, sourceb7ab979d, frozen independent testsbcb63005.
- First implementation execution: Python3.13 `-B`,37 methods PASS in0.206s,
  exit0. No source fix or test amendment. Full argv/output/status/times are in
  [host_first.json](P7_static_startup_raw/host_first.json), with prior
  [freeze](P7_static_startup_raw/host_freeze.json) and author provenance.
- Exact18-read/713656-byte plan, strict input types/order/extents, all flash
  mismatch combinations, prefix fields/enums/flags, error/fault precedence,
  counter wrap/half-range and input/result independence are exercised in memory.
- [Fresh-context same-model code review](../reviews/P7_static_capture_review.md)
  cdae7896 reports no open findings. No redundant rerun or new private suite.
- Local checks revalidated17 frozen dependencies,103 source/102 staged files,
  sourcefcddbd8e, unchanged src/tools/host/tests from82b34f4a and original
  PROGRESS prefix. [Receipt](P7_static_startup_raw/local_checks.json), zero board calls.

The original contract's caller-reference prose incorrectly identified the
packaged loader BIN as the flash reference. Original prose and design PASS are
preserved in6d45e3b5. The [separate reference review](../reviews/P7_static_capture_reference_review.md)
53cb6ee7 records the MAJOR defect and correction: the checked ELF39d4a4fd yields
263680 bytes/SHAe9322826; packagedBIN6b2ffd differs at offset260287. Both retained
historical D118 loader brackets agree with the ELF-derived image. Commit8fa01d1f
corrects caller provenance without changing pure semantics or frozen tests.

The parser accepts supplied bytes; it does not establish their origin, simultaneous
sampling, absence of resets, sensor readiness, physical outputs, live memory,
stack/WCET or any gate. The next task is a reviewed one-shot upload/capture
composition using the existing packet and [verified route](P7_static_upload_route.md).
[Guard options](P7_static_startup_guard_options.md) are advisory, not an execution
grant. Use ELF-derived loader bytes as corrected here. No new binary or build is needed.
