# P2 ADC1 ownership and NVIC source audit

2026-09-23. **The installed ADC1/ADC4/DAC1 ownership and finite NVIC read
prerequisites are established for a narrow software implementation. A material
clock limitation remains: stock MSIS hardware auto-calibration is enabled, and
ordinary RCC readiness is not proof that it remains locked.** This report does
not qualify runtime battery accuracy or close that global clock issue.

Scope: read-only UNO Q Linux files through ADB serial2629958581, offline packaged
ELF inspection, and the already cached official RM0456. No MCU attachment,
register read, ADC/GPIO call, upload, reset, or hardware measurement. Only this
report and `P2_adc_ownership_raw/` were written. No source/configuration/shared
ledger edits. All collection commands have completed.

## Reproducible evidence

Let C be `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`, I be
`C/variants/arduino_uno_q_stm32u585xx/llext-edk/include`, and H be
`I/modules/hal/stm32/stm32cube/stm32u5xx`. Receipt names below are in
`P2_adc_ownership_raw/`. `installed_01.json`, `installed_02.json`,
`installed_03.json`, `installed_03b.json`, `installed_04.json`, and
`installed_04b.json` retain exact commands, selected numbered source lines,
hashes, exit codes and unsuccessful guessed symbol queries. Empty searches are
not evidence that a hardware feature is absent.

Nine complete installed headers are in `headers/`: STM32U585 CMSIS,
`core_cm33.h`, and LL ADC/GPIO/bus/RCC/PWR/DAC/EXTI. `headers/manifest.json`
records original paths, sizes and remote SHA-256 values; every local byte stream
was checked against that remote hash. They total2,779,053 bytes.

| Source | SHA-256 |
|---|---|
| I/modules/hal/cmsis_6/CMSIS/Core/Include/core_cm33.h | `28837edccc98d00852e30213482bb2e6d039cdd7e696b976b01bd1621a38e283` |
| I/zephyr/include/zephyr/device.h | `300420020155fc22a7e4e3a867f26fe30c6a79b9be3474caf990bacfecbd2d19` |
| H/soc/stm32u585xx.h | `8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06` |
| I/zephyr/include/generated/zephyr/devicetree_generated.h | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| I/zephyr/include/zephyr/drivers/clock_control/stm32_clock_control.h | `5ff73868f537e9a761b7b4b45d7fed7147a929cb526760cb5678a01afa2f3936` |
| C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf, reused identity | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

The pinned [Arduino Zephyr ADC source](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/adc/adc_stm32.c)
and [clock source](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/clock_control/clock_stm32_ll_u5.c)
are reused from `P2_adc_native_raw/`, with hashes respectively
`d70756d2a035794897a0aab1c2c5393b92c34d3aac885bac7d6dc72b58caf397` and
`ae2a361260bda1c543824d45c7b7bd0b6124590047cd82e0cb9163cb4a84b1cd`.
No new network retrieval was required for this audit.

## ADC1 is a deferred stock device, not a free-standing peripheral

`device.h:458–471` publicly defines `device_state`, including `uint8_t init_res`
and `bool initialized : 1`; `struct device` exposes its `state` pointer. Use
`state != nullptr && !state->initialized && state->init_res == 0`, rather than
`!device_is_ready()`. Offline `do_device_init` at0x08019e2c calls initialization,
stores a nonzero failure result when needed, and sets `initialized` on both
success and failure. ADC1's packaged device17 has deferred flag1 and no deinit.
Its initializer is false/zero; this says nothing about current live state.

The flag is set after the initializer returns, so it cannot exclude an
initialization already in progress. Admission must occur in serialized setup,
under a whole-application exclusion of stock ADC1 initialization/read APIs and
unrelated register writers. A private owner boolean cannot lock those callers.

