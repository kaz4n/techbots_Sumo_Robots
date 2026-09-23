# D078 bounded native battery acquisition

2026-09-23, selected under D051/D075 for P2 B5 software. Public API is power.h;
private helpers/state may change. Source prerequisites: P2_adc_native_audit.md,
P2_adc_errata.md, P2_adc_limits.md and P2_adc_ownership.md. Later reports supersede
the first audit's conditional CFGR2=0: **LFTRIG must be enabled** (RM33.4.26).
No app integration, upload, physical supply/divider/accuracy/PINMAP acceptance.

## Selection and ownership

Implement the actual native ADC1/PA4/channel9 source, not an abstract placeholder
or a wrapper around analogRead/adc_read. Reader construction/destruction have no
I/O/allocation. Noncopyable, one lifetime enclosing exclusive use, no restart or
fault-reset API. A second live Reader must fail admission on the first's changed
ADC state. Whole-application ownership excludes stock ADC1 initialization/APIs,
ADC4 conversion producers, PA4/DAC1 channel1 users, clock/power changes and all
concurrent writers. Guards cannot establish absence of an interrupt/thread owner.

A zero-initialized process/boot-lifetime claim flag enforces the single native
owner after pristine admission and before the first ADC/pad mutation. Never
clear it on failure, destruction or repeat begin. This also rejects a second
Reader after an ignored first register write left the peripheral pristine.
Preownership admission failures do not consume the claim. Tests representing
fresh boots must isolate production state by process, not add a reset backdoor.

Name unchanged proposed A0/index14 in config, nominal3.3V reference and122/22
divider ratio. These constants are provisional scaling, not calibration evidence.
Use14-bit single-ended regular software-triggered, single-rank channel9,
814-cycle sampling, LFTRIG1. No IRQ/DMA/continuous/external/injected trigger,
watchdog/oversampling/bulb/auto-delay/offset/gain/shift transform. Preserve all
reserved/reset bits, including CFGR1 bit31. Use installed LL operations/CMSIS
register layout, never a fabricated generic STM32 ADC ABI.

Validate config, native metadata and ownership before any ADC/pad configuration.
Bind native ADC1/common/GPIOA addresses, channel, selected Arduino pad, IRQ37 and
clock metadata to the installed DT. Reject invalid index/flags/mask/alias with
existing motor/opponent/QTR proposals. Reject nonfinite/nonpositive nominal
scaling, unsupported ADC reference above3.6V, divider below1, zero/half-range
timeouts/poll guards and post-cal spacing below2us. The nominal high-supply
profile supports reference>2.4 and<=3.6V only; no low-voltage booster branch is adopted.

Require ADC1 stock device never initialized (failed init is also inadmissible),
ADC1 IRQ disabled/not pending/not active, compatible reset state, RCC/GPIOA ready,
GPIOA clock and unlocked PA4. ADC1 kernel must remain HCLK160MHz with divider4,
ASV enabled, stable VOSRange1 and the documented high-supply switch profile.
At160MHz also require PWR_VOSR EPOD BOOSTEN1/BOOSTRDY1 and the installed
PLL1MBOOST DIV1 field0 (MSIS4MHz). RM0456 Rev6 10.5.4 pp410–411 requires this
above55MHz; installed clock_stm32_ll_u5.c496–538/603 supplies the boot setting.
This EPOD booster is distinct from SYSCFG's analog-switch BOOSTEN, which remains0.
Only read these controls; never enable a missing global booster from this HAL.
Check shared selector rather than change it; do not initialize/reset RCC/ADC1 or
steal ADC4/DAC. ADC4's boot-enabled IRQ113 is permitted, but active conversion,
calibration/stop/disable or external/continuous conversion configuration is not.
DAC1 channel1 must be disabled. Follow the ownership audit's exact additional
finite live clock/supply checks. Preserve the installed MSIS automatic-calibration
configuration (enabled, MSIS selected); do not disable or retune the shared clock.
Mode/ready/rate metadata checks do NOT prove automatic-calibration lock or actual
frequency. ES0499 2.2.27 can degrade its accuracy; no reliable stock lock predicate
was established (revisionX lacks the W/U EXTI23 unlock event). This is a separate
global runtime-integration blocker, not silently solved by ADC register checks.
Host/compile-only work proceeds under D075; no ADC deployment/runtime acceptance
or claim of a qualified40MHz frequency follows. Future platform clock handling
must resolve detection/history/recovery and MCU-revision conditions before use.

Admission order: validate config, mapping, stock device/IRQ, shared environment
and pad ownership first. Then enable ADC1's peripheral clock through checked
finite native dispatch and confirm readback BEFORE reading its reset registers;
a gated read cannot prove reset state. Clock enable alone does not claim ADC1.
If reset-state admission then fails, return NOT_ATTEMPTED without ADC/pad writes
or clock rollback; leaving that clock enabled is explicit, not a disabled-device
acknowledgement. Only after compatible pristine registers are observed does this
instance claim ADC1. Configure PA4 alone analog/no-pull, not the six-pin ADC state.
Check initial pin is already analog/no-pull (stock DAC boot pinctrl); reject an
unrelated remux rather than seize it. No global analog-power/reference writes.

## Bounded setup

begin() attempts initialization once. Before begin, read returns NOT_INITIALIZED
with no I/O. Repeat begin returns ALREADY_STARTED with current ready/shutdown
state, performs no I/O and cannot recover a fault. Any failed first begin latches
fault; subsequent read returns FAULT_LATCHED with no I/O or cached sample.

