# D079 bounded native MPU6050 transport contract

2026-09-23 Asia/Dubai. D051/D075 authorize P2 B3 software before hardware
acceptance. This contract freezes the public imu_bus_unoq.h boundary before
independent implementation and tests. It specifies the actual narrow I2C4
transport; sensor setup, sampling freshness, units and heading come afterward.
No application integration, upload, physical test or human gate is implied.

## Source binding and conditional timing

Read P2_i2c_native_audit.md/raw and P2_i2c_timing.md/raw. The installed core is
arduino:zephyr1.0.0 with native I2C4 at0x40008400, ordinal40, deferred and
IRQs100/101. Qwiic's existing default route is PD12/PD13, AF4, open-drain,
pull-up, low speed. These are source facts, not new wiring or live pin approval.
The transport must check actual DT base/clock/IRQ/default-pinctrl metadata,
native device state and source-derived clock/power prerequisites before use.

Select TIMINGR0x40EB202C, analog filter ON, digital filter0. Fields are PRESC4,
SCLDEL14, SDADEL11, SCLH32, SCLL44. The timing report derives this profile with
the actual U585 analog-filter50..115ns range. Its conditional clock envelope is
158.4..161.6MHz and rise/fall at most300ns; the MCU operating-frequency limit
still applies independently. The envelope is an engineering acceptance premise,
not proof that the installed oscillator meets it or permission to overclock.
SC-AJ remains an open global runtime blocker. Do not change shared clocks or
invent a lock indicator to make a profile check pass.

New config values: address0x68 (support0x69 when explicitly configured), existing
portD/SCL12/SDA13/AF4, the fixed TIMINGR,100us setup acceptance,600us transfer
acceptance,50us separate fault cleanup,8192 total polling passes per operation.
Register/address/port/count suffixes are explicit R9 naming exceptions. No B16
value is changed. Invalid values fail before peripheral/pad mutation: only
0x68/0x69 and the exact supported route/timing are admitted; time/count limits
must be nonzero and less than2^31. The fixed filter policy is not tunable here.

The15-byte read needs162 SCL clocks. The timing model is not whole-tick WCET,
nor a guarantee that interrupt load or clock stretching fits the600us deadline.
Both accepted and fault paths require later on-robot qualification below R4's
800us complete tick budget. A fast or slow software clock also changes physical
deadline duration. Preserve the report's physical-time uncertainty.

## Public result and lifetime

imu::Bus is noncopyable with no constructor/destructor I/O, dynamic allocation,
Wire API, semaphore, interrupt registration, Bridge call or retry/recovery loop.
It owns one fixed MPU6050 address from config. No caller-supplied bus/device or
arbitrary-length transfer is exposed. Register enum entries are the exact
configuration/identity set in the public header. Read permits every enum entry;
write excludes INTERRUPT_STATUS and IDENTITY. Invalid enum casts or read-only
writes return INVALID_REQUEST without I/O or poisoning an otherwise ready Bus.

begin is one attempt per instance. A second call returns ALREADY_STARTED with
ready=false and no I/O; it does not release an established owner. One static
zero-initialized irreversible boot claim is set after pristine admission and
before the first pad/controller mutation. Clock-enable preparation alone is not
the claim. Ignored first writes, failed setup, object destruction and a second
Bus cannot clear a consumed claim. Preclaim failures do not steal another owner.
There is no release, reset, resume, automatic address scan or retry API.

Before begin, transfer methods return NOT_INITIALIZED without I/O; after a
terminal failure, supported methods return FAULT_LATCHED without new I/O.
Malformed requests are rejected first as INVALID_REQUEST. Fault results include
recorded native error flags before cleanup and a distinct cleanup status.
error_flags retains observed ARLO/BERR/NACKF/OVR/PECERR/TIMEOUT/ALERT and any
unexpected protocol status bits (TXIS/RXNE/ADDR/STOPF/TC/TCR/DIR/ADDCODE).
Ordinary allowed progress bits are not errors. Missing flags cannot be invented
when a deadline or ownership failure prevents further safe observation. This
explicit diagnostic definition includes protocol faults before PE0 erases them.

