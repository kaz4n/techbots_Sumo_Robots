# D096 actual application runtime validation

2026-09-23 Asia/Dubai. Baseline38d71d3, public contract36c251f. Active P2 software
under D051/D075; no physical acceptance or human gate follows.

## Delivered source and boundaries

Runtime owns actual Transaction/Robot/MotorGate/AttemptRecorder, InputOwner,
Estimator and Calibration. Fixed NativeSources forwards existing native HAL APIs.
app.ino now instantiates this actual pipeline with all setup grants unconfirmed.
It is no longer the earlier one-BOOT-step scaffold. Default MOTORS_ALLOWED0,
absent grants and upload refusal remain; the actual app is not an inert allowlist
entry and has not been uploaded or run.

The original1kHz release grid executes one actual epoch per due call and counts
missed slots without invented catch-up timestamps. QTR charge remains exclusive;
active discharge is advanced at least once each epoch; IMU retains its original
600us acquisition lifetime through caller work. Projection happens at actual D,
preserves genuine source identity and explicitly expires unavailable evidence.
RAW preparation/calibration can initialize without classified line data. Every
post-decision bias/calibration/display/cancellation operation belongs inside S..C.
STOP receives one real inhibited tail, then remains passive until reboot.

Three source corrections were independently verified: reject outer clock failure
before Robot; admit Gate A and validate last outer observation before completion;
prevent retained QTR lower bounds starving subsequent service. Legacy decide({})
and finish remain compatible. See P2_app_runtime_failures.md for original evidence.

## Host validation

Full normal and ASan/UBSan runs pass1411main cases/25187345assertions and173
motor-enabled cases/4536382assertions, zero failed/skipped. Following the new
fixture include correction, the final frozen-file rebuild is recorded separately;
the earlier exit2 and initial passing runs remain. Old locked/core/HAL files are
unchanged. No baseline assertion is weakened.

Independent author default builds pass37cases/68688assertions each motor setting;
isolated configured-button copies pass43cases/105510assertions each. Six tooling
methods pass78.026s, including eight actual-app upload refusals under substitutes.
Heap guards, required callback positions, real5.1s hold, bias application, eight
16-sample calibration stages, handover, source-age boundaries/wrap, and separate
all-white recorder sealing and clean STOP DRAINING/real-tail SEALED are exercised.
All five author final file hashes match their saved manifest. These are synthetic
host source traces, never sensor/competition evidence.

Fresh separate reviewer passes131711checks per motor setting under ASan/UBSan,
including24 injected clock positions, finite service/idle bounds, source expiry,
full-wrap nonrevival and actual later QTR completion. The only open review finding
is the real target RAM BLOCKER. Review/author original failures and fixes remain
in separate raw directories; reviewer did not edit implementation.

## Target result: BLOCKED, not compiled successfully

Exact source SHA256:
`4cb637f9be3e97225e2f894e9ce20002d72062dcee084ce14b9d14be161dd352`.
Actual UNO Q Linux Arduino CLI compile-only exits1 with the pinned1.0.0 core.
Reported program211444B; required memory276456B versus262144B, excess14312B.
No MATCH build, upload, reset, MCU peripheral access or motor operation occurred.
The previous deployed image remains D0911502e948 synthetic frozen recorder.

The failed build still produced three linked cache ELFs. Source/staging/remote
comparison matches all82 actual compiled files and aggregate hash; cached source
identity is not a passing Arduino memory check. Receipt source_integrity.json
explicitly sets target_compile_accepted=false. Captured offline evidence includes
sections, full symbol sizes, retained methods, imports, startup and initializer
disassembly. All188 imports and the base firmware hash match D092; no newly
unresolved import is hidden by the RAM failure. Final reviewer checks are in
state/reviews/P2_app_runtime_review.md and its raw directory.

The original fe65a3ad compile failure and linked images remain separately retained;
they predate the final clock/QTR corrections. No capacity or timing limit was
relaxed to repair memory. P2_app_runtime_ram_audit.md identifies bounded follow-on
experiments; none has been adopted or measured as a remedy in this task.

## Build tooling and provenance

Only the same seven existing inert source keys were refreshed after independent
byte reconstruction and actual local staging matched. No key, permission or app
upload path was added. Existing61 tool tests pass134.641s, exit0. Controlled fake
transport output saying UPLOAD belongs only to those script fixtures.

Root command wrappers retain exact argv, UTC start/end, output and exit statuses.
Raw evidence is binary-preserved by .gitattributes. Author tests use separate
public-contract expectations and isolated synthetic button-window config copies;
production windows remain unconfigured. Reviewer is a separate fresh same-model
context, not cross-model review. Established tests and locked safety files remain
unchanged. Host success does not qualify native timing, voltage, polarity or pins.

## Remaining work

Resolve the actual app memory blocker, then repeat accepted target builds and
startup/loader checks. Native UART/dump, local reset UI and calibration snippet
transport remain explicit P2 tasks. Actual complete800us WCET, loaded free memory,
QTR color/cadence, IMU mounting, button circuitry/windows, sensor/motor electrical
acceptance, EXPLAINED OK and human gates remain pending. No extra hardware is
requested now; continue eligible software work and preserve original deadlines.

Final index audit compares all82 actual compiled-source bytes, every raw receipt
and all five new test files to the Git index. A final trailing-blank-line cleanup
in test_app_projection.cpp changes no tokens; before/after hashes are retained in
test_eof_cleanup.json, while the author's original validated hash remains intact.
No test rerun is represented as having used a different source hash.
