# P2 native motor clock and register contract audit

2026-09-23. Result: installed source and offline ELF support immutable candidate
periods **{3200,250,3200,3200}** in Gate channel order D3/D5/D6/D9 for the proposed
10 kHz carrier. They remain candidates until checked during configurePwm after
Gate has acknowledged EN LOW. No timer clock, register or waveform was measured.
No MCU connection, GPIO/PWM operation, upload, production/config/ledger edit or
implementation was performed. Only this report and `P2_motor_native_raw/clock.json`
were written. The earlier D-075 construction-order clarification remains needed.

## Source-derived clock lineage, not CPU-to-timer inference

Installed generated DT identifies:

- RCC clock-frequency=160000000; AHB/APB1/APB2/APB3 prescalers all 1
  (DT:1921-1935). The pinned RCC binding defines clock-frequency as **HCLK/core
  clock, already SYSCLK divided by AHB**. Do not divide this property by AHB a
  second time.
- RCC selects PLL1 (DT:1954); PLL1 selects MSIS (DT:1705). MSIS range=4
  (DT:1574); packaged MSIRangeTable index4 is 4000000 Hz. PLL1 M=1, N=80,
  R=2 (DT:1715-1721), giving 4 MHz / 1 * 80 / 2 = 160 MHz SYSCLK; AHB/1
  gives the 160 MHz HCLK above. Enabled HSE is 16 MHz but is not this PLL source.
- TIM3/TIM4 domain clock is STM32_SRC_TIMPCLK1=13; TIM1 uses
  STM32_SRC_TIMPCLK2=14. Each second clock spec has div=0 and enr=255
  (no separate selector), distinct from the first RCC enable-bit spec.
- Pinned clock_stm32_ll_u5.c:385-390 computes timer kernel rate as HCLK when
  the matching APB divider <=2, otherwise (HCLK/APB divider)*2. Both dividers
  here are 1. The actual ELF jump table for buses13/14 selects the same
  SystemCoreClock load at 0x0800ba80. Thus each selected kernel is 160 MHz
  under this installed clock configuration.
- The packaged SystemCoreClock initializer is 4000000, **not a live value**.
  Clock init source:978 updates it to CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC,
  which is 160000000 in the installed config. PWM init obtains the selected
  kernel through clock_control_get_rate and caches it. PWM get_cycles_per_sec
  divides that cache by PSC+1 (actual ELF 0x080196d6-0x080196ea).

| Gate channel | Timer/channel | Domain | PSC | PWM cycle rate | N at 10 kHz | ARR=N-1 |
|---|---|---|---:|---:|---:|---:|
| LEFT_FORWARD / D3 | TIM3 CH3 | TIMPCLK1 | 4 | 32000000 | 3200 | 3199 |
| LEFT_REVERSE / D5 | TIM1 CH4 | TIMPCLK2 | 63 | 2500000 | 250 | 249 |
| RIGHT_FORWARD / D6 | TIM3 CH4 | TIMPCLK1 | 4 | 32000000 | 3200 | 3199 |
| RIGHT_REVERSE / D9 | TIM4 CH3 | TIMPCLK1 | 4 | 32000000 | 3200 | 3199 |

The native device config objects independently establish PSC63/4/4, up-counter,
deadtime0 and master mode0. These periods divide their source-derived cycle rates
exactly, fit the native 16-bit timers and preserve TIM3's shared ARR. Float
granularity or a nanosecond conversion is not used to derive the integer periods.

## Usable public macros and rate checks

Include Arduino.h, wiring_private.h, zephyrPinctrl.h,
`<zephyr/drivers/pwm.h>`, `<zephyr/drivers/clock_control.h>`,
`<zephyr/drivers/clock_control/stm32_clock_control.h>`, and
`<stm32u5xx_ll_tim.h>` as needed. The STM32 clock header selects its U5 binding
and defines STM32_CLOCK_CONTROL_NODE as DT_NODELABEL(rcc).

The following exact installed public macros can derive metadata without literal
clock or prescaler duplicates:

```cpp
DT_PROP(DT_NODELABEL(rcc), clock_frequency) // HCLK, 160000000
DT_PROP(DT_NODELABEL(rcc), ahb_prescaler)   // 1
DT_PROP(DT_NODELABEL(rcc), apb1_prescaler)  // 1
DT_PROP(DT_NODELABEL(rcc), apb2_prescaler)  // 1
DT_PROP(DT_PARENT(DT_NODELABEL(pwm1)), st_prescaler) // 63
DT_PROP(DT_PARENT(DT_NODELABEL(pwm3)), st_prescaler) // 4
DT_PROP(DT_PARENT(DT_NODELABEL(pwm4)), st_prescaler) // 4
DT_CLOCKS_CELL_BY_IDX(DT_PARENT(DT_NODELABEL(pwm3)), 1, bus) // 13
DT_REG_ADDR(DT_PARENT(DT_NODELABEL(pwm3))) // 0x40000400
```

