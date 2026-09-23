# P2 MPU6050 checked-sample source audit

2026-09-23, Asia/Dubai. Independent source preparation during D079 review.
Read-only repository/public-document inspection; no MCU or sensor operation.
Only this report and P2_mpu6050_sample_raw were written. D051/D075 permit the
next software task; identity, mounting, electrical and runtime acceptance remain
pending F056/F057 conditions.

**The next implementable task is a finite MPU6050 reset/configuration/readback
and sensor-coordinate sample decoder over imu::Bus.** Its result must distinguish
setup/fault/no-new/new observation from coherent transfer completion. A lone
INT_STATUS+motion burst does not, from the retrieved wording alone, prove that
its status bit identifies the generation in its coherent motion bytes. An
existing-API two-transaction handshake below gives a stronger freshness argument
at an explicit extra cost. Core calibration and continuous-heading integration
need a separate, recorded adapter contract; this audit changes neither.

## Primary evidence and revision limits

R: manufacturer RM-MPU-6000A-00 Rev4.0,2012-03-09,47 pages,
[SparkFun mirror](https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf).
Complete bytes downloaded; SHA-256
`ccaa6312b9d86a9da79e26e511101e1150dc85a48255600010a854369cf7c05d`.
Relevant page text is retained with hashes. The official-domain Rev4.2 indexed
register/shadow descriptions corroborate the narrow fields, but a complete
Rev4.2 original was not retrieved. Do not claim revision-matched silicon proof.

