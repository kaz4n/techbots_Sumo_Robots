# D087: explicit A1 button evidence through existing logical services

Selected under D051/D075, 2026-09-23 Asia/Dubai. Software development policy;
no measured ADC windows, circuit change, physical acceptance or phase pass.
Public interfaces: types.h ButtonEvidence, countdown.h ButtonTiming/stepObserved,
fsm.h RobotInput.buttons/RobotResult diagnostics, hal/ui.h decoder/adapter.
Preserve every established test and all legacy API behavior.

## Decoder and thin adapter

Config holds four inclusive count windows in NONE,START,MODE,BOTH order. Values
are 14-bit raw ADC counts; low<=high<=16383 and CONFIGURED in {0,1}. Production
CONFIGURED=0 and all windows0: deliberately no electrically qualified defaults.
BUTTON_SAMPLE_MAX_AGE_US=5000 is a development continuity/age ceiling (five default
ticks), not measured cadence. Config validation enforces 0<age<2^31 and age>=100.
A synthetic configured profile used in tests is not a wiring recommendation.

Canonical default ButtonSample (NOT_INITIALIZED, NOT_ATTEMPTED, invalid, all numeric
fields zero) yields ABSENT evidence, explicit=true, contract_valid=true. Other
records always yield explicit evidence. Valid requires status OK, valid=true,
shutdown NOT_ATTEMPTED, raw<=16383 and unsigned conversion duration<existing100us
VBAT_ADC_CONVERSION_US. Invalid status/shutdown enums, valid/status disagreement,
OK with invalid shape, or malformed config yield INVALID/contract_valid=false.
Known non-OK provider faults are INVALID/contract_valid=true (valid must befalse);
their shutdown can be any known value, including UNCONFIRMED. NOT_ENABLED is a
failure, never an absent reading. A valid ADC record with configuration off yields
UNCONFIGURED; zero matches UNKNOWN; multiple matches AMBIGUOUS; these all produce
INVALID presence, no accepted logical level. Exactly one match yields VALID,
with its level/raw/sequence/start/completion preserved. candidate_mask reports
all matching windows. No priority resolves overlapping windows. Failure evidence
has level NONE (not a valid NONE observation); presence is authoritative.
applyButtons changes only RobotInput.buttons and returns the qualification.
No clock, I/O, allocation, debounce or second ADC owner in ui.cpp.

HARDWARE5.6 still describes START and BOTH at the same nominal voltage. SC-A is
open: no classifier can manufacture a fourth distinguishable electrical state.

## Robot admission and continuity

First step selects legacy (explicit_values=false) or explicit mode until reset.
Mode mixing latches BUTTON_CONTRACT=512. Legacy behavior remains byte-for-byte
compatible at the API level. Explicit INVALID, invalid enum/shape/contract,
noncanonical ABSENT, or unconfigured decoding latches this same reset-only fault,
which immediately inhibits output through the existing STOP/fault path.

ABSENT means no new scheduled observation, never release. Before initialization,
ABSENT without history may remain BOOT. initialization_complete requires current
valid bounded history; once initialized, missing history faults. Valid evidence
requires level0..3, raw<=16383, duration<100us, start age<=5000 and nonfuture
completion (modular forward checks use half range). First valid sequence may be0.
Subsequent distinct evidence requires sequence delta in (0,2^31), completion
delta in (0,2^31), start not before previous completion (equality allowed), and
start-to-start gap<=5000. Exactly identical replay (including all data/identity)
is no-new and never renews age. Same sequence with changed fields faults.
A fresh record can replace history before expiry evaluation only if these source
continuity checks pass and the decision delta since the previous accepted step
is <=5000; otherwise an expired history cannot revive. Decision delta>=2^31
faults explicit admission. Accumulate/saturate age on distinct decision ticks so
cached data cannot revive after full micros wrap. On ABSENT/replay age>5000 faults;
equality is usable. No automatic recovery: Robot.reset clears admission state.

