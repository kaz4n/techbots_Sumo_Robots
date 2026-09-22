# P1 B3 countdown-services independent test authorship

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016; no phase gate.
Objective: independently specify D-024 service sampling/retention and prove the
bounded logical composition cannot bypass D-019's qualified-release hold.

Owned files:
- tests/locked/test_countdown_services.cpp: 27 new doctest cases.
- state/analysis/P1_countdown_services_test_author.md: this report.

Sources: AGENTS.md, test-author role, BEHAVIOR.md B3, accepted D-024,
countdown.h Services/ServiceSample/ServiceResult and Controller contracts,
config.h constants committed under 5bfcf70, and governor.h.
No src/core/*.cpp was read. No preexisting locked test, header or configuration
was edited. All expectations were written before any service implementation run.

Coverage: [1.5,4.5) s exact endpoints and adjacent microsecond/millisecond calls;
arithmetic mean and max-minus-min; exactly 2 dps spread versus next float above;
minimum two valid samples; unavailable/nonfinite/missing readings; retained
previous bias; duplicate timestamp suppression; no fabricated gap samples;
one-time late finalization; cancel/reset/restart; final-second warning latching;
final-300-ms latest low-seven-bit snapshot including zero; GO exclusion/freeze;
ordinary time wrap and late calls spanning a full start-time counter cycle.

The logical harness composes the real Controller, Services and Governor at
1 kHz for accepted/rejected calibration. It starts Services only from the
qualified release pulse, passes Controller permission alone to governor inhibit,
and explicitly calls Services.cancel on MODE/STOP. Delayed qualification and
wrap cases verify no backdating or early motion. Cancellation remains caller
wiring; Services has no implicit Controller connection or motor authorization.

Validation at handoff: 27 test cases counted; no whitespace errors reported.
All assertions use CHECK/CHECK_FALSE for the no-exceptions build. Coordinator
owns the shared compile, normal and sanitizer runs; this author ran no build.
Earlier independent motion/codec tests passed in the coordinator's 155-case
P1_motion_codec_cases.txt receipt after the CAPTURE-only syntax correction.

Ambiguities: none requiring an invented behavior in this bounded contract.
Duplicate timestamps are not observations, including a changed/invalid duplicate.
Limits: no ADC/button electrical proof, sample freshness, IMU calibration on
hardware, UI icon/matrix check, MotorGate proof, sensor timing or physical run.
No recorder storage or FSM behavior is inferred from these component tests.
Next action: coordinator runs the unchanged suite, resolves implementation
failures against the committed contract and records final evidence in state/.