BusTransfer is value-initialized. All failed calls leave bytes zero, count0 and
complete=false. Successful reads publish exactly1 or15 bytes; successful writes
publish count0/zero bytes and complete=true. started_us is the request admission
observation and completed_us the final acceptance observation, using wrapping
uint32 micros. Software timestamps bound observation, not physical sample time.
Completion means an entire checked bus request, never sensor identity, accepted
configuration, unique sample, accurate voltage/clock, valid yaw or calibration.

## Admission and native ownership

Serialized setup must exclude every stock Wire1/native I2C4 controller/target,
DMA/interrupt/raw-register producer, PD12/PD13 owner and clock/power reconfigure
for the lifetime. Public device state must exist, initialized=false and
init_res0. Both IRQs enabled/pending/active must be0. Those predicates cannot
detect all concurrent initialization; exclusivity is a whole-application premise.

Use only finite installed native operations. Check clock-source metadata and
live nominal PLL/MSIS/AHB/APB1/I2C4 selection plus the established Range1/ASV/
EPOD requirements without changing them. GPIO D must be ready with its clock
enabled. Pins must be unlocked and initially analog/no-pull before being claimed.
Check default pinctrl route/AF/type/pull/speed metadata, not the sleep route.

Enable only I2C4's APB1-group2 clock gate and read it back before accessing the
peripheral. If pristine admission fails, leave it enabled, unclaimed; do not
blindly reset or disable a possibly shared resource. Pristine means CR1/CR2,
OAR1/2,TIMINGR,TIMEOUTR,AUTOCR0; ISR exactly reset TXE, no event/error/BUSY.
Set the irreversible claim before configuring either pad or the controller.

Configure only the selected two pads and their specified AF4/open-drain/pull-up/
low-speed mode, with readback. Configure timing/filter with PE0, all target,
interrupt, DMA, autonomous, SMBus, PEC, wake and special modes disabled; then
enable PE and check. No stock device init, RCC reset, IRQ disabling or line
bit-banging. Setup acceptance and any fault cleanup remain finite.

Runtime guards preserve device/IRQ/clock/pad ownership and exact control modes.
Each new request requires no old event/error, pending START/STOP or active BUSY,
and both actual GPIO input bits HIGH. BUSY0 alone after PE0 is not bus health.
No dummy read or status clearing may turn an old event into fresh completion.
Dynamic transfer fields are checked for the current request; do not mistake
hardware-cleared command flags for ownership loss or rewrite fields while START1.

## Bounded transfer sequence

All request waits share the original600us acceptance deadline and total8192-pass
budget; no per-byte or per-phase restart. Every interval uses unsigned wrapping
subtraction. Equality rejects (elapsed>=budget); a final elapsed/ownership/error
check is required after the last progress observation and before publication.
Poll exhaustion fails even if micros is frozen. Recheck after a readiness
observation before the next write so an observed ownership loss cannot permit
another command. Every loop and byte index has a fixed bound.
The setup operation has its own100us/8192 budget. Terminal cleanup is a separate
operation with its own50us/8192 budget; it does not borrow or restart the failed
request's acceptance budget. Thus a failed transfer plus cleanup can consume at
most16384 polling passes, still not a measured physical-time bound.

For a single register read or readMotion:

1. Require a clean idle bus and controller. Start one7bit address-write with
   NBYTES1/SOFTEND/RELOAD0; transmit the selected register exactly once on TXIS.
2. Wait for fresh TC and START0, errors excluded, then issue the repeated START
   to the same address with NBYTES1 or15, AUTOEND1, read direction and RELOAD0.
