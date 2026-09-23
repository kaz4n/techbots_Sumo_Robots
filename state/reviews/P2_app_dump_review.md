# D101 actual Runtime dump attachment: independent safety review

2026-09-23 Asia/Dubai. Review baseline `f5f8f34`, public contract `8b4cc4d`
plus the explicit bad-receipt abort/skip clarification. This is a separate,
fresh-context same-model review; it is not cross-model review or a phase gate.
The reviewer owns only this report and `P2_app_dump_review_raw/` and has performed
no source/test/config/allowlist edit, shared build, board/network/upload or MCU action.

## Current disposition

**Verdict: TARGET-BLOCKED (FAIL for target acceptance); software-tested.**
Final source is
`836008588522b81c0f94435725a9b93cbd3cf826b871caf960285797b17b9db0`.
D101-R1 remains open. No additional local safety MAJOR or MINOR was found.
The compiler limit check does not establish loader fit, loaded free RAM, stack
margin or physical operation. This review does not approve an upload or claim
full B8, 800 us WCET or any human gate.

## Findings

- **D101-R1 BLOCKER, open:** `src/app/app.ino:14` instantiates the integrated
  Runtime/dump image. Final source `83600858...` passes MATCH/Immediate compilation
  at 257784 bytes, but its exact ELF requires a conditional pristine loader peak
  of 262400 bytes against the 262144-byte pool, 256 bytes excess. Its temporary
  global-symbol allocation needs 4136 payload bytes while the modeled largest
  available payload is 3900; the allocator chunk is already 240 bytes short,
  before the further 16-byte export copy. Evidence:
  `analysis/P2_app_dump_raw/target_summary.json` final MATCH entry and
  `P2_app_dump_review_raw/final_target_verification.json`. The source-derived
  budget includes copied regions and installed loader metadata lifetime; it is
  not an actual failed load. A known over-budget load model blocks target
  acceptance even though compilation succeeds. Reduce storage without changing
  evidence/config/capacity, then rerun final-source default and MATCH audits.
  Actual loaded memory remains separate.

The initial `96c80701...` image is preserved: default compiler257968/loader262576
(432 excess), MATCH compiler258344/loader262960 (816 excess). The final cache
change removes Runtime's duplicate last_robot_, saves 400 bytes of its target
object, and reduces MATCH compiler usage by560 bytes including changed code.
It initializes prior state BOOT and prior calibration context false, updates
both at the former postDecision copy point, and uses the current Transaction
result for same-epoch display/bias/calibration/STOP work. selectLineMode is the
only prior-epoch reader; its two cached primitives survive Transaction.open.
The current result stays valid through postDecision/display/service and finish.
The reviewed edit and expanded regression pass establish this narrow lifecycle
equivalence, but do not close the remaining 256-byte loader deficit.

## Independent local evidence

- Final `P2_app_dump_review_raw/review_1790185305598746699.json`: actual production
  Runtime/Transaction/Robot/MotorGate/recorder/Transfer sources copied into an
  isolated `/dev/shm` tree, strict warnings plus ASan/UBSan, both
  `MOTORS_ALLOWED/MATCH=0` and `=1`. Each passes the independently authored
  61 cases and 111569 assertions, combining all21 D101 cases with established
  configured D096 Runtime/projection coverage, including eight-stage calibration,
  raw/control handover and STOP tail after the cache edit. Only copied button-window values are
  synthetic; production `src/config.h` remains unchanged. The receipt records
  production/test hashes and the exact synthetic config. All production files
  still match `app_source_reconstruction_final.json`. This is a fresh rerun of
  independently authored tests, not a claim that this reviewer authored them.
  The earlier pre-cache19-case/2063-assertion reviewer run is preserved as
  `review_1790185040520157992.json`.
- The same receipt and factory-only `review_1790184874934156786.json` compile
  the actual `src/app/dump_port_unoq.cpp` with `ARDUINO_ARCH_ZEPHYR`, its real
  public headers, and reviewer-authored instrumented UnoQDumpPort methods.
  193 ASan/UBSan checks pass: two different owners, all 16 setup-grant
  combinations per owner, exact grant reference and return-status forwarding,
  both readiness values, identical output context/callbacks and no begin,
  readiness, write or cancel operation during factory construction. Native
  `UnoQDumpPort::port()` is also inspected and simply returns its three bindings.
- The first configured reviewer compilation failed at the new author's two
  `Transfer(second.port())` calls because they passed an app DumpPort instead
  of its output Port. The original rejection is retained in
  `review_1790184967939504034.json`; the author corrected only those test calls
  to `.port().output` before the successful rerun. This was a new test compile
  error, not a production regression or weakening of an established assertion.
- Root's final normal and sanitizer suites each pass2/2 CTest targets in
  `analysis/P2_app_build_raw/d101_host.txt` and `d101_sanitize_tests.txt`.
  The six established D096 tooling methods pass in
  `d101_runtime_tooling_package.txt`; their test-method ASTs are unchanged.
  Only the three now-required source dependencies were added to their build
  list. The first wrong package-discovery invocation and its four relative-import
  errors remain preserved in `d101_runtime_tooling.txt`.
- Author pre-cache receiver evidence (`analysis/P2_app_dump_raw/author/README.md`
  and `run_1790185111677398343`) passes real Runtime stream/strict Parser/exact
  CSV checks and publication for both motor settings. Both identical1268-byte
  streams contain2frames/3events, session1476/epoch86, CRC4237426210 and synthetic
  provenance. This receiver roundtrip predates the cache edit; the final reviewer
  rerun above covers the real pipeline afterward but did not rerun publication.
