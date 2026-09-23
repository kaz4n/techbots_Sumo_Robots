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

### 2026-09-22 | P1 B8/B11 existing sweep and recency | no physical tuning
- Centralize SEARCH_SCAN_DEG=360 and RECENT_EDGE_MS=5000 from existing B8/B11
  text. D-041/D-042 define side memory and loss fallback; no B16 value/pin changes.
- Evidence: B8/B11, accepted decisions, exact config-source checks; independent
  SEARCH boundary tests follow. Neither angle nor duration has physical evidence.

### 2026-09-22 | P0 bare UNO Q scheduler measurement | no tuning change
- Actual target: USB2629958581, user-reported bare board, CLI1.5.1/core1.0.0;
  source3de6da69, default/dynamic, MATCH0/MOTORS_ALLOWED0. No sensor or motor.
- Result:60000 completed samples; maximum and nearest-rank p99 lateness3us;
  zero observations at least1000us late. Bins0/1/2/3us:16561/16683/16603/10153.
- Exact loader and sketch flash verified, final-ELF/runtime BSS checked, two
  identical4016-byte snapshots plus before/after60000 sample counters. First
  debug attachment was over248s after upload; frozen run2 readout exit0.
- Evidence: analysis/P0_timing_capture_run2_20260922.json, P0_timing_run2_raw/,
  P0_capture_run2_invocation_20260922.txt and P0_capture_validation_20260922.md.
  Run1 reference-format failure is retained separately, not counted as a pass.
- Scope: bare scheduler lateness including installed yield/mutex loop hook;
  not complete control-tick WCET, pin/API timings, startup or ring evidence.
  No config value or pin changed; M1-M13 remain unmeasured.

### 2026-09-22 | P0 bare UNO Q matrix progress | no tuning change
- Inert source72214f8a/default/MOTORS_ALLOWED0 uploaded23:34:33+04 to USB2629958581.
- Actual p0Seconds counter441 then444; requested3s wait, read-to-read time bounds
  3.000219..3.078029s. Full loader/sketch comparison and before/after runtime
  mapping checks passed; capture exit0 in104.838s.
- Evidence: analysis/P0_matrix_capture_20260922.json and P0_matrix_run1_raw/.
  This shows software progress through the matrix workload, not optical
  correctness, precise clock rate, loaded tick timing or Monitor round trip.
- No config/pin change, additional hardware or motor operation; no phase gate.

### 2026-09-23 | P1 B13 menu constant centralization | no measured tuning
- Added MODE_SHORT_MS=600 to config.h, copying the existing strict short-press threshold in BEHAVIOR B13 under D-058. All original B16 defaults are unchanged. Evidence: P1_mode_menu_contract_audit.md and P1_menu_contract.md; exact/adjacent-threshold host tests follow the committed interface. No physical measurement, pin assignment or motor operation.

### 2026-09-23 | P0 counter transport | diagnostic settings, no strategy tuning
- D-062 adds P0_MONITOR_TIMEOUT_US=100000 as an explicit diagnostic development
  timeout, not a measured safe control-loop duration. P0_MONITOR_BAUD_BPS=115200
  validates the installed internal UART/router configuration; it never changes
  that link. Original76 B16 values, pins, gains and motor limits are unchanged.
- Evidence: P0_counter_transport_contract.md; installed UART/router receipts;
  independent25 packet cases/39 adapter cases, ASan/UBSan and156 full tool checks.
- Inert source75ab5a22/default/MOTORS_ALLOWED0 uploaded01:55:51+04. Actual logger
  received4..11 and56..63 in two8-second windows, with no input bytes sent. This
  measures delivery, not IRQ timing, precise1Hz accuracy, optical output or WCET.
- Exact receipts and limitations: analysis/P0_counter_validation.md. Linux stayed
  running; another Monitor client existed. No physical fault injection or motor
  operation, no additional hardware request, and no human phase gate.

