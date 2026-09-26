# D197 native settle exit observation

26 September 2026. Add only diagnostic observation of the existing native
settle decision. D195's longer inhibited observation reported an APPLY SETTLE
failure at epoch921 and another during final HALT. The outer154/153us callback
spans do not identify an internal exit. Its stored859us maximum is not a WCET
pass. Do not select a timing or hardware repair from those observations alone.

Implement only a new public header `src/hal/motor_settle_probe.h` and conditional
instrumentation in `src/hal/motor_port_unoq.cpp`. Use the existing
SUMOX_MOTOR_FAULT_PROBE==1 selection; config already requires MATCH0/MOTORS_ALLOWED0
and excludes competing profiles. Do not add a new selection flag, change config,
the sketch, Runtime, MotorGate, Trace, Runner, pins, limits or historical evidence.
This contract prepares host software only, not a new native attempt.

## Frozen starting points

These are the exact current bytes before instrumentation. Only the first source
may change in this implementation; the new header has no historical predecessor.

| Path | Bytes | SHA256 |
|---|---:|---|
| src/hal/motor_port_unoq.cpp | 16448 | 04803c88dc51e62dee4c1be15f4c1c8392df01d84893155bc10644cf7afd694a |
| src/hal/motor_port_unoq.h | 1427 | 7f09a544a032b35207de7c5f074f3f1fd3de9e74c3b482579f819eaa39020ef5 |
| src/config.h | 22873 | 34d6d6bce215fc098c3c4ae8e2c4436cb66e50e4f73db81a7ef8da964ba242c6 |
| tests/locked/native_motor_port/native_fixture.h | 1988 | 2dad212ae2eb1d116e79f450345f6d171a8da15d1a5408ff34fc10921510cae5 |
| tests/locked/native_motor_port/native_fixture.cc | 9292 | 8119661047e90a5d1aff4b946986385591f6a5b5fdcee92a4f2f302a1e3d2aa2 |
| tests/locked/native_motor_port/cases.cc | 22990 | 7d01821ab2ccc042140e9433bb3207b943331868726e41f644d45ca2006de312 |
| tests/tooling/test_motor_port_unoq.py | 9136 | 71b25cce8042dfcb2cd49b1fe35f0c6f548185fff836f987fa42faba416cd152 |
| bench/motor_fault/src/motor_fault.h | 3618 | 0b6daf206692baab509fba12ff1afb17b812caf1ff36817883b6ee9d358c1728 |
| bench/motor_fault/src/motor_fault.cpp | 7606 | a5e3624ec89cf37f8344e069fed2e2f25bce1be8e0e6911b7aee774297c2f8c6 |
| bench/app_motor_observe/app_motor_observe.ino | 845 | 1df77ff537ef354bcb6bae9141ad117881216df125581f0d4ade3e286a6f007b |
| bench/app_motor_observe/src/app_motor_observe.h | 2478 | 25bf299be1e2b917a0f91e7ad933eec5179cbfe6d92273bed0a8d9f5ce97d77e |
| bench/app_motor_observe/src/app_motor_observe.cpp | 3116 | eec10eacd250590f4eb4a6b1c01b0cac925411c1f126fe45fda9401de3de4bb3 |

All other locked/native fixture files and established tests remain unchanged.
Preserve the original cpp bytes by its Git source identity; do not add a second
production implementation or duplicate source snapshot.

## Public interface and fixed representation

The new header includes the existing config and standard fixed-width types.
The following declarations exist only when SUMOX_MOTOR_FAULT_PROBE==1, in
namespace `motors`. There is no probe0 accessor, report symbol, runtime no-op
dependency, diagnostic allocation or diagnostic class field.

