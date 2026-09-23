# D085 independent test author handoff

Objective: derive native acquisition, raw qualification and controller-freshness
tests from the frozen contract/public headers, then compile actual production
sources without reading their implementation bodies. Completed locally; no board
operation, transport, upload, physical run or phase acceptance was performed.

Owned additions: `tests/native_qtr/**`, `tests/tooling/test_qtr_native.py`,
`tests/test_qtr_adapter.cpp`, `tests/test_qtr_integration.cpp`, and this `author/`
receipt directory. No established test, production source, configuration, build
file, gate, shared decision or progress ledger was edited by the test author.

## Results

- Full tooling run: all 11 methods passed, 121.529 seconds.
- Pure adapter/Robot: 22 cases, 26,881 assertions, both ordinary and ASan/UBSan.
- After the reviewer found the repository-specific no-exceptions assertion mode,
  focused ordinary/sanitized/confirmation-three rerun passed all three methods in
  43.456 seconds. The 22-case suite retained all 26,881 assertions in both modes.
- Native lifecycle/acquisition: 14 cases, 834 parent assertions plus 1,098
  successful isolated-child assertions, UBSan.
- Native boundaries/fault cleanup: 10 cases, 918 parent assertions plus 25,637
  successful isolated-child assertions, UBSan.
- Actual native -> adapter -> Robot: three cases, 108 parent assertions plus 497
  successful isolated-child assertions. Includes all 16 raw patterns, a second
  acquired frame with continuing opponent debounce, an ambiguous 600us read gap,
  and allocation guards across three acquisitions plus 10,000 replay transactions.
- Eleven invalid configuration variants and 21 initial metadata variants passed.
  The added valid-but-unknown foreign-device variant was run separately after the
  full runner had already loaded: one case/four assertions passed. The current
  runner includes this 22nd metadata variant in its standard method.
- Confirmation-count-three variant passed distinct/replayed-frame and expired
  BOOT-history scenarios.
- Both MATCH/MOTORS_ALLOWED macro modes: actual compile-probe constructors,
  setup and 10,000 loops remain inert; one case/19 assertions each.
- All eight transport/match/startup upload combinations were refused before
  target, remote or transport lookup. Per-combination refusal receipts are saved.
- Deliberately failing child-assertion and child-signal sentinels returned expected
  failures and proved parent propagation. Child counts are separately reported;
  they must not be confused with doctest's parent-only count.

## Preserved first failures and repairs

Every compiler/runtime command saves its exit and streams before raising. The
nonzero-command index is in `final_test_manifest.json`; sentinel failures are
labeled expected. Initial failures were retained rather than overwritten:

1. Fixture extraction lost a conditional around two EXTI constants; preserve the
   installed conditional. An independent fixture indentation warning was split.
2. A doctest bitwise expression required explicit parentheses/comparison.
3. The native worker added exact GPIOC exclusion binding while metadata builds
   were running; add the installed-shaped GPIOC binding and required adapter/core
   source linkage to the widened inert probe. Earlier failed builds remain.
4. New pure test files needed `<initializer_list>`.
5. A final-guard-delay scenario accidentally invoked begin twice; repair its
   setup sequence, retaining the exact deadline-failure assertion.
6. A countdown-window scenario violated the 2000us source-start spacing; move
   its prior valid frame earlier, retaining the source-window expectations.
7. A fresh review standard-host build rejected five new `REQUIRE` sites because
   the established build uses `DOCTEST_CONFIG_NO_EXCEPTIONS`. Preserve the identical
   predicates with `CHECK` plus explicit safe early returns, and compile pure
   focused tests using that exact mode. The original build receipt was copied
   byte-for-byte to `first_standard_host_require_failure.txt`.

The target build's Arduino `bit(b)` collision was identified outside this author
run. The fixture now retains that installed macro; the worker's renamed helper
passes the updated native suite. Source hashes distinguish all intermediate
implementations; early success is not silently attributed to a later source.

## Evidence limits and next action

`final_test_manifest.json` hashes the final test files. Command receipts include
staged source hashes; production bodies were handled opaquely. Installed header
extraction and GPIO semantics are documented in `tests/native_qtr/README.md`.
Generation wrap uses an explicitly authorized test-only seed after an ordinary
completed frame; it does not claim billions of observed acquisitions.

Controlled headers establish software behavior under the declared model. They do
not establish actual pad handoff/debugger absence, electrical levels/discharge,
sensor color separation, hardware cadence/service precision, native call latency,
cleanup voltage, complete-tick WCET, SC-AJ/F091 closure or a human gate.

Next action belongs to root/fresh reviewer: finish the standard full-host and
sanitizer regressions, actual inert target build/source/import/startup verification,
and frozen-source review; record final shared evidence and limitations.
