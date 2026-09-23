# D077 native MotorGate interim implementation review

2026-09-23. **No findings in the reviewed source snapshot.** This is an interim
implementation-only review using the existing primary-source fact-auditor
context. It is not a fresh-context review and does not pass a phase gate.
The coordinator reported that attempts to create/reuse a fresh reviewer were
rejected by the agent thread limit. That limitation is not silently waived.

## Scope and evidence

Reviewed `src/hal/motor_port_unoq.cpp` and its private header state against the
finalized D077 contract, actual `motors.cpp`/`motors.h`, current config and
`P2_motor_clock_audit.md` / `P2_motor_update_audit.md`. The latter includes the
previously retrieved RM0456 Rev6 and current ES0499 Rev12 evidence. Exact source
hashes and the current Git HEAD are in `P2_motor_native_interim_snapshot.json`.

Source inspection covered:

- Factory/constructor inactivity and immutable source-derived periods; guarded
  fixed-size GPIO/PWM mapping, supported native device/channel identity and
  separation from EN/opponent/QTR pads.
- EN-first setup, checked native statuses/readback and OUTPUT/PUSHPULL/NOPULL
  ownership checks. Runtime callbacks perform no device initialization or
  pinctrl operations. HIGH admission consumes a settled current transaction and
  is rejected in MOTORS_ALLOWED0.
- Distinct reset/partial/full timer states and shared TIM3 progression. Exact
  CR1/CR2/SMCR/DIER/CCMR1/CCMR2/CCER checks exclude unsupported modes, including
  OPM, dithering, extended PWM encodings, output-clear and alternate consumers.
  TIM1 RCR/BDTR checks exclude repetition and break/automatic-output options;
  reserved advanced-timer register slots are not read on TIM3/TIM4.
- Invalidation before writes, requested pulse readback, all-four write receipt,
  post-write stale UIF clears and distinct fresh bits for all three timers.
  The loop has both an unsigned elapsed bound and a fixed iteration bound;
  final validation and deadline admission precede successful settle.
- Existing MotorGate integration: begin configures all channels before zero
  writes; activation follows LOW, four writes and settle; failure calls inhibit,
  which attempts every channel even after one fails. The backend supports
  cleanup on its already configured channels without requiring a complete bank.
  Unconfigured/unknown ownership is rejected, never initialized during cleanup.

These are source/control-flow assessments, not emulated execution or measured
hardware outcomes. Exclusive ownership remains a contract prerequisite; register
readbacks cannot prove the absence of a concurrent unregistered writer.

## Validation boundaries and next action

No tests were run by this reviewer. Independent test execution was in progress
under its separate author; current target compilation and binary inspection
were assigned to the coordinator. This review makes no claim that either passed.
It also does not certify transitive runtime hooks, loader behavior, actual MMIO
instruction order, physical EN/waveforms, silicon revision, WCET or human gates.

The next action is to attach the independent test and actual target evidence,
recheck this report if the reviewed source hashes change, and obtain the required
truly fresh-context review when a new eligible context is available. Preserve
the distinction between interim source review and phase/hardware acceptance.

Only this report and its snapshot receipt were written for this review. No
source/test/config, shared ledger or board state was changed by the reviewer.
