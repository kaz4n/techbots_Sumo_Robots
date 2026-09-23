# P2 native I2C4 / MPU6050 acquisition prerequisites

2026-09-23. **The installed LL operations and RM0456 support a finite native
one-byte register-pointer write followed by a repeated-START, 14-byte read.
The shortest next implementation is that specific checked transfer engine,
followed by bounded MPU6050 setup/readback and validity handling.** Stock Wire1
and the synchronous Zephyr transfer cannot supply its deadline guarantee.
No general bus framework, new interface or tunable is proposed here.

Scope: D-051/D-075 software prerequisites while the coordinator completes B5.
Read F-084/F-085, P0_imu_installed_contract_20260923.md, P0_G6.md, applicable
HARDWARE/PLAN/P2 sections, and P2_adc_ownership.md. Current date is Wednesday
23 September; the plan's hardware gates remain pending. This task read Linux
files, inspected the packaged ELF offline and inspected primary documents.
No MCU/register/pin/I2C/API execution, upload, reset or hardware measurement.
Only this report and `P2_i2c_native_raw/` were written; no live jobs remain.

## Exact installed binding and ownership

Let C be `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`,
I be `C/variants/arduino_uno_q_stm32u585xx/llext-edk/include` and H be
`I/modules/hal/stm32/stm32cube/stm32u5xx`. `installed_01..03.json` under the new
raw directory preserve full paths, hashes, numbered excerpts, GDB queries and
exit codes. They corroborate the earlier F-084 source/ELF audit.

| Item | Verified installed value |
|---|---|
| Arduino name | Wire1 = I2C4; ordinary Wire is I2C2. |
| Device | `DT_NODELABEL(i2c4)`, ordinal40, exported at0x0801c2a4; base0x40008400; deferred flag1; init0x0800d8e5; no deinit. |
| Pins | PD12 SCL and PD13 SDA, AF4. Default pinmux1924/1956, pincfg576 each. Decoded actual state: alternate function, open-drain, internal pull-up, low GPIO speed. Sleep state's PF14/PF15 are not an alternative Qwiic route to use. |
| Peripheral gate | DT clock0 `{bus=160,div=0,enr=2}`: RCC_APB1ENR2/I2C4EN bit1. One clock spec only; no explicit kernel selector spec. |
| Kernel source | Reset `RCC->CCIPR1 & RCC_CCIPR1_I2C4SEL == 0` selects PCLK1. Existing source clock lineage is HCLK160MHz/APB1 divider1, hence nominal160MHz. Check the live selector and divider rather than assuming the DT bitrate establishes the kernel. |
| IRQs | `I2C4_ER_IRQn=100`, `I2C4_EV_IRQn=101`, priority0. DT lines6339/6346 and CMSIS lines169/170 agree. Both packaged ISR-table entries carry device40. |
| Stock startup | Init enables both NVIC IRQs at0x0801929a–0x080192bc, configures its semaphores, pinctrl and clock, then calls runtime configure. That configure takes K_FOREVER. Do not call it from the native bounded owner. |
| Stock concurrency | Target support is compiled; private data includes target/target2 callbacks, controller_active and transfer buffer/length. The packaged zero initializer is not a live ownership test. |

The installed pinctrl decoder is `I/zephyr/soc/st/stm32/common/pinctrl_soc.h`,
SHA256 `f49dfad5a5ca5c68cbf1d631bb87ff763f04cf238d9c0bfb889f0e892ccaf595`;
bits6/8:7/10:9 encode output type/speed/pull. DT:5914/5920 and6132/6138
independently specify pull-up/open-drain; :5897/6115 specify low speed.
These internal pull-ups do not establish external rail, resistance or rise time.