Diagnostics: button_available means bounded valid history and no button fault;
button_updated pulses for distinct accepted observations; button_level is last
accepted level; button_source_us is earliest acquisition/start time;
button_age_us is accumulated source age; button_sequence retains identity.
Immediate duplicate Robot decision time clears updated/actions and ignores changed
input exactly as existing Robot semantics. Final unrelated faults still inhibit.

After boot/reset, START qualification requires fresh NONE observations whose
completion times span BTN_DEBOUNCE_MS20. Any non-NONE before this qualification
restarts neutral arming. Until armed, Buttons is reset/suppressed; StopHold still
sees fresh BOTH, including at boot. Once armed it remains so until fault/reset;
existing Buttons handles later contamination. No duplicate HAL debounce.

## Source time versus decision time

stepObserved uses ButtonTiming observation_us=actual completion, fresh only on a
new admitted observation, restart on initial explicit entry/fault, start_ready
only after neutral qualification. restart clears unfinished gestures; never a
latched STOP, Gate timer, or menu selection. No-new calls do NOT cancel a gesture
within the accepted continuity limit, and do NOT sample or advance its qualifier.
New equal levels qualify sampled stability across bounded source gaps; this is
not proof of a physically continuous waveform. Missing beyond the limit faults.

Buttons uses source spans for debounce. Its edge timestamp is first source;
qualified timestamp is actual decision tick. Controller Gate always advances at
decision time and anchors the complete5100ms hold at completed release debounce,
never backdates. Services always advance even without fresh button data. External
qualified stop_requested acts every tick. Controller snapshots have no stalepulse.

StopHold uses source spans for debounce; the complete BTN_LONG_MS begins at the
actual decision tick that qualifies BOTH. Subsequent fresh source must reach that
anchor plus the hold; a source still before the anchor contributes zero, never
unsigned underflow. Fresh release on deadline cancels; STOP remains until reset.
StopHold.interrupt clears unfinished qualification but preserves latchedSTOP.

Menu uses source spans for neutral/press/release qualification. MODE hold begins
at the actual qualification decision; subsequent source before that anchor has
zero hold age. First fresh NONE freezes hold duration, then release debounce is
source-based. No-new cannot toggle/cycle/request, but final fault/non-IDLE still
disarms. restart preserves selection. Legacy step wrappers use fresh=true,
start_ready=true, source=decision and retain all old delayed/wrapped behavior.

## Event compatibility

Keep FaultCode CORE_CONTRACT_FAULT7 validation exactly1..255 (existing tests).
Append EXTENDED_CORE_CONTRACT11: value must have at least one of bits8/9 set and
no bits outside0x3ff; all low known bits may accompany it. Robot emits one contract
fault event for newly reported bits, selecting11 when any new high bit is present,
otherwise7. LINE_CONTRACT256 and BUTTON_CONTRACT512 now reach the actual recorder.
Enlarge internal fault_values to12 and emit through11. Keep event capacity21 and
wire size8, existing codes/CSV schema unchanged. Never emit both7and11 forone mask.

## Verification and scope

Independent author reads this contract/public headers/specs, not implementation
CPP. Cover synthetic windows/boundaries/overlap/off/config errors; pureadapter
isolation; all gestures through explicit Robot with replay/ABSENT/invalid data;
boot-held behavior; age/gaps/sequence/source/decision wrap; conservative qualification
anchors; expiry/reset; legacy tests unchanged; actual MotorGate enabled callback
writes become inhibited; events retained/CSV accepts11 and rejects reserved bits.
Host normal/sanitizer plus inert compile-only probe, actual staged source/ELF
identity, no startup invocation and upload refusal required. Fresh separate reviewer
reviews final diff/evidence. No full app scheduler integration or live input test.
Physical windows, SC-A, full tick800us, SC-AJ/F091 and human gates remain pending.
