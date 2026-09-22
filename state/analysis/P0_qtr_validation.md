# P0 0.4 QTR-style bare-board validation — 2026-09-23

Status: IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / REVIEWED; physical execution
pending. This is a P0 setup-only diagnostic, not P2 HAL.

## Contract, source and independent expectations

D-065/public layout/config preceded source in af4cc67; db8728b clarified clock
quantization and cleanup. Installed source/ownership basis is
P0_qtr_bare_contract_audit_20260923.md (F-082). Contract review's three documentation
findings were corrected, with no algorithmic BLOCKER/MAJOR. All76 B16 defaults,
existing core/HAL and established locked tests remain unchanged.

Final candidate source SHA-256:
`61d7a2d00ec1e7f1782d0a7439bd71cb123338dc1073e55abe43b9c6e3fe521e`.
26 staged files, with an empty post-setup loop. Two datasets of100 samples use
neutral INPUT and separately labeled diagnostic INPUT_PULLUP. Actual four-read
passes, measured charge/deadline, bounded guards and cleanup attempts are retained.
Readbacks do not recover native wrapper errors or certify physical cleanup.

Independent author used the contract and public header, never the implementation.
Final50 cases (26 opaque-sketch /24 decoder) PASS7.804s; existing8 config cases
PASS0.024s. Strict g++13.3 C++17 warnings, no exceptions/RTTI and UBSan. A separate
fresh same-model reviewer independently reproduced50 PASS7.078s. This is distinct
context review, not cross-model or a human gate. Tests include actual call ordering,
deadline/guard equality, wrap/stopped/ambiguous clocks, early/late LOW, failure
cleanup, no allocation, publication, frozen loop and sketch-to-decoder roundtrip.

Preserve initial46-method/45-subcase failures and first repair50-method/5-subcase
failures in P0_qtr_host_tests_20260923.txt. P0_qtr_failure_analysis.md explains the
extra fault-path timestamp and premature timeout-mask publication. Neither defect
was repaired by relaxing an assertion. The new invalid-total end_us expectation
was strengthened to the original contract before the first repair rerun.

## Commands and target evidence

- WSL: `python3 -m unittest discover -s tests/tooling -p test_p0_qtr.py -v`.
- Native Windows, explicit ADB serial2629958581 and board-side CLI:
  `python tools/board_tool.py flash bench/p0_qtr --compile-only`.
  Final receipt P0_qtr_target_compile_final_20260923.txt: exit0, MATCH0,
  MOTORS_ALLOWED0, default startup. Compiler reports76924B program,45896B globals,
  216248B remaining; these are compiler figures, not measured stack headroom.
- Initial fb4248d9 and intermediate016896c1 compile receipts are retained. Those
  images were never uploaded;23fb81e6 was a local intermediate, not target-built.
- Five controlled SSH/ADB upload tests initially passed17.316s. Compile-only/match,
  Immediate rejection, source mutation and failed compile all covered. Reviewer
  later observed the expected rejection while the manifest still named the older
  candidate. Exact final61d7a2d0 manifest now independently approved/refreshed;
  reviewer rerun PASS5/5 in19.785s against the final manifest.
- New8 coordinator-authored passive boundary tests use synthetic extension/record
  readers, distinct from the actual target's independently checked layout.
  Fresh reviewer independently reproduced8/8 PASS0.053s and exercised8 additional
  ephemeral main/readout-failure fixtures without any board operation.
- Full WSL tooling: `python3 -m unittest discover -s tests/tooling -v`, exit0,
 306 tests PASS112.485s, no failure/skip. Receipt P0_qtr_tooling_20260923.txt.
  Includes unchanged counter packet25 cases/156553 assertions. This is script/
  host evidence, not target execution or a new895-case full-core run.

No upload, sensor result, PINMAP OK, human gate or motor authorization is implied
by this checkpoint. Current physical image remains reviewed GPIO1dfbd571 until
an actual QTR upload receipt below supersedes it. Preserve source/host/build/run
distinctions and report actual observed values only after readout.


## Exact artifact/readout pins

Final source61d7a2d0: ELF76924B SHA256
080142c992024089255c0ced50904bb0ef4a6f41a7caf748ddecfcde625d1077;
default wrapped ELF76924B SHA256
46d305b50bd71f8f48aa8fb97a8f71d5faff1faa032dad1db123c1b62d93e632.
Debug ELF1429120B SHA256
ad7ec53bcd26613225c2454c15671c64f157eea44738998af2771600c4dad83c.
Final BSS index9, VMA0x5778,size21980,alignment8; readelf p0Qtr st_value4 is
already section-relative, size14424. Do not subtract the VMA from that value.
Capture tool pinned these exact identities; SHA256
00798d186378b9e5016db9d1fea1fd254a30e92775c02818c9aecb7dd6e941c6.
Shared capture helper/config unchanged. Artifact source map independently matches
all26 files. Binary verdict and final layout fixtures recorded in linked reports.


Pre-upload review complete: fresh P0_qtr_codex.md PASS/no open findings;
P0_qtr_binary_audit_20260923.md PASS for exact61d7 candidate. Fresh reviewer checked
19 additional ephemeral readelf-layout cases, including rejection of nm's VMA
as a section-relative offset. First reviewer fixture attempt had Windows path
separator mismatch, corrected in its ephemeral fixture with as_posix; production
code/tests unchanged. Source/manifest/capture identities rechecked unchanged.
Staged source/docs/JSON whitespace check passed; preserved initial unittest output
contains trailing spaces from failed subtests and was not rewritten to hide them.
