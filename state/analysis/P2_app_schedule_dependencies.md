# P2 app schedule dependencies - 2026-09-23

Scope: source inspection of the existing IMU, QTR, D093 InputOwner and MotorGate
interfaces while D093 validation runs. Only this new note is owned by the audit.
No production code, config, ledger, established test, board state or requirement
was changed. No test or hardware command was run. D093 implementation presence is
not a claim that its concurrent validation has completed.

## Concrete conclusion

The runtime IMU API does **not** support deferring I2C chunks around other work.
`imu::Acquirer::read(now)` calls one synchronous `Bus::acquireMotion()` and returns
only its final result (`src/hal/imu_acquisition.cpp:121-149`). `acquireMotion()`
creates a stack-local Operation, completes the readiness transaction, then
immediately completes the 15-byte transaction under that same Operation
(`src/hal/imu_bus_unoq.cpp:464-501`). Its byte/flag waits are polling loops, with
no caller callback, pending state, resume method or scheduler admission point
(`:351-400`). The public API exposes only complete operations
(`src/hal/imu_bus_unoq.h:53-63`).

The app can defer **starting** an IMU read. Once it calls read, it cannot service
QTR, buttons, battery or MotorGate until the read and any cleanup return. Splitting
the public readRegister/readMotion calls in app code is not equivalent: Acquirer
owns its Bus, and D081 requires one shared operation deadline, poll budget,
readiness/STOP ordering and terminal failure lifecycle.

Setup is cooperative only **between** operations. `advanceSetup()` delegates to
`Setup::advance()`, which either returns for a wait or executes one whole Bus
operation (`src/hal/imu.cpp:156-185`). It does not make each I2C operation resumable.

The existing APIs therefore permit an honest experimental schedule, but do not
establish a schedule satisfying all current deadlines and full-tick <800 us.
The component limits below are acceptance/cleanup guards, not measured physical
WCET or proof that their adverse cases occur together. Conversely, unmeasured
typical speed cannot justify smaller scheduling reservations.

## Actual calls, limits and evidence ages

| Public operation | Current execution and scheduling obligation |
|---|---|
| `imu::Acquirer::start`, `advanceSetup` (`imu_acquisition.h:32-34`) | Start arms the setup lifetime; each advance performs at most one complete native operation. Setup has an existing 1000000 us total deadline, 1024 advance calls and 64 requests (`config.h:73-75`). Calling advance in every spin can exhaust its count during prescribed waits; the app must schedule useful advances. Setup calls remain inhibited boot work. |
| `imu::Acquirer::read` (`imu_acquisition.h:35-37`) | One whole readiness/status + STOP/idle + 15-byte acquisition; aggregate elapsed must be <600 us, with one 8192-poll budget. Failure allows one separate 50 us/8192-poll cleanup, never a new 600 us allowance (`P2_imu_acquisition_contract.md:28-33`). All other app work waits for return. |
| `imu::Estimator::observe` (`imu_heading.h:47-49`) | New accepted observation completion gaps must be <=2000 us; >2000 latches GAP (`imu_heading.cpp:113-135`). Runtime acquisition separately faults at >=20000 us observed silence, both at call admission and accepted completion (`imu_acquisition.cpp:87-118`). The 20 ms limit is not permission to schedule heading updates every 20 ms. |
| `line_qtr::Reader::start/advance/report` (`line_qtr.h:56-62`) | Start returns CHARGING. Release needs at least 11 reported us after the last HIGH write and must complete while charge age is <100 us. Each active call has a <100 us acceptance guard; complete frame including cleanup must be <2500 us. Start spacing is >=2000 us; active calls are limited to 8192. See `line_qtr.cpp:166-174,252-279,351-377,430-438`. |
| QTR failure/cancel cleanup | One finite cleanup pass attempts every safely owned pad; a separate 100 us reporting budget does not preempt the native calls. Cancellation of an active frame latches a fault, so cancel is not a scheduler pause (`line_qtr.cpp:380-445`; `P2_qtr_native_contract.md:32-40,94`). |
| `power::InputOwner::readBatteryIfDue(bool)` / `readButtons(bool)` (`power_inputs.h:47-50`) | Caller grant authorizes at most one actual A0 or A1 conversion. No hidden second conversion. Native success requires <100 us and failures may add separate 100 us cleanup. A0 period 10000 us / expiry 20000 us are now selected D093 values (`config.h:44-48`); this supersedes the earlier integration map's battery-contract-pending statement. The grant remains the scheduler's obligation. |
| Button/line admission | Button continuity/age is bounded by 5000 us (`config.h:37`); line source age expires at >=6000 us and requires source start spacing/ordering (`P2_qtr_native_contract.md:157-166`). Deferring calls cannot manufacture new evidence or reset either age. |
| `motors::MotorGate::apply` (`motors.h:31`) | One synchronous transaction writes EN low, four PWM values, performs settle, then optionally EN high (`motors.cpp:142-162`). Settle polls all three native timers with a <150 us guard / 4096-poll ceiling (`motor_port_unoq.cpp:330-354`). The 150 us number is the settle phase, not the complete Gate call. |

