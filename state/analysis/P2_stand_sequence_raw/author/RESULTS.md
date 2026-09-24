# Independent D119 contract oracle

The independent author read the public contract, public header and relevant
configuration, but did not inspect `src/core/stand_sequence.cpp`. Literal
expectations were frozen before any execution against the implementation.

## Freeze and bounded harness correction

- Initial freeze: `oracle_freeze.json`, 2026-09-24T04:55:07.3657984+04:00,
  SHA256 `65351127a46b2280b76a57acdc448d87863130ab74282a2739399ff08988c1c1`.
- Before first compilation/execution, review identified the installed doctest
  `REQUIRE` restriction under the existing no-exception build flags. The installed
  optional ALL_ASSERTS mode would not retain fatal behavior because its
  no-exception `throwException()` is empty.
- The single harness amendment adds `requireCondition`, which records a CHECK
  and explicitly aborts on failure. All 12 original REQUIRE expressions are
  evaluated once with their exact original conditions. All 49 original CHECK
  expressions remain, with one additional helper CHECK. The complete literal
  transformation was verified in `assertion_preservation.json`.
- Every CAPTURE was already single-argument in the original frozen source; a
  review observation of multi-argument CAPTURE referred to the earlier authoring
  draft and did not require a post-freeze change.
- Amended freeze: `oracle_amended_freeze.json`,
  2026-09-24T04:56:28.6521438+04:00, SHA256
  `5e03938c09337d2dc6ce419b1030ef0e7b9d75f110df858219814cce3122c026`.
- Original and amended source copies, the literal harness diff and both freeze
  manifests remain preserved. Neither oracle was executed before its freeze.

## First isolated execution

Authorized first runs completed from 04:57:23 to 04:57:47 +04 on 2026-09-24.
Both used GCC 13.3.0 in WSL Ubuntu, C++17, strict warnings as errors,
`-fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS`.

| Build | Cases | Assertions | Compile status | Run status |
|---|---:|---:|---:|---:|
| Normal, O0 | 18 passed | 246080 passed | 0 | 0 |
| ASan+UBSan, O1, debug, frame pointers | 18 passed | 246080 passed | 0 | 0 |

ASan leak detection and halt-on-error were enabled; UBSan halt-on-error was
enabled. No sanitizer finding occurred. Both build output files are empty.
Commands, exact compiler flags, source/binary hashes, timestamps and statuses are
in `run_isolated.sh`, `first_execution.log`, and `execution_status.txt`.
Binaries were built in `/dev/shm/d119-author-oTtm3s`, away from the low-space
Windows volume. No source/expectation changes followed execution.

Implementation SHA256 before and after both runs:
`8dfc2dcbdc74a01002ae117fd5649d0388bcf452d63a2ca5ab84990c6a899a94`.

The tests cover the literal twelve-row table, all rows' adjacent/exact/delayed
boundaries, nominal six-second completion, bounded delayed completion, unsigned
wrap, gap/half-range/backward boundaries, STOP/edge/clock precedence, duplicate
suppression, one-shot start and terminal immutability. These are pure software
results. Full-suite checks are owned by the parent; no target build, upload,
motor run, electrical validation, integration acceptance or human gate follows.