CMSIS:106 assigns `ADC1_IRQn = 37`; :182 assigns `ADC4_IRQn = 113`. The actual
`core_cm33.h` provides finite, read-only `__NVIC_GetEnableIRQ` (:2377–2387),
`__NVIC_GetPendingIRQ` (:2415–2425), and `__NVIC_GetActive` (:2466–2476).
For a nonnegative IRQ each tests one bit in ISER, ISPR or IABR, respectively;
there is no wait, write or scheduler call. Ordinary `NVIC_Get*` aliases are at
:2272/2274/2277 under the non-virtual CMSIS branch. IRQ37 is bank1/bit5;
IRQ113 is bank3/bit17. Use the actual target aliases or these documented
`__NVIC_` bodies, with compile verification, rather than a fabricated helper.

The packaged IRQ37 wrapper at0x080098e0 loads ADC1 device17 at0x0801c238;
IRQ113's wrapper at0x080098ec loads ADC4 device54 at0x0801c214. Each dispatches
the shared ISR with its own device argument. ADC1's deferred init enables IRQ37
at0x08018304–0x08018316. Require IRQ37 enabled/pending/active all zero before
admission and throughout polling. Do not clear or disable an unknown owner to
make that condition pass. Dynamic IRQ installation is enabled in this build
and must be excluded for these resources.

## Stock ADC4 and DAC1 are compatible only while idle

ADC4 device54 is non-deferred. Its installed default pinctrl has zero states.
`adc_stm32_init:1933–2006` selects its clocks, enables analog supply and its
regulator, configures IRQ113, calibrates, selects software triggering, then
explicitly calls `adc_stm32_disable(adc, true)` at2004. Its final action unlocks
the context semaphore; it does not create a conversion producer or start a
periodic acquisition. The installed disable function at0x080183d2 issues a
stop if necessary, waits for ADSTART to clear, issues ADDIS and waits for ADEN
to clear. Those stock waits are unbounded; the new driver must not call them.
Startup does not enable ADC4 IER bits. Calibration/readiness flags can remain
set; a blanket ISR==0 guard would be unjustified.

Thus a normally completed fresh boot can have ADC4's regulator on and NVIC113
enabled, with ADC4 itself disabled and no conversion in flight. The source
ignores some subroutine error returns; an initialized/ready device alone does
not prove the required live state. Read the guard fields below. Stock
`CONFIG_ADC_STM32_DMA`, ADC_ASYNC, ADC_STREAM, PM and PM_DEVICE are unset;
this removes those automatic paths from the packaged build, not future callers.

DAC1 device64 is also non-deferred. Its initializer at0x0800c38c enables its
peripheral clock and applies default pinctrl only. The two entries are
pinmux144/pincfg0 and pinmux176/pincfg0: PA4 and PA5 analog/no-pull. The initializer
contains no DAC register write, output enable or conversion producer. Given
peripheral reset and no later DAC calls, DAC CR remains at its reset value0.
Later `dac_channel_setup`, `dac_write_value`, or the Arduino analog-write path
are separate potential owners; initialization alone cannot exclude them.

## Concrete finite admission and ongoing checks

These are proposed software predicates, not measurements performed here. Checks
must be repeated at request and before sample publication, with required
phase-specific ADC1 mode comparisons. A failed ownership check remains invalid;
do not reset or reconfigure the other device to repair admission.