### 2026-09-23 | P0 A0 startup timing | diagnostic only, no strategy tuning
- D-063 config adds P0_ADC_SAMPLES=1000 and P0_ADC_PIN=14, checked against the
  installed named A0. This selects the existing ADC-only input for a bare-board
  diagnostic, not a robot pin-map approval; all76 B16 defaults remain unchanged.
- Actual sourcef5f637b2/revision9de8cd1/default/MOTORS_ALLOWED0 uploaded02:16:28+04.
 1000 complete raw API calls: first276us;999 subsequent calls139..140us/p99140us;
 paired micros overhead1..2us/p992us, unsubtracted; total144116us. Raw codes124..306.
- Full deployed-image identity and two frozen RAM records verified. Evidence:
  analysis/P0_adc_validation.md and linked raw receipts, reviewP0_adc_codex.md.
  These are empirical setup costs, not an ADC deadline or voltage calibration.
  Source proves indefinite waits; debug overlap is not independently excluded.
  No motor, new external component, electrical approval or phase gate follows.

### 2026-09-23 | P0 builtin LED GPIO timing | diagnostic only
- D-064 adds P0_GPIO_SAMPLES=400 and P0_GPIO_PIN=50, compile-checked against
  installed LED_BUILTIN/LED3_R. No robot pin-map or76 B16 default change.
- Actual revisiona98bcf6/source1dfbd571/default/MOTORS_ALLOWED0 uploaded02:36:15+04.
 400 cycles matched LOW/HIGH/HIGH and final HIGH. First mode/write/read-low/
 read-high/pair4/2/2/2/3us; subsequent399 mode2..11/p993us, write/reads1..2/p992us,
 pair2..3/p993us. Clock overhead1..2/p992us unsubtracted; full interval8347us.
- Exact image and frozen RAM verified;111.053s passive readout, source/binary/
  receipt review and raw evidence in analysis/P0_gpio_validation.md.71.022s
  same-host quiet interval; possible debug overlap remains. No optical proof,
  recovered native error codes, header-pin timing or full-robot WCET claim.
  No additional external hardware, motor operation or human gate.

## 2026-09-23 — D-065 diagnostic-only configuration
Added P0_QTR_SAMPLES_PER_MODE100, P0_QTR_GUARD_POLLS4096,
P0_QTR_PINS{2,4,7,8} and P0_QTR_QUANTIZATION_US1. These bound the setup-only
bare-board experiment; B16 QTR_CHARGE_US10/TIMEOUT_US1500 are unchanged.
Source/ownership evidence: P0_qtr_bare_contract_audit_20260923.md. No physical
measurement, production pin assignment, tuning result or wiring approval yet.

## 2026-09-23 — D-065 actual bare-board QTR-style measurement
Firmware dcca300/source61d7a2d0, default/MOTORS_ALLOWED0 uploaded03:00:13.327+04.
No B16 value changed. Neutral100 and diagnostic pull-up100 acquisitions all ended
DEADLINE with mask15 and no observed LOW;100% stimulus qualification. Charge11..12us,
cleanup attempts4 each. Neutral first1535us/subsequent1531..1536us/p991536us;
pull-up first1534us/subsequent1530..1536us/p991536us. Micros overhead1..2us retained.
Source/binary/host review and actual raw-image/record review PASS; no tuning adopted.
Evidence P0_qtr_validation.md, P0_qtr_run1_raw/, P0_qtr_codex.md. These empirical
setup-only data exceed the tick budget; SC-B remains unresolved. Not real sensor
or calibrated electrical/physical-cleanup/WCET proof; debug overlap unexcluded.


## 2026-09-23 - D-069 offline storage capacity, no physical tuning
Added LOG_FRAME_WINDOW_MS200000 from B15 and derived LOG_FRAME_CAPACITY10001
at unchanged LOG_HZ50. All76 B16 values remain. Actual host ABI sizeof objects
292848B; payload292794B exceeds installed262144-byte LLEXT pool before app.
Evidence P2_frame_host_size_20260923.json/P2_frame_buffer_validation.md. No MCU
allocation/free RAM, ring measurement, rate change or target-fit claim.