Minimal admission is serialized setup with the public device-state predicate
`state && !state->initialized && state->init_res == 0`, plus IRQ100/101
enable/pending/active all0 using the verified finite CMSIS helpers from
P2_adc_ownership.md. The state bit is not a mutex against initialization in
progress. Exclude Wire1.begin/end/setClock/transfers, native I2C configure/read/
write/target registration, dynamic IRQ replacement, DMA/raw register writers,
other PD12/PD13 owners and clock/power reconfiguration for the entire lifetime.
Do not disable another owner's IRQ or erase its status to force admission.

After exclusive admission, enable only the authorized I2C4 gate using the
finite LL APB1-group2 enable/readback or the previously verified RCC dispatch.
Check compatible pristine state before configuration: CR1=0, CR2=0, OAR1/2=0,
TIMINGR=0, TIMEOUTR=0, AUTOCR=0 and ISR reset-compatible (TXE1, no fault/event).
Do not read disabled-clock peripheral state as proof of reset. Configure only
the two authorized pins and require their clocks/readback/unlocked state;
never apply the sleep state or borrow GPIO clock pulses for bus recovery.

## Timing is a remaining concrete contract choice

`LL_RCC_GetI2CClockSource(LL_RCC_I2C4_CLKSOURCE)` can be compared with
`LL_RCC_I2C4_CLKSOURCE_PCLK1`. CMSIS identifies I2C4SEL at CCIPR1 bits15:14,
not CCIPR2. Keep the inherited clock mode unchanged. Source-derived160MHz is
nominal metadata, subject to the existing global MSI auto-calibration issue;
no oscillator accuracy or lock is proved here.

DT400000 is a requested bitrate. The actual stock fallback in pinned
`i2c_stm32_v2.c:1299–1377` searches prescalers using integer nanoseconds and
Fast-mode minimum durations. With clock160000000 it derives PRESC4, SCLDEL15,
SDADEL12, SCLH18, SCLL40: **TIMINGR0x40fc1228**. This is a derivation, not a
new selected value or a register measurement. Its programmed high+low counter
duration is1.875us before synchronizer/filter/pad delays. Copying it does not
prove an SCL period of at least2.5us or the MPU6050 maximum400kHz.

RM65.4.3/5/9, pp2693–2698/2710–2712, require a documented TIMINGR and
ANFOFF/DNF calculation that covers kernel-clock tolerance, SCL high/low,
START/STOP/bus-free timing and SDA setup/hold across the chosen rise/fall and
filter ranges. Change these controls only with PE0. Use a constant result
derived offline for the narrow mode; no timing search in the control tick.
Before adoption, select and justify that value and finite transfer/cleanup
deadlines/count limits in the contract/config. This audit selects none.

## Finite register mechanism for the narrow burst

The actual I2C_TypeDef layout is CR1/CR2/OAR1/OAR2/TIMINGR/TIMEOUTR/ISR/ICR/
PECR/RXDR/TXDR/AUTOCR at offsets0x00/04/08/0c/10/14/18/1c/20/24/28/2c.
Retained `stm32u5xx_ll_i2c.h` is the complete installed header. Its operations
below are straight-line register accesses, not the stock semaphore transfer.

1. **Prepare once while disabled.** Keep own addresses disabled, no target,
   SMBus, PEC, autonomous trigger, wake, DMA or interrupt mode. Configure the
   approved filters/TIMINGR, TIMEOUTR0 and AUTOCR0; preserve reserved bits.
   Enable PE using LL_I2C_Enable (:500). Confirm exact expected CR1/filter,
   address, timing, timeout and autonomous controls before each request.
2. **Admit a request.** Use one fixed private14-byte staging buffer, one request
   identity and one absolute transfer deadline plus finite polling budget.
   Require no old active request, no sticky fault, no event/error/START/STOP,
   BUSY0 and both SCL/SDA GPIO IDR bits high. RM p2712 explicitly requires bus
   idle checking; BUSY0 alone after PE0 is inadequate. Keep output invalid.
