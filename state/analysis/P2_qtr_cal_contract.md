# D089 actual QTR calibration and safe threshold handover

2026-09-23, selected under D051/D075. Implements B13/P2 2.4 software using actual
Reader snapshots, Robot service intents, RAM profiles and explicit line admission.
Physical color measurements, A1 decoding, printing transport, full scheduler and
human gates remain separate; this contract must not stop at a disconnected bank.
No established test changes, native pin change, fault recovery or motor permission.

## Shared raw validation and threshold adapter

line_qtr::validateRaw exposes the exact existing D085 structural validation.
ABSENT is a valid pending snapshot, VALID a complete valid raw frame,
PROVIDER_FAULT a valid native fault report, INVALID malformed data. No classification
or decision-age check occurs here. Existing no-bank applySnapshot keeps its exact
semantics. New explicit Thresholds overload checks every value in1..QTR_TIMEOUT_US;
invalid bank produces INVALID/contract_valid=false even for a pending snapshot.
Its source evidence includes threshold_version; it never changes unrelated inputs.
All values/defaults remain in config; the new bank initially copies QTR_WHITE_US.

applyRawSnapshot sets explicit_values and LineUse::CALIBRATION, version0 and
white_candidates0. Valid raw COMPLETE maps VALID with real sequence/start/end;
valid pending maps ABSENT. Native fault maps INVALID/contract_valid=true and bad
structure INVALID/false. RAW means unknown color, never a synthetic black sample.
CONTROL remains the default LineUse, including for every old caller/test.

## Real Robot raw-only mode and activation

Explicit CALIBRATION input is an opt-in raw preparation request. It is admitted
only with entry BOOT/IDLE, no existing contract/escape/STOP fault, and explicit
line representation. It can start before service selection (including initial
BOOT->IDLE), so old-threshold ambiguity cannot prevent navigating to QTR_CAL.
It does not itself start a capture. Requests while COUNTDOWN/moving/STOPPED,
unknown use, malformed/native-invalid input or invalid source ordering latch
LINE_CONTRACT. All other input/receipt/button/STOP/fault checks remain live.

RAW suppresses match allow_start and motor permission. Publish line_raw_mode=true,
line_calibration_hold=true, line_available=false/line_updated=false and mask0
explicitly unavailable. Invalidate only classifier/white-warning readiness on
entry; never reset Robot/Lifecycle/STOP/faults/tokens/source ordering. RAW absent
may wait indefinitely in BOOT/IDLE, never qualifying a line measurement. Valid
present RAW requires D085 span/age/sequence/spacing rules, zero version/candidates.
Retain source identity/accumulated age. Identical raw replay never renews age.
Transition from classified to raw may reuse the same source identity only with
identical start/end/sequence; old candidates are unconsumed in RAW. Fresh RAW
frames advance source history but never white confirmation or edge replan counts.
Present expired/malformed/conflicting source still faults; absence is distinct.

Ending RAW alone cannot restore control. Keep the calibration hold until CONTROL
contains QTR_CONFIRM_TICKS distinct qualified frames whose acquisitions started
strictly after the last RAW decision. A retained last capture reclassified with
new thresholds does not count. Before that, CONTROL ABSENT may wait inhibited;
CONTROL INVALID still faults. Nonlater valid frames can update ordering history
but are unavailable and cannot advance confirmation/readiness. Same identity with
changed classified candidates/version is invalid except the first RAW-to-CONTROL
reclassification, which is ignored for readiness. Preserve source ordering through
every transition and accumulated ages through wrap. Compare the finite current
source age against accumulated time since the RAW decision, not an old timestamp
alone, so long waits cannot resurrect pre-handover frames.

CONTROL version is initially0 and must remain unchanged during ordinary control.
Only while calibration hold is active may a new version>=previous be adopted
(no wrapping version). A version change resets requalification/white counters;
it must be associated with a distinct later acquisition, never a cached frame.
On success publish line_threshold_version and only new-frame classification.
QTR_CONFIRM_TICKS remains effective; count only distinct qualifying observations.
Do not clear a safety fault or change a remembered calibration bank on failure.