Equivalent parent nodes are timers1, timers3 and timers4. Assert expected domain
sources13/14 using STM32_SRC_TIMPCLK1/2 names, zero encoded clock divisor, normal
PWM flags, expected channels and exact common carrier. Calculate N from the
derived cycle rate and config-selected carrier with nonzero/remainder/range
checks. Keep carrier and robot pin assignments in config.h; DT hardware metadata
is not a new tuning value.

After native initialization in configurePwm, require readiness and checked
`pwm_get_cycles_per_sec(dev, channel, &uint64_rate) == 0`, nonzero rate and exact
equality to the candidate rate. Also check physical PSC register against its
source-derived value. The PWM API reports cached initialization metadata; it
does not reread a changed PSC or measure the oscillator.

If an additional current software clock consistency check is desired,
`clock_control_get_rate(DEVICE_DT_GET(STM32_CLOCK_CONTROL_NODE), &domain,
&uint32_rate)` dispatches to the verified RCC API. domain is `stm32_pclken`,
whose public fields are bus/div/enr. Fill from the selected timer's second DT
clock spec; require return0 and candidate kernel equality. The helper
STM32_CLOCK_INFO(1,node) exists at stm32_clock_control.h:850-857, but its
designators are enr/bus/div while the struct order is bus/div/enr. Avoid assuming
that C initializer is valid C++17: zero-initialize the object and assign those
three fields, using the same DT extraction/mask/shift expressions. This caveat
is source-observed; no new target compilation was performed in this audit.

The installed TIMPCLK rate branch itself is finite and reads SystemCoreClock
metadata; it is not independent frequency measurement. No dynamic clock owner
may change the timer source/dividers after validation. Detectable mismatch
must fail setup rather than silently mutate the Port already copied by Gate.

## Pin-to-PWM mapping without extra pin assignments

`wiring_analog.cpp:35-53` places arduino_pwm[], arduino_pwm_pins[] and
pwm_pin_index() in an anonymous namespace. They cannot be imported from a header.
`wiring_private.h` does expose zephyr::arduino::arduino_pins[] for GPIO specs.
Reconstruct the two constant PWM tables using public generated-DT macros:

```cpp
#define MOTOR_PWM_SPEC(n, p, i) PWM_DT_SPEC_GET_BY_IDX(n, i),
constexpr pwm_dt_spec specs[] = {
  DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), pwms, MOTOR_PWM_SPEC)
};
#undef MOTOR_PWM_SPEC
constexpr gpio_dt_spec pads[] = {
  DT_FOREACH_PROP_ELEM_SEP(DT_PATH(zephyr_user), pwm_pin_gpios,
                         GPIO_DT_SPEC_GET_BY_IDX, (,))
};
```

The installed lists have 16 paired entries. Bounds-check each config-selected
Arduino pin, then match its GPIO port/pin against pads in a fixed bounded scan.
Require exactly one match, equal list lengths, selected flags0 and distinct
physical GPIOs, including EN. This avoids DIGITAL_PIN_GPIOS_FIND_PIN's ambiguity
between D0 and no match. Validate each selected spec against the intended
PWM3/CH3, PWM1/CH4, PWM3/CH4, PWM4/CH3 metadata and selected pad. The corresponding
global PWM indices are1/2/3/6 and per-device ARDUINO state indices0/0/1/0.
Derive the latter with
`zephyr::arduino::state_pin_index_from_spec_index(specs,index)` from
zephyrPinctrl.h:21-33. Its loop is bounded by this fixed array. Pass the result
to checked init_dev_apply_channel_pinctrl; do not route whole groups.

Expected timer bases derive from parent DT: TIM1 0x40012c00, TIM3 0x40000400,
TIM4 0x40000800. Device identity must equal the expected DEVICE_DT_GET(pwmN).
Offline DWARF also verifies native pwm_stm32_config begins with the 4-byte timer
pointer at offset0, followed by PSC at4; its size is32. This struct is private,
not a public header API. Prefer DT-derived timer bases tied to exact device
identity and pinned package evidence. If the implementation additionally checks
the native config prefix, record that version-specific ABI dependency explicitly,
check non-null config, and copy its pointer bytes with memcpy rather than aliasing
an invented struct. Do not treat a private-layout cast as a portable Zephyr API.

## Register checks before and after first PWM setting

The following are **derived expected software postconditions**, conditional on
successful native reset/init and exclusive ownership, not observed MCU values.
Native init ignores reset-toggle return; unexpected retained state must therefore
be rejected rather than presumed reset. Register consistency checks cannot prove
the physical EN pin is low. Set EN LOW through Gate first in every case.

