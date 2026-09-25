# D169 inert diagnostic activation review

2026-09-25, Asia/Dubai. Separate fresh-context, same-model, review-only agent; no cross-model claim.
Reviewed D169/activation contract, implementation32b2d9d4 and corrected expectations84b3fbaf.
Read AGENTS.md, safety-auditor role, handoff, current phase/schedule and diagnostic public contracts.

BLOCKER: none in this bounded change.
MAJOR: none open.
MINOR: none open.

- src/config.h:34-44 defaults the selector to0, admits only0/1, and requires MATCH0/MOTORS_ALLOWED0 plus all seven other profiles0 when active; existing assertions, values and pins remain unchanged.
- bench/motor_fault/motor_fault.ino:12 selects only the existing grant; construction and active-only loop are unchanged. The build choice supplies no physical ownership evidence or run permission.
- tools/app_build_policy.py:81-87 and125-126 admit exactly the two documented motor_fault strings. Other projects retain their prior admission, with default startup/dynamic linking and equal C/C++ flags still checked.
- bench/motor_fault/src/motor_fault.cpp:94-109 retains EN-high/nonzero-PWM refusal; native MotorGate/Runner/Trace bodies and150us limit are unchanged. No dynamic input, network, motion, upload-allowlist or staging-helper path was added.
- RESOLVED pre-execution MAJOR: draft0c140362 tests/tooling/test_motor_fault_activation.py:291-292 mistook project selection for complete flag validation and named recorder_inert.ino. The original fd03b1c0 draft remains preserved and unexecuted; corrected a727bdc8 tests use all17 actual alternative profiles with valid controls and full-validator refusals.

Source SHA256 prefixes: config9236d831; sketch25e366c0; policyadc7f42a; companiona727bdc8.
Independently recomputed all63 pins in analysis/P7_motor_fault_raw/activation_freeze.json: zero mismatches.
Inspected root-executed activation_first.json:13/13 new methods PASS on first actual execution.
Inspected root-executed activation_regressions.json:29/29 existing macro/policy/executor methods and3/3 diagnostic driver methods PASS; normal and ASan/UBSan each18 cases/2570 assertions, zero skipped.
Reviewer ran no tests/compiler/board commands; only source, fixture, receipt and local hash checks. Full host suite was not rerun in this review; scoped regressions above are the evidence.
Existing tests/assertions and consumed receipts were not changed; this scope does not touch the policy-denied stage. No target compile/upload/reset/capture or motor-capable run is established.
Active artifact binding, separately identified inert capture, original fault attribution, physical acceptance, WCET and human gates remain pending.

Verdict: PASS for D169 source and inspected host evidence only. Next action: prepare fresh active-image compile/artifact scope without reusing consumed native scopes or deleting the retained stage.
