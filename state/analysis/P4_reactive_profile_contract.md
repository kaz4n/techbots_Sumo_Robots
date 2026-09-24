# D128: reactive P4 build without openers

Software scheduling follows the user's explicit direction to complete software
and defer hardware testing, D051's delegated engineering choices and D122's
assumed physical prerequisites. D123-D127 complete the identified P3 software
preparation. Active software now advances to P4; no P3 gate, actual acceptance,
tuning approval or motor-run permission is authored or inferred.

## Build identity and local admission

Add compiler-wide SUMOX_P4_REACTIVE, default 0, accepting only 0/1. Profile 1
excludes MATCH, SUMOX_B4_STAND and all three SUMOX_P3_* profiles. Existing
profiles and established tests remain unchanged. RobotResult exposes a static
REACTIVE_PROFILE boolean; do not add per-instance storage for profile identity.

Use the existing ordinary local match-menu START admission, initialization,
classified-line/source readiness, real release debounce and full 5000+100 ms
hold. Service selections cannot start this profile. Boot-held START, MODE
cancellation, STOP, source/receipt faults and D103 service-only inhibition stay
unchanged. No new service, UI control, pin/grant or remote path is introduced.
All six selected match modes execute the same reactive behavior in this build;
running_mode remains selection metadata, not evidence that an opener executed.

## Literal SEARCH at GO, then existing reactive behavior

Keep permission/fault/STOP and actual runEscape handling ahead of this branch.
On a permitted non-edge GO, cancel existing motion, set normal_active=true,
select State::SEARCH, call actual runSearch() with the real current effective
opponent mask, and return from routing for that observation. No opener starts
or runs anywhere in profile1, including later observations.

An effective target at GO produces the existing Search PERCEPTION/zero-duty
result, while visible state remains SEARCH for that observation. Zero duty
does not require EN low after a valid full hold. A merely new raw bit is not
substituted for a confirmed effective target. Empty GO begins genuine Search;
preserve its captured heading, timer and phase into the next distinct tick.

The next distinct eligible observation uses unchanged NormalPerception and
executors. The current entry observation starts centered qualification at one;
ATTACK requires the third centered post-GO observation. Preserve actual bearing
memory, Search, TRACK steering, centered contact lifetime, final electrical
Governor caps/slew, target-loss immediate braking, DEFEND, stall/re-flank and
ALL_IN safety behavior. checkStall remains enabled. No contact, sensor health,
time or applied receipt is fabricated.

Edges at GO or later retain full priority, escape scripts/replans and reset-only
faults. Preserve current successful-escape exit: select by current perception,
brake for that observation, execute no earlier than the next tick. Force SEARCH
only for a non-edge GO. Duplicate calls do not re-enter or advance motion.
All actual Transaction/MotorGate hold, source, PWM and receipt checks remain.
Profile0 keeps its existing opener behavior byte-for-byte where practical.

## Inert staging and verification

New bench/reactive_test wrapper uses the actual NativeSources/UnoQPort/Runtime,
empty SetupGrants and compile guards for profile1/MATCH0/MOTORS_ALLOWED0 and
absence of every other special profile. Default startup only. The checked build
route admits exact C/C++ flags
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1`, compile-only; no upload key.
No generic motor-capable upload route is added.

Independent spec/public-header oracles freeze before execution. Add profile M0
and M1 host targets; preserve all 38 established locked files. Cover all six
modes, full hold/wrap and service rejection, effective targets at GO, empty-GO
Search continuity, next-tick front/side arbitration and three-tick centering,
actual Gate writes/quantization, low-voltage/contact caps, loss braking, stall/
re-flank, edges/faults/STOP/duplicates and actual configured Runtime service-only
inhibition. Run normal/sanitizers, existing-profile regressions, controlled
tool-policy negatives, target compile/loader accounting and separate review.

This slice implements P4 admission/routing only. SC-AO's exact target-loss/abort
evidence is the next bounded task; 25 Hz frames are not timing proof. Physical
P4.1-4.7, evidence-backed tuning and a real human P4 gate remain pending. Keep
EDGE_PUSH_THROUGH_MS at its disabled default and all other B16 values unchanged.
