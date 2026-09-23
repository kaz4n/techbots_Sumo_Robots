# D103 independent test coverage and explicit limits

Objective: exercise the frozen optional local service reset through actual public
Runtime/Transaction/Robot/MotorGate/AttemptRecorder ownership. Tests are derived
from D103/D095/D096/D101 and existing source-evidence contracts. No implementation
`.cpp` body was opened. No private-access macro, owner mutation, fabricated motor
receipt, token seed, direct Runtime Robot reset, hardware action or commit used.

Owned deliverables: `tests/test_app_service_reset.cpp`, the two new
`tests/fixtures/app_service_reset/` files, and this author evidence directory.
The parent separately owns build-list integration, full regressions, target
compilation/memory audits, shared ledgers and final review.

| Contract group | Observable coverage |
|---|---|
| Defaults | Public flag/report/display defaults; real enabled and default-off STOP/tail; off has zero terminal callbacks/clocks. |
| Guard phases/history | NOT_INITIALIZED/IDLE/ACQUIRING/DECIDED/FAULT; one STOP/old SEALED not sufficient; genuine two completed STOPs; wrong calls preserve owners; once-only latch. |
| Recorder lifecycle | Real EMPTY, RECORDING, DRAINING, SEALED; actual abort while RECORDING/DRAINING gives INTERRUPTED; payload, status/loss/summary serialized before/after unchanged. |
| Actual motor authority | Both compiled motor policies; STOPPED consumed valid matching zero/disabled receipt; same native setup counts, no new high/nonzero writes; failed inhibited write terminates observation/service and cancels transfer once. |
| Honest stopped perception | Genuine CONTROL and expired/fault line evidence, LINE_CONTRACT retained; real current A1/opponents continue; early calls have no sensor callbacks. |
| Gesture stages | Held MODE cannot skip neutral; neutral/MODE/release source completion boundaries19999/20000/20001us; long deadline actual MODE completion; release-first equality; early release/START/BOTH/release contamination; no underflow from qualifying source before its decision. |
| Invalid observations | Actual ADC conversion failure, replayed callback sample, unknown raw A1, eventual battery-owner failure cannot create reset; old native faults are not cleared. |
| Pending expiry/continuity | Real release source start; S ages4999/5000/5001; source and independent D gap each<=5000; exact D5000/5001 with real A0 work; late first A1 after accepted reset terminal/no C; natural uint32 wrap. |
| Reset ordering/faults | Completed original C before next real S; bad original C, preopen clock and actual post-reset clock; genuine token continuity, UNKNOWN reset cause, fresh pulse even after post-reset failure; passive call clears pulses. |
| Permanent service projection | First service input canonical RAW/CALIBRATION ABSENT line and explicit unavailable IMU; real retained ADC/opponents/battery prerequisites; old source diagnostics and actual nondefault committed350us QTR bank retained; no new QTR/IMU acquisition/setup. |
| Unavailable actions/display | Genuine QTR_CAL/DRIVE_TEST menu/request/token retained; app-owned UNAVAILABLE pulse; prior calibration report/bank unchanged; C/cross matches existing cross region; actual submitted Runtime frame compared; SENSOR_VIEW shows current opponents and absent lines. |
| No rearm/second reset | START held across reset; all six mode selections/START attempts stay IDLE and inhibited; second BOTH STOP gives one CONTROL/ABSENT tail then permanent callback/clock passivity. |
| Actual postmatch transport | Actual GO -> STOP -> real tail/SEALED -> real reset gesture -> BOOT/IDLE/menu/LOG_DUMP; same recorder; exact raw CSV/status/loss/summary, session/epoch/CRC via strict byte-fragment receiver and offline capture publication. |
| Native poison preservation | POISONED setup callback retained across logical reset and genuine request; one native setup, no readiness/write/reconstruction; actual native UART not executed by this fixture. |

Bounded limitations: no practical public path drives2^64 token increments to
terminal exhaustion. Transaction exposes no mutable recorder or Gate, so a
healthy Transaction with forged INTERRUPTED/exhausted evidence, altered receipts,
or external Gate reset cannot be manufactured; source review and established
owner tests cover these exclusions. A genuine abort interrupts evidence and
terminally faults Transaction, which is tested. An active Transfer cannot coexist
with the specified qualified STOP history via genuine Runtime input; its reset
notification ordering is source-review territory, while actual active transfer
cancellation on failed inhibition is exercised. Tests establish software
chronology and retention only, not physical grants, A1 wiring, loaded RAM/stack,
native UART behavior, target800us WCET or a human phase gate.

Final result receipts are recorded separately after all profile runs complete;
all exploratory failures and oracle corrections remain append-only.
