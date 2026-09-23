# D115 motor_stand inhibition diagnostic contract

Adopted2026-09-24 under D051/D075 after coordinator source review and separate
public-oracle preflight. No implementation, hardware grant, upload key, board
action or B4/B7 acceptance. D051/D075 permit the proposed software/compile-only
preparation. This is the narrow next increment identified in
`P2_motor_stand_next_audit.md`; it does not resolve the full-reversal/R6 conflict.

## Purpose and ownership

Prepare one finite observation of the existing native motor setup and terminal
inhibition paths. Use one `motors::UnoQPort` and one actual `MotorGate`. Preserve
both the actual begin outcome and the actual D095 HaltResult, including failed
setup and unconfirmed inhibition. No second driver, timer owner, scheduling
framework, Robot, Governor, Countdown, recorder or transport is introduced.

This owner never calls apply/reset, constructs RobotResult/PreviousTick, emits
START/GO/contact, selects wheel demands or obtains a motion token. It cannot
exercise active brake, directional drive, powered-output kill or20 full reversals.
Do not describe LOW/zero acknowledgement as measured electrical coast or a motor
safety guarantee. Existing R1/R6 token/hold/contact contracts are untouched.

Proposed new files only:

- `bench/motor_stand/motor_stand.ino`.
- `bench/motor_stand/src/motor_stand.h` and `motor_stand.cpp`.
- `bench/motor_stand/src/motor_stand_native.h` and `motor_stand_native.cpp`.

No existing HAL/core/config/locked-test changes. No new tunables, sampling count,
period, artificial deadline, loop timeout or default sensor/wiring assumption.
Both the bench owner and sketch require MATCH0/MOTORS_ALLOWED0 at compile time;
the established HAL's separate host-only active tests remain unchanged.

## Minimal public interface and report

Declare in namespace `motor_stand`, using the existing `hal/motors.h` types:

```cpp
enum class Phase : std::uint8_t {
    NOT_STARTED, DISABLED, ACTIVE, COMPLETE, FAULT
};
struct Grants {
    bool exclusive_motor_outputs = false;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    bool begin_called = false;
    bool begin_ok = false;
    motors::Fault begin_fault = motors::Fault::NONE;
    bool halt_called = false;
    motors::HaltResult halt;
};
class Runner {
public:
    explicit Runner(const motors::Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    void poll();
    const Report& report() const;
private:
    // Implementation-owned one MotorGate, Report and one-shot state only.
};
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    motors::Port port();
private:
    motors::UnoQPort native_;
};
```

The native declaration includes the actual `hal/motor_port_unoq.h`. Native.port
returns `native_.port()` directly: preserve every callback, context and candidate
period without wrapping, substituting success, invoking callbacks or adding a
clock owner. Native outlives Runner. The Port contract remains synchronous,
bounded, non-reentrant and exclusively owned by this Gate; callers must not invoke
its callbacks separately. Runner copies the Port into its single Gate.

The declaration's enum order, field order, types and actual HaltResult members
are the frozen public data contract after adoption. There are no reserved fields,
packed wire struct or assumed numeric sizeof/offsets. Any later raw-memory reader
must derive the actual target ABI from that exact debug ELF before use; this
increment adds no readout/serialization format. Report returns a const reference
valid for the Runner lifetime. A terminal report remains memberwise unchanged.

## One-shot sequence and publication

Constructor, Native.port, report and poll perform no clock/backend I/O. `poll()`
is always passive, before and after begin; there is no deferred work or cadence.
The only operation that can invoke motor callbacks is the first granted begin.

1. Mark the first Runner.begin attempt internally before any callback. A later
   call returns false with no change to Report or any Gate/native/clock activity,
   regardless of its grant. Reentrant use is outside the Port contract.
2. If the grant is false, set only phase=DISABLED and return true. All other
   report fields retain their defaults. Do not call Gate.begin, fault or halt;
   absent callbacks/invalid periods are irrelevant on this passive path.
3. With the grant true, set phase=ACTIVE and begin_called=true, then invoke actual
   Gate.begin once. Save its returned bool in begin_ok and immediately sample
   actual Gate.fault into begin_fault, before invoking halt. Do not add a private
   Port validator or change the existing Gate admission/failure ordering.
4. Set halt_called=true and invoke actual Gate.halt once, **whether begin returned
   true or false**. Copy the entire returned HaltResult unchanged. There is no
   retry, Gate.reset, conditional omission, synthetic stop command or extra clock.
5. Set phase=COMPLETE only when begin_ok=true, begin_fault=NONE, and the actual
   HaltResult has fresh=true, attempted=true, inhibition_confirmed=true,
   timing_valid=true and fault=STOPPED. Return true only for that COMPLETE result.
   Otherwise set phase=FAULT and return false, retaining all original fields.

ACTIVE only denotes the in-progress synchronous method. Once the first begin
returns, DISABLED/COMPLETE/FAULT is terminal and all future public operations are
passive. The bench does not mutate halt.fresh on reads or passive polls: that
retained true value describes the one actual halt invocation, not a new pulse.
COMPLETE is a valid diagnostic sequence with acknowledged callbacks/timing,
never measured pins, accepted motor operation, physical timing or a phase gate.
FAULT is the bench's unsuccessful diagnostic classification; it does not invent
or overwrite a Gate fault. In particular, invalid timing can yield phase=FAULT
while the actual Gate fault remains STOPPED and inhibition_confirmed remains true.

