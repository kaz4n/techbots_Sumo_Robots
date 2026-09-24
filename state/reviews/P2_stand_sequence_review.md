# D119 finite stand sequence review

Date: 2026-09-24 (Asia/Dubai). Reviewer: separate same-model context, read-only
for production and tests. Scope: pure sequence software and narrow read-only
validation of the coordinator's default/M0 compile-only receipt. This reviewer
performed no board/network action, target build or motor run. Integrated B4
behavior and phase gates are outside this review.

## Findings

No open BLOCKER, MAJOR or MINOR finding in this pure sequence software scope.

## Static review evidence

- Reviewed the complete AGENTS.md, current P2 progress and D119 decision, P2 B4
  requirements, B6/B16, public contract and the exact `bf2c4524^..bf2c4524`
  adoption diff. The local date is Thursday 24 September, the PLAN section 3
  sensor/bench preparation day; this review establishes no scheduled human gate.
- `src/core/stand_sequence.cpp:25` has exactly the twelve literal table rows.
  BRAKE and COAST are distinct states with zero nominal requests. Four DRIVE
  rows select left forward, left reverse, right forward, then right reverse.
- `src/core/stand_sequence.cpp:45` accepts start once and does not mutate on
  refusal. `:54` clears only the two pulses on unstarted, duplicate and terminal
  steps. The passive const report accessor adds no clock or I/O.
- `src/core/stand_sequence.cpp:61` preserves the specified priority: unsigned
  half-range clock admission, STOP, edge, duration-sized gap, then one row
  transition. A legal delayed transition anchors the next dwell at the actual
  observation, rather than shortening an interval or replaying skipped rows.
- `src/core/stand_sequence.cpp:13` rejects invalid duty/duration bounds at
  compile time. Arithmetic uses a 64-bit duration product. With continuing
  admitted distinct observations, each row lasts at least one duration and
  strictly less than two: the prior observation is before its boundary, and
  the next admitted delta is less than one duration. Twelve such intervals fit
  strictly inside the unsigned clock half range.
- `src/core/stand_sequence.cpp:94` zeros terminal requests and preserves the
  original reason/segment on subsequent calls. COMPLETE alone publishes row12.
  There is no loop, allocation, I/O, Arduino dependency, sensor synthesis,
  request injection, motor permission, or mutation of an actual Robot result.
- The adoption config diff adds only STAND_SEGMENT_MS=500 and STAND_DUTY=0.25.
  Existing values, motor default inhibition, locked tests, MotorGate, Robot,
  countdown, governor and application behavior are unchanged. The config
  registry gains exactly two additive literal expectations. Only the new helper
  and its tests refer to the new request-sequence API.

## Verification status

- The independent 18-case oracle originally froze as `65351127` at
  04:55:07+04:00 without implementation execution. Its unexecuted original is
  retained. The corrected oracle `5e03938c` froze at 04:56:28+04:00, before the
  reviewer probes. The complete original/amended diff and preservation receipt
  are retained under `state/analysis/P2_stand_sequence_raw/author/`.
- Inspected that amendment: twelve REQUIRE prerequisites became calls to a
  once-evaluated CHECK-plus-explicit-abort helper, with the required standard
  header. All literal expectations remain the same. The earlier multiargument
  CAPTURE concern applied only to an authoring draft; the original frozen oracle
  already had single-argument calls. No implementation failure drove the change.
- The public tests explicitly cover the literal rows, exact/adjacent timing,
  six-second nominal completion, delayed anchoring, bounded finiteness, gap and
  clock-order boundaries, wrap, all cancellation precedence, duplicate-input
  suppression, passive reports/terminals and refused restart.
- Reviewer `check_config_invariants.py` passed all twelve isolated copied-source
  profiles at 04:56:59-04:57:01+04:00. Nine invalid configurations failed with the
  intended static-assert diagnostics: duration0/89479/UINT32_MAX and
  duty0/negative/1/above1/NaN/infinity. Three valid profiles (1ms, the maximum
  allowed89478ms, and duty0.125) compiled and ran full twelve-row latest-legal
  delayed transitions, wrap, completion/passivity/refused restart and exact-gap
  rejection. See `state/analysis/P2_stand_sequence_raw/reviewer/config_invariants.json`
  and its exact compiler output/fixtures. No production or public-test file was
  edited by the reviewer.
