# D169 inert activation profile

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED.

Commit32b2d9d4 adds SUMOX_MOTOR_FAULT_PROBE, default0, in config.h. Only0/1 is
accepted. Activation requires inert flags and excludes all seven other profiles.
The same sketch passes the selected boolean to its existing Runner grant. Trace,
Runner, native MotorGate, its150us limit, every existing config value and all
existing tests remain unchanged. Checked policy admits the new exact flag tuple
only for motor_fault.ino with default startup/dynamic linking. No upload allowlist
or run permission is added.

Independent test draftfd03b1c0 was preserved in0c140362 before execution. Review
found one misplaced helper-level expectation and an incorrect recorder project
name; the contract clarified the complete validation boundary. Author correction
a727bdc8 replaces only that method, retaining the original rejection requirement
and adding valid controls for all17 other project profiles. No draft tests ran.
The corrected expectations and63 source/test/fixture pins were frozen in84b3fbaf.

Actual commands and complete output are in P7_motor_fault_raw/:

- activation_first.json:13/13 independent methods PASS,1.463s, first execution.
  These include real config compilation and exact-byte sketch compilation/execution
  through controlled Arduino/native/Runner headers, plus full policy boundaries.
- activation_regressions.json:29 unchanged macro/policy/executor methods PASS;
  diagnostic driver3/3 PASS. Normal and ASan/UBSan each pass18 cases and2570
  assertions, with zero skips. Unsafe motor flag combinations remain rejected.
- activation_freeze.json: all63 hashes remain exact after both commands.

Separate fresh-context same-model revieweeb297fa PASS, no open material finding:
../reviews/P7_fault_activation_review.md. Reviewer inspected source and root-run
receipts; reviewer did not execute tests or board commands.

No target compilation/upload/reset occurred. D168 proves only its prior disabled
revision; its historical manifest now correctly rejects changed config/sketch/policy.
The active diagnostic still needs a fresh checked artifact and identified inert
run/capture; neither host substitutes nor the selector prove native behavior/WCET.
All compiler/fixture outputs were RAM-backed and removed; a fresh check found zero
sumox task remnants. The policy-denied104-file Windows stage was untouched.

Next dependency: existing board_tool.stage deletes its fixed destination. Add the
smallest explicit fresh-attempt staging API that preserves the Arduino layout and
never deletes or overwrites in explicit mode. Keep the retained directory and all
consumed scopes unchanged; do not invoke implicit legacy cleanup on that path.
