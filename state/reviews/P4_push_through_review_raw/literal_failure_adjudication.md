# D132 first-run staging expectation adjudication

Reviewed at clean checkpoint `2bdc6eaedbe04482d1bc72c0f790cf7d465434a6`.
The retained `state/analysis/P4_push_literal_raw/admission.{txt,json}` reports
32 methods, three failed subtests: app staging at 0/20/100, all at the new
`tests/tooling/test_push_literal_admission.py:285` root `local.h` assertion.

This is a fixture expectation error, not a D132 production regression. Both
`ef763104:tools/board_tool.py` and the preserved D132 original intentionally skip
app-root C/C++ support files beside the staged `.ino`, then copy them under
`src/app/`. Current `tools/board_tool.py:228` and `:249` retain those rules. Bench
local headers still remain beside the sketch. D132's only stage change is the
identified config-copy failure and copied-config admission at lines 239-243.
The P0 staging documentation specifies project support beneath staged `src/`;
it does not promise an app-root copy of `local.h`.

Proposed narrow correction: use `output / ('src/app/local.h' if sketch == 'app'
else 'local.h')`; compare its exact bytes with the corresponding fixture source
header. For app, additionally assert that `output / 'local.h'` does not exist.
Keep every 0/20/100 case, exact config-byte assertion, root `.ino` assertion and
zero-board-operation check. Preserve the original failing oracle and receipts.
No production change or safety assertion weakening is justified.

The frozen independent nine-method contract suite and three-method lexical
supplement passed on their first execution using local Python with `-B`.
`private_literal_*_first_run.{json,txt}` records command, time, exit status,
probe SHA-256, implementation SHA-256 and checkpoint commit. Frozen probes were
hash-checked before running; all stage work used temporary roots and no real
board command ran. Corrected public admission and regression receipts remain
the coordinator's responsibility before final packet closure.
