# Next P2 native driver: checked MotorGate backend candidate

2026-09-23, read-only selection under D-051/D-075. Recommendation: implement a
concrete UNO Q backend for the existing `motors::Port` callbacks after resolving
the two narrow source/contract prerequisites below. Do not start a replacement
ADC or I2C driver first. No implementation, configuration, shared ledger, locked
test, app, build, upload or MCU action is part of this audit.

## Why this is the next bounded implementation

The real MotorGate already exists and is independently tested. F-086/F-088 and
P0_pwm_installed_contract_20260923.md establish native checked GPIO/PWM routing,
finite PWM writes, the three selected timers and actual loader imports. SC-AI
correctly leaves preload settling unresolved. The missing deliverable is one
native backend, not another Port abstraction or more synthetic compatibility code.

F-078 instead proves stock ADC has indefinite ownership/completion waits and
hardware polling, with no installed asynchronous/read-cancel alternative.
Wrapping analogRead in an elapsed-time check, moving it to a worker, or changing
a sketch macro does not bound those precompiled waits. A direct ADC1 polling
implementation would need clock/init/calibration, IRQ exclusion, sequence,
completion, stop/recovery and shared A0/A1 ownership proofs. F-084 similarly
leaves installed I2C with indefinite locks, 500 ms completion and the BERR
success-path issue. Either replacement is substantially broader than this PWM
backend. No new ADC/I2C API support was discovered or asserted by this audit.

## Exact implementation scope proposed for the next decision

Add a target-conditioned `src/hal/motor_port_unoq.h/.cpp` that supplies the six
existing callbacks and immutable period array to MotorGate. Constructor and
Port creation perform no I/O. Only MotorGate invokes the callbacks; no secondary
GPIO/PWM writer, public drive command, app integration or upload allowlist change.
Tests compile that actual source against deterministic fake native headers.

Keep the proposed D3/D5/D6/D9 PWM and D10 EN assignments, centralized in config.h;
this adds code names for existing proposals, not PINMAP approval. Native mapping:

| Gate channel | Proposed pin | Native device / channel | Arduino state index |
|---|---|---|---:|
| LEFT_FORWARD | D3/PB0 | PWM3/TIM3 CH3 | 0 |
| LEFT_REVERSE | D5/PA11 | PWM1/TIM1 CH4 | 0 |
| RIGHT_FORWARD | D6/PB1 | PWM3/TIM3 CH4 | 1 |
| RIGHT_REVERSE | D9/PB8 | PWM4/TIM4 CH3 | 0 |

Use `gpio_pin_configure_dt(...,GPIO_OUTPUT_LOW)` and checked raw GPIO access
for D10/PB9. GPIO return/readback acknowledges the MCU interface, not the physical
driver EN voltage or isolation. Use the verified per-channel pinctrl helper,
checked readiness, `pwm_get_cycles_per_sec`, and `pwm_set_cycles` with normal
polarity. Do not use analogWrite or whole ARDUINO pinctrl states. Named native
PWM z_impl exports are zero; actual final ELF must retain inline device dispatch.

Candidate new config defaults, requiring an explicit D-051 decision before code:

- `MOTOR_PWM_HZ = 10000` (100 us intended carrier). HARDWARE specifies an upper
  capability of 25 kHz but selects no carrier. This is a new engineering default,
  not an existing requirement, measured frequency or approved driver waveform.
- `MOTOR_PWM_SETTLE_US = 150` for the complete three-timer settle pass, not 150 us
  per timer. The 50 us margin is a candidate, not measured WCET.
- `MOTOR_PWM_SETTLE_MAX_POLLS = 4096` as a fixed second termination guard when
  micros freezes or advances unexpectedly slowly. It may expire before the time
  deadline and must fail closed; do not call the resulting instruction count a
  verified microsecond bound. Include this naming exception/count unit explicitly.

For each channel, immutable period N must derive from verified timer rate C as
`N = C / MOTOR_PWM_HZ`; reject a nonzero remainder, zero, overflow or unsupported
16-bit timer period. TIM3 channels must share the same N. All three timers must
have equal C/N, even though their prescalers and period counts differ. Do not
assume CPU 160 MHz is the PWM timer kernel clock. The actual candidate C/N values
are still to be established from installed clock lineage before coding them.

## Construction ordering needs an explicit contract clarification

