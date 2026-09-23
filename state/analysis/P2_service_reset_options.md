# Optional post-STOP local service reset: feasibility and contract boundaries

Read-only inspection, 2026-09-23 Asia/Dubai, baseline HEAD
`f6f65fc3cf27ca3237ad053d1c4b1e5f8e738ed5`. This follows the coordinator's concrete
proposal after D101 (`0b1013b`) and the D102 packing work. Target acceptance and
memory conclusions remain the coordinator/reviewer's work; this report did not
run builds/tests or contact the board. Only this new file was authored. No policy
is adopted here, and no source, test, shared ledger or earlier report was edited.

## Recommendation

The proposed optional, once-per-boot service transition is feasible without a
native-owner reset or full app rearm. Keep `local_service_reset=false` as exact
legacy behavior. With it enabled, continue real inhibited STOPPED transactions
after the real tail, qualify a local fresh gesture, and perform a guarded
**Robot-only** reset inside the next opened epoch before acquisition. Retain
MotorGate's STOPPED latch, every native owner, recorder storage, clock chronology,
token high-water marks, canceled-source diagnostics and committed thresholds.

The proposal needs the explicit refinements below before public interfaces/tests
are frozen. It is a service access path, not a replacement for eventual complete
control integration, rearm, physical validation or the original project scope.

## Existing behavior that directly supports the design

- `MotorGate::apply` (`src/hal/motors.cpp:165`) accepts a fresh well-formed IDLE
  zero command while its fault is STOPPED, calls actual inhibition, returns a
  matching valid zero receipt if inhibition succeeds, and keeps STOPPED latched.
  D101 `Runtime::dumpReceiptValid` explicitly accepts NONE or STOPPED. No Gate
  reset is needed for the new service lifetime; other Gate faults are not eligible.
- `Robot::reset` preserves `next_token_`. `AttemptRecorder::onRobotReset` preserves
  SEALED storage/summary. Subsequent actual IDLE consumes update only its private
  token high-water, not the retained summary. Existing Transfer equality therefore
  remains valid during a dump; no new protocol or recorder copy is needed.
- Runtime STOP cleanup cancels only active QTR/IMU. The same healthy InputOwner,
  native A0/A1 reader, opponent GPIO owner and matrix can continue. Their setup
  must not repeat. ADC failure is shared/reset-only; its callbacks cannot recover
  by resetting Robot. Current physical button windows are still unconfigured.
- Existing Robot can reach BOOT -> IDLE with real fresh buttons, available battery,
  real fresh opponents, canonical explicit RAW/CALIBRATION ABSENT QTR and explicit
  unavailable IMU. RAW prevents match START even if the operator leaves services.
  Fresh neutral, MODE and service START gestures continue through real Robot/Menu.
  ADC plus matrix alone is insufficient: initialized Robot requires fresh opponents.
- D101 already accounts readiness/Transfer/write/cancel inside S..C, checks current
  real Gate receipts, cancels on terminal failures, and preserves native UART poison.

## Necessary refinements

### 1. STOPPED observation must not invent QTR readiness

Continued STOPPED epochs with CONTROL+ABSENT line input eventually latch
LINE_CONTRACT when the previous genuine line source reaches 6,000 us. This follows
`fsm_line.cpp:57` and is expected with the native source deliberately stopped.
RAW cannot be used to suppress that fault while entry state is STOPPED: D089
explicitly rejects RAW outside BOOT/IDLE. Keep actual CONTROL/ABSENT before reset,
preserve the resulting fault and distinguish it from an earlier provider failure.

The reset gesture cannot require `robot.contract_faults==0`, or normal stopped
observation will make it unreachable. The narrower path needs no core change:
qualify from actual `button_available && button_updated` and the exact current
explicit ButtonEvidence, plus a successful inhibited receipt and healthy app/ADC
clock. Existing non-button source faults may remain recorded while service-only
reset excludes their sources; do not pretend the native faults were repaired.
BUTTON_CONTRACT, invalid/absent/stale A1, an ADC owner fault, token exhaustion,
Transaction/Runtime fault, or an invalid Gate receipt cannot qualify the gesture.

