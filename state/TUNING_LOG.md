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

### 2026-09-22 | P1 B4.2/D-021 forward demand | no physical tuning
- Setup: host only, no board or measured battery.
- Change: add EDGE_FWD_INNER_RATIO=0.70 from B4.2's existing 70% inner-wheel
  request. D-021 approves reusing unchanged EDGE_BACK_DUTY=0.80 as the forward
  base and final cap. All 76 B16 defaults remain unchanged; no pin assignment.
- Evidence: human D-021; exact-value config test and independent forward-demand
  governor tests. Actual trajectory/ratio after compensation and cap saturation
  is not a physical measurement. M1-M13 remain unmeasured.

### 2026-09-22 | P1 B3/D-024 service constants | no physical tuning
- Add CAL_START_MS=1500, CAL_END_MS=4500, COUNTDOWN_LINE_WARN_MS=1000,
  COUNTDOWN_SNAPSHOT_MS=300 from B3 text; CAL_MIN_SAMPLES=2 is explicitly
  approved in D-024. Preserve all 76 B16 values and all pins (still unassigned).
- D-022 reuses the existing gain/correction cap and D-023 removes undefined
  second compensation without changing a config value. No measurement inferred.
- Evidence: user decisions D-022 through D-024, new exact config source checks,
  independent locked service tests to follow. M1-M13 remain unmeasured.

### 2026-09-22 | P1 B11.3 rolling window | no physical tuning
- Add REFLANK_WINDOW_MS=10000 from B11.3's existing ten-second limit, centralized
  under R9. Preserve all 76 B16 defaults and existing REFLANK_MAX_PER_10S=2,
  ALL_IN_MS=1500. No pin, wiring, duty limit or motion authorization changes.
- Evidence: B11.3/D-025, explicit exact-value config check and independent limiter
  tests to follow. Host time arithmetic only; M1-M13 remain unmeasured.

### 2026-09-22 | P1 B15/D-028 event capacity | no physical tuning
- Add LOG_EVENT_CAPACITY=4096 from the existing B15 capacity and accepted D-028.
  Keep all 76 B16 defaults unchanged. This centralizes fixed event storage under
  R9; it does not alter frame frequency or claim target RAM/latency validation.
- Evidence: D-028, exact config source check and independent first-event retention
  tests to follow. HAL recorder ownership, frames and idle dump remain later work.

### 2026-09-22 | P1 B4.2 side-row angle | no physical tuning
- Add EDGE_SIDE_TURN_DEG=45 from the existing B4.2 side-row/B4.3 text, centralized
  under R9. No B16 value, pin, voltage, acquisition or wiring assumption changes.
- Evidence: BEHAVIOR B4.2/B4.3, exact config-source check and independent row
  executor tests to follow. This is not a measured or tuned escape angle.

### 2026-09-22 | P1 B14 overrun warning threshold | no physical tuning
- Add TICK_OVERRUN_PERCENT=1 from B14's existing more-than1% warning, centralized
  under R9. All76 B16 defaults and pins remain unchanged. No motor/fault reaction
  or measurement is inferred. Strict duration overrun remains duration>TICK_US.
- Evidence: B14 text, exact config-source assertion; independent statistics
  boundary tests follow. R4 target WCET<800us still needs actual robot evidence.
