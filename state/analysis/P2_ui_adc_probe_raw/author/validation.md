# D114 independent policy and wrapper validation

PASS on first execution: **24 unittest methods** (17 new independent methods and
7 untouched D112 UI policy methods), with zero failures, errors or skips. The
new tests and embedded C++ fixtures froze before any production execution. No
test/oracle/fixture amendment was needed.

Frozen test SHA-256:
`f88ff324c23f6c0b3d0b91498874498910fa19eb0c9529dec84360990a73f297`.
Harness SHA-256:
`30f95f1a439d4239816c2b466aacfa8c261a51d7aee2c154f65d98de65fecd03`.
Adopted public contract at freeze:
`1250e761bc46b517816ca012b45c7ecc89ce665847e7f04e06b4e99a7c1dab0e`.
Exact tested board_tool, app_build_policy, new wrapper and all five existing UI
file hashes are retained in `run1_source_copy.json` and `validation.json`.

The suite covers the exact four-file source selection and bytes, required Arduino
layout and existing project modules, each file's participation in source hashing,
restaging, missing files, source/ancestry symlinks, direct destination collisions
(regular files, directories and dangling links), local shadow sources, and no
shared-source selection for other sketch names. The public helper destination is
the `src` directory itself, as clarified before freezing tests.

Public checked-policy tests cover default startup with MATCH0/MOTORS_ALLOWED0,
all conflicting macro profiles, Immediate refusal, exact project references and
artifacts, external-library/result rejection, checked-route dispatch, profile
overrides, failure propagation, and upload refusal before transport/staging. Both
old UI startup profiles and old upload refusal remain tested unchanged. A literal
D112 hash baseline additionally verifies the old sketch and all four shared
implementation/header files remain byte-identical.

Actual new and old wrapper bodies were copied and compiled opaquely against
independently declared Native/Runner substitutes. **Eight executable profiles**
passed: new/old wrapper, begin returning false/true, and normal/ASan+UBSan. Each
proved one Native, one Runner, one port binding, zero begin/poll calls during
construction, the exact true/false grant respectively, one begin, and10000 polls
from10000 loop calls. Guarded C++ allocation operators reject heap use. Every
binary exited0 with empty stdout/stderr. Three nonzero MATCH/motor combinations
were required to fail compilation and did so.

Command: `wsl.exe -e python3 <repo>/state/analysis/P2_ui_adc_probe_raw/author/run_policy.py run1`.
The harness uses a unique copied Linux workspace and mock transports; no shared
build or board is touched. Full results and exact process command/outcome remain
in `run1_full.txt`, `run1_summary.json`, and `run1_command.json`.

This reused author context remained independent of the new implementation bodies;
it is not fresh to the repository or cross-model. Existing public test fixtures
were read and reused without changing their assertions. These tests qualify
staging, policy dispatch and wrapper calls only. They do not prove ADC silicon,
ownership admission on the actual board, capture ABI/decoder correctness, target
memory/loader fit, any upload key, or physical input acceptance. Full established
policy regressions, exact target/readout review and any identified run remain
coordinator-owned acceptance evidence.
