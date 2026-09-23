# Independent D096 author validation

Objective: derive new runtime/projection tests from the full frozen D096 contract and public dependent contracts without reading production implementation CPP. Contract initially36c251f; root-owned explicit projection/clock chronology amendments applied before final validation. No old or locked tests edited.

Final exact command: `python3 -m unittest tests.tooling.test_app_runtime -v` under WSL from repository root. Six Python methods PASS in78.026s. C++ builds use actual copied production sources, strict C++17 warnings, no exceptions/RTTI and UBSan; all heap assertions use actual Runtime operations with counted malloc/new/free hooks and positive controls.

| Profile | MOTORS_ALLOWED/MATCH | Cases | Assertions |
|---|---|---:|---:|
| Default config, ADC omitted for multi-epoch source isolation |0/0|37|68688|
| Default config, ADC omitted for multi-epoch source isolation |1/1|37|68688|
| Isolated synthetic configured A1 windows |0/0|43|105510|
| Isolated synthetic configured A1 windows |1/1|43|105510|

Synthetic window changes exist only in temporary copied config: NONE0..100, START900..1100, MODE1900..2100, BOTH2900..3100; production config remains untouched. A separate default test explicitly grants unconfigured ADC and proves INVALID buttons/STOP, so omission does not hide that safety behavior.

Coverage: optional/required grants and all19 missing callback positions; first Gate/setup order and native setup failures; actual original-grid S/D/A/C, early idleness, missed-release saturation, wrap, finite65536 equal idle clocks; exclusive charge and finite8192-pass pending service cancellation; CONTROL next-epoch progress and immutable mailbox; actualD IMU1999/2000/2001 and line5999/6000/6001 boundaries, observed whole-wrap nonrevival; completed IMU publication survives NO_NEW, setup-fault-once and malformed payload; real ADC cadence/shared fault and stale button inhibition; RAW boot, all8 real menu-driven16-frame calibration stages, exact350us threshold bank and fresh CONTROL handover; actual5100ms hold, accepted estimator bias without GO yaw reset, separate allwhite guard fault sealing and clean BOTH STOP DRAINING->real ADC/opponent tail->SEALED; output timing, overrun logging and allocation silence. Projection tests cover pure callback exactD, admission/order/clock failure, missing callback, duplicateD, legacy equivalence and decide({}) compatibility, source clock rejection, finishAfter chronology/equality/wrap.

Tooling covers eight actual-app upload refusals before target or transport lookup, compile-only app/bench staging for both match configurations, shared native/runtime includes, local shadow rejection and compile failure/no upload. These use controlled fake transports. This author did not execute actual native app startup or hardware; root owns native source/ELF/startup review and actual target compilation.

`frozen_test_hashes.json` records the five final test files; `final_hash_verification.json` confirms all match after the complete final run. `final_pass_receipts.json` indexes exact successful subprocess outputs and source/test hashes. Every prior failing compile/run remains in append-only command receipts. `exploration_failures.txt` classifies all fixture/oracle corrections and the independently found actual CONTROL QTR starvation fix. Earlier hash manifests remain preserved.

No board, upload, motor, physical clock/WCET, loaded RAM or gate claim; no commits made by the author. Root completes full existing normal/sanitizer suites, independent review and target evidence.
