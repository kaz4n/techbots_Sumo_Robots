# D116: complete synthetic recorder transport bench

Selected under D051/D075, 2026-09-24. Implements the remaining P2 B8 software
composition in the named `bench/recorder`, without modifying D091's existing
terminal recorder_inert experiment or claiming assembled-robot acceptance.
Independent public-header and source reviewers found the composition feasible.

## Ownership and default

One fixed `app::Transaction` owns actual Robot, MotorGate and AttemptRecorder.
One existing `recorder::dump::Transfer` owns serialization; one optional existing
UnoQDumpPort supplies the native output through app::DumpPort. Motor callbacks
are counted, inert checks: accept only EN LOW, zero PWM, valid channels/periods;
never bind a native motor backend. All four inert periods are 1 (not physical
frequency claims). Match or MOTORS_ALLOWED nonzero must fail compilation.

The public Runner accepts ClockPort and DumpPort. `begin(enabled, SetupGrant)`
is once-only. Default sketch supplies false and empty grants: no clock, native
setup/readiness/write/cancel, motor callback, or transaction occurs; report is
DISABLED and begin returns false (no running attempt). Enabled success returns
true; failures return false. Constructor/report/source access is passive. Repeated begin returns
false without changing an existing terminal result. Poll before begin fails
ORDER without callbacks. Disabled, failed and sent states remain passive.

Enabled begin requires the clock and every DumpPort callback plus all four
existing SetupGrant predicates. Missing grant/port fails before any callback.
Validation order is PORT, GRANT, then CONFIG. Disabled begin skips validation.
CONFIG validates positive TICK/debounce/long/poll limit, G < BTN_LONG_US,
LOG_FRAME_WINDOW_US >= COUNTDOWN_US+MARGIN_US, and the derived total bound below
strictly below the unsigned half-range, using uint64 intermediates.
Only a later identified run may truthfully supply those native grants. Valid
setup initializes Transaction (inert Gate first), then calls supplied dump begin
once; failed setup is retained and terminates, without retry/reconstruction.
Preserve D090's unbounded setup-only device-init qualification; do not describe
this setup as bounded. Native factory construction is passive and direct.

No heap, Arduino String, dynamic container, RX/command handler, Bridge worker,
new UART protocol or new tunable. Existing config values are unchanged. Existing
strong empty hooks remain in the staged project. Native acquisition grants,
pin ownership, clean framing and receiver attachment are not manufactured.

## Clock, transaction and synthetic sources

Use one caller clock, wrapping uint32 microseconds. Every accepted observation
must be non-reversed by unsigned half-range arithmetic. Equal observations are
allowed internally; consecutive equal poll-entry observations reaching existing
APP_CLOCK_STALL_MAX_POLLS fail CLOCK. The first due epoch is one TICK_US after
successful setup's final clock observation. Preserve that release grid; early
polls perform only clock admission. Each poll runs at most one actual epoch.
At a due observation, lateness >=TICK_US records the skipped releases then fails
MISSED_RELEASE, without catch-up decisions. A reversed clock fails immediately.
The final setup sample is the baseline for the first poll equality count; any
changed poll-entry time resets that count to zero. Every accepted clock sample
still participates in full chronology, independently of that poll-entry count.

The total post-setup deadline is the following structural budget, in us:
LOG_FRAME_WINDOW_MS*1000 + DUMP_TOTAL_MS*1000 +
2*(BTN_LONG_MS*1000+G) + 24*G + BUTTON_SAMPLE_MAX_AGE_US + 4*TICK_US.
This reserves both long gestures and all finite neutral/short/tail transitions;
it changes no production timeout. Poll admission and actual closing C must be
strictly before this deadline from setup_completed_us. Equality fails DEADLINE.
On poll admission, CLOCK precedes DEADLINE precedes MISSED_RELEASE. At C, retain
the genuinely completed transaction (and any actual SENT_UNCONFIRMED report),
but fail Runner DEADLINE instead of freezing success at/after the boundary.

