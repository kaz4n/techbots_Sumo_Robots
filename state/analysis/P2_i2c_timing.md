# P2 native I2C4 conditional timing calculation

2026-09-23, Asia/Dubai. Source engineering only; no MCU, GPIO, I2C, upload or
reset operations. This report supplements P2_i2c_native_audit.md and supplies
the timing arithmetic for D079. Only this report and P2_i2c_timing_raw were
written. It does not qualify the physical bus, oscillator or complete tick.

**Candidate: TIMINGR=0x40EB202C, analog filter ON, digital filter zero.**
The calculation supports this candidate under the conditions below. There is
no timing-source blocker to implementing the bounded transport; physical
acceptance and global clock blocker SC-AJ remain open.

| Control | Value | Encoding |
|---|---:|---|
| PRESC | 4 | TIMINGR[31:28] |
| SCLDEL | 14 | TIMINGR[23:20] |
| SDADEL | 11 | TIMINGR[19:16] |
| SCLH | 32 | TIMINGR[15:8] |
| SCLL | 44 | TIMINGR[7:0] |
| Analog filter | enabled | CR1.ANFOFF=0 |
| Digital filter | disabled | CR1.DNF=0 |

TIMINGR[27:24] remain zero. Configure timing and filters only while PE=0.
The analog filter is enabled by reset and supports Run-mode Fast-mode spike
suppression without DNF. Low-power entry and filter changes during operation
are excluded. RM0456 Rev6 pp2695, 2710, 2743; retained primary pages are linked
by hash in the receipt.

## Sources and explicit conditions

- [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf),
  pp2693-2698, 2710-2712, 2743: U585 timing counters, synchronization, filter
  configuration and PE semantics. Cached original PDF SHA-256 is
  `52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`.
