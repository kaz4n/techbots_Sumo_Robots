# D096 fresh-context independent runtime review

2026-09-23 Asia/Dubai. Baseline `38d71d3`; contract `36c251f` plus visible
decideFrom, pure clock admission and finishAfter clarifications. Separate
same-model reviewer; no cross-model or physical review is claimed. This reviewer
changed only this review and its raw directory; no implementation, established
tests, config, board operation, shared build or commit.

**Final scoped disposition: TARGET-RAM-BLOCKED.** The actual app fails the target
memory acceptance check. Two software MAJOR findings have been fixed and
independently rechecked. Final source reconstruction and failed-link target
receipt inspection are complete for source
`4cb637f9be3e97225e2f894e9ce20002d72062dcee084ce14b9d14be161dd352`.
No human phase gate is approved. This review's test claims are scoped to the
independent results below; root's broader host suite is separate evidence.

## Findings

1. **BLOCKER, open: actual app exceeds the target memory limit.**
   `src/app/app.ino:13` instantiates the real Runtime with all retained source
   bindings. The final actual app compile (source `4cb637f9`) reports 276456 bytes
   against 262144 bytes, exceeding it by 14312 bytes, and exits 1 with "data
   section exceeds available space in board"; program size is211444 bytes.
   Evidence: `state/analysis/P2_app_runtime_raw/target_compile_final.json` and
   `.txt`. The earlier `fe65a3ad` failure (276368 bytes,14224 excess) is preserved
   in `target_compile_01.json` and `.txt`.
   This is a failed target build, not successful target qualification. Cache ELF
   inspection can establish linked paths but cannot turn this result into an
   accepted firmware image. Reduce actual image memory without weakening
   recorder capacity, timing, grants or safety contracts, then repeat the real
   compile and review its exact source/ELF identity. Loaded free RAM remains a
   separate measurement even after the compile limit passes.

2. **MAJOR, fixed: regressed decision clock created a false Robot decision.**
   Original `Runtime::project` encoded a late outer-clock regression as
   `line.contract_valid=false`; Transaction then stepped Robot, applied Gate and
   consumed recorder output before Runtime aborted. It inhibited motion, but
   attributed an application clock failure to a fabricated LINE_CONTRACT/STOP
   decision. The two-line original policy is explicitly reconstructed only in
   an isolated source copy in
   `P2_app_runtime_review_raw/clock_results_1790177491661606760.json`:
   injection 8, S=10102, D=10106 after outer clock10107, decision_made=true.
   The current pure `clockAccepted` seam (`src/app/transaction.cpp:83`) rejects
   this before Robot/Gate.apply/recorder.consume. The current actual-source
   regression has decision_made=false and no fabricated successful duration.

3. **MAJOR, fixed: outer post-work chronology escaped S/D/A/C validation.**
   The original Runtime failed to admit Gate's actual A into its clock history,
   and validated C only after Transaction had published completion. The actual
   source receipt `clock_results_1790177329208937573.json` demonstrates both:
   injection10 allowed post-work clock10108 after A10109; injection12 rejected
   C10110 after last outer10111 but retained finished=true/timing_valid=true.
   Runtime now admits A at `src/app/runtime.cpp:321`; `finishAfter` checks the
   last actual outer observation before publishing completion at
   `src/app/transaction.cpp:133`. Both cases now terminally inhibit with
   finished=false/timing_valid=false. Legacy finish remains unchanged.

No additional open MAJOR/MINOR implementation finding was found in the reviewed
runtime, projection, native binding or application entry path. The RAM BLOCKER
prevents successful D096 target delivery despite the scoped software checks.

## Independent evidence

`P2_app_runtime_review_raw/reviewer_clock.cpp` and `run_independent.py` build
isolated copied production sources in `/dev/shm`, with actual Runtime,
Transaction, Robot, MotorGate, InputOwner, Estimator and Calibration. No shared
test fixture is used. Final current-source receipt:
`clock_results_1790177704141226046.json`, 131711 checks per MOTORS_ALLOWED=0/1
under AddressSanitizer and UndefinedBehaviorSanitizer, both exit0. This includes:

- 24 adversarial clock positions, rejection before Robot for bad D, rejection
  without completed evidence for bad A/post-work/C, and passive terminal calls.
