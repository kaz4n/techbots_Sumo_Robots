# Head-on row additive contract — 2026-09-22 Asia/Dubai

D-044 approves B4.2 one-tick braking and the existing long reverse duration/duty.
The original RowExecutor.start(mask) has established locked coverage requiring
mask3 to remain unsupported. Preserve it byte-for-byte in tests and preserve its
API behavior. Add explicit startHeadOn with caller-selected LEFT/RIGHT instead;
it does not silently choose the unresolved last-opponent-side history mapping.

The new entry shares the existing three-phase row engine: TICK_US brake, reverse
EDGE_BACK_LONG_MS at negative EDGE_BACK_DUTY, pivot EDGE_TURN_FULL_DEG toward
the supplied side at TURN_DUTY. Same profiles, last-known heading capture,
strict B7 tolerance/timeout/fallback, observed transition times and terminal
brake=true apply. Invalid enum or nonfinite initial heading returns INVALID/zero.
Reset/start must clear the new head-on flag so legacy reverse stays EDGE_BACK_MS.

Add NEW locked tests only, authored from specs and public headers, covering
mirrors, exact/adjacent/delayed phase times, capture, missing IMU/recovery,
clock wrap, finite extremes, restart into legacy rows, and real guard/governor
composition. Hardware MotorGate, full escape selection/replanning and physical
heading validity remain separate. No prior locked amendment or new tuning occurs.
