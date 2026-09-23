# D080 MPU6050 setup and decoder validation

2026-09-23 Asia/Dubai. Contract/source00f96ee; implementation63c7eaa. D051/D075
authorize P2 software before physical acceptance. The implemented layer is
finite sensor setup and coherent sensor-coordinate decoding, not runtime
freshness, bias calibration, heading, application integration or physical B3.

## Implemented boundary

Setup performs the fixed48-operation reset/identity/profile/readback/discard
sequence with one bounded Bus call per advance. Every wait returns to the caller;
write completion anchors the later wait. Absolute1s/1024advance/64request bounds,
explicit configuration checks and wrap-safe order/deadline validation make
failure terminal. PROFILE_READY means observed profile, not measured settling.
The decoder preserves signed raw axes and selected1000dps/8g scaling, diagnostic
status and rail bits. It returns fully zero payloads on malformed/fault transfers.
It does not claim that the status byte identifies a fresh motion generation.

CPP SHA f38f0f2116f77534a9c812acd925c574d009fff8c3a521dd6af3c255f49e8a37.
Only12 new development config constants; previous B16 values/pins unchanged.
Native Bus, core, app and all established locked tests unchanged from70b52c5.

## Actual validation

- Normal complete host2/2 PASS8.19s, exit0 (initial23-new-case build also passed).
- Complete ASan/UBSan2/2 PASS32.36s, exit0:1056cases/22544915assertions plus the
  enabled MotorGate37cases/3796846assertions. Actual detailed output is retained in
  P2_imu_setup_raw/sanitize_tests.txt; no failure or skipped host case.
- Independent spec-derived author tests26/26 PASS1,562,374 assertions. A separate
  fresh same-model reviewer independently passes the same cases/assertions in
  normal and ASan/UBSan builds. Their focused filter excludes one unrelated
  scaffold case; it excludes no D080 case. Root complete suites cover the rest.
- Ten new tooling methods pass across an8-method variant run and a2-method
  startup/refusal run.44 separately compiled configuration variants and2 actual
  probe builds run successfully. The reviewer reproduces both groups, with92
  compiler/executable receipts all exit0 and201,164 variant executable assertions.
  Primitive zero-initialized counters establish no Bus call before main, in
  setup or10000loops under host MATCH/MOTORS_ALLOWED0/0 and1/1. Eight upload
  combinations reject before transport lookup. No firmware execution follows.
- Strict config13/13 PASS, retaining complete declaration equality and all old
  default assertions. No assertion or compiler flag was weakened.
- Actual UNO Q Linux compile-only PASS, CLI1.5.1/core1.0.0, FQBNunoq,
  MATCH0/MOTORS_ALLOWED0/startupdefault. Source
  c45ffd3dda53de8b8fbf6c8008fc939362ca2024aedcb4cd23e4c55ce138cd41;
  84132B program/34748B compiler global-memory report, exit0.
  Root and reviewer separately match44source files and3ELF identities. Native
  bindings, retained methods, constructor relocations/setup/loop were inspected;
  new startup operations are memory-only. No measured runtime RAM claim.
- Fresh independent review PASS/no open findings; exact5existing inert-source
  hashes reproduced/adopted with no added key. See reviews/P2_imu_setup_review.md.
- Full existing tooling432/432 PASS630.788s, exit0. Together with the ten new
  setup methods,442 distinct tooling methods pass across separate invocations.
  The strict config13 are already part of432, not an additional13 in that total.
  The existing native Bus run also retained102 subprocess receipts (100exit0 and
  two required assertion/signal sentinel exits1). Its default historical output
  directory was archived to existing_native_bus/ without changing receipt bytes;
  existing_native_bus_relocation.json identifies only the new D080-run files.

The first test-only compile failed because REQUIRE conflicts with the existing
no-exceptions flags. New-test fatal guards now use CHECK+abort without changing
predicates or existing tests. The actual driver passed first execution; no
production repair was required. A separate reviewer invocation's PowerShell
comma-parsing error and quoting repair are retained. Reviewer feedback also
closed the missing actual-probe startup-counter evidence with the two added
tests above. Original failures and earlier smaller passing runs remain intact.

## Evidence and limits

Exact commands/status/times are in P2_imu_setup_raw/, author/AUTHOR.md and
reviews/P2_imu_setup_raw/. target_c45ffd3d_bench-default.json contains the actual
source/ELF collection; root_target_integrity.json and manifest_adoption.json
bind independent local comparisons. The byte-exact raw staging check is recorded
when the final evidence commit is made.

No upload/reset/MCU/I2C/pad operation or motor run occurred. Last-known actual
MCU image remains inert QTR61d7a2d0. Physical identity/power/address/pull-ups,
settling, new-sample rate, axes, yaw and full-loop WCET remain unmeasured.
SC-AJ clock qualification and F091 inherited runtime paths remain global
deployment blockers. No PINMAP/EXPLAINED/human gate or motor permission follows.

Next actual B3 work: one bounded status/STOP/motion acquisition with a shared
deadline/poll budget and explicit NO_NEW/FAULT/observation results. The source
shadow-freshness inference and sample-age limits must be adopted explicitly;
two independent600us allowances do not establish an800us complete tick. Later
calibration-presence routing and continuous-yaw/axis/gap policy remain separate.
