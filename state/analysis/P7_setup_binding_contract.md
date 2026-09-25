# D180 configurable main-app setup binding

25 September2026, under D051 and the user's software-first continuation. A fresh
read-only audit identified the literal SetupGrants{} in app.ino as a real release
integration gap (P2.1, P7.2, P7_software_map item2). D096 requires unconfirmed
defaults, not a permanently unconfigurable caller. Prepare that binding now.

## Scope and public interface

Add src/app/configured_setup.h with pure C++17
`constexpr app::SetupGrants configuredSetupGrants()`; include runtime.h and
config.h. Return the existing SetupGrants type with exact independent mappings
below. No I/O, clocks, allocation, global mutable state, inference or new owner.
The function must be usable in a constant expression. Wire only the main
src/app/app.ino setup call to `runtime.begin(app::configuredSetupGrants())`.
No other entry/sketch or Runtime/HAL/core implementation changes.

All new values live in namespace config in src/config.h. Boolean declarations
are uint32_t values, default0, with compile-time rejection of values above1.
These are dimensionless declared evidence inputs, never proof of verification.

| Config constant | Existing SetupGrants destination |
|---|---|
| APP_GRANT_OPPONENTS | opponents |
| APP_GRANT_ADC_PAIR | adc_pair |
| APP_GRANT_QTR_EXCLUSIVE_PADS | qtr_exclusive_pads |
| APP_GRANT_IMU_ENABLED | imu_enabled |
| APP_GRANT_IMU_POWER_CONFIRMED | imu_power_confirmed |
| APP_GRANT_IMU_MOUNTING_CONFIRMED | mounting.confirmed |
| APP_GRANT_DEFAULT_LINE_THRESHOLDS | default_line_thresholds_confirmed |
| APP_GRANT_MATRIX_ENABLED | matrix_enabled |
| APP_GRANT_MATRIX_NORMAL_STARTUP | matrix.normal_startup |
| APP_GRANT_MATRIX_EXCLUSIVE_OWNER | matrix.exclusive_boot_owner |
| APP_GRANT_DUMP_ENABLED | dump_enabled |
| APP_GRANT_DUMP_SETUP_PHASE | dump.setup_phase |
| APP_GRANT_DUMP_EXCLUSIVE_UART | dump.exclusive_uart |
| APP_GRANT_DUMP_READY_PIN_OWNED | dump.ready_pin_owned |
| APP_GRANT_DUMP_FRAMING_CLEAN | dump.framing_clean |
| APP_GRANT_LOCAL_SERVICE_RESET | local_service_reset |
| APP_GRANT_CALIBRATION_OUTPUT | calibration_output_enabled |

APP_IMU_BODY_AXIS is int32_t[3], default{0,0,0}, mapped element-for-element to
mounting.body_axis. Reject elements outside[-3,3] at compile time before int8
conversion. Existing Estimator retains proper signed-permutation/confirmation
validation; this binding does not relabel an invalid or unconfirmed mounting.
APP_DUMP_ORIGIN is uint32_t, default0;0=UNKNOWN,1=SYNTHETIC,2=HARDWARE_REPORTED
mapped to existing Origin. Reject other values at compile time. Origin does
not imply any dump permission or observed provenance.

No grant derives from MATCH, MOTORS_ALLOWED, another grant, a valid axis map,
an origin value or any measured-looking config constant. Preserve independent
false values even in inconsistent combinations; existing consumers reject or
ignore them under their established contracts. No cross-field auto-enabling.

## Evidence and permission boundary

Every shipped grant remains0, mounting allzero and originUNKNOWN. Preserve all
existing constants/pins/button windows, build defaults, Runtime/Gate/hold/edge
checks, protected tests and per-run upload authorization. Setting a declaration
later requires its actual acceptance/evidence and approved wiring/config scope;
it cannot substitute for physical verification, current UART preparation, a
human gate or fresh STAND/RING permission. No values are enabled in this task.

Other bench entries retain their explicit empty-grant guards and established
tests. Their future deployment qualification is separate; do not silently turn
an inert measurement sketch into a hardware-granted one. The already compiled
D172 diagnostic and D173-D179 pins/scopes remain historical exact inputs; do
not repin/rebuild them because main-app source gains this disabled binding.

## Host acceptance

Separate spec-only author freezes new tests before first execution. Use actual
public SetupGrants and the new header, small RAM fixtures and serial C++17 builds:

- Constant-expression default equals every field of SetupGrants{}, including
  nested fields and all axes; all four MATCH/MOTORS_ALLOWED combinations preserve
  these defaults and do not grant a source.
- Independently exercise each flag1 with all other declarations0; every field
  must match the table with no cross-field inference. Mixed false/true combinations
  and signed axis mappings/origin values preserve exact declarations.
- Each nonbinary flag, every out-of-range axis position and invalid origin fail
  compilation; unconfirmed/malformed in-range mounting passes unchanged to the
  existing consumer contract instead of being silently repaired.
- Execute the actual .ino setup/loop text with controlled typed native/Runtime
  substitutes to verify the configured builder result reaches begin exactly once;
  default and synthetic nonzero fixtures. Keep builder tests against real types.
- Verify existing config values, bench entries and locked tests remain unchanged;
  run relevant existing tooling checks. No native/target execution or new SDK.

Separate fresh-context same-model source/test/evidence review required. New code
is HOST-TESTED only until actual target compilation and physical qualification.
Update the runbook's current-source description and resume state truthfully;
do not fill physical fields or claim the robot can operate from these defaults.