Save a small explicit pre-reset fault/status snapshot before `open` clears its
report. Existing shutdown reports and source owners already preserve most native
details. Avoid recreating the full duplicate RobotResult removed by D101.

### 2. Qualify the trigger from source evidence, then expire the pending intent

The proposed NONE debounce -> MODE debounce -> full long hold -> NONE release
debounce is suitable and remains distinct from BOTH STOP and match START. Make
its exact source-time semantics explicit:

- Only new actual Robot decisions with valid current inhibited Gate receipts and
  fresh admitted A1 observations may advance it. Replayed/ABSENT observations do
  not accumulate time; malformed/expired input cancels rather than becoming NONE.
- Neutral and MODE debounce use successive actual A1 completion times. Start the
  full `BTN_LONG_MS` interval at the **decision that qualifies MODE**, matching
  existing non-backdated hold policy. A source completion preceding that decision
  must not underflow a subtraction and appear to have held for a full wrap.
- Observe MODE at or after the long deadline before arming release. A first NONE
  at the deadline wins as release; it cannot retroactively qualify the long hold.
  Thereafter require fresh contiguous NONE for `BTN_DEBOUNCE_MS`. MODE/BOTH/START
  contamination during release cancels and requires a new neutral qualification.
- Only begin gesture history after the completed genuine STOP tail. Held MODE at
  entry cannot qualify until the required fresh neutral stage has occurred.
- Generate a one-shot pending intent during post-decision work before C. Consume
  it only at the next actually opened epoch, after the previous C succeeded.
  Recommend expiring it if its real release-source start is older than
  `BUTTON_SAMPLE_MAX_AGE_US` at that new S. Otherwise a delayed reset before
  acquisition can erase the Robot button history that should detect a >5 ms gap.
  Cancellation/expiry must not generate a reset or refresh its source timestamp.

The complete current-source qualification remains subject to D087's <=5,000 us
source/decision continuity and source identity checks. Use the real admitted
Robot button pulse rather than a second logical Menu/Buttons instance or a
second physical ADC reader. A small private reset-gesture state machine has a
different purpose from the existing service menu and should not step that menu
again. A new press immediately after the completed release does not invalidate
the already completed intent by itself; the next real Robot input still handles
it, while the Gate remains permanently inhibited.

### 3. Guard the logical reset with owner-held completion proof

Smallest useful public Transaction addition:

```cpp
bool resetStoppedRobotForService();
```

No caller-supplied timestamp, RobotResult, token or proof boolean is needed. The
method belongs to the actual Transaction, not an exposed Robot/Gate accessor.
Its frozen contract should require all of the following:

- Current phase ACQUIRING, a real successful `open`, and not previously reset for
  service in this Transaction lifetime; no FAULT, before begin, DECIDED or repeat.
- Eligibility captured internally before `open` clears the previous report:
  completed/timing-valid real STOPPED decision, gate phase STOPPED, no release/GO
  or motion permission, zero commanded/applied duties, fresh nonzero token,
  consumed matching `applied_valid` receipt, Gate fault exactly STOPPED, and
  normal successful C-S chronology. No caller can manufacture this cache.
- No active RECORDING/DRAINING attempt and no terminal exhaustion. Root must
  explicitly choose whether EMPTY/INTERRUPTED are supported or only SEALED; a
  missing attempt can never become fabricated evidence. In the normal proposed
  clean-stop path, a real tail yields SEALED or remains EMPTY.