After requalification, require a fresh NONE span BTN_DEBOUNCE_MS before match
START. Requalification tick cannot start a match. Use source times/fresh samples
for explicit buttons, decision samples for legacy; no fresh sample, no qualification.
Use ButtonTiming.start_ready to discard old START qualification without restarting
StopHold or clearing a latched Gate. Set start_ready=false until fresh neutral
qualifies, then initialize Buttons from that neutral on the qualification tick,
while still suppressing match allow_start on that tick. A subsequent new press/
release gets the unchanged full5100ms hold. Raw-mode service gestures still work;
rearming gates only the handover, not QTR_CAL's eight service requests. Expose
line_start_rearming. These additive calls do not alter ordinary D085/D087 behavior.

## Calibration owner

qtr_cal::Calibration::step(t_us, actual_result, same_snapshot) is pure/bounded.
Caller pairs one current actual Robot result with the decision time and native
snapshot used for it. No clock/I/O, extra native acquisition, button decoder or
second Robot/Menu/Lifecycle step. Duplicate/nonfresh result is ignored and clears
only committed pulse. Fresh token0/reversal or backward/half-range decision time
rejects the current run; token/time high-water never decreases. Successive actual
fresh decision gaps must be below half uint32 wrap. No replay renews a deadline.

Eligibility requires final IDLE, disabled outputs/exact zero duties, no contract
or escape fault, line_raw_mode, service_menu and QTR_CAL selected. A fresh genuine
menu.request=QTR_CAL begins each stage. Wrong context cancels an active collecting
or waiting run before any sample/commit; completed/rejected/inactive reports may
remain for inspection. Existing STOP and faults cannot be cleared by this owner.

Stages0..7: FLwhite,FLblack,FRwhite,FRblack,RLwhite,RLblack,RRwhite,RRblack.
First request starts stage0. Each batch collects QTR_CAL_SAMPLES distinct frames
(default16, supported1..256), with fixed QTR_CAL_CAPTURE_MS deadline(default1000).
Equality at deadline rejects before collection. Success advances to WAITING for
next stage; no timeout while waiting for placement/request. Extra request during
COLLECTING is ignored, not queued. After SUCCESS/REJECTED/CANCELLED, a new genuine
request starts a completely new run with cleared candidate statistics but keeps
the committed bank and raw identity history. No partial sensor values are committed.

During COLLECTING/WAITING admit complete raw frames using shared validation and
D085 forward span/source age<6000, sequence/start advancement/spacing>=2000 and
nonoverlap. Native fault/malformed/expired/conflicting replay/order failure rejects.
Exact semantic replay does not count or refresh age; compare actual fields, not
padding bytes. Keep accumulated source age across waits/runs to reject resurrection.
Valid frames acquired before this stage request are remembered but not counted.
Stage age/source age advance only on new actual result tokens, saturating safely.
Pending/absent data never counts/renews timeout. Same-tick context/deadline wins.
Inactive/terminal runs need not validate unrelated raw payload until a new request.

For selected sensor record W=max(white upper_us); white must have a finite LOW,
so censored white rejects. Record B=min(black lower_us), preserving actual timeout
lower bounds and count of censored black. U=min(B,QTR_TIMEOUT_US) restricts only
the threshold domain. Require0<W<U, choose T=W+(U-W)/2 (integer). Thus all captured
white upper<=T and black lower>=T. One-unit gap is allowed and recorded literally;
no confidence/optical claim. Record per-sensor extrema/counts/censor counts and
last actual source identity. Complete all8batches before publishing all4thresholds
atomically, incrementing version once. VersionUINT32_MAX rejects without mutation.
Report.thresholds always holds the last complete bank; candidate values private.
reset restores config defaults/version0 and consumer history only; caller must
coordinate genuine owner reset, never use this to recover Robot/Reader faults.

## Export and UI ownership