D-075 currently says Port periods are already validated against actual clock
configuration. MotorGate copies the Port before begin. The native PWM devices
are deferred; their cached tim_clk is zero in the packaged initializer and is
populated by device initialization. Preparing them externally before Gate.begin
would bypass its required EN-LOW-first ordering. Mutating the backend's Port
later would not change MotorGate's copy.

Recommend recording this precise clarification under D-051 before implementation:

> A native Port may be constructed without I/O using immutable periods derived
> from the installed clock configuration. Those periods are candidates until
> MotorGate.begin has acknowledged EN LOW and its configurePwm callbacks have
> initialized each required device and checked its actual cycle rate, prescaler,
> routing and common carrier against the copied periods. No duty write or
> activation is admitted before the corresponding validation succeeds. A
> mismatch fails begin; periods are never silently adjusted after construction.

This is a proposed clarification, not the current contract or a performed edit.
It preserves existing Gate callback order and locked tests. Failed/unconfigured
channel cleanup must reject unsafe native writes rather than call an unready
device. Cleanup continues through the remaining channels as Gate already
requires. If the clarification is not adopted, this immutable-period prerequisite
remains unresolved; do not conceal it with assumed rates.

## Proposed natural-update settling algorithm

Prefer natural post-write update flags; no stop/restart or extra software UG is
proposed. Gate already acknowledges EN LOW before the four PWM writes and calls
settle before any EN HIGH. Settling is conditional on exclusive timer ownership
and the primary update semantics identified below, which remain an explicit
source prerequisite rather than a completed proof in this audit.

1. Require a complete successful current transaction and validated immutable
   periods. Check the expected timer modes and compare/ARR/PSC register values;
   register readback is consistency evidence, not latch or waveform evidence.
2. On each unique TIM1/TIM3/TIM4, require CEN=1, UDIS=0, URS=0, up-counting,
   expected ARR/preload/channel mode, TIM1 repetition count zero, no update
   IRQ/DMA consumer and no slave/trigger owner. Reject changed configuration.
3. After the four writes, clear each stale UIF once. Begin one bounded polling
   pass over all three timer flags, retaining a separate fresh-update bit for
   each timer. Never count the flag value observed before the clear. An update
   racing with the clear may be conservatively discarded; wait for the next one.
4. Only the all-three fresh mask can succeed. Abort on the single 150 us unsigned
   elapsed deadline, 4096-pass guard, readiness/configuration loss or error.
   A clock wrap must preserve elapsed arithmetic. A frozen microsecond clock
   still terminates by the iteration guard. One healthy timer cannot stand in
   for one stalled timer. Check elapsed/guard admission before accepting a late
   completion; no success after the deadline simply because all flags are set.
5. Return true only with a current complete acknowledged update sequence. Failure
   returns false so Gate latches IO and performs its existing EN-LOW/all-zero
   cleanup. No elapsed delay alone and no constant-success callback qualifies.

Provided the U5 update/CCR transfer semantics are verified, fresh post-clear
natural update flags identify an update after the newest writes on each timer.
This would support a software latch receipt, not physical frequency, full-duty,
deadtime, EN-voltage, brake/coast truth-table or reversal-waveform acceptance.
In particular CCR==period readback alone does not prove physical full duty.
Native first-channel enable already generates UG; settle must discard that old
flag and establish a later event. No atomically simultaneous cross-timer update
is claimed, and no PWM carrier phase reset is added.

## Installed LL evidence obtained in this audit

Essential read-only request used the same exact USB 2629958581, installed Windows
ADB 32.0.0 and `tools.board_tool.remote(...,['python3','-c',PROGRAM],capture=True,
timeout=30)` as P2_opp_gpio_audit.md. PROGRAM used pathlib to locate two installed
headers, hash their bytes and print the named inline functions with line numbers.
It returned exit 0. No live peripheral registers were read. No new raw file was
created; the relevant exact installed expressions and identities are below.

Base: `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/llext-edk/include/modules/hal/stm32/stm32cube/stm32u5xx/`.

- `drivers/include/stm32u5xx_ll_tim.h` SHA-256
  `1da2403c2e6d11b7537e863b2715b550a82938d200b32cfb134fedfae39f0b46`.
- `soc/stm32u585xx.h` SHA-256
  `8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06`.

