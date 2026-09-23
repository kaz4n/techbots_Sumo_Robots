# Next B6 implementation after D086 closes

2026-09-23 Asia/Dubai. Read-only source assessment during ADC pair validation;
this note adopts no new behavior, thresholds, timing, wiring or phase approval.

Implement the missing button evidence boundary next, then its actual integration
with the existing logical countdown/menu/STOP services. D086 raw conversion is
not a valid ButtonLevel. Do not duplicate the existing20ms debounce or shift
D019/D035/D058 anchors into a second HAL debouncer.

Current core::ButtonLevel has only NONE/START/MODE/BOTH (types.h). RobotInput
fsm.h carries only that level; countdown::Buttons arms on NONE and can generate
START release after a qualified NONE transition. StopHold's elapsed-time route
currently assumes each logical observation is current. Menu has its own NONE
arming interval. Therefore passing raw failures as NONE can synthesize a start;
replaying a cached level can qualify an unobserved continuous hold. A source
presence/identity/time admission must sit before all three consumers, with an
explicit policy for gaps, invalid/ambiguous classifications and reset recovery.
Inspect countdown.cpp Buttons/StopHold/Controller/Menu and Robot routing, keeping
legacy host API compatibility and all locked assertions unchanged.

HARDWARE5.6 physically has only three nominal levels: NONE3.3V, MODE1.65V,
START or BOTH0V. This is an electrical identity, not an unknown threshold that
software can infer. Keep SC-A open and prevent any nominal low-voltage classifier
from asserting a unique START/BOTH. D051 permits choosing a conservative software
policy and evidence contract without another question, but cannot verify a fourth
voltage or authorize an undocumented wiring change. A configurable explicit raw
window classifier may preserve ambiguous/unknown instead of synthesizing one
of those states. No measured noise/ranges are presently available; do not seed
unverified windows as physically qualified defaults.

Freeze public evidence/gap/replay/age/fault semantics and configuration before
independent test authoring, then implement actual decoder/adapter/controller
routing in that same task. Regression cases must include no release on missing
or invalid data, boot-held buttons, finite fresh-only debounce/STOP/menu timing,
sequence and micros wrap, duplicates, conflicting identity, expiry/recovery and
MotorGate inhibition. Keep decision time and ADC start/completion/source time
separate. Source acquisition validity is not physical circuit acceptance.

P2 B6 also needs the104-byte matrix renderer and a separately source-verified
bounded native display adapter. Existing P0 Arduino_LED_Matrix0.1.3/Immediate
restrictions and refresh interrupt cost still apply. Neither stock blocking
text routines nor Bridge should enter the control path. Do not replace actual
input development with another scaffold or documentation-only milestone.

App scheduler, ADC cadence, battery freshness integration, whole tick800us,
SC-AJ/F091 and all physical/human gates remain pending. Two ADC calls at100us
each plus IMU600 and motor150 already total950us in acceptance ceilings, before
other work; this note makes no WCET claim. No hardware connection request is
needed to finish eligible software work under D051/D075.
