# D103 local inhibited service reset validation

2026-09-23 Asia/Dubai. IMPLEMENTED, HOST-TESTED, TARGET-COMPILED;
fresh separate same-model software review completed without a finding. Physical
acceptance, actual loaded RAM/stack/WCET and every human phase gate remain open.

The optional grant defaults false. With it enabled, actual STOP and final tail
precede fresh NONE/MODE-hold/NONE qualification. One guarded Robot-only reset
occurs inside the next real epoch. MotorGate remains STOPPED; recorder, tokens,
source owners, clocks and calibration bank survive. Service-only RAW/absent
line and IMU evidence prevents match starts; unavailable actions are reported
without inventing sensor results. A second STOP tails once then stays passive.
No config, core, established locked test, native backend or app grant changed.

Contract/public interfaces: 61ea3da, with explicit inherited source/decision
continuity clarification. Implementation adds runtime_service.cpp and
transaction_service.cpp and integrates existing Runtime/Transaction/UI owners.
Existing D095/D096 tooling changes only extend link lists: all14 test-method
ASTs match the baseline exactly. CMake adds the new tests to both motor profiles.

## Reproducible host evidence

Commands and exact exit statuses are retained under P2_app_build_raw:

- d103_host_final: `wsl -d Ubuntu -- bash tools/test_host.sh`, exit0.
- d103_san_build: `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, exit0.
- d103_san_test: `wsl -d Ubuntu -- ctest --test-dir build/host-sanitize --output-on-failure`, exit0.
- d103_tooling: `wsl -d Ubuntu -- python3 -m unittest tests.tooling.test_app_transaction tests.tooling.test_app_runtime -v`,14PASS, exit0.

Normal and ASan/UBSan each pass1443 main cases/45,732,771 assertions plus187
motor-enabled cases/4,536,952 assertions. Exact complete suite output is copied
to P2_service_reset_raw/host_final_LastTest.log and san_final_LastTest.log.
Default production button windows remain unavailable; additional independent
synthetic configured-window tests exercise the full real gesture/lifecycle.
Final test SHA256 is e3b4521085cf471a1fbe71434b3968ea0e62dd19d0fa6c6a47546ef0b2c212ba.
The independent author provides34 configured cases and9 default cases; original
failures, freezes, chronology corrections and coverage limits remain in
P2_service_reset_raw/author. No private owner seeding or implementation-source
access was used by that author. Public API exhaustion cannot be forced within
a bounded run; that limitation is disclosed rather than fabricated.
All8 author normal/UBSan profile runs pass: default9/403 in each motor profile,
configured34/6132 inert and34/6139 enabled. All4 strict post-match receiver
roundtrips pass; final_matrix_results.json binds commands, bytes and hashes.
Two additional configured ASan/UBSan runs also pass with the same frozen
predicates and exact two further strict receiver roundtrips; six streams total.

Separate fresh reviewer combines all34 configured cases with3 extra probes:
37/27,154 assertions inert and37/27,161 enabled pass ASan/UBSan. The probes add
24 clock positions around reset, service-fault categories and pixel invariance.
Actual GO -> STOP -> real tail -> local reset -> IDLE/menu LOG_DUMP is parsed by
the independent strict receiver; saved frames/events/summary must remain exact.
These streams are explicitly synthetic host evidence, not native UART evidence.

The initial Windows/WSL cache mismatch, production enum-warning fix, in-flight
test compile warning, doctest expression compile fixes, boundary-oracle failures
and analyzer assertion correction are retained. The boundary failures were
escalated after repetition: D087 requires both source gap and decision delta
<=5000us. Actual new decisions were5004/5005us late despite4999/5000us source
gaps, so terminal failure after an actual reset was correct. Final tests assert
both positive equality and adjacent failure, preserving the reset pulse and no
fabricated completion. See root_failure_analysis.md and author/oracle_corrections.md.

## Target evidence and limits

Actual app source1fbd72385c9a729be869bebaaabcc28b5614aa8ff23616843d7b2809a187301f
has87 files. Default and MATCH Immediate compile-only commands exit0, receipts
147ff7c62e974466a115cc42e75a5637 and46a4514f871e49a9b103b4252f388fd0. Exact
source,77 objects,6 ELFs/2 packages, startup and176 imports pass coordinator and
separate review. Default static payload256332B/model peak261056B; MATCH256716B/
261448B. The262144B pristine-pool model leaves1088/696B spans,1084/692B largest
next payloads. This is narrowly fitting static arithmetic, not a measured load.

Target Runtime166304B, Robot2640B; Robot::reset's own frame2680B plus callers and
callees. Installed main-stack reservation32768B is not available stack, a high
watermark or full tick timing. See P2_service_reset_target_audit.md and exact raw
source/ELF/DWARF/loader receipts. No sensor grant or native recovery is inferred.

The same seven inert keys were refreshed after every independently reviewed
file map matched actual local staging byte-for-byte. No new key/app upload scope
was added. No board upload, reset, MCU action, motor run, push or tag occurred
in D103; the prior MCU remains D0911502e948. The user has since reconfirmed the
bare board and authorized inert testing; a new scoped probe/review comes next.

Next: bounded bare-board Runtime load evidence with no external-pin operation,
then calibration-snippet delivery and remaining P2 physical-bench software.
P0/P1/P2 physical acceptance and P3-P7 cannot be marked passed by software tests.