Motor failure accounting is larger than the common shorthand: if a transaction
fails during/after its first settle, `transact()` calls `inhibit()`, which writes
the disabled bank and calls settle again (`motors.cpp:60-76,151-155`). Allow for
two settle invocations plus surrounding work on that path. The audit does not
claim either invocation consumes exactly 150 us, or that every native failure
reaches the second poll loop.

Similarly, an IMU failed transfer reports `completed_us=op.observed_us` after
calling cleanup, without changing that operation observation to cleanup end
(`imu_bus_unoq.cpp:310-320`). Its diagnostic interval must not be used as the
wall-time duration of the full call. An outer clock bracket includes cleanup.

## QTR creates sub-tick service obligations

After starting charge, the scheduler owes a qualified release in [11,100) us
from `drive_completed_us`; it must reserve time for the full charge-read and
release pass, not merely enter advance before the deadline. Do not admit an
atomic IMU call, ADC call, motor settle or display/transport job whose admitted
duration can cross that window. The existing 100 us ADC and 150 us settle guards
alone are already insufficient reservations inside a newly started charge.

Discharge also needs service opportunities for **color qualification**, not just
eventual frame completion. The actual samples form intervals: last HIGH supplies
a conservative lower bound; first LOW supplies an exclusive upper bound
(`line_qtr.cpp:309-335`). Classification is white when upper<=threshold, black
when lower>=threshold, otherwise ambiguous (`P2_qtr_native_contract.md:183-196`).
At the current 300 us thresholds, a long IMU blocking interval spanning the
threshold can produce a structurally valid frame whose color is ambiguous. A
frame finishing before 2500 us does not by itself avoid that fault. Do not clamp
late LOW readings or infer a color from a poll schedule. Calibration thresholds
can differ per pad, so a hardcoded 300 us scheduling assumption is insufficient.

Service gaps, release skew, intervals and source age already have observable
fields in Snapshot. Actual color separation and useful maximum service gaps
still need physical evidence; no unmeasured universal poll interval is selected
here. The raw driver detects deadlines only when called; no background watchdog
services overdue QTR work (`P2_qtr_native_contract.md:35-40`).

## Fixed 1 kHz work and complete-tick accounting

1. The app must preserve 1 kHz decisions, fresh opponent observations, one actual
   Gate transaction per fresh Robot result, and the existing receipt ordering.
   It cannot reduce their rates to make sensor scheduling easier.
2. It cannot simply alternate IMU and ADC on successive 1 ms ticks and claim
   healthy heading: IMU completion-to-completion gaps, including duration
   variation, must stay <=2000 us. A nominal 2 ms invocation period has no
   completion-jitter margin. Missing heading remains the existing explicit
   fallback/fault behavior, never a new fabricated observation.
