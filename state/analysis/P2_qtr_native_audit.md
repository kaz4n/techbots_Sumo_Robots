# P2 B2 native QTR GPIO boundary audit

2026-09-23 Asia/Dubai. Source audit only; no GPIO/MCU operation, board access,
upload, implementation, shared ledger or config edit. D051/D075 permit the
software work; physical acceptance and human gates remain absent. The local
clock was read as2026-09-23, PLAN3's Wednesday, before the28September scope cut.
Read AGENTS, CODEX_EXECUTION, latest PROGRESS, D051/D075, relevant FACTS/HARDWARE,
P2 B2 and the prior QTR/IRQ/opponent/motor evidence. Only this report and
`P2_qtr_native_raw/source/` are added by this audit.

## Result and minimal boundary

The installed-shaped headers support a concrete, bounded native driver with
checked GPIO calls plus direct read-only mode/clock/lock/EXTI predicates. No new
transport abstraction, interrupt registration or unavailable GPIO direction
syscall is necessary. Prefer one boot-lifetime acquisition owner, serialized
setup and fixed four-pad operations. Check the complete bank before the first
write, use native `GPIO_OUTPUT_HIGH` for charging, native `GPIO_INPUT` for
release/cleanup, and preserve every status and uncertain timing interval.

The proposed guards establish consistency of observable register state. They
do **not** prove software exclusivity, debugger absence or physical impedance.
Require an explicit caller grant of exclusive pad ownership and final-image
exclusion of competing callers in addition to the guards. Under that grant,
begin can deliberately neutralize PB3/PB4's AF0 debug-capable mode; AF0 alone
is not evidence of an inactive debugger or of a completed handoff. Reject
other alternate/output, locked and interrupt-owned states. Without the grant,
perform no write. A test-fixture grant is not evidence of actual pad handoff.

The guard/admission/cleanup policies below are recommendations to freeze in the
coordinator's contract, not already adopted behavior or physical facts.

## Source identity and reproducibility

`P2_qtr_native_raw/source/manifest.json` records this audit's local verification
of the four reused saved CMSIS/LL files against their original acquisition
manifest, plus two pinned primary-source downloads. No current board-package
refresh is implied. The completed driver still needs the actual target build
and final-image source/import verification.

- Installed core identity and GPIOA/B exports are reused from
  `P0_qtr_bare_contract_audit_20260923.md:43-118` and
  `P2_opp_gpio_audit_raw.json`. Loader SHA-256 remains the recorded
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
  `source/reused_gpio_elf.json` extracts the original offline tool commands,
  statuses and disassembly, with the original receipt hash. These are cached
  ELF observations, not live MCU reads.
- `source/gpio.h` is the full primary header at the already audited Zephyr
  revision1743741760ee5d2d58da50d504855d43f9f8e826. Its SHA-256 exactly matches
  the previously captured installed header:
  `aab7888876f29b6ad98217d8099aac677f5238249b95599511038cc35d982316`.
- `source/gpioport_mgr.c` is pinned to that revision, SHA-256
  `9807c1b0501f4fe7a41ead122a205417840be38a1e2d8da34aeb05c9606331b1`.
  Its selected U5 operations agree with the saved loader disassembly
  at0x080178bc..0x080179c4. This is not a claim that the upstream source file
  itself was present on the board.
- Reused installed headers live in `P2_adc_ownership_raw/headers/`:
  `stm32u585xx.h`, `stm32u5xx_ll_gpio.h`, `stm32u5xx_ll_exti.h`, `core_cm33.h`.
  Their original full installed paths and verified hashes are in the new
  manifest. They are deliberately not recopied.

Primary links: [GPIO ABI](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/include/zephyr/drivers/gpio.h),
[GPIO pad manager](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/soc/st/stm32/common/gpioport_mgr.c),
[native GPIO driver](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/gpio/gpio_stm32.c).
Line numbers below refer to saved local source files, retaining original file
lines, rather than the browser's whitespace-normalized rendering.

## Exact metadata and register layout

The existing proposal is unchanged. `P0_qtr_bare_contract_audit_20260923.md:84-101`
identifies the installed DT source lines and object bindings:

| Corner | Arduino index | Pad | Device | Register bit | EXTI / IRQn |
|---|---:|---|---|---:|---|
| FL | D2 /2 | PB3 | gpioB ordinal90 | 1<<3 | EXTI3 /14 |
| FR | D4 /4 | PA12 | gpioA ordinal89 | 1<<12 | EXTI12 /23 |
| RL | D7 /7 | PB2 | gpioB ordinal90 | 1<<2 | EXTI2 /13 |
| RR | D8 /8 | PB4 | gpioB ordinal90 | 1<<4 | EXTI4 /15 |

