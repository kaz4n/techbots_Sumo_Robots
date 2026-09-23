# QTR_CAL next-task recovery

2026-09-23 Asia/Dubai. Read-only source recovery at implementation HEAD
`385c46c`, while the root agent closes D088 matrix runtime evidence. This file is
the only owned modification. No MCU call, hardware measurement, configuration
change, implementation, test execution or gate is claimed here. Recommendations
below are not adopted decisions. D051 permits the implementation owner to select
and record them without another engineering-choice question.

Today is Wednesday 23 September; PLAN section 3 schedules P0/P1 today and P2 bench
work on 24-26 September. D075 permits the current P2 software work before hardware
acceptance. PROGRESS's D088 entries are newer than the D087 heading still present
at the top of CODEX_HANDOFF during this recovery; do not repeat completed matrix
implementation or infer the result of the root agent's in-progress runtime run.

## Existing requirement and implemented path

| Evidence | What it establishes |
|---|---|
| `docs/BEHAVIOR.md:481` and `docs/prompts/P2_hal_bench.md:24` | QTR_CAL holds each QTR over white/black, stores thresholds in RAM and prints values for config.h; P2 2.4 requires the service to work. Neither specifies sample count, capture gestures, estimator, threshold activation or failure policy. |
| `docs/BEHAVIOR.md:129` and D085 (`state/DECISIONS.md:1043`) | Acquisition is asynchronous, using timing intervals rather than invented exact RC times. Source-age expiry, ambiguity and reset-only line inhibition remain binding. |
| `src/core/countdown.h:244` and `:257`; `src/core/countdown.cpp:459` | Service selection exists. A qualified START release emits one `MenuResult.request == QTR_CAL`. `request_unavailable == false` does not prove a consumer exists. MODE short/long gestures already cycle/leave the service menu. |
| `src/core/fsm_robot.cpp:871`; D057/D058 | Robot supplies the genuine one-tick intent after IDLE-at-entry and final STOP/fault checks. No raw button decoder, second debounce path or remote command should be added for calibration. |
| `tests/test_robot.cpp:87`; `tests/locked/test_menu_routing.cpp` | Established service-intent behavior excludes match countdown and IMU bias calibration; those assertions must remain intact. QTR calibration can be a separate bounded consumer. |
| `src/hal/ui_display.cpp:121`; D088 matrix contract | QTR_CAL currently shows C/checker selection only. It does not expose a sensor index, white/black stage, progress, success or rejected calibration. |
| `src/app/app.ino:14` and `:21` | Application is still inert BOOT-only with empty loop. Actual scheduling, service invocation, threshold use and output transport are not integrated. |

Repository searches of src/tests found no QTR_CAL executor, mutable threshold
bank, capture accumulator or threshold text formatter. `bench/qtr_raw` named by
the P2 plan does not yet exist. Existing p0_qtr is an isolated bare-pad diagnostic;
it is not measured black/white calibration evidence.

## Reusable raw evidence and the important boundary

`src/hal/line_qtr.h` already provides Reader and Snapshot. COMPLETE evidence has
source sequence/start/completion, per-pad conservative lower/exclusive-upper
bounds, LOW/right-censored-timeout masks, source read timestamps and checked
cleanup. `Snapshot.valid` means a bounded raw acquisition, not a measured color.
The public Reader has begin/start/advance/report/cancel; calibration should consume
reports without owning pins or changing Reader's acquisition/cleanup lifecycle.

`src/hal/line_qtr_adapter.cpp:83` validates COMPLETE shape/timing and cleanup in
private `complete()`. `classify()` at line 113 then compares intervals against
immutable `config::QTR_WHITE_US[i]`: upper <= threshold proves white, lower >=
threshold proves black. `applySnapshot()` at line 125 conflates raw validation
and current-threshold classification in its public result. VALID forwards only
the qualified mask and identity. AMBIGUOUS produces INVALID line presence even
though the raw frame is structurally valid. Calibration therefore cannot recover
raw evidence from RobotResult.line_mask or from a synthetic `line_raw_us` value.

`src/core/fsm_line.cpp:23` independently admits source identity and age:
frame span <2500us, source age <6000us, minimum 2000us start spacing, no source or
sequence reversal/conflict, and no new confirmation from exact replay. Accumulated
age prevents wrap resurrection. `prepareLine()` at line 45 latches LINE_CONTRACT
on invalid input or unavailable initialized line state. Calibration must not
claim the Robot's existing freshness checks apply to raw snapshots automatically.

