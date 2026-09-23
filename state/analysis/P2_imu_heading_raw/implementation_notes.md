# D082 concrete estimator implementation handoff

2026-09-23 Asia/Dubai. Objective: implement exactly the frozen D082 estimator over
D081 Sample, and an inert probe. No Acquirer/core/app/header/config/test changes,
physical mapping selection, clock/I/O, allocation, target execution or commit.

Owned files:
- src/hal/imu_heading.cpp
- bench/p2_imu_heading_compile/p2_imu_heading_compile.ino
- bench/p2_imu_heading_compile/src/imu_heading_probe.h
- bench/p2_imu_heading_compile/src/imu_heading_probe.cpp

The concrete estimator validates the confirmed proper signed permutation and
initial configuration/bias in contract order. It accepts only ordered, contiguous
Acquirer observations, tracks completion-time age independently of new presence,
and preserves double unwrapped yaw. The first observation anchors zero without
prehistory. Subsequent increments use the specified raw-endpoint trapezoidal rule
and current bias; a bias update changes only configuration until a later increment.

NO_NEW retains bounded-age heading with its original observation timestamp and
publishes no gyro/acceleration. The selected yaw gyro rail terminally faults;
horizontal acceleration rails independently invalidate only impact inputs. Faults
clear all observation/heading payload while retaining bias, accepted sequence and
last validated time. No GO or public reset is exposed, and initial sequence must1.
Raw arrays are not re-decoded; existing decoder/native phase validation is not
duplicated. No actual robot signed-axis mapping is encoded anywhere in this work.

Probe namespace imu_heading_probe has default estimator, zero/unconfirmed candidate
mounting, NOT_READY candidate sample and zero candidate bias. Setup only assigns
its unused volatile exercise pointer; loop is empty. The unused exercise retains
actual begin/observe/applyBias/report calls. These memory values are not physical
mounting or calibration evidence.

Frozen estimator CPP SHA256:
e314f57b78980993f782cf85aa48f0cd6ffadf1cb1ae99fb801c7981f1736411
Root and independent author were notified before tests; source is frozen pending
an actual preserved failing test/review finding. No private header change needed.

Narrow syntax check:
wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions
-fno-rtti -fsyntax-only
/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/hal/imu_heading.cpp
Exit0, combined stdout/stderr empty, wall time0.4936061s. No linked behavior was
executed by this agent. Owned git diff --check returned0/empty. Function-length
check returned0:16functions, maximum33lines, all below60.

Independent analytic/config/probe tests, root's actual compile/source/ELF review,
and a separate fresh reviewer remain pending. Completion-time integration and the
2000us gap are the D082 engineering policy, not sampling/drift/rotation accuracy.
D081 freshness inference, SC-AJ/F091 and physical mounting/rate/full-tick WCET gates
remain. The current combined core imu_ok still needs separate presence/heading/
acceleration routing before application integration.