**A single preceding STOP receipt is not universal proof of a final tail.** An
old SEALED attempt or EMPTY recorder can coexist with the very first new STOP
decision. To enforce the stated contract in Transaction rather than trusting a
caller flag, a small internal two-completed-STOP marker/streak can prove that both
the initial STOP and a subsequent actual inhibited epoch completed. Runtime also
knows its tail state. Alternatively, scope this Transaction method only to
completed STOP receipts and make actual-tail proof explicitly Runtime-owned; do
not claim the lower-level guard proves more than it checks. The internal marker
is the stronger narrow option and needs only scalar state.

On accepted reset: notify the same recorder before logical reset, reset Robot,
clear `previous_`, consume the one-shot permission, and preserve Gate, recorder
object/arrays, app phase/start S, `last_us_`, `last_decision_us_`, decision chronology
and token sequencing. Do not call Gate.reset/begin or change motor pins. Refuse
invalid calls without clearing faults or mutating protected owners; Runtime may
treat an unexpected refusal of a valid pending request as its terminal invariant
failure. The method can be pure work with no clock callback: Runtime samples its
actual clock after it and before acquisition, preserving the ordinary D/C checks.

Runtime owns Transfer, so its `onRobotReset` notification precedes Transaction's
recorder/Robot reset. Under the correct STOPPED history Transfer is already
inactive from D101 cancellation; preserve that fact, cancellation reports and
permanent native poison. An unexpected active Transfer must be canceled, never
reconstructed. Do not add a remote reset path or let LOG_DUMP request this reset.

### 4. Keep every transition operation inside the new epoch

Recommended ordered seam:

```text
real due release -> Transaction.open/S -> admit S to Runtime chronology
  -> validate pending local intent + cached STOP completion proof
  -> Transfer.onRobotReset -> guarded Transaction Robot-only reset
  -> admit actual post-reset clock -> same-owner ADC/opponent acquisition
  -> actual D/service projection -> Robot -> inhibited Gate -> recorder
  -> permitted display/dump/unavailable-action reporting -> actual C
```

A fault after gesture qualification but before its original C prevents the next
reset. A bad next S prevents all reset work. A bad post-reset/acquisition/D clock
must terminally inhibit/cancel; it cannot close a successful timing record or
recover another owner. The actual cost of Robot reset, including its existing
temporary storage, belongs to S..C and target stack/memory review.

Do not clear the current sensor-suspension condition just to exit the old tail:
`acquire()` restarts QTR when `!stop_tail_`, even though `sources_cancelled_` is
true; only IMU service currently checks that cancellation flag. Use an explicit
service/suspended-source state or preserve equivalent gating across the transition.
One-shot tail completion, continued STOP observation, active service and the final
second STOP are distinct lifecycle facts; do not overload one boolean ambiguously.

### 5. Force service projection and report unavailable actions honestly

The first post-reset input must already be RAW; `previous_state_` is otherwise
still STOPPED and `confirmed_bank_` may be true. Ordinary `selectLineMode` would
select CONTROL and immediately lose service readiness. Force canonical RAW only
for service BOOT/IDLE, with no QTR acquisition/sequence/timestamps or threshold
version; preserve the committed real bank separately. Use CONTROL/ABSENT for any
actual subsequent STOPPED tail rather than feeding forbidden RAW to STOPPED.

Recompute service readiness from real current ADC/buttons/opponents and retained
setup results; do not treat the old full-control initialization latch as proof that
stopped sensors restarted. Keep the same ADC/native sequence and clock lifetime.
Unavailable IMU must have canonical empty observation fields, no fresh pulse and
no yaw/bias reset. Preserve source reports rather than republishing old samples.

Do not call `Calibration::step` during the service-only lifetime. Given genuine
QTR_CAL selection plus RAW/ABSENT input, it otherwise starts a capture and later
times out instead of reporting the action unavailable. Retain its prior bank and
report; do not call Calibration.reset. Report QTR_CAL and DRIVE_TEST refusal in
an **app-owned** service-action status (service, request token and unavailable
outcome/pulse), without mutating the actual RobotResult/menu intent or fabricating
a calibration rejection. Define the display of that status before UI tests;
the current DisplaySample has no generic service-unavailable field. SENSOR_VIEW
can truthfully show opponents and unavailable lines; LOG_DUMP keeps D101 authority.