3. **Write register pointer.** For an approved7-bit address, pass `address<<1`
   to LL_I2C_HandleTransfer (:2305), 7-bit mode, NBYTES1,
   LL_I2C_MODE_SOFTEND, LL_I2C_GENERATE_START_WRITE. Wait boundedly for TXIS
   (not merely TXE); write0x3b exactly once with LL_I2C_TransmitData8 (:2409).
   Do not change address/direction/NBYTES while START is still set.
4. **Repeated START.** After the pointer's TC, with no error and START0, call
   HandleTransfer with the same shifted address, NBYTES14, RELOAD0,
   LL_I2C_MODE_AUTOEND and LL_I2C_GENERATE_START_READ. TC means the first
   NBYTES completed; setting START clears it and retains the transaction.
   A STOP-separated pointer write is not this mechanism.
5. **Receive exactly14 bytes.** Each RXNE permits one LL_I2C_ReceiveData8
   (:2397), which reads RXDR and clears RXNE. Maintain an index bounded by14.
   Check errors/deadline before accepting progress. AUTOEND generates the last
   NACK and STOP; software must not emulate target-mode NACK control. RXNE and
   STOPF may coexist at the last byte: drain the expected final byte, then
   evaluate completion, rather than declaring an early STOP unconditionally.
6. **Commit only complete success.** Require exactly14 received bytes, fresh
   STOPF, no error, no remaining RXNE, START/STOP inactive, BUSY0, unchanged
   ownership/configuration and a final deadline check. Clear owned STOPF using
   its W1C helper and confirm completion before publishing the staging buffer.
   No caller buffer or validity flag is updated on a partial or late transfer.

RM65.4.9 pp2712–2718 and65.9.2/7 pp2743–2750 support this sequence. TXIS is
cleared by TXDR write, RXNE by RXDR read, TC by START/STOP; STOPF/NACKF/error
flags are W1C through ICR. HandleTransfer clears/replaces its documented CR2
fields and preserves unrelated bits; it is not safe if another producer can
set command bits concurrently. Use a fixed mode/exclusivity guard, not blind RMW.

Each service call must have a fixed action/poll quota and every wait must share
the finite request budget. There are exactly one TXDR write and14 RXDR reads,
but arbitrary waiting for those actions is still unbounded unless explicitly
capped. A design doing only one byte per1ms tick cannot provide1kHz acquisition;
the chosen servicing cadence and total tick budget need explicit tests. Ideal
153 SCL clocks at400kHz take382.5us, excluding all START/STOP, stretching,
software and fault costs. It is a lower bound, never WCET.

## Error and cleanup semantics

| Observed condition | Supported narrow response |
|---|---|
| NACKF | Invalidate immediately. Hardware sends STOP after controller TX NACK; wait boundedly for STOPF and bus release, then clear NACKCF/STOPCF. Never equate the NACK flag alone with completed cleanup. |
| ARLO | Invalidate; hardware releases SDA/SCL and leaves controller mode. Do not issue STOP against the winning controller. Clear ARLOCF only as owned status; boundedly observe idle or leave faulted. |
| BERR | Record it; it does not itself stop a controller transfer. The contract may conservatively invalidate and perform bounded abort, or implement the documented spurious-BERR continuation rule with full byte/completion checks. Never let BERR alone masquerade as completion. |
| OVR, unexpected ADDR/TCR/PECERR/TIMEOUT/ALERT | Reject as error or mode inconsistency. OVR is documented for target NOSTRETCH mode, which this candidate excludes. Clear only owned W1C flags after recording them; do not publish partial data. |
| Deadline/count exhaustion while still exclusive controller | Invalidate permanently for that request. Request STOP once only in an established active controller phase, with START0, BUSY1 and no ARLO/ownership loss; its completion is bounded separately and never assumed. A START still pending is not evidence that the bus is owned. |
| STOP cannot complete / SDA or SCL stays low | Under retained exclusive ownership, clearing PE releases this peripheral's lines and resets its internal transfer/status state. Confirm PE0; remain faulted. This does not prove the external bus or sensor released the lines. No retries, remux pulses, RCC reset or recovery loop are required for the first implementation. |
| Ownership loss | Latch invalid and avoid blind register/pad cleanup writes to a resource no longer established as owned. |

