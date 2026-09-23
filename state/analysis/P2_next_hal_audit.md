# Next P2 sensor HAL: checked battery acquisition

2026-09-23, read-only selection under D-051/D-075. **Recommend B5 next: a
concrete ADC1/A0 battery driver with finite native initialization and conversion
steps, explicit sample validity, and host/compile-only verification.** Its exact
ADC clock, initialization, ownership and errata prerequisites below must be
settled before native code is represented as verified. Stock `analogRead` or
`adc_read` cannot implement its deadline contract. This is a recommendation,
not a new decision, implementation, hardware acceptance or integration approval.

Only this file was written. Existing source, configuration, tests, ledgers and
other agents' files were untouched. No board connection, MCU operation, upload,
reset or peripheral call occurred. The date is before PLAN section 3's September
24 sensor work and September 26 P2 target; pending human gates remain pending.

## Comparison of the remaining drivers

| P2 bench / driver | Reusable evidence | Material obstacle | Selection |
|---|---|---|---|
| B5 `power` | F-078/F-079; exact A0 mapping, native ADC ABI, successful-call timing; HARDWARE divider proposal | Stock ownership/completion and some hardware polling are unbounded; no installed async/cancel API. Direct ADC ownership/init/clock/stop still need the targeted checks below. | Best next concrete driver: one regular channel, no bus transaction protocol, narrow raw-to-voltage result. |
| B2 `line_qtr` | F-082/F-083; checked GPIO paths and existing parallel acquisition diagnostic | BEHAVIOR B4 requires a read every tick with a 1500 us observation limit; R4 requires 1 kHz and <800 us WCET. The observed bare-board diagnostic took 1530–1536 us. | Do not silently port the blocking diagnostic into runtime. An explicit acquisition/freshness scheduling decision and proof are still required. |
| B3 `imu` | F-084/F-085; Wire1/I2C4 mapping, installed driver audit, retained MPU6050 compile probe | Installed I2C has K_FOREVER ownership, 500 ms completion, ignored Wire stopBit and a BERR-only success-path problem; library failure/reset behavior also remains. | Replacing the actual bounded I2C transport is broader than one-channel ADC acquisition. Compile success does not repair it. |
| B6 `ui` | Logical mode/button behavior already exists; A1 mapping is verified | A1 shares ADC1 with A0. The proposed ladder makes START and BOTH electrically identical; matrix runtime/interaction qualification is separate. | Share the eventual ADC owner; do not invent BOTH discrimination or duplicate ADC initialization. |

This comparison is about the next implementable software increment. It does not
change the edge-first priority or imply that B2/B3/B6 can be omitted before use.

## Established facts that should not be researched again

The complete installed identities, hashes, line references and packaged-ELF
checks are in [P0_adc_installed_contract_20260923.md](P0_adc_installed_contract_20260923.md).
F-078 establishes A0 = Arduino14 / PA4 / ADC1 channel9; A1 = Arduino15 / PA5 /
ADC1 channel10. ADC1 is deferred-init device ordinal17. The installed DT uses
single-ended 14-bit conversion; Arduino defaults to a shifted 10-bit return.
Zero is a valid raw result. The API's 3300 mV reference metadata is declared,
not measured. These facts do not grant PINMAP approval.

The installed synchronous path has K_FOREVER ownership and completion waits,
including warm calls. ADC_ASYNC/STREAM/RTIO/DMA support is not compiled in.
LDORDY/calibration/disable-stop loops have hardware-dependent back edges without
total deadlines. The bounded local enable helper does not bound the complete
read. An elapsed check after a blocking call, a worker thread, or a sketch macro
cannot change that precompiled implementation. The existing per-pin ADC pinctrl
helper can itself call `device_init`; calling it is not a way around this gap.

F-079's 276 us first and 139–140 us subsequent successful calls characterize
one bare-board setup-only run. They establish no failure deadline, battery
accuracy or runtime WCET. Reuse [P0_adc_validation.md](P0_adc_validation.md),
not a new successful-call benchmark offered as proof of bounded failure.

HARDWARE sections 2/3 propose A0 with 100 k / 22 k and 100 nF. Its nominal divider
factor is 122/22; neither component tolerance nor actual reference calibration
is measured. B5 still requires comparison with a multimeter over 9.5–12.6 V.
Do not add another one-second filter: `Governor::step` already implements B6's
`VBAT_FILTER_MS` in `src/core/governor.cpp:59–70`.

## Minimum real implementation to pursue

Use `src/hal/power.h/.cpp` with one private, target-specific ADC1 implementation
(a separate private source only if it keeps the module small). No general ADC
framework, background worker, new heap use, bus library or synthetic-only Port
is needed. Compile the actual native implementation against test substitutes.
Keep app integration and UI decoding out of this increment.

1. A constructor performs no I/O. Checked setup claims the unchanged A0 route
   and ADC1 only after confirming the approved initial ownership/register state.
   Set up one software-triggered regular channel with a source-verified clock,
   resolution, sampling time and calibration sequence. Each readiness/calibration
   wait must have an explicit finite termination rule; do not delegate it to the
   known-unbounded stock initializer. Reject an already-owned/incompatible ADC
   instead of stealing it or resetting a shared peripheral.
2. Runtime starts one conversion and services it through short finite steps.
   Prefer a start/poll interface so it need not spin for the conversion time.
   A pending sample is not a new reading. Admit completion only for the current
   request, verified status/mode and source-proved flag/data order, before its
   deadline. A frozen clock must not create an unbounded loop; eventual pending
   expiry can also use a finite service-attempt count. Timing/attempt constants
   belong in config under a later explicit D-051 decision.
