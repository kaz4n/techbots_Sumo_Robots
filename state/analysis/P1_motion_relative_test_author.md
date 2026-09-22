# P1 independent relative-turn test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: protect Turn.startRelative public contract 18414c0 and the existing
B7 behavior independently of implementation. Owned files are
`tests/test_motion_relative.cpp` and this report. Read motion.h and B7; AGENTS
was read earlier in this continuous session. No implementation cpp was read,
no existing files were edited, and no build or commit was performed.

Nine focused cases cover canonical (-180,180] relative bearings; +180 validity
and -180 rejection; finite initial yaw even without IMU; duty bounds; healthy
nonfinite yaw and unavailable-yaw fallback; exact +180 RIGHT ties at tiny,
ordinary and extreme finite actual origins; and nextafter samples immediately
below/at/above strict five-degree tolerance with origin +/-90 and opposite
relative bearing. Expectations use actual supplied float observations, not
test-side rounded replacement coordinates.

Timing cases cover initial/mid-turn loss, recovery without shortening/restarting,
remaining-angle fallback, exact/adjacent 120 ms and 700 ms endpoints, timeout
winning a target tie, and unsigned micros wrap. Ordinary absolute start and
reset clear relative coordinate/fallback state; their existing shortest-angle
behavior remains exercised.

A cross-mode regression also covers NaN/+infinity/-infinity advertised as healthy
after initial or mid-turn fallback is already latched: INVALID before expiry,
latched terminal retention, and TIMED_OUT winning at the exact original deadline
on a fresh command. Both ordinary absolute and relative entry APIs are tested.

Static handoff: nine cases, CHECK/CHECK_FALSE only, no trailing whitespace.
Parent owns host/sanitizer runtime evidence. These arithmetic observations do
not establish physical orientation resolution at huge float values, actual IMU
freshness, motor permission, HAL behavior or a phase gate. Next action: parent
reviews/runs the frozen tests and records verified results before committing.