P: manufacturer PS-MPU-6000A-00 Rev3.4,2013-08-19,52 pages, official
[TDK source](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf).
Manufacturer-domain indexed tables were retrieved for pp12/17/30. The direct
TDK product URL timed out and the older official URL redirected to search.
For layout checking, the complete older Rev3.2 manufacturer document was obtained
from [CDI](https://www.cdiweb.com/datasheets/invensense/ps-mpu-6000a.pdf), hash
`d7ec2ddece4b2b0d5ff5ae4bcb2940cd17ca39b8fff11c9b979e24653c7c88dd`.
Its pp12/14 table images were inspected. It is labelled older throughout; it
does not silently replace missing Rev3.4 byte/column verification.

## Narrow register profile

All following registers are already in imu::Register. Write full selected bytes
with reserved controls zero; read back the defined mask, rejecting a mismatch.
Do not infer successful application from an ACK. No stock Adafruit or Wire path,
FIFO, auxiliary-master, DMP, FSYNC, self-test, cycle or axis-standby operation is
needed. No new INT connection or interrupt-handler ownership is proposed.

| Register | Address | Proposed value | Defined mask/readback purpose |
|---|---:|---:|---|
| IDENTITY | 75 | read only | FF, exactly68 at either AD0 address |
| POWER_1 reset command | 6B | 80 once | EF; reset bit80 must subsequently clear; reset state40 |
| POWER_1 wake, internal clock | 6B | 00 | EF; sleep/cycle/temp-disable/reset off |
| POWER_1 final clock | 6B | 01 | EF; X-gyro PLL, keep X gyro active |
| POWER_2 | 6C | 00 | FF; all axes active, no low-power wake selection |
| USER_CONTROL | 6A | 00 | 77; FIFO/master/interface-disable/reset controls off |
| FIFO_ENABLE | 23 | 00 | FF; no sensor/aux FIFO producers |
| FILTER | 1A | 01 | 3F; DLPF1, external sync disabled |
| SAMPLE_DIVIDER | 19 | 00 | FF; nominal1 kHz with DLPF1 |
| GYRO_RANGE | 1B | 10 | F8; self-tests off, FS_SEL2, +/-1000 dps |
| ACCEL_RANGE | 1C | 10 candidate | F8; self-tests off, AFS_SEL2, +/-8g |
| INTERRUPT_CONFIG | 37 | 00 | FE; INT_RD_CLEAR0, no FSYNC/bypass, default pulse pin |
| INTERRUPT_ENABLE | 38 | 01 | Rev4.0 mask59; only DATA_RDY enabled |
| INTERRUPT_STATUS | 3A | read only | bit0 ready; any other asserted status is unexpected in this profile |

Numbers in the table are hexadecimal. R pp8,12-15,27-29,39-43,46 support
these fields. Rev4.0 includes motion-enable bit6 in38, absent from the retrieved
Rev4.2 overview; setting only01 and rejecting any other live enabled bit avoids
relying on that difference. Likewise keep reserved USER_CONTROL bit7 zero;
do not assume an undocumented DMP interface. The8g accelerometer value is an
explicit development proposal, not a tuned or measured range. Other documented
AFS_SEL scales are2g/16384,4g/8192,8g/4096,16g/2048 LSB/g.

DLPF1 gives nominal gyro1 kHz,188 Hz bandwidth/1.9 ms delay and accel1 kHz,
184 Hz/2.0 ms. Divisor0 preserves that nominal sample rate. Those filter delays
are not settling-time maxima or observation timestamps. Gyro FS_SEL2 uses
32.8 LSB/(degree/s); FS_SEL3 alternatively gives2000 dps/16.4. The fixed profile
should be read back once established; never read range registers each sample.

## Finite setup candidate

Use a small caller-advanced setup sequence, with at most one bounded bus request
per advance. Every wait returns to the caller; no delay(), allocation, reset-bit
spin, NACK retry or bus recovery. One setup attempt, an absolute acceptance
deadline and a maximum advance/request count make failure finite even if the
time source stalls. A bus fault is terminal under D079, including during reset.

One concrete engineering candidate for a later contract is:

1. Require the independently established sensor power-valid precondition; wait
   110 ms from that conservative setup observation before the first device
   request. Begin Bus once, then require exact WHO_AM_I68. This does not identify
   breakout wiring or distinguish every compatible part/clone.
2. Write POWER_1=80 once. Wait110 ms, then read POWER_1 once: reject if RESET
   remains set or the expected reset/sleep state is absent. Recheck identity.
   The110 ms is a selected acceptance policy, not a vendor reset-time guarantee.
3. Write POWER_2=00 and POWER_1=00; verify. Leave reset DLPF0/internal clock
   active while allowing50 ms for initial gyro stabilization. Then write final
   POWER_1=01 and allow20 ms for PLL switching before later acceptance.
4. Write/read back the fixed controls above with DATA_RDY disabled until last;
   final enable01 only after the other settings pass. Allow20 ms after final
   filter/range changes. This is an engineering discard interval, not a proved
   maximum filter-settling specification. Recheck power/clock/range/rate/mode.
5. Discard an initial completed motion/status burst to establish a clear baseline.
   Admit runtime acquisition only after all setup predicates pass. A candidate
   overall1 s deadline,1024 advances and64 bus requests bounds this sequence;
   expired waits/missing advancement cannot manufacture a ready sample.

These proposed values belong in config only if adopted by a new decision; none
was added here. They allow completion under ordinary1 kHz advancement without
requiring it. Fast-clock tolerance/quantization applies to minimum waits;110 ms
exceeds100 ms even under D079's conditional+1% clock premise. SC-AJ remains
unresolved, so elapsed software time is not independent physical qualification.

Source limits matter: R p42 gives reset self-clear semantics but no duration.
P Rev3.4 p17 lists PLL settling typical1 ms/maximum10 ms at its table conditions.
Older full P Rev3.2 p14 gives register-access startup typical20 ms/maximum100 ms.
Its p12 places gyro ZRO30 ms in the **typical** column, with DLPF0 and a1 dps
settling criterion; indexed Rev3.4 column extraction is insufficient to promote
that number into a hard maximum. No retrieved specification proves all-temperature
DLPF1 settling or calibration quality merely because these waits elapsed.

## Coherence, freshness and the status race

R pp30-32 describes internal sensor registers and idle-updated user shadows.
The14 motion bytes in one burst therefore share a sampling instant. INT_STATUS
is outside that listed shadow set. R pp27-29 says INT_RD_CLEAR0 restricts clearing
to INT_STATUS reads, DATA_RDY is generated when sensor-register writes complete,
and status clears on read. It gives neither a generation counter nor a precise
atomic ordering between status assertion/read-clear and shadow freezing.

Consequently, a source-consistent counterexample for one15-byte burst is:
the bus starts with the previously consumed motion shadow; a new internal
conversion sets DATA_RDY before byte0 is read; byte0 returns1 but the busy
interface still holds the old motion shadow. This is an **unexcluded ordering**,
not a claim that measured MPU silicon necessarily behaves that way. Single-burst
coherence is established; single-burst new-generation certification is not.

An existing-API conservative handshake is:

1. readRegister(INTERRUPT_STATUS). Failure is terminal; bit0=0 yields NO_NEW
   without motion publication. Reject unexpected status bits.
2. When bit0=1, require that request's completed STOP/idle before readMotion().
   That idle provides the documented shadow-copy opportunity following the
   observed event. Accept only a complete15-byte result and the final common
   sensor-operation deadline. Never retry a failed second transaction.
3. The new payload is newer than the previous accepted payload under the
   stated shadow/clear model and sole-owner/no-reset premises. Its included
   status byte is not a second sample certificate: retain it diagnostically,
   reject unexpected status, and do not assign another generation from bit0.

This handshake is an inference from the documented behavior, checked by
freshness_model.py over13,122 single-acquisition and65,536 paired schedules.
It does not prove actual device synchronization latency or physical timing.
The next contract must explicitly adopt this inference, or obtain stronger
manufacturer/physical evidence for the single-burst status/payload relationship.

The extra status read costs36 clocks: total198 rather than162. Under the prior
conditional timing calculation, clock-only time is502.548..659.340 us, before
START/STOP, software, stretch and other tick work. Two independent600 us bus
allowances do not create an800 us sensor/tick bound. A common aggregate sensor
deadline and measured full-loop budget remain necessary; this audit does not
silently increase D079's allowance or claim feasible measured WCET.

Even the handshake reports at least one event, not how many updates occurred.
Identical numerical data can be genuinely new; changed bytes do not establish
generation identity. A software sequence increments only accepted observations,
never estimated sensor generations. Multiple updates can overwrite/coalesce.
Transport start/end are observation bounds, not physical sample timestamps;
filter delay and polling phase remain additional age uncertainty.

## Decoder and proposed result boundary

For bytes0..14: status0; accel X1/2,Y3/4,Z5/6; temperature7/8;
gyro X9/10,Y11/12,Z13/14. High byte precedes low byte, signed two's-complement.
Decode through unsigned16 then signed32 subtraction65536 when bit15 is set,
avoiding an implementation-defined out-of-range signed16 cast in C++17.
Convert gyro by32.8 and candidate accel by4096. Preserve sensor-axis raw values.
Do not infer robot X/Y or clockwise Z polarity from package axes or Qwiic.

The narrow result should contain setup state, transport status, observation
state {NO_NEW, NEW, FAULT}, raw/scaled sensor-coordinate motion, local accepted
sequence, request observation interval and explicit age/continuity metadata.
Failure/no-new produces no new-value publication, sequence increment, calibration
reading or yaw integration. Keep retained diagnostic values separately from a
new observation; count/surface rail values without claiming all other values
are necessarily unsaturated. No FIFO/DMP or temperature compensation is needed.

## Existing core boundary and the required next decision

The actual inspected headers name countdown::Controller/Lifecycle/Services and
fsm::HeadingReference, not GatedController/HeadingFrame. countdown.h
ServiceSample has raw gyro plus imu_ok but no no-observation state. Its contract
requires new samples and rejects any invalid calibration-window reading.
fsm.h RobotInput similarly has imu_ok for the combined IMU payload; its
observations_fresh flag concerns QTR/opponent data, not an IMU generation.

An asynchronous nominal1 kHz sensor does not guarantee one new reading per
1 kHz controller tick. P Rev3.4 p17 gives gyro-reference initial tolerance
/-1% at25 C plus temperature variation; even ideal clocks have uncontrolled
relative phase. NO_NEW is not proof of sensor failure, yet mapping it directly
to the current imu_ok=false calibration sample rejects D024. Replaying the old
gyro with a fresh tick timestamp instead falsely adds an observation. Skipping
Lifecycle/Robot updates also breaks button/hold/warning processing.

Recommend a D051 adapter clarification before integration: introduce an explicit
gyro observation-presence state, defaulting to legacy PRESENT for existing
callers/tests. Keep stepping lifecycle/time/buttons/line/opponent services every
tick. PRESENT+valid adds one reading; PRESENT+invalid/transport failure rejects
as D024 requires; ABSENT/NO_NEW adds none and does not pretend to be an invalid
reading. Finish at the same CAL_END boundary, preserving minimum count/spread/
previous-bias rules and every locked safety test. Add independent tests for
no-new ticks and genuine invalid observations; do not silently edit core here.

Heading health must remain separate from last sample availability. No-new ticks
must not advance yaw by fabricated zero gyro or repeatedly integrate a cached
reading. An explicit numerical integration contract may interpolate only between
accepted observations over a qualified maximum interval, identifying that as
an approximation, not recovered missing samples. On an interval/generation gap
outside that policy, retain last yaw only diagnostically and invalidate heading;
do not silently resume a continuous healthy domain with the missing angle set
to zero. Reset-only heading invalidation is the simplest conservative candidate
until a documented recovery policy exists. B14's20 ms silence condition remains
a health/fault deadline, not permission to refresh cached data or a new evidence
timestamp. D059 still requires continuous provider yaw and logical GO origin.
An absence reaching B14's20 ms silence limit must become an explicit invalid/
fault observation, not remain benign NO_NEW indefinitely during calibration.

Immediate next work can implement/test checked setup, register profile, decode
and explicit sample/no-new/fault output without app/core integration. Before
claiming full B3, freeze acquisition/aggregate deadline, freshness/age semantics,
calibration-presence routing, robot mounting transform and integration-gap
policy. Physical identity/settings, >=800 Hz accepted new observations, sensor
settling/bias, clock/rails/bus timing and success/fault whole-loop WCET remain
unmeasured. No hardware action or new human gate is implied.