For each due epoch: real open/S; pending reset if qualified; decideFrom with a
pure synthetic projection at actual D; exact Robot result/actual Gate receipt/
recorder; any admitted dump work; real finishAfter/C. Retain S,D,A,C, maximum
execution and failure facts. Never fabricate a result/token/receipt/duration or
backdate decision to scheduled time. Abort Transaction and active Transfer once
on a failure; preserve first Runner failure and existing owner diagnostics.
After an initialization attempt, failure cleanup calls Transaction.abort first
(Gate inhibition), then Transfer.abort. An aborted epoch has no fabricated C;
do not call finishAfter after abort. Failures detected after an actual completed
C retain its finished/timing fields even though terminal cleanup changes the
transaction phase/fault. Before initialization, no abort/callback occurs.
Terminal queries never repeat cleanup.

A is precisely actual applied.feedback.applied_us. After each valid receipt,
sample a clock before readiness, optionally call ready, sample immediately after
it (this becomes Transfer Context.now_us), call Transfer once, sample immediately
after Transfer, then finishAfter(that sample), which captures actual C. Brackets
exist even when readiness is ineligible and skipped. Readiness eligibility is
D101 inhibited IDLE with its valid matching zero/disabled receipt, not a fabricated
menu predicate. Transfer itself enforces actual LOG_DUMP selection and intent.
Reject reversed brackets or now-D >=TICK_US before calling Transfer; validate the
post-Transfer bracket before C. Reversal is CLOCK; forward expiry at or beyond
TICK_US before or after Transfer is DEADLINE. Expose actual Transaction report flags to separate
available S/D/A from missing C; do not fill missing times with scheduled values.

Before service reset, synthetic initialized input has four legacy black readings
QTR_TIMEOUT_US, nominal valid battery V_NOM_V, no opponent until GO then only
FC (bit1, using configured electrical polarity), explicitly absent IMU, and
fresh logical button evidence. Initialization-complete is true from the first
pre-reset decision. Explicit button source start/completion equals actual D;
its first sequence is 1, increment once per decision with natural
uint32 wrapping. `raw=0` is synthetic metadata, never an ADC or electrical claim.
Use actual prior feedback only through Transaction. All exported bytes declare
Origin::SYNTHETIC. No live sensor module/ADC/matrix source is instantiated.

## Full recording and service lifecycle

Let G = BTN_DEBOUNCE_MS*1000 + 4*TICK_US. Each timed synthetic stage begins at
its first actual projection D. Change stage only on a later due epoch whose D
has reached its duration, at most one stage transition per epoch. The new stage
is anchored at that actual D; no inferred skipped observations.

1. NONE for G; START for G; NONE until real accepted START_RELEASE. Require it
   within the next G stage. Preserve its actual release time and token.
2. Continue NONE with the unchanged real hold. Require one GO; record until the
   first actual D with release age >=LOG_FRAME_WINDOW_MS*1000 (200 seconds at
   current defaults), then project local stop_requested=true. Capture actual
   STOP and one later finished STOP tail. Require SEALED with go_seen, real
   timing, no loss/rejections, and valid zero/disabled receipts. Do not invent
   extra frames or a perfect period if the runner failed or missed a release.
3. Only after the completed tail, synthesize new NONE for G, MODE for
   G+BTN_LONG_MS*1000, then NONE until its release debounce qualifies. The
   release stage ends on that qualification, not after an extra G interval.
   The qualification uses the same logical
   D103 contract: fresh neutral debounce, fresh MODE debounce, full hold starting
   at its qualifying decision, release debounce, no backdating. Pending intent
   is based on the actual qualified release, only before that epoch's C.
4. At the immediately following real open/S, require the previous epoch actually
   finished, source age <=BUTTON_SAMPLE_MAX_AGE_US and forward chronology. Notify
   Transfer.onRobotReset then invoke Transaction.resetStoppedRobotForService once.
   Unexpected refusal fails. Never reset/rebegin Gate, recorder arrays or UART.
   Preserve source sequence/time continuity across reset, including first new D.
5. Service-only projection is permanent: canonical explicit CALIBRATION/ABSENT
   line evidence, explicitly absent IMU, synthetic current opponents/buttons/
   nominal battery for service readiness. No fake classified black after reset.
   Match release/GO or any non-BOOT/IDLE state after reset fails. Gate stays
   STOPPED; valid actual inhibited receipts with that fault remain acceptable.
