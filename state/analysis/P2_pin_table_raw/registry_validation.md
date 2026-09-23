# Additive D096 registry invocation evidence

The D106 integration run exposed a stale invocation context in D093's unchanged
config-registry wrapper. Its additive registry included D093 and earlier names,
but not the three existing D096 runtime guard names. The original failure remains
in P2_app_build_raw/d106_native_integrations.txt and
P2_power_inputs_raw/author/registry.jsonl. D106 did not introduce those constants.

The new `tests/tooling/test_runtime_config_registry.py` derives these literal
expectations from P2_app_runtime_contract.md (actual release-grid and per-epoch
acquisition sections) and D-096's selected development limits:

| Constant | Approved value |
| --- | --- |
| APP_QTR_SERVICE_US | 600 us |
| APP_SERVICE_MAX_PASSES | 8192 passes |
| APP_CLOCK_STALL_MAX_POLLS | 65536 observations |

The new wrapper uses mock.patch.dict to extend the existing expected-default
dictionary only for the invocation. It invokes the unchanged D093 registry
method, which invokes unchanged D090 registration and all 18 unchanged P0 config
test methods. No assertion or production file was edited. Direct invocation
avoids the D093 class's unrelated native C++ setUpClass; the registry method
requires no native fixture. The legacy receipt destination is temporarily
isolated and its complete result is retained in registry_cases.jsonl.

Before execution, registry_freeze.json records the new test, contract, config
and all three legacy-test hashes. The new test SHA-256 is
`b45f5d9cdcb8d944036693f1dc86c3549277b7421e898f7a67fc589657917b49`.
The checked config SHA-256 is
`db11bbeea16d8bd68c9c2cb2db50eef3a61b80bd98c1e1483393620afb570c8e`.
Every invocation checks that all frozen files remain byte-identical and that
the temporary expected-default dictionary changes are restored.

Command: `python -m unittest tests.tooling.test_runtime_config_registry -v`.
First run PASS, exit 0, two new test methods, no skips. The approved profile
passed the nested 18 legacy tests. Three independent copied config profiles
changed exactly one D096 value to its approved value plus one. Each executed all
18 legacy tests and was rejected by the unchanged explicit-default-value test,
with one expected failure and no errors. This confirms that the additive context
does not conceal drift in any of the newly registered values.

See registry_run1.json/txt and registry_cases.jsonl for exact outcomes. This is
offline source-config evidence only; it does not validate runtime execution,
complete WCET, a pin map, target memory or any physical gate.