LL helpers are ClearFlag_NACK/STOP/BERR/ARLO/OVR (ICR stores, :1935–1994),
GenerateStopCondition (:2173) and Disable (:514). RM pp2698/2743 requires
PE remain0 for at least three APB cycles before reenable. A reset-only terminal
fault that never reenables avoids inventing a successful recovery interval.
BUSY becomes0 on PE0 regardless of the external lines; log cleanup outcome
separately from bus health. Successful stop and failed stop require separate tests.
There is no separate controller-ownership/MSL flag in this ISR layout. The
software phase plus single-controller bus premise and ARLO checks must justify
an abort STOP; if that premise is unavailable, do not infer ownership from
BUSY alone. Do not replay a pending START through a naive CR2 RMW.

## Current errata and remaining acceptance limits

Official [ES0499 Rev12, June2026](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
was reopened successfully (51pages). Sections2.20.1–3, pp32–33: standards-
compliant Fast-mode100ns transmitter setup requires at least10MHz kernel clock;
nominal160MHz satisfies that conditional inequality. Controller BERR can be
spurious without stopping the transfer; the workaround clears it and permits
normal handling to continue. SMBus target-timeout behavior is outside the
proposed mode. Section2.4.1, p17 concerns revisionX GPIO excess consumption:
filter changes and Stop entry have ordering constraints. Keep low-power entry
out of scope and record any chosen filter policy. The inherited MSI lock/
frequency issue remains global. No physical silicon revision was read.
`errata_receipt.json` retains source/page/line provenance, not a local PDF hash.

F-056/F-057 and P0_G6 establish a user-reported MPU6050 and manufacturer burst
layout0x3b..0x48, including accelX/Y and gyroZ. They do not establish address
0x68 versus0x69, breakout/pull-ups, successful WHO_AM_I, configured gyro range,
sample rate, axis signs or freshness. A complete bus transfer is not a new
sample-generation proof: INT_STATUS0x3a bit0 clears on read and is not a counter.
The next contract must specify bounded reset/configuration/readback, a range
at least1000dps, data-ready/age semantics and integration of only accepted
samples. Do not add yaw integration to this transport audit or adopt unchanged
Adafruit getEvent error handling.

## Sources and shortest next action

Installed LL I2C is94,337 bytes, SHA256
`aeb2be3a463efbf1ca47b15c4696da323b5a212a47055b10cdd8fd2e8e92ae0a`;
the complete local header matches the installed byte hash in `installed_02.json`.
The existing common CMSIS/LL GPIO/RCC/bus headers and
their identities remain available in `P2_adc_ownership_raw/headers/`.
New pinned [i2c_stm32.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32.c)
and [i2c_stm32_v2.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32_v2.c)
copies exactly match F-084 hashes `eb85fcfcff500e12b33de4f961ea0bff81a53d6be86fd918e2236017dad9f725`
and `3d6764569c403e6a40ac3a82d0d0970432b20649bc445aea87a6bfe735efcb2b`.
Official [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf)
is reused from build/cache, SHA256
`52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`;
selected page text/hashes are retained in the new raw directory.

After B5 review, freeze one narrow B3 contract: owned I2C4 polling transfer,
documented timing/filter choice, absolute deadline plus count budget, explicit
BERR policy and terminal-fault cleanup. Implement/test that real source with
fake registers and retain it in an inert target compile. Then add bounded
MPU6050 setup/readback and sample-validity handling using the same mechanism.
No additional driver framework or source-discovery phase is needed for the
transfer flags. Timing calculation and sensor freshness/setup policy are the
remaining software choices; physical wiring/waveform/fault/WCET acceptance and
global clock qualification remain separate, unproved requirements.
