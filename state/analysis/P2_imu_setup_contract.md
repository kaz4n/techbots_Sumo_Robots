# D080 MPU6050 checked setup and coherent decoder

2026-09-23 Asia/Dubai. D051/D075 authorize this P2 B3 software increment.
Public interface: src/hal/imu.h. Source: P2_mpu6050_sample_audit.md and its
manufacturer-document receipts. Baseline70b52c5; this is not runtime acquisition,
heading, calibration, app integration or physical acceptance.

## Fixed profile and scope

Select gyro +/-1000dps (32.8LSB/dps), accelerometer +/-8g (4096LSB/g), DLPF1 and
divider0 (nominal1kHz). New config constants name these selections and waits;
no existing B16 default or pin changes. Exact profile support only: unsupported
range/filter/divider or zero/half-range-invalid bounds return INVALID_CONFIG.
Require every wait < setup deadline, deadline <2^31us, and count limits1..65535.
Register bit encodings and documented scale factors are fixed format constants,
not independently tunable copies. All setup readbacks require the full expected
byte, including zero reserved bits: unexpected reserved values conservatively
reject this supported profile, not a claim that every silicon revision reads0.

Setup holds a reference to the existing concrete Bus. Construction/destruction
does no I/O and owns no new hardware. start(now,power_confirmed) arms exactly
once, with no Bus calls; false power confirmation terminally faults. Repeated
start returns the existing report unchanged. advance before start, after fault
or after PROFILE_READY returns the existing report without I/O or count changes.
The caller owns the power-valid precondition; passing true is not evidence.

## Finite exact sequence

Every Bus call below occupies its own advance invocation. Wait steps may share
their expiration call with the immediately following single Bus operation, but
never perform two Bus operations per invocation. Normal sequence48 Bus calls
including begin, with no retry/recovery. Each named wait begins at start or the
specified successful write's completed_us, never at an earlier caller time.

1. Wait IMU_POWER_WAIT_US110000 from start; Bus.begin once. Require OK,ready=true,
   cleanup NOT_ATTEMPTED. Then read IDENTITY exactly68; write POWER_1=80.
2. Wait IMU_RESET_WAIT_US110000 from reset write completion. Read POWER_1=40
   (reset cleared, sleep set); read IDENTITY=68 again. Then require reset-zero
   POWER_2,USER_CONTROL,FIFO_ENABLE,FILTER,SAMPLE_DIVIDER,GYRO_RANGE,ACCEL_RANGE,
   INTERRUPT_CONFIG,INTERRUPT_ENABLE, in that order.
3. Write/read POWER_2=00, then write/read POWER_1=00. Wait IMU_GYRO_WAIT_US50000
   from the POWER_1 write completion. Write/read POWER_1=01; wait IMU_PLL_WAIT_US
   20000 from that write completion.
4. Write then immediately read back each pair, in order: USER_CONTROL=00,
   FIFO_ENABLE=00,INTERRUPT_CONFIG=00,FILTER=01,SAMPLE_DIVIDER=00,GYRO_RANGE=10,
   ACCEL_RANGE=10,INTERRUPT_ENABLE=01. Wait IMU_FILTER_WAIT_US20000 from the
   final INTERRUPT_ENABLE write completion (conservative final-change anchor).
5. Final readbacks in order: IDENTITY=68,POWER_1=01,POWER_2=00,USER_CONTROL=00,
   FIFO_ENABLE=00,FILTER=01,SAMPLE_DIVIDER=00,GYRO_RANGE=10,ACCEL_RANGE=10,
   INTERRUPT_CONFIG=00,INTERRUPT_ENABLE=01. Then one readMotion, requiring
   complete15bytes and no status bits except bit0. Discard all motion values.
   Its successful completion, strictly before deadline, yields PROFILE_READY.

All values above are hexadecimal except counts/times/ranges. The user register
profile is finite; no stock Wire/Adafruit reset loop or optional DMP/FIFO path.