- Reviewer evidence binds implementation SHA-256
  `8dfc2dcbdc74a01002ae117fd5649d0388bcf452d63a2ca5ab84990c6a899a94`,
  public header `3f01869c`, config `995a549b`. Current files still match.
- Inspected independent author normal and ASan+UBSan runs: each passed all18
  cases and246080 assertions, with zero failed/skipped tests and no sanitizer
  diagnostic. Exact pre/post hashes match the frozen oracle and first source.
- Inspected coordinator full normal and full ASan+UBSan receipts and actual
  LastTest logs. Each passed1496 main cases/50418546 assertions plus187 active
  MotorGate cases/4536952 assertions, with zero failed/skipped tests. Their
  pre/post source/config/oracle hashes are unchanged. Sanitizer flags and link
  command contain both address and undefined instrumentation. Full suites were
  run by the coordinator, not rerun by this reviewer. Evidence:
  `normal.json`, `normal.txt`, `normal_LastTest.log`, `sanitize.json`,
  `sanitize.txt`, `sanitize_LastTest.log`, `sanitizer_flags.make` and
  `sanitizer_link.txt`, all under
  `state/analysis/P2_stand_sequence_raw/coordinator/`.
- The config registry rerun passed both methods. The first failed invocation is
  retained: it imported the legacy registry under a second module name, leaving
  its evidence destination unpatched. The canonical import-path correction
  changed no source, expected value or assertion. Inspected both receipts and
  the two additive adoption expectations. The protected source/locked-test diff
  remains empty, and `git diff --check` reports no whitespace error.

## Narrow compile-only target check

D119's recorded validation extension permits this additional local receipt
review. `reviewer/check_target_receipt.py` passed at05:02:33+04:00. It rehashed
all20 archived receipt files, compared all93 current staged files with their
repository sources, and independently reproduced stage SHA-256 `62e38204`.
The fresh receipt `e72172eec9c649e7b785c42d7c570ad9` records a successful checked
default-startup, MATCH0/MOTORS_ALLOWED0 compile of `arduino:zephyr:unoq`.

Compared directly with D118's fresh receipt `10f17227`, the new loadable ELF
SHA-256 remains `8379f152`, the ZSK remains `c60443cd`, and the loader ELF remains
`39d4a4fd`; the full hashes are retained in
`state/analysis/P2_stand_sequence_raw/reviewer/target_receipt_review.json`.
The exact final current application bytes and resulting loading footprint are
unchanged. The retained low-memory compiler warning remains valid; the compiler
arithmetic is not stack-space evidence.

The completed build's object/compile-command receipt records the new
stand_sequence.cpp object at13244 bytes (`e2f14d7b`) with explicit M0/MATCH0
flags. Source staging includes this exact helper; the final identical loadables
show it contributes no retained application bytes while it remains unreferenced.
This supports the expected linker garbage-collection result. No target behavior
execution, loader/ABI re-audit or new MCU observation is claimed. The outer
compile-only argv, actual arduino-cli compile argv and read-only object-collection
receipt contain no upload operation.

Review completed after the software and target receipts were present on
2026-09-24 at05:02+04:00.

## Limits and next action

The helper is a nominal request planner. D119 explicitly leaves the real B4
Robot/Transaction profile, actual GO and source admission, electrical cap,
brake/coast enable handling, true Lifecycle STOP and MotorGate receipts for a
separate integration task. Its future integrated target fit and physical B4/B7
remain unqualified; this review verifies only the unchanged current default-app
footprint described above.
There is no watchdog or physical stop guarantee when software is not invoked.
Existing P3 DRIVE_TEST remains unavailable. No STAND OK, RING OK, motor authority,
hardware acceptance, upload permission or human phase gate follows.

## Verdict

PASS for the D119 pure sequence software and unchanged current default-app
footprint. No open material finding. This is a scoped review result, not B4/B7
acceptance, integration approval or a phase pass.