3. Preserve raw code, resolution, request/sample identity, timestamp and status.
   Expose nominal/calibrated volts with their provenance. Reject impossible
   raw/configuration states and nonfinite calibration arithmetic. Keep a valid
   raw zero distinct from native failure and from a physically healthy battery.
4. Fault/late/overrun results are invalid. If an owned conversion is active,
   request its documented stop without an indefinite wait. Do not announce
   successful cancellation or rearm until the required hardware stop state is
   observed. If it never arrives, remain faulted and retain ownership; a deadline
   does not prove that the peripheral stopped. Avoid automatic peripheral resets
   or blind writes after ownership loss.
5. ADC1 has one owner. Exclude stock analogRead/adc_read and unrelated ADC1 IRQ,
   DMA, injected, continuous, trigger or calibration producers. This first
   increment need only acquire A0; later A1 must use that same owner, with an
   explicit channel-change sequence and freshness contract. Do not initialize
   a second ADC driver independently from `ui`.

The base `core::Inputs` has only `vbat_v` (`types.h:31`), but the actual
`fsm::RobotInput` wrapper already adds `vbat_valid`; P1_robot_contract requires
a fresh valid finite battery sample before motion. The new HAL must preserve
validity and age for that existing boundary. The governor itself only checks
finiteness, so bypassing the wrapper or promoting an old finite value would lose
the distinction. No new core validity field is needed. Do not quietly substitute
V_NOM, zero or an old sample as a fresh successful reading. This corrects the
original audit's incomplete inspection of the base struct alone.

## Exact remaining source prerequisites

The U5 manual is already available: official ST Japan [RM0456 Rev6](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf),
cached at `build/cache/RM0456_Rev6_52152e41.pdf` (73,439,635 bytes; SHA-256
`52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616`).
It need not be downloaded again. The next bounded source pass must establish:

- **Actual ADC clock and power prerequisites.** Read the installed ADC1 DT/config,
  selected RCC clock/reset lineage, ADC prescaler and board supply/reference
  assumptions. Match RM0456 33.4.3 pp1272–1273 and device datasheet operating
  limits. Do not inherit the timer's 160 MHz calculation as the ADC clock.
- **Safe init/calibration and revision handling.** Read RM0456 33.3/33.4.6–10
  pp1267,1276–1282 plus the installed LL helpers. Page1267 explicitly distinguishes
  U585 (ADC1 and ADC4; no ADC2) and says extended calibration is unsupported on
  U575/U585 revision X. Select a supported sequence and all necessary waits;
  do not invent a silicon revision or ignore its calibration restrictions.
- **Regular conversion and flags.** Verify 33.4.11–18 pp1283–1289, 33.4.22–27
  pp1294–1304 and register descriptions 33.6 pp1340–1367: channel9 selection,
  preselection/sample time, full-resolution data, stale EOC/EOS/OVR handling,
  W1C versus read side effects, and completion/late-result ordering.
- **Stop and fault ownership.** Pages1288–1289 were read in this audit: ADSTP
  requests regular abort and discards its partial result; ADSTART must clear
  before software assumes the ADC stopped. The complete stop/control-bit
  constraints still need to be translated into the chosen bounded code path.
- **Installed owner/API exclusions and final imports.** Reuse the packaged ELF
  hash `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`
  and established device/config objects. Inspect IRQ routing/enable and actual
  driver init behavior; prove chosen clock/pin calls avoid stock ADC init and
  unbounded callees. Never treat a named zero-valued export as callable.
- **ADC-specific errata.** Review the actual ADC subsection of current ES0499,
  including revision applicability and required workarounds. The previous timer
  audit retrieved Rev12 (June2026) but reviewed its timer subsection only. This
  audit's main ST and ST China retrievals timed out, so ADC errata coverage is
  explicitly incomplete; those failures are not evidence of absent errata.

For the exact next installed read, use
`C=/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0` and
`I=C/variants/arduino_uno_q_stm32u585xx/llext-edk/include`. Read/hash
`I/modules/hal/stm32/stm32cube/stm32u5xx/drivers/include/stm32u5xx_ll_adc.h`
and relevant LL RCC/PWR helpers, existing `soc/stm32u585xx.h`, generated DT and
autoconf. The old ADC audit did not record the LL ADC header's complete content
or hash; it must be obtained, not assumed. Use read-only installed Linux files
and offline ELF, with no MCU calls. `adc_stm32.c` is absent from that installation;
its exact versioned [primary source](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/adc/adc_stm32.c)
and the existing matching-ELF audit supply the driver side. Retrieve the actual
ADC errata paragraphs from [ES0499](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)
or its official regional mirror, preserving revision and page evidence.

## Verification and completion boundary

Independent tests should exercise actual native code: rejected ownership and
mode/clock mismatch; init failure at each hardware wait; stale flags; raw zero,
maximum and invalid values; missing/late conversion; wrap/frozen time; overrun;
stop-request versus stop-complete; no rearm after failed stop; repeat/old receipt;
and nominal/calibrated scaling without a second B6 filter. Target-compile a
retained never-called probe and inspect actual native accesses/imports and inert
startup. No upload is needed to prove that code builds.

Physical reference/divider accuracy, source impedance and settling, signal
noise, real error recovery, WCET and B5's +/-0.05 V requirement remain separate
measurements. No host test or compile-only receipt supplies them. The next useful
action is the short ADC-specific source pass above, followed directly by the
concrete bounded driver and independent tests under a recorded implementation
contract; another wrapper around synchronous ADC calls would not advance B5.
