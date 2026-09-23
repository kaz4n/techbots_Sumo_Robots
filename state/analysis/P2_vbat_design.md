# P2 B5 voltage bench design input

2026-09-24 Asia/Dubai. **Proposal only, not an adopted contract or implementation.**
Read-only investigation while the coordinator finishes D109. Only this new file
is authored here. No board call, upload, pin operation, source/config/ledger/test
edit, or claim of physical acceptance. Thursday24September is the scheduled
sensor-bench day in PLAN section3; D051/D075 permits software preparation despite
the still-pending human gates.

## Existing facts and minimal scope

P2_hal_bench.md B5 names `bench/vbat` and requires error within0.05V against a
multimeter over9.5..12.6V. D078 supplies the actual fresh-only native A0 reader;
D086 preserves its battery-only profile. D093's10ms cadence is useful here, but
its InputOwner is unsuitable: `readerInputPort()` unconditionally forwards setup
to `beginWithButtons()` and exposes A1. Do not reuse that owner or create a second
ADC owner just to obtain scheduling.

Use exactly one `power::Reader`, direct `begin()`/`read()` callbacks and its
`micros()` domain. No A1 call, arbitrary channel, InputOwner, app Runtime, Robot,
MotorGate, QTR, IMU, matrix, UART/Bridge or other peripheral owner. Construction,
destruction and native-port creation remain passive. All ADC1/ADC4/PA4/DAC1,
clock/supply exclusivity obligations remain D078's; a local grant cannot prove
external/thread exclusivity or repair incompatible hardware.

The sketch uses `static_assert(MATCH==0 && MOTORS_ALLOWED==0)` and
`runner.begin(Grants{})` with `exclusive_adc=false`. False grant takes precedence
over port/config checks and returns an inert DISABLED state without even a clock
callback. This checked-in revision is compile-only and performs no ADC I/O.

## Proposed public surface and finite capture

New bench-local `src/vbat.h`, `vbat_native.h`, implementation partners and
`vbat.ino`/README. Namespace `vbat`:

- `Port{void* context; clockUs; beginBattery; readBattery}` uses the exact existing
  `power::InitResult` and `power::Sample` return types. No cleanup/reset callback.
- `Grants{bool exclusive_adc=false}`; noncopyable `Native` owns one Reader and
  returns `Port port()`; noncopyable `Runner` copies its port without I/O.
- `Runner::begin(Grants)`, `poll()`, const `report()`, `captureCapacity()`,
  `captureCount()`, `const Capture* capture(index)`. No restart or stop API needed.
- Phases NOT_STARTED/DISABLED/RUNNING/COMPLETE/FAULT. First fault distinguishes
  PORT/CONFIG/SETUP/ADC/CONTRACT/SOURCE_ORDER/CLOCK; preserve independent clock
  failure information even when a native failure takes precedence.
- `Capture` holds the unchanged accepted `power::Sample`, actual wrapper S/A/C
  observations, and qualified native/call/poll durations. Array position is the
  capture identity; Sample has no native sequence and none must be invented.
- `Report` retains actual init and latest attempted Sample, source-attempt and
  source-accepted flags, one-call fresh pulse, immutable first failure result,
  captured/attempt/not-due/missed-release counters, saturation indication, and
  setup/read/poll timing with separate measured/invalid flags. Report access is
  passive; retained data is diagnostic history, never a current cached voltage.

Recommend one new count constant `config::VBAT_BENCH_SAMPLES=128`, adopted by the
coordinator with its literal-registry expectation. Reuse existing
`VBAT_SAMPLE_PERIOD_US=10000`; do not tie capacity to QTR's separate count.
At ideal cadence128samples span1.27s, not a guaranteed physical duration. Store
the first128 accepted records once, without ring overwrite, allocation, averaging,
rounding, clipping, or filtering. Exact struct/target RAM fit must be checked.
Zero capacity fails CONFIG before callbacks in the granted path. Capacity1 is
a useful executable boundary. Published slots remain immutable through fault.

## Acquisition, validity and timing

Begin attempts once, brackets one native begin, and accepts only coherent
OK/ready=true/NOT_ATTEMPTED. Repeat begin is passive and cannot clear a fault.
First poll after healthy setup is due; later reads are due at accumulated age
>=10ms from the preceding accepted source start. Poll is O(1), with at most one
native read and no delay, catch-up burst or extra read. A late release performs
one read and records skipped periods; reanchor to that actual accepted source.
Freeze after capacity or the first fault. A frozen outer clock can prevent a
future scheduled read: fixed capacity is not an independent wall-time watchdog.

Use consecutive unsigned deltas<2^31, allowing equality and natural wrap.
Accumulate source age across all observations rather than reviving old timestamps
after a full observed wrap; reject an aggregate half-range. As elsewhere, a full
unobserved wrap is unknowable. Source success must lie within the actual native
call's S..A bracket, with start<=completion and native span strictly<100us.
No timing success follows a reversed/half-range observation.

