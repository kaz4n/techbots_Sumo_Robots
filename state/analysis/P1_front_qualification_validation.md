# B9 centered qualification — 2026-09-22 Asia/Dubai

Status: HOST-TESTED; final scoped review is recorded below. Header c0b3ad6 precedes
source/tests. Worker owns fsm.cpp only; independent author owns new unlocked
test_front_qualification.cpp and report, reads specifications/public headers only.
Root owns shared headers/state/docs/build. Reused separate read-only reviewer
examines actual diff/tests; no full fresh phase-gate review is claimed.

The component counts NEW effective confirmed observations supplied by its caller.
It uses the B5 front table, resets on absent/off-center front and saturates at
ATTACK_ENTER_TICKS. Callers must reset on preemption and never resample stale
observations. It supplies eligibility only; no state, clock, contact or motor
permission. This deliberately leaves SC-AD entry anchor and SC-AE loss routing
for human decision before the complete Robot arbiter; see the contract audit.

Worker strict C++17 syntax and diff checks reported exit0. Root inspected the
14-line source addition: existing fsm behavior remains unchanged. No configuration,
hardware, established locked test or production safety assertion was changed.

Actual coordinator commands/results:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1;
  P1_front_qualification_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0;
  P1_front_qualification_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0;
  P1_front_qualification_sanitizer.txt, **497 cases / 11,920,333 assertions**,
  zero failures/skips and no ASan/UBSan diagnostics.

19 independent new unlocked cases cover256 masks,125 centered triples,
interruption/reset/threshold/saturation and actual Fusion/contact/governor
composition. The initially authored redundant generated case was removed before
any build; exhaustive table coverage remains. No test failure/repair attempt
occurred. Neither these tests nor the counter select SC-AD/AE policy or prove
the complete Robot/MotorGate path. No hardware action or human gate.

Final separate reused read-only review PASS/no open finding; independent host
run agrees with497/11920333. See ../reviews/P1_front_qualification_codex.md for
scope and exact reviewed23-file hashes. After manifest refresh, controlled
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` passed48/48,
exit0 (P1_front_qualification_tools.txt). Implementation1950635; contractc0b3ad6.
Next eligible task: B14 statistics from supplied tick durations, per the audit.