3. Receive exactly the requested bytes into private staging on RXNE. readMotion
   starts at0x3A and spans INT_STATUS plus0x3B..0x48. Do not clear INT_STATUS in
   a separate transaction or describe the returned status bit as a counter.
4. AUTOEND supplies the final NACK/STOP. RXNE and STOPF may coexist on the final
   byte; drain that byte first. An early STOP, extra RXNE, unexpected TXIS/TC/TCR,
   target ADDR or inconsistent mode/error never completes successfully.
5. Require fresh STOPF, START/STOP inactive, BUSY0 and no excess RXNE. Clear only
   the owned STOP flag, confirm it cleared, then final-check deadline/ownership/
   errors and publish once. No intermediate caller-visible data or stale cache.

For writeRegister: address-write/NBYTES2/AUTOEND1; transmit register then value
once each on TXIS, wait for the same checked fresh STOP completion. No repeated
START, receive data, silent configuration verification or extra transaction.
Higher sensor setup must subsequently read back its chosen settings.

## Failure and cleanup

Any runtime hardware error, bad ownership/mode, unexpected event, nonidle bus,
readback failure or deadline/count exhaustion terminally faults this Bus. Report
ARLO before other simultaneous errors, then BERR, NACK, OVR, then other protocol
errors. BERR is conservatively invalid even though ES0499 permits spurious BERR
continuation; a false invalid sample is preferable to unverified completion.

The selected minimal fault policy is local disable, not bus recovery. Under
retained native ownership, clear PE once using its command-safe CR1 operation
and boundedly confirm PE0 within the separate50us/8192-pass cleanup budget.
There is no synthesized STOP, no replay of pending START, reenable, RCC reset,
GPIO clock pulses, IRQ manipulation or retry. This avoids guessing controller
ownership after ARLO or an uncompleted address phase. Snapshot error flags before
PE0 resets internal state; do not erase the failure evidence first.

DISABLED means PE0 was observed and deadline/ownership still hold; it does not
mean STOP completed, external SDA/SCL are HIGH or the sensor recovered. Ignored
disable, expired/frozen-clock count bound or unconfirmed readback gives
UNCONFIRMED. Preownership failure or lost ownership gives NOT_ATTEMPTED and no
blind controller/pad write. Once ownership has been observed lost, cleanup may
not reacquire it from a later coincidentally matching snapshot. Partial owned
setup must be tracked explicitly so readback failure does not force uncontrolled
writes to a new owner. Final terminal calls perform no further native operations.

## Verification and scope limits

Independent tests derive expectations from this contract, public header, config
and actual installed register operations, without reading implementation CPP.
Exercise both supported addresses, every register/read-only restriction, both
read lengths and2byte write; precise TXIS/TC/repeated START/AUTOEND/STOP/W1C order;
last RXNE+STOP, early STOP/extra data, every error and simultaneous priority;
stale flags/low lines/BUSY, deadline adjacent/equality/wrap/frozen clock, total
budget across bytes, ownership loss at progress/final boundaries, ignored writes,
boot claim after partial failure and failed cleanup. Compare complete-zero
failure buffers and no retry/allocation/I/O constructors. Preserve real failures.

The inert bench/p2_imu_bus_compile probe retains actual methods behind an unused
volatile function pointer; setup stores only its address, loop is empty, and no
global constructor calls begin/read/write. Test10000loops in both host macro
modes and every upload combination refusal before board lookup. Compile on the
actual board Linux toolchain, inspect source/ELF/native imports and perform a
fresh separate read-only review. Changes to exact existing inert source hashes
need explicit review; no new upload allowlist key is added.

Physical address/breakout/pull-ups/voltages, MSI/clock qualification, SCL waveform,
fault timing and whole-loop WCET remain pending. Subsequent bounded MPU6050
reset/config/readback, data-ready/age semantics, axis transform, gyro bias and
heading integration are unfinished B3 work. No transport-complete bit may stand
in for those requirements or a human phase pass.