- [ST AN4235 Rev2](https://www.st.com/resource/en/application_note/an4235-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf),
  pp10-12: timing calculation method. Its stated scope is F0/F3; only equations
  consistent with the U585 RM are used. Its older-family analog-filter maximum
  is not used. This is a calculation, not a claimed CubeMX run.
- [DS13086 Rev10](https://www.st.com/resource/en/datasheet/stm32u585ri.pdf),
  p299 Table148: actual U585 analog-filter delay is **50..115 ns**, specified
  by design. This replaces the 260 ns maximum appearing in AN4235's family.
- [TDK MPU-6000/MPU-6050 specification Rev3.4](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf),
  p18 section6.7: Fast-mode maximum400 kHz; minimum low1.3 us, high0.6 us,
  data setup100 ns; maximum data/ACK valid900 ns and rise/fall300 ns. These
  manufacturer-domain indexed values were retrieved; direct PDF download was
  unavailable. Its characterization conditions and lower edge limits apply
  independently of this calculation. No original MPU PDF hash is claimed.

The selected engineering envelope is effective I2C kernel158.4..161.6 MHz,
nominal160 MHz +/-1%, including the counter-interval timing needed by the
model. It is **conditional**, not a manufacturer guarantee for this installed
clock. DS13086 Table83's MSI PLL-mode accuracy depends on the LSE crystal;
installed MSI auto-calibration and ES0499 section2.2.27 remain covered by
SC-AJ. Register-ready bits and nominal source metadata do not prove lock or
this frequency envelope. The MCU's applicable rated maximum160 MHz remains
independent: physically admissible operation must satisfy the intersection
of this calculation envelope and the rated clock/power limits. The161.6 MHz
corner provides arithmetic margin, never permission to overclock.

For calculation, rise and fall each range0..300 ns independently. Zero is a
deliberately conservative mathematical endpoint for maximum frequency. An
actual MPU bus must also satisfy its minimum rise/fall limit20+0.1Cb ns
(Cb in pF), the stated10..400 pF range, electrical rails and actual device/
breakout requirements. The source table is characterized at25 C with its
specified circuit; it does not qualify our board over temperature. Pull-ups,
capacitance, low-speed GPIO output waveform and clock accuracy are unmeasured.

## Calculation

Let T=1/fkernel, P=5T, A=analog-filter delay, D=DNF=0, and s=2..3
synchronizer cycles. Each edge/filter/synchronizer corner is independent.
RM0456 p2710 and AN4235 pp10-12 give the following no-extra-stretch model:

```
high = A_high + (D+s_high)T + (SCLH+1)P
low  = A_low  + (D+s_low )T + (SCLL+1)P
period = rise + fall + high + low

setup_min = (SCLDEL+1)P_min - rise_max
hold_min  = A_min + (D+3)T_min + SDADEL*P_min - fall_max
valid_max = rise_max + A_max + (D+4)T_max + SDADEL*P_max
```

These are actual calculated bounds, not measured waveforms:

| Quantity | Calculated interval/bound | Required check |
|---|---:|---:|
| Kernel period T | 6.188119..6.313131 ns | conditional input |
| Prescaled period P | 30.940594..31.565657 ns | 5T |
| SCL high excluding rise | 1083.416..1175.606 ns | >=600 ns |
| SCL low excluding fall | 1454.703..1554.394 ns | >=1300 ns |
| SCL period | 2538.119..3330.000 ns | >=2500 ns |
| SCL frequency | 300.300..393.993 kHz | <=400 kHz |
| SCLDEL counter | 464.109..473.485 ns | rise + setup |
| SDADEL counter plus one T | 346.535..353.535 ns | RM output delay component |
| Data setup minimum | 164.109 ns | >=100 ns |
| Data hold minimum | 108.911 ns | >=0 ns |
| Data/ACK valid maximum | 787.475 ns | <=900 ns |
| Extra SDA-delay counter maximum | 827.020 ns | below SCLL counter minimum1392.327 ns |

The extra SDA-delay counter is [(SDADEL+SCLDEL+1)(PRESC+1)+1]T=131T;
it does not extend the programmed225T low counter in this model. Software
failure to feed/drain data can still stretch the bus. RM Table662 assigns
SCLL also to bus-free/repeated-START setup and SCLH to START hold/STOP setup.
Their counter minima1392.327 ns and1021.040 ns respectively exceed the1.3 us
bus-free and0.6 us START/STOP minima. Kernel period6.313 ns also satisfies
RM p2693's clock inequalities by a wide margin. ES0499 Rev12 section2.20.1's
Fast-mode transmitter-setup minimum kernel10 MHz is met conditionally.

## Transfer and acceptance budgets

Every byte includes its ninth ACK/NACK clock. Register reads use address-write,
one register byte, repeated address-read and the requested receive bytes.
Register writes use address-write, register and value. These figures include
only clock periods; START/STOP, bus-free admission, target/controller stretching,
software and preemption add time.

| Operation | SCL clocks | Modeled clock portion | Ideal400 kHz lower reference |
|---|---:|---:|---:|
| One register write | 27 | 68.529..89.910 us | 67.5 us |
| One register read | 36 | 91.372..119.880 us | 90 us |
| 14-byte read, comparison only | 153 | 388.332..509.490 us | 382.5 us |
| Selected0x3A..0x48 status+motion read | **162** | **411.175..539.460 us** | 405 us |

The selected contract values are100 us setup acceptance,600 us whole-request
acceptance and50 us separate terminal fault cleanup, with an8192-pass finite
poll backstop shared across an operation rather than renewed for every byte.
Capture the request anchor before admission/start; use unsigned wrapping
subtraction, reject equality and recheck before publishing. These are engineering
acceptance limits, not source-proved maximum completion times. No source-backed
post-PE1 startup delay requires a delay() call in pristine initial setup.
When PE is cleared, however, RM p2743 requires at least three APB cycles low
before reenable; do not remove that condition from any future restart path.
The selected terminal cleanup never reenables.

With a software microsecond clock tracking the same +/-1% frequency envelope,
and conservatively allowing one microsecond quantization per interval:

- Earliest600 us acceptance expiry is (600-1)/1.01 = **593.069 us**.
- The539.460 us burst clock bound leaves **53.609 us** for every omitted cost
  before that conservative deadline. Thus the clock portion fits, but neither
  the source nor this calculation proves every healthy burst completes in time.
  Unbounded target stretch or interrupt service can legitimately cause timeout.
- Latest600+50 us expiry is at most (650+2)/0.99 = **658.586 us**, **before**
  deadline-check lateness, preemption and return overhead. An800 us whole tick
  has at most **141.414 us** left on this arithmetic for all other work and
  those overheads; the nominal150 us remainder alone is insufficient evidence.
- Frozen-clock poll exhaustion proves finite iteration count, not800 us WCET.
  The8192-pass value has not been measured or given a target cycle bound.

Cleanup is a retained-owner PE disable/readback with a terminal reset-only
fault. PE0 releases this peripheral's line drivers and resets internal status;
it does not prove a completed STOP, external lines HIGH or a recovered MPU.
No synthesized STOP, RCC reset, GPIO pulse recovery, retry or shared-clock
change follows from these timing numbers. Capture error flags before PE0.
Transport completion does not establish sensor setup, freshness or heading.

## Reproduction and next action

`python state/analysis/P2_i2c_timing_raw/calculate.py` passes128 independent
corners, exact rational high/low/period and setup/hold/valid constraints,
field encoding, SDA-delay dominance and positive burst-clock margin. A
negative control rejects the prior stock fallback's2.000 us fastest modeled
period at nominal160 MHz; this is not a claim about its measured bus speed.
calculation.json retains every corner and the deadline arithmetic.

source_receipts.json records source revisions/pages, reused local hashes and
retrieval limits. Direct DS/AN downloads timed out and the direct TDK URL
returned404; positive official web/indexed retrievals are distinguished from
those failures. No missing PDF is represented as cached evidence.

Next: implement/test the D079 bounded transport against this conditional fixed
profile. Later qualify the clock policy, actual bus electrical timing and both
success/fault whole-loop time on the robot before runtime acceptance. This
report creates no new physical fact, wiring approval, deployment or phase pass.
