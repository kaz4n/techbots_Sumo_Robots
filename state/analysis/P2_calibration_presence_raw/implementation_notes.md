# D083 countdown gyro admission implementation

2026-09-23 Asia/Dubai. Contract/header baseline `3c356ec`. Implementer owns only
`src/core/countdown.cpp` and this note; other authors own tests/review/evidence.

## Implementation and scope

`Services::admitGyro` selects legacy or explicit mode only for known in-window
presence values. Mode mixing and unknown values latch rejection without adding a
reading. Legacy finite/imu_ok behavior is preserved. ABSENT ignores gyro/source
fields; INVALID rejects; explicit VALID ignores the legacy heading-health bool.

`Services::admitExplicitGyro` checks finite gyro and unsigned delivery age first,
then source-time/sequence identity. Identical last observations are ignored;
conflicting, partially repeated, reversed or half-range identities reject without
replacing history. Valid distinct identities are committed even before the source
window; only observations inside both source and decision windows contribute.
Forward sequence gaps and uint32 wrap use modular subtraction without fabricating
readings. Both new helpers are under 60 lines and have no loops, clocks or I/O.

`observeCalibration` now gates its unchanged aggregation through admission. Its
mean/spread/minimum calculations and finish behavior are unchanged. Existing
`Services::step` owns all decision timing and closes the window before admission
at CAL_END. Its warning/snapshot/hold order and duplicate-decision behavior are
unchanged. Existing reset/start/cancel clear the new private fields through the
already-established value reset. Gate, Buttons, Controller, Lifecycle and Menu
were not edited. No header, config, test, app or ledger was edited by this author.

## Narrow implementer validation

Command executed:

```text
wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -fsyntax-only /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/core/countdown.cpp
```

Exit status 0; stdout/stderr empty; tool wall time 6.6638532 seconds.
`git diff --check -- src/core/countdown.cpp` produced no diagnostics. Inspected
diff contains only the admission helpers and aggregation entry gate (58 added,
3 removed lines). No runtime test was authored/read/run by this implementer;
independent contract tests, broader regressions, target compilation and fresh
review are coordinated by root. No hardware/MCU/upload action occurred.

Frozen production SHA256:
`09174efe38003245c635237bdd489454efc86b9ec1e65b089fcc167a2106eb7d`.

This establishes compilable source only, not tested runtime acceptance, physical
calibration, integration with Robot/HAL, full-tick timing or a phase gate. Remain
available for fixes supported by retained independent failures.
