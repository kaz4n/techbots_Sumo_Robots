# D095 halt implementation worker evidence

Implemented only `src/hal/motors.cpp`; the frozen header already supplied all private state.

- First halt latches and disarms; before begin attempt it performs no clock or port I/O and selects NOT_INITIALIZED only if no prior fault exists.
- After begin attempt it selects STOPPED only without an earlier cause, brackets exactly one existing inhibition pass, retains its acknowledgement and forward-half-range timing, and preserves the first diagnostic.
- Repeated halt changes only the returned fresh pulse; no clock or backend calls.
- Successful existing reset clears the halt cache; failed reset preserves it. Existing begin/apply paths are unchanged.

Validation, all local host-only with UBSan:

| Check | Result |
|---|---|
| Unchanged locked MotorGate, MOTORS_ALLOWED=0 | PASS 37 cases / 3993226 assertions |
| Unchanged locked MotorGate, MOTORS_ALLOWED=1 | PASS 37 cases / 3796846 assertions |
| Existing actual native port contract, MOTORS_ALLOWED=0 | PASS 38 cases / 108417 assertions |
| Existing actual native port contract, MOTORS_ALLOWED=1 | PASS 38 cases / 108603 assertions |
| git diff --check for motors.cpp | PASS |

Exact commands and output: compile_gate_0.json, run_gate_0.json, compile_gate_1.json, run_gate_1.json, native_regression.json, and native/*.json. Reproducer: run_regressions.py. No compiler/test failures. Initial read-only inspection attempted a nonexistent test_motor_native.py path; corrected by file search to test_motor_port_unoq.py, without edits or execution of the nonexistent path.

No header/config/established test edits, commit, hardware command, upload, motor run or physical evidence. Independent new halt tests and aggregate integration checks are parent-owned next work.
