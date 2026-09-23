# Missing B3 named bench: bounded design inventory

Read-only proposal, 2026-09-24. No policy adoption, source change, measurement or
hardware permission. This date matches PLAN section3's sensor-bench software day;
PROGRESS remains authoritative and physical/human gates remain open.

`docs/prompts/P2_hal_bench.md:13` requires rest bias, less than2deg drift over60s,
hand-rotated360deg within3deg, and read time within the tick budget. Existing
`bench/p2_imu_*_compile` sketches retain never-called methods; they do not implement
this trial (`bench/p2_imu_heading_compile/src/imu_heading_probe.cpp:8`).

## Reuse the actual owners

| Existing source/public seam | Bench use and limit |
|---|---|
| `src/hal/imu_acquisition.h` Acquirer | One native owner containing its Bus and Setup. Direct start/advanceSetup/setupFailure; beginRead/advanceRead/cancelRead. Retain SetupReport and SampleProgress unchanged. Do not instantiate another Bus or use legacy read alongside pending work. |
| `src/hal/imu.h` SetupReport; D080 `P2_imu_setup_contract.md` | PROFILE_READY means checked fixed profile/readbacks. Setup has48 bounded Bus calls, mandatory waits,1s exclusive deadline and1024 advances. It does not prove settling or healthy physical rate. |
| `src/hal/imu_acquisition.h` Sample; D081/D094 contracts | Only completed progress supplies a Sample. PENDING is empty, NO_NEW is absence, and OBSERVATION supplies a new accepted sequence. Native timestamps are observations, not sensor-generation timestamps. Silence is20ms; an acquisition retains one600us/8192-pass budget. |
| `src/hal/imu_heading.h` Estimator | Runner owns this pure object: begin(Mounting, initial_bias), observe each completed Sample once, applyBias once after acceptance, report. Continuous unwrapped yaw and raw/corrected body-Z rate are already implemented. No duplicate integrator. |
| `src/core/countdown.h:126-178` Services | Reuse explicit gyro presence/source-time/sequence admission and D024 mean/min-count/spread policy, subject to the bench-anchor clarification below. No Controller, Lifecycle, Robot or MotorGate is needed. |
| `src/app/runtime.cpp:109-145`, `src/app/runtime_inputs.cpp:173-175` | Existing composition illustrates completed-only estimator delivery and future-increment-only bias application. Do not instantiate Runtime or `app::NativeSources`: the latter also owns opponents/QTR/ADC/matrix (`native_sources_unoq.h`). |

Relevant preserved decisions: D079-D082/D094 native and estimator contracts,
D024/D083 calibration admission, and D059 continuous HAL yaw. Defaults in
`src/config.h:54-78,93,107,201-205` remain unchanged. Mounting defaults to zeros/
unconfirmed; D082 requires a confirmed proper signed permutation, body X forward,
Y right, Z down. No physical map can be inferred from the board or example probes.

## Smallest useful trial

Propose one finite calibration-plus60s observation trial per owner/boot. The same
trial is later run separately and externally labelled STILL or HAND_ROTATION;
there is no remote command, interactive transport, motor or extra input owner.
The physical plan will define when a person rotates and how the true360deg endpoint
is established. Software cannot infer rest or completion of a human rotation.

Native owns only one Acquirer, forwarding clock/start/advanceSetup/beginRead/
advanceRead/cancelRead/setupFailure. Runner owns Estimator, Services and fixed
evidence. Construction, port creation and report/capture accessors are passive.
Sketch asserts MATCH=0/MOTORS_ALLOWED=0 and uses all-false grants. Required future
permissions are explicit enable, exclusive native I2C use, confirmed valid power,
confirmed mounting and rest for calibration. Missing permission never initiates
I2C. Passing true is caller evidence, not proof created by the bench.

Recommended phases: DISABLED, SETUP, CALIBRATION, MEASURING, COMPLETE, FAULT.
There is one begin attempt; terminal reports/captures remain stable. Setup gets
at most one advance per elapsed TICK_US release, with no catch-up burst: polling
every Arduino loop would consume1024 advances before mandatory waits expire
(`src/hal/imu.cpp:156-160`). Native start is passive. After PROFILE_READY, begin
at most one acquisition per TICK_US release; while PENDING, each poll advances it
once without waiting for the next tick. A one-kHz-only advance schedule cannot
satisfy the existing600us aggregate deadline. Do not relax either deadline or
the estimator's2000us continuity limit to make a trace pass.

