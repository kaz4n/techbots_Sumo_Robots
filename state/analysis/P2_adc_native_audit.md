# P2 native ADC1 prerequisite checkpoint

2026-09-23. **Installed register operations, clock metadata and the ordinary
single-channel ADC sequence are verified sufficiently to define a concrete
candidate. The implementation contract is not ready for adoption:** detailed
current ADC errata, operating-limit confirmation and the final ownership/IRQ
guards below remain explicit source checks. No ADC implementation or new
decision is supplied by this audit.

Scope: read-only files on UNO Q Linux using existing ADB serial2629958581 and
the installed32.0.0 ADB executable; offline packaged-ELF inspection; local
official RM0456 PDF; pinned primary source and official errata retrieval.
No MCU connection, live register read, ADC call, pin operation, upload or reset.
Only this report, `P2_adc_native_raw/`, and the authorized correction to
`P2_next_hal_audit.md` were written. No jobs remain running.

## Correction to the preceding selection audit

The actual public type is `fsm::RobotInput`, singular (`src/core/fsm.h:385–403`).
It already contains `vbat_valid` at398. `fsm_robot.cpp:208` inhibits initialized
operation for invalid/nonfinite battery input; :677 passes NaN to the governor
when invalid. P1_robot_contract's input section already requires a valid finite
battery sample. The base `core::Inputs` alone was an incomplete view. The new
HAL should provide validity and sample age to the existing boundary, without a
new core field or a second B6 voltage filter. The older audit is corrected.

## Installed identities and exact evidence

Let C be `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`,
I be `C/variants/arduino_uno_q_stm32u585xx/llext-edk/include`, and H be
`I/modules/hal/stm32/stm32cube/stm32u5xx`. The old F-078 audit's package identities
were matched by fresh reads; no deployed-loader flash identity was measured.

| Source | SHA-256 |
|---|---|
| H/drivers/include/stm32u5xx_ll_adc.h | `c72e076314ab1e3ec41928bfb04c942e321065a47ca778358f0503984f0f441f` |
| H/drivers/include/stm32u5xx_ll_rcc.h | `08a13b1c17bc496658c1ad1b32fc4718d4d864aecf3165a47c360cbdc82c8191` |
| H/drivers/include/stm32u5xx_ll_bus.h | `a771a988182391a991c4b419c47d4e2cbf70f79f378add0c60fe9f3cb5cac6f2` |
| H/drivers/include/stm32u5xx_ll_pwr.h | `5f7f9a5c03f840bd145ee473abe55d42a2f5138eea47a46512395aa3c41ec18f` |
| H/soc/stm32u585xx.h | `8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06` |
| generated devicetree_generated.h | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| generated autoconf.h | `52178f5eefcf276720b859bdd60fc87ca4207b0130ac1fd5ba099af74b877a0c` |

`installed_source_01..05.json` preserve paths, hashes, numbered selected lines,
offline GDB commands, individual exit codes and missing-name errors. The
collector and remote query scripts are included for reproduction. Missing
guessed GDB symbols are recorded as absent; they are not API availability proof.