All DT flags are0. GPIOA/B base addresses are0x42020000/0x42020400;
their nonzero exported objects are0x0801c064/0x0801c040. Their shared native
API has nonzero configure/read/set/clear entries0x08019151/0x080190bd/
0x080190db/0x080190e5. Device readiness uses nonzero export0x08019e6f.
The driver config pin mask is0xffff. See `source/reused_gpio_elf.json` for the
original object/API/config structures and disassembly.

Validate each config index before table access; exact named device/pin/flags,
no duplicates, pin<16, non-null port/config/data/api/state, pin mask coverage,
required API callbacks and readiness for **both** ports. Compare
`DT_REG_ADDR(DT_NODELABEL(gpioa/gpiob))` with `GPIOA_NS/GPIOB_NS` before MMIO.
Do not cast an arbitrary accepted GPIO device to the U5 register binding.
Also exclude overlap with motor/opponent/battery proposals using their actual
DT-resolved pads. The table comes from `wiring_private.h:23-25`, as recorded in
`P2_opp_gpio_audit.md:91-105`; no invented pin translator is needed.

`stm32u585xx.h:585-598` defines GPIO registers in order:
MODER0x00, OTYPER0x04, OSPEEDR0x08, PUPDR0x0c, IDR0x10, ODR0x14,
BSRR0x18, LCKR0x1c, AFR[0/1]0x20/24, BRR0x28, HSLVR0x2c,
SECCFGR0x30. Base/NS symbols are at:1845-1846,2295-2296. Derive masks from
the validated pin, using unsigned shifts. GPIOB's selected bank is0x1c;
GPIOA's is0x1000. Do not accidentally read/write all bank pins.

## Native operation ABI and effects

`source/gpio.h:241-282,810-842,1066-1072,1565-1580,1650-1669` gives the
32-bit port masks/flags,8-bit pin index, driver table and inline operations:

```cpp
int gpio_pin_configure_dt(const gpio_dt_spec*, gpio_flags_t);
int gpio_pin_get_raw(const device*, gpio_pin_t);      // 0,1 or error
int gpio_pin_set_raw(const device*, gpio_pin_t, int); // 0 success or error
```

Raw setter delegates nonzero to `port_set_bits_raw`, zero to
`port_clear_bits_raw`; the inline dispatches are at:1410-1423,1453-1466.
The saved driver `P0_irq_installed_raw_20260923/gpio_stm32.c:197-205,225-258`
reads IDR, sets BSRR and clears BRR. Do not use masked-output or toggle helpers.
The saved installed binary confirms finite paths; no runtime latency guarantee
or status-based detection of electrical faults follows.

Use checked inline/device dispatch. Several named `z_impl_gpio_*` LLEXT entries
are zero; importing those as external direct calls is invalid. The final ELF
must show the actual local wrappers and nonzero retained imports. Generic
get-config is disabled and direction/pending callbacks are NULL, as already
established by F082/F087 and the extracted native API structure.

`GPIO_OUTPUT_HIGH` is supported (:79). The saved native driver:306-314 writes
BSRR before pad configuration; unlike Arduino OUTPUT, this need not first drive
LOW. Retain the charge operation's start/end observations. Success means the
selected output command succeeded; ODR HIGH alone is not physical HIGH. Check
the configured output mode and actual raw input HIGH before claiming charge
readiness. A low/error read is failed acquisition evidence, never a fabricated
discharge sample. No diagnostic pull-up belongs in this production path.

Native flags-to-config chooses neutral input at driver:81-96; output defaults
push-pull at:59-79; omitted speed selects low at:99-113. The pad helper
`source/gpioport_mgr.c:182-219` writes output type, speed, pull, then mode. It
updates AFR only in alternate mode. Thus `GPIO_INPUT` establishes input,
push-pull metadata, low speed and no pulls, while preserving ODR and AFR.
The saved disassembly independently shows stores to offsets4/8/12/0 and AFR
stores only through the alternate branch. An old HIGH latch does not enable
an input pull-up. It also means a neutral-input readback should not require
ODR LOW or AF0. Preserve the per-pad AFR nibble across this owner's lifetime.

Configure is not transactional: the inline GPIO wrapper updates its invert
bitmap before native configure returns (`gpio.h:1044-1052`), and the driver's
pad helper has no status-bearing readback. Preserve failed statuses and treat
the attempted pad as potentially touched. Never equate return0 with observed
final mode; use the direct predicates below.

