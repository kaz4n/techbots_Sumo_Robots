# D120: actual B4 controller integration

Adopted under D051/D075, 2026-09-24. P2 B4 and R1/R4/R5/R6/R7 remain
the requirements. This is software preparation; no physical acceptance or upload.

## Fixed build identity

`SUMOX_B4_STAND` is a compiler-wide 0/1 flag, default 0. Value 1 is forbidden
with MATCH=1. All translation units use the same flags. Default/match routing,
existing enum values, existing locked tests and P3 DRIVE_TEST remain unchanged.
The profile is observable as `fsm::RobotResult::STAND_PROFILE`; only profile1
adds `stand_sequence::Report stand` and `bool stand_stopping` to RobotResult.
OPENER means the finite B4 script in this explicitly identified profile, never
a competition opener. Existing CSV layout remains unchanged: every future bench
export must carry its checked build receipt/profile sidecar and be labeled B4
bench evidence; OPENER alone cannot identify this profile.

## Real authority and routing

Use the actual Runtime/Transaction/Robot/Governor/MotorGate and actual application
receipts. Sources, setup grants, full qualified START-release hold, clocks,
calibration, freshness, fault handling, recorder and sole writer stay intact.
There is no forced initialization, synthetic sensor allowance or permission bit.
On actual GO, start the D119 sequence only when no escape is required. Its normal
route ignores opponent motion requests and never enters TRACK/ATTACK/DEFEND,
SEARCH, re-flank, stall or ordinary openers. Observation/final Fusion commitment
still run exactly once through the existing pipeline.

DRIVE requests use the additive conditional governor profile STAND, appended
after all old values: final electrical cap is STAND_DUTY, after compensation,
with normal slew. BRAKE is enabled zero duty on both sides; COAST inhibits both
sides because EN is shared. MotorGate M0 always applies disabled zero regardless
of the governed request; only controlled host fixtures use M1 in this scope.
No request or feedback claims actual wheel motion.

## Priority, terminal behavior and diagnostics

Run existing lifecycle and escape before routing the sequence. Qualified STOP,
missing/stale source, actual receipt or independent contract fault immediately
inhibits using the existing path. Cancel an active sequence with Reason::STOP;
this diagnostic means local safety cancellation, not necessarily a button.
Never overwrite a prior terminal reason. Before GO it remains NOT_STARTED.

While permission exists, an actual required/faulted edge takes priority over
sequence advancement, natural completion and a sequence gap fault. Cancel the
active sequence with EDGE, latch an owner edge interruption even when white at
GO prevented start, and run the unchanged escape planner/governor caps (these
may exceed STAND_DUTY). Its persistent/all-white/replan faults retain inhibited
EDGE_ESCAPE until reset unless explicit STOP or independent contract fault wins.
Do not automatically STOP a still active/faulted escape.

On successful escape exit, inhibit on that same observation, retain EDGE_ESCAPE
for that observation, and latch stand_stopping. On the next distinct admitted
Robot tick, request actual Lifecycle STOP before motion. Never resume/start the
sequence after an edge. Explicit STOP on an exit observation wins normally.

Otherwise advance D119 once at the real current time. Natural COMPLETE inhibits
on the same observation in OPENER and latches stand_stopping; the next distinct
tick requests actual Lifecycle STOP. A sequence FAULT similarly inhibits at once,
latches SCRIPT_RESULT and stand_stopping, and requests Lifecycle STOP next tick.
Existing SCRIPT_RESULT finalization publishes ui_state STOPPED on that first
fault observation; only natural COMPLETE retains OPENER until the next tick.
No timed future call, forged timestamp, second lifecycle evaluation or patched
MotorGate result is permitted. Logical STOP qualification occurs first, so STOP
wins a simultaneous natural terminal. An edge on the natural final boundary
interrupts before advancement. Terminal reason stays immutable afterward.

Duplicate Robot ticks retain cached values with all action pulses cleared.
Expose the actual helper report and pending STOP flag in fresh results; do not
turn a prior helper freshness pulse into a new one on escape/STOP observations.
stand_stopping remains latched until Robot reset after completion/fault/escape
exit; it need not be set for an earlier explicit STOP/source cancellation.
Robot::reset reconstructs the same immutable build profile and normal BOOT/start
sequence. D103 local service reset is unavailable in profile1: Transaction returns
false without mutation; Runtime never publishes pending/fresh/service_only even
when local_service_reset is supplied. Full motor reset remains the normal owner
operation; this profile has no automatic repeat.

## Additive helper cancellation

`bool Sequence::interrupt(Reason)` accepts only STOP/EDGE while DRIVE/BRAKE/COAST.
It immediately sets INTERRUPTED, the reason, zero duties, fresh=true and
phase_changed=true, without changing last_us. Before start, terminal state or
any other reason returns false and changes nothing, including pulses. This
owner action allows qualified safety cancellation without inventing a time.
Existing D119 start/step/duplicate behavior is unchanged.

## Wrapper, tooling and validation

Add bench/motor_direction using actual NativeSources, UnoQPort and Runtime, with
empty SetupGrants and no dump transport. Wrapper requires profile1/MATCH0/M0.
Only its literal checked compile-only route adds the compiler-wide flag to C/C++;
all old checked route flag strings remain unchanged. No upload allowlist entry,
run claim, native true grant, pin change or B7 full-reversal exception.

Independent public/spec-derived tests freeze before first implementation run.
Dedicated .cc host targets use profile1/M0 and profile1/M1 with actual callbacks;
existing targets remain profile0. Cover full hold and adjacent ticks, actual Gate
brake/coast/low-voltage limits, all phases, STOP, source/receipt faults, edge at GO
and completion, escape exit/fault, wrap, duplicates, service reset refusal and
default compatibility. New safety cases may be established in a new locked file;
no existing locked file is editable. Normal/sanitizer, script route refusals,
separate read-only review and checked target compilation are required. Default
loadable identity/fit and dedicated bench loader fit must be measured, not assumed.
