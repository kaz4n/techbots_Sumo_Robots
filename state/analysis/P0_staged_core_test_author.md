# P0/P1 independent staged-core include regression

Date: 2026-09-22, Asia/Dubai.

Objective: reproduce the target-stage include-resolution failure before the
coordinator's source-only repair. Owned files are
`tests/tooling/test_staged_core.py` and this report. Production core sources
were copied and compiled opaquely; no implementation source was inspected.
The existing ToolContractTests fixture is instantiated for setup/helpers only,
not inherited, so its established cases are neither edited nor duplicated.

Each new case calls the public compile-only entry point with fake SSH/CLI
transports, staging the actual project src and inert timing sketch. Every staged
core cpp is then syntax-compiled with g++ C++17, warnings-as-errors, exceptions
and RTTI disabled, and no project-root -I/-iquote options. Every staged public
header is separately included into a one-include translation unit under the same
flags. CPATH/CPLUS_INCLUDE_PATH/C_INCLUDE_PATH/OBJC_INCLUDE_PATH are removed from
the compilation environment so environmental search paths cannot hide the bug.

## Red receipt, before coordinator repair

```text
wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -p test_staged_core.py -v
Ran 2 tests in 1.599s
FAILED (failures=10)
Process exit: 1
```

Both staging operations succeeded under the command substitutes. Independent
compiler failures were:

| Staged file | Missing include reported by compiler |
|---|---|
| src/core/edge.cpp | core/motion.h, through edge.h |
| src/core/fsm.cpp | core/fsm.h |
| src/core/logframe.cpp | config.h, through logframe.h |
| src/core/openers.cpp | core/openers.h |
| src/core/stall.cpp | core/stall.h |
| src/core/edge.h | core/motion.h |
| src/core/fsm.h | core/motion.h |
| src/core/logframe.h | config.h |
| src/core/openers.h | core/motion.h |
| src/core/stall.h | config.h |

The failing tests and expectations are frozen for the coordinator's include
repair. No existing tests, headers, core source, config, manifest or ledger were
edited by this author. No board command, upload or commit occurred. This proves
host compiler reproduction in the actual staged layout; it is not an Arduino
target-build pass, linker check or physical validation. Next action: coordinator
fixes relative includes and runs the same unchanged tests, then separately repeats
the authorized real target compile before considering upload.
