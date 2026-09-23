# Bare-board actual Runtime probe options

2026-09-23 Asia/Dubai. Read-only design audit requested by the coordinator;
only this report is written. No build, board command, upload, reset, MCU read,
pin operation or source change was performed. P2 remains active under D051/D075.
The date is Wednesday23September: PLAN section3 schedules sensor benches for
24September and assembled P2 acceptance for26September. Neither is inferred.

## Recommendation

Add one small `bench/runtime_inert` that constructs the **existing actual
app::Runtime**, using a checked inert motors::Port and empty ADC/Source/Dump
ports, then calls `begin(app::SetupGrants{})`. Do not change Runtime or Robot
to make this probe work. Run real micros-paced Runtime::step calls for one
existing LOG_FRAME_WINDOW_MS interval (200s), then stop invoking Runtime and
freeze a compact diagnostic. This establishes loaded execution, scheduling and
sampled memory evidence for this exact no-source BOOT path. It does not create
a recording attempt or establish the physical app's load/WCET.

This is supported directly by tests/test_app_runtime.cpp's default-grants and
null-source/ADC cases: setup succeeds, real epochs run, state remains BOOT,
initialization remains false, explicit line/IMU/buttons remain absent and
battery remains invalid. No fake sensor frame, physical grant, synthetic START,
nominal battery value or asserted initialization is needed. D103 service reset
and D101 dump grants remain false; this does not exercise either active feature.

## Options and evidence boundary

| Option | Benefit | Limit / disposition |
|---|---|---|
| Upload existing exact D103 full app default ELF | Would measure that precise complete linked image | Reject for this scope: app.ino always constructs UnoQPort and Runtime::begin invokes MotorGate setup, which configures proposed header GPIO/PWM even with MOTORS_ALLOWED0. Existing app upload remains blocked. |
| New inert entry retaining every native singleton/path, replace only motor callbacks | Closer derivative of full app load; unused sensor/dump owners can remain linked but ungranted | Larger, separate image with its own initialization/call-graph review; still cannot claim the existing full app ELF was loaded. Diagnostic/code growth may exceed loader margin. Not fastest. |
| Minimal actual Runtime bench with absent source owners | Smallest safe implementation, genuine scheduler/Transaction/Robot/Gate/recorder object lifetime | Recommended. Native code/path elimination changes image allocation; actual bench free RAM cannot be copied into the production app budget. Recorder is allocated but EMPTY; no B8 retention or dump result. |

D103 target audit selects source1fbd7238: default conditional peak261056B leaves
1088B span/largest next allocation1084B; MATCH peak261448B leaves696B/692B.
Runtime is166304B, Transaction162544B, AttemptRecorder159200B; native sources848B
and dump owner204B. Thus even a few-hundred-byte diagnostic plus code/import/symbol
growth needs a new ordered loader audit. Removing references may recover code
and objects, but savings must be measured in the actual new ELF. No fixed
"diagnostic fits" assumption is justified. Leave capacities/cadence unchanged.

## Minimal frozen contract to author before implementation

- Probe phases NOT_STARTED/RUNNING/FROZEN/FAILED are distinct from RuntimePhase.
  Normal terminal probe is FROZEN while its last real Runtime report remains
  RUNNING/BOOT. Freeze after a completed epoch whose real elapsed time reaches
  the interval; never manufacture a STOP, SEALED recording or Runtime fault to
  obtain a stable snapshot. Terminal poll calls perform no clock/callback/write.
- One fixed Runtime object, no second Robot/Recorder or copied RuntimeReport.
  At most one Runtime::step per poll, existing release grid and skipped-slot
  semantics. Timestamp input comes only from actual micros through the Gate
  callback. No fast-forward, catch-up loop, sleep, allocation or remote input.
  Use an explicit bounded repeated-clock/half-range failure rule and saturating
  counters; elapsed duration and aggregate successful epochs are both retained.
- Inert callbacks validate each channel/period, count their acknowledgements,
  reject and latch any enabled EN/nonzero PWM request, and never use Arduino GPIO,
  PWM, ADC, Wire, UART, Bridge or native motor APIs. Unit periods are inert integer
  representations, not a PWM frequency. Compile-time MATCH0/MOTORS_ALLOWED0.
