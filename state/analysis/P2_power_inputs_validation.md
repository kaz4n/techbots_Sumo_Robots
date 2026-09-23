# D093 ADC input owner validation

2026-09-23 Asia/Dubai. Active P2 software under D051/D075. Baseline8e4544a;
contract/public header commitd248782. This bounded task is IMPLEMENTED,
HOST-TESTED and TARGET-COMPILED with fresh separate review PASS. No result
below is a human gate, physical acceptance or motor authority.

The owner exclusively controls setup and A0/A1 requests to one native Reader.
It retains battery source evidence for strictly less than20000us and requests
replacement at10000us source age. These are development limits, explicitly
amending app-level D078; native Reader calls remain fresh-only. Shared faults
invalidate both projections. The existing governor filter/caps remain unchanged.

The implementation worker owns only new power_inputs.cpp/power_inputs_unoq.cpp.
The independent test author reads the public contract/headers and old fixtures,
not implementation bodies. Root owns integration/probe/build/evidence. A separate
fresh-context reviewer reviewed actual changes and evidence before completion;
that review is same-model, not cross-model or human gate approval.

Actual source, command exit status, test counts, compiler/ELF evidence and review
results are recorded below. Raw commands are recorded beneath
P2_power_inputs_raw using P2_power_inputs_record.py; no earlier receipt is replaced.

The compile-only probe retains Reader->InputOwner->Robot->MotorGate->recorder
without executing the path. No upload allowlist key is added. Actual app scheduler,
sensor readiness, ADC settling/accuracy, physical button circuit/windows, MCU clock
qualification, full800us WCET and assembled-robot gates remain pending. No native
sensor/motor setup or MCU run is authorized by this task's compile evidence.

Last deployed board firmware remains D091 source1502e948, its frozen inert
synthetic recorder image. Its old runtime measurements cannot validate this change.

## Final evidence

Full normal and ASan/UBSan suites each pass1327main cases/24484165assertions and
111enabled MotorGate cases/3850460assertions, no failure or skipped case. CTest
durations6.41s and23.97s exclude compilation. Sanitizer cache uses address+undefined
and frame pointers. Exact argv/exit/stdout and complete LastTest copies are in
full_host_include_retry1, full_sanitizer_include_retry1 and full_*_ctest.log;
validation_summary.json records final counts and current implementation/test hashes.

Independent author24cases/2421assertions pass both motor settings. Actual native
Reader/binding/owner5cases pass (24 parent isolation assertions; not a total of
child assertions), including100 no-allocation iterations. Seeded saturation/
sequence tests2cases30assertions,15config profiles, both actual inert-probe startup
modes1case14assertions each, all18established config registry checks and8controlled
upload refusal combinations pass. All7new Python methods have passing executions:
initial6 plus the corrected host method. These are host substitutes, not MCU ADC
or motor measurements. Exact commands/hashes/limits: raw/author/HANDOFF.md and JSONL.

Fresh separate same-model review PASS/no open BLOCKER/MAJOR/MINOR. Reviewer added
6adversarial cases/20059assertions normal and ASan/UBSan, including1350 source
bracket tuples, exhaustive metadata/clock-priority cases and observed full-wrap
aging. Review: state/reviews/P2_power_inputs_review.md and its raw directory.
358established source/test/tool files independently compared; no established test,
core behavior, native Reader, motor backend or original B16 value changed.

61existing controlled tooling methods pass: SSH/ADB argument handling, staging,
compile/upload separation and matrix/recorder guards. Seven existing inert source
hashes independently reconstructed/reviewed, then reproduced by actual staging
before updating only their values. No upload key or permission was added.

Actual board-Linux compile-only on bareUNOQ ADB2629958581 exits0 with source
4d5e21cc418a6089b593fe95c020b129787c63786a7e44511b183bef9e7d65da,
bench/p2_power_inputs_compile, pinned arduino:zephyr:unoq/core1.0.0,
MATCH0/MOTORS_ALLOWED0/default startup. Compiler reports321652program and
241524global bytes,20620 nominal residual with the low-memory warning preserved.
This is not measured loaded free RAM or worst-case stack use.

76current/staged/target source files match exactly. All three ELFs retain actual
Reader/InputOwner/Robot/MotorGate/native motor callbacks/AttemptRecorder paths and
the strong empty loop hook. Loader hash and188undefined imports match D092;
40native and42AEABI exports are nonzero, preserving prior fmod/sqrt evidence.
Constructor relocations resolve only passive factories/constructors; sketch setup
only stores the exercise pointer. Target/source/startup evidence is independently
reviewed. No upload/reset/MCU native ADC/GPIO or other runtime operation occurred.

## Preserved validation failures

First full host/sanitizer attempts failed because the new test fixture lacked
initializer_list. An explicit include corrected only that new fixture. Independent
author then detected40false failures at three doctest CHECK_FALSE ternary sites;
materializing each conditional result as bool preserved every expected rejection
and corrected macro decomposition. Passing full suites use the corrected tests.
Reviewer-only include/macro mistakes and source ordering assumptions are also
retained in its raw receipts. No production fix or assertion relaxation was needed.

The passing normal build reported generated Makefile timestamps0.3s/0.051s ahead
under WSL. Final LastTest counts include all24newcases and their2421assertions;
source hashes match the author's frozen files. A later settled_build_check exits0
with both targets current, no rebuild and no clock-skew warning. Sanitizer results
independently match the counts. No stale-binary success is substituted for testing.

## First unfinished task

P2_app_schedule_dependencies.md corrects the earlier simplistic deadline sum:
runtime IMU read is atomic, failure cleanup lies outside its source timestamp,
and MotorGate failure can invoke a second settle pass. QTR charging requires
sub-tick service; an eventual frame can still be color-ambiguous after long gaps.
Existing guards do not prove a complete800us schedule.

Next audit installed/primary I2C peripheral states and freeze a bounded resumable
native Bus/Acquirer contract before implementing app scheduling. Preserve the
single600us wall-clock deadline, poll budget, actual source freshness and cleanup;
pending work must never look like a new sample. No new timing allowance is selected
by that dependency audit. Full app composition, physical acceptance and human gates
remain pending; the full P0-P7 goal remains ACTIVE/incomplete.