| Resource | Required condition and exact installed names |
|---|---|
| Stock ADC1 owner | Public state predicate above; IRQ37 enable/pending/active all0; no stock ADC1 API or dynamic IRQ producer. |
| ADC4 conversion owner | Its stock init has completed successfully; IRQ113 pending/active0 (enabled may be1); `ADC4->IER == 0`; `(ADC4->CR & (ADC_CR_ADEN | ADC_CR_ADDIS | ADC_CR_ADSTART | ADC_CR_ADSTP | ADC_CR_ADCAL)) == 0`; `(ADC4->CFGR1 & (ADC_CFGR1_EXTEN | ADC_CFGR1_CONT | ADC4_CFGR1_DMAEN | ADC4_CFGR1_DMACFG)) == 0`. Preserve ADVREGEN and calibration flags. No later ADC4 start, calibration, external-trigger setup, ADC API, DMA/raw writer or queued acquisition. |
| PA4/DAC output | DAC1 init completed successfully; `(DAC1->CR & (DAC_CR_EN1 | DAC_CR_CEN1 | DAC_CR_TEN1 | DAC_CR_DMAEN1 | DAC_CR_WAVE1)) == 0`. These exclude channel1 output, calibration, trigger, DMA and waveform producers. No DAC/Arduino analog-write operation on A0. Channel2 need not be seized or rewritten. |
| PA4 pad | GPIOA device/clock valid; PA4 unlocked; existing analog/no-pull state remains compatible. `LL_GPIO_GetPinMode(GPIOA, LL_GPIO_PIN_4) == LL_GPIO_MODE_ANALOG`, `LL_GPIO_GetPinPull(...) == LL_GPIO_PULL_NO`, `LL_GPIO_IsPinLocked(...) == 0`. Exact helpers at LL GPIO:318/529/755. Do not apply the stock ADC six-pin Arduino state or alter A1. |
| Shared analog supply | `LL_PWR_IsEnabledVddA() == 1` (LL PWR:2005–2009; `LL_PWR_IsEnabledVDDA` is its alias). Reads `PWR->SVMCR & PWR_SVMCR_ASV`. Retain ASV; do not write shared supply controls from this backend. |
| ADC clock mux | `(RCC->CCIPR3 & RCC_CCIPR3_ADCDACSEL) == 0`, the installed HCLK selector. Do not invoke clock configure or change the shared selector. Preserve installed nominal HCLK160MHz lineage and check its expected register mode; frequency/lock qualification remains below. |
| Peripheral clocks | ADC1 uses `RCC_AHB2ENR1_ADC12EN` bit10, aliased by `LL_AHB2_GRP1_PERIPH_ADC1`; ADC4 uses `RCC_AHB3ENR_ADC4EN`. Enable only ADC1's authorized gate if needed, then read it back before peripheral access. Require existing ADC4/DAC/GPIO clocks for meaningful idle reads; no peripheral reset or unrelated clock-off. |
| ADC1 reset admission | After its authorized clock enable and before configuration, check compatible pristine controls: CR=DEEPPWD (`0x20000000`), IER0, CFGR1=`0x80000000`, CFGR2/PCSEL/DIFSEL/common CCR0 and no configured sequence/injected/offset/gain producer. The reserved CFGR1 bit31 is1 and must remain1. Do not require calibration-factor registers to be zero or access ADC4-only members. Configure/read back the exact owned register set in the implementation contract. |

These conditions are sufficient only with the exclusion of concurrent callers.
A sample-time snapshot cannot prevent another thread/ISR from starting ADC4
immediately afterward. In particular, matching both ADC prescalers to /4 does
not establish their relative phase or eliminate simultaneous conversions.
The chosen ADC4-disabled/no-producer condition addresses that ownership hazard.

The finite clock-enable alternatives are actual `LL_AHB2_GRP1_EnableClock`
(masked set and one readback) or checked dispatch to the installed RCC device9
`clock_control_on`. Previous `P2_adc_native_audit.md` binds its `{bus=140,
div=0,enr=1024}` and installed on/get_rate entry points; `installed_01.json`
independently disassembles `stm32_clock_control_on`, which validates the bus,
sets bits and reads them back without a wait. Require the RCC device/API/method
and expected clock specification before dispatch; do not call device init.

Bind target constants to ADC1 base0x42028000, ADC1 channel9, PA4/ArduinoA0,
and `ADC12_COMMON_NS` at0x42028308. The actual common type contains only CCR
at offset0. Full header copies permit meaningful compile assertions instead
of mirroring invented peripheral layouts in tests.

## Clock finding and limit of a stock-compatible implementation