- Every completed epoch must have valid real S<=D<=application<=C chronology in
  the unsigned half-range domain, fresh strictly advancing nonzero Robot token,
  matching consumed Gate receipt, timing_valid/finished, BOOT/inhibited zero
  outputs and unavailable physical inputs. Preserve all observed Runtime,
  Transaction, Robot and Gate faults; define exact expected absent-input status
  from the frozen public contract and independent fixture before authoring tests.
- Record epochs, first/last S/D/C, token, actual elapsed, skipped releases,
  maximum full Runtime S..C duration and separately maximum outer probe step
  duration. Diagnostic publication/checking after C is outside Runtime timing;
  outer duration includes it only if actually bracketed. Track gaps and
  continuation failures explicitly. A max below800us applies solely to this
  instrumented absent-source path, never full-app acceptance.
- Concrete duration/count recommendation using unchanged config: anchor at the
  first completed epoch's actual S; normal completion requires C-S_anchor >=
  LOG_FRAME_WINDOW_MS*1000 (200000000us), at least
  LOG_FRAME_WINDOW_MS*1000/TICK_US (200000) completed epochs, zero skipped
  releases and no chronology/receipt/output failure. Permit the ordinary final
  boundary epoch; do not demand an exact count from a jittering real scheduler.
  Freeze FAILED immediately on a missed release or invariant failure, and in
  every case by (LOG_FRAME_WINDOW_MS+BTN_LONG_MS)*1000 (201000000us) after that
  anchor if normal completion has not occurred. Bound absence of a first epoch
  by BTN_LONG_MS*1000 after begin; bind unchanged-clock stalls to
  APP_CLOCK_STALL_MAX_POLLS (65536), tracking progress across poll calls.
  Use uint64 arithmetic for products and bounded unsigned32 time deltas.
  These are probe admission thresholds, not changes to core scheduling rules.
- If cleanup chooses Runtime::abort on failure, preserve the first probe cause
  and pre-abort report before recording actual abort/halt facts; resulting
  Transaction ABORTED is not a physical STOP or a new completed epoch. Normal
  freeze does not require abort because every callback is inert and outputs
  already zero; it must not relabel last RUNNING/BOOT as STOPPED.
- Fixed little-endian words with schema/version/size and zero reserved fields;
  no opaque C++ struct dump as public ABI. Retain rejected-active-write counters,
  callback setup counts, state/input-presence mask and recorder EMPTY/counts.
  Use nonzero even front/tail sequence with memory barriers; freeze success and
  explicit failure equally. Successful completion must never mask faults/loss.
- Reuse D091's validated current-thread region and sampled PSP technique with
  the exact installed ABI assertions. Sample at real clock callbacks, name the
  value sampled_headroom_bytes. Do not call the zero-address stack-space export,
  paint stack, infer watermark or claim reset-path stack use: D103 reset does
  not run here. Count samples and keep invalid metadata/faults explicit.

## Exact implementation ownership and tooling delta

1. **Probe owner:** new bench/runtime_inert/runtime_inert.ino and a small
   src/runtime_bench.h/.cpp plus src/runtime_native.h/.cpp beneath that bench.
   Public pure runner/diagnostic contract first; native wrapper owns only micros,
   stack sampling and publication. Reuse D091 callback/stack/publication patterns,
   not its synthetic input generator or duplicated Robot/Gate/Recorder runner.
   All new test duration/poll tunables belong in config.h if existing constants
   cannot express the chosen interval; do not hide tunables in the bench.
2. **Independent test owner:** new tests/tooling/runtime_bench_cases.cc and
   test_runtime_bench_runner.py (or bounded equivalent) against actual Runtime;
   cases for BOOT chronology/lifetime, absent sources, terminal idempotence,
   clock faults/wrap/equality, rejection of active output, skipped releases,
   real callback failures and complete report preservation. Established and
   locked assertions remain unchanged; do not import the huge host Fake trace
   array into target firmware.
3. **Build owner:** tools/board_tool.py currently stages shared core/hal/app into
   every bench, so no staging framework is needed. However D100's checked
   no-library policy is *app-only*, and app_build_policy.py pins app.ino and its
   artifact names. First compile-only using the existing bench recipe is valid
   only if actual imports/strong empty loop hook and ordered memory fit pass.
   Prefer explicitly extending the checked policy to this one named bench with
   exact runtime_inert.ino project/artifact binding, MATCH0/MOTORS_ALLOWED0 and
   default startup, plus independent negative tests. This avoids assuming the
   stock bench recipe's known RouterBridge cost will fit. Do not silently
   generalize all bench recipes or weaken D100 effective-property/compiler/hook
   checks. Coordinator owns these tools; probe implementer owns no build policy.
