# P2 ADC1 electrical limits and timing source check

2026-09-23, Dubai. Source-only audit for the proposed A0/ADC1 driver under
D-051/D-075. No hardware action, implementation/config/ledger edit, supply
measurement, approval, or phase pass. The current date is Wednesday 23 September;
PLAN section3's original P0 gate remains subject to its human acceptance.

**The 40MHz,14-bit,814-cycle candidate is conditionally supportable. Add LFTRIG=1.
Constrain this increment to the existing nominal high-supply profile and verify
its software guards; physical VDDA/VREF/divider accuracy remains unproved.**

## Sources and retrieval limits

- Current official [DS13086 stable alias](https://www.st.com/resource/en/datasheet/dm00639779.pdf)
  and [STM32U585AI alias](https://www.st.com/resource/en/datasheet/stm32u585ai.pdf)
  served DS13086 Rev10, July2024,350pages through web extraction. History p349
  dates revision10 to5July2024. The history p348 records the calibration-time
  update under revision8,4August2023, not revision10.
- Current datasheet **original PDF bytes were not obtained**: main/ST-China
  direct requests timed out; Japan download returned404; a guessed Rev10 archive
  redirected to HTML and was rejected. Receipts preserve each failure. The
  [official Japan index](https://www.stmcu.jp/design/document/datasheet/86117/)
  points current English to the stable ST alias; its local archive stops atRev9.
  No older archive was substituted. `ds_*_web.txt` preserves extracted lines;
  their hashes identify these captures, never an original PDF.
- Official [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf),
  cached `build/cache/RM0456_Rev6_52152e41.pdf`,3653pages, SHA256
  `52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`.
  Relevant page text plus rendered/visually checked pp654/1297 is retained.
- Previously collected installed ST LL header evidence is read-only input:
  `P2_adc_native_raw/installed_source_01.json`, source header hash
  `c72e076314ab1e3ec41928bfb04c942e321065a47ca778358f0503984f0f441f`.
  Its calibration timing comments are distinguished below from the datasheet.
- This agent did not retrieve or inspect errata or perform the parallel
  ownership/NVIC audit. Their conclusions must be incorporated separately.

## Published electrical/timing values

DS13086 Rev10 Tables33/104/105/107, pp160-162/243-248:

| Item | Published value/condition |
|---|---|
| VDD |1.71..3.6V with HSLV off |
| HCLK maximum, voltage ranges1/2/3/4 |160/110/55/25MHz;160MHz requires range1 |
| ADC1 VDDA |1.62..3.6V |
| VREF+ |2V..VDDA when VDDA>=2V; otherwise VDDA |
| VREF-/input |VSSA; single-ended input0..VREF+ |
| ADC clock |5..55MHz;45..55% duty; degraded DNL below10MHz |
| ADC regulator startup |17us maximum |
| Ordinary offset+linearity/offset-only calibration |31849/885 ADC cycles |
| ADC enable stabilization |3ADC cycles plus1conversion |
| Sampling/conversion |5..814cycles; total sampling+resolution+3cycles |
| Analog-switch booster startup |50us maximum, if used |

Table105 is specified by design, not production-tested. At40MHz, derived values:
ordinary calibration796.225us; offset22.125us; acquisition20.35us;
14-bit conversion20.775us. Table107's non-X total-error/gain maxima require
extended calibration; ordinary mode cannot inherit those guarantees. Table105's
14-bit leakage-related source-resistance limit is1kohm at130C. Table106 excludes
external capacitors. Long sampling does not establish divider accuracy.

## Supply/boost guard and reference constraints

RM10.4.4 p406 requires VDDA presence before analog isolation is removed via ASV.
ASV is a software selection, not a voltage measurement. RM15.3.2 Table132 p654
specifies shared SYSCFG_CFGR1 bit8BOOSTEN and bit9ANASWVDD:

| Supply case in RM table | BOOSTEN | ANASWVDD |
|---|---:|---:|
| VDDA>2.4V |0|0|
| VDDA<2.4V, VDD>2.4V |0|1|
| VDDA<2.4V, VDD<2.4V |1|0|

The DS footnotes simplify the low-VDDA case to requiring booster operation;
the RM adds the VDD-fed alternative. Do not silently claim low-supply branches
are reconciled. They are outside the recommended narrow high-supply increment;
do not select operation exactly on the2.4V boundary either.

**No frequency-dependent ADC_CR BOOST field exists in this ADC1 register map.**
RM33.6.3 pp1344-1345 marks bits15:6 reserved. The BOOST label in the block diagram
is not permission to set another STM32 family's control bit at40MHz.

Recommended software contract: require the installed160MHz HCLK configuration,
settled voltage range1, existing ASV=1, and shared BOOSTEN=ANASWVDD=0; preserve
these shared controls and reject an incompatible state. This is conditional on
the existing nominal3.3V high-supply design. Do not pretend those register checks
prove actual VDDA>2.4V, VREF voltage, reference stability, or decoupling.

The proposed100k/22k divider has calculated Thevenin resistance18.033kohm and,
with its proposed100nF, an ideal1.803ms time constant. Its capacitor changes the
dynamic source model but does not remove DC leakage error. Neither configuration
nor ordinary internal calibration calibrates VREF, resistor tolerance, external
settling, noise, or absolute battery voltage. Preserve the existing physical
B5 comparison within0.05V as pending; do not change wiring under this audit.

## Minimum sequence and LFTRIG correction

RM33.4.6/8 pp1276-1278: exit DEEPPWD, enable ADVREGEN, observe LDORDY before
calibration/enable. Calibration requires ADEN=0 and CAPTURE_COEF=LATCH_COEF=0;
set ADCALLIN for ordinary linearity+offset, start ADCAL, wait for its completion.
No conversion may overlap calibration. Ordinary calibration is distinct from
RMp1280's extended coefficient sequence. Loss of analog power/deep power-down
loses calibration; RMp1277 recommends new offset calibration after a long disabled
interval, temperature change, or >10% reference change.

Installed LL lines1956-1960/7920-7926 require4ADC cycles between calibration
completion and ADEN. At40MHz this is0.1us. Its520/131072-cycle offset/linearity
comments differ from the newer datasheet's885/31849; do not describe either
comment as a measured bound. A5ms timeout covers both quoted linearity durations
at the constrained clock, but success still requires ADCAL=0.

RM33.4.9 p1281 requires clearing stale ADRDY, issuing ADEN, and observing fresh
ADRDY. Its stabilization requirement is fulfilled by that acknowledgement;
a nominal delay alone is not success. Retain barriers needed for calibration
clock-domain accesses (RMpp1280-1281) and documented command-write masks.

**RM33.4.26 p1297 explicitly gives Tidle=150us** after ADC enable or completion.
For a longer wait to a single conversion, its input multiplexer must be
reinitialized using LFTRIG; the manual recommends always enabling this mode and
states no timing/performance impact. This applies to occasional software-triggered
samples;814sampling cycles are not an exemption. Set ADC_CFGR2 bit27 while
ADSTART=0 (p1351). Thus the earlier candidate CFGR2=0 must become
`0x08000000` for otherwise-zero controls, preserving reserved bits.

## Candidate deadlines: engineering selections, not hardware maxima

The root's proposed values are supportable fail-closed development policies:

| Stage | Candidate | Basis/acceptance |
|---|---:|---|
| Regulator |100us |Margin beyond17us; require LDORDY |
| Ordinary calibration |5000us |Margin beyond both source timings; require ADCAL0 |
| Calibration-to-enable spacing |2us |Minimum spacing, not a success timeout |
| ADC enable |100us |Margin beyond a conservative20.85us stabilization calculation; require freshADRDY |
| One sample, whole acceptance window |100us plus4096poll ceiling |20.775us nominal conversion plus margin; fresh complete result and all mode/error checks before deadline |
| Stop+disable fault cleanup, total |100us plus finite poll ceiling |Failure deadline selected by software; inspected sources do not guarantee stop/disable completion within100us |

For the2us gap, take the time anchor **after** observing ADCAL0. With a verified
clock quantum<=1us, a reported2us interval guarantees sufficient real spacing
for0.1us. A quantized1us delta alone is insufficient evidence of a nonzero
minimum interval. Otherwise use a separately verified delay/cycle mechanism.

Each stage also needs a finite count guard for a stalled clock; each poll must
have finite work.4096polls may expire before100us and legitimately fail closed;
it does not guarantee100us of waiting. Calibration needs its own count policy
large enough for normal setup, not an assumed reuse of the short-sample count.
No source-derived CPU/WCET guarantee follows. Reject late data before publication.
On a failed stop or disable, retain fault/ownership and report quiescent=false;
never call a deadline expiry proof that hardware stopped. No automatic retry or
global reset follows. The reset-only recovery policy remains a separate choice.

## Completion and next action

The named limits/sequence/LFTRIG source checks are complete at the evidence level
above; original datasheet bytes and their visual table/hash verification were
unavailable. `P2_adc_limits_raw/manifest.json` inventories retained evidence.
Next: combine the independent errata/ownership findings, adopt the narrow contract
and constants, then implement/test/compile the actual inert native driver.
Hardware supplies, divider accuracy, runtime fault timing, and whole-tick WCET
remain separate acceptance work. No human question is needed for these delegated
software selections. Only this report and its new raw directory were changed.