```cpp
enum class SettleProbeReason : std::uint8_t {
    NONE = 0, SUCCESS = 1, NULL_CONTEXT = 2, PRECONDITION = 3,
    INITIAL_BANK = 4, POLL_DEADLINE = 5, POLL_BANK = 6,
    FINAL_DEADLINE = 7, POLL_LIMIT = 8
};
inline constexpr std::uint8_t SETTLE_ELAPSED_VALID = 1U;
inline constexpr std::uint8_t SETTLE_POLL_VALID = 2U;
inline constexpr std::uint8_t SETTLE_FRESH_VALID = 4U;
struct SettleProbeSample {
    std::uint32_t elapsed_us = 0U;
    std::uint32_t poll_index = 0U;
    SettleProbeReason reason = SettleProbeReason::NONE;
    std::uint8_t fresh_mask = 0U;
    std::uint8_t valid = 0U;
    std::uint8_t reserved = 0U;
};
struct SettleProbeReport {
    SettleProbeSample current{};
    SettleProbeSample first_failure{};
    std::uint8_t has_current = 0U;
    std::uint8_t has_failure = 0U;
    std::uint8_t reserved[2] = {};
};
const SettleProbeReport& settleProbeReport();
```

Require standard-layout types with alignment4. Sample is12 bytes, with offsets
elapsed_us0, poll_index4, reason8, fresh_mask9, valid10, reserved11. Report is28
bytes: current0, first_failure12, has_current24, has_failure25, reserved26.
Use ordinary fixed-width members and static assertions; no packing, heap,
pointer field, dynamic container, virtual dispatch or variable-length buffer.
All reserved bytes remain0 and has_current/has_failure are exactly0 or1.

One internal static-duration `SettleProbeReport` in the native cpp is the sole
persistent diagnostic storage. Its source identifier is `settle_probe_report`;
the accessor returns a const reference to that same object without hardware,
clock, allocation, mutation or reset. Its symbols/address still require actual
target observation before a future capture. Do not publish a mutable reference,
setter or reset API. No change to UnoQPort fields/layout is allowed, even in
probe1; existing Trace/Runner/report layouts remain exact.

The report covers calls to this native settle callback during one program
lifetime. Initial state is entirely zero/NONE with both presence flags0. Each
return replaces current and sets has_current1. The first false return copies
that sample to first_failure and sets has_failure1. Later false returns,
successful returns, accessor calls, a repeated port() call, MotorGate cleanup
and final HALT never replace or clear first_failure. NONE is initialization
only and must never describe a completed call. No invocation counter or history
buffer is needed. Fresh-process tests provide independent initial states.

## Exit meanings and observed values

These reasons identify the seven existing false outcomes and success, not
subcauses inside bankValid or the compound precondition. Never split, re-evaluate
or reorder a compound expression to obtain a more detailed reason.

| Reason | Existing decision | valid | elapsed_us, poll_index, fresh_mask |
|---|---|---:|---|
| NULL_CONTEXT | context is null | 0 | all0; no clock/hardware call |
| PRECONDITION | configured_mask/written_mask/enableLow compound guard fails | 0 | all0; no settle-start clock |
| INITIAL_BANK | first bankValid fails after started_us was read | 0 | all0; a start timestamp alone is not an elapsed observation |
| POLL_DEADLINE | loop-top unsigned elapsed is >=150 | 7 | that exact elapsed; current zero-based poll; accumulated fresh mask before this poll's flags |
| POLL_BANK | bankValid fails after this poll's three flag checks | 7 | the loop-top elapsed, without a new clock read; current poll; fresh mask after those checks |
| FINAL_DEADLINE | all three timers fresh but final unsigned elapsed is >=150 | 7 | that exact final elapsed; current poll; mask7 |
| SUCCESS | all three timers fresh and final unsigned elapsed is <150 | 7 | that exact final elapsed; current poll; mask7 |
| POLL_LIMIT | all4096 iterations complete without success or earlier rejection | 7 | last loop-top elapsed; last executed poll4095; mask after its flag checks |

An invalid numeric field is0; validity distinguishes absence from an observed
zero. ELAPSED_VALID means the value was read at the stated existing clock site,
not that it measures duration through the return or through bankValid. In
particular POLL_BANK/POLL_LIMIT retain an earlier sample. FRESH_VALID describes
the original accumulated software mask, including legitimate0; it does not add
a register observation. POLL_VALID is the executed loop index, never the number
of reads or the untaken post-loop index4096. No other validity bits are set.

## Preserve the exact decision and I/O sequence

Preserve all existing settle conditions, short-circuit order, bool result,
self.settled_ writes, started_us acquisition, three update clears, per-poll
clock/three update checks/bankValid order, final clock and unsigned wrap
arithmetic. Preserve every other native function body and all existing device,
GPIO, PWM, timer-register and clock reads/writes and their counts. In particular,
do not optimize/cache bankValid, add a timer read, request another micros(),
split enableLow checks, add a clock sample for INITIAL_BANK, or delay any native
call until after another existing decision.

