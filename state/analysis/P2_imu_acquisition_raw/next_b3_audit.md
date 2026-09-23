# Next B3 bias, presence and continuous-heading audit

2026-09-23 Asia/Dubai. Read-only followup while D081 sources remain frozen. This
report proposes a later contract; it does not select mounting, change D024/D059,
implement an adapter, or qualify physical heading. No code/config/test/core/app
file was edited during this audit.

## Current facts and integration gaps

1. **New sensor data now has an explicit boundary.**
   `src/hal/imu_acquisition.h:9` distinguishes NOT_READY/NO_NEW/OBSERVATION/FAULT;
   `:16` excludes cached payload; `:20` counts accepted observations, not sensor
   generations; `:24` exposes observed completion gaps without approving heading
   continuity. The decoder remains sensor coordinates (`src/hal/imu.h:62`).
   D081 does not produce robot yaw, calibrated gyro, body acceleration or imu_ok.

2. **Calibration cannot represent benign absence today.**
   `src/core/countdown.h:108` ServiceSample has one tick, raw gyro and imu_ok;
   `src/core/countdown.cpp:148` rejects any imu_ok=false/nonfinite window reading.
   `:182` de-duplicates equal service timestamps only; a later tick with repeated
   payload counts again. `:188` finishes at CAL_END before reading that endpoint;
   `:199` still handles warning/snapshot windows. D024
   (`state/DECISIONS.md:160`) requires [1.5s,4.5s), min2, max-min spread, any invalid
   reading rejection and prior-bias retention. NO_NEW must add no reading while
   the service clock/buttons/line/opponent handling continue. Suppressing the
   whole Lifecycle step is not a valid adapter (`countdown.cpp:216`).

3. **One shared imu_ok couples three different consumers.**
   `src/core/fsm.h:385` RobotInput has raw yaw, raw gyro, accel and one imu_ok;
   `:388` observations_fresh explicitly belongs to four QTR/seven opponents.
   `src/core/fsm_robot.cpp:270` forwards the same imu_ok to calibration;
   `:288` passes it to HeadingReference; `:221` sends it to Fusion's yaw/impact
   consumers. NO_NEW mapped to imu_ok=false permanently starts Turn fallback
   (`src/core/motion.cpp:97`). NO_NEW mapped to true with cached values records
   another healthy yaw timestamp (`src/core/fsm.cpp:571`) and reuses acceleration
   as current impact evidence (`src/core/opp_fusion.cpp:366`). Merely adding a
   calibration presence bit therefore does not complete safe Robot integration.
   Setting observations_fresh=false instead latches STALE_SENSORS
   (`src/core/fsm_robot.cpp:207`) and incorrectly drops QTR/opponent acquisition.

4. **The bias return path exists, but the physical consumer does not.**
   `src/core/fsm_robot.cpp:283` emits bias_update_requested/accepted_bias_dps once
   after accepted calibration; rejected calibration retains Services' prior bias
   (`countdown.cpp:164`). Robot consumes previous_bias_dps only on release
   (`countdown.cpp:225`). Lifecycle explicitly says accepted bias affects later
   integration increments only (`countdown.h:181`). Frames deliberately contain
   raw pre-bias rate (`fsm_robot.cpp:820`); an adapter must retain both raw and
   corrected rate rather than silently changing the recorder field's meaning.

5. **Continuous yaw and GO behavior are already decided.**
   `src/core/fsm.h:35` requires continuous unreset provider yaw. D059
   (`state/DECISIONS.md:581`) makes GO only a logical match origin and forbids
   resetting provider/Fusion history. Missing data preserves bounded fallback;
   healthy nonfinite yaw creates a reset-only coordinate fault. A new HAL must
   never reset integrated yaw when heading_reset_requested pulses. The existing
   HeadingReference stores last healthy observation time; retained heading must
   not acquire a new measurement timestamp on an absent tick.

6. **Mounting and numerical integration remain unselected.**
   `docs/HARDWARE.md:107` says centered/flat/rigid but supplies no sensor-axis to
   robot-axis correspondence or yaw sign. `docs/BEHAVIOR.md:14` requires positive
   clockwise yaw. `state/FACTS.md:286` retains physical axes/yaw as pending.
   No signed permutation or gyro-Z polarity can be inferred from Qwiic or the
   package alone. `state/analysis/P2_mpu6050_sample_audit.md:212` already separates
   observation absence from heading availability and calls for an explicit gap
   policy. The20ms silence deadline is not an integration-gap allowance.