Generated DT:1580 sets `DT_N_S_clocks_S_clk_msis_P_msi_pll_mode 1`; :21904
sets MSIK mode0. `stm32_clock_control.h:578` uses that MSIS property. Pinned
clock source:840–843 selects MSIS and calls `LL_RCC_MSI_EnablePLLMode()`.
The packaged init independently sets RCC CR bit6 at0x0800bbac and bit3 at
0x0800bbb4. This is MSI hardware auto-calibration against LSE, distinct from
ordinary PLL1 multiplication. Requiring MSIPLLEN0 would reject expected stock
initialization. `LL_RCC_IsEnabledPLLMode()` at LL RCC:2109–2111 is only an
enable-bit read; `LL_RCC_GetMSIPLLMode()` reads the selection bit.

Official [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf),
cached SHA256 `52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`,
p491 explains loss of LSE pulses unlocks MSI auto-calibration and degrades
accuracy. Pages511/916–917/920 route that event through EXTI23 and vector125
on supported STM32U575/585 revisions, explicitly excluding revisionX.
Pages514–515 define MSIPLLEN as mode enable and MSISRDY as oscillator ready;
neither establishes current auto-calibration lock. Selected page text and
SHA-256 values are retained in `rm_msi_pages.json` and
`rm_msi_unlock_pages.json`. No existing EXTI capture/clear ownership was proved;
an unarmed historical unlock cannot be ruled out by a current ready bit.

Concrete finite nominal-lineage checks use LL RCC's actual read helpers:
`LL_RCC_GetSysClkSource() == LL_RCC_SYS_CLKSOURCE_STATUS_PLL1` (:2564),
`LL_RCC_GetAHBPrescaler() == LL_RCC_SYSCLK_DIV_1` (:2683),
`LL_RCC_PLL1_GetMainSource() == LL_RCC_PLL1SOURCE_MSIS` (:3981),
`LL_RCC_PLL1_GetDivider() == 1` (:4097), `LL_RCC_PLL1_GetN() == 80`
(:4003), `LL_RCC_PLL1_GetR() == 2` (:4075),
`LL_RCC_PLL1_IsReady() == 1` (:3866),
`LL_RCC_PLL1_IsEnabledDomain_SYS() == 1` (:4207), and
`LL_RCC_PLL1FRACN_IsEnabled() == 0` (:4229). For MSIS, require the source
selection `RCC->ICSCR1 & RCC_ICSCR1_MSIRGSEL` set,
`LL_RCC_MSIS_GetRange() == LL_RCC_MSISRANGE_4` (:2299), and
`LL_RCC_MSIS_IsReady() == 1` (:2072). Preserve expected
`LL_RCC_IsEnabledPLLMode() == 1` and
`LL_RCC_GetMSIPLLMode() == LL_RCC_PLLMODE_MSIS`. Compare fields rather than
the whole PLL1CFGR: the stock clock initializer also enables other PLL outputs.
These numeric divider/multiplier expectations derive from DT and agree with
the packaged initializer. They are nominal configuration checks only; the
power/VOS operating-limit contract is supplied by the separate datasheet audit.

Root's selected implementation scope is therefore to preserve stock MSIS mode,
check nominal metadata and mode consistency, use finite count backstops, and
make **no lock-detection or frequency-qualification claim**. No ADC-local RCC
recovery, mode toggle, EXTI ownership, or clock rewrite follows from this audit.
The coordinator's current ES0499 section2.2.27 source review is the authority
for that erratum; global runtime clock policy/qualification remains an explicit
integration blocker. Software host tests and inert target compilation under
D-075 can proceed without manufacturing runtime acceptance.

## Next action

Use the saved headers and predicates in the narrow B5 ADC implementation and
independent native tests, including stock ADC4 IRQ-enabled idle, failed owner
admission, changed mode, partial initialization and no late publication. The
coordinator supplies the adopted voltage/timeout/calibration contract and
datasheet/errata limits. Resolve the global MSI auto-calibration policy before
deployment/runtime acceptance. This audit makes no physical, silicon-revision,
accuracy, timing, phase-gate or motor-run claim.