After admission, own ADC1 even if partial initialization fails. Exit deep-power
down, enable its regulator and require LDORDY before ordinary offset+linearity
calibration, ADEN0, capture/latch0. Extended calibration is excluded. Use __DMB
after calibration controls; wait for ADCAL0. Start a new minimum-wait timestamp
after observing completion, wait elapsed>=2us (one-microsecond quantization),
then clear stale ADRDY/W1C, enable and require fresh ADRDY. Configure controls in
their documented idle state; validate readback before returning OK/ready=true.

Config development deadlines: regulator100us, calibration5000us, enable100us,
post-cal minimum2us; each wait also capped at65536 passes. Deadline equality is
failure except the explicit minimum spacing. Guard exhaustion is POLL_LIMIT.
These margins cover inspected source limits, not guaranteed physical completion.
Use unsigned elapsed subtraction; no delay/sleep/unbounded wait/thread/heap.
Check ownership throughout waits and after readiness, not just before setup.

## One fresh runtime sample

read() captures started_us before its admission/status-clear work and uses one
100us acceptance deadline for the entire transaction. It never invokes setup,
reinitializes hardware or filters/stores a previous voltage. All valid calls
represent a new conversion. Verify ready and exact owned mode/clock/pad/IRQ and
idle command state. Clear stale EOC/EOS/OVR/EOSMP once using W1C, verify cleared,
then issue one ADSTART using LL's command-safe CR mask.

At most4096 observation passes, all finite fixed work. Reject ownership change,
OVR, elapsed>=100us or exhausted count. Accept only current EOC+EOS and completed
single conversion, never assume DR freshness from its numerical value. Do not
require observing ADSTART1, since a conversion may finish before first poll.
Read DR once as32bits, reject values>16383 before narrowing; raw0 is valid data.
Check flags/mode/time again, clear EOS by W1C, and perform final time/readback
validation. A sample becoming late during cleanup is invalid. A successful
conversion need not consume the full deadline; the poll cap may fail earlier.

On success return OK, valid=true, raw, started_us and completed_us from actual
micros, voltage_v=raw/16383 * VBAT_ADC_REFERENCE_V * VBAT_DIVIDER_RATIO.
Require finite result. No clamp to a healthy battery voltage; no second B6 filter.
The sample's interval/age remains explicit for eventual integration. Repeated
calls acquire new results; invalid outputs keep raw/voltage0 and valid=false,
never a prior good reading. This software validity cannot verify the divider,
physical connection or reference voltage. No change to RobotInput/core behavior.

## Faults and bounded shutdown

First failure returns its specific Status, latches fault/ready=false, and never
publishes partial/late data. Ownership loss (including during cleanup) permits
no blind write: return Shutdown::UNCONFIRMED. Admission failure before ownership
uses NOT_ATTEMPTED. For an owned fault with unchanged peripheral controls, one
separate total100us/4096-pass shutdown budget attempts only documented commands:
ADSTP if regular conversion active; await both ADSTART/ADSTP0; then ADDIS only
when all start/stop/calibration commands idle; await ADEN0. Never issue JADSTP,
reset the peripheral, disable a shared clock or claim failed stop as success.
Pending calibration/enable commands may preclude cleanup; report UNCONFIRMED.
DISABLED requires observed idle commands and ADEN0 under still-valid ownership.
No powerdown/clock gating is needed. The original failure status is preserved
even if shutdown itself times out; subsequent calls perform no I/O and retain
the shutdown result. A new object cannot recover a partially claimed peripheral.

Command writes must suppress read-as-set command bits as installed LL does;
W1C status operations must not read-modify-write. Fixed guards plus deadlines
bound software work even with frozen/wrapped micros. Actual register/bus access,
interrupt preemption and whole-tick WCET remain later physical measurements.

## Independent validation and inert retained probe

Test actual native CPP with installed-shaped controlled headers. Independent
author reads this contract/public API/facts, not production CPP. Cover every
admission exclusion, stale/fresh/partial EOC+EOS, raw boundaries/invalid32bit,
OVR, mode loss at each stage, setup/calibration order and2us spacing, exact
deadlines/adjacent times/wrap/frozen clock/poll caps, failed abort/disable, one
deadline across cleanup, no recovery/cached voltage/dynamic allocation, repeated
fresh samples and nominal arithmetic. Model command semantics and W1C explicitly.
Existing locked tests remain unchanged. New tests here are ordinary B5 tests.

New bench/p2_power_compile has static Reader plus a never-called exercise()
retaining begin/read results; setup retains only its address, loop empty.
Test startup plus10000loops makes zero native I/O, and every attempted upload
refuses before transport/board lookup. Compile actual staged source on installed
toolchain; inspect retained native imports/MMIO/startup. No upload allowlist
expansion. Five existing inert hashes update only after separate exact-map review.
Separate fresh read-only review is required; same-model independence is labeled.

Probe public ABI: src/power_probe.h under that bench declares namespace
power_probe, Result{power::InitResult init; power::Sample sample;},
using Probe=Result(*)(), extern power::Reader reader, extern Probe volatile entry,
and Result exercise(). Definition constructs reader without I/O, initializes
entry=nullptr, and exercise calls reader.begin() then reader.read(), retaining
both results. setup only assigns entry=&exercise; loop is empty. No result/global
initializer or startup callback invokes exercise. The public probe header may
quarantine inherited platform macros if necessary; never alter production names
or weaken the startup test to accommodate platform collisions.
