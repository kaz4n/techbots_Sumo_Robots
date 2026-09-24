# P3 DRIVE_TEST software contract — D123

Scope: P3_first_drive.md firmware preparation for 3.1, 3.5, 3.6 and 3.7,
BEHAVIOR B1/B2/B3/B4/B6/B8/B13. D122 authorizes software scheduling with physical
prerequisites assumed, not measured. D051 delegates these engineering choices.
No R1-R11, B16 value, wiring/source grant, existing locked test or motor-run
permission changes. Separate 3.3 stopping trials and 3.4 isolated turn trials
remain unfinished; this profile does not claim to provide them.

## Build and start

- Compiler-wide `SUMOX_P3_DRIVE_TEST` defaults 0, accepts only 0/1, rejects MATCH
  and simultaneous SUMOX_B4_STAND. All existing targets remain profile0.
- `fsm::RobotResult::DRIVE_TEST_PROFILE` reports immutable build identity.
- In profile1, a new START release can enter the actual Lifecycle countdown only
  from initialized, fault-free IDLE with the existing service menu's DRIVE_TEST
  item selected, classified line readiness, and its genuine button qualification.
  Match selections and other services cannot start motion. Selection is by existing
  local MODE gestures only. The release is not replayed or synthesized.
- The unchanged full 5000+100 ms hold starts after release debounce. MODE cancels,
  boot-held START is ignored, STOP/source/receipt faults inhibit as before.
- Menu's DRIVE_TEST intent is available only in profile1; intent itself confers
  no authority. It accompanies the accepted release on that observation. Existing
  service-only post-STOP projection remains permanently inhibited and cannot rearm.
- Profile1 UI shows D without the unavailable cross for selected/active DRIVE_TEST.
  An explicit service_unavailable flag still shows D+cross in the service menu;
  default profile0 presentation and all battery/fault overlays are unchanged.

## Motion and safety

- After GO and before any non-edge motion, route to State::DRIVE_TEST and the real
  B8 Search helper. Skip opener, normal opponent arbitration, attack, defend,
  re-flank and stall execution. No contact latch, ALL_IN, CONTACT/STALL/REFLANK event.
- Search receives a zero interruption mask in this profile only. Actual raw and
  filtered opponent evidence, memory, stuck faults, logged masks and B4 pushed-out
  context remain real. Opponents cannot repeatedly restart or stop the scan.
- Retain B8 memory turn, full directed scan, timed fallback, inward-heading
  advance, alternating cycles and exact existing Governor profiles. Forward
  search retains final SEARCH_DUTY_MAX=0.30, even at low voltage; pivots retain
  TURN_DUTY and edges their approved caps. There is no global 0.30 edge/pivot cap.
- Existing runEscape precedes this route. White at GO, persistent/new white,
  replan limits, three/all-white faults and STOP retain existing behavior.
  Successful escape exit selects DRIVE_TEST and brakes to zero on that observation;
  next distinct eligible tick starts a fresh Search, using retained inward/history.
- Allow energized State::DRIVE_TEST only in profile1 in both Robot's final moving
  classification and MotorGate's state validation. All actual independent Gate
  hold, enable, duty, clock, token, source, PWM and receipt checks remain intact.
  Profile0 continues to reject energized DRIVE_TEST exactly as its locked tests.
- Preserve duplicate suppression, immediate fault inhibition, reset semantics,
  real receipt FIRST_NONZERO evidence and bounded frame/event recording. Build
  identity accompanies any future evidence; existing running_mode is retained
  metadata, not a statement that an opener ran. State identifies DRIVE_TEST.

## Staging and validation

`bench/drive_test/drive_test.ino` uses actual NativeSources, UnoQPort and Runtime
with empty SetupGrants, no remote command path or synthetic source values.
Checked tooling admits only default startup and exact compiler C/C++ flags
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_DRIVE_TEST=1`, compile-only, no upload key.
Keep the default app and B4 profile flags/policy intact.

Independent tests derive from this contract/public headers/fixtures before first
implementation execution. Dedicated profile1 M0/M1 .cc targets exercise actual
Transaction/MotorGate callbacks: menu admission, exact hold/wrap/cancellation,
every opponent mask/no combat, scan continuity and forward cap at low voltage,
edge at GO and after motion, persistent/all-white/escape exit, STOP/source/receipt
fault, duplicates and actual applied evidence. M0 never writes nonzero/EN high.
New locked safety tests are frozen; all old locked files stay byte-identical.
Normal and sanitizer tests, tooling negative cases, target compile/conditional
loader accounting if connected, and separate read-only review precede completion.
No host/mock result proves physical P3 acceptance or on-robot WCET.
