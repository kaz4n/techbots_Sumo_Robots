# D094 compile-only resumable IMU probe

`python tools/board_tool.py flash bench/p2_imu_resume_compile --compile-only`
builds on board Linux with the configured transport. No upload allowlist entry
exists. Sketch setup stores a pointer; its loop is empty. Constructors are passive.

The never-invoked exercise retains actual native resumable/legacy acquisition,
Estimator, IMU projection, Robot, native MotorGate and AttemptRecorder. Only a
completion pulse enters Estimator; pending carries no measurement. Mounting and
power confirmation are caller parameters, not verified physical facts. The probe
does not define an app cache or scheduling policy and must not run as a sensor test.

Host substitutes and exact target source/ELF inspection are separate evidence.
Compilation proves neither MPU6050 behavior, physical mounting, source cadence,
full 800 us timing, loaded RAM, motor measurements nor a phase gate.
