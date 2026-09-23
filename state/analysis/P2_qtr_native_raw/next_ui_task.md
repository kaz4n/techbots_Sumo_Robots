# Next P2 B6 task: A1 acquisition through the existing ADC1 owner

2026-09-23 Asia/Dubai. Read-only next-task audit while D085 validation runs.
Only this note is written. No production/config/tests/ledgers, board action,
network lookup, physical measurement or QTR re-audit is part of this task.
Local date is Wednesday23September, before PLAN3's28September scope cut and
1October21:00 freeze. Current PROGRESS leaves physical/human gates pending.

## Recommended next actual implementation

Extend the existing concrete native ADC1 owner to support the fixed A0/A1 pair,
and expose an explicitly identified raw A1 sample for UI use. Keep the existing
battery-only default/API behavior compatible. This is a narrow two-channel
extension of an already implemented peripheral owner, not a new generic ADC
framework, separate competing UI ADC owner, stock analogRead wrapper or app
scheduler. Freeze the exact extended contract and public interface first, then
implement native source plus independent tests and an inert retained target
probe in the same task. Do not end the next task at another audit alone.

Choose explicit setup-time A1 participation; it cannot be silently added after
the owner has initialized. One object/lifetime must own ADC1, both admitted pads,
calibration, channel selection, conversion status and reset-only cleanup. The
coordinator can select an additive fixed-channel interface on the current owner
or a small shared concrete owner with a compatible power facade. Prefer the
smaller source change that preserves the existing power regression suite;
neither UI nor power should independently initialize/reset ADC1.

One request should acquire one named channel with actual start/completion time,
raw14-bit data, status/validity and source identity. A1 raw data is not a battery
voltage and must never use the122/22 divider. Preserve the100us battery-call
contract unless a separate explicit decision changes it. Include channel-select,
status-clear, conversion, result validation and final checks in the accepted
call budget; no previous result may masquerade as a new sample. No unqualified
channel-switch or cleanup result should reach the button decoder.

This supplies real missing HAL functionality even while the electrical START/
BOTH ambiguity remains unresolved. Do not advertise the raw-A1 increment as
complete B6 or connect it to match START automatically.

## What already exists and what does not

There is no src/hal/ui.h or ui.cpp and no bench/ui. P2_hal_bench.md B6 requires
START/MODE distinction, both-held detection, modes/services and matrix countdown.
The pure core already has Buttons, StopHold, Controller, Menu and gated Services;
Robot routes their logical events. D019/D035/D057/D058 specify qualified release,
reset-only STOP, service START routing and mode gestures. BTN_DEBOUNCE_MS20 and
BTN_LONG_MS1000 remain config values. Reimplementing these in a HAL decoder would
duplicate qualification and could shift protected deadlines.

power::Reader currently claims ADC1 for its whole boot lifetime. It requires an
uninitialized stock ADC1 device, calibrated private configuration and exact
single-rank channel9 state. Its fixedModes predicate explicitly requires SMPR2=0,
PCSEL=(1<<9), SQR1=channel9 and no injected/DMA/IRQ/continuous configuration.
Another reader or a UI write changing channel selection would violate that
ownership. The driver is not a shared ADC service merely because reads finish.

Source-backed A1 mapping already exists: P0_adc_installed_contract_20260923.md
maps Arduino index15 to PA5 and ADC1 channel10 (A0 is14/PA4/channel9), from exact
saved installed DT/source. Stock DAC1 boot pinctrl admits PA4/PA5 analog/no-pull
without starting DAC output. Current power ownership guards DAC1 channel1 only;
A1 support needs channel2 ownership guards as well. Existing proposed pins are
unchanged; source mapping is not PINMAP OK or physical wiring evidence.

Stock analogRead/adc_read remains unsuitable: F078 and the installed audit prove
K_FOREVER lock/completion waits and unbounded initialization paths. The installed
ADC_ASYNC/STREAM/DMA paths are disabled. A background worker, timeout checked
after return or second stock caller does not repair those liveness facts.

## Narrow source prerequisites before coding the extension

Use the saved installed headers and existing RM0456/DS13086/errata evidence;
refresh only missing exact source facts. No board action is needed to inspect
these local files.

