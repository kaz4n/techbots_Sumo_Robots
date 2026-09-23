# D114 bare ADC firmware and staging validation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED. This receipt excludes capture,
upload approval and actual native ADC execution.

One13-line wrapper reuses the unchanged finite D112 sampler with Grants{true}.
The ordinary bench/ui stays disabled. A literal four-file staging case and
default-startup checked compile route refuse conflicting profiles, MATCH,
Immediate and uploads before transport. No existing upload key changed.

Final source hashes: wrapper87e305fe, board_tool e0444bc4, app_build_policy744d7d41.
Full identities and first/second/third source freezes remain under
`P2_ui_adc_probe_raw/root_implementation/`. The coordinator's pre-execution
review changed exists to lexists to reject a dangling destination collision;
no test expectation or production driver was changed.

Independent public-contract author froze17 new methods before execution.
All17 and7 unchanged UI methods pass, including8 normal/sanitized actual-wrapper
profiles and3 compile refusals. Separate private review reproduced24/24.
Root additionally verified the union of all128 earlier policy methods plus17new:
an initial100 passed while five modules failed package import because root used
unqualified module names. The corrected package-qualified45-method invocation
passed. Both original commands/status/output are retained in
`P2_app_build_raw/ui_adc_probe_policy_full.*` and `ui_adc_probe_policy_remaining.*`.
This invocation correction did not change source or tests.

Checked compile-only on USB2629958581 succeeded with pinned CLI1.5.1/core1.0.0,
receipt73d13df1e7244ddc8a71d1a7e52c0ed8. Exact96-file source:
`396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`.
All94 shared staged source files match the earlier D112 target. The wrapper
and README are the only replacements. No MCU upload or reset was invoked.

Final ELF `76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b`;
ZSK `567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`.
Both19840bytes. Debug ELF7544d247 confirms Runner9892/Native32, Report132 at16,
captures128x76 at148. Direct ET_REL symbol value is0; the nm display1690 includes
BSS VMA and must not be used as the offset. Actual installed loader semantics
and separate review confirm relocated BSS+0. The original draft interpretation
was corrected before decoder implementation and is retained as provenance.

Exact three-ELF review finds all function bodies equal to D112 except setup's
grant byte0-to1, sole expected constructors, empty thread bounds/loop hook,
unchanged native guards and expected imports. Conditional loader payload16245,
peak17128/free245016/largest245012; these are modeled fit, not measured free RAM.
See `P2_ui_adc_probe_raw/reviewer/target_396bcc45_bench-default.json` and the
scoped review. Read-only inventory exit1 reflects missing rsync alone; verified
ADB compilation succeeded without it.

Next: independently test/review the exact passive capture, pin its artifacts,
then identify one bare diagnostic run under D114. Upload remains refused until
then. SC-A/SC-AJ, physical button/pin/clock/reference qualification, full-app
WCET and all human phase gates remain open. No extra hardware is requested.
