# STM32U585 MotorGate update/preload source audit

2026-09-23, P2 software preparation under D-051/D-075. **The proposed natural
post-write UIF algorithm has primary-source support, conditional on the guards
below.** No MCU registers, pins, upload, reset or motor operation were performed.
No physical acceptance, silicon revision identification or timing result follows.

## Retrieved sources and identities

The [official ST Japan RM0456 index](https://www.stmcu.jp/design/document/reference_manual/84660/)
supplies the [English RM0456 Rev 6 PDF](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf).
The index identifies STMicroelectronics copyright and its download metadata
explicitly names that URL. The downloaded PDF identifies January 2025, Rev 6,
3653 pages, and explicitly includes STM32U585. Its 73,439,635 bytes hash to
`52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`.
It is retained locally in ignored `build/cache/RM0456_Rev6_52152e41.pdf`, not
added as a large tracked artifact. This resolves the earlier retrieval gap;
byte equality with the main-site differently sized PDF is not asserted.

`P2_motor_native_raw/update_sources.json` records exact pages, extracted-page
hashes, a short verbatim CCR excerpt and the download/hash evidence. Pages 2198
and 2217 were also rendered and visually checked against the extracted text.

The [versioned ST U5 LL timer header](https://github.com/STMicroelectronics/stm32u5xx-hal-driver/blob/0e5fefb8dc2d6afa60816ebbf8b1672cfec4595b/Inc/stm32u5xx_ll_tim.h#L5222)
was downloaded from that exact commit and has SHA-256
`02157f3fbfcce84f5223d6d7486da02e4eb4e22949ff170ade76ac25115c3178`.
This upstream file is not claimed to be the installed header. Its clear function
matches the installed expression and line numbers already captured in
`P2_next_driver_audit.md` (installed hash `1da2403c...f0b46`).

The current [ES0499 official errata](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
and its [official regional URL](https://www.st.com.cn/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
were retrieved by the web PDF extractor: Rev 12, June 2026, 51 pages. Current
PDF bytes were not downloaded locally, so the receipt deliberately has no PDF
hash. An attempted Japan Rev12 filename returned an HTML home page; it was
rejected, despite HTTP 200. Retrieval failures are not hardware evidence.

## Exact manual locations establishing the chain

Page numbers below are printed and one-based PDF numbers; they agree.

| Claim | TIM1 | TIM3/TIM4 |
|---|---|---|
| Upcount overflow generates UEV; repetition qualifies TIM1 | 54.3.4, 2103-2104 | 55.4.4, 2246 |
| UDIS=0 permits preload transfer; UDIS=1 suppresses transfer | 54.6.1, 2186 | 55.5.1, 2317 |
| PWM preload/shadow transfer occurs on update | 54.3.13, 2128 | 55.4.11, 2268 |
| UIF is set when registers update; overflow needs UDIS=0 | 54.6.5, 2198 | 55.5.5, 2326 |
| UIF is a read/clear-by-zero status bit | 54.6.5, 2195 | 55.5.5, 2324 |
| Owned CCR preload becomes active on update | CCR4: 54.6.19, 2217 | CCR3: 55.5.17, 2341; CCR4: 55.5.18, 2342 |

URS changes request qualification, not the existence of every transfer: software
UG can transfer without UIF when URS=1. The proposed URS=0 guard is valid;
natural overflow also sets UIF with URS=1, but accepting that alternative is
unnecessary here. Interrupt enable is separate from the status flag. RCR=0,
continuous edge-aligned upcounting and no alternate update producer make each
accepted fresh UIF an ordinary carrier update. ARR/PSC/CCR readback by itself
does not expose the active shadow value.

## Supported algorithm and conservative clear race

This is a deduction from the cited register semantics and the proposed exclusive
ownership contract, not a separately executed experiment.

1. Keep acknowledged EN LOW. Require all four successful writes of the current
   transaction, expected immutable periods and pulse readbacks, and the complete
   readiness/mode/ownership guards. Complete all writes before any stale clear.
2. Issue one vendor UIF clear on each of TIM1, TIM3 and TIM4. The installed LL
   operation is `WRITE_REG(TIMx->SR, ~(TIM_SR_UIF));` rather than a status-register
   read/modify/write. Do not use a pre-clear flag observation as completion.
   Preserve native volatile MMIO ordering; final target code must retain the
   four writes/readbacks before the clears and reads. No clear/set emulation
   using cached software register values qualifies.
3. Poll all three flags with one elapsed deadline and fixed iteration guard.
   Accumulate a separate fresh bit per unique timer. Revalidate relevant state
   and the time bound before success. A second TIM3 channel cannot substitute
   for missing TIM1 or TIM4 completion. Never write a new CCR after its accepted
   update without invalidating the entire transaction receipt.
4. Return success only for all three fresh bits inside the deadline. Otherwise
   fail so MotorGate performs its existing LOW/zero cleanup and fault latch.

No simultaneous hardware set/software clear priority was found in the examined
text, and the algorithm need not assume one. A pre-clear update is discarded.
An update coincident with the clear is already later than all four writes: if
its set survives, its transfer qualifies; if the clear wins, the next update is
required. Either outcome avoids accepting a pre-write transfer. The algorithm
does not require observing an intermediate UIF=0; such a requirement could
reject a legitimate fresh update that occurred immediately after the clear.

This reasoning requires exclusive ownership, not merely DIER=0: another CPU
context or independently triggered DMA can write timer registers or SR without
using that timer's interrupt/DMA request. Register masks cannot prove the absence
of an unregistered writer. No hardware fault immunity or cross-timer atomic
transfer is claimed. The 150 us and 4096-pass proposals remain software rejection
limits, not a guaranteed completion time or measured WCET.

## Guards and errata exclusions for the native contract

In addition to the draft's rate/readiness/channel checks, make these explicit:

- CR1: CEN=1, UDIS=0, URS=0, DIR=0, CMS=0, OPM=0, DITHEN=0,
  ARPE=1. OPM=0 excludes a counter that stops at the first update; DITHEN=0
  preserves ordinary compare/period encoding. TIM1 RCR remains zero.
- No slave/external-clock/trigger owner (SMCR configuration checked), DIER
  interrupt/DMA requests disabled, and no other timer register writer.
- Owned CCMR2 channels are outputs with preload enabled, full OC3M/OC4M
  encoding equal to normal PWM1, and OC3CE/OC4CE=0. Check mode extension bits;
  checking only the low three mode bits could admit another PWM mode.
- CCER has exactly the expected active-high owned outputs and no unowned or
  complementary outputs. TIM1 MOE is required after the writes; do not rely on
  automatic output re-enable. TIM1 BDTR BKE, BK2E, BKBID and BK2BID are zero.
  The implementation's exact masks must use installed U585 definitions.

ES0499 Rev12 table 3, page 4, lists two TIM limitations, both on X/W/U revisions.
Section 2.16.1, page 28, concerns short bidirectional break pulses, including
software breaks not reflected at the pin. Section 2.16.2, page 28, concerns
output-clear with combined/asymmetric PWM. The proposed guards exclude both
conditions. No ordinary TIM UIF/preload-transfer limitation is listed. LPTIM
flag errata on page 29 concern a different peripheral and are not applied to
TIM1/TIM3/TIM4. This is an errata applicability assessment, not a claim that the
unknown board silicon revision or actual waveform has been qualified.

## Contract assessment and remaining work

The fresh-update section of `P2_motor_native_contract.md` is supported with the
explicit OPM/dithering/OCclear/break guards and clear-race explanation above.
No software UG, counter restart or blocking delay is required by this settling
algorithm. Native initialization's existing UG is not a current transaction
receipt; the later stale clear removes it.

The source prerequisite is closed for this narrowly configured algorithm.
Implementation tests must still model distinct preload/active registers,
all-initially-set flags, both clear-race outcomes, asynchronous fresh flags,
one stalled timer, changed modes/ownership, repeated transactions, clock wrap
and freeze, and late completion. Review actual target register access and
ordering. Physical EN, reversal/full-duty waveform, timer rate, driver truth
table, tick WCET, PINMAP and human gates remain open. Clock/pinctrl/init-path
proof is the separate concurrent audit. No shared ledger or source/config file
was edited by this audit.