Exact LL bodies/expression excerpts from that installed timer header:

```cpp
// :1912-1914, LL_TIM_IsEnabledCounter
return ((READ_BIT(TIMx->CR1, TIM_CR1_CEN) == (TIM_CR1_CEN)) ? 1UL : 0UL);
// :1945-1947, LL_TIM_IsEnabledUpdateEvent
return ((READ_BIT(TIMx->CR1, TIM_CR1_UDIS) == (uint32_t)RESET) ? 1UL : 0UL);
// :1979-1981, LL_TIM_GetUpdateSource
return (uint32_t)(READ_BIT(TIMx->CR1, TIM_CR1_URS));
// :2258-2260, LL_TIM_GetRepetitionCounter
return (uint32_t)(READ_REG(TIMx->RCR));
// :5222-5224, LL_TIM_ClearFlag_UPDATE
WRITE_REG(TIMx->SR, ~(TIM_SR_UIF));
// :5233-5235, LL_TIM_IsActiveFlag_UPDATE
return ((READ_BIT(TIMx->SR, TIM_SR_UIF) == (TIM_SR_UIF)) ? 1UL : 0UL);
```

LL_TIM_UPDATESOURCE_REGULAR is 0 (:667), COUNTER is TIM_CR1_URS (:668).
GetCounterMode begins at :2050. The installed comments :1951-1958 describe
regular update requests from overflow/underflow, UG and slave control, whereas
COUNTER selects overflow/underflow only. These are vendor primary source API
facts, but the header snippets alone are not the complete CCR-shadow/UIF proof.

## Primary U5 manual gap and remaining source checks

The official [RM0456 STM32U5 reference manual](https://www.st.com/resource/en/reference_manual/rm0456-stm32u5-series-armbased-32bit-mcus-stmicroelectronics.pdf)
was located. Its indexed Rev 6 contents identify the general-purpose timer
sections 55.5.1 (CR1, p2316), 55.5.5 (SR, p2324) and 55.5.6 (EGR, p2326).
The actual relevant register/counter/PWM paragraphs were **not retrieved**:
the web extractor rejected the 23,798,382-byte document as too large; a direct
Python urllib request timed out before HTTP response, and a final parallel
request to the official st.com.cn URL and st.com `?download=1` variant both
timed out. That final command exited 0 only because it printed both caught
TimeoutErrors; it did not read a PDF. An earlier alternate-name download also
provided no usable content. No other MCU family's text is substituted.

The next task must verify RM0456's TIM1 and TIM3/TIM4 sections explicitly tie
an enabled update event to CCR/ARR preload transfer and UIF setting, including
UDIS/URS, repetition, slave mode and flag-clear semantics. It must also check
applicable U585 timer errata. Until then, natural-UIF settling is the recommended
candidate, not a verified hardware guarantee or finalized implementation contract.
Separately establish source-derived timer clock lineage/period candidates and
verify transitive device-init/clock/pinctrl/error-path bounds. Existing PWM setter
boundedness does not prove all initialization and logging paths are bounded.
Initialization remains in setup; post-setup callbacks must not invoke init.

## Required independent validation for the concrete backend

Test exact mapping and one-channel pinctrl routing; source-derived period versus
actual-rate mismatch, zero rate and nonintegral carrier; TIM3 shared ARR;
default-disabled and separately host-only active Gate composition; native errors
at every configure/readiness/write slot; no HIGH after any error; cleanup of
configured versus unconfigured channels; stale UIF rejection, all flags initially
set, successive asynchronous fresh flags, one permanently missing flag and
configuration/owner changes during settling. Test micros zero, wrap and freeze,
deadline-1/deadline/deadline+1, guard exhaustion, late completion rejection, and
incomplete/replayed transaction receipts. Model distinct preload and active
compare state in the fake timers; do not make CCR readback or write return 0
automatically count as a latch event. Full-duty/zero/reversal tests verify
software ordering only; physical waveform acceptance remains separate.

Then target-compile an inert never-called probe and inspect exact imports,
retained methods, setup/constructors/hooks and intended register accesses. Do
not upload or integrate it. SC-AI physical settling/reversal/EN/WCET acceptance,
PINMAP and specific STAND OK/RING OK remain open. This report selects a concrete
next implementation and two explicit prerequisites; it closes no hardware gate.
