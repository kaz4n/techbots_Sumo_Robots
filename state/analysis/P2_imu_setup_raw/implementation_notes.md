# D080 setup and coherent decoder implementation handoff

Objective: implement only the frozen finite MPU6050 setup and pure sensor-coordinate
motion decoder, plus an inert retained-method compile probe. No acquisition/freshness,
axis transform, bias, yaw, application integration or physical acceptance is implied.

Owned implementation: src/hal/imu.cpp. New probe files:
bench/p2_imu_setup_compile/p2_imu_setup_compile.ino;
bench/p2_imu_setup_compile/src/imu_setup_probe.h;
bench/p2_imu_setup_compile/src/imu_setup_probe.cpp.
No public/private header edits were needed. Shared config, contract, tests, build files,
ledgers and target actions remain with root or the independent author/reviewer.

Source: P2_imu_setup_contract.md/D080 and P2_mpu6050_sample_audit.md with retained
manufacturer register-layout/scaling evidence. The 48 fixed operations include begin;
each advance performs at most one concrete Bus operation. All waits return immediately,
use caller time and anchor to start or the selected successful write completion. Both
counts and the absolute deadline are checked; faults and completion are terminal.
No additional clock, callback transport, retries, heap, exceptions or RTTI are used.

Decoder success publishes signed big-endian accel/temperature/gyro in sensor coordinates,
fixed scaling, rail bits and bus observation timestamps. Status bit0 is diagnostic only.
Failure leaves every payload field zero. The unsigned word is converted via bounded
subtraction and signed32 negation, without an out-of-range signed16 conversion.

First frozen imu.cpp SHA256:
f38f0f2116f77534a9c812acd925c574d009fff8c3a521dd6af3c255f49e8a37.
Independent test author and root were notified before targeted verification.

Local targeted compile, 2026-09-23 Asia/Dubai:
Command: wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Werror -pedantic
-fno-exceptions -fno-rtti -fsyntax-only
/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/hal/imu.cpp
Exit status: 0. stdout/stderr combined by exec tool: empty (0 tokens).
Elapsed wall time: 6.3051128 seconds. This is syntax compilation, not linked execution.
Owned-file git diff --check: exit0, empty output.

Next action: independent scripted-Bus tests and review, then root's actual target
compile/source/ELF binding. Preserve any first failures before repairs. Physical power,
identity, settling, sample rate/freshness, clock qualification and whole-loop WCET remain
pending. The probe stores an unused exercise pointer; setup/loop perform no Bus operation.
Local function-length check: 12 functions; maximum32 lines; all below60. No source changes followed the frozen hash.

Bounded linked check using independent author's exact link inputs (assertion source
was not inspected), actual frozen imu.cpp; 2026-09-23 Asia/Dubai:
Command: wsl.exe --cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots
--exec g++ -std=c++17 -O1 -Wall -Wextra -Wpedantic -Werror -fno-exceptions
-fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS -I src -isystem host/third_party
tests/test_scaffold.cpp tests/test_imu_setup.cpp tests/support/imu_bus_fake.cpp
src/hal/imu.cpp -o /dev/shm/sumo-d080-implementation-check
Compiler exit0, stdout/stderr combined empty; wall time6.2750477s.
Execution: wsl.exe --exec /dev/shm/sumo-d080-implementation-check --no-colors
--test-case=*D080*
Execution exit0, wall time0.5039278s. Exact combined output:

[doctest] doctest version is "2.4.12"
[doctest] run with "--help" for options
===============================================================================
[doctest] test cases:      23 |      23 passed | 0 failed | 1 skipped
[doctest] assertions: 1549570 | 1549570 passed | 0 failed |
[doctest] Status: SUCCESS!

No production edit followed. Root separately reported actual target c45ffd3d,
44 source files,84132B program/34748B compiler memory and source/ELF collection
PASS. Full regression/sanitizer/variant/reviewer evidence remains parent-owned.
