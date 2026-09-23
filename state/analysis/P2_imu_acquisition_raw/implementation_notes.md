# D081 native acquisition and owned Acquirer implementation

Objective: add only the frozen one-budget status/STOP/motion acquisition and its
owned setup/sample/silence lifecycle. No core/app changes, calibration, mounting,
bias, heading, hardware execution or phase acceptance are part of this task.

Owned files: src/hal/imu_bus_unoq.cpp; new src/hal/imu_acquisition.cpp;
bench/p2_imu_acquisition_compile/p2_imu_acquisition_compile.ino and
src/imu_acquisition_probe.h/.cpp inside that probe. Header/config/test/CMake/ledger
changes belong to root or independent agents; none were edited by this author.

The original transaction body now takes an existing private Operation. D079 public
single-request wrappers still construct one Operation and invoke that unchanged
body. acquireMotion constructs one Operation for a checked1-byte0x3A read, full
STOP/idle acceptance, and conditional15-byte0x3A motion burst. Both phases share
one600us/8192 budget; there is no reset/retry or second cleanup. Both MPU status
bytes remain separate diagnostic metadata, never native error flags.

Acquirer owns its concrete Bus and Setup. It arms once at checked setup completion,
validates shape/time/phase metadata, and returns NO_NEW without an old payload or
sequence advance. Accepted decoded observations reset the observed20ms silence
anchor. Any runtime fault clears payload/phase/gap fields and latches the identical
failure until reset. The adopted freshness inference remains conditional on the
manufacturer shadow/read-clear model and sole-owner/profile/no-reset premises.

First frozen production hashes:
imu_bus_unoq.cpp 1955d95c5e523e1538aaa44c1aa72bfc79398937245a0b573dc7285796a00603
imu_acquisition.cpp 6dd161d0f4837ecb0c0b2874b1d7a7ddff6228c79c786ae69c2ff6890eabb4ed
Root and independent author were notified before execution. No new native API,
CMSIS/LL identifier, DT metadata or private header declaration was needed.

Targeted syntax command, 2026-09-23 Asia/Dubai:
wsl.exe --exec g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions
-fno-rtti -fsyntax-only
/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/src/hal/imu_acquisition.cpp
Exit0; combined stdout/stderr empty; wall time6.7492098s. This is syntax-only,
not linked native execution. Owned git diff --check returned0 with empty output.
A source function-length check counted45 functions across both files, max39lines,
all below60. Its first shell wrapper failed on PowerShell quote parsing before
Python executed (?:bool and ] treated as command names); stdin here-string repair
passed exit0. No production source was changed by either check.

Next: independent native D081 and existing D079 executions, direct scripted-Bus
Acquirer tests, root's actual compile/source/ELF evidence and separate review.
The198-clock slow timing corner exceeds600us, so a slow compound transaction
must fail; there is no new physical800us tick or healthy sample-rate claim.
