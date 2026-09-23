# Fixed ADC1 A0/A1 pair: primary-source prerequisite audit

2026-09-23 Asia/Dubai. This is a source audit and API recommendation, not an
implementation or adopted contract. Only this file and P2_adc_pair_raw/source/
are written. No board/MCU/register operation, upload, config/test/ledger change,
physical evidence or phase gate follows. D051/D075 permit the next software
increment; original physical and runtime integration limits remain.

## Result

The documented ADC1 state machine supports one calibrated owner alternating
single-rank channel9 and channel10 conversions. Preselect both channels and set
both sampling times once during opt-in setup, then change only SQR1.SQ1 while
the enabled ADC is idle. Retain the existing battery-only profile unchanged.
There is no need for a second ADC owner, stock analogRead, multi-rank scan,
interrupt/DMA path, recurring ADC disable/calibration or generic channel router.

This result is source-verified register eligibility. It does not prove electrical
settling, actual timing, exclusive runtime ownership or distinct START/BOTH
voltages. The existing documented ladder still makes START and BOTH identical.

## Source identity and reproduction

P2_adc_pair_raw/source/manifest.json identifies the reviewed power.cpp/power.h
bytes,24 complete manual-page text extracts,6 rendered pages and4 reused installed
headers with excerpts/line numbers. Header bytes were rehashed and checked against
their original installed manifest. The original headers remain in
P2_adc_ownership_raw/headers/; they were not recopied or changed.

The cached official RM0456 Rev6 PDF has SHA256
52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616, checked again.
Printed and one-based PDF page numbers agree. Pages1354/1355/1479 were visually
inspected to confirm register-field positions and cross-page restrictions.
Primary manual: https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf.

