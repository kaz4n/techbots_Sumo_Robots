# Core implementation checkpoint

P1 host development is permitted by D-016. P0 hardware acceptance and all human
phase gates remain pending. This describes the implemented standalone modules;
the complete robot scheduler, FSM and actuator path do not yet exist.

| Module | Implemented responsibility | Integration still needed |
|---|---|---|
| `core/types.h` | B0 logical input fields, state/mode/event names, inert output defaults | Recorder outputs, validated HAL input mapping |
| `countdown::Buttons` | Stable logical level qualification; rejects boot-held START; reports release edge and qualification timestamps | A1 decoding and both-held STOP |
| `countdown::Gate` | Full 5.1 s inhibit after a supplied qualified release event, cancel, latched STOP, one GO pulse | Heading reset/calibration/warning/snapshot services, FSM, real MotorGate |
| `countdown::Controller` | D-019 composition: qualify buttons first, then start the entire hold at the qualification tick | Services composition and complete Robot FSM |
| `countdown::Services` | D-024 bounded bias accumulation, rejection/previous-bias retention, latched line warning and latest opponent snapshot | Feed raw gyro/new observations, start/cancel from Controller, apply bias in HAL, complete FSM |
| `edge::Classifier` | Per-corner threshold and consecutive-white confirmation, persistent white mask | Validated fresh QTR acquisition, escape policy, R5 arbitration |
| `edge::Guard` | D-020 persistent escape request, black-plus-finished exit, latched all-white motion veto until reset | Escape directions/scripts/replanning and application of veto at MotorGate |
| `edge::forwardDemand` | D-021 straight/left/right-biased forward requests using 0.80 base and 70% inner-side request | Timed/heading-held segments and selection by the escape planner |
| `opp_fusion::Debouncer` | Per-bit polarity, two-sample assertion, continuous-clear hysteresis | Bearing memory, side/rear conflict policy, contact, phantom/stuck logic |
| `opp_fusion::frontView` | Seven front bearing/centering/close rows from B5.2 | Overall target selection and downstream motion policy |
| `governor::Governor` | D-017 electrical caps after compensation, slew, immediate braking/reversal/cap reductions, one-second battery lag | FSM profile selection and target-loss brake trigger; real MotorGate |
| `motion::Turn/Straight/Arc/Brake` | B7 demands, D-022 bounded heading correction, D-023 fixed timing with duty-only compensation, bounded IMU fallback | Escape/openers/re-flank scripts, explicit governor profile and MotorGate integration |
| `logframe` | B15 portable 25-byte frames and 8-byte exact-tick events, explicit invalid/clipped status | Recorder cadence/rings, approved overflow policy, event collection and idle-only dump |

All inputs are ordinary C++ values. Time arrives from callers as `uint32_t`
microseconds; elapsed intervals use unsigned subtraction. Motion/services
accumulate successive deltas in `uint64_t` to avoid losing a long-duration
deadline at the start-relative wrap. Consecutive calls must remain less than one
whole microsecond-counter wrap apart. Storage is fixed per object. Modules do
no I/O and read no clock. Sensor loops have fixed bounds; encoding is fixed-size.
Host execution does not prove the target's worst-case timing, including math calls.

The current isolated data paths are:

```mermaid
flowchart LR
    L[Logical button samples] --> B[Buttons]
    B --> E[Qualified events and both timestamps]
    E -->|D-019 qualification tick| G[Gate]
    G --> P[Logical motion permission and event pulses]
    Q[New completed RC observation] --> W[Edge classifier]
    W --> M[Persistent white mask]
    M --> EG[Edge guard]
    P --> EG
    EG --> EV[Escape request or latched motion veto]
    R[Raw electrical opponent mask] --> D[Debouncer]
    D --> F[Front table]
    F --> V[Front bearing, centered and close cues]
    A[Requested duties and explicit cap profile] --> S[Governor]
    S --> O[Bounded electrical duty requests]
```

`countdown::Controller` now connects qualification to Gate under D-019. It never
backdates a late qualifying call to the raw release edge. `motion_permitted` is a
logical result, not a hardware write. The application must apply the edge guard's
motion veto to governed outputs and MotorGate: logical permission alone must not
bypass all-white inhibition. Composed host tests check this path without claiming
that the full app or real MotorGate exists. Only the future HAL MotorGate may
write EN/PWM; BOOT, IDLE, COUNTDOWN and STOPPED must inhibit motion.

