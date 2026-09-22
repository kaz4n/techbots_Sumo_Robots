# P1 offline component validation — 2026-09-22

Authority: D-016 permits host development; D-017/D-018 approve the recorded
governor/order changes. Hardware disconnected. No gate, pin approval or motor-run
receipt. Results below are host/software evidence only.

## Commands and observed results

| Command | Result | Saved artifact |
|---|---|---|
| `wsl -d Ubuntu -- bash tools/test_host.sh` (reviewer) | exit 0; CTest 1/1; 77 cases, 3,457,564 assertions, all pass, none skipped | P1_core_tests.txt |
| `wsl -d Ubuntu -- g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -Wconversion -fno-exceptions -fno-rtti -fsyntax-only src/core/edge.cpp src/core/opp_fusion.cpp` (worker, before front-table addition) | exit 0; strict filter syntax | worker report; final front table also built by full suite |
| Same strict syntax flags with `src/core/governor.cpp` (coordinator) | exit 0 | coordinator tool output |
| `wsl -d Ubuntu -- cmake -S host -B build/host-sanitize -DCMAKE_BUILD_TYPE=Debug '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer' '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined'` | exit 0 | configured GNU 13.3.0 sanitizer build |
| `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2` | exit 0 | all four core .cpp and tests built |
| `wsl -d Ubuntu -- ctest --test-dir build/host-sanitize --output-on-failure` | exit 0; 77 cases and same 3,457,564 assertions; no sanitizer diagnostics | P1_sanitizer_tests.txt |
| `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` | exit 0; 46/46 pass in 17.910 s | P1_tool_tests.txt |
| Local Python `board_tool.source_hash(board_tool.stage(sketch))` for each P0 bench | matched both independently reviewed hashes | reviews/P1_components_codex.md |
| `git diff --check` | exit 0 | coordinator validation |

Environment: Windows PowerShell 7.6.6, WSL Ubuntu, GNU C++ 13.3.0, CMake 3.28.3,
Python 3.12.3, vendored doctest 2.4.12. No target command was attempted because
the board is disconnected and no SSH target is configured.

The test author read specs and headers only. Initial authored test compilation
needed explicit `<initializer_list>` and CHECK in place of REQUIRE because this
repository disables exceptions; all predicates were preserved. There were no
behavioral test failures to repair and no locked-test weakening. An early
Windows-mounted WSL incremental build emitted a filesystem clock-skew warning;
subsequent complete host and separate sanitizer builds passed. No WCET inference
is made from either host duration.

Status: IMPLEMENTED / HOST-TESTED for standalone components; SCRIPT-TESTED for
tool controls. NOT TARGET-COMPILED, not hardware/bench/ring tested. Full P1, R1 at
the MotorGate write boundary, R5 integrated arbitration, all table-row coverage,
fresh gate review, EXPLAINED OK and human gates remain incomplete.