Downloaded exact [Arduino Zephyr adc_stm32.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/adc/adc_stm32.c)
is76,275 bytes, SHA256
`d70756d2a035794897a0aab1c2c5393b92c34d3aac885bac7d6dc72b58caf397`,
matching the previous source/binary audit. The corresponding
[clock_stm32_ll_u5.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/clock_control/clock_stm32_ll_u5.c)
is28,846 bytes, SHA256
`ae2a361260bda1c543824d45c7b7bd0b6124590047cd82e0cb9163cb4a84b1cd`.
Both are retained with download receipts. Installed package ELF is the previously
identified `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

## Concrete map and clock

- A0 remains Arduino14, PA4, ADC1 channel9; A1 remains Arduino15, PA5, channel10.
  ADC1 device ordinal17 has base0x42028000, flags1/deferred, native API0x0801c5f4,
  init0x0800a129 and no deinit. Its packaged state has initialized=false; this
  is an initializer, not a statement about current live state.
- DT:2922–2925 assigns ADC1 IRQ37/priority0. The packaged IRQ37 table already
  points to adc_stm32_isr_37 at0x080098e1. ADC1 init calls its IRQ setup routine,
  which sets priority then enables NVIC37 (0x08018304–0x08018316). A polling
  backend must exclude this stock owner, not merely avoid requesting interrupts.
- DT:2969–2995 and the packaged config independently agree on peripheral clock
  `{bus=140,div=0,enr=1024}` and kernel `{bus=9,div=0,enr=4980968}`.
  These mean AHB2 enable ADC1 and STM32_SRC_HCLK with ADCDAC selector0 in
  RCC_CCIPR3. DT:3058/3073 chooses ASYNC/prescaler4; config clk_prescaler is
  524288 (0x80000, ADC_CCR_PRESC_1 / LL_ADC_CLOCK_ASYNC_DIV4).
- Existing clock audit establishes HCLK160MHz from MSIS4MHz, PLL1 M1/N80/R2,
  AHB/1. Thus the candidate ADC conversion clock is **40MHz**, not160MHz.
  Clock driver:256–263 returns HCLK for bus9. This remains installed-source
  metadata, not measured frequency or unconditional live register truth.
- RCC ordinal9 is exported at0x0801befc. Actual native API entries are on
  0x080189a3, get_rate0x0800b9ed, configure0x08018a13. `on` validates the bus,
  sets its enable bits and performs one readback; HCLK get_rate has no hardware
  wait. The candidate can use checked inline device dispatch plus register
  consistency guards. There is no reason to invoke RCC device initialization.
- **The ADCDAC selector is shared.** ADC4 ordinal54 and DAC1 ordinal64 are
  non-deferred, status-okay devices, not uninitialized resources to seize.
  ADC4's packaged config selects the same HCLK selector/prescaler4. Preserve the
  shared selector; reject an incompatible value instead of rewriting it.
  ADC1's independent common CCR can be configured while ADC1 is disabled.
- PA4's Arduino ADC pinctrl entry is pinmux144/pincfg0. Default/sleep ADC1
  pinctrl states have zero pins; the Arduino state has six. Do not apply the
  whole six-pin state. Direct installed LL GPIO mode/pull helpers permit the
  one-pin analog/no-pull route without calling ADC `device_init`. Check GPIOA
  readiness/clock and pin lock/ownership first; final target assertions must
  bind the native address, channel and pin to the installed DT.

ADC1 common layout is especially important: installed `ADC_Common_TypeDef`
contains **only CCR at offset0**. `ADC12_COMMON_NS` is0x42028308 (CMSIS:1855),
not0x42028300 with a fabricated generic-family CSR/CCR layout. Installed
ADC_TypeDef uses ISR0, IER4, CR8, CFGR1=0x0c, CFGR2=0x10, SMPR1=0x14,
PCSEL=0x1c, SQR1=0x30, DR=0x40, DIFSEL=0xc0, CALFACT=0xc4, CALFACT2=0xc8.
Do not access ADC4-only fields merely because the common C struct contains them.

## Supported candidate algorithm

The official [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf)
is already in `build/cache/RM0456_Rev6_52152e41.pdf`, SHA256
`52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`.
`manual_page_hashes.json` identifies the relevant pages for reproduction.
The sequence below is conditional on exclusive ownership and the remaining
operating/errata checks; it is not an adopted contract or a measured timing claim.

1. **Claim without stealing.** Require the stock ADC1 device state to be
   never-initialized, not just `device_is_ready()==false` (failed initialization
   is also not-ready). Require no pending/active/enabled ADC1 IRQ owner, no
   competing raw register/ADC API user, compatible reset state and the expected
   clocks. Require the established analog-supply enable ASV and shared HCLK
   selector rather than changing global power/clock settings. Never reset ADC1
   or clear another owner's flags to make admission pass. Package initializers
   alone cannot establish these runtime conditions.
2. **Power/calibrate in finite setup stages.** With ADC1 disabled and its
   command bits idle, set common divider4 and single-ended mode; exit DEEPPWD,
   enable ADVREGEN, then observe LDORDY with a deadline plus finite poll/service
   guard. RM33.4.6 p1276 and33.4.8 pp1277–1278 require regulator-ready, ADEN0,
   CAPTURE_COEF0 and LATCH_COEF0 before calibration. Choose ordinary offset plus
   linearity calibration once from reset using the installed LL command, then
   observe ADCAL0. On timeout, remain invalid/faulted; do not pretend calibration
   completed or run another command while it is busy.
3. **Avoid extended calibration in this increment.** RM33.3 p1267 excludes it
   on U575/U585 revision X. Ordinary calibration is documented independently
   of that enhancement. No calibration-factor save/reinjection is needed.
   The installed driver's extended-mode condition is literally
   `(dev_id != 0x482) && (rev_id != 0x2001)` (source:672), which skips all U585
   IDs; do not copy it as a general silicon-revision policy. Its current
   offset-only behavior is not a substitute for deciding the new sequence.
4. **Enable with a fresh readiness flag.** Installed LL declares four ADC
   cycles between calibration completion and enable (:1960), and its comments
   estimate520 offset/131072 linearity cycles. At40MHz the latter is about3.28ms;
   it belongs in setup, with explicit bounded failure, not a control-tick spin.
   Use a verified minimum wait mechanism (including clock quantization) and
   preserve command-write restrictions. Clear ADRDY by W1C, issue ADEN and
   wait boundedly for fresh ADRDY (RM33.4.9 p1281). Clear the ordinary calibration
   mode/index controls while disabled if required by the selected exact enable
   guard; do not start conversion during calibration or disable.
5. **Configure the narrow regular mode while idle.** Follow RM33.4.10 p1282's
   write-state constraints; configuring regular controls after enable/ADRDY
   while ADSTART/JADSTART are0 satisfies them. Candidate: 14bits, software
   trigger, single conversion, no auto-delay/continuous/discontinuous/injected
   operation, no IRQ/DMA/MDF/oversampling/bulb/triggered sampling/watchdog,
   no offset/gain/left-shift transformation. Use channel9 preselection, one
   regular rank/channel9 and814 sampling cycles. Preserve reserved bits:
   CFGR1 reset bit31 is1 and must remain1 (RM33.6.4 p1347).
6. **Start one identifiable sample.** Verify current mode/ownership, ADEN1,
   ADCAL/ADDIS/ADSTP/ADSTART/JADSTART/JADSTP all0. Clear stale regular
   EOC/EOS/OVR/EOSMP with a W1C mask and confirm their expected cleared state
   before issuing ADSTART. Start one request identity and a single deadline.
   No other producer may set these flags or consume DR.
7. **Poll without blocking calls.** Each poll makes a fixed small number of
   register/time reads. Reject ownership/mode change, OVR and deadline expiry;
   accept only current EOC+EOS and a completed single conversion. RM33.4.23–24
   pp1294–1295 ties EOC to new DR data and EOS to the last result. DR read clears
   EOC; EOS is W1C. Read DR once as32bits, reject a value outside0..16383 before
   narrowing, and recheck status/mode/time before publishing. Do not require
   observing ADSTART1: a valid conversion may complete before the first poll.
   Clear/confirm stale flags only while no previous conversion is active.
8. **On timeout, never publish a late sample.** For an owned active regular
   conversion, issue ADSTP only under its documented preconditions. Observe
   ADSTART/ADSTP clearing in bounded subsequent steps. RM33.4.18 pp1288–1289
   says the abort discards partial data and requires ADSTART0 before assuming
   stopped. Only after regular/injected conversion and stop commands are idle
   may ADDIS be issued and ADEN0 awaited boundedly. If any stage stalls, retain
   fault and ownership; no reset, restart, reusable success receipt or false
   stop acknowledgement. On ownership loss, avoid blind cleanup writes.

Actual LL CR commands deliberately suppress all read-as-set command bits during
RMW: `ADC_CR_BITS_PROPERTY_RS` includes ADCAL/JADSTP/ADSTP/JADSTART/ADSTART/
ADDIS/ADEN (:479–480). Start/stop bodies:8002–8027, enable:7867–7873,
calibration:7948–7962. Use these installed operations or equivalent proved masks;
naive `CR |= command` can replay a concurrent command. ISR flag clear helpers
write the flag mask (:8542 onward); they are **W1C**, unlike timer SR/UIF clears.
RM pp1280–1281 also advises `__DMB()` after calibration-control/coefficient
accesses because they cross the ADC clock domain; include this in the exact
sequence rather than assuming C volatile alone supplies it.

Useful candidate register values, subject to preserving reserved/reset state:
CCR PRESC=0x80000; CFGR1=0x80000000; CFGR2=0; IER=0; DIFSEL=0;
PCSEL=0x200; SMPR1 SMP9=7 at bits29:27; SQR1 SQ1=9 at bits10:6 and L=0.
OFR/GCOMP transformations and injected/extra-rank configuration must remain
disabled. Readback is mode consistency, not physical accuracy.

RM33.4.13/22 pp1284/1294 gives814+17=831 ADC cycles for this single14bit sample:
20.775us at the source-derived40MHz. This excludes synchronization, CPU/scheduler
overhead, faults and analog settling requirements. It is not a measured WCET,
chosen deadline, proof of the divider's acquisition accuracy or permission to
claim an800us tick. No new timing constant is selected here.

## Remaining checks and exact next action

1. **Finish current errata paragraphs.** No errata PDF existed in build/cache.
   Main long-name ST/ST-China requests timed out; a guessed Japan Rev10 filename
   returned HTML and was rejected. The official Japan index identifies the
   real archive `ES0499_Rev-10.pdf` and stable latest ST alias
   [dm00648236.pdf](https://www.st.com/resource/en/errata_sheet/dm00648236.pdf).
   A successful web extraction of the latter established ES0499 Rev12, June2026,
   51pages, and table3 p4 lists ADC1 sections2.8.1 (AWD output) and2.8.2
   (injected data register), applicable X/W/U; ADC4 issues are separate2.9.1/2.
   Subsequent actual paragraph requests returned404/timeouts; direct download
   timed out. **The detailed current ADC/calibration-related coverage is still
   incomplete.** Do not infer no errata from errors or silently use Rev10/11 as
   current. Retrieve Rev12 sections2.8/2.9 plus relevant supply/clock/reference
   errata and revision history from that stable alias; retain text/pages/revision.
2. **Confirm electrical limits and calibration timing in current DS13086.**
   Match40MHz and chosen sampling/calibration mode to the documented supply,
   voltage-scaling and frequency conditions. The nominal3.3V board/divider is
   not a measured VDDA/VREF. Until this is checked,814cycles/40MHz is a software
   candidate, not an established accuracy guarantee or a selected init timeout.
3. **Finish the minimal admission guards.** Locate/hash the installed
   `core_cm33.h` (the attempted `I/cmsis/CMSIS/Core/Include/core_cm33.h` is absent)
   and verify the chosen NVIC enable/pending/active read helpers. Bind the actual
   compile-time ADC_NS/common/PA4 constants. Confirm inherited ADC4/DAC behavior
   does not create concurrent conversion/output producers or alter the shared
   HCLK/ASV state during this backend's lifetime. ADC4/DAC being non-deferred
   means a blanket uninitialized-device requirement would be wrong. A native
   owner also needs an explicit whole-application exclusion of analogRead,
   adc_read, stock ADC1 initialization and unrelated PA4 users; a private bool
   cannot arbitrate with those APIs automatically.
4. **Then adopt a narrow implementation contract under D-051/D-075**, with the
   actual native state machine, timeout/clock-failure policy, exact mode guards,
   voltage calibration provenance and reset-only fault behavior. Independently
   test the real native source and retain it in an inert compile-only target
   probe. Preserve partial-init/late/overrun/failed-stop failures. The target
   imports and source guards must be checked on that actual implementation.

These are source/implementation prerequisites, not a request for human action.
No physical facts, PINMAP approval, battery accuracy, silicon revision, runtime
fault timing, gate pass or motor authorization is inferred. D077's completed
work remains separate from this deliberately unfinished ADC prerequisite audit.
