# TUNING_LOG (append only)

Every bench or ring measurement and every config.h change goes here with its evidence.

## Entry format
### <date> <time> | <phase> <test id> | battery <V>
- Setup: surface, box weight, mode, firmware commit
- Runs: N, results (numbers, pass/fail per run)
- Log files: logs/...
- Change: CONSTANT old -> new (reason, evidence) or "none"
- Metric status: M# pass/fail

## Metrics board (update as results arrive)
| Metric | Target | Result | Date | Evidence |
|---|---|---|---|---|
| M1 early starts | 0 in 50 | | | |
| M2 self-exits solo | 0 in 20 | | | |
| M3 edge escapes | 24/24 | | | |
| M4 acquire | 9/10 | | | |
| M5 push-out | 8/10 | | | |
| M6 lost target | 10/10 | | | |
| M7 spectators | 0 in 20 | | | |
| M8 re-flank | 8/10 | | | |
| M9 sidestep vs charger | 8/10 | | | |
| M10 tick worst case | < 800 us | | | |
| M11 brownout resets | 0 in 20 | | | |
| M12 weight | 2,950 g +/- 20 | | | |
| M13 footprint | 199 x 199 mm | | | |

### 2026-09-22 | P0 0.3 software configuration initialization
- Setup: host only; no board, battery, bench or ring measurement.
- Change: created src/config.h with all 77 B16 constants unchanged. No pin values assigned.
- Added diagnostic-only defaults: P0_SCROLL_MS=100, P0_COUNTER_MS=1000,
  P0_JITTER_SAMPLES=60000, P0_JITTER_HISTOGRAM_US=1000. These parameterize P0
  display/capture scaffolds and do not alter robot behavior or safety timing.
- Evidence: comparison script reported all 77 B16 values exactly equal; C++17
  host build/CTest passed (analysis/P0_host_tests.txt). P0 smoke test only.
- Metric status: M1-M13 unmeasured; no tuning or physical performance claimed.

### 2026-09-22 | P0 recovery | scaffold correction, no physical tuning
- Setup: WSL host and synthetic clocks only; no board or battery.
- Correction to the previous initialization entry: B16 has **76**, not 77,
  constants. The old extraction also imported `FC = 0` from the B5 bearing table.
  Removed that extraneous declaration; all 76 B16 names, values and types remain
  unchanged. The four explicitly documented P0 diagnostic values also remain unchanged.
- Evidence: independent B16-scoped checks and real-sketch synthetic runtime
  tests in tests/tooling/test_p0_*.py; state/analysis/P0_scaffold_audit.md.
- Corrected the matrix RAM seconds accumulator to preserve elapsed whole seconds
  after delayed calls; no duty, timing threshold, pin, or wiring value changed.
- Metric status: M1-M13 remain unmeasured; source/host checks do not satisfy them.

### 2026-09-22 | P1 B6 implementation | no physical tuning
- Setup: host only, board disconnected; no measured battery value.
- Change: add VBAT_FILTER_MS=1000 from B6's existing "1 s time constant" rule
  (not listed in B16). All 76 B16 defaults remain unchanged. No pin assignment.
- Reason: centralize this specified filter constant under R9 while implementing
  the explicitly approved D-017 governor ordering. The config contract test adds
  a named exact-value check rather than allowing arbitrary additional tunables.
- Evidence: docs/BEHAVIOR.md B6; independent governor tests and host results to be
  recorded in P1_core_tests evidence. M1-M13 remain unmeasured.
