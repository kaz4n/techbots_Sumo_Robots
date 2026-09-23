# P2 motor_stand feasibility

Read-only source/contract audit, 2026-09-24. No implementation, test execution,
board operation, wiring change or motor-run authorization. This is a proposal,
not an adopted stand-control contract.

**Conclusion:** the driver is present, but a truthful arbitrary stand-command
owner is not. Existing public interfaces cannot compose the complete B4/B7 trial
without a new, explicitly scoped command-authority seam. Full B7 additionally
conflicts with the retained centered-contact full-duty rule; do not disguise it
as an ATTACK, manufacture contact, or edit a RobotResult to obtain permission.

## Existing evidence and the actual gap

| Requirement/interface | Source evidence | Consequence |
|---|---|---|
| B4 individually tests each side forward/reverse/brake/coast, EN kill within one tick, wheel agreement, PWM and supply compatibility | `docs/prompts/P2_hal_bench.md:14` | Driver transactions alone do not schedule or measure these physical trials. |
| B7 requires a half-charged pack and 20 full-forward/full-reverse cycles without an uptime reset | `docs/prompts/P2_hal_bench.md:17`; exit criterion `:30` | Partial-duty reversal or an inert callback trace cannot satisfy it. |
| Sole native writer already exists | `src/hal/motor_port_unoq.h:9`; `P2_motor_native_contract.md:9`; `P2_motor_native_validation.md:11` | Reuse UnoQPort and MotorGate. Do not add analogWrite/direct EN/PWM writers or another timer owner. |
| MotorGate has begin/apply/halt/reset; apply accepts a RobotResult | `src/hal/motors.h:35-44`; `src/hal/motors.cpp:165` | There is no independent stand-demand API. The struct being publicly constructible does not make invented lifecycle/contact/token fields authoritative. |
| Robot supplies one actual lifecycle/contact/governor transaction | `src/core/fsm.h:479-511`; `src/core/fsm_robot.cpp:692-735` | Robot::step has no arbitrary left/right-duty selector. Exact returned results/actual application feedback must be retained. |
| DRIVE_TEST is unavailable in current Robot and inhibited by Gate | `src/core/fsm.h:503`; `src/hal/motors.cpp:26`; `docs/BEHAVIOR.md:54` | It is a P3 SEARCH/edge mode, not a hidden B4/B7 command facility. |
| Pure Countdown and Governor are reusable owners | `src/core/countdown.h:90-122`; `src/core/governor.cpp:58-94` | They can supply real logical hold and shaped duty in a future explicitly adopted bench composition, but do not produce a genuine RobotResult today. |
| Current native probe deliberately never calls its begin/apply/reset exercise | `bench/p2_motor_native_compile/src/native_motor_probe.cpp:7-13`; `P2_motor_native_validation.md:26` | A callable, bounded stand trial with retained phase results is missing; another pointer-only probe would add little. |

The production native boundary already distinguishes intended brake (EN HIGH,
four zero pulses) from inhibit/coast (EN LOW, four zeros), and applies LOW before
new PWM/settle/HIGH (`src/hal/motors.cpp:142-160`,
`P2_motor_gate_contract.md:66`). This is source/callback behavior, not verified
IBT-2 electrical behavior. F095/F096 retain live-rate, waveform, driver supply,
PINMAP and B4/B7 limitations (`state/FACTS.md:244,251`;
`docs/HARDWARE.md:130-134`). MOTORS_ALLOWED=0 prevents nonzero duty/HIGH, but
begin still configures the proposed output pads (`src/hal/motors.cpp:79-98`).
Thus default passivity requires withholding begin, not merely that macro.

## Why full B7 is not reachable honestly

All non-ATTACK governor caps are statically below 1; ATTACK permits full duty
only when centered and contact are both true (`src/core/governor.cpp:10-33`).
Actual Robot ATTACK selects a positive base, with correction bounded by that
base, so neither side reverses (`src/core/fsm.cpp:79-97`). Robot passes actual
perception/contact to its single governor call (`fsm_robot.cpp:714-735`). The
reverse edge/reflank profiles remain capped below full duty. Gate independently
requires ATTACK, contact and a centered current mask for either full-duty wheel
(`src/hal/motors.cpp:133-139`).

Calling Governor with negative ATTACK demand and fabricated centered/contact
booleans, or altering the returned Robot duties, would exploit the representable
API rather than preserve its contract. A synthetic sensor stream through real
Robot is useful host evidence, but is not physical opponent/contact evidence and
still cannot produce Robot's full reverse. Existing D091 already covers genuine
Robot/Gate/recorder composition with explicitly synthetic inputs
(`bench/recorder_inert/src/recorder_bench.h:1,131`).

Full B7 therefore needs an explicit bench-only behavioral exception to R6's
centered-contact condition and a distinct authority path through the same sole
MotorGate writer. It must also define dwell/cycle completion and preserve the
approved brake-before-reversal/slew behavior (`docs/BEHAVIOR.md:276-290`), unless
that behavior is separately changed explicitly. B7's wording supplies neither a
driver bypass nor permission to silently weaken these rules. This audit adopts
no exception. D051 delegates recorded engineering choices, but does not supply
physical facts or a particular motor run (`state/DECISIONS.md:442-453`);
D075 likewise preserves wiring/run limits (`:841-853`).

## Smallest eligible next preparation

The fully compatible **partial** increment is a finite, inhibition-only
`bench/motor_stand`: one UnoQPort/one MotorGate, a default-false setup grant,
one bounded setup attempt, a retained terminal halt result, and passive terminal
polls. It needs no RobotResult, Countdown, Governor, pretend START or motor command.
Keep the actual begin result/fault and HaltResult fields, especially attempted,
inhibition_confirmed, timing_valid, timestamps and first fault
(`src/hal/motors.h:26-33`; `src/hal/motors.cpp:200-225`). Exact failure cleanup
and first/duplicate-call behavior must be frozen before implementation.

This adds preparation for observing the actual native setup/inhibit path, unlike
the existing never-called probe. It expressly excludes brake, either directional
drive, EN-kill-from-powered-output, all 20 B7 cycles and any physical pass claim.
With the default grant false it performs no native callbacks at all. A future
granted execution would touch output pads even though it requests only LOW/zero;
it requires separately reviewed setup/ownership and execution scope. No upload
allowlist addition follows from this proposal.

Minimum ownership would be new `bench/motor_stand/motor_stand.ino` and small
bench-owned header/runner/native binding only. Independently check constructor/
factory/default/terminal passivity, one-shot calls, actual failure preservation,
bounded cleanup, wrap/bad-clock evidence and no HIGH/nonzero path. Then perform
the checked compile/source/ELF/startup/loader audit; no driver, core or locked-test
change is needed for this partial scope.

If useful directional B4 coverage is preferred over that limited increment,
first adopt a narrow explicit stand command interface into MotorGate, using real
Countdown qualification and one Governor pass with caps below full duty. Keep
the existing Robot apply path unchanged and keep B7 disabled/unimplemented.
This is a separate API/ownership decision with independent safety regression
obligations, not something a bench-only controller can implement under today's
interface. Do not spend a task cloning Robot/driver logic or relabelling existing
inert evidence as B4/B7 completion. Full B7 remains a separately scoped exception
and later physical stand trial with its specific STAND OK.