- Exact 65536 equal idle polls and 8192 frozen QTR charge passes; bounded abort,
  active-source cancellation once, no fabricated Robot decision or positive PWM.
- Real synthetic QTR charging/discharging service with no IMU advance while
  charging; one completed IMU observation forwarded into the actual Estimator.
- Retained CONTROL discharge that already crossed the threshold still receives
  one actual service in the next epoch and completes the same source; the worker's
  first-pass correction prevents indefinite frame starvation.
- IMU publication at age1999/2000/2001, canonical invalid projection after expiry,
  retained original publication identity, QTR absence at6000, and no revival
  after three valid clock increments span a whole uint32 clock wrap.

Two reviewer-harness mistakes are preserved, not production failures:
`clock_results_1790177298178585580.json` used a default injection index999 that
interrupted the frozen-clock test; it was changed to UINT32_MAX.
`clock_results_1790177439695088117.json` is the compiler rejection for a missing
standard initializer_list include; the include was added before rerun. Historical
source reconstruction is labeled separately from actual-source validation.

## Source review and limits

The native SourcePort forwards each operation to its fixed existing HAL owner.
Its factory and constructors add no peripheral operation; UnoQPort's factory
calculates periods from fixed device-tree/config values. Runtime initialization
calls MotorGate first, validates required granted callbacks, and keeps all
default grants false. Setup/read/cancel for ungranted sources remain absent.
The default app neither invents an axis map nor confirms button/color thresholds.

Runtime service loops are finite and preserve QTR exclusive charging. IMU
pending is serviced under the actual Acquirer's original lifetime; no retry or
new operation occurs inside the pump. Projection validates original reports
before expiry, retains source identity, keeps RAW bootstrap independent of
classification, and passes the exact decision snapshot to Calibration. Source
review confirms real STOP cancellation and one later due inhibited tail, with
recorder sealing checked before passive STOPPED. Matrix work is inside S..C.
Ordinary timing overruns remain logging rather than a new runtime stop policy.

The seven existing inert sketches do not instantiate the app's Runtime globals;
the shared app sources introduce functions/classes only. The independent
`inert_source_reconstruction.json` contains every file hash and aggregate for
exactly the seven existing keys (82-86 files each), reconstructed without the
staging implementation or board access. App.ino is excluded, the seven shared
app support files are included, and no key is added. Root's subsequent
`state/analysis/P2_app_runtime_raw/manifest_refresh.json` matches that independent
reconstruction. This is narrow source approval for those existing inert keys;
it grants no app upload key or permission to operate motors.

The earlier failed-image receipt was independently inspected in
`target_review_fe65a3ad.json`. It has 82 source files and three cache ELF artifacts,
188 imports each, 40 nonzero native and42 nonzero AEABI export addresses. It is
explicitly stale in runtime.cpp/transaction.cpp/transaction.h and lacks finishAfter;
therefore it cannot validate the final corrected source. Core and locked-test
diffs against38d71d3 were empty.

The final `target_review_4cb637f9.json` independently matches all82 local source
files against the final downloaded compile receipt and reproduces its aggregate
hash. All three failed-build cache ELFs retain Runtime, NativeSources,
decideFrom/finishAfter, MotorGate.halt, resumable IMU, QTR and ADC owner paths.
`final_startup_review.json` confirms12 init-array relocation entries,188 unchanged
imports, unchanged loader hash,40 nonzero native exports and42 nonzero AEABI
exports. Setup zeroes the13-byte grant object then calls Runtime.begin; loop
binds Runtime.step. The app constructor only initializes storage and calls the
passive port factories and Runtime constructor. Actual main binds initVariant,
start_static_threads, setup, loop and the strong empty loop hook. Inherited
Bridge/serial/C++ runtime startup remains present and is not a new qualification
claim. This verifies exact linked cache evidence, not successful target compile,
loader acceptance, startup execution or loaded RAM.

No sensor accuracy, physical QTR/IMU timing, independently calibrated clock,
all-sensor800us bound, loaded memory minimum, UART dump, local reset UI, electrical
acceptance, PINMAP OK, STAND OK, RING OK or human P0-P7 gate follows from this work.
