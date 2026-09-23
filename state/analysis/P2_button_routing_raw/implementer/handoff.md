# D087 core implementer handoff

2026-09-23. Implemented the frozen button-routing contract in assigned core files:
countdown.cpp, fsm_robot.cpp, new fsm_buttons.cpp, logframe.cpp, and private sections
only of countdown.h/fsm.h. Source hashes are recorded in source_hashes.json.
Root owns public declarations, HAL decoder/adapter, config, build/probe and state
closure; a separate author owns new tests. No existing test was modified or new
independent assertion read. No commit or board/hardware operation was performed.

Legacy timing methods now forward source=decision and fresh/start_ready=true.
Observed methods preserve source spans for qualification, but anchor the full
START countdown and qualified BOTH/MODE hold to the actual decision tick. A source
still preceding its decision anchor contributes zero hold time. No-new observations
retain unfinished gestures without advancing qualifiers; Gate and Services still
advance each decision tick. Restart preserves STOP, Gate state and Menu selection.

Robot selects one input mode until reset, admits explicit evidence with identity,
source/decision continuity and bounded accumulated age, and requires fresh neutral
completion times to span debounce before arming START. StopHold remains live before
arming. Replay does not renew age; malformed, expired or mixed evidence latches
BUTTON_CONTRACT and inhibits through the existing fault path. Current diagnostics
retain the accepted level/source/sequence; duplicate decisions clear update/actions.

Fault event7 retains its original1..255 validation. Event11 carries masks containing
LINE_CONTRACT or BUTTON_CONTRACT with no bits beyond0x3ff. One event is selected per
new fault mask, and the fixed fault-value array is enlarged to12 entries. Existing
event capacity/wire format are unchanged.

commands.json names exact commands and outcomes. Initial isolated CMake configure
failed because its concurrently authored MotorGate test source was not yet present;
configure_initial.txt preserves that failure. No build/test was run by that failed
command. Strict compilation of the four core units then passed with no diagnostics;
syntax_initial.txt and syntax_initial.exit.txt retain the result. Diff whitespace
checks passed. Coordinator owns full normal/sanitizer host tests, final target
compile-only evidence and fresh review; those are not claimed complete here.

At implementer final handoff the coordinator reports actual target snapshot
a4a4b803 compiled successfully with59 current source files matching. This is a
coordinator-reported result, not a target command run by this worker. Normal and
sanitizer builds were continuing after test-fixture-only repairs; no core finding
or production repair had been reported. ButtonTiming restart applies to initial
explicit entry and button-admission faults; unrelated final faults retain the
existing Gate STOP/Menu inhibition and STOP-priority snapshot behavior, as the
coordinator confirmed and clarified in the contract.

An initial read-only PowerShell command also failed parsing a Unix-style brace
file list before execution; a corrected explicit file list succeeded. No source
or test action was affected, and no raw log is claimed for that tool-only error.

Limits: this is source/host software work. Electrical windows remain disabled in
production config. START/BOTH electrical ambiguity, physical ADC/input behavior,
whole-tick timing, runtime integration/clock ownership and human gates remain open.
Next action: coordinator resolves any independent test/review findings, verifies
the frozen final source and records the bounded software acceptance.
