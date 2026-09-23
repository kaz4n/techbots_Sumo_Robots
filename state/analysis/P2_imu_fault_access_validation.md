# D097 passive setup-fault retrieval: verified dependency reduction

2026-09-23 Asia/Dubai, contractcf3dfe1, baselinea93d536. IMPLEMENTED/HOST-TESTED;
bounded getter review PASS, full-app TARGET-BLOCKED. No physical gate is closed.

Acquirer::setupFailure() returns the already latched Sample only when actual Setup
is FAULT; elsewhere it returns canonical NOT_READY. NativeSources' setup-fault
callback uses this const getter and ignores its old time argument. It neither
observes time nor performs I/O. Legacy read, setup/async acquisition, mixed-API
cancellation, configuration, capacity and every safety rule remain unchanged.

Independent author tests: actual Acquirer7cases/31474assertions and actual native
callback1case/178assertions pass in both MATCH/MOTORS_ALLOWED settings with strict
C++17, Werror and UBSan. All sample/motion fields, start/advanceSetup faults,
passivity, runtime-only-fault absence and old mixed-API behavior are covered.
Root fullnormal/ASan/UBSan each1418main/25218819assertions and173enabledGate/
4536382assertions pass, zero skipped/failed. Exact argv/status/output and final
CTest logs are under P2_imu_fault_access_raw. No established/locked test changed.

Fresh separate same-model reviewer independently passes3cases/685111assertions
under ASan/UBSan, including all48 possible setup-request transport failures and
byte-immutable repeated reads. Native callback object relocation references only
the getter. This is separate-context review, not cross-model review.

Actual same-app board-Linux compile-only source:
`570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84`.
The pinned1.0.0 core reports210600program/275760memory and exits1:13616B over262144.
The final D096 image needed276456B. Actual net saving is **696 bytes**, not the
initial752B gross estimate:268B legacy read +484B acquireMotion disappear while
the56B getter is retained. All other allocated section sizes are unchanged.
This does not qualify a deployable target image or loaded free memory.

All82 current/staged/remote sources and three failed-build cache ELFs are captured
and checked. Setup::advance/Bus::transfer and native async paths remain.188imports,
40native/42AEABI export addresses, base loader,12init targets and actual startup
instructions/relative relocations remain unchanged. See dependency_comparison.json,
source_integrity.json and independent review raw receipts. Explicit
target_compile_accepted=false preserves the failed memory check.

The same seven inert keys were independently reconstructed and matched to actual
local staging before refresh; no app/new upload key. No D097 upload/reset/MCU
sensor or motor operation occurred. Old deployed D0911502e948 remains the last
known image. No configuration, pin, startup or toolchain change occurred.

Original failures remain: author's mixed-API fake initially injected cancellation
on the wrong Bus method; the established collision occurs through acquireMotion.
Correct only that new fixture and retain the old behavior assertions. Root's first
normal/sanitizer builds rejected new REQUIRE macros under the actual no-exceptions
doctest policy. New tests now CHECK and explicitly return on failed prerequisites;
no existing assertion or shared build flag was weakened. All old receipts/hashes
and the author's NO_EXCEPTIONS_SUPPLEMENT.md remain. Reviewer path/symbol-type
harness mistakes are likewise disclosed in its raw evidence.

The full RAM blocker remains13616B. D098 is a separate isolated discovery-property
control/candidate experiment, not a production adoption or a D097 compiler pass.
LoadedRAM/full800us, physical sensor/motor acceptance, native UART/local-reset/
calibration-snippet integration, EXPLAINED and all human phase gates remain open.
