# D180 main-app setup binding validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED.
Board disconnected throughout. No target compile, upload, MCU query or motor run.

The original-scope audit found that main app setup always passed literal empty
grants. Contract e4aea29c and source70b9cea5 provide the existing Runtime with
independent declarations from config.h. All17 flags remain0; axes remain{0,0,0}
and dump originUNKNOWN. No existing value, pin or consumer check changed.
The header is pure constexpr C++17. Only the ordinary app entry uses it; bench
entries and the already built historical diagnostic remain unchanged.

## Tests and evidence

The separate test author /root/setup_binding_tests read the contract and public
headers, without inspecting changed implementation or executing the subject.
Oracle ad9bd19c, SHA23633aa0dd6b712f1253db4d28460ee82477dc8297292110e61fb15dcf467da1,
was frozen before its first run. No fixture or source repair was needed.

| Receipt under P7_setup_binding_raw/ | Observed result |
|---|---|
| freeze.json | Ten source/contract/oracle identities; original command and HEAD |
| first_test_result.json + first_test_output.txt |16methods PASS,18.179s unittest; exit0, no skips |
| legacy_test_result.json + legacy_test_output.txt |26unchanged methods PASS,3.067s unittest; exit0, no skips |
| integrity.json | Ten current and24priorD179pins exact; protected paths unchanged; no owned RAM remnants |

First command: `wsl -d Ubuntu -- python3 -B -m unittest tests.tooling.test_configured_setup -v`.
Checks cover all21 destination leaves, each flag alone and each false among
true peers, mixed values in all four MATCH/MOTORS_ALLOWED combinations, axes,
origins, compile-time refusal of out-of-range inputs and existing Estimator
rejection of unconfirmed/malformed mounting. The actual .ino setup/loop text is
executed with typed native/Runtime substitutes; real-builder constant-expression
tests separately use the actual public SetupGrants. These substitutes do not
qualify real Runtime/HAL/Arduino execution or target ABI.

Method15 invokes the unchanged18-case legacy config registry with additive
declarations and a deliberately wrong default, requiring its exact single
assertion failure. Temporary nested receipts are checked by the existing wrapper
and disposed with the fixture; the outer16-method result records their success.

Legacy command: `wsl -d Ubuntu -- python3 -B -m unittest tests.tooling.test_motor_fault_activation.ActivationCompileTests tests.tooling.test_app_build_policy.AppBuildParserTests -v`.
Eight actual config/inert-sketch controlled checks and18 build-envelope parser
checks pass. No established or locked test was edited. Source/bench/core/HAL/tools
preservation was also checked against d8ff6b5a; config has only35 added lines.

Host: WSL Python3.12.3, g++13.3.0. Compilers serial, C++17 warnings-as-errors,
small RAM fixtures, Python-B. All owned scratch removed; no build tree/package
download. Keep compact receipts and reproducible source, not copied binaries.

## Limits and next dependency

The changed main app remains TARGET-COMPILE-PENDING. Historical target receipts
do not qualify it. Declarations cannot establish verified wiring, current port
ownership, physical measurements, phase gates or run authorization. Default
firmware remains unconfigured and cannot operate the robot as shipped.

Next native work is fresh board admission and the already reviewed D179 inert
diagnostic scope, followed by actual cause/acceptance work. No real scope/owner
was created. No further offline omission was identified by the scoped audit;
do not repeat passing suites or build new frameworks while hardware is absent.

## Independent review

Fresh-context same-model review: state/reviews/P7_setup_binding_review.md,
SHA4e26ed277a39ed1a30a722b08d5a6b92fa7b5636a4cdc8e14c4ee44331fcf0fe.
PASS, no open BLOCKER/MAJOR/MINOR in this bounded scope. The reviewer inspected
source/tests/receipts and independently checked identities; did not rerun tests
or operate hardware. This is not a cross-model review or human phase approval.