formatConfig accepts SUCCESS only and a valid nonzero-version bank. Exact text:
`QTR_WHITE_US[4] = {123U, 234U, 345U, 456U}; // us\n` with actual decimal values.
No leading zeroes. On success written excludes NUL; capacity must include it.
Unavailable/invalid/too-small/null output produces no partial snippet, written0,
and leading NUL if writable. Fixed local storage and bounded decimal loops only.
This is the real printable data producer, not a claim that transport printed it.
MATCH retains only documented IDLE log-dump Bridge permission; no new Bridge use.
The later app owner must use permitted bench output/IDLE evidence transport.

The next renderer extension must show actual stage/color/sample count/status so
the eight-request workflow is usable; it cannot claim physical calibration from
synthetic data. Freeze its literal pixels before independent UI tests. The real
pipeline tests must cover adapter->Robot->Calibration->bank->later classifier->
Robot->MotorGate, not just standalone helpers. Include actual boot ambiguity,
menu navigation/service intent, active STOP/fault/cancel, new-version handover,
fresh START/full hold, time/sequence wrap and nondefault confirmation counts.

No MCU/calibration sensor test is authorized by a synthetic probe. The currently
running inert D088 matrix image stays separate. All physical/human gates pending.

## Export status precedence and calibration display (frozen before tests)

Export first checks SUCCESS and valid nonzero-version bank. An unavailable phase
returns UNAVAILABLE; invalid bank or null output returns INVALID; a nonnull output
with insufficient capacity returns BUFFER_TOO_SMALL. All failures set written=0
and set output[0]=NUL whenever writable. WAITING reports the next stage with
samples=0; SUCCESS retains stage7 and its final sample count.

DisplaySample gains CalibrationScreen SELECTION (default), WAITING, COLLECTING,
SUCCESS, REJECTED, CANCELLED, plus stage and sample-count fields. SELECTION retains
D088 pixels. A non-SELECTION overlay is rendered only in IDLE with the service
menu selecting QTR_CAL; elsewhere it has no effect. Invalid screen enum, stage>7,
or count>QTR_CAL_SAMPLES is INVALID even when hidden. Brightness remains7.
WAITING/COLLECTING: left x0..2 rows1..5 uses existing digit1..4 for stage/2+1;
center x4..8 uses WHITE full rows {31,31,31,31,31} for even stages and BLACK outline
{31,17,17,17,31} for odd stages. WAITING lights only x6 on row6. COLLECTING lights
row6 columns strictly below floor(samples*13/QTR_CAL_SAMPLES). SUCCESS shows left
C {7,4,4,4,7}, center check {0,1,18,12,0}, row6 all13 pixels. REJECTED shows E
{7,4,6,4,7} and existing cross {17,10,4,10,17}; CANCELLED shows C and that cross.
Their row6 is blank. Existing top-row faults, right fault glyph and bottom battery
remain unchanged. applyCalibration maps actual owner phase INACTIVE to SELECTION
and other phases one-to-one, copying stage/samples; no invented progress or I/O.
The display is not proof of optical visibility and the formatter is not transport.

## Review disposition: unambiguous source era (D089,2026-09-23)

Fresh review demonstrated that an unseen cached pre-handover source can alias a
small modular age after a full clock wrap. RAW/CONTROL absence may still wait
inhibited indefinitely. A VALID presentation is rejected when retained source age
has reached 2^31us, or (for CONTROL handover) elapsed time since the last RAW
decision has reached 2^31us. A reset is required to establish a new source era;
absence alone does not clear history. Before that boundary, a distinct source's
forward start delta must be <= accumulated prior source age, and subtracting that
delta must equal its delivered modular age. This ties source time to observed
elapsed decisions instead of guessing a wrap epoch. Robot latches LINE_CONTRACT;
Calibration rejects SOURCE_ORDER without changing the committed bank. Owner
source identity/history persists across rejection/new requests until genuine reset.
Exact replay still uses its stricter 6000us expiration rule. These bounds apply
before replacing source history or counting samples. No physical acquisition or
counter claim follows. Reviewer reproducer and independent adjacent-boundary
regressions are required; ordinary source cadence and all old tests remain intact.