Feed completed samples once to the actual Estimator, then map raw body-Z/presence/
sequence/source time into ServiceSample with the actual post-acquisition delivery
clock. ABSENT must remain absent, invalid results remain invalid, and pending
work must never be fabricated as NO_NEW. Start calibration only after setup;
use the original [1500,4500)ms window, minimum2 and spread<=2dps. A rejected
calibration ends this trial with retained evidence, rather than silently using
zero bias for an acceptance measurement. Apply accepted bias exactly once, with
no yaw reset. Anchor measurement at the first subsequent updated heading and
finish at the first updated source observation at least60000000us later. Retain
actual endpoint times/span; do not interpolate a fictitious exact60s sample.

Keep a fixed summary plus a proposed61-entry checkpoint bank (anchor and first
fresh observation at each1s boundary). Record every observation in aggregate
counts/extrema even though raw history is not fully retained. Minimum evidence:
setup/result diagnostics, current/failing Sample and Estimate, calibration result,
anchor/final source times and sequences/headings, exact applied bias, signed yaw
delta, min/max relative yaw and maximum absolute excursion, observation/NO_NEW/
pending/missed-release counts, maximum observed source gap, and timing maxima.
Each checkpoint copies real source time/sequence, heading and rates. No overwrite,
fabricated points or loss-hidden average. Capacity/size and final RAM fit require
actual compilation before acceptance;61 is a proposal, not an installed constant.

For STILL, retain both endpoint drift and maximum observed excursion; a quiet
endpoint must not hide earlier movement. For a separately evidenced clockwise
rotation retain delta-360deg (and absolute error); counterclockwise uses the
declared-360deg reference. Do not choose direction or assert true angle in code.
These comparisons require verified external trial labels and physical reference.

## Decisions and evidence still needed before implementation

1. `Services::start` currently documents a Controller-qualified release anchor.
   Adopt an explicit bench-only timer-anchor use of the same averaging service,
   without fabricating START/GO or changing its windows/acceptance. Otherwise a
   new shared calibration seam is needed; duplicating averaging is less desirable.
2. Freeze exact Port/header, all-grant precedence, cadence/missed-release math,
   setup/progress shape checks, source-versus-delivery chronology and terminal
   cleanup before independent tests. Keep the old source era through each closing
   clock; check accumulated half-range as well as consecutive deltas.
3. A wrapper fault with possibly pending acquisition must cancel exactly once;
   preserve the first fault and separate returned cancellation/clock evidence.
   Known terminal native faults already performed their cleanup. Setup has no
   public abort, and successful completion is not peripheral shutdown. Do not
   invent a disable/reset or destroy/reconstruct the boot-lifetime owner.
4. Freeze measurement/checkpoint durations and counts in config, and define finite
   wrapper poll/attempt limits without pretending they create physical WCET or a
   watchdog when polling stops. Callback S..A, poll S..C, native acquisition span
   and inter-service gaps are distinct evidence; closing publication is excluded
   explicitly. A maximum observed poll or600us guard is not the full800us app WCET.

Independent tests should cover default sketch plus10000 loops with zero calls;
one native Acquirer only; setup wait pacing/readiness/failure; pending pulses,
empty payload and cancel-once; NO_NEW versus actual observations; exact D024/D083
boundaries/rejection/bias application; constant/ramp/wrapped yaw without reset;
natural time wrap/reversal/aggregate half-range;2000us gaps and600us equality;
60s endpoint, intermediate excursion, checkpoint immutability/hidden failed
closure, counters and terminal silence. Preserve all existing locked assertions.
Use synthetic maps/rotations only as labelled software fixtures.

The next bounded task is an adopted contract and declaration-only headers, then
independent implementation/tests in the five new `bench/imu_heading` sketch/src
files plus README. Coordinator separately owns config, literal checked compile
policy, target source/ELF/startup/import/loader audit and state records. Default
and Immediate may be compile-only; MATCH/upload/profiles must refuse until an
explicit later physical plan is authorized. No new inert-upload key is needed.

F103/F104/F105/F117 establish narrow software evidence. They do not establish
MPU breakout supply/address/pull-ups, actual mounting, stillness, calibrated time,
sensor generation synchronization, drift, rotation accuracy or whole-app timing.
Those physical prerequisites, frozen-bank readout/provenance and an actual
time-correlated human measurement procedure remain separate work.
