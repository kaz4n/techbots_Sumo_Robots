# D086 fixed A0/A1 ADC owner

Selected2026-09-23 under D051/D075 for P2 B6 software. Extends D078's existing
native owner; P2_adc_pair_audit.md and its installed/manual evidence supply the
exact register prerequisites. No wiring, optical/electrical result, human gate,
runtime scheduler, button decoder or upload authorization follows.

## Public profile and results

Preserve exact begin()/read() signatures, Sample layout and Status values0..13.
Append NOT_ENABLED=14. Add beginWithButtons() and ButtonSample readButtons().
The first begin call fixes battery-only or fixed A0/A1 for the owner's lifetime.
Every subsequent begin is ALREADY_STARTED with no I/O, even after failure;
there is no upgrade/reset/reclaim path. Construction/destruction have no I/O.
The boot-lifetime ADC1 claim and shared reset-only fault latch cover both methods.

ButtonSample contains status, shutdown, raw uint16, started_us/completed_us uint32,
sequence uint32 and valid. No battery scaling, filtering or logical button level.
Successful A1 conversions alone increment sequence (first1, unsigned wrap0).
Battery conversions never increment it. All invalid results have raw/sequence0
and valid=false, never cached readings. Failed attempted reads retain actual
diagnostic start/completion times as in D078. No-I/O cases retain zero times.
Before begin, readButtons returns NOT_INITIALIZED. After any fault, either read
returns FAULT_LATCHED and saved shutdown without I/O. A healthy battery-only
owner's readButtons returns NOT_ENABLED without I/O or faulting the owner.
Repeated successful reads are distinct fresh conversions, even if raw matches.

## Exact fixed hardware profile

Keep D078 A0/index14/PA4/channel9,14bit,814cycle,LFTRIG and all existing guards.
BUTTON_INPUT_PIN=15 names the unchanged documented A1 proposal; it is not PINMAP
acceptance. Pair admission additionally binds PA5/channel10 and installed DT
child channel_a to ADC1. Validate exact GPIOA metadata/index/flags/supported
mask and no alias with A0 or existing EN/PWM/opponent/QTR proposals. Pair
nonalias checks must reject unknown device bindings, admitting named GPIOA/B/C
only. Battery-only behavior and its existing admission contract remain intact.

Pair guards require PA4 and PA5 independently unlocked, analog/no-pull and
GPIOA clock available, without reconfiguring PA5 or a shared pinctrl group.
Also require DAC1 channel2 EN2/CEN2/TEN2/DMAEN2/WAVE2/DMAUDRIE2 all0 and scoped
MCR.MODE2=0 throughout ownership; other MCR fields are not seized or modified.
Battery-only profile makes no PA5/DAC2 access/requirement. Existing ADC4, IRQ,
clock, supply and mode exclusions remain. Guards cannot prove race-free ownership.

Pair setup adds SMPR2.SMP10=7 and PCSEL0x600; battery retains SMPR2=0/PCSEL0x200.
Initial SQR1 is rank9/L0. Configure once after calibration and ready enable.
Retain every other exact owned/reset mode bit. No scan, DMA, IRQ, generic channel
argument, second owner, recurring calibration or dummy conversion is introduced.

## Runtime switch, completion and faults

Each call starts its existing VBAT_ADC_CONVERSION_US=100 acceptance budget before
ownership guards and rank switching. Validate exact tracked last rank and enabled
idle ADEN1/ADRDY1 with all start/stop/disable/calibration commands0. If needed,
change only SQ1 once (9 or10), verify exact requested whole SQR1, then clear stale
flags once and run D078's one fresh EOC+EOS conversion and single32bit DR read.
Reject raw>16383 before narrowing. Button raw0 and16383 are valid ADC values.
Final mode/flag/ownership/readback and time checks must occur before publication;
elapsed>=100us or count4096 exhausted is failure, including switching/cleanup.
No default repeated command, stale numerical sample or old channel publication.

Leave the selected rank after success. Outside a tracked rank-write transition,
only the owner's exact selected SQR1 is accepted; an external9<->10 change faults.
During verification of an ignored/partial rank write, only exact old/requested
whole SQR1 values are eligible for bounded cleanup. Other bits/values mean lost
ownership and UNCONFIRMED. Partial setup follows equally narrow tracked readback;
do not broaden all configured modes to allow arbitrary partial states.

D078's separate100us/4096 shutdown and command-safe ADSTP/ADDIS ordering remain.
First failure preserves its specific status; later methods share FAULT_LATCHED.
No rank restoration, PCSEL clearing, PA5/DAC2 repair, reset, shared clock changes
or recalibration in cleanup. Unknown ownership means no blind write. Neither a
new instance nor the other API recovers a failed owner.

## Required evidence and probe

Independent tests derive from this contract/public headers/manuals, without
reading implementation CPP. Preserve all existing battery and locked assertions.
Cover additive ABI/status compatibility, both profiles, alternating/repeated
rank traces and channel-specific raw identity, flags/time/sequence wrap, invalid
data, stale/partial completion, failed switch, every new metadata/pad/DAC2 guard,
ownership loss at switching/final readback, common faults, bounded cleanup and
no allocation. Exercise deadline adjacency/wrap/frozen clocks and no repeated
setup/calibration. Sequence wrap may use a test-only private-state fixture seam;
no production reset/testing API. Preserve old battery regressions.

New bench/p2_adc_pair_compile retains actual methods only through never-called
adc_pair_probe::exercise(). Public src/adc_pair_probe.h declares Result containing
init plus battery_first, buttons_first, battery_second, buttons_second; fields
use InitResult/Sample/ButtonSample respectively. Probe=Result(*)(), extern Reader
reader and Probe volatile entry. exercise calls beginWithButtons then those four
reads in order. setup only sets entry=&exercise; loop empty; global initialization
has no native I/O. Verify startup+10000loops in bench and match macro variants,
and all attempted uploads refuse before transport lookup. No new allowlist key.
Target compile-only with actual source/ELF/native imports and fresh separate
same-model read-only review. Existing five inert hashes need exact-map approval.

This is raw acquisition only. SC-A START/BOTH ambiguity, decoder freshness, A1
settling/carryover/accuracy, whole-tick800us, SC-AJ/F091 and physical gates remain.
IMU600+motor150+twoADC100 ceilings total950us before QTR/core; no timing pass.