## 2026-09-23 - D-071 isolated rate experiment, no production tuning
Production LOG_HZ50 and all76 B16 values unchanged. Candidate copies alone use25Hz
with5001 endpoints/200s; target owner162952B, image RAM226584B. Repaired50Hz
baseline356608B fails262144B size limit;25Hz passes. This is target compilation,
not a physical run/free-RAM/recording measurement. P2_memory_compile_validation.md
and raw provenance retain all source differences, commands, failures and hashes.
Conditional pristine loader peak230072B is analysis only. Rate adoption remains
separate; no full-HAL, loadability,200s/dump/WCET, wiring or gate claim.


## 2026-09-23 - D-072 specified low-memory fallback adoption
Production LOG_HZ50->25 is the only changed B16 value, under D-051/D-072.
B15 already permits25Hz when RAM is short. Actual50Hz probe356608B exceeds
262144B; actual current25Hz probe226584B exits0 and matches D-071 candidate ELF.
5001frame endpoints/40ms cadence;200s window,4096events and1kHz control unchanged.
Evidence: P2_rate_adoption_validation.md/raw, F-092 and fresh same-model review.
975hostcases/15667813assertions normal+ASanUBSan and340controlledtools pass.
This is an evidence-backed development default, not ring tuning or measured
free RAM. Load/fullHAL/200s/no-gap dump/WCET and original human gates remain.
No core/HAL body, locked test, motion/sensor parameter, upload or MCU action.


2026-09-23 - D076 software pin naming only
Added config::OPP_INPUT_PINS[7]={11,12,13,16,17,18,19} from the unchanged
HARDWARE3 proposals. All76B16 values retained; no tuning, wire change or physical
measurement. Installed mapping is source-verified in F094/P2_opp_gpio_audit.md;
actual native driver host/target evidence in P2_opponent_validation.md. PINMAP
approval, electrical readings and B1 range/false-hit acceptance remain pending.


2026-09-23 - D077 native motor development defaults
Names unchanged HARDWARE3 proposals MOTOR_PWM_PINS={3,5,6,9}, MOTOR_ENABLE_PIN10.
New MOTOR_PWM_HZ10000, MOTOR_PWM_SETTLE_US150, MOTOR_PWM_SETTLE_MAX_POLLS4096
selected under D051/D075/D077. No B16 value changed and no measurement/tuning
claim: source-derived carrier periods3200/250/3200/3200 still need setup rate
validation; complete tick/WCET/physicalwaveforms remain pending. Primary manual/
errata and installedclock evidence in P2_motor_update_audit.md/P2_motor_clock_audit.md.
No wiring approval, upload, motor run or human gate.


2026-09-23 - D078 native battery development constants
Added VBAT_INPUT_PIN14 (unchanged A0 proposal), nominal VBAT_ADC_REFERENCE_V3.3
and VBAT_DIVIDER_RATIO122/22. New VBAT_ADC_REGULATOR_US100,
VBAT_ADC_CALIBRATION_US5000, VBAT_ADC_POST_CAL_US2 (minimum spacing),
VBAT_ADC_ENABLE_US100, VBAT_ADC_CONVERSION_US100, VBAT_ADC_SHUTDOWN_US100,
VBAT_ADC_SETUP_MAX_POLLS65536 and VBAT_ADC_READ_MAX_POLLS4096. No B16 changes.
Source timing basis: P2_adc_limits.md; acquisition/ownership/errata reports and
P2_power_contract.md distinguish software deadlines from physical bounds.
These are development fail-closed selections under D051/D075/D078, not tuning
measurements, divider calibration, wiring approval or runtime/WCET acceptance.
