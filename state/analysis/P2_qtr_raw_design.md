# Next named P2 bench: qtr_raw

Read-only design inventory, 2026-09-23 Asia/Dubai. No production, config,
test, build policy, ledger or hardware changes accompany this note. D107 remains
the active implementation under review. This is a proposed next contract for
coordinator adoption, not authorization to initialize QTR pads or upload a bench.

## Recommendation and existing requirements

Implement `bench/qtr_raw` as a small, motor-free cooperative runner around one
existing `line_qtr::Reader`. Preserve complete raw snapshots and explicit faults;
do not instantiate the full application to acquire four sensors. Use the shared
`line_qtr::validateRaw` and leave threshold calibration and color decisions out
of this runner. Defaults must perform no callbacks, including clock calls.

`docs/prompts/P2_hal_bench.md:12` names this bench for B2. Its adopted D085
criterion is bounded calls and complete frames below `QTR_FRAME_MAX_US`, with
10 us charge/1500 us discharge and source brackets retained. Actual black,
white-border and brown-line evidence must qualify every color; brown must read
black. The original whole-call timeout+100 us criterion was explicitly replaced;
the assembled robot's full-tick <800 us requirement remains separate.

`state/CODEX_EXECUTION.md` and `docs/prompts/CODEX_RESUME.md:16` permit named P2
bench software after D107, while physical gates remain open. The current date
is 23 September; `docs/PLAN.md:65-67` schedules sensor benches for 24 September
and assembled B1-B8 for 26 September. Software progress does not advance those
hardware criteria or human gates. `bench/qtr_raw` currently does not exist.

## Reuse exactly these existing boundaries

| Existing boundary | Meaning and consequence |
|---|---|
| `src/hal/line_qtr.h:56`, `Reader` | Passive, noncopyable single owner. One `begin(exclusive_pads=false)` attempt; `start`, `advance`, `cancel`, passive `report`. No reset/reinitialize API. |
| `src/hal/line_qtr.h:16`, `Pad`/`Cleanup`/`Snapshot` | Preserve all timestamps, sequence, four interval pairs, native statuses, masks, service-gap/advance counters and cleanup evidence. `valid` means bounded raw evidence, not a color. |
| `src/hal/line_qtr_adapter.h:17`, `validateRaw` | Existing exact structural validator returns ABSENT, VALID, PROVIDER_FAULT or INVALID; it does not classify a threshold or check decision age. Reuse it rather than duplicating interval rules. |
| `src/hal/line_qtr.cpp:213` | Granted begin preflights and then configures the bank. A declined caller grant is not physical handoff. The bench should skip begin altogether when disabled. |
| `src/hal/line_qtr.cpp:251` | Start clears the prior frame only when accepted. BUSY/NOT_DUE are command results, not replacement snapshot statuses. Capture the report separately after a status-returning callback. |
| `src/hal/line_qtr.cpp:362` | One advance services one fixed bank pass; COMPLETE and FAULT are terminal for that frame. No internal 1500 us discharge wait. |
| `src/hal/line_qtr.cpp:421-450` | Failure and active cancellation use the owner's checked cleanup. A fault cannot be recovered by beginning another Reader. Idle/complete cancellation is a no-op. |
| `state/analysis/P2_qtr_native_contract.md:155` | Low/timeout/high masks and raw structure have a precise public contract. Fault timing fields can be diagnostic and need not be a valid optical interval. |
| `state/analysis/P2_qtr_cal_contract.md:9` | D089 exposes the shared raw validator; calibration requires actual Robot service authority. Raw bench collection must not fabricate that authority. |

Do not use `app::NativeSources` merely for its QTR callbacks: its public class
also owns opponents, ADC, IMU and matrix (`src/app/native_sources_unoq.h:32`). A
bench-local native binding should own only one Reader and delegate directly to
it. The existing `bench/p2_qtr_native_compile` retains a Reader-to-Robot path but
only publishes an exercise address at startup; it is not a live raw bench.

## Smallest proposed public software contract

Freeze a bench-local `Port`, `Grants`, `Report` and noncopyable `Runner` before
independent tests. Proposed operations are constructor, `begin(Grants)`, `poll`,
`stop` and passive `report`; final names belong to the adopted header. Port needs
only clock, begin(bool), start(), advance(), cancel() and passive snapshot()
callbacks with context. Native contains one Reader and no destructor I/O.

