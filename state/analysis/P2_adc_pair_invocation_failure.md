# D086 staging runner invocation failure

2026-09-23 Asia/Dubai. Root preserved two failed command receipts before further
execution. No implementation or test assertion failed and no tests were changed.

1. P2_adc_pair_raw/staging_final.json/.txt: requested nonexistent module
   tests.tooling.test_staging, exit1 ModuleNotFoundError.
2. staging_corrected.json/.txt: corrected filename but used package invocation;
   existing test_staged_core.py imports sibling test_tools as a top-level module,
   so that invocation also exits1 before collecting tests.

The previously successful D085 receipt already supplies the proper command:
python3 -m unittest discover -s tests/tooling -p test_staged_core.py -v, under WSL.
Root has now inspected both errors and the actual import at line9. This is a
runner correction only; discovery adds the test directory exactly as intended.
Escalated to the separate reviewer; do not weaken imports/assertions or treat
these failed collections as passed tests. The next distinct receipt records
whether the unchanged two staging checks actually pass.

Checkpoint script also initially used Windows default cp1252 to read the existing Unicode handoff, raising UnicodeDecodeError before any checkpoint write. The retry explicitly uses UTF-8 for every read/write and succeeds; prior handoff text is preserved. No source or test edit was involved.