The edge guard handles the default zero push-through window. A positive configured
window fails compilation until its bounded exception is implemented and tested.
An all-white fault persists across black readings, script completion and revoked
permission; only explicit guard reset clears it. Before GO, line readings do not
start escape or latch a new fault. Normal escape requires both all-black readings
and a finished script to clear. Scripts/replanning and freshness remain separate.

This diagram is the implemented standalone Gate, **not the unfinished Robot FSM**:

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> HOLDING: supplied qualified START release
    HOLDING --> IDLE: MODE cancel
    HOLDING --> READY: elapsed >= 5100000 us
    IDLE --> STOPPED: STOP request
    HOLDING --> STOPPED: STOP request
    READY --> STOPPED: STOP request
    STOPPED --> IDLE: reset object
    READY --> IDLE: reset object
```

Reset is a software lifecycle operation, not a new physical STOP-recovery
interaction. GO is emitted once on entry to READY; permission stays latched until
STOP or reset. No commanded motor duties are produced by these services.

The intended complete path remains the original architecture: MCU scheduler reads
HAL -> builds Inputs -> steps Robot -> governor -> MotorGate. Linux builds,
flashes and receives idle log dumps. As PLAN section 7 explains, control belongs
on the MCU so Linux boot and scheduling cannot delay edge response; target timing,
boot behavior and log independence still need their own evidence. D-018 approves
gated-state services before motor inhibition; the complete scheduler/FSM is still
pending. D-017 approves final electrical caps; the governor implements those for
the specified profiles. D-020 resolves persistent/all-white inhibition. QTR
acquisition, timed escape motion/replanning, ALL_IN arbitration
and recorder policy remain in `state/analysis/spec_conflicts.md`.

The governor's battery filter is a first-order lag with the existing B6 one-second
time constant, using backward Euler: `alpha = dt / (tau + dt)`. Its first sample
initializes voltage and has zero acceleration budget. Signed braking and reductions
to smaller safety caps are immediate; reversal emits zero before opposite torque.
Nonfinite inputs yield a zero result with `valid=false`, leaving the application
fault decision to its future controller. Target-loss braking still requires the
FSM to assert `brake`; dropping centered/contact flags alone selects the approach
cap and is not an implementation of the separate B6 target-loss transition.

D-021 now supplies the forward escape base and cap: EDGE_BACK_DUTY (0.80 default).
The pure demand builder produces `(0.80, 0.80)`, `(0.56, 0.80)` for left bias,
or its right mirror. The caller must pass these through the EDGE_FORWARD governor
profile and obey the edge guard's veto. The 70% value specifies requested duties;
compensation, individual caps and acceleration slew can alter the final ratio.
For example, at 9 V after settling, a left-biased request becomes approximately
`(0.69067, 0.80)`. This is arithmetic, not a measured turn trajectory. No timed
segment, heading-hold controller or hardware path is supplied by this helper.

Motion now supplies those generic primitives separately; it does not yet select
or sequence escape/opener/re-flank segments. A turn uses shortest signed heading
error, a strict 5-degree completion tolerance and the original 700ms timeout.
On IMU loss it times the last known remaining angle once, without extending that
deadline on recovery. Straight correction preserves wheel direction, including
reverse, and arcs use accumulated yaw. Every terminal command requests zero;
only the eventual caller/governor/MotorGate path can grant and apply motion.

Countdown Services uses the D-024 half-open [1500,4500)ms window and reports its
result once. It accepts raw gyro values before bias subtraction. Missing samples
are never manufactured; any invalid in-window observation rejects calibration,
and duplicate timestamps add no observation. The application must start this
object on the qualified release and cancel it on IDLE/STOPPED transitions. The
independent host harness checks that composition; Controller alone still only
owns Buttons and Gate. Line warning does not block GO. Physical sample freshness,
HAL bias application and the heading reset at GO still need integration.

Recorder encoding retains multi-revolution heading in signed 32-bit centidegrees
and event time in uint32 microseconds. Encoding is separate from collection and
storage, so it does not resolve B15's finite-buffer overflow conflict. A future
recorder must handle INVALID/CLAMPED status explicitly and never turn an invalid
measurement into apparently valid evidence. No CSV/dump or ring exists yet.

Student explanation of what exists today: "We pass timestamped values into small
C++ functions, so the laptop can test the same decisions without a robot. The
start timer cannot grant permission until the complete hold has elapsed. Separate
filters reject sensor flicker and classify the line corners; a table converts
front detections into a bearing. These pieces cannot drive motors by themselves.
We still have to connect the approved control rules, verify the hardware motor
gate, and measure the complete loop on the robot."
