# P1 independent re-flank test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: independently test chooseSwing and Reflank from public fsm.h contract
a37c9c8, B11/B7/B6 and D-037/D-038/D-040/D-043. Owned files are
`tests/test_reflank.cpp` and this report. AGENTS and the approved saved re-flank
audit were read in this continuous session. No src/core/*.cpp source was read;
no existing tests, config, headers, state ledgers or build files were edited.
No build or commit was run.

The 29 cases cover literal defaults; chooser default/right-first alternation;
unseen/seen/older/equal front histories including uint64 limits; recent known
edge precedence at 4,999,999/5,000,000/5,000,001 us; and validation of direction
enums only when consumed. Unknown edge metadata never supplies a guessed side.

Execution coverage includes all 256 masks for BACK with both current-cue levels,
both private SWING segments and TURN_IN, in both directions. BACK requires a
current front plus current cue to skip; prior cue does not carry. Front alone
does not abort SWING; inner SL/RL or SR/RR starts TURN_IN; front then exits via
PERCEPTION. The independent literal B5 bearing fixture uses the front table,
side/rear priority and an explicit prior -90 degree bearing for bilateral
conflicts. No unspecified bearing is fabricated for a required turn.

Boundary cases cover 150 ms BACK, mirrored 60 degree pivot, opposite-direction
400 ms time-only arc at requested .32/.80, strict five-degree TURN_IN tolerance
with adjacent floats, and 700 ms turn timeouts. Inner triggers win both pivot
timeout and arc-expiry ties. Every mask without an inner trigger exits naturally
at arc expiry. TURN_IN captures one heading/bearing and survives lost/changed
side readings until front, completion or timeout.

One-call SWING/TURN_IN flags are checked separately and together, including
same-tick terminal front exits; the documented decoding order remains SWING then
TURN_IN. Private pivot-to-arc transition does not create another SWING entry.
Timeout flags persist on the transition call and do not replay. BACK entry is
the caller's successful-start notification, as specified by the header.

Further cases cover per-segment capture/correction; initial/mid-turn unavailable
IMU and recovery without timer extension; last-known heading; unavailable and
healthy nonfinite yaw; consumed/unused bearing validation; finite huge headings;
exact +180 relative-bearing RIGHT ties at tiny, ordinary and extreme headings;
delayed segment starts; exact wrapped deadlines; cumulative wraps with every
call gap below one wrap; terminal retention, reset and restart.

Real Governor composition checks low-voltage caps, reverse/pivot/arc sign
reversals, the requested versus final inner ratio, fixed arc timing and immediate
zero on revoked permission. The harness supplies permission explicitly; no
execution phase grants it.

Static handoff: 29 cases, CHECK/CHECK_FALSE only, no trailing whitespace, and
explicit uint64 initializer-list types. Parent owns actual host/sanitizer builds
and result records. No full Robot transitions, D-038/D-045 qualification reset,
contact lifecycle, limiter admission integration, event serialization, edge/STOP
arbitration, MotorGate writes, hardware motion or phase gate is proved.

Next action: parent reviews and runs the frozen suite, records verified evidence,
and commits the completed batch.