The once-per-boot latch must also prevent recovery from service faults. Recommend
using the existing real inhibited tail on the second BOTH STOP, then permanent
passivity; state explicitly if a different tail rule is selected. A service fault
must also stop/cancel, not become another reset opportunity. Every match START,
menu exit and inactive-service request stays inhibited; Gate remains STOPPED.

## Minimal public surface and verification inventory

Public additions can stay limited to the optional SetupGrants flag, the one
guarded Transaction method, and compact RuntimeReport reset/service/action status.
No new SourcePort callbacks, ADC/matrix/QTR/IMU reset APIs, exposed mutable owner,
recorder copy, protocol version or tunable duration is needed for this proposal.
Use the existing debounce/long/freshness constants; a new timeout would require a
separate documented choice. Preserve all default-off behavior and established tests.

Add independent tests for:

1. Default false: exact legacy STOP/tail/passivity, callback counts and D101 timing.
   Enabled: genuine initial STOP, one real tail, continued actual inhibited epochs;
   receipt/token/recorder high-water stays monotonic and retained summary is stable.
2. Real unmodified QTR expiry during STOP observation; no invented raw freshness,
   preserved LINE_CONTRACT/provider diagnostics, fresh buttons still qualify.
   BUTTON_CONTRACT/ADC fault/invalid motor receipt/token exhaustion cannot qualify.
3. Every gesture state, NONE/MODE debounce adjacent values, full post-qualification
   hold, source-before-decision anchor, release-first equality, bounce/contamination,
   held-at-entry, replay/absence and exact natural wraps. No elapsed stale input
   completes a stage. Pending expiry at 4,999/5,000/5,001 us and late original-grid
   scheduling cannot bypass D087 continuity.
4. Guard calls in every phase and twice; only owner-held proof works. Cover first
   STOP with EMPTY/old SEALED, real tail, active/draining/interrupted/exhausted
   evidence, mismatched/failed/invalid receipt and failed preceding completion.
5. Reset cost and Transfer notification occur after actual S and before acquisition;
   real clocks before/after reset/D/A/C and natural wrap. Inject failures at every
   boundary; no synthetic tail, timestamp, receipt or successful completion.
6. Actual Robot-only reset preserves next token and Gate STOPPED; no Gate reset/
   begin/high-enable/nonzero duty in either motor build. First service tick reaches
   real BOOT/IDLE with RAW even with a committed nondefault bank. Missing current
   buttons, voltage or opponent evidence cannot be marked ready.
7. Same ADC/InputOwner sequence and age across every transition; no hidden second
   reader. No QTR/IMU setup/acquisition/reconstruction after initial cancellation;
   exact old shutdown/fault/bank diagnostics remain inspectable. Same matrix owner.
8. Actual neutral/menu/LOG_DUMP gesture, retained payload/status/loss equality,
   source/session/CRC and independent receiver roundtrip. Readiness loss, native
   poison, current failed inhibit and clock fault cancel exactly once without retry.
9. App-owned unavailable QTR_CAL/DRIVE_TEST status, no Calibration.step/reset or
   invented Robot menu field. Every match-mode START/menu exit stays inhibited.
   Second BOTH STOP -> selected real tail -> permanent passivity; no second reset.
10. Final default/Immediate/MATCH source/ELF/import/startup and conditional-loader
    memory checks, then fresh scoped review. D102's small conditional margin is
    not proof that the added code fits, nor loaded RAM/full 800 us or hardware proof.

No new hardware fact is needed to implement host semantics. Real physical A1
decoding, grants, UART framing/ownership, loaded RAM/WCET and all phase/motor gates
remain separately unproved. This report authorizes no upload or motor run.