Before any positive-period pwm_set_cycles call on a newly initialized timer:

| Register/property | Expected for each newly initialized selected timer |
|---|---|
| CR1 | CEN1, up-counter, CKD0, ARPE0, UDIS0, URS0, OPM0, UIFREMAP0, DITHEN0 where supported; expected0x0001 |
| CR2 / SMCR / DIER | 0; no alternate master/slave/external-clock, IRQ or DMA owner |
| PSC | TIM1=63; TIM3/TIM4=4 |
| ARR | 0, as written by native init; **do not demand final N-1 yet** |
| CCMR1 / CCMR2 / CCER | 0 after reset; no channel enabled or PWM mode/preload yet |
| TIM1 RCR / BDTR | RCR0; BDTR has MOE1 and all other writable options0, expected0x8000 |

These initialization checks apply once per newly initialized unique timer.
For TIM3's second configurePwm callback, accept the already validated shared
device without resetting it. Do not apply a reset-state expectation to an already
configured/active timer during later write transactions. Reject an unexpectedly
preowned timer instead of resetting another owner's state.

The native positive-period setter sets selected CCR=pulse and shared ARR=N-1.
On the first enable of a selected channel it sets PWM1 output mode/idle reset,
enables that channel, **enables ARR preload and its CCR preload**, then generates
UPDATE. Therefore ARPE1 is required only after at least one such setting, not
immediately after device initialization. The complete normal four-write state is:

| Register | TIM1 (CH4) | TIM3 (CH3+CH4) | TIM4 (CH3) |
|---|---:|---:|---:|
| CR1 | 0x0081 | 0x0081 | 0x0081 |
| PSC | 63 | 4 | 4 |
| ARR | 249 | 3199 | 3199 |
| CCMR1 | 0 | 0 | 0 |
| CCMR2 | 0x6800 | 0x6868 | 0x0068 |
| CCER | 0x1000 | 0x1100 | 0x0100 |
| CR2 / SMCR / DIER | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| RCR / BDTR | 0 / 0x8000 | not applicable | not applicable |

Express checks using installed named masks, not unexplained magic integers.
CCMR2 CH3 expects OC3M_2|OC3M_1|OC3PE; CH4 analogously expects
OC4M_2|OC4M_1|OC4PE. Both CCxS=0 (output), OCxFE=0, OCxCE=0 and extended
OCxM_3=0. The full OC3M mask includes bit16 and OC4M includes bit24: checking
only the legacy three mode bits is insufficient. CCER has only the selected
CC3E/CC4E enables; no polarity inversion, complementary output or unused channel
enable. TIM1 BDTR must retain MOE and exclude lock/deadtime/off-state/automatic
output/break options, including any supported second-break bits. Do not read
reserved BDTR/RCR locations on TIM3/TIM4 as though they were advanced timers.
In particular, exclude BKE/BK2E/BKBID/BK2BID; do not rely on AOE to restore MOE.
The separate RM0456/ES0499 audit supplies the errata rationale for these guards.

Each used CCR must match its current acknowledged pulse (0..N); unused channels
must remain disabled. A first TIM3 CH3 write yields only0x0068 CCMR2/0x0100
CCER until CH4 is also set. Validate against transaction progress or perform the
complete-state check in settle after all four writes. Cleanup must handle partial
initialization without demanding a full normal state before it can set a zero on
an otherwise validated initialized channel. SR/UIF is asynchronous and is never
part of a whole-register equality check. CCR/ARR reads expose preload values;
they do not establish a fresh latch event or physical0/full-duty waveform.

## EN ownership guard supported by installed GPIO LL APIs

An internal LOW input read alone cannot establish that EN still belongs to the
GPIO output. SPI2 or TIM4's other pinctrl channel can remux the proposed PB9.
After checked GPIO_OUTPUT_LOW configuration, and before accepting later EN
writes/settle/activation, require its source-validated GPIO spec to remain an
output, push-pull and without internal pulls. Use either `<stm32_ll_gpio.h>`
(installed common_ll/include selector, lines53-54 include U5) or explicitly
`<stm32u5xx_ll_gpio.h>`. Both were freshly read, not guessed.

Match the selected EN spec's port to DEVICE_DT_GET(DT_NODELABEL(gpiob)), reject
other ports, validate its physical uniqueness and pin<16, then derive its
one-bit mask from the config-selected spec. Use
`DT_REG_ADDR(DT_NODELABEL(gpiob))`, verified0x42020400, for GPIO_TypeDef access.
No GPIO private-config struct copy or second write path is needed. The public
vendor functions are reads only:

