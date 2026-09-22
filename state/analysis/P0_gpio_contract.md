# D-064: bare-board internal LED GPIO timing

Scope: P0 0.4 under D-051/D-052, using only the installed LED_BUILTIN/LED3_R
mapping PH10/index50 (F-080 and P0_gpio_installed_contract_20260923.md).
No header, motor, PWM, matrix, ADC, I2C or Bridge operations. New bench/p0_gpio
uses setup-only finite work and empty loop. This is a measurement scope choice;
installed native GPIO paths have no discovered unbounded wait. Preserve R4.

## Public contract before code/tests

config::P0_GPIO_PIN=50, checked against LED_BUILTIN and LED3_R at compile time;
config::P0_GPIO_SAMPLES=400. This count keeps all raw results below the existing
16384B passive-read bound; it is not a behavior tunable. MOTORS_ALLOWED must be0.
p0::gpioReady() is a read-only readiness query using the installed GPIOH device,
not initialization or pin reconfiguration. It is checked once before all GPIO
calls. If false, publish version1/ready0 but no complete flag or samples; return.

Expose volatile p0::GpioCapture p0Gpio in zero-initialized BSS, with the public
layout in bench/p0_gpio/src/gpio_capture.h. Header fields: version, ready,
complete, completed, start_us, end_us (uint32), final_level (int32). Then400
GpioSample records: overhead_us, pin_mode_us, write_high_us, read_low_us,
read_high_us, pair_us (uint32), low_level, high_level, pair_level (int32).
Size36B/sample and14428B/capture. Version1, ready1 after successful readiness.

For each sample, in this order:
1. Record paired adjacent micros overhead (no subtraction).
2. Time pinMode(P0_GPIO_PIN, OUTPUT), which establishes physical LOW/on.
3. Time digitalRead on that pin; retain the signed low_level.
4. Time digitalWrite on that pin to HIGH/off.
5. Time digitalRead on that pin; retain signed high_level.
6. Time the contiguous pinMode(OUTPUT)+digitalWrite(HIGH) pair.
7. Read pair_level, untimed, to check that the pair finished HIGH.
8. Store all fields, then publish completed=i+1. If levels are not exactly0/1/1,
   stop further samples, attempt HIGH/off once more, read/store final_level and
   end_us, and return with complete0. No hidden retry or discarded bad sample.

On normal completion also attempt final HIGH/off, read/store final_level, then
end_us; publish complete1 only if final_level==1. First start_us precedes any
sample timing; every unsigned interval uses wrap-safe subtraction. No globals,
fields or peripherals are updated by loop after setup. If setup does not finish,
the incomplete record never becomes success. A LOW read can also represent a
masked native error; readbacks are observations, not recovered native error codes.

## Decoder and passive capture

tools/p0_gpio_capture.py reuses only pinned p0_capture.py mechanics/config,
unchanged120s/16-read/16384B-per-RAM-read limits. Review exact source, target
constructor/hook/native dispatch, artifact hash and layout before upload/capture.
Default startup only; Immediate GPIO uploads rejected. Compile-only never uploads.
Compare every loader/sketch byte, two identical records and unchanged LLEXT/BSS
identity. Preserve raw dumps and commands. No MCU reset/halt/data writes during
capture. Record a >=60s quiet interval on the host before invocation, but retain
possible debug overlap because completion is checked after attachment. Do not
subtract host and board clocks for a precise interval.

Public analyze_record(data: bytes) raises ValueError unless exact14428 bytes,
version1/ready1/complete1/completed400/final_level1, all400 levels exactly0/1/1,
each of the six intervals <2^31, and total unsigned end-start <2^31 and >=sum of
all measured intervals. Zero durations are valid microsecond quantization.
Return version, samples, total_elapsed_us; first_call dict with all9 sample
fields; subsequent_calls dict with samples399 plus min_us/max_us/p99_us for
each of the six interval names; overhead dict min_us/max_us/p99_us for all400;
readbacks dict low_matches400, high_matches400, pair_matches400, final_highTrue.
Percentiles use nearest rank ceil(0.99*N), no overhead subtraction.

Independent tests: exact order/count/pin, first/subsequent values, wrap, readiness
failure/no GPIO, low/high/pair mismatch early termination and final off attempt,
final-level failure, publication/incomplete behavior, frozen loop, motor/mapping
compile rejection; decoder boundary/corruption/p99/zero/error cases and frozen
readout identity. Tool checks cover default-only/match/compile-only/source changes
and compile failure for both SSH/ADB. No locked test change.

Acceptance is empirical API timing plus observed digital readbacks on this exact
image. Initial physical LED state, optical appearance, electrical accuracy,
header-pin cost, production contention/interrupt load and full robot WCET remain
unproved. No PINMAP approval, human phase gate or P2 implementation follows.
