# Independent D099-R1 regressions

The positive input is the unmodified, saved actual default receipt at
`state/analysis/P2_app_build_raw/default_receipt/compile.stdout.json`, SHA256
`416a0f71c229863fc8e4325138b9eae8897bd439979bb4afac84c21a4e08ca69`.
It records an earlier board-Linux compile, not a new hardware operation.

`mutations.json` supplies independent synthetic changes derived from the D099
public contract, the D099-R1 review, and command properties in that receipt.
The tests keep checked C/CPP safety metadata intact while changing effective
compiler/recipe/link/startup/hook properties, adding commands, or removing
required command entries. They include the reviewer's three exact mutations.
Unrelated metadata and property reordering remain positive controls.

The author did not read the implementation of `app_build_policy.py` or
`board_tool.py`. Production validators are called through documented public seams.
D100 adds `validate_preflight` and `resolved_directory`, and the same independent
effective-command mutation matrix exercises result and preflight validators.
All84 controlled properties are changed/removed one at a time. Default,
Immediate and MATCH positives include independently relocated data/build paths.

`fault_command.py` uses the existing isolated transport fixture and adds malformed
directory/preflight output, changed recipes/hooks and precompile-pin failures.
The fixed shell absence check executes only against six temporary local paths,
including regular files and dangling symlinks; it never receives real board paths.
Tests check no real compile follows rejection, positive ordering/identical argv,
all18 pins before/after compile and separate raw preflight stdout/stderr retention.
These tests never contact a board, compiler or network.

Directory expectations follow the D100 path clarification: ordinary spaces remain
allowed, while root, unnormalized/control-character paths, dollar signs, backticks
and quotes are refused because installed prebuild shell recipes interpolate paths.

Run `python3 -m unittest discover -s tests/tooling -p test_app_build_overrides.py -v`.
Raw red/green evidence belongs in `state/analysis/P2_app_override_raw/author/`.