- `LL_GPIO_GetPinMode(const GPIO_TypeDef*, uint32_t Pin)` at :318-321 reads
  MODER; require `LL_GPIO_MODE_OUTPUT`.
- `LL_GPIO_GetPinOutputType(...)` at :387-389 reads OTYPER; require
  `LL_GPIO_OUTPUT_PUSHPULL`.
- `LL_GPIO_GetPinPull(...)` at :529-533 reads PUPDR; require `LL_GPIO_PULL_NO`.
- `LL_GPIO_IsOutputPinSet(...,uint32_t PinMask)` at :867-869 reads ODR and can
  check the commanded latch alongside checked native input readback. It does
  not measure the external driver EN voltage.

All accept the GPIO **bit mask**, not the Arduino index or bare bit number.
The mode/pull functions require one selected bit; do not pass a zero mask or
multi-pin combination. These are finite inline register reads without imports.
The installed gpio_stm32_config/pad-manager path already audited in
P0_gpio_installed_contract_20260923.md maps OUTPUT_LOW with no single-ended/pull
flags to output/push-pull/no-pull, writes BRR LOW before applying output mode,
and preserves checked configure/write results when called natively. This guard
must not silently reconfigure a remuxed pin during a HIGH request; mismatch is
a failed ownership check and activation remains unavailable. Existing bounded
inhibition still attempts its authorized LOW cleanup. No post-check eliminates
a race with another configurator, so exclusive ownership remains mandatory.

## Evidence identities and reproduction

Abbreviations: C is installed core `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`;
Z is C/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include;
E is C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf. All SHA-256:

| Artifact | SHA-256 |
|---|---|
| E | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| generated DT | 5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80 |
| installed core config | a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba |
| wiring_analog.cpp | 32d805872068e175b03cc291d3697f3ea7443501424dd870165d0bebeddd6c98 |
| stm32_clock_control.h | 5ff73868f537e9a761b7b4b45d7fed7147a929cb526760cb5678a01afa2f3936 |
| stm32u5_clock.h | 5889b5061fd67b5414e0cc6ef1f1fde252e7c2f6a0ee53ba1ed616439db08d0d |
| installed stm32u5xx_ll_tim.h | 1da2403c2e6d11b7537e863b2715b550a82938d200b32cfb134fedfae39f0b46 |
| installed stm32u585xx.h | 8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06 |
| installed stm32_ll_gpio.h | 714197e0cd2890fbe1539d52a0544f3c60bb14fd52ed48036ae2a646b48be80d |
| installed stm32u5xx_ll_gpio.h | 5e6772bee2e03314b266d5bb9ad448c02bcd5a41f618fc126375006db7cfc346 |
| pinned clock_stm32_ll_u5.c | ae2a361260bda1c543824d45c7b7bd0b6124590047cd82e0cb9163cb4a84b1cd |
| pinned st,stm32-rcc.yaml | efb3a40a4e0a41347e26fe8e215e65c24b593f772eb4747f3f69c568d2e91af8 |
| raw clock.json | cba7a393e4abd0a9083dd9ebb774a20ef629f2242184818329568f915d82d6ca |

Pinned primary source commit is Arduino Zephyr
1743741760ee5d2d58da50d504855d43f9f8e826:
[clock driver](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/clock_control/clock_stm32_ll_u5.c),
[RCC binding](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/dts/bindings/clock/st%2Cstm32-rcc.yaml).
Native PWM init/set evidence is retained in P0_pwm_installed_contract_20260923.md
and its exact raw receipt, complemented by freshly captured init/get disassembly.
Installed LL mode/preload/enables and complete bit definitions are in clock.json.

All six read-only board Linux requests and all ten nested offline nm/GDB/objdump
commands completed exit0; pinned source reads succeeded. Transport was
tools.board_tool.remote with exact serial2629958581, SUMO_TRANSPORT=adb and the
installed `%LOCALAPPDATA%/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe`.
Raw JSON preserves exact Python programs, commands, numbered excerpts, hashes,
stdout and stderr. GDB was `-nx -nh -batch E` only; it never attached a target.

One exploratory `p pclken_N` printed a different translation unit's same-named
static symbol, despite exit0. It is not used for conclusions. The corrected
expressions `p *pwm_stm32_config_N.pclken@2` establish the actual pointer-owned
arrays: TIM1 enable bus164/enr2048 + domain14; TIM3 bus156/enr2 + domain13;
TIM4 bus156/enr4 + domain13. The original exploratory output is preserved.

Next: freeze the explicit construction clarification and source-derived constants,
combine with the separate primary manual/errata update audit, then implement and
independently test the concrete native backend. These source expectations do not
close SC-AI, runtime WCET, physical waveform/PINMAP or motor-run authorization.