4. **Upload guard owner:** new name in board_tool.py's explicit inert allowlist,
   default-startup-only restriction, and one reviewed aggregate source key in
   tools/p0_inert_sources.json. MATCH/upload refusals remain. Add tests proving
   altered source, wrong target, Immediate and MATCH cannot take this route.
   Review actual ELF/ZSK, constructors/entry/loop and retained imports before
   adding approval. No native motor entry or callback may be reachable.
5. **Capture owner:** new tools/runtime_capture.py, not a repin/redefinition of
   D091 recorder_capture.py. The old helper is deliberately pinned to its exact
   artifact, recorderDiagnostics symbol and296B schema. Reuse only reviewed pure
   validation/heap decoding and appropriate bounded traversal helpers; keep old
   hardcoded purposes and tests intact. New capture pins exact artifact path,
   ELF/ZSK/loader/tool/config and runtimeDiagnostics offset/size. No address,
   size, command or arbitrary artifact CLI escape. Independently test all bounds,
   immutable terminal ABI, enums, chronology and rejection before any MCU read.
6. **Evidence owner:** new contract/decision, run scope, target/source audit,
   receipts, fixed-schema decoder tests and capture assessment under state/.
   Subsequent FACTS/PROGRESS/TUNING_LOG must say "actual inert Runtime BOOT".
   Independent reviewer owns final source/ELF/tool approval and failure checks.

## Positive runtime acceptance

Require exact deployed loader and new sketch bytes before private RAM. Decode a
terminal successful report with nonzero coherent sequence; all reported runtime
and transaction/receipt invariants must pass, no active callback attempted,
initialization false and recorder EMPTY with0frames/0events. Elapsed must cover
the real interval with advancing completed epochs and retained missed-release/
duration values. No zero-duration or synthetic-clock completion is acceptable.

Using D091's pinned262144B LLEXT allocator layout, take two full bounded pool
snapshots, independently decode/compare metadata, and reread the diagnostic and
24B heap descriptor unchanged. Report actual free payload/largest block only
for this image at those terminal samples. Preserve raw reads, command times,
hashes and failures. CAPTURED is a transport/read result; a separate assessment
decides whether this specific experiment met its invariants.

Keep <=48read attempts, <=2MiB cumulative, <=16KiB/RAM read, <=64commands,
<=600s sequence and <=30s/command unless a separate reviewed contract explicitly
changes them. D091's completed capture used47reads, leaving only one read spare.
New ELF/ZSK size can require another64KiB flash chunk: calculate the complete
read budget from the actual package before execution, never auto-raise it.
No Cortex attach/halt/reset/write/daemon action inside capture. Capture after
terminal freeze, so slow MEM-AP reads do not purport to measure running tick load.

## Open facts / limitations

The new probe has not been implemented, built or reviewed. New memory fit,
constructor safety, imports, diagnostics ABI and capture byte/read budget are
blocking prerequisites to its upload. F113's sampled stack method and private
heap decoder remain valid only after exact loader/ABI identity is rechecked.
SC-AJ clock calibration remains unresolved: elapsed and timing are MCU-clock
measurements, distinct from host monotonic command brackets. Full-app loaded RAM,
historical stack peak, D103 reset stack/latency, native sensor/UART paths, physical
buttons, motor behavior, five-minute all-live800us criterion and every human
phase gate remain unproved by this experiment. No new physical fact is needed
to prepare this strictly absent-source probe; retain the user's bare-board run
authorization and freeze a concrete reviewed run before execution.

Sources inspected: AGENTS.md; PLAN3; P2_hal_bench.md; HARDWARE.md; BEHAVIOR B14/B15;
FACTS F113/F114/F126; DECISIONS D091/D101-D103; P2_recorder_bench_contract.md and
run.md; P2_service_reset_target_audit.md; actual Runtime/Transaction/MotorGate,
bench/recorder_inert, recorder_capture.py, board_tool.py/app_build_policy.py and
default-grant Runtime tests. No external memory guidance matched this repository.
