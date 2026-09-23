# IMU heading bench (P2 B3)

The checked-in grants are false. Construction, setup and loop therefore perform
no clock or I2C operations. The future enabled bench uses one existing MPU6050
Acquirer, the actual heading Estimator and the actual calibration Services.
It contains no motor, button, ADC, matrix, application controller or transport
owner. MATCH and uploads are refused by the checked build route.

Compile only with the existing board connection settings:

```
python tools/board_tool.py flash bench/imu_heading --compile-only
python tools/board_tool.py flash bench/imu_heading --compile-only --startup immediate
```

After native setup, the finite trial performs the existing calibration window
and applies an accepted bias exactly once. The next updated heading anchors a
60-second source-time trial with 61 immutable checkpoints. Actual source times,
sequences, raw samples, headings, endpoint change, maximum excursion, missed
release counts, and wrapper timing remain available in fixed RAM. Checkpoints
use actual observations; there is no interpolation or second heading integrator.
Each poll makes at most one normal native operation, plus cancellation when a
wrapper fault may leave an acquisition pending. Limits stop further progress.

Setup readiness starts this bench's calibration timer; it is not a START event
or permission to move. Rejected calibration, invalid chronology, missed source
continuity or other faults terminate the trial. Pure/native diagnostic state
may reflect work completed before a rejected closing timestamp; only accepted
checkpoints count as successful evidence. A terminal bench stops callbacks and
does not claim that I2C power was disabled. One trial is allowed per boot.

Physical acceptance still requires verified supply, exclusive bus ownership,
mounting, stillness and clock, plus a reviewed capture method. The stillness
check uses actual elapsed time, endpoint drift and maximum observed excursion
against 2 degrees. A separately labelled hand-rotation run compares actual
signed delta to an externally confirmed +/-360 degrees within 3 degrees.
The firmware cannot establish how far the human turned the sensor. No attached
IMU, physical drift, 800us application WCET or phase gate is claimed by a host
test or target compilation. See state/analysis/P2_imu_heading_bench_contract.md.
