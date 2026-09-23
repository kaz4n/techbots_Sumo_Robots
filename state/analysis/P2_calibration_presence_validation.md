# D083 countdown gyro presence validation

2026-09-23 Asia/Dubai. Contract/interface3c356ec; implementation5516bef.
IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / fresh separate review PASS.
This is actual Services/Lifecycle behavior, not yet Robot/HAL/app integration.

Services now distinguishes explicit ABSENT, VALID and INVALID observations while
preserving old LEGACY callers. Qualified distinct gyro sources are averaged once;
conflicting identities, stale/future delivery and mixed modes reject calibration.
Both source and decision must lie in the existing window. Closing, hold, warning,
snapshot, cancellation and STOP timing are unchanged. No new config value, old
test edit, motor write, physical fact or gate was introduced.

| Check | Actual result |
|---|---|
| Independent spec/header-derived author | Normal and ASan/UBSan each31cases/2283assertions; five new tooling methods PASS13.109s; author/independent_test_report.md |
| Fresh separate same-model reviewer | New plus existing locked Gate/Services/Lifecycle94cases/3507334assertions pass normal and sanitizer; five new methods and15strict config checks pass; reviews/P2_calibration_presence_review.md/raw |
| Full root host | tools/test_host.sh,2/2PASS12.51s,exit0; host_corrected.json/txt |
| Full root sanitizer | ctest verbose,2/2PASS24.57s,exit0;1124main cases/22648059assertions plus37enabledMotorGate/3796846; sanitize_build_corrected/tests.json/txt |
| Staging and tooling | Existing staged-core2PASS2.931s and tools25PASS47.651s,exit0; staged_core_discovery/tools.json/txt |
| Actual UNO Q Linux compile-only | CLI1.5.1/core1.0.0,arduino:zephyr:unoq,MATCH0/MOTORS_ALLOWED0/default startup;79248Bprogram/31916Bcompiler globals,exit0; target_initial.json/txt |

The root's27existing methods plus5new methods are32distinct checks across scoped
runs, not a new complete all-tooling run. The independent reviewer separately
checked unchanged config defaults. Both author/reviewer executed the actual
probe constructors/setup/10000loops in both macro modes,10000Services/Lifecycle
attempts with ordinary allocation/clock counters, and8mocked upload refusals
before connection lookup. Counter scope and source half-range reachability limits
are explicitly disclosed in the author report; no physical/WCET claim follows.

Actual target aggregate:
`9a7c64323e59555b327395c27227d1fa53ca7955a1a08c5a152932335a91ffe1`.
All46staged sources and3ELF identities retained/verified. Services/Lifecycle paths
are retained. Setup0xcc stores an unused function pointer, loop0xdc returns;
initializer0x24f0 has only inherited HCI/Bridge memory stores and no service call.
36native exports and42math exports, including9calibration helper routes, match
installed bindings. This is offline ELF consistency, not executed loader/runtime
or MCU timing evidence. Exactly5existing inert hashes reviewed and adopted; no
new upload key. Root verified all318review snapshot files and6command/output
hashes unchanged. Review compared246protected pre-existing files without content
edits; existing newline-only differences are separately listed.

Retained failures and repairs:

- Initial new tests lacked initializer_list and used5REQUIRE expressions disabled
  by the existing no-exceptions doctest mode. Author and root initial builds failed;
  add the include and use5identical CHECK expressions. No expectation, old test,
  compiler policy or production behavior changed. Both final full builds pass.
- A comment-only LCG modular arithmetic typo was corrected before first execution.
  The independently derived375distinct/125absent fixed-seed count was unchanged.
- Root's first staged-core module invocation could not import its sibling fixture;
  unittest discovery supplied the correct path. No test/source edit was needed.
- Author's initial outer shell exit file is invalid due to quoting. Inner command
  receipts preserve the actual compiler failures; the corrected literal runner
  retains final exit0. Do not use the initial exit file as a valid status receipt.

Raw paths above are in state/analysis/P2_calibration_presence_raw unless indicated.
No upload/reset/MCU/pad/sensor/motor action occurred. The last-known MCU image is
inertQTR61d7a2d0. Physical B3 accuracy/drift/read time, mounting, SC-AJ/F091 and
human P0/P1/P2 acceptance remain pending. Original deadlines remain unchanged.

Next actual implementation: HeadingReference availability/update/source-time
interface preserving legacy behavior and D059 origin/history timestamps, followed
by Fusion/Robot/recording routing from P2_imu_heading_raw/next_adapter_audit.md.
Do not wire D082's retained heading into the old combined imu_ok path. D083 alone
does not solve acceleration freshness or the remaining world/inward/stall evidence
routes. All established locked assertions remain protected.
