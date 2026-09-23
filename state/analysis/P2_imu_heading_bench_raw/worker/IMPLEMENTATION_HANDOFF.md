# D111 implementation handoff

Implemented only `bench/imu_heading/imu_heading.ino`,
`src/imu_heading_bench.cpp`, `src/imu_heading_bench_native.cpp` and private
helpers/storage in the runner header. Native owns one Acquirer. Runner uses the
actual Estimator and countdown::Services, with the adopted timer-anchor exception;
there is no duplicate decoder, averaging algorithm or integrator.

The default sketch passes all-false grants. Setup/read release grids and frequent
single pending advances are bounded separately. Native result shape, wrapper clock
chronology, source brackets and pure diagnostics retain their ordered evidence.
Pending cancellation is one-shot; historical failed-clock inputs and unmeasured
late cleanup are not represented as current-time/timing success. Checkpoints and
measurement observations publish only after accepted C with no wrapper fault.

`first_source_freeze.json` and `first_sources/` preserve source/config bytes before
checks or fixes. No production fix was made after that snapshot. Current CPP:
`6d3c6c5f5234d995689cc265c65de7848e2bc2dd6b8fa0748e6b2f1cec8ce61f`.
The current runner header hash is
`bd63d529aa87ae907b00a6bcb62d502450ac577edd8e4651357ee9fea498d12a`.

`first_syntax.json` records strict C++17/Werror/no-exceptions/no-RTTI syntax PASS
for all three translation units under seven temporary profiles: unchanged config,
checkpoint count0/1, checkpoint period0, tick0, half-range deadline and poll cap0.
The Arduino clock was declaration-only; no native link or execution is claimed.
`first_function_lengths.json` records all definitions below60 lines. Source/config
hashes remained equal to the freeze after checks; diff whitespace check passed.

No independent test bodies were read and no board/hardware action occurred.
Independent executable tests, target/loader/startup audit and fresh review remain
with assigned owners. Physical mounting, calibration, drift/rotation, clock accuracy
and full-app WCET remain unqualified. This handoff is implementation plus syntax,
not a passed behavioral or hardware gate.