The only refreshed official source was the missing full pinned UNO Q overlay:
[ArduinoCore-zephyr79b3f1af overlay](https://raw.githubusercontent.com/arduino/ArduinoCore-zephyr/79b3f1afdad455f55e4a25030953617152c0227c/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay).
Its12523 bytes hash to bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5,
exactly matching the saved installed overlay identity. The HTTP200 receipt and
bytes are preserved as unoq.overlay/unoq.receipt.json. This is not a live package
refresh or deployed-loader verification.

Installed binding excerpts are extracted from the earlier exact receipt
P2_adc_native_raw/installed_source_01.json, whose hash is retained. That cached
generated DT is authoritative for macro spelling; upstream source alone is not
treated as a regenerated installed header.

## Exact A1 and field bindings

| Item | Verified source |
|---|---|
| A0 battery | Arduino14, PA4, ADC1 channel9; unchanged current power driver. |
| A1 buttons | Overlay293/384/422: Arduino15, PA5, ADC1 channel10. Overlay428-432 also maps PA5 to DAC1 channel2. |
| A1 DT child | **channel_a**, not channel_10. Generated DT31176 gives channel_a register address10;31225 gives acquisition16383;31229 gives resolution14. Native check can use DT_REG_ADDR(DT_CHILD(DT_NODELABEL(adc1), channel_a))==10. |
| PA5 pinctrl | Generated DT2244 gives adc1_in10_pa5 pinmux176; existing DAC boot evidence configures PA4/PA5 analog/no-pull. No whole six-pin ADC pinctrl operation is needed. |
| Channel9 sampling | SMPR1.SMP9 bits29:27;111 means814 ADC cycles. RM1353 and installed CMSIS field masks. |
| Channel10 sampling | SMPR2 offset0x18, SMP10 bits2:0;111 means814 cycles. RM1354; stm32u585xx.h3968-3977. |
| Preselection | PCSEL offset0x1c; fixed opt-in mask(1<<9)|(1<<10)=0x600. Battery-only remains0x200. RM1354-1355. |
| Single rank | SQR1 offset0x30, SQ1 bits10:6, L bits3:0=0 for one conversion. SQR1 values9<<6=0x240 and10<<6=0x280; remaining ranks/reserved bits stay at their owned reset values. RM1355-1356. |

The installed LL channel constants are encoded identifiers; LL_ADC_CHANNEL_10
is not merely the integer10. Use that constant with LL_ADC_REG_SetSequencerRanks
and LL_ADC_SetChannelSamplingTime, or use the already verified explicit register
field/position masks consistently. Do not pass10 to an LL function expecting its
encoded channel literal. Existing direct PCSEL bit masks are a different domain.

## Exact legal setup and idle switching

RM33.4.10 p1282,33.4.11 p1283 and SQR1's field notes p1355 require regular
conversions to be stopped before changing the regular sequence. RM33.4.16 p1287
defines ADSTART=JADSTART=0 as idle. With CONT0/EXTEN0 single software conversion,
hardware clears ADSTART at EOS; no extra stop is necessary after an observed
successful completed conversion. The existing injected path is entirely excluded.

The LL rank helper at4610-4720 permits disabled or enabled/no-regular-conversion
states; RM1282's general description names enabled/idle. The recommended path
uses their common supported state: **ADEN1, ADRDY1, ADSTART0, JADSTART0,
ADSTP0, JADSTP0, ADDIS0, ADCAL0**, under unchanged owned modes/clocks/pads/IRQs.
There is no need to rely on broader disabled-state eligibility.

PCSEL's note continues onto RM1355: writes require both ADSTART0 and JADSTART0.
The same requirement applies to SMPR1/2 at1353-1354. RM1283 explains why each
selected channel must be preselected before conversion. The installed LL
preselection helper at5261 ORs a channel bit; selecting10 does not clear9.

Recommended setup extension: after the existing calibrated enable/ADRDY stage,
and before any ADSTART, set SMPR1.SMP9=7, opt-in SMPR2.SMP10=7, PCSEL0x600,
and initial SQ1=9/L0. Validate every final register. Battery-only setup retains
SMPR2=0/PCSEL0x200/SQ1=9 and makes no PA5 operation. Preserve LFTRIG1 and all
other D078 operating choices. Do not configure a two-rank sequence: it changes
DR/EOC/EOS collection semantics and is unnecessary for two separately scheduled
single-channel requests.

For each runtime request, start its total budget before guard/switch work. Verify
the exact currently owned selected rank and idle state; change SQ1 once if needed,
then verify the requested rank and unchanged remaining registers. Clear stale
EOC/EOS/OVR/EOSMP as before, confirm clear, then issue one ADSTART. RM1287 prohibits
starting while stale EOC remains set. Publish only after a new EOC+EOS, completed
ADSTART0, one DR read, raw-range check, W1C/final readback and deadline checks.

Leave the last successfully selected rank in place. Track it in the owner; the
next battery read validates that known state and changes it back to9 if needed.
Do not assume all idle intervals use9 or silently rewrite an unexpected rank.
Both pads' preselection and sampling fields remain fixed for the owner's life.
There is no source requirement to recalibrate after changing only SQ1.

## PA5 and DAC1 channel2 ownership

The new admission must validate PA5's exact named GPIOA binding, input proposal,
clock, analog mode, no pull and unlocked state before an ADC/pad change. Check
PA4 and PA5 independently, or require(GPIOA_NS->LCKR & 0x30)==0.
**Do not** pass both bits to LL_GPIO_IsPinLocked and treat0 as neither
locked: its installed all-selected-bits semantics can miss one locked pad.
No GPIO output/voltage/pull-up reassignment or shared pinctrl takeover is needed.

Existing source evidence shows DAC1 boot initialization only applies analog
PA4/PA5 pinctrl; it does not enable DAC outputs. That is a compatible initial
candidate, not proof that no later caller used the DAC. RM1448 states ENx controls
the analog channel while its digital interface remains enabled even with ENx0.
Thus EN2 alone is insufficient for a conservative exclusion of other producers.

Mirror the existing channel1 guard for channel2 in the opt-in profile:
DAC_CR_EN2(bit16),CEN2(bit30),TEN2(bit17),DMAEN2(bit28),WAVE2(bits23:22) must all
be0. The source additionally supports rejecting DMAUDRIE2(bit29) for this
polling-only ownership contract. Exact fields are in CMSIS5456-5493 and RM1467-
1469. Do not clear these controls or a DAC IRQ to make admission succeed.

RM1479 defines MODE2 bits18:16 in DAC_MCR:0 is reset normal external-pin/buffer
mode;4..7 are sample/hold modes. MODE2 can change only with EN2=CEN2=0. A narrow
boot-compatible A1 contract can require initial MODE2=0 and retain its snapshot,
rejecting a later mode change instead of remuxing the DAC. This extra consistency
guard is an engineering recommendation, not a manual statement that every other
disabled mode necessarily drives PA5. Never require or write all MCR=0 because
the register also contains shared/channel1 fields. Avoid guessed electrical
high-impedance claims from register consistency alone.

Whole-image exclusions still cover stock ADC1 setup/read, DAC/analogWrite users,
ADC4 producers, concurrent register/pad writers and shared clock/power changes.
No register guard proves the absence of an interrupt/thread performing a
check-to-use takeover. A1 opt-in extends these exclusions to PA5/DAC2; default
battery-only operation need not seize or reconfigure PA5/channel2.

## Cleanup must preserve the original safety properties

Keep D078's single reset-only fault latch and boot-lifetime claim for both read
methods. Failure on either channel prevents both from later returning valid
samples. Keep original failure status distinct from DISABLED/UNCONFIRMED cleanup.
No error publishes old raw data under a new channel identity.

An ignored or partial rank write needs a narrow tracked transition: the old and
requested complete SQR1 values are the only eligible owned alternatives while
that write is being checked; unexpected other mode bits remain ownership loss.
Never broaden fixedModes to accept either channel at all times without preserving
the owner's selected-state history. The same staged readback discipline applies
to partial two-channel setup. A register mismatch is not permission to restore
whatever state makes the test pass.

If controls remain owned, preserve the separate bounded shutdown: ADSTP only for
an active regular conversion with ADC enabled/no disable pending; wait until
ADSTART/ADSTP clear; ADDIS only when all start/stop/calibration commands are idle;
acknowledge ADEN0. RM1288-1289 says an aborted partial conversion does not update
DR and software must observe ADSTART0. Use the installed LL command masks at
8007/8023-8027; no CR read-modify-write that reissues other command bits.

Do not restore SQ1, clear PCSEL, rewrite PA5/DAC2, reset the peripheral, disable
shared clocks or recalibrate during fault cleanup. If ownership is uncertain,
do no blind write and return UNCONFIRMED as today. A successful read leaves the
ADC enabled for the next selected channel; calibration/enable runs once only.

## Smallest backward-compatible API recommendation

Retain the exact existing InitResult begin() and Sample read() methods and
existing public structs/enum values. Add two explicitly named methods:

```cpp
InitResult beginWithButtons(); // One setup attempt, fixed A0+A1 profile.
ButtonSample readButtons();    // This same owner, fresh A1 raw data only.
```

Distinct names avoid changing begin's signature or making existing member-function
address expressions ambiguous. Whichever begin method is called first selects
the boot-lifetime profile; every subsequent begin attempt remains ALREADY_STARTED
and cannot upgrade, reset or reacquire it. The explicit A1 method is a software
ownership request, not evidence of physical wiring or PINMAP acceptance.

Recommend a new ButtonSample with Status, Shutdown, raw uint16, started_us,
completed_us, uint32 sequence and valid. It contains no battery-scaled voltage
and no logical ButtonLevel. A typed button result has fixed channel10 meaning;
its status/times/identity must come from that verified conversion. Keep sequence
semantics explicit at contract freeze, including wrap and failed attempts.

Append a NOT_ENABLED status, without renumbering existing statuses, for a
readButtons call after successful battery-only begin. Recommend returning it
invalid with no I/O and without disturbing the healthy battery-only owner;
this unsupported API request is distinct from an actual acquisition fault.
Before any begin, return NOT_INITIALIZED; after a native fault return the shared
FAULT_LATCHED result. No new reset method, global owner or arbitrary channel
argument is needed. Private implementation can share the fixed9/10 transaction.

These are coordinator decisions to freeze under D051/D075 before independent
test authoring. New config must name the unchanged A1/index15 proposal and any
selected guard values; do not scatter tunables or invent decoder thresholds.

## What is still unverified

The existing14-bit/814-cycle/nominal40MHz profile gives the same conditional
20.775us conversion calculation for either selected slow channel. RM1283-1284
requires the source to charge the sampling capacitor adequately; this audit
does not prove resistor tolerance, external RC settling, leakage, reference
accuracy or cross-channel carryover. No mandatory extra dummy conversion was
established by the audited sections; neither adding nor omitting one can be
called a measured accuracy fix. Preserve raw evidence for later electrical tests.

The actual START/BOTH distinction remains impossible in HARDWARE5.6's documented
ladder, and core button freshness/absence/invalid handling remains a separate
integration contract. Two100us ADC calls plus IMU600us and motor settle150us total
950us in selected acceptance ceilings, before other work; this is not an800us
schedule. SC-AJ clock qualification, F091 runtime paths and all human gates remain.

Next action: freeze the fixed-profile API/transition/status/timing contract,
implement the actual shared-owner extension with preserved battery regression,
independent two-channel native fixtures, inert target compilation and fresh review.
