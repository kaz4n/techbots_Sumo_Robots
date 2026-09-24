# D138 first implementation: informational pre-start display

2026-09-24 Asia/Dubai. Contract: [P7_readiness_contract.md](P7_readiness_contract.md),
SHA256 `568bc27719e32d397dfcfe7130558e952b53f0f651430a89c6b8d6a66b00904a`,
adopted in `36a96bd2`. This note records the first complete implementation before
any implementation test execution. Source was compared against current HEAD
`b7d8b509ee5d93b2fabf1fa7fa8b88f2f8800f9a`.

## Scope and source identity

The implementation worker changed only the following four source files and this
new note. The coordinator owns the public/private declarations, host integration,
independent test execution and project records. Concurrent edits were preserved.

| File | First complete SHA256 |
| --- | --- |
| `src/core/countdown.cpp` | `4875714d84e2a1caff22c006dbf4e9d2cc389db9e9686346581181d1c0ede5e6` |
| `src/core/fsm_robot.cpp` | `2efd83e51ecdd6d213a5e97cd6e23cf9e7084d50fd4cf49fc8b202967827dfd8` |
| `src/app/runtime_inputs.cpp` | `fc1d095ab96f97fa4f81e3609bdd3108c39ed4b6b17639b4843e6d6f4e5cc4dc` |
| `src/hal/ui_display.cpp` | `496b5f289e5199f8aad6d01313befbd5d12401b65e3c3977397ac605c884991d` |

`Buttons::neutralStartArmed()` observes the existing initialized, armed,
unpressed, stable-NONE and candidate-NONE state. Controller and Lifecycle merely
forward it. No button sampling, qualification, state transition or timer changed.

`Robot::runLifecycle()` captures eligibility from the unchanged actual
`allow_start` expression and call, current explicit D087 observation, and actual
post-step neutral arming. The final result filters this through the final outputs,
Gate/menu state, selection-change flags, faults and line handover flags. Admission
clears the metadata through the existing `clearActions()` path, including passive
results; default construction clears reset results. All listed bench/evidence
profiles report false. Eligibility remains an observation and is never read by
control, recorder or permission logic.

`Runtime::projectStartStatus()` binds the display to its current fresh decision,
token and actual consumed application receipt through the existing receipt
predicate. Its ready projection additionally requires the contract's genuine
RUNNING, initialization, service, source, classified-line and ordinary-menu facts,
the actual fault-free zero/disabled inhibited-IDLE receipt, and an enabled mode.
It uses the existing observed `last_clock_us_`; it adds no clock read. M0 and every
listed nondefault profile withhold ready. The call stays at the existing display
projection point before render; native write order is unchanged.

The renderer extends only explicitly bound ordinary IDLE samples. It preserves
the original battery bar, adds the exact threshold marker at row6/column12, and
draws the contract's R masks `[6,5,6,5,5]` only on qualifying even blink pages.
Existing validity checks and all-clear conditions suppress inappropriate R
frames. Unbound samples retain the old render path and pixels.

## Approved mechanical extraction

To keep `runLifecycle()` under 60 lines, the coordinator approved and declared
private `Robot::finishLifecycle(const RobotInput&)`. Its call replaces the old
tail at exactly the same point, after the existing calibration and bias reporting.
The following entire tail moved without content or ordering changes:

```cpp
    result_.heading = input.imu.explicit_values ? heading_.step(
        HeadingSample{input.t_us, input.raw_heading_deg, input.imu.heading_available,
                      input.imu.heading_updated, input.imu.observation_us},
        result_.lifecycle.gate.go) : heading_.step(input.t_us, input.raw_heading_deg,
            input.imu_ok, result_.lifecycle.gate.go);
    if (result_.heading.fault) faults_ |= HEADING_CONTRACT;
    if (result_.lifecycle.gate.go) {
        attempt_go_ = true;
        timing_active_ = true;
    }
    tick_.permission = initialized_ && result_.lifecycle.gate.motion_permitted &&
        faults_ == 0U && !tick_.line_start_inhibited;
    if (faults_ != 0U || result_.lifecycle.gate.phase == countdown::Phase::STOPPED)
        tick_.selected = core::State::STOPPED;
    else if (!initialized_) tick_.selected = core::State::BOOT;
    else if (result_.lifecycle.gate.phase == countdown::Phase::HOLDING)
        tick_.selected = core::State::COUNTDOWN;
    else if (result_.lifecycle.gate.phase == countdown::Phase::IDLE)
        tick_.selected = core::State::IDLE;
    tick_.limit = limiter_.step(input.t_us);
```

A source-only comparison extracted the block from `git show HEAD:src/core/fsm_robot.cpp`
and the working file, bounded by its first heading assignment and final limiter
assignment. Exact text equality passed after newline normalization. This is
source comparison, not execution or a behavior-test result.

## Evidence and remaining work

`git diff --check` returned 0. The worker inspected the source diff and computed
the four hashes above, then sent them to the coordinator before execution.
The worker did not read new test bodies, execute tests, build, use the board,
change configuration/grants/native adapters, or commit. Independent frozen tests
and source review are still required; no test success is asserted here.

The added observation is before completion C and cannot prove tick completion or
future health. Terminal failure can retain the last physical frame. MATCH
Immediate startup versus native matrix initialization remains unresolved.
Source/ABI size and a separately authorized checked MATCH compilation remain
required before any new target-fit claim; earlier native span estimates do not
qualify this source. Optical, calibrated voltage, timing, deployment and physical
acceptance remain outside this implementation. No phase gate follows.