6. Allow actual BOOT->IDLE and fresh neutral for G. MODE for G+BTN_LONG_MS*1000,
   NONE for G, then exactly three MODE-G/NONE-2G pairs select actual LOG_DUMP.
   Verify the resulting selection. START for G, then NONE for G must produce
   one real LOG_DUMP intent and no match START. Thereafter synthesize NONE only.
   Require real menu/result authority, never directly edit selection/request.
7. Step the existing Transfer at most once per actual decision, preserving its
   chronology across recording, STOP, reset and service. Readiness is sampled
   only after successful native setup and current fresh, zero/disabled IDLE
   result plus matching consumed valid inhibited Gate receipt. Use actual D and
   clock observations bracketing readiness/write; reject age >=TICK_US or reverse
   order. No readiness or write outside eligible IDLE. Invalid applied receipt
   aborts active transfer without readiness or write. Retain native diagnostics.
8. Freeze only after a completed actual epoch reports SENT_UNCONFIRMED, or fail
   on Transfer REFUSED/FAILED/CANCELLED. Existing DUMP_STALL_MS/DUMP_TOTAL_MS and
   native poison semantics remain unchanged; no replay, rearm, or automatic retry.
   SENT_UNCONFIRMED is never host receipt, valid CSV, framing or hardware success.

The scripted stage durations are derived from existing button constants; they
are declared synthetic stimulus, not new production interaction rules. The
logical gesture only authorizes this autonomous inert bench caller. Production
Runtime's actual A1/ADC/local gesture policy is unchanged and remains unqualified
physically. Failure evidence, source arrays and exact summaries remain accessible.

## Public evidence and verification

Expose const Transaction/source and retained Runner report with phase/failure,
native setup status, timing/epochs/missed releases, release/stop/reset identity,
GO/service-only flags, inert callback counters, and actual Transfer report.
Current native status stays accessible on the external UnoQDumpPort owner;
app::DumpPort has no status callback and Runner must not infer one from readiness.
Do not require a new wire/readout ABI; exact target layout can be inspected later.
Private implementation fields may change without altering these public semantics.

Independent tests derive from this contract and public headers, before execution.
Use actual Transaction/Robot/Gate/recorder/Transfer. Verify full 200-second
recording, exact final tail/reset/menu lifecycle and strict existing Python
receiver roundtrip; compare every exported CSV row with actual retained source.
Exercise default/invalid setup, reentry, callback order, wrap, equal-clock stall,
missed slots, time reversal before/after dump callbacks, Linux loss, partial and
malformed progress, cancellation/terminal passivity, flags and no allocation.
No shortened recording may stand in for the full positive acceptance case.
Keep locked tests and all existing assertions unchanged. Run normal/sanitizer
tests and separate actual-diff review; failures are evidence, never assumed PASS.

Root adds only this bench to the existing checked default/M0 compile-only path;
MATCH, Immediate, sketch profiles and all upload paths refuse. No allowlist key.
Compile-only target inspection must prove actual empty hooks, ownership/imports
and loader fit before claiming TARGET-COMPILED. No board execution is in D116.
Clean framing/exclusive UART/receiver attachment and actual end-to-end transfer
are later run prerequisites; this task does not close those or physical B8.

Throughput remains a concrete open acceptance issue: a FIFO-disabled UART may
submit only one or two bytes per 1kHz call, including MessagePack overhead.
The full 5001-frame dump may then exceed unchanged DUMP_TOTAL_MS. Independent
host tests must retain a slow-progress TOTAL-failure case as well as complete
full-length transport. Count actual serialized payload/packets to quantify the
required throughput. A fast host sink is pipeline evidence only, not a native
throughput proof. Do not shorten the recording or extend the timeout to hide it;
resolve any supported native-port improvement as a separate reviewed change.

Prefreeze literal clock clarification: an ordinary successful due poll observes
ClockPort exactly at entry, S, D, A, before-ready, after-ready, after-Transfer, C
(eight calls). Skipping readiness preserves its two surrounding observations.
The guarded reset itself adds no ClockPort observation between S and D. Reversal
at any of those observations maps to Runner CLOCK, including inside Transaction
or Gate; owner evidence is retained. Terminal cleanup has its own actual Gate
halt observations, outside that ordinary sequence. Native adapter internal clock
reads are separate from the injected Runner ClockPort and not counted as these
eight. This clarification precedes executable test freeze, not a repaired oracle.