IMU_SETUP_DEADLINE_US1000000 is an absolute exclusive acceptance deadline from
start. IMU_SETUP_MAX_ADVANCES1024 includes every in-progress invocation, including
waits. The1024th invocation is permitted; the next faults before work. Likewise
IMU_SETUP_MAX_REQUESTS64 includes Bus.begin; check before every bus operation.
Both counters saturate at their caps. Tests use variant limits to reach boundaries.
Forward time uses unsigned intervals <2^31. Backward/half-range ambiguity faults
TIME_ORDER. Input now must not precede the last observed successful completion.
At equality with the absolute deadline fail DEADLINE before any further Bus call.
After each transfer, started_us must follow/equal call time, completed_us must
follow/equal started_us and elapsed must be strictly < IMU_I2C_TRANSFER_US.
Then recheck the complete setup deadline at completed_us before accepting bytes.
Success requires statusOK,complete=true,exact count(0write,1read,15motion),
error_flags0,cleanup NOT_ATTEMPTED. Any violation is a terminal fault. Bus faults
retain status/cleanup/error_flags in SetupReport; no silent success or later I/O.
begin has no completion timestamp and cannot itself publish PROFILE_READY.

Fault classifications: Bus nonOK => TRANSPORT; malformed successful transfer or
duration at/over600 => RESPONSE; nonmonotonic timestamps => TIME_ORDER; absolute
expiry => DEADLINE; WHO_AM_I mismatch => IDENTITY; other register mismatch =>
READBACK; unexpected motion status bits => STATUS. A failing init with statusOK
but !ready or unexpected cleanup => RESPONSE. NonOK wins over response checks.
No disable/reset is attempted by Setup after a semantic failure; transport is
already idle on a completed semantic rejection, and further use is prohibited
by this Setup lifecycle. Bus remains externally exclusive to this driver.

Clarified response-check precedence before implementation/testing: nonOK status,
then shape/cleanup/error flags, then forward timestamp order, then transfer
duration, then setup absolute deadline. Both setup and decode require a positive
IMU_I2C_TRANSFER_US below2^31; invalidity is INVALID_CONFIG. The decoder does not
depend on setup-only waits/caps/deadline. Its malformed or backwards/ambiguous
observation interval is RESPONSE (DecodeStatus has no TIME_ORDER value).

The setup waits are conservative engineering acceptance choices. They are not
proof of all-temperature gyro/filter settling, oscillator accuracy or calibration.

## Coherent decoder (no freshness API)

decodeMotion is a pure C++17 function with no state/I/O/allocation. Validate fixed
profile, then nonOK status as TRANSPORT, then complete/count15/flags0/cleanup and
strict transfer duration as RESPONSE, then unexpected byte0 bits as STATUS.
Bit0 may be0or1; neither value certifies payload generation. Successful results
copy observation interval and status byte. These are bus observation times, not
sensor sample times. Raw accel[XYZ], temperature, gyro[XYZ] use big-endian signed
16bit semantics represented in int32; explicit unsigned subtraction65536 avoids
implementation-defined casts. Scale accel/gyro with the fixed profile above.
rail_mask marks raw -32768 or32767 for bits0..2 accel,3temp,4..6gyro. A rail flag
does not invalidate coherent bytes; no rail flag does not prove unsaturation.
Any failure zeros every payload/timestamp/flag field, coherent=false; only the
DecodeStatus describes failure. No new-generation flag, yaw or health output.

## Required validation

Independent tests derive from this file/header/manufacturer layout, not imu.cpp.
Scripted substitutes exercise actual Setup code: exact48-call ordering/full
readback, one call per advance, write-completion wait anchors, every response and
register mismatch, terminal no-retry, time wrap/backward/equality, frozen-time
advance/request caps and supported/invalid config. Decode endian signed limits,
axis placement, scale, all rail bits, status0/1 and malformed/fault zero outputs.
No old locked tests change. Full host/sanitizer and relevant tooling checks plus
retained-method compile-only probe and separate review complete software scope.
Physical settling/address/power, sample rate/freshness/yaw and full-tick WCET are
pending. The later status/STOP/motion freshness handshake needs one aggregate
deadline and explicit sample-age policy; two600us Bus calls are not an800us tick.
