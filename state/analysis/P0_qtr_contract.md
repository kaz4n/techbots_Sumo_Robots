# D-065: P0 bare-board QTR-style timing contract

This setup-only diagnostic implements P0 0.4 under D-051/D-052. It is not P2 HAL,
a wiring approval, a QTR sensor test or a resolution of SC-B/R4. Source basis:
P0_qtr_bare_contract_audit_20260923.md. Preserve every B16 value.

## Operations and bounded acquisition

- Default startup, MATCH0/MOTORS_ALLOWED0. Pins come only from config:
  P0_QTR_PINS={2,4,7,8}, compile-asserted against installed D2/D4/D7/D8.
  Read-only device readiness checks for GPIOA/B produce mask3 before any pin call.
  If either port is not ready, no acquisition/pin writes; complete remains0.
- No PWM, motor pins, Bridge/Serial begin, I2C, ADC, matrix, interrupt masking,
  delay/delayMicroseconds or heap use. All data collected in setup; loop is empty.
- Collect100 consecutive neutral INPUT samples, then100 separately labeled
  DIAGNOSTIC-ONLY INPUT_PULLUP samples. An early LOW in the latter is retained;
  it does not synthesize a timeout or prevent collecting remaining samples.
- Each sample first records two adjacent micros reads as overhead. Then capture
  total start; in pin order configure OUTPUT then write HIGH on each of four pins.
  Timestamp after the last HIGH: drive_us is elapsed since total start.
- Charge guard: repeatedly read micros, at most4096 calls, until elapsed is at
  least QTR_CHARGE_US+P0_QTR_QUANTIZATION_US (10+1=11us). This extra integer tick
  covers floor quantization of the installed1us clock; it is diagnostic margin,
  not changed B16 charge semantics or electrical proof. Keep charge_polls and
  charge_us. Clock elapsed >=2^31 is a CLOCK_FAULT; exhaustion is CHARGE_GUARD.
  Equality on the last allowed call satisfies the charge before guard exhaustion.
- After successful charge, configure each pin INPUT or INPUT_PULLUP in the same
  order. Timestamp after all four transitions. release_us includes that sequential
  release overhead; this timestamp is the observation epoch for the full1500us
  interval. Individual release skew is not measured and remains a limitation.
- Each observation pass performs four actual digitalRead calls in pin order,
  including pins already observed LOW. Timestamp after the whole pass. Every
  first LOW is assigned that end-of-pass elapsed time (shared timestamp/skew).
  Record a sticky low_mask and four first_low_us; unset is UINT32_MAX. This is
  sampled digital evidence, not analog discharge timing or continuous HIGH proof.
- Validate read results are exactly LOW/HIGH. A different result causes BAD_LEVEL;
  complete the four reads in that pass, timestamp, then stop and clean up. Clock
  faults take priority. For valid passes first record LOW observations, then test
  elapsed >=QTR_TIMEOUT_US: DEADLINE wins over all-LOW at an exact tie or overshoot.
  Its timeout_mask is 15 XOR low_mask. Thus a late first LOW is retained with its
  actual timestamp; a deadline outcome can legitimately have timeout_mask0.
  Otherwise low_mask15 ends with ALL_LOW. At most4096 passes; exhaustion is
  POLL_GUARD. A qualifying deadline/all-LOW on the last pass wins over exhaustion.
- Record observe_us at the final pass timestamp. No timeout cap is substituted
  for real elapsed time. All-high pull-up success requires DEADLINE, low_mask0,
  timeout_mask15, all first_low unset and observe_us>=1500; any early LOW fails
  stimulus qualification even if that sample eventually reaches the deadline.
- After every acquisition, including any post-configuration failure, attempt
  pinMode(INPUT) exactly once on every pin, no pulls. Timestamp after cleanup;
  cleanup_calls4 records attempts, not native return success. Floating readback
  cannot verify no-pull cleanup, so no LOW expectation is imposed. Retain total_us.
- Every elapsed subtraction is unsigned/wrap-safe. Any measured elapsed>=2^31
  (including overhead/drive/release/cleanup/total or record total) fails explicitly.
  Zero overhead/read intervals are valid quantization. A stopped clock hits the
  finite guards; these cannot bound a hypothetical non-returning GPIO/clock API.
- Store the whole sample before increasing completed. Any fault outcome ends
  setup after cleanup, preserving the failed sample; complete0. Normal ALL_LOW or
  DEADLINE continues. Set end_us and complete1 only after all200 samples and a
  valid record duration. Complete1 means acquisition finished, not stimulus valid.

## Frozen record and decoder

Public layout is qtr_capture.h:24-byte header and20072-byte samples =14424 bytes.
The passive decoder must require exact length/version1/ready3/complete1/completed200,
mode0 for first100/mode1 for last100, outcomes1/2, bounded elapsed/count fields,
cleanup_calls4, disjoint/complementary masks, first-LOW/mask agreement and timestamps
<=observe_us. ALL_LOW requires low_mask15, timeout_mask0 and observe_us<1500;
DEADLINE requires observe_us>=1500. charge_us>=11; charge/poll counts1..4096.
Normal total_us must equal drive+charge+release+observe+cleanup; record total must
cover all sample totals plus overheads and be <2^31. No overhead subtraction.
Reject pull-up stimulus failure explicitly while preserving the raw capture.

Report the two datasets separately: count, first sample, subsequent99 min/max/p99
(nearest rank) for intervals, all100 overhead statistics, all-low/deadline counts,
timeout masks and poll range. Expose neutral observations without imposing timeout.
Passive readout uses the existing hash-pinned helper, exact default loader/sketch
bytes/layout and two identical frozen records with repeated extension metadata.
Final artifact constants are filled only after target compile and independent
binary review. No MCU halt/reset/write to obtain records. Preserve debug-overlap
limitations. Upload only after fresh independent source review, exact binary
audit and inert-manifest approval. Match/Immediate remain upload-ineligible.

## Required independent validation

Derive tests from this file/header/config without reading the implementation.
Exercise exact call order, both labels, early/mixed/all timeout, four real reads
per pass, tie/overshoot/last-guard boundaries, wrap, clock halt/ambiguous intervals,
bad levels, failed readiness, cleanup on all post-configuration exits, publication
ordering/empty loop, incomplete/malformed records and separate stimulus failure.
Test script substitutes for compile-only/match/Immediate/changed source and both
SSH/ADB transports. Preserve existing locked tests. Host success and measured
bare-pad data are not sensor, pin-map, physical cleanup or complete-tick evidence.
