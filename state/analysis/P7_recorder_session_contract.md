# D224 recorder delivery session identity

Objective: accept one identified synthetic recorder delivery from the bare UNO Q
without treating upstream framing cleanliness as measured. The existing wire v1
already carries a uint64 session on BEGIN, all row envelopes and END. Keep that
format and the existing count, CRC, chronology, lifecycle and CSV checks.

## Firmware contract

`recorder::dump::Context::session` defaults to zero. Zero preserves historical
wire identity (`RobotResult.token`); a nonzero value supplies the wire session.
`Transfer` freezes the supplied value at start. Any change during ACTIVE cancels
pending bytes once with appended `Reason::SESSION_CHANGED`, including a same-time
call and changes between zero and nonzero. No identity creates service intent,
inhibited IDLE authority, a valid source, a port or a setup grant. Existing time,
result-token, source immutability, loss, bounds and failure behavior stay active.

`SetupGrant` preserves its first four booleans and appends `receive_stream` and
`session`. The default `TRUSTED_FRAMING` requires all four historical grants.
Explicit `UNTRUSTED_RECEIVE_STREAM` requires nonzero session and the existing
setup, MCU-exclusive UART and ready-pin ownership grants. It relaxes only the
`framing_clean` precondition and does not modify or claim that observation.
Unknown modes fail. The native device, register, IRQ, clock, FIFO, poison,
deadline and lifetime-owner checks are unchanged. Linux receiver framing may
remain unknown; the expected-session receiver must reject stale/mixed bytes.

The existing 200-second synthetic `Runner` copies the setup session into its
private attempt state and passes it to each `Transfer::step`. Its inert motor
backend, fixed recording scenario, real transaction receipts, FIFO8 transport and
inhibited IDLE requirement stay unchanged. Production runtime/setup grants are
untouched. `recorder_run_identity.h` is checked in disabled with zero identity
and no grants. Only a separately admitted staging operation may replace its
staged copy with one fresh nonzero identity and explicit setup ownership grants.

## Receive contract

`Parser(expected_session=None)` (also `WireParser`) and
`save_capture(..., expected_session=None)` preserve legacy behavior by default.
An expected session must have exact Python type `int` and be in 1..UINT64_MAX;
bool, int subclasses, floats, strings and zero are rejected before capture I/O.
The CLI `--expected-session` accepts canonical positive decimal only, with the
same range. It is a capture option and is forbidden in observation-only mode.

BEGIN and every subsequent envelope, including END, must match the expected
session and the original stream session. An expected mismatch fails with
`SESSION_MISMATCH`; legacy mixed sessions retain `SESSION`. Failure is terminal;
there is no skipping, stream resynchronization, retry or acceptance of a later
matching BEGIN. Existing counts/CRC and trailing-byte rejection remain required.

`capture.json` and `error.json` retain `expected_session`, `observed_session`
(BEGIN) and `rejected_session` (first valid mismatching integer). Existing raw
`wire.txt`, partial publication and transport/connection failures are retained.
No expected identity proves hardware origin, continuous exclusivity, clean
framing, DMA completion, receiver registration, sensor/motor acceptance or a
phase gate. Session freshness only binds accepted bytes to the caller's attempt.

## Run boundary

The later narrow caller must generate and stage one fresh identity, compile only
MATCH0/MOTORS_ALLOWED0/static/default recorder.ino, verify current source and
checked artifacts, arm its expected-session receiver shortly before one exact
upload, and preserve every initial/closing failure and timeout. It must reuse
existing compile/upload identity guards without widening generic upload policy.
It must not stop/start a router service, open/close/flush the UART, issue UART RPC,
reset framing or silently retry. TCP connection evidence is not router
registration or a framing-clean claim. No board action is part of this source
implementation. Actual delivery remains untested until that one admitted run.

Independent focused source/host tests precede review. Do not repeat broad
historical suites without a new finding; target builds run serially and are
scheduled by the main owner after its source-frozen commissioning matrix.
