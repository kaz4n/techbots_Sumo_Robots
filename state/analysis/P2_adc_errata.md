# P2 ADC errata applicability

2026-09-23, source review only. The official [ES0499 Rev12, June2026](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
was retrieved through ST's product-documentation link and subsequently reopened
successfully. All51 pages were available; the earlier retrieval failure in
P2_adc_native_audit.md is superseded for the sections below. No MCU was accessed.

Source findings (page numbers are printed pages):

- Table3 and2.8.1–2.8.2, pp4/24–25: the watchdog-output and injected-register
  limitations cover X/W/U. A regular-only, watchdog-free acquisition avoids them.
- 2.9.1, p25: simultaneous ADC1/ADC4 conversion requires matching clock phase,
  not just equal frequencies. Divider use is allowed when conversions do not
  overlap.
- 2.9.2, pp25–26: ADC4 can retain a clock request after reset. Its workaround
  changes enable/regulator state; it is not a reason to seize another owner.
- 2.7.1/2.8.3, pp24–25 correct older datasheet sampling/accuracy values.
- 2.10.1, p26 concerns reference-buffer startup in low-voltage/Stop conditions.
- 2.2.8/2.2.26/2.2.27, pp9/16 concern clock requests, low-power entry and MSI
  automatic PLL calibration. MSI automatic calibration differs from PLL1.
- Table2 identifies X/W/U revisions; no physical revision was read here.

Implementation conclusions: retain HCLK160MHz/div4 only with an explicit
whole-application exclusion of ADC4 conversion producers, stock ADC1 APIs,
unrelated PA4/DAC1-channel1 users and clock/power reconfiguration. ADC4 may be
initialized and have its NVIC interrupt enabled while idle; do not reject that
legitimate boot state merely by IRQ enable. Live mode guards supplement, but
cannot replace, exclusive application ownership. No ISR or another thread may
start an ADC4 conversion between checks.

Use ordinary single-ended regular acquisition, no injected sequence/watchdog,
no internal-reference measurement, no VREFBUF/low-power writes and no borrowed
ADC4 workaround. Check installed MSI automatic-calibration state before relying
on the chosen clock lineage. Current DS13086 and RM0456 remain separate sources
for operating limits, LFTRIG and conversion/calibration sequencing; see
P2_adc_limits.md and P2_adc_ownership.md. These conclusions are an engineering
interpretation for the narrow candidate, not a global errata clearance, measured
supply/clock/accuracy, deployed-loader match, PINMAP or phase acceptance.

Retrieval provenance: canonical URL above, web extraction2110 lines/51pages;
opened2026-09-23 Asia/Dubai. Relevant extracted intervals1025–1125 and365–400,
698–725 were inspected. No local PDF hash is claimed because this retrieval
used the web PDF reader, not a saved byte-identical local PDF.
