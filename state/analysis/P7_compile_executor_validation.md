# D164 checked-build executor validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED; no target action.

Commit4707fbce adds a keyword-only command_runner to three existing board helpers.
Every command in an explicit invocation uses that callable, including version,
preflight, compilation and artifact hashes. Defaults preserve old calls; invalid
values refuse before dispatch. No globals, policy/recipe/pin manifests, firmware,
config, locked tests or upload permissions changed.

Independent author froze15 contract-derived methods in03fcb903, without reading
implementation bodies. The first161-method invocation passed all146 established
methods, but new cases failed because the fixture classified an installed loader
ELF as a new project artifact. Original output is executor_first.json. Commit
bb04de24 repairs only that classifier, matching the four exact project basenames;
assertions and production code are unchanged. All15 new methods then pass in
0.408seconds; exit0 and all20 repaired-freeze inputs remain exact.

Evidence is under P7_motor_fault_raw/: executor_freeze.json, executor_first.json,
executor_repair_freeze.json and executor_fixture_repair.json. The first command
ran test_compile_executor plus test_app_build_policy, test_motor_fault_policy,
test_motor_stand_inhibit_policy, test_opp_view_policy, test_runtime_inert_policy,
test_app_build_overrides and test_tools using WSL Python-B with RAM scratch.
The repaired invocation reran only the15 affected new methods; it did not claim
a single all161-green invocation. No broad C++ rebuild was needed for this Python
change; prior fullhost22/22 remains unchanged-firmware evidence only.

[Separate fresh-context same-model review](../reviews/P7_compile_executor_review.md)
passes with no open material findings. This parameter does not itself enforce
target deadlines or grant a native run. Next is the fixed inert compile caller
with explicit CLI/config/environment, one compiler, source checks and a remote
process-group deadline/reap. Its review and real-child host checks are separate.
