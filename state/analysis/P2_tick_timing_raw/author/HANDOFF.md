# D092 independent test-author handoff

2026-09-23. Objective: independently test the frozen whole-tick timing contract
against the actual Robot, MotorGate and AttemptRecorder public interfaces.

## Ownership and independence

New files only: `tests/test_tick_timing.cpp`,
`tests/fixtures/tick_timing_fixture.h`, and this `author/` evidence directory.
Expectations came from `P2_tick_timing_contract.md`, public headers and established
tests. No production implementation body was inspected. The compiler consumed
the actual implementation; the final production source was hashed only.
No existing test, configuration, ledger, hardware state or commit was changed.

## Result and reproduction

Both `MOTORS_ALLOWED=0` and `MOTORS_ALLOWED=1` independently compiled with g++
C++17, `-Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti`, and each
passed **22 cases / 487 assertions**. No author build or test failed. The initial
21-case / 453-assertion passing receipts remain alongside the final receipts.

PowerShell command:

```
wsl.exe -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_tick_timing_raw/author/run_targeted.py
```

The runner builds only the new independent test, host test entry point, actual
core sources and the three required HAL sources into `/tmp/sumox_d092_author`.
Every exact compiler/test argv, exit code, stdout and stderr is in
`20260923T134845064934Z.json`. Source identities are in the neighboring
`20260923T134845064934Z_source_hashes.json`.

## Coverage

| Cases | Frozen contract evidence |
|---|---|
| 1-3 | Acquisition600 + later401 =1001; 799/800/801/999/1000/1001; equality and adjacent chronology boundaries |
| 4-7 | Missing/inconsistent duration; backward/future/overlapping chronology; invalid current and pending start; common-anchor half-range minus1/exact/plus1; largest unambiguous duration |
| 8-12 | Natural wrap and warning-before-STOP ordering; legacy ignored fields; fixed-mode mismatch/recovery; BOOT selection; duplicate input cannot recount or replace metadata |
| 13-14 | Wrong/stale tokens and invalid application times remain motor faults; invalid duty with valid identity/time still counts timing |
| 15-18 | PreGO exclusion and GO acquisition inclusion; STOP suppresses GO at deadline; cancellation nonmembership; accepted START after cancellation preserves lifetime selector |
| 19 | Explicit fresh IMU evidence between acquisition and decision; retained source age stays decision-based |
| 20 | Full maxima65535/65536 and existing packed-field clamp/loss behavior |
| 21 | Actual Robot -> MotorGate fake callbacks -> AttemptRecorder; real feedback; final STOP acquisition1400 + remaining25 =1425 dominates final packed frame and sealed summary; no later recount |
| 22 | Reset clears timing selection/pending metadata, keeps token monotonicity and external recorder evidence; subsequent legacy attempt counts correctly |

## Tested identities

| File | SHA-256 |
|---|---|
| tests/test_tick_timing.cpp | 82800781a308c4ef5e3cfc9b1fcdde928203bb6dfb10132d85b64ca173bb3227 |
| tests/fixtures/tick_timing_fixture.h | de2037f7028ff1d95a65a330094925689385a070bde3fa31530e27934670b52f |
| src/core/fsm.h | 4f7f1400dead7b71b978a439f9054e48b025d298fafd0e94a24c29de2fcb5454 |
| src/core/fsm_robot.cpp | 0e1ddb2057e0cc412529c2c8f1d77e1519edc5243847c0950fc6cda07e9f4e2d |
| state/analysis/P2_tick_timing_contract.md | 60cdbd039cb3437e90c761f1d3fc3fce1c456b93ba05edcc34e13c16aa034697 |

These are synthetic host clocks and callbacks, proving accounting and public
composition only. They do not prove physical timing, calibrated clocks, acquired
sensors, real motor behavior, scheduler fit or under800us WCET. Root owns the
full ordinary/enabled suites, sanitizers and target compile-only validation;
the separate reviewer owns fresh source review. No further author edits planned.
