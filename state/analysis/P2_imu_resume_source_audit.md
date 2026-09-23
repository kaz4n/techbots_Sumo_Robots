# P2 resumable IMU source audit

2026-09-23 Asia/Dubai; inspected baseline `2f0981cbe570b3bc6d041072455efe81ebb5bff5`.
Owned output: this note and `P2_imu_resume_raw/source/` only. No implementation,
config, public header, established test, ledger, board, upload or gate change.
The date matches PLAN section 3's Wednesday 23 September row; D051/D075 permit
this P2 software preparation while human and physical acceptance remain pending.

## Conclusion

**The source supports a resumable polling transaction with one guarded protocol
action per advance.** Returning to ordinary CPU work does not itself clear I2C
flags, read RXDR, write TXDR or terminate the transfer. Preserve the existing
exclusive I2C4 owner, enabled peripheral, clock/pad configuration and complete
on-wire transactions across returns. Reobserve time, ownership, errors and
phase-valid flags before each next mutation; a saved flag snapshot cannot authorize
a later write after arbitrary caller work.

This permits implementation and host tests of an advance API. It does not prove
a useful maximum service gap, a measured per-call duration, accepted sample rate,
sensor synchronization, schedulability or the complete tick's <800 us WCET.

## Evidence identity and retrieval

- **R:** ST RM0456 Rev 6, cached complete PDF
  `build/cache/RM0456_Rev6_52152e41.pdf`, SHA-256
  `52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`.
  [Official ST Japan source](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf).
  This turn verified exact PDF and LF-normalized page-text hashes (the checkout's
  extracts use CRLF) and visually inspected Figures
  783, 798 and 801 on pages 2699, 2717 and 2721. A fresh web open of this exact URL
  failed with the reader's inaccessible/internal-error result; no new complete
  RM retrieval or newer-revision equivalence is claimed.
- **L:** Complete installed `stm32u5xx_ll_i2c.h` retained in
  `P2_i2c_native_raw/`, 94,337 bytes, SHA-256
  `aeb2be3a463efbf1ca47b15c4696da323b5a212a47055b10cdd8fd2e8e92ae0a`.
  It matches the exact path/hash/bytes in `installed_02.json` for Arduino
  Zephyr core 1.0.0's UNO Q EDK. This is an offline recheck of the retained
  installed-source receipt, not a new board inventory.
