# D126 finite P3 3.3 stopping trial

D051/D122 authorize this software preparation. Preserve all existing locked
oracles, B16 values, source/pin grants and R1-R11. This prepares one trial; it
does not measure translation, approve a search cap, or authorize motors.

## Profile and admission

New compiler-wide SUMOX_P3_STOP_TRIAL defaults0, accepts0/1, excludes MATCH,
SUMOX_B4_STAND, SUMOX_P3_DRIVE_TEST and SUMOX_P3_TURN_TRIAL. New config-only
STOP_TRIAL_DUTY defaults0.30 and accepts exactly0.30/0.40/0.50/0.60/0.70.
STOP_TRIAL_APPROACH_MS=1000 and STOP_TRIAL_BRAKE_MS=500 are finite development
limits, not measured safe distances/settling times. Existing SEARCH_DUTY_MAX
remains0.30. No remote or local runtime duty selector is added.

Use the same actual selected DRIVE_TEST service, genuine START release/full hold,
classified-line/neutral readiness, source admission, UI availability and real
MotorGate state permission as D125. Match selections/other services cannot start.
Skip every combat/opener/Search/stall executor; preserve real perception and logs.

## One bounded approach and actual escape

Actual runEscape runs first. With GO/permission and no escape, start actual
motion::Straight with current match heading, configured positive base and1000ms.
Start/step uses real imu_ok unchanged: healthy heading correction follows D022;
actual unavailable IMU produces existing equal requests/fallback, and recovery
resumes that primitive's captured reference. State remains DRIVE_TEST while
approaching/braking. No fabricated sensor health or motion evidence.

All approach requests use new conditional Governor::Profile::STOP_TRIAL_FORWARD:
its final electrical cap is STOP_TRIAL_DUTY after voltage compensation and before
the existing acceleration slew. Cap reductions/braking remain immediate. This
does not relabel ordinary straight motion as an opener/edge/pivot or raise the
production search cap. Both corrected wheel requests remain nonnegative; their
actual applied values are separately recorded and need not equal the selected
duty during slew, voltage compensation or heading correction.

If Straight reports DONE without edge, enter BRAKE at that observed timestamp,
mark approach_finished, retain DONE, and label reason NO_EDGE_TIMEOUT. Start the
actual Brake primitive for the full500ms from this observation; delayed calls do
not backdate completion or skip this interval. BRAKE requests zero immediately,
retaining requested enable while permitted (physicalM1high/M0low). At actual
Brake DONE, phase COMPLETE immediately inhibits; next distinct Lifecycle tick
receives STOP. Timeout/COMPLETE is not a valid stopping-distance result.

STOP/source/receipt faults preempt the approach. Edge at GO prevents start and
sets the owner edge flag while report remains NOT_STARTED. Edge during APPROACH
or BRAKE permanently interrupts the trial and executes the unchanged complete
escape; do not latch owner STOP until successful escape exit. Edge wins an
approach/brake deadline tie. Successful escape exit immediately inhibits, then
Lifecycle STOP next distinct tick. All-white/recovery faults retain existing
reset-only inhibited EDGE_ESCAPE behavior. No trial resumes or repeats.

Actual Straight/Brake INVALID or failed start faults SCRIPT_RESULT/SCRIPT_START,
publishes FAULT/INVALID_MOTION, zeros demands and latches owner stopping. Other
owner faults publish STOP interruption of an active trial and immediately inhibit.
Report terminal states stay retained. A report's finished flag ends the trial
request, not necessarily its ongoing edge-escape motion. All owner publication,
duplicate pulses, exhaust inhibition and applied receipts retain existing rules.

Conditional RobotResult::STOP_TRIAL_PROFILE, stop_trial report, stop_trial_stopping
and stop_trial_edge_interrupted expose identity/history. Report timestamps use
boolean presence flags so timestamp0 remains valid. approach_finished marks only
actual Straight DONE; interruptions retain its previous status/fallback and any
already-observed approach completion. Duty fields are current pre-Governor trial
requests; terminal/brake fields are zero. No new frame/event wire fields are added.
Profile-only storage keeps default/B4/D123/D125 layouts unchanged.

D103 post-STOP service-only reconstruction may clear the trial report; recorder
frames/events remain, but do not serialize this report. Native Gate stays STOPPED,
source projection inhibits countdown, and DRIVE_TEST service stays unavailable.

## Measurements and evidence

SC-AN disposition: retain the original border-to-robot-front at-rest measurement
with identified orientation/rest observation. Supplement it with independently
measured maximum outward excursion from the same first-white reference/direction
used for R_room. No inferred conversion offset or duty-to-distance estimate.
Only compatible measured peak/R_room data can support a conservative70percent
comparison; record rest separately. No-edge timeouts are excluded from cap advice.
Actual3runs/duty, voltage, run/build identity and evidence-backed tuning approval
remain pending. The fixed approach timeout does not protect against every failed
edge sensor and is not evidence of a safe starting position or stopping distance.

## Validation and native route

bench/stopping_distance uses actual NativeSources/UnoQPort/Runtime with empty
SetupGrants. Checked route admits default-startup compile-only and exact C/C++
flags -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_STOP_TRIAL=1, no upload key.
Independent public-header/spec tests freeze before execution: actual local/full
hold/wrap, all5duty configs/low voltage/correction/slew, finite timeout/observed
brake/inhibit/STOP, actualM0/M1Gate writes and receipts,128opponentmasks/no combat,
edgeGO/approach/brake/deadline/fullescape/persistentfaults, actualunavailableIMU,
source/receipt faults/duplicates, configuredRuntime readiness and service-only
inhibition. Preserve37oldlocked files. Run normal/sanitizers, original profile
regressions, tooling negative cases, exact target/loader checks when connected
and independent review. No synthetic test establishes physical acceptance/WCET.