3. Holding/delaying an actual observation preserves its real completion time.
   Robot admission also checks decision-to-source age <=2000 us
   (`src/core/fsm_imu.cpp:62-65`). A late decision can invalidate otherwise timely
   acquisition. Replaying a previous estimate does not refresh that age.
4. A deferred acquisition is not an actual `NO_NEW` result: D081 obtains NO_NEW
   only from a completed readiness read. Pending/deferred work must not advance
   Acquirer sequence, calibration, yaw or sensor checked time. The current public
   Acquirer/Estimator API has no runtime PENDING result; NOT_READY after the
   profile was seen is not a valid substitute (`imu_heading.cpp:179-197`).
5. D092 must be used from the first Robot tick. With S=start, D=decision,
   A=application, C=completion and N=next start, preserve S<=D<=A<=C<=N and
   execution=C-S (`P2_tick_timing_contract.md:26-44`). Native acquisition,
   cleanup, QTR service, ADC work, estimator/projection, Robot, Gate, recorder
   and applicable output work must have an explicit real timing owner.
6. Do not close C, do additional sensor/service work, and begin N afterward:
   that omits work. Starting N before early QTR/I2C service is valid, but any
   elapsed wait before its decision remains inside the next complete interval.
   Splitting a hardware QTR frame across control epochs is valid; every executed
   service call still belongs to an accounted epoch. Do not treat the entire
   1500 us discharge as one blocking control tick or subtract its waits from
   a contiguous C-S receipt.
7. The published ceilings 600+150+100=850 us already exceed 800 before other
   work; adding a second ADC gives950. This does not prove real hardware takes
   that time, but is not a sufficient reservation proof. Merely moving the
   same synchronous calls between named ticks does not solve it.

## Smallest remaining software contract and first eligible task

Before an app transaction owner is allowed to assume interleaving, freeze a
**resumable runtime IMU acquisition contract at the actual native Bus/Acquirer
boundary**. This is the smallest missing enabling interface; another wrapper
around synchronous read cannot provide it. No new configuration value, deadline
increase, lower sample-rate requirement or phase/motor authority is selected by
this audit.

The first eligible task is a narrow installed-source/manual audit and public
contract for bounded native acquisition advances. Verify the exact peripheral
states where returning to the app is supported (TXIS/TC/RXNE/STOP and deferred
servicing/clock stretching), then freeze these obligations before implementation:

- Persist the same 1-byte readiness transaction, completed STOP/idle and 15-byte
  burst. Partial bytes remain private. Preserve D081's conditional freshness
  inference; a consumed readiness event cannot be retried after failure.
- Keep one 600 us **wall-clock** operation deadline and one 8192-poll budget
  across all advances, including time spent running other jobs. Do not renew
  either on resume. Retain at most one existing 50 us cleanup allowance and
  terminal native ownership/fault behavior.
- Define a fixed amount of work per advance and its admission/overdue/cancel
  result. A bounded count is not a measured sub-tick WCET; its native calls still
  need actual timing evidence before full schedule acceptance.
- Separate pending/no-call state from completed NO_NEW/OBSERVATION/FAULT and
  specify how an app decision sees absence or already admitted bounded heading
  without inventing a source timestamp. Preserve estimator source gap, sequence,
  bias and explicit Robot admission contracts.
- Define how every advance and fault cleanup is assigned to D092's actual S/C
  interval. Total I2C elapsed still includes the periods spent servicing QTR/ADC.

Independent tests can then demonstrate interrupted/resumed protocol ordering,
one aggregate deadline and poll budget, no partial publication, one cleanup,
real source timestamps, and interleaved QTR charge service with complete timing
receipts. Reuse the established constraints in
`tests/native_imu_bus/acquisition_cases.cc:175-262` and
`tests/test_imu_acquisition.cpp:276-290`; preserve all established tests.

If the audited native peripheral cannot support that bounded service contract,
record that result rather than silently weakening deadlines. A measured atomic
schedule could be another future option, but no suitable combined hardware timing
evidence exists in the inspected artifacts. This note authorizes no hardware
run and proves neither schedulability, physical color separation nor full WCET.