MOTOR_PWM_SETTLE_US stays150 and MOTOR_PWM_SETTLE_MAX_POLLS stays4096. EN/PWM
pins, ownership checks, fresh-update requirements and every safety refusal stay
unchanged. Probe1 remains forced inert by the unchanged config guard.

For probe0, the preprocessed UnoQPort::settle function body must equal the
original preprocessed body apart from whitespace. Merely equivalent behavior
is insufficient. Small probe-only helper/macros around existing return sites
and elapsed expressions are permitted: probe0 must expand back to the original
expressions/returns, with no extra empty statements or evaluated arguments.
No runtime no-op diagnostic call may remain. Preserve original probe0 symbols
and UnoQPort layout, with no diagnostic storage or accessor symbol.

For probe1, reuse each existing micros result exactly once; local diagnostic
bookkeeping may retain that already obtained unsigned value. Publish the fixed
report only after the corresponding decision at a return site. Do not write the
persistent report on every polling iteration or introduce a callback/hook path.
Keep functions under60 lines, use a small explicit RAM-only publication helper,
and keep instrumentation visibly separate from admission logic. No generic
tracing framework or bankValid subreason tree is needed.

Added instructions and stores can perturb timing even with identical clock and
hardware-call counts. A later result concerns the instrumented image. The
report supplies no atomic-live-read guarantee; sequential capture coherence
remains UNPROVEN. No timer-limit relaxation or native failure repair follows
from a particular reason until actual evidence is collected and reviewed.

## Independent tests before implementation execution

The test author derives expectations from this contract and the unchanged
locked native fixture, then freezes new tests before reading the implementation.
Add only new unlocked tests, initially `tests/tooling/test_motor_settle_probe.py`
and `tests/native_motor_settle_probe_cases.cc`. Reuse the existing native fixture
headers/cc and real Port callbacks; do not edit any locked file or old assertion.
Compile/execute only after separate coordination; this drafting task runs none.

Required bounded coverage:

- Exact enum values, sizes/offsets/alignment/defaults, stable const accessor,
  zero reserved/unknown bits and no allocation. Probe1+MATCH1 or MOTORS_ALLOWED1
  is rejected by the existing guard; probe0 exposes no observation interface.
- Trigger NULL_CONTEXT and every other reason via public Port::settle. Use
  incomplete writes/EN readback, initial rate/register faults, per-poll readiness
  loss/register corruption, fresh_after, ticks_per_poll and event_elapsed.
  Test each compound-precondition short-circuit position without changing it.
- Strict149/150/151 final-clock boundary, loop-top deadline, unsigned micros
  wrap, a frozen clock with4096poll exhaustion, partial fresh masks and correct
  validity/last-sample semantics. Observe no extra clock on initial bank failure.
- Success before failure, first failure followed by another failure and success,
  and actual MotorGate cleanup/HALT where practical. Current changes; the first
  failed sample remains byte-exact. Run scenarios in fresh processes instead
  of adding a diagnostic reset interface or casting away accessor constness.
- Compare probe0/probe1 bool results, complete ordered fixture native-call trace,
  clock counts and relevant final hardware state for the same controlled inputs.
  Check probe0 preprocessed settle body against the frozen original, and all
  unchanged headers/config/Trace/Runner/locked fixture hashes. Existing locked
  native tests remain independent regressions, not rewritten copies.

The existing Linux fixture maps synthetic timer/GPIO addresses and records
READY/CONFIGURE/WRITE_GPIO/READ_GPIO/ROUTE/RATE/PWM/CLEAR/POLL/CLOCK calls. Its
failure controls support the listed scenarios without real hardware. This
demonstrates software observation and preserved fixture-visible sequencing,
not real register timing or electrical behavior.

Later target use needs a new source-bound compile/ABI/entry/capture binding for
the changed diagnostic image and report symbol. Preserve every consumed D195
owner and raw failure. That later work, production static compilation, actual
loading, live RAM/stack/WCET, physical acceptance and motor-run/human gates are
outside this contract.
