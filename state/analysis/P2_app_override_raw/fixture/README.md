# D100 established fixture adaptation

2026-09-23. Objective: extend only the controlled fixture protocol and its positive
metadata for D100 while preserving established test assertions and test methods.

The independent fixture reference is derived directly from saved actual
`P2_app_build_raw/default_receipt/compile.stdout.json`, SHA256
`416a0f71c229863fc8e4325138b9eae8897bd439979bb4afac84c21a4e08ca69`.
`derive_reference.py` records the reproducible extraction: 84 effective command
properties, including build.compiler_path/crossprefix/zip.pattern in addition to
the 81 recipe/compiler/link/check/zsk/postbuild properties. It never reads the
production D100 command reference or validator. The positive parser fixture
contains 97 total properties, including explicit build.path and the corrected
actual compiler namespace packages/zephyr/tools.

Modified files and scope:
- `tests/tooling/fake_command.py`: contextualize actual command metadata for the
  selected build path, data root, safety flags and startup mode; provide resolved
  directory JSON; trace properties-only queries separately; model the exact
  fixed six-path absent-file shell probe without executing shell text.
- `tests/tooling/fake_app_reference.json`: independent saved actual reference.
- `tests/tooling/test_tools.py`: setup copies reference data and installs the
  synthetic sh command.
- `tests/tooling/test_adb_transport.py`: setup copies reference data and embedded
  protocol dispatches the fixed sh probe.
- `tests/fixtures/app_build_policy/valid_result.json`: complete positive metadata.
- `tests/fixtures/app_build_policy/fault_command.py`: existing compile injections
  apply only to actual compile, never the properties-only query.
- `tests/tooling/test_app_build_policy.py`: only set_property fixture helper now
  updates expanded recipes for deliberate FQBN/safety-flag mode changes. The
  boot-mode property remains independent, preserving its final negative test.

Final verification, WSL Ubuntu with `PYTHONPATH=tests/tooling`:
`python3 -m unittest -v test_tools test_adb_transport test_app_build_policy`
passed all 78 tests in 83.365 seconds, exit 0. Exact stdout/stderr/exit are retained
in `established_final.*`. `assertion_integrity.json` confirms every assertion and
complete test method is AST-identical to HEAD: 25 SSH, 24 ADB, 29 D099 tests.
Scoped git diff --check passed (only a Git LF-to-CRLF informational warning).

The initial run began before the implementation owner's ready message and is
preserved in `established_initial.*`: 78 tests in 51.477 seconds, 8 failures and
15 errors. Eight early SSH subtests copied the initial 81-key fixture before its
84-key expansion; eleven D099 integration methods hit an invocation PYTHONPATH
error; four pure positive checks exposed omitted build.path fixture metadata.
The final run uses the complete fixture and correct invocation. No assertion was
changed to address any failure.

All transports, compilation responses, dependency hashes and artifacts here are
synthetic. No board, installed package, firmware source, locked test, upload,
reset, MCU or motor action occurred. New D100 regression tests, physical evidence
and final adoption review remain separately owned work.
