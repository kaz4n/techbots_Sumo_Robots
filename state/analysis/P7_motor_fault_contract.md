# D162 inert MotorGate callback diagnostic (draft)

Purpose: distinguish the first false callback in a separately instrumented bare
UNO Q run after D161. This is not proof of the original D160 failure site: added
clock/trace work changes timing. Native adapter, MotorGate, config, core, installed
API assumptions, existing locked tests and150us settle limit remain unchanged.
Unchanged native setup callbacks (including device initialization) may block;
this diagnostic records in-progress evidence but cannot time out such a callback.

Files: bench/motor_fault/{motor_fault.ino,src/motor_fault.h,src/motor_fault.cpp};
new independently authored tests/tooling/motor_fault_cases.cc and test_motor_fault.py.
No production build/config change. Existing generic staging may prepare the sketch,
but no new upload allowlist or target operation belongs to this host-only scope.

Public header is the interface. MATCH=0/MOTORS_ALLOWED=0 is mandatory at compile
time. Construction, port retrieval, report inspection, denied begin, terminal poll
and repeated begin have no native callbacks or clock reads. Default sketch grants
nothing. Native UnoQPort owns the existing pads; only one real MotorGate invokes
its callbacks through Trace. No serial/Bridge/network path, heap, delays or I2C.

Trace copies original periods and preserves null callback pointers. Valid callbacks
forward the exact original context/arguments/result once. Clock forwarding returns
one actual original reading. EN-high or nonzero PWM requests are locally refused,
recorded with invoked=false/returned=false, and never reach the native backend.
No other argument/result is invented or corrected. This is extra inert guarding,
not a change to MotorGate or its production native port.

Trace retains64 completed calls in order, a current call (completed=false while
in progress, has_current=false until the first call), and a separate first-failure
record that cleanup cannot replace.
Records identify SETUP/APPLY/HALT stage, one-based application index (otherwise0),
operation/channel/request, invoked/result flags, and start/end microseconds.
Capture the native false outcome before the trailing diagnostic clock read.
If that clock returns, update that same first-failure record's completion/timing.
Timing is valid only with an original clock and modular end-start<2^31; same-time
and wrap intervals are valid. Any invalid timing latches timing_fault. Missing
clock produces invalid timing, not fabricated zero-duration evidence. Trace-full
latches overflow and saturating rejected count; retain the first64, current call,
and first false call even if it occurs after capacity. Callback order/return is
unchanged by overflow. clock_reads counts all reads through Trace, saturating.

Runner is one-shot: begin({false}) enters DISABLED successfully with no callbacks.
Every subsequent begin returns false, preserving reports with no side effects.
Granted begin performs real Gate.begin once in SETUP. On setup failure it records
that outcome, performs one real Gate.halt in HALT, and ends FAULT. On successful
setup it anchors the first application immediately at the next actual clock read,
enters RUNNING and returns true unless trace timing is already invalid/overflow.
Poll accepts micros() from its caller; only RUNNING polls use it. Clock movement
must be forward/equal under half-range arithmetic; backward/ambiguous movement,
or APP_CLOCK_STALL_MAX_POLLS repeated equal-time polls, terminates with CLOCK.
Every active equal-time poll counts, including the first poll at the anchor;
any forward movement resets that consecutive count. The limit check precedes work.
Before the next release no application occurs. On/after release perform at most
one application; advance the release grid by whole TICK_US intervals to the first
future grid time, recording skipped releases (no catch-up applications).

Each of four fixed application receipt slots is one capture sample (ABI extent,
not a new control tunable). Use fresh=true, token=slot+1, disabled zero duties,
BOOT UI and IDLE countdown gate, all other RobotResult fields at defaults. This
is an explicitly synthetic inert command, not a Robot decision/perception stream.
Real Gate.apply receives the poll time. Save its complete Result unchanged.
Invalid/disabled-command-inconsistent feedback (invalid, wrong token, not consumed,
fault!=NONE, enabled or nonzero duty) ends FAULT/APPLICATION immediately.
Trace timing/overflow ends FAULT/TRACE. Otherwise stop after four applications.

All active terminal routes call Gate.halt exactly once and preserve its whole
result separately. COMPLETE requires all four applications successful, no trace
error and a fresh/attempted/timing-valid/confirmed halt with Gate STOPPED; failed
cleanup ends FAULT/HALT unless a prior failure reason exists. First false callback
and prior failure reason survive cleanup failures. Repeated calls cannot restart.
Scheduling uses existing TICK_US/APP_CLOCK_STALL_MAX_POLLS; no config tuning.

Independent tests derive from this contract/public headers and the existing
P2_motor_gate_contract.md, not implementation bodies. Exercise exact forwarding,
all callback failures (including cleanup), first failure, clock wrap/reversal,
overflow, scheduler thresholds/skips, four zero applications, terminal passivity,
denied/default construction, compile refusal for motor/match flags, allocation
absence and unchanged real Gate safety tests. Use serial RAM-backed compilation,
normal and sanitizer runs; preserve first failures, freeze expectations first.
Target compilation/upload and passive record capture require later identified
scope, source/artifact binding and separate review; no physical or human gate.