- `git diff --check` passes. Existing core, config and locked tests are unchanged
  against the review baseline.

## Safety and timing trace

- `Runtime::begin` keeps `Transaction::initialize`/MotorGate as the first
  native operation, checks existing source ports, completes source setup and
  only then calls `initializeDump`. Disabled dump invokes no dump callback.
  Any missing required callback produces CONTEXT without invoking another.
  Setup failures remain reported while sensor/control work proceeds, without
  retry, owner reconstruction, Linux wait or inferred readiness.
- `dumpReceiptValid` requires the actual DECIDED transaction, consumed and
  applied-valid feedback with its exact current Robot token, valid application
  time and acceptable Gate outcome. `dumpReadyContext` additionally requires
  current fresh nonzero-token IDLE/gate-IDLE authority, age below TICK_US,
  disabled/zero intended and actually applied outputs, and successful setup.
  The source uses the real transaction result, decision timestamp and retained
  recorder. It does not invent a decision, receipt, local intent or origin.
- A failed actual receipt aborts ACTIVE transfer immediately after application,
  before calibration/display/readiness or another byte. Its later service call
  skips Transfer.step and preserves CANCELLED/CONTEXT, as the explicit contract
  requires. Other actual results, including START/COUNTDOWN/STOP/fault, reach
  Transfer with false readiness where appropriate. Transfer remains the fuller
  eligibility/source/format/CRC authority and consumes only genuine local intent.
- The current clock is observed before readiness, after readiness, and after
  Transfer. The after-ready clock becomes Context.now_us; D is unchanged.
  Formatting, callbacks, writes and cancellation are inside the actual S..C
  epoch. The 999/1000/1001 us readiness-cost tests exercise freshness boundaries;
  callback cost appears in the final actual duration. Early calls do not pump.
- Runtime terminal failure first aborts the Transaction, which inhibits through
  MotorGate and preserves recorder interruption, then aborts Transfer before
  source cleanup. Clock reversals after readiness/write retain failed completion
  evidence, not a fabricated C. Abort cancels exactly once only while ACTIVE and
  preserves identity/history and passive reports. STOP reaches Transfer, retains
  one real final tail, then becomes passive. No reset/rearm path was added.
- The new source adds no motor writer, governor/edge override, inbound command,
  network/Bridge/Serial call, heap use, delay or loop. It binds the existing
  output-only native adapter. Its permanent native poison is unchanged.

## Native startup and existing inert keys

`app.ino` owns one fixed native dump owner and supplies its direct binding to
one Runtime-owned Transfer. Its `SetupGrants{}` remains unconfirmed, including
dump_enabled=false and every UART ownership/framing bit false. The factory
performs no peripheral operation. `final_target_verification.json` independently
checks all85 frozen source hashes against the final target collection and all3
downloaded ELF hashes; each retains176 imports. The actual ELF factory references
exactly its begin/ready forwarders and UnoQDumpPort::port. Its sole static
initializer constructs bindings/Runtime without native begin/ready/advance calls.
Runtime169968B, NativeSources848B and the single dump owner204B are retained;
no additional static thread appears. Actual main references the strong two-byte
empty loop hook, setup calls Runtime::begin, and loop calls Runtime::step.
The target audit also verifies39 native and42 AEABI exports,75 objects/125 metadata
texts and unchanged native UART/CSV object sections. Final-source default mode
was not recompiled after the cache edit; final MATCH remains blocked regardless.

`P2_app_dump_review_raw/inert_source_reconstruction_final.json` independently rebuilds
staged-byte identities without staging or transport. Baseline `f5f8f34`
reproduces all seven current allowlist keys exactly. Current source changes
for each key are exactly eight reviewed shared files: dump_port.h,
dump_port_unoq.cpp, runtime.cpp, runtime.h, runtime_dump.cpp, runtime_inputs.cpp,
recorder_dump.cpp and recorder_dump.h. Bench-local code/config/core/native HAL
bytes are unchanged, and the actual `app.ino` with its new owner is excluded.

The recorder_dump change only declares/defines the new nonvirtual
`Transfer::abort()`; old Transfer methods and layout are unchanged. None of the
seven bench paths instantiates Runtime or calls this new method. New app helper
translation units contain functions only, no new global or startup action.
These changes are behaviorally inert for the seven existing bench scopes.
Their source hashes nevertheless change; exact reconstructed maps/digests are
available for the coordinator's separately checked refresh. This reviewer has
not modified or regenerated the allowlist, added a key or granted an upload.
The coordinator intentionally leaves all seven old keys unchanged while the
separate recorder-memory follow-up is pending. The pre-cache reconstruction is
retained separately and is not the final source identity.

## Limits and remaining work

The compiled native factory probe verifies binding code, not registers/UART
execution. Native setup's previously documented unbounded device-init ACK waits,
physical UART/framing/cancellation, independent clock qualification, actual
loaded RAM/stack/full-tick WCET and all sensor/motor/human gates remain open.
The current attachment defaults disabled; it does not authorize enabling its
hardware grants. Post-STOP local reset/source lifetime and calibration snippet
delivery remain separate tasks. The next action is a separately contracted
lossless recorder-storage reduction, then new independent tests/source/target
review and final default/MATCH accounting. Keep D101-R1 explicitly open until
that evidence closes it; no phase gate or physical acceptance follows.
