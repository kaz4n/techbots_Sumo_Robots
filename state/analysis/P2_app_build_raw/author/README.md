# D099 independent test-author evidence

Objective: derive strict parser and public compile-command tests from the D099
contract and pinned CLI schema without reading either production implementation.
The author read AGENTS.md, .claude/agents/test-author.md, schedule/state/decisions,
P2_app_build_contract.md, P2_bridge_dependency_audit.md and captured installed
boards/platform evidence. Public validator and transport-protocol clarification
came from the coordinator. Neither tools/board_tool.py nor
tools/app_build_policy.py was opened or inspected by this author.

Modified files are only the new tests/tooling/test_app_build_policy.py,
tests/fixtures/app_build_policy/* and this author evidence directory. Existing
assertions, firmware/source/config, locked tests and shared state were not edited.
Another agent owns the separately documented established transport adaptation.

## Final result

`final.json`, `final.stdout.txt` and `final.stderr.txt` preserve the exact final
host command and result: **29 unittest methods PASS, exit0, 12.996 seconds**.
There are 18 parser methods and 11 public-command methods. Mutations exercise
strict JSON/envelope/types/duplicates/nonfinite values, zero external libraries,
required identity/properties, all three safety/startup configurations, upload
guards before target lookup, no arbitrary flag options, unchanged bench command
shape, fresh paths, CLI/core mismatch, injected compile-result rejection,
nonzero process rejection despite success JSON, exact separate stdout/stderr
retention and exit43, all three ELFs/package/18 installed hash requests, and
changed/missing/malformed/empty/reordered/extra/wrong-path hash evidence.

Every command test uses synthetic SSH/CLI/hash executables in a temporary root.
No actual compiler, board/network request, MCU operation, upload, reset, motor
action or commit occurred in this author's task. Passing host tests establish
neither hardware identity nor the validity of a target build or human phase gate.

## Preserved first-run failures and corrections

- `initial.stderr.txt`: all18 parser methods passed. App compile tests stopped
  at old synthetic CLI version-command exit94, before the separate transport
  fixture adaptation. Uploads already rejected before transport; an unsupported
  test-only expectation that the diagnostic contain literal `app` was removed.
  The contract requires a meaningful rejection, not that exact word. The early
  nested PowerShell/WSL status wrapper also failed to preserve shell status;
  `initial.exit.txt` is not a usable return-code receipt. Its raw output remains.
- `injected.json`/stdout/stderr:28 methods with two failed subcases. The author's
  fault wrapper incorrectly assumed pins and artifacts arrive in separate hash
  calls, so changed/missing-pin mutations did not fire for combined batches.
  Row selection was corrected to the documented fixture absolute paths;
  production code and acceptance assertions were not changed for this correction.
- `run_tests.py` now captures WSL process output/returncode directly through
  Windows Python, avoiding the initial nested-shell status ambiguity.

## Deferred evidence and next action

`SumoPolicyFixture/` and `phase_probe/` are local phase-independent external-library
fixtures only. No empirical macro0/macro1 library-resolution experiment was run.
The user requested a pause after current local work. Stop now; the coordinator
must retain the partial target status and schedule any outstanding actual modes,
library experiment, dependency/startup audits and fresh review only after resume.

After this final pass, the coordinator reported a separate review MAJOR: modified
effective recipe.cpp.o.pattern/compiler.cpp.cmd/prebuild properties can pass the
current checks while a platform.local override leaves pinned platform.txt bytes
unchanged. These29 tests do not cover that gap and their PASS does not resolve it.
D099 remains WIP/adoption pending. Per the pause instruction, no additional tests
or production fix were made; effective-command/local-override regression tests
and validation are the first stated resume task.
