# D167 compile attempt isolation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED.

Source7bd0108c adds closed per-instance compile01/compile02 selection to the
existing caller. Compiler process code, environment, timeouts, flags and final
checks remain unchanged; original inputs and consumed receipts remain exact.

Independent contract-derived tests were frozen at ac92e45c before execution.
The first run passed7/9 and reported two missing test-fixture files: Windows ADB
and the pinned helper were unavailable under the substituted RAM root. Original
result is compile02_host.json. Production and original assertions were unchanged.
Fixture additions and three positive routing cases are in9db179f8. Review found
three additional fixture preconditions before execution;5e705716 supplies them.
That intermediate draft was never executed. All nine original methods remain exact.

Final testb23c4bac passes12/12 in0.146s, exit0. All seven frozen inputs are unchanged.
Receipts: P7_motor_fault_raw/compile02_ready_freeze.json and compile02_repair.json.
These are controlled host substitutions, not native compile evidence. Existing
four real-child tests apply only to the exactly preserved child machinery.

Actual Windows local02 admission separately checks all117 source/tool pins with
zero transports; selected output and local stage are absent. Historical manifest
d1ba918d rejects the three intentionally changed source files. New manifest74af663e
keeps its exact filename set. Read compile02_local.json and the separate review
in ../reviews/P7_compile02_review.md before the separately identified target step.

No source/config/safety limit, upload permission, physical acceptance or gate changed.