## Read-only admission and owned-state predicates

All checks are bounded reads. They must precede an affected write and follow
configuration; serialize this owner with all GPIOA/B reconfiguration, including
other pins sharing MODER/PUPDR/OTYPER or the software invert bitmap. Readbacks
cannot prevent a concurrent owner's check-to-use race. This driver must never
reset a GPIO port, disable a peripheral, clear a foreign EXTI flag or invoke
device_init to make its admission pass.

1. Check metadata/readiness first. Then require
   `(RCC_NS->AHB2ENR1 & (RCC_AHB2ENR1_GPIOAEN|RCC_AHB2ENR1_GPIOBEN))`
   equals both bits and the corresponding AHB2RSTR1 reset bits are clear.
   `stm32u585xx.h:1033,1043,16350-16355,16606-16611` supplies the layout/masks.
   No clock enable write is needed or recommended: these are existing boot
   devices. If a required clock is off, reject before GPIO register reads.
2. Require no selected LCKR bits. `LL_GPIO_IsPinLocked` is source-defined at
   `stm32u5xx_ll_gpio.h:755-758`; importantly it reports whether **all** supplied
   bits are set. Call it with each one-bit mask, or use `(LCKR & bank_mask)==0`.
   Passing0x1c and accepting a0 result could miss a single locked PB pad.
3. Initial admission requires an explicit exclusive-pad grant. With that grant,
   accept INPUT/ANALOG as deliberately neutralizable and permit AF0 specifically
   on PB3/PB4 as the scoped debug-pad handoff; reject other alternate/output
   states. The grant, final-image exclusions and mode checks are separate
   prerequisites. No source here proves a live debugger absent or an exact
   reset-pull fingerprint; do not require invented reset values. Startup neutral
   configuration may deliberately clear preexisting pulls under the grant.
   Without the grant, or after ownership is lost, do not neutralize the pins.
4. After neutral setup/release, require INPUT, no pull, push-pull metadata,
   low speed, unlocked, and unchanged AFR nibble. During charge require OUTPUT
   with those same properties and ODR HIGH. `stm32u5xx_ll_gpio.h:318-322,
   387-390,461-465,529-534,607-611,685-689` gives the exact getters.
   Use `LL_GPIO_GetAFPin_0_7` for PB2/3/4 and `GetAFPin_8_15` for PA12.
   AFR is inactive in GPIO mode; an unchanged snapshot detects some unexpected
   reconfiguration without inventing a requirement that it equal zero.
5. For conservative polling-only ownership require EXTI lines2/3/4/12 wholly
   idle, even if currently routed to a different port. With mask0x101c, reject
   any selected bit in IMR1, EMR1, RTSR1, FTSR1, SWIER1, RPR1 or FPR1.
   These fields are in `stm32u585xx.h:491-504`; LL get/active helpers at
   `stm32u5xx_ll_exti.h:373,499,637,772,871,991` show read access.
   Use a direct masked OR predicate, avoiding LL multi-bit all-set semantics.
   Require `NVIC_GetEnableIRQ`, `NVIC_GetPendingIRQ`, `NVIC_GetActive` all0 for
   EXTI2/3/4/12 IRQn13/14/15/23 (`stm32u585xx.h:82-92`; CMSIS
   `core_cm33.h:2377-2387,2415-2425,2466-2476`). Do not clear/disable them.
6. No EXTI routing write is necessary. Record selected source fields and
   reject later changes if the contract adopts this additional consistency
   check. Their four-bit fields use **eight-bit spacing**, not STM32 families'
   common four-bit spacing: EXTICR[0] shifts16/24 for lines2/3, EXTICR[1]
   shift0 for4, EXTICR[3] shift0 for12 (`stm32u585xx.h:7745-7758,
   7761-7767,7821-7827`). Source0 means A and1 means B (LL header:133-134).
   A disabled reset route of A for PB2/3/4 is not an active conflict; do not
   demand a B route or remap it to manufacture ownership. `LL_EXTI_GetEXTISource`
   at:1188-1194 takes encoded LL CONFIG_LINE constants, not a raw line number.

EXTI software callback records can remain after masking, and existing public
pending/direction queries do not expose them. The source-owned register
predicate cannot certify callback-list emptiness. Require no IRQ registration,
analogWrite/tone/Servo, CAN/MCU USB/debug reclaim or arbitrary pinctrl caller
on these pads in the final image. Existing per-channel motor pinctrl avoids
the whole TIM3 group's PB4 claim; see `motor_port_unoq.cpp:278`. It does not
authorize another concurrent whole-group caller. The prior QTR audit:120-160
remains the ownership/exclusion source. Security attribution/access policy is
not reconfigured here; binding to existing NS registers does not authorize
changing TrustZone, privilege or debugger state.

