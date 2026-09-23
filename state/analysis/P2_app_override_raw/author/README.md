# D099-R1 independent test-author evidence

Objective: reproduce the checkpoint review's effective recipe/compiler/hook
gap and prevent regression through the documented pure `validate_result` seam.
Author read the D099 public contract, review/reproducer and saved actual default
receipt. Author did not inspect production `app_build_policy.py` or
`board_tool.py`; opaque imports and file hashes do not supply test expectations.

Modified files are limited to the new `tests/tooling/test_app_build_overrides.py`,
new `tests/fixtures/app_build_overrides/` and this author evidence directory.
No established or locked test, shared fixture, firmware, config, ledger, or
installed package was changed by this author. No board/network/commit action.

## Initial red baseline

`initial.json`, `initial.stdout.txt` and `initial.stderr.txt` preserve the
2026-09-23 local WSL run against production validator SHA256
`99c446714f16e6d234b2bf0670fce934a511c6668c37bdc8f89c3b94e6f038af`.
The run executed 14 test methods, exited 1, and reported 141 failure subcases,
all because the expected ValueError was not raised. The actual default receipt
and unrelated-property/property-order positive controls passed. The three
specific review mutations each failed as expected for this red baseline.

Negative cases cover effective C/CPP/S safety flags and executable/source/output
paths; compiler commands/flags/response paths; linker commands, numbered recipes
and entrypoint; packaging and startup settings; changed/extended existing hooks;
additional hooks/numbered recipes; missing or empty required command properties.

These are local synthetic mutations of saved evidence, not proof of actual
installed overrides or a defect in the saved default binary. Parser rejection
alone cannot prove precompile hook prevention. Public preflight and integration
tests await a documented seam from the implementation owner.

## D100 extension and intermediate evidence

After the implementation owner froze `P2_app_override_contract.md`, the author
added the public `validate_preflight`/`resolved_directory` seams and independent
wrapper integration tests. The pure matrix is reused unchanged at the preflight
boundary; every reviewed effective property is separately replaced and removed.
The new tests still use the actual saved receipt rather than the production
reference file. Pinned installed/primary platform lines164-165 establish the
Immediate packaging argument used by independent mode positives.

`d100_seams_initial.*` records 38 methods and11 failure subcases against an
in-progress implementation: accepted build.compiler_path changes/removal/empty,
build.crossprefix and build.zip.pattern changes in both validators, and embedded
NUL in a resolved directory. The author reported those findings; production was
fixed by the implementation owner. No assertion was weakened to hide them.

`d100_integration_initial.*` records46 methods with46 failing integration
subcases before the wrapper's preflight sequence was implemented. Its receipt
scope label predates the runner's integration-aware description; the run included
isolated command fixtures as shown by the test output, never an actual board.

The owner clarified the fixed probe includes six paths (four override sources
plus remote sketch.yaml/sketch.yml), and shell-interpolated paths reject quotes,
dollar signs/backticks and control bytes. Two newly authored directory positives
were moved to negatives to reflect that explicit contract clarification; the
previous evidence remains. Ordinary normalized spaces remain positive. The
exhaustive matrix now includes all84 properties, adding the three original
command-alias gaps to the initial81-prefix property set.

`d100_integrated.*` records46 methods PASS with stable before/after source hashes,
prior to extending exhaustive removal checks to those three aliases. Integration
covers all modes, identical preflight/real compile argv,18 pins before/after build,
all six override files as regular files and dangling symlinks, malformed directory
and properties output, failed precompile pins, no real compile after failures,
local profiles before transport lookup, and separate failed preflight stdout and
stderr retention. The shell test executes the exact supplied fixed literal against
temporary local paths, so dangling-symlink refusal is exercised rather than mocked.

The runner now records before/after hashes of validators, wrapper, tests and
shared fixture sources. Hashing/copying opaque production files is not reading
their implementation for expectations.

## Final author result

`final.json`, `final.stdout.txt`, `final.stderr.txt`:46 methods PASS, exit0,
29.638 seconds; source identities stable during the run. The final exhaustive
matrix tests changed/missing values for all84 controlled properties through both
validators. Original reviewer reproductions and their initial red baseline remain.

This establishes independent host regression evidence for the scoped correction.
It is not fresh target compilation, a complete security proof, a physical result,
or a D099 adoption/phase pass. Next action belongs to the implementation owner:
separate review and the still-required actual default/Immediate/MATCH/library
evidence. This author performed no board, network, upload, reset, commit, source,
config, installed-package or shared-ledger operation.