Two current threshold users are `src/core/edge.cpp:20` (legacy exact-time API) and
the actual explicit-line adapter. A new RAM bank should affect an explicit adapter
overload; leave legacy defaults/locked tests unchanged. Four mask bits and proposal
order are FL, FR, RL, RR (`src/core/edge.h:77`, `docs/HARDWARE.md:62`). This is a
software order, not evidence that the pads are wired accordingly.

## Smallest next bounded implementation

Implement the real, allocation-free QTR_CAL consumer, a caller-owned RAM threshold
bank, and bounded config-text formatter using existing Snapshot and MenuResult
data. Keep it callable in host tests and the inert compile-only target. Do not
build a generic service framework, new acquisition provider or parallel menu.

Suggested ownership is `src/hal/qtr_cal.h/.cpp` for the pure consumer/formatter
(no Arduino headers or native calls), and a small additive change to
`line_qtr_adapter.h/.cpp` to expose the existing raw validation result and accept
an explicit checked four-threshold bank. Reuse the same raw validator for both
calibration and motion qualification rather than duplicating its timing rules.
An existing no-bank `applySnapshot` overload must preserve today's behavior.

Freeze the public contract and record the material choices in DECISIONS before
separate implementation and independent tests. The next scoped closure can prove
intent-to-capture-to-RAM-to-formatter and explicit-threshold qualification in host
tests. It cannot honestly close P2 2.4 until scheduling, live output and the
IDLE/raw-ambiguity policy described below are integrated and verified.

## Concrete recommendations to freeze under D051

1. **Authorization and cancellation.** Accept only a fresh Robot result with a
   previously unconsumed token, final IDLE, no contract/escape fault, disabled
   motors, zero duties, service menu active and QTR_CAL selected. Only its genuine
   QTR_CAL request starts a capture. Leaving that selection/IDLE or any final
   inhibition cancels a pending calibration and retains the previously committed
   RAM bank. The consumer returns no duty, motor permission or match START. It
   does not clear Robot, Reader or button faults. Repeated tokens cannot replay
   a request or collect a sample. Preserve actual STOP priority on the same call.

2. **Use the controls already available.** Fixed order FL-white, FL-black,
   FR-white, FR-black, RL-white, RL-black, RR-white, RR-black. Each qualified START
   request begins only the displayed stage; collect a bounded batch then wait for
   the next request, giving the human time to reposition. MODE retains its current
   selection/exit behavior and thus cancels the unfinished run. Extra START while
   collecting is ignored, not queued. After success/failure a new qualified START
   begins a completely new eight-stage run. No circuit START/BOTH fix is inferred.

3. **Bound the batch.** Recommend 16 distinct valid complete frames per stage and
   a 1000ms capture deadline from the accepted request. Centralize the new count
   and `_MS` value in config; identify the count-name exception explicitly as with
   existing count constants. These are provisional software selections, not an
   optical-confidence or cadence claim. Wait states do not time out and perform
   no work beyond bounded context/identity checks. During capture, missing/pending
   frames do not count or renew the deadline. Equality at the deadline rejects.

4. **Raw admission independent of the old threshold.** Accept only completely
   validated raw frames with start at or after the stage request, forward complete
   and delivery times, age < QTR_SAMPLE_MAX_AGE_US, and D085 advancing sequence/
   spacing/order. Preserve identity across stages so an old frame cannot be reused
   after a later button action. An otherwise valid pre-request retained frame is
   ignored, not evidence for the new stage. Exact semantic replay does not count; conflicting
   replay, reversal, malformed/provider-fault or a present expired frame rejects
   the current run. Same-tick cancellation/deadline wins before collection. Use
   unsigned wrap admission plus accumulated bounded ages, not plain timestamp
   comparisons. Source absence is distinct from rejection.

5. **Calculate from conservative bounds.** For each sensor retain
   `W = max(white upper_us)` over all white observations; every selected white
   observation must have a finite LOW interval. Retain
   `B = min(black lower_us)` over all black observations; a native right-censored
   timeout supplies its actual lower bound, never an invented exact 1500us edge.
   Set `U = min(B, QTR_TIMEOUT_US)` as an explicit threshold-domain restriction,
   not a clamped measurement. Require `0 < W < U`, then choose the integer
   `T = W + (U - W) / 2`. This guarantees every captured white interval has
   upper <= T and every captured black interval has lower >= T, with T <=1500.
   Retain W/B, censor counts, sample counts, source identities and the selected
   threshold in the result; do not call an overlap/inversion or zero margin
   calibrated. A one-unit gap may put T at W and must be reported honestly.

