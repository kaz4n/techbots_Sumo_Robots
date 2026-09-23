# D079 native MPU6050 transport validation

2026-09-23 Asia/Dubai. Baseline6911b25, contract/source4ec0ef4. D051/D075 permit
actual P2 software before physical acceptance. Implementation commit a749816. This increment supplies the real
private I2C4 transport, not MPU6050 setup/calibration/heading or app integration.

## Implementation and selected bounds

imu_bus_unoq.cpp/h provide typed configuration/identity reads, two-byte register
writes and one15-byte INT_STATUS+motion read. The native path uses checked TXIS,
TC, repeated START, RXNE, AUTOEND and fresh STOP completion. Partial buffers stay
private; any fault returns zero data and explicit status/diagnostics. Constructors
and the inert retained-method probe perform no bus operations.

An irreversible claim survives failed first writes and destruction. Admission
checks the installed deferred device, both IRQs, exact source/pad/timing metadata
and nominal clock/power modes. Each pad's lock is checked separately. One600us
request deadline and8192 polling budget cover all bytes/phases. Setup has its own
100us/8192 limit; cleanup has a separate50us/8192 limit. Terminal cleanup only
disables PE under retained ownership: no synthesized STOP, reset, GPIO pulses,
reenable or retry. Local DISABLED does not establish an electrically idle bus.

The fixed0x40EB202C AFON/DNF0 profile is conditional engineering arithmetic,
independently reproduced over128 corners. The modeled15-byte clock portion is
411.175..539.460us; unmodeled software/stretch/preemption costs remain. The clock
envelope is not measured, and the MCU's160MHz rating still applies. The nominal
650us failed-request/cleanup sum can extend to658.586us before check lateness,
leaving at most141.414us before800 for other work under the chosen mathematical
premises. These figures are not complete-tick WCET. SC-AJ remains open globally.

## Actual validation

- Config12/12 PASS, including every original B16 expectation and strict whole
  declaration equality. The initial11-method run's one missing-D079-allowlist
  failure is preserved; a new exact-value test and ten declared names resolve it.
- Normal host CTest2/2 PASS6.84s, exit0. ASan+UBSan2/2 PASS25.61s, exit0:
  1030cases/20982541assertions and enabled MotorGate37/3796846, no failures/skips.
  Those suites do not execute native target code, which has separate tests.
- Independent author native10-method run PASS138.097s, exit0:49 positive native
  executions/83cases/992parent assertions, no skips.102 subprocess receipts have
  100exit0 and the two required assertion/signal sentinel exits1. Root verified
  all102receipt hashes and30fixture files against the frozen final manifest.
- Fresh separate same-model review PASS/no open software findings. Independently
  replayed all10methods PASS146.531s,83positive native cases/992parent assertions,
  no skips;102subprocess receipts with the same two required negative sentinels.
  Four supplemental final-boundary regressions pass separately. Source/fixture
  hashes, actual42-file target map,3ELFs and36native exports independently checked.
- Initial actual UNO Q Linux compile-only PASS, source
  df4c3f13694f46574d459e85ed2945cc93d3f0656ad539fec3945c87c46bb4ee,
  default/MATCH0/MOTORS_ALLOWED0,81720B program/33628B compiler memory, exit0.
  This draft predates repairs and is not final validation.
- Repaired actual target compile PASS, source
  f3e9b5464c0d83b0249cabf78c7cf73a5d150d4b3823277bce320d7d7a84d224,
  default/MATCH0/MOTORS_ALLOWED0,81992B program/33788B compiler memory, exit0.
  Root independently restaged and matched all42source files to the collected
  target map. This is an isolated probe, not full-application measured free RAM.
- Broad existing tooling421/421 PASS526.431s, exit0. With the independent native
  10-method suite this is431 distinct tooling methods across separate runs, not
  one combined invocation. The broad run retains its command/status/full output;
  per-subprocess native receipts are retained by the separate author/reviewer runs.

P2_imu_bus_record.py captures exact commands/status/streams in P2_imu_bus_raw/.
P2_imu_bus_target_audit.py collects source/ELF evidence without MCU attachment.
The read-only preflight reached CLI1.5.1/core1.0.0/Python3.13.5; overall status
INCOMPLETE/exit1 was caused by the existing missing rsync utility(exit127).
The already verified ADB compile path does not depend on rsync.

## Preserved defects and test-model corrections

Draft power-independent transport CPP SHA
82b0c3314b93095da723aadc11347e685b094fa011faa5dfd03974f35fa55e43:

- A combined-mask LL pin-lock check required both pins locked and missed either
  individually locked pin. Independent setup/runtime mutation cases exposed it.
  Later fixture refinement models silicon ignoring writes to locked pads: the
  original fake setup-ready outcome was model-specific, while missed admission
  and runtime lock checks remain genuine source defects. Both receipts remain.
- A pad change at the pristine ISR observation could evade the earlier check.
  Revalidation before the claim/first configuration now rejects it.
- Final setup, request and cleanup timing observations preceded accepted scans;
  a late transfer error could also evade the last ISR observation. The separate
  reviewer reproduced four incorrect acceptance outcomes on the draft. Final
  observations were reordered; all four focused regressions now pass.
- Native protocol-fault flags such as ADDR/TCR were lost from error_flags.
  D079's explicit diagnostic addendum retains unexpected protocol status along
  with native hardware errors before PE0 resets the flags. Assertions retained.

The independent test author did not read production CPP. Supplemental boundary
regressions came from the source-aware reviewer and retain specification-derived
failure expectations. A moved injection hook initially did not inject its fault;
the original no-injection failure and selector-only correction are preserved.
Another fixture pacing correction exercises shared budget exhaustion across
payload phases rather than before payload. Neither change relaxes a deadline,
failure status or zero-buffer assertion. Expected child CHECK/signal failures
test harness propagation and are never counted as passing native cases.

Repaired CPP SHA
940f4e2c8c7a251b7060c5336f54da9e128a4a6fae1b21f5f5851203deb9e0de.
No old locked test, core, application, behavior default or board tool changed.
Do not describe parent fork-status assertion totals as all child assertions.

## Acceptance limits and next work

No upload/reset/MCU attachment, I2C/pad operation or motor run occurred. Existing
MCU image remains the last-known inert QTR61d7a2d0. No physical MPU address,
breakout/pull-up/voltage, oscillator lock, waveform, success/fault timing or
whole-tick acceptance is claimed. SC-AJ and inherited F091 runtime paths remain
deployment blockers. No human phase gate, PINMAP or EXPLAINED approval follows.

Next B3 task is actual bounded MPU6050 reset/configuration/readback and genuinely
new sample handling, followed by scale/axes/bias and continuous-yaw integration.
A completed bus transfer alone cannot supply those sensor guarantees. Preserve
the current core's unreset continuous-yaw domain and explicit unavailable-data
behavior; do not silently treat repeated or partial data as fresh measurements.