## Smallest next implementation scope to freeze

Implement one concrete C++17 HAL estimator consuming the existing qualified
`imu::Sample`; keep Acquirer ownership and all native transactions unchanged.
It should explicitly map sensor axes, retain raw mapped rate for calibration,
apply accepted bias to subsequent increments, integrate an unwrapped yaw and
surface presence/time/continuity metadata separately. It needs no callbacks,
clock, new bus abstraction, allocation, fusion library or application scheduler.
Host tests can use supplied arbitrary maps without choosing the robot's physical
map. A missing/unconfirmed map must not yield qualified robot-coordinate output.

Freeze these engineering choices before coding:

- Body-axis conventions, a validated signed permutation, how mounting confirmation
  gates qualification, and a reset-only prohibition on changing map mid-history.
  No physical map is selected by this report. Acceleration gravity removal/tilt
  compensation is outside this minimal planar estimator.
- Observation timestamp policy. Completion timestamps are available but are bus
  observations, not physical sample times; choosing them for integration is an
  explicit approximation. Never substitute current loop time on NO_NEW.
- Numerical rule and maximum permitted interval, exact equality behavior, handling
  of same-time distinct observations, sequence duplicates/skips/wrap, gyro rails,
  nonfinite/out-of-range results and reset-only continuity loss. A conservative
  candidate is trapezoidal integration only between ordered accepted endpoints,
  with no NO_NEW integration, no extrapolation and no recovery across a rejected
  gap. A sequence detects dropped accepted observations, not every coalesced
  internal sensor generation. No interval constant is selected here.
- Bias units/sign and update boundary. Keep raw mapped endpoints; stage finite
  accepted bias for a subsequent integration increment without rewriting history.
  Decide initial-bias provenance and rail eligibility without inventing a new
  motor veto on calibration rejection. Do not reimplement D024 averaging in HAL.
- Core adapter semantics. Minimal calibration extension is an additive observation-
  presence field defaulting to PRESENT for old callers: ABSENT/NO_NEW skips only
  observeCalibration; PRESENT invalid/FAULT still rejects. Broader Robot routing
  must separately decide heading availability/age and current acceleration
  presence. In particular, do not mark cached heading/acceleration as a fresh
  combined imu_ok sample to avoid transient fallback.

Candidate public shape (proposal only; types/units must be frozen by the next ADR):

```cpp
struct AxisBinding { SensorAxis axis; int8_t sign; };
struct Mounting { AxisBinding body[3]; bool confirmed; };
enum class Presence { ABSENT, PRESENT, INVALID };
struct Estimate {
    Presence gyro_observation;
    bool heading_valid;       // distinct from a new gyro observation
    bool heading_updated;
    float raw_gyro_z_dps;     // mapped but before bias
    float gyro_z_dps;         // after accepted bias
    float ax_g, ay_g;
    double continuous_yaw_deg;
    uint32_t observation_us, sequence, gap_us;
    EstimateFault fault;
};
class Estimator {
public:
    bool begin(const Mounting&, float initial_bias_dps);
    Estimate observe(const Sample&); // no clock or I/O; no GO/reset argument
    bool applyBias(float accepted_bias_dps); // future increments only
};
```

The exact absent-result payload/provenance and heading_valid lifetime still need
selection. Keeping a last yaw diagnostic is permitted; calling it a new measured
coordinate or silently refreshing its age is not. An adapter can later compose
this concrete estimator with Acquirer without exposing either private Bus.

Independent next tests should cover calibration absence versus actual invalidity,
unchanged service boundary/warning/STOP behavior, every permitted map/sign, bias
update continuity, sequence/time wrap/duplicates/gaps, rails and yaw overflow,
no integration on NO_NEW, fault latching and GO retaining continuous provider yaw.
Existing locked assertions remain untouched. This remains HAL software scope;
`src/app/app.ino:21` has no scheduler and is still inert. B3's drift/hand-rotation
and timing criteria (`docs/prompts/P2_hal_bench.md:13`) remain physical work, along
with SC-AJ clock qualification and the full800us tick measurement.