For the granted AF0 handoff, the installed CMSIS header additionally exposes
`DBGMCU` at0xE0044000 (`stm32u585xx.h:2096,2523`) and CR TRACE_IOEN bit4,
TRACE_CLKEN bit5, TRACE_MODE bits6..7 (:6048-6058). Rejecting enabled trace I/O
and unexpected later trace changes provides a read-only configured-trace guard;
it cannot prove no JTAG debugger is attached. Do not clear these fields to make
the guard pass. `CoreDebug_DHCSR_C_DEBUGEN_Msk` exists
(`core_cm33.h:2158-2159,2231`), but debug enabled is not equivalent to PB3/PB4
owned: the already documented SWD pads are PA13/PA14. A debugger-absence claim
requires external handoff evidence, not a guessed interpretation of that bit.

## Neutral setup and bounded cleanup recommendation

Use an internal boot-lifetime claim to reject a second owner; construction must
perform no I/O. After explicit caller grant and whole-bank preflight, claim before the first write and
attempt checked neutral configuration with per-pad status/readback. Do not
release that claim on partial failure for an unrelated second object to reuse.
The contract must decide whether an entirely pre-write failure is retryable;
post-write setup or ownership faults should remain reset-only.

For each operation, track each pad's expected phase and whether configuration
was attempted. A failed configure can leave the old or requested state; cleanup
may accept only explicitly enumerated old/requested owned states that preserve
the other guards. Reject an unrecognized mode/AF/lock/clock/EXTI change instead
of broadening the predicate to any convenient state.

On success, cancellation, timeout, native error or time-policy fault, perform
at most one checked `GPIO_INPUT` attempt per pad that remains safely owned,
then read back neutral mode. Attempt all four eligible pads even after an
earlier native cleanup failure. Record attempted/failed/skipped/not-neutral
masks independently; do not call success just because calls were issued.
If the global ownership predicate fails, prohibit blind cleanup writes and
report ownership loss with explicit skipped cleanup. A detected takeover does
not grant authority to restore someone else's pad. Clock loss also forbids
GPIO writes until a separate reset/recovery policy is satisfied.

Do not clear ODR merely to prove cleanup. Neutral input/no pull is the relevant
electrical configuration; ODR can remain HIGH while MODER is input. A floating
IDR can be either level, so LOW is not a cleanup requirement. Readback establishes
the programmed mode only; external pull networks and actual voltage remain
physical tests. Prefer no destructor cleanup: hidden I/O after owner lifetime
complicates the explicit bounded fault policy.

## Timing, validation and remaining unknowns

Preserve10us charge and1500us timeout. Existing F082/F083 evidence says micros
is integer-us modulo32 and the old diagnostic used an11-tick guard; it does not
prove a new production charge interval. Bracket each sequential release and
observation with actual timestamps, retain last-HIGH/first-LOW uncertainty and
timeout censorship, and bound service gaps/call counts separately. This audit
does not choose those numerical production limits or close SC-B.

Independent controlled-native tests should include every metadata/clock/reset/
single-lock/mode/pull/type/speed/AF/EXTI/NVIC admission rejection without a write,
all16 raw combinations, status failures after every partial stage, neutral
readback mismatch, every owner-loss boundary, second-owner rejection, all-four
eligible cleanup and cleanup-skipped reasons. Confirm native HIGH preload
before output mode and no intentional LOW/pull-up/IRQ/peripheral-init path.
Controlled headers should preserve installed field names, signatures and the
real LL one-bit/multi-bit semantics. Target retention/import/startup verification
must follow; compile-only never calls the driver.

No actual exclusive-pad grant/handoff, live pad ownership, sensor attachment/polarity/discharge,3.3V/5V transient
safety, debugger activity, measured cleanup, service-gap/capture precision or
whole-tick WCET was checked. The existing F091/SC-AJ clock/runtime limits remain.
No app/Robot freshness adapter, integration or physical B2/P2 gate follows.

Next action: freeze the coordinator's explicit setup/timing/uncertainty/cleanup
contract, implement the real native owner and independently test it. Its explicit
fixture grant and compile-only retention must remain distinct from an actual
debugger/peripheral-to-QTR handoff before hardware execution.