- Construction and port creation are passive. `Grants::exclusive_pads` defaults
  false. Disabled begin succeeds without validating/calling ports or clocks;
  repeated begin is false with retained state unchanged. Disabled/not-started/
  stopped/fault polling performs no callbacks. Sketch asserts MATCH=0 and
  MOTORS_ALLOWED=0 and begins with the false grant.
- Enabled begin checks required callbacks before I/O, then calls the native
  begin once. Require OK plus an IDLE/OK raw-ABSENT report. Preserve both returned
  command status and full report if setup fails; do not retry ownership/setup.
  Existing Reader configuration and native checks remain authoritative. No new
  period, pin, threshold, guard, grant or configuration value is needed.
- Service every ordinary Arduino loop pass, not every 1 kHz tick. Each poll has
  at most one start or advance operation, with passive report retrieval where
  needed. Start only from IDLE/COMPLETE; advance only while CHARGING/DISCHARGING.
  Native NOT_DUE retains the old frame without a fresh pulse or another advance.
  Never spin until a complete frame in one poll, wait, delay, allocate, or catch
  up missed frames. No other peripheral work goes between these service calls.
- Preserve a current raw snapshot and a separately retained last valid COMPLETE
  snapshot. Report availability and a one-poll `fresh` pulse separately; the
  retained record is historical while another frame is pending. Use validateRaw
  on provider snapshots. A valid pending record is not an invalid optical read;
  malformed shape and provider FAULT are explicit terminal runner failures.
  Never overwrite a native status with a guessed microsecond value or color.
- Track bounded/saturating counts of starts, advances, completed valid frames,
  NOT_DUE observations, and cancellation attempts, with visible saturation.
  Exactly one newly completed accepted frame increments the completed count.
  Validate expected command/phase transitions and advancing identity, including
  ordinary sequence/time wrap, so a bad provider cannot replay COMPLETE as new.
  Do not require consecutive sequence integers where the native contract only
  requires an advancing identity; expose any gap as diagnostic evidence.
- Stop is terminal for this runner. If a frame may be active, call its existing
  cancel exactly once and retain the returned snapshot/cleanup report. Stopping
  IDLE/COMPLETE performs no pad work. Known provider FAULT already ran its own
  cleanup; do not blindly repeat it. Stop must not imply cleanup succeeded, and
  must never reset the Reader or rearm after fault. Missing/malformed callback
  evidence requires an explicit fail-and-cancel policy frozen before tests.
- Use actual outer clock brackets to report setup/start/advance/cancel and
  successful-poll durations. Define exact closure/first-fault precedence before
  tests. Reversed or half-range clock evidence is a terminal clock fault; cancel
  an active frame once while preserving both primary fault and cleanup result.
  Do not publish fabricated duration/completion on an invalid closing clock.
  Accepted clock deltas must be accumulated where a comparison survives many
  polls, rather than allowing a full-wrap alias to resurrect old timing.

No matrix rendering, Robot, MotorGate, UART, Bridge, calibration owner, threshold
mutation or command parser belongs in this first bench scope. R7's compile-time
motor default is additional evidence; actual absence of motor owners and calls
must also be verified.

## Timing and bounded work

`src/config.h:80-98` currently selects charge10 + quantization1 us, charge age
<100 us, call<100 us, cleanup<100 us, start spacing>=2000 us, frame<2500 us,
timeout1500 us and at most8192 advances. Those are software guards, not measured
hardware upper bounds. Waiting 1000 us between start and the first advance can
violate the charge guard. Consequently the D107 release-grid scheduler should
not be copied. The sensor-only loop can advance once each invocation and yield;
actual loop overhead/service gaps still require target measurement.

Count explicit native GPIO API operations separately from register checks and
internal driver work. A normal start configures four outputs. Charge release
can read four charged pads, configure four inputs, read four discharged pads,
then perform four cleanup configurations if the frame finishes: up to16 direct
GPIO API invocations in that advance. Ordinary discharge can perform four reads
plus four cleanup configurations. Cancellation attempts at most four cleanup
configurations, with ownership checks possibly skipping unsafe pads. Fault
cleanup can add work after a failed call; report that whole path rather than
subtracting it. Source: `line_qtr.cpp:238`, `295`, `339`, `379`.

