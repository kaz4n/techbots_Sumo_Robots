# P1 independent HeadingReference test author

Date: 2026-09-23, Asia/Dubai. P1 host-only under D-016.

Objective: protect B0/B3/B14 and D-059's raw-Fusion/match-motion coordinate split.
Owned files are `tests/test_heading_reference.cpp` and this report. Sources were
committed public contract fd40a5b, its pre-establishment precision clarifications,
the amended BEHAVIOR/DECISIONS text, public Fusion/motion/Search/countdown headers,
and P1_robot_heading_contract_audit.md. No implementation cpp was read, no existing
test/header/config/build/ledger was edited, and no build, hardware operation or
commit was performed by this author.

The 31 cases cover inert/pre-GO behavior, current-GO versus actual last-known
source/time, nominal pending origin without synthetic healthy evidence, first
recovery anchoring, later losses/recoveries without re-zero, and unwrapped signed
coordinates. Unavailable arbitrary payloads are ignored; healthy NaN/infinities,
including before GO, preserve finite last state and latch a reset-only fault.
Equal extreme finite raw values yield exact zero. The maximum representable
difference is accepted; an adjacent larger difference faults before narrowing.
Reset, repeated GO, changed duplicate GO/recovery samples and multiple micros
wraps protect origin provenance and one-call change pulses.

Projection cases separate current healthy world-bearing evidence from retained
world/inward evidence, which can be viewed while IMU is unavailable but requires
a resolved origin. Canonical input validation rejects -180/out-of-range/nonfinite
directional inputs without changing fault/freshness. Literal angle tables check
computed +/-180 ties, continuous headings and shifted retained bearings. Exact
large full-turn multiples preserve tiny +/-1e-6 bearings after reduction.

Two independent numerical regressions protect the clarified public contract.
Origin -1F and raw16777216F publish rounded float local16777216F, while the exact
double difference16777217 yields worldBearing(+15F)=152F. Origin -1e-6F with raw0F
and +180F yields a negative non-tie; both current/retained projections must return
nextafter(-180F,0F), preserving LEFT rather than incorrectly becoming +180 RIGHT.
Read-only invalid projections are compared against an unqueried control reference
to detect mutation, coordinate faults or changed duplicate-sample handling.

Bounded actual-component compositions exercise Gate cancellation/STOP without an
origin; constant raw720 across GO without fake stuck span; live raw candidate
age/span continuity at exact360/adjacent-above; reset-only Fusion faults surviving
GO/clears; unchanged raw phantom marker and expiry; and retained world timestamp
whose projection cannot renew Search's expired memory. The raw evidence remains
outside the heading helper. These fixtures are not full Robot transaction proof.

Motion compositions begin with genuinely unavailable IMU and nominal local zero.
Turn keeps its original180ms fallback despite recovered target heading; Search
keeps its720ms scan fallback, without a700ms short-turn cutoff; Straight retains
its original reference/250ms deadline; Arc credits no outage rotation and keeps
its original sweep/400ms timeout precedence. No executor is restarted at recovery.

Static handoff: 31 cases, CHECK/CHECK_FALSE only, no throwing checks/trailing
whitespace/diff-check errors, and all test/helper blocks below60 lines. The file
is frozen for coordinator normal/sanitizer builds and independent review. Runtime
validation remains pending; preserve independent expectations on failure.

Limits: no provider yaw continuity, physical orientation, sensor freshness, actual
HAL gyro integration/bias application, complete Robot/MotorGate arbitration,
full-loop WCET, motor permission or phase gate is established. Future Robot must
honor faults and evidence validity and preserve the raw-domain/one-observation
contract. Next action: coordinator runs/reviews the frozen suite and records the
actual test evidence before committing.