Accept native success only for known statusOK, valid=true, shutdownNOT_ATTEMPTED,
raw<=16383 and finite voltage exactly equal to D078's float expression:
`float(raw)/16383.0F * VBAT_ADC_REFERENCE_V * VBAT_DIVIDER_RATIO`.
Current constants3.3V and122/22 are nominal. Raw0/voltage0 and raw16383 remain
legitimate software data;9.5..12.6V is the eventual test range, not an acceptance
clamp. A repeated numerical value is allowed when produced by a new bracketed
call. Old timestamps outside the new bracket fail SOURCE_ORDER. Neither a
plausible value nor a callback stub establishes physical battery connection.

Read S before call, A immediately after it, and C after validation/tentative
record copy/counter work. Setup uses the corresponding actual bracket. Store
source S..A timing separately from wrapper S..C, explicitly excluding closing
publication/return. Publish a new immutable slot/fresh pulse only after C passes;
bad C hides the tentative slot and preserves previous count. The final accepted
poll returns fresh=true while entering COMPLETE; the following passive poll
clears fresh only. No formatting/transport occurs inside acquisition.

Preserve the actual native failure result and its Shutdown. Known non-OK with
valid=false takes native-failure precedence; unknown enums or contradictory
success shape are CONTRACT. Evaluate failed timing separately, without applying
the success-only100us rule to a native failure whose cleanup extends its span.
Native bounds remain100us conversion plus its separate100us fault cleanup,
4096poll limits, and setup100/5000/2minimum/100us with65536poll guards. Wrapper
timestamps do not abort a blocking callback or establish physical WCET.

**Reader has no public stop/disable API.** On COMPLETE or a wrapper-only fault,
cease callbacks and retain its actual last Shutdown (normallyNOT_ATTEMPTED).
Do not synthesize DISABLED, inject a failing read, change registers, destruct and
recreate a Reader, or claim current ADC quiescence. Native faults already own their
bounded cleanup; do not duplicate it. The native boot-lifetime claim remains.

## Independent tests and target-policy integration

Freeze the adopted contract/public headers before independent tests. Cover false
grant/passive constructors/startup/repeat begin, absent callbacks/config/capacity,
exact setup shape, first/due/not-due/late/no-burst cadence, raw endpoints and
identical fresh values, exact scaling/nonfinite/unknown statuses, source brackets,
100us equality, natural/aggregate wrap, clock failures including C, native-failure
precedence and retained shutdown, immutable capture/capacity1/128/final fresh,
terminal no-callback behavior and timing labels. Inspect saturation branches
without claiming billions of calls were executed. Preserve every old assertion.

Separate counted-method tests compile the actual Native binding and prove one
Reader, battery-only begin/read, no buttons method, no I/O in factory/constructor,
and default sketch setup plus10000loops makes no native/clock calls. Run the
existing D078/D086/native-pins regressions as relevant; synthetic callbacks are
not actual ADC measurements. Keep actual native-driver tests distinct from the
binding substitutes and maintain process isolation for its boot-lifetime claim.

Extend only the existing checked-build literals: `tools/board_tool.py` sensor
bench tuple/project map and `tools/app_build_policy.py::selected_project` add
`bench/vbat`/`vbat.ino`. Preserve all property/dependency/artifact/loader checks.
Default and Immediate compile-only profiles require MATCH0/MOTORS_ALLOWED0;
uploads, MATCH, sketch.yaml/yml including dangling symlinks must fail before
transport lookup. No inert upload-manifest key. Test routing/negative profiles
additively, then inspect exact target sources, retained Native/Reader paths,
startup/constructors/empty loop hook, excluded unrelated owners/imports and
conditional loader fit. Reusing D107's checked route avoids its known generic
Bridge-startup artifact, without asserting anything about this future ELF.

## Later physical comparison and current gaps

Stable RAM is sufficient for this software increment; `bench/vbat` currently has
no capture reader or transport. Before a physical run, separately review an exact
enabled revision and readout path that preserves complete slots/status/times and
verifies source/ELF/deployed identity and stable count/terminal state. Do not claim
the default-false build collected data or silently add an output owner now.

For each later actual voltage point, retain raw samples and nominal voltages,
reference/divider constants, exact firmware/config identity, measured multimeter
voltage and time/measurement point, instrument identity/resolution, supply/pack
description, settling conditions, supply/reference/divider checks, source/read/
poll timings, actual faults, and raw capture hashes. Associate those external
observations with a particular capture; local hashes alone cannot do so.
Report signed and absolute per-sample error, spread and worst observed error;
do not hide a failing record behind an average. Sampling points across9.5..12.6V
and settling protocol still need a declared physical test plan; no particular
point count or stability tolerance is already specified. Any later calibration
constant change needs its evidence/decision/tuning entry and independent validation.

F097/F098/F108/F115 and the ADC source audits remain software evidence. Unknown
VDDA/VREF, divider tolerances/leakage/filter settling, physical A0 connection,
clock accuracy/SC-AJ, actual ADC runtime bounds and the0.05V criterion remain open.
HARDWARE2's proposed50kohm guidance does not supersede the qualified DS13086
accuracy/impedance limitations recorded in P2_adc_limits.md. No extra hardware is
needed for the proposed implementation/tests/compile-only work. Actual multimeter
testing, PINMAP and human phase gates remain separate; no new request is made.