Snapshot copies and four-pad validation are finite wrapper work. Measure their
enclosing S..C scope as well as native source span/max-service-gap. State plainly
if duration publication and return are excluded. Native guards detect late
returns; they do not preempt a blocking native call. Neither source arithmetic,
a fake-clock test, a compile nor this isolated bench proves app R4 WCET.

## Raw evidence delivery and physical blockers

An exposed in-memory Report is sufficient to test this acquisition owner, but
does not by itself deliver the black/white/brown dataset required by B2. Do not
claim the bench physical acceptance is complete after this software increment.
Before a real run, adopt a bounded capture/output contract: sample count and
surface provenance, immutable or stop-frozen records, overflow/loss reporting,
exact source/config/artifact identity, and complete interval/cleanup fields.
This is a separate small decision, not an implicit permission to add blocking
Serial prints, dynamically growing storage, or debugger pauses during charge.
An explicit terminal stop offers a clean seam for subsequent stable capture.

Keep intervals `[lower_us, upper_us)` and right-censored timeouts distinct.
Zero upper on timeout means no finite upper bound, not a zero discharge or an
exact1500 us sample. A late LOW keeps its actual bound. Pending is not fresh;
ambiguous color is not black. Later surface analysis must pin the threshold bank:
upper<=threshold proves white, lower>=threshold proves black, otherwise unknown
(`line_qtr_adapter.cpp:112`). Brown needs actual black qualification on all four
channels, not a label selected by firmware. Channel order is FL, FR, RL, RR
(`docs/BEHAVIOR.md:18`, `docs/HARDWARE.md:62-65`).

Existing physical blockers remain: FACTS F-045/F-046 require actual QTR mounting
and safe OUT voltage evidence; F-107 does not prove pad handoff, sensor color,
cadence or WCET. `docs/HARDWARE.md:128` is a proposed verification step, not
evidence that VIN5V/OUT transients are safe. The installed D2/D4/D7/D8 mapping and
native exclusivity guards do not supply PINMAP OK or electrical approval. The
old P0 bare-pad timeout observation F-083 is not QTR color evidence. Do not
enable the grant while only the UNO Q is connected or infer physical readiness
from the user's earlier inert-runtime authorization.

## Ownership, tests and acceptance of the software increment

Coordinator freezes `bench/qtr_raw/src/qtr_raw.h` and `qtr_raw_native.h` plus the
contract. Worker owns only `bench/qtr_raw/qtr_raw.ino`, `src/qtr_raw.cpp`,
`src/qtr_raw_native.cpp` and private header state/helpers. An independent author
owns new runner/native-binding tests; existing D085/D089/D106 HAL/tests/config
remain unchanged. Keep functions under60 lines and each new file's three-line
purpose/why/test preamble. No shared generic scheduler or HAL refactor is needed.

Tests should cover passive default/repeated begin, missing callbacks, every
setup status/shape, correct start/advance sequencing, NOT_DUE retention, valid
pending versus raw failure, all four interval/censoring masks, replay/conflicting
identity, wrap/order/clock closure, timeout and advance exhaustion, one-shot
completion publication, saturated counters, stop in each phase, cleanup evidence
and first-fault precedence. Native-binding tests must execute the real binding
with counted Reader substitutes, proving grant passthrough and no unrelated
owner/callback. The actual sketch's default setup and loop must be exercised.
Use independent frozen tests, strict normal/sanitizer builds and meaningful
invalid-configuration profiles; preserve existing assertions and failures.

Root then compiles through `tools/board_tool.py flash bench/qtr_raw --compile-only`
and audits exact staged sources/objects/ELFs/package, constructor/setup/loop,
Reader/native_pins ownership, imports/strong hooks and conditional loader fit.
The current generic bench branch differs from the checked app/runtime_inert
policy (`tools/board_tool.py:317-327`); do not claim D100 coverage or a loader fit
until the actual artifacts establish it. Root owns build/tool policy changes.

`tools/board_tool.py:297-300` rejects qtr_raw uploads before transport. Keep that
restriction. A later physical run requires separately reviewed exact artifacts,
explicit safe electrical/pad setup and a scoped upload policy. Source/test/target
review can close this software task; no physical B2 result, full-loop timing,
motor permission or human phase gate follows.
