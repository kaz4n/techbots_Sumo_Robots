# D-060 production Robot implementation receipt - 2026-09-23

Objective: implement the actual production `fsm::Robot` transaction from the
committed public API/D-060 contract, reusing the existing behavior components.
This is implementation and syntax evidence, not a runtime review or gate pass.

## Owned changes and initial source freeze

- `src/core/fsm_robot.cpp`: new complete production implementation, 862 lines,
  49 functions; longest function 38 lines (`Robot::runLifecycle`).
- `src/core/fsm.h`: only Robot's private helper/member section; fixed ownership
  of existing components, one pending application/frame slot, bounded histories.
- This receipt only. Public APIs, existing implementation files, configuration,
  build files, tests and shared ledgers were not edited by this worker.

Frozen SHA-256:

```text
src/core/fsm_robot.cpp
c43bbb2f0255c01e2c41a241de3347efde7b56e0c706aa46d6e77dbbea22547b
src/core/fsm.h
8e8c42556e6a06550a2147e0bd3dba666b1e53a8a8817679847264456b1f9b7d
```

## Implemented composition

- Distinct-timestamp admission/nonzero monotonic tokens, duplicate pulse clearing,
  reset preserving the next token and explicit exhausted-token inhibition.
- Actual prior receipt identity/time/enable/sign/magnitude checks; optional
  consistent duration evidence counted only for GO-through-final-stop members.
  Missing application inhibits; missing/malformed timing only marks incompleteness.
- One raw-line classification and raw-yaw Fusion observation on fresh data; stale
  data never feed Classifier/Fusion/Escape. Known input/receipt faults reach
  Lifecycle STOP before countdown services can process the stale tick.
- Actual Lifecycle/menu/running-mode composition and D-059 GO/recovery coordinates.
  Accepted calibration publishes its bias once; no HAL reset or implicit motion
  service action. All six openers are routed through existing executors.
- Persistent-edge and Escape fault precedence; then re-flank/opener/normal routing.
  Current-perception qualification on exits, immediate loss/escape-exit brake,
  deferred executor capture at the next current observation, bounded defend-timeout
  SEARCH entry and scan-hint lifetime. No recursive routing or unbounded loop.
- One candidate Detector observation using preceding actual duties, at most one
  limiter admission, and actual SWING-entry history. Final request rejection
  conditions are checked before one final Fusion commit and one Governor call.
  Only committed contact supplies permission; unexpected governor contract failure
  immediately disables outputs and is latched without a second commit/pass.
- Bounded world/front/inward/edge history; raw-coordinate retention and D-059
  projection; exclusive-side evidence from the whole completed escape episode.
- IMU/battery/QTR/calibration/stuck/escape/core/timeout diagnostics. QTR warning
  qualification breaks on stale observations and uses actual reported pivot duty;
  warning-only conditions retain their prescribed non-veto behavior.
- Ordered bounded metadata events, matched FIRST_NONZERO and timing extensions,
  match-world PHANTOM_SET and explicit semantic loss. Shared metadata validation/
  append helpers remain coordinator-owned; this worker uses their public contract.
- Phase-anchored frame cadence, skipped-slot accounting, one pending frame,
  next-receipt actual duty binding, codec status/incomplete evidence and one final
  stopping candidate. Raw pre-bias gyro is recorded directly as clarified by root;
  release-only previous_bias is never reused as a live correction input.

## Checks and limits

Final command, exit 0 with no diagnostics:

```text
wsl --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -fsyntax-only /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/core/fsm_robot.cpp
```

Scoped `git diff --check` passed. A bounded brace/definition scan found the maximum
38-line function above. The first syntax pass failed on aggregate assignment of
EventBatch and enum/non-enum conditional warnings; these were fixed by explicit
`logframe::EventBatch{}` assignment and enum-bit accumulation. Both later strict
syntax checks passed. No predicate was weakened to resolve those compile errors.

No existing opponent/FSM/motion implementation or test fixtures were read to
derive behavior. No tests, link/build directories, board command, motor action or
commit were run by this worker. No D-060 item is intentionally left as a stub;
correctness remains subject to the coordinator's real Robot tests and independent
review. App/HAL acquisition and applied-duty evidence, external recorder storage/
transport, physical behavior and target WCET remain outside this source task.

Next action: compile/link with the coordinator-owned metadata helpers, run the
independent actual-Robot suite plus established regressions/sanitizers, resolve
findings without editing locked predicates, and record the resulting frozen hashes
and review evidence before any completion/gate claim.