- **E:** The [official ES0499 PDF](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
  reopened successfully this turn as Rev 12, June 2026, 51 pages. Sections
  2.20.1-3, pages 32-33, were inspected; retrieval/section provenance is retained
  without claiming a complete local PDF-byte hash.
- **M:** Manufacturer MPU register manual RM-MPU-6000A-00 Rev 4.0, retained
  complete bytes and pp27-32 in `P2_mpu6050_sample_raw/`, hash
  `ccaa6312b9d86a9da79e26e511101e1150dc85a48255600010a854369cf7c05d`;
  [manufacturer-document mirror](https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf).
  This reuses D081's identified manufacturer document and revision limits; it
  does not upgrade the earlier partial Rev4.2 retrieval to full verification.

`P2_imu_resume_raw/source/receipt.json` records exact local file identities and
locators. Existing raw files remain authoritative and unchanged.

## Supported yield boundaries

| Phase | Source behavior and condition for resumption |
|---|---|
| START/address pending | R65.4.9 pp2712-13 and R65.9.2 pp2743-45: hardware clears START after the address sequence, on arbitration loss, and specified other termination conditions. Software can return while it progresses. Do not update address, address mode, direction or NBYTES while START remains set. START clearing alone is not success; check errors and the expected next phase. |
| Waiting for TXIS / before pointer write | R65.4.7 pp2697,2700 and Fig784: empty TXDR delays transmission by stretching SCL after the acknowledge pulse until software supplies data. R65.4.9 p2714 / R65.9.7 p2750: TXIS requests the next byte and TXDR writing consumes that event. Yielding before the write retains it under unchanged ownership/mode. Use TXIS, not merely TXE: TXE is also the reset/idle empty state and is not an acknowledged transfer request. A NACK does not produce the expected TXIS and can cause automatic STOP. |
| Waiting for TC / before repeated START | R65.4.9 p2714 and R65.9.7 p2750: in RELOAD0/AUTOEND0, completing NBYTES sets TC and stretches SCL low. Setting START or STOP clears TC. A return without either command preserves the transaction; the later guarded START must retain the approved address/read length. No extra STOP is introduced for scheduling. |
| Waiting for RXNE / before or after one RXDR read | R65.4.7 p2699, Fig783: reception uses RXDR plus a shift register. If the next byte reaches its eighth SCL pulse while RXDR is still occupied, hardware stretches SCL before that byte's acknowledge until RXDR is read. It does not overwrite the unread byte. R65.4.9 p2718 / R65.9.7 p2750: reading RXDR consumes exactly the pending byte and clears RXNE; merely reading ISR does not. A fresh RXNE may promptly follow a read if another byte was held in the shifter. Never assume RXNE immediately freezes the bus, or require a sampled RXNE-low interval before the next byte. |
| Last RXNE and AUTOEND STOP | R65.4.9 p2718 and Fig801 p2721: AUTOEND supplies final NACK/STOP. The last byte can remain unread in RXDR after STOP; RXNE and STOPF can coexist. Preserve the existing index-aware final-byte drain, then STOP/idle checks. A CPU return does not turn these into two transactions or allow accepting an early STOP/extra byte. |
| STOPF pending / after STOPCF | R65.9.7-8 pp2749-51: BUSY clears at STOP; STOPF stays set until STOPCF or peripheral disable. Read-only polling is nondestructive. In the existing CR1 mode STOP auto-clear is off. Yield before STOPCF is legal; after clearing it, persist that software phase and perform the required fresh final checks, rather than waiting for a second STOP. A retained byte buffer is not yet a published observation. |

R65.9.1 p2741 requires NOSTRETCH cleared in controller mode. The selected CR1
contains only PE; interrupt, DMA, autonomous, target, SMBus and automatic STOP
flag-clear modes are absent. Ordinary scheduling must not toggle PE, gates,
clocks, filters, pad mode or interrupt ownership. PE0 releases the controller's
lines and resets transfer/status state (R p2743), so it remains terminal cleanup,
not a pause. R pp2698,2741,2746-47 retain the disabled-peripheral constraints on
timing/filter/NOSTRETCH changes. No new register update is needed merely to yield.

Installed L functions confirm the distinction: flag predicates at lines
1724-1804 only read ISR; ReceiveData8 at2397-2399 reads RXDR;
TransmitData8 at2409-2411 writes TXDR; ClearFlag_STOP at1946-1948 writes the
ICR STOPCF command through SET_BIT. HandleTransfer at2305-2320 replaces the
documented CR2 address/count/mode/command fields with a register RMW. It is not
a lock and cannot protect against another producer or make updating START1
fields legal. The current driver's ownership/command safeguards remain required.

E2.20.1 still requires an adequate I2C kernel clock relative to transmitter setup
time (at least10 MHz for the standard100 ns Fast-mode minimum). E2.20.2 permits
spurious controller BERR while the bus continues; D079's conservative terminal
invalidation remains unchanged. E2.20.3 concerns SMBus target timeout, outside
the selected mode. These errata supply no additional polling-gap limit or
evidence that an accepted transfer fits the chosen software deadline.

## Sensor coherence and D081 are separate from flag retention

M pp30-32 establish coherent motion registers within one burst through internal
registers and user-facing shadows copied while the serial interface is idle.
The **14 motion bytes** are the coherent set; INT_STATUS is outside that listed
shadow set. Calling the entire15 bytes an atomic status-plus-motion sample would
exceed the source. M pp27-29 define status read-clear with INT_RD_CLEAR0 but no
precise generation-to-shadow synchronization latency.

CPU interleaving alone does not add STOP, START, sensor reads or a reset. Under
the same documented burst interpretation, a clock-stretched interval remains
part of that transaction; neither an RXNE service delay nor unrelated CPU work
is evidence that the sensor serial interface became idle. Thus resumption
preserves D081's *conditional* status/STOP/idle/15-byte inference, rather than
establishing stronger silicon coherence or freshness facts. The caller must:

1. Complete the first one-byte INT_STATUS transaction, including checked
   STOP-clear/idle and final guards; only status1 authorizes the motion phase.
2. Preserve exactly one second burst from0x3A through0x48, with its included
   second status byte and all existing rejection rules. Do not split motion into
   STOP-separated byte reads, expose a partial payload, or replace it with14 bytes.
3. Keep sole ownership and the D080 sensor profile throughout. Intervening I2C
   register access, reset, mode change, PE toggle or failed/retried second transfer
   is not a supported scheduling technique. A consumed readiness event is not
   reusable after failure.
4. Preserve real observation intervals. A longer idle gap before the second
   START can coalesce additional sensor updates under the existing model; it
   cannot establish their count or physical sample time. A delayed CPU read of
   RXDR is not the time at which the sensor's status register was read on the bus.

The manual does not quantify a special permissible clock-stretch/service gap
for MPU shadow behavior. The inherited D081 inference remains explicitly
conditional; no new synchronization guarantee or service-gap number is selected.

## Smallest useful bounded advance and remaining contract work

The smallest positive progress quota is **one guarded protocol action per call**:
one CR2 launch, one TXDR write, one RXDR read, one STOPCF clear, or one software
phase-finalization transition. If the expected event is absent, make one bounded
guarded observation attempt and return PENDING. Guarding an action can require
several finite register/time reads; one action is not one MMIO access or one
microsecond. This is a legal minimal candidate, not an adopted config value or
proof that such a quota is the fastest useful schedule. A larger fixed quota
needs its own contract and tests; no waiting loop may run until hardware becomes
ready merely because it is hidden inside one named action.

Keep the original admission timestamp, staging bytes, exact phase/index,
ownership-loss latch, error evidence and **one cumulative8192-poll budget** in
the request across all calls. Every active service attempt must spend a bounded
part of that budget, including no-progress attempts, so a frozen micros source
does not permit unlimited active calls. Pure result inspection must not initiate
hidden progress. Preserve one aggregate **elapsed <600 us** acceptance test,
including every gap running other work, with equality failing and a fresh final
test before publication. At most one existing **50 us/8192-poll cleanup** follows
a terminal failure; resuming cannot renew any allowance. Pending is neither
NO_NEW nor NOT_READY after setup, and cannot update sample sequence, source age,
calibration or yaw.

A cooperative API cannot autonomously execute timeout cleanup while its caller
never invokes it. The600 us acceptance guard rejects overdue completion when
serviced; it does not itself guarantee physical line release at600/650 us.
The app must own timely advancement/cancellation and account every service and
cleanup in D092's actual S..C interval. One action each1 ms cannot finish this
compound operation within600 us. The existing198-clock timing envelope already
includes slow corners above600 us before extra software/stretch overhead; those
must fail, not justify a larger allowance.

No new source contradiction blocks the proposed software interface. Before
implementation, freeze begin/advance/report/cancel lifetime and error semantics,
including attempted concurrent legacy operations, cancellation after readiness
consumption, post-STOP finalization and terminal no-I/O behavior. Independent
tests should advance fake hardware during caller gaps, exercise retained RXDR
plus a pending shift byte, immediate next RXNE, TC holds, final RXNE+STOP,
ownership/error changes during every yield, exact deadline/poll exhaustion and
one cleanup. Hardware waveform/stretch behavior, actual per-advance and full-tick
timing, accepted rate, SC-AJ clock qualification, physical sensor/pin acceptance
and human gates remain unproved. Root owns fact IDs and the subsequent decision.
