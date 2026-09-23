# D096 runtime failures and disposition

2026-09-23 Asia/Dubai. Preserve original receipts; no established/locked test
was changed. New test fixtures are independently authored from public contracts.

## Actual implementation findings

- The first decision-time projection encoded a regressing outer clock as a
  LINE_CONTRACT input, manufacturing a Robot stopping decision. The independent
  reviewer reconstructed that historical path in a labeled isolated copy.
  Optional pure DecisionSource.clockAccepted now rejects before Robot/Gate.apply/
  recorder.consume; actual current-source regression passes.
- Gate A was absent from Runtime clock chronology; C was checked only after
  completion publication. Actual original-source reviewer receipts demonstrate
  a regressing display clock being accepted, and a regressing C retaining
  finished/timing_valid. Admit real A before postwork; finishAfter validates the
  last actual outer observation before completion publication. Independent
  adversarial-clock regression passes in both motor configurations.
- CONTROL stopped pumping at a retained QTR lower bound on every subsequent
  epoch, starving real discharge completion. Advance each active source at least
  once each due epoch, then apply the existing early-exit rules. No sample time,
  color, timeout or source budget is invented. Author and reviewer regressions
  exercise the later genuine completion.

## Target blocker

The first actual app build exited1:276368 bytes required versus262144 available,
excess14224. Its compiler output and exact command are retained in
P2_app_runtime_raw/target_compile_01.json/.txt. Linked cache ELF evidence is
target_fe65a3ad_bench-default.json, explicitly failed_compile_cache=true. These
objects do not establish an accepted target build. A second build checks corrected
final source, not a second attempted RAM remedy. No buffer/capacity reduction,
new upload, toolchain alteration or fabricated success is used.

Keep RAM resolution as the next bounded software task. This is a real open review
BLOCKER for target delivery, not a reason to discard independently tested source.

## Harness and compile corrections

The worker's original strict compile rejected a signed/unsigned opponent-status
comparison; explicit int32 conversion corrected it without changing accepted bits.
The original overloaded decide made legacy decide({}) ambiguous; distinct
decideFrom preserves established source compatibility and has a new regression.
Author and reviewer harness failures, their exact causes and subsequent receipts
are retained in their raw directories/reports. Synthetic native reports must meet
the actual public ADC voltage formula, QTR interval consistency and button gap
contracts; changing those fixtures must not weaken threshold expectations.

Root full CMake normal and sanitizer builds initially failed only because the new
fixture included fixtures/qtr_cal_fixture.h from within tests/fixtures. The
standalone author harness had an extra tests include path. Fix the new fixture to
use same-directory qtr_cal_fixture.h; preserve host_normal_final and
host_sanitized_final exit2 receipts, and rerun under distinct receipt names.
No existing test/assertion or global include-path workaround is changed.

Final corrected-source compile4cb637f9 also exits1:211444program276456memory,
excess14312B. This is the authoritative final D096 size; the earlier14224B result
belongs only to fe65a3ad. Exact82-file staged/remote/source audit and3 cache ELFs
pass identity checks with target_compile_accepted=false; target acceptance fails.