## Existing callbacks and failure/timing provenance

Delegate every native action to the existing Gate; do not duplicate its algorithm.
The required behavior is already specified in `P2_motor_gate_contract.md:11-31`
and `P2_app_transaction_contract.md:25-53` and implemented in
`src/hal/motors.cpp:79-98,200-225`:

- Gate.begin validates its copied Port. For an admitted port it configures EN LOW,
  writes LOW, configures the four PWM channels, writes zeros and settles in the
  existing order. Native callbacks retain all mapping/ownership/rate/readback/
  preload guards (`P2_motor_native_contract.md`). No bench bypass is allowed.
- A begin failure may already have performed its own bounded inhibition cleanup.
  The subsequent first halt performs the D095 terminal pass because begin was
  attempted: LOW first, every writable channel zero despite earlier failures,
  then settle once. It never reconfigures an unconfigured channel. Invalid Port
  begin can perform no I/O yet still be followed by this actual partial halt path.
- Preserve the immediate begin_fault separately. Halt keeps an earlier fault
  except the existing callback-failure upgrade to IO; successful setup normally
  yields halt fault STOPPED. An acknowledged later halt cannot turn a failed
  begin into COMPLETE or erase its cause.
- Halt obtains its own before/after timestamps when clockUs exists. The wrapper
  adds no S/A/C clocks and no duration for begin or total setup. Keep the actual
  timestamps, including equal values, natural wrap and reverse/half-range cases.
  timing_valid is the actual Gate result: both readings present and unsigned
  elapsed<2^31. Missing/backward time cannot suppress the inhibition pass. Zero
  default timestamps with invalid timing are not claimed observations.
- The existing native settle150us/4096-pass bounds remain unchanged. They bound
  the existing settle routine, not a newly claimed whole-bench WCET. No new delay,
  allocation, wait, reset or recovery command is added.

The ordinary sketch constructs one Native and one Runner from its passive port,
calls `runner.begin(Grants{})` once from setup, and `runner.poll()` from loop.
All-default deployment therefore performs no native motor/clock callbacks.
True-grant paths are exercised only in controlled host fixtures in this scope.
MOTORS_ALLOWED0 alone is insufficient for passivity: granted begin would still
configure proposed header pads/timers. No true-grant target run or upload key is
included, and no UART/Bridge/network command can toggle the grant.

## Checked compile route

The only new literal project is `motor_stand.ino`, from `bench/motor_stand`.
It requires default startup, MATCH0 and MOTORS_ALLOWED0. The board helper rejects
MATCH, Immediate, sketch.yaml/sketch.yml (including dangling links), every upload
and any D114 run option before staging/transport. Ordinary default compile-only
uses existing generic staging, followed by the same pinned `compile_app` checks
with project=`motor_stand.ino`; no direct unchecked compile fallback. No source
manifest key or upload path is added. The dependency policy admits that exact
project only with base FQBN and exact inert flags; all old projects stay unchanged.
Controlled tests check propagation of unavailable configuration/failed compilation
and show no upload/reset/monitor operations. This route is software-only and does
not change the current D114 run's pinned files until its capture is complete.

## Independent acceptance before implementation execution

Freeze tests separately from implementation, preserving any first-run failures.
Use the real existing MotorGate for owner traces; use a counted UnoQPort substitute
only for isolated Native/sketch binding tests, never as production hardware code.

| Test group | Required evidence |
|---|---|
| Defaults/ownership | Constructor and repeated Native.port are passive; one native owner/one Gate; exact underlying Port is returned; default grant has no calls even with a completely invalid Port; sketch calls begin once with false and polls passively. |
| Successful trace | Actual ordered begin then exactly one halt, all LOW/zero, no HIGH/nonzero; immediate begin_fault=NONE retained; actual halt STOPPED/fresh/attempted/confirmed/timing valid; COMPLETE/true; report remains unchanged after repeated begin/poll/report calls. |
| Failed begin | Missing callback/invalid period plus failures at each actual configure/write/settle slot; preserve begin bool/fault before halt, existing begin cleanup and distinct single D095 halt pass. All failed begin cases remain FAULT even if the later inhibit is acknowledged. |
| Failed halt | Fail each LOW/zero/settle callback; later writable channels still attempted; preserve first fault/IO upgrade and unconfirmed inhibition. No retry, reset or new configuration. |
| Time | Exactly the actual Gate clock callbacks; valid zero elapsed and natural wrap; reverse and exact half-range invalid; missing clock; invalid timing never skips cleanup and does not fabricate a Gate fault or total setup duration. |
| Terminal/API | First false/true grant consumes the one attempt; changed later grants do nothing; poll-before-begin does nothing; const report lifetime; no apply/reset/RobotResult/START/GO/contact/token production. |
| Build/native | Both nonzero MATCH and MOTORS_ALLOWED profiles refuse compilation; host bounds/no heap/functions<60lines; unchanged HAL/core/locked assertions; checked default compile, exact startup/retained-path/ABI/loader audit with no upload. |

Callback return values/readback claims remain software evidence. The named bench
does not complete B4's forward/reverse/brake/coast/powered-kill/wheel/PWM/supply
tests or any B7 brownout trial (`docs/prompts/P2_hal_bench.md:14,17`). A later
directional interface or full-duty exception requires its own explicit contract;
an actual motor-capable run still needs its specific STAND OK and physical
prerequisites. Implementation and independent frozen tests follow; physical acceptance remains open.
