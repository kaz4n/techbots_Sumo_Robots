# Initial worker command failures

2026-09-23 D094 Acquirer worker; all commands were host-only. No source assertion
or production behavior was changed in response to these harness failures.

The first attempted async-suite compilation ran while its independently owned
test file was still being prepared. Command:

```
wsl --exec g++ -std=c++17 -O1 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS -I src -I tests -isystem host/third_party tests/test_imu_resume.cpp tests/native_imu_bus/test_main.cc tests/support/imu_bus_fake.cpp tests/support/imu_acquisition_fake.cpp tests/support/imu_resume_fake.cpp src/hal/imu.cpp src/hal/imu_acquisition.cpp src/hal/imu_acquisition_async.cpp src/hal/imu_heading.cpp -o /tmp/sumo-d094-acquirer-async
```

It exited1. The complete output is in the tool transcript; representative errors:

```
tests/test_imu_resume.cpp:46:5: error: static assertion failed: Exceptions are disabled! Use DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS if you want to compile with exceptions disabled.
tests/test_imu_resume.cpp:71:25: error: loop variable 'p' creates a copy from type 'const imu::SampleProgress' [-Werror=range-loop-construct]
cc1plus: all warnings being treated as errors
```

The same unsupported REQUIRE macro appeared at additional locations and the
range-loop error at88/128. The independent author was notified and owns changes
to the new tests. This provisional command also lacked the complete Robot
integration link dependencies; no successful async-suite result is claimed here.

Four legacy tooling methods initially passed with receipt directory
`/tmp/sumo-d094-acquirer-legacy`. A later WSL copy of that directory failed with
`FileNotFoundError`; those temporary receipts could not be retained. The checks
were repeated with a workspace-owned receipt directory via run_checks.py.