6. **Atomic RAM lifetime.** Initialize the RAM bank from the unchanged four
   config defaults. Do not publish individual sensor results early. Commit all
   four only after the eighth successful batch; any failure/cancel retains all
   four old values and has an explicit reason/status. Reset restores defaults.
   A bank version distinguishes changed calibration from old line evidence.
   Reclassifying the same acquisition under a new bank must not masquerade as a
   fresh D085 frame; apply a committed bank only to a later acquisition, with
   controller-history activation policy explicitly resolved before app wiring.

7. **Truthful export and display.** Produce a fixed-buffer snippet containing
   four `QTR_WHITE_US` values only for a complete successful result, with a typed
   insufficient-buffer error and no truncated valid-looking snippet. Expose the
   stage/sensor/count/rejection fields for a later small D088 renderer extension.
   Rendering C/checker or producing text in RAM is not evidence that calibration
   ran or printed. No flash persistence, config file rewrite, Bridge call or
   serial motion/control endpoint belongs in this consumer.

## Integration choices that cannot be hidden

**IDLE raw ambiguity:** today a raw frame crossing the old threshold becomes
LINE_CONTRACT before Robot can authorize another service request. Repositioning
sensors during QTR_CAL can therefore terminate IDLE and block further actions.
The safe smallest next slice above preserves that rule and reports cancellation;
it does not make an on-ring calibration workflow complete. Before full service
integration, explicitly amend the contract for a strictly motor-disabled QTR_CAL
observation mode, or retain reset/manual config adoption as a stated limitation.
Recommended eventual amendment: raw-only capture may continue only inside an
already admitted IDLE/QTR_CAL transaction, with no match START and no retained
motion permission; ordinary qualified line evidence must be re-established on a
new frame before returning to match-ready IDLE. Genuine native/malformed/STOP
faults remain faults. This is a new safety policy needing its own public contract
and independent tests, not permission to feed fabricated black or clear faults.

**Threshold activation:** merely passing new thresholds into the adapter can
conflict with Robot's retained identity, confirmed-white history and warning
state. The consumer can publish a candidate bank now; production activation needs
an explicit IDLE-only handover/invalidation contract and cannot re-label a cached
frame. Do not reset Robot implicitly, bypass an existing STOP latch, or advertise
RAM storage alone as active calibrated edge protection.

**Printing:** B13 asks for printed config values, but R2/AGENTS permits MATCH
Bridge use only for IDLE log dump. A formatter is independent of transport.
Choose and record a permitted bench-only diagnostic output or a deliberate
extension to the existing IDLE dump evidence format later; do not add live MATCH
calibration Bridge traffic by inference. SC-A, SC-AJ and F091 remain open.

## Independent tests needed for that bounded slice

- Actual Menu/Robot qualified service intent reaches the consumer exactly once;
  legacy/explicit buttons, duplicate tokens, wrong selections, stale results,
  final STOP/fault and service-menu exit cannot begin/continue a capture. Existing
  locked countdown/edge/menu assertions remain unchanged.
- All eight stages and all four sensor positions; inter-stage placement waits,
  ignored busy START, canceled/retried/failed runs and all-or-nothing RAM commit.
  No consumer output can grant motion or produce a match START/GO event.
- Complete native Snapshot fixtures through the shared validator: malformed
  cleanup/times/masks, provider fault, pending/absent and ambiguous-under-default
  but valid raw data. Calibration must accept/reject independently of current
  color classification while ordinary applySnapshot preserves D085 semantics.
- Admission boundaries: pre-request frame, equality at request, exact replay,
  same identity changed bounds, sequence/start reversal, sequence/time wrap,
  1999/2000us spacing, 2499/2500us span, 5999/6000us source age, and missing frame
  through the capture deadline. Use independently derived expected decisions.
- Extremal conservative math: censored black, rejected censored white, overlap,
  inverted colors, equal W/U, one-unit gap, varying samples, values beyond1500,
  and a bad fourth sensor leaving the entire old bank unchanged.
- Formatter exact values/order/units and successful-only output; every buffer
  capacity around the exact required length, null/invalid arguments, zero heap
  use and bounded loops. Text/raw evidence must not claim hardware provenance.
- Explicit-threshold adapter regression: config-default overload equivalence,
  out-of-domain banks rejected, old raw Snapshot unchanged, unrelated RobotInput
  fields preserved, and no duplicate line update on a bank change.

Run relevant normal/sanitizer suites, native adapter regressions and actual inert
target compilation for the changed files, then separate read-only review. Record
source identity, precise test scope and missing app/runtime/physical evidence.
Real optical black/white/brown separation, A1 windows, physical mapping, timing,
motor-run authorization and all human gates remain outside this source recovery.

Next action: implementation owner selects/refines these bounded recommendations,
records the new decision/public interface, then delegates code and independent
tests with disjoint ownership. This recovery does not modify those files.
