# D084 heading and evidence consumer implementation

2026-09-23 Asia/Dubai. Frozen contract/header baseline `aef3be2`.
Owned source changes: HeadingReference section of `src/core/fsm.cpp`,
`src/core/opp_fusion.cpp`, and the fresh-inward predicate in `src/core/edge.cpp`.
Root owns all shared interfaces, Robot admission/routing, recording and adapter.

## Implemented behavior

- HeadingReference's existing bool entry delegates to a common advance helper,
  supplying each healthy legacy tick as a fresh event-time source and bypassing
  the new explicit source cutoff/order checks. Existing projection checks and
  finite fallback/fault behavior remain. Typed input checks availability/update
  consistency, finite yaw, delivery age, forward source time and exact retained
  identity. Only fresh accepted input replaces history. Source age accumulates
  on every distinct tick, including unavailable ticks, and saturates at uint32
  maximum; modular timestamp reuse cannot revive old retained history.
- Fresh GO records CURRENT_GO at source time; retained GO records LAST_KNOWN at
  the original history time; unavailable GO preserves last-known or nominal
  pending behavior. First fresh recovery resolves pending origin at source time.
  Duplicate decisions clear only origin/update pulses. Fresh-match update pulses
  are false before GO, while retained usable heading remains available afterward.
- Fusion separately routes explicit acceleration validity to impact detection,
  fresh-heading status to stuck/phantom evidence, and actual source time to world
  bearing memory. Legacy Fusion uses event time as heading source time. Electrical
  debounce, visual contact counters and one-observation/commit behavior are intact.
- Stuck candidates require fresh heading to start or expand extrema. Existing
  candidates age on retained available ticks and can declare using already-seen
  span; unavailable heading or cleared bits reset undeclared candidates. Phantom
  creation requires fresh heading; retained available heading still masks against
  an existing marker. Marker event age and heading-source time remain separate.
- BearingMemory's new overload stores heading source time in the current view and
  world memory while preserving opponent event time. Its old overload uses event
  time. Escape exit emits inward evidence only with fresh healthy finite heading;
  row motion continues to use available heading under the unchanged rules.

No header/config/app/test/ledger, Gate, lifecycle or other fsm.cpp section was
edited by this author. No dynamic allocation, clock, I/O or new unbounded work.
HeadingReference's longest function is 52 lines, including its signature/braces.

## Narrow compile evidence and limits

Executed command:

```text
wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -fsyntax-only /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/core/fsm.cpp /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/core/opp_fusion.cpp /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/core/edge.cpp
```

Exit 0, stdout/stderr empty, tool wall time 7.2633793 seconds. Owned-source
`git diff --check` produced no diagnostics. No tests were inspected, authored or
executed by this implementer; root coordinates independent runtime tests, full
regressions, target compilation and fresh read-only review. These narrow checks
do not prove runtime behavior, physical heading, integration timing or a gate.
No board/MCU/upload action and no commit were performed.

Frozen SHA256 values:

```text
src/core/fsm.cpp        cad394ff8ee7f9072a8596a566092e2f3b9fadfda5966170e3d126ea18c71bb0
src/core/opp_fusion.cpp 693cfa4e900783d0d7bff7995623862f67296e7223b9c31157cbf620bc316d85
src/core/edge.cpp       de5a0f2337c3609812feaea4728675e3d99f46901eb843313bb2aa6a795f9321
```

Source is frozen pending independent findings. Any necessary repair must preserve
the original failure evidence and leave other authors' owned files untouched.

## Inert integration compile probe

Separately authorized ownership added `bench/p2_imu_integration_compile/` only;
the production sources above remain unchanged. Namespace `imu_integration_probe`
exposes memory-only Estimator/Robot/candidate inputs, an exercise counter and a
volatile `Result (*)()` entry. Candidate mounting remains default unconfirmed.
`setup()` only assigns the address of `exercise`; `loop()` is empty. There is no
MOTORS_ALLOWED branch, hardware driver, clock, Bus object or constructor I/O.

The never-startup-called exercise function retains actual Estimator begin/observe,
applyEstimate, Robot::step, conditional accepted-bias application, a second Robot
call with a disabled zero-duty identity/time-matched compile-fixture receipt,
and the actual frame codec. The synthetic receipt is not physical application
evidence. Robot's production pending-frame path remains reachable through step;
no additional RAM recorder owner is allocated. All probe functions are under
60 lines. Its public header/interface was sent directly to the independent author
for default and MOTORS_ALLOWED=1 inert startup/10000-loop and upload-refusal tests.
No upload manifest or tooling was edited by this author.

Narrow probe command:

```text
wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -fsyntax-only -I /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/bench/p2_imu_integration_compile/src/imu_integration_probe.cpp
```

Compiler exit 0 with empty output. Tool call wall time 6.2433934 seconds includes
the subsequent hash listing. This is CPP syntax evidence only; author startup
tests and root's actual target/ELF collection remain separate evidence.

Frozen probe SHA256 values (paths relative to the new probe directory):

```text
p2_imu_integration_compile.ino b53fa54c7136db83cb1114766f0af677ee1aa058428b636933be8eeca5f7306e
src/imu_integration_probe.h   687fd1b2f22b33f8fdb91b11d529ef8e05900463a5c48a03b7801e39e7705bce
src/imu_integration_probe.cpp d203510e03b7403b1ddfc05dd9126c6c5a632c7283b5e388aedfccbcb8a4ba1e
```