| Item | Existing evidence and remaining check |
|---|---|
| A1 binding | P0_adc_installed_contract_20260923.md Pin/call contract: index15/PA5/channel10. Bind exact named GPIOA/ADC1 devices, DT channel, flags, range/masks and non-overlap with A0 and other proposals. |
| Native register fields | Saved stm32u585xx.h defines ADC_SMPR2_SMP10 at3974 and DAC_CR_EN2/CEN2 at5458/5489. Use channel10's SMPR2 field, never channel9's SMPR1 field or another STM32-family map. |
| Safe rank switching | Saved stm32u5xx_ll_adc.h:4625-4705 documents sequencer rank changes only disabled or enabled with no regular conversion ongoing. Decide exact old/requested mode guards and readback around one-rank9/10 transitions. |
| Sampling/preselection | Same header:6252-6342 requires no regular/injected conversion during sampling-time changes;5261 implements PCSEL by OR, preserving earlier preselected channels. Check RM's state restrictions and freeze whether both channels are preselected/configured once in setup, with only idle SQR1 changes at runtime. Do not invent PCSEL write eligibility from a void helper. |
| PA5 ownership | Extend PA4's already-analog/no-pull, unlocked, clock and final-image exclusions to PA5. Audit DAC1 channel2 enable/calibration/trigger/DMA/wave controls and any analog-switch mode affecting its impedance. Never neutralize an unrelated output to pass admission. |
| Conversion accuracy | Preserve existing ordinary14-bit/LFTRIG/814-cycle profile only after checking channel10's applicable electrical limits. Channel switching, external source impedance and sample-capacitor carryover need explicit assumptions and later measurements; nominal timing alone proves no button voltage. |
| Shared environment | Keep D078 supply/clock/ADC4/stock-driver exclusions and one retained claim. No global RCC/ASV/reference/ADC4/DAC reset, no second calibration, and no stock API during native ownership. |

The current fixed single-channel D078 contract needs a visible scoped extension,
not a silent rewrite of its exact-state predicate. Tests must cover battery-only
compatibility, both channel orders, forbidden/busy switching, partial selection
writes, stale EOC/EOS, raw0/max/out-of-range, channel-tag mismatch, time/ownership
loss at every stage, shared fault latch and bounded cleanup, plus actual target
retention/import/startup inspection. Preserve all existing locked assertions.

## A1 ambiguity and the authorization boundary

HARDWARE5.6 ties START directly to ground. Holding START therefore gives nominal
0V whether MODE is open or closed. NONE is nominal3.3V and MODE alone nominal
1.65V. START and BOTH are mathematically indistinguishable in that documented
circuit; this is not merely missing ADC thresholds. P0_MANUAL_CHECKLIST.md:156
explicitly preserves SC-A. D035 authorizes logical BOTH timing only and expressly
does not establish electrical decoding. No ADC precision or software debounce
can reconstruct the missing distinction for arbitrary button press order.

D051/D075 permit the coordinator to choose and record software ownership,
API shape, sample cadence/age/error handling, explicit ambiguous classifications,
host fixtures and compile-only checks without asking another engineering
question. They do not turn the documented three-voltage circuit into four
distinct states, authorize a physical wiring change under R8, supply resistor/
noise/reference measurements, or grant a phase pass/motor run.

Before actual button-to-Robot routing, freeze a decoder profile and evidence
contract. Unconfigured, overlapping, ambiguous or stale input must remain
explicit and inhibit the relevant control path; never convert a failed sample
to NONE because that can synthesize a START release. A reusable last button
level cannot automatically count as continuous new electrical evidence. Existing
core ButtonLevel has only NONE/START/MODE/BOTH; a separate validity/source-time
boundary is needed before wiring HAL data into it. Do not weaken the logical
BOTH stop rule to pretend the circuit meets B6. Hardware correction/confirmation
and actual isolated readings for all four combinations remain physical work.

## Scheduling, display and resource impact

A0 and A1 serialize on ADC1. Existing selected successful-call maxima already
sum to850us for IMU600 + motor settle150 + one ADC100, before QTR service,
opponent reads, Robot, logging or UI. Sampling both ADC channels with separate
100us calls raises that sum to950us. These are policy ceilings, not measured
durations, but they cannot be asserted to fit an800us tick. Select a justified
per-channel cadence with explicit fresh/retained/invalid semantics; do not simply
append both reads to every1kHz tick. Later app integration must account for fault
cleanup budgets and startup-only calibration separately.

The existing matrix path is internal GPIOF/loader counter work, not a newly
shared Qwiic/I2C1 peripheral. P0_installed_debug_contract.md:103-125 identifies
Arduino_LED_Matrix0.1.3 raw draw as a104-byte copy and matrixBegin's10us counter
top interval. Rendering less often does not remove the refresh interrupt cost.
Any production matrix integration must inspect timer/interrupt ownership and
measure its interference with acquisition/whole-tick WCET. Existing Immediate
matrix restriction F061 remains; normal loader handoff evidence does not prove
Immediate safety. Avoid blocking text/playSequence and the documented apparent
renderBitmap buffer issue. RGB GPIOH uses a separate ownership boundary.

A bounded, pure104-byte renderer for existing Robot/menu/countdown/sensor/battery/
fault state can be implemented separately while electrical work is pending; it
must not call the matrix library, Bridge or motors. It is a useful small parallel
output task, not a replacement for raw A1 acquisition or B6 acceptance. Only then
add a reviewed native display adapter and its own timing/startup evidence.

SC-AJ clock qualification and F091 inherited runtime paths remain global blockers.
None of these software changes establishes physical A1 separation, full UI,
800us WCET, live application integration, PINMAP/EXPLAINED or GATE P2.
