# D166 macro compatibility repair

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED; target recompile pending.

D165 exposed the installed Zephyr CONFIG_PWM=1 macro colliding with a diagnostic
enum label. Commit88ce3e78 renames CONFIG_ENABLE/CONFIG_PWM to CONFIGURE_ENABLE/
CONFIGURE_PWM in the diagnostic header and implementation. Enum values0/1 and
all control flow, fields, callbacks and safety limits are unchanged. No macro was
undefined. Commit7619da9c updates exactly three test identifiers and freezes an
independent macro regression; all established assertions and locked tests remain.

Both commands in P7_motor_fault_raw/macro_validation.json returned0:

- test_motor_fault_macro.py:1/1, actual host syntax compilation with CONFIG_PWM=1,
  checking that the macro survives both header/implementation inclusion and all
  five operation IDs remain0..4. No object/executable was produced.
- test_motor_fault.py:3/3 driver methods; normal and ASan/UBSan each18/18 cases and
 2570/2570 assertions, including refusal of the three motor-capable flag variants.

The new expectation was authored from D166/public identifiers and the actual
compiler diagnostic, without reading the implementation body. All47 frozen input
hashes match. Source/test/compiler evidence is macro_freeze.json and
macro_validation.json. Separate same-model reused-context
[source/receipt review](../reviews/P7_motor_fault_macro_review.md) passes without
material findings. It does not replace the pending target compile.

D165 remains failed and consumed. Its original117-pin manifest intentionally
rejects the new diagnostic source. Preserve original native_compile01 receipts
and the raw byte preservation added in36c1ded9. Next provide fresh per-instance
compile02 ownership/input binding in the existing caller, without module-global
rebinding or copying its implementation, then review and run one inert compile.
No new upload, reset, motor permission, physical acceptance or human gate exists.
