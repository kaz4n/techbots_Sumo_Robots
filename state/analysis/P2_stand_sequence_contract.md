# D119: finite B4 directional sequence, pure software slice

Adopted under D051/D075 on 2026-09-24. This implements the finite request
sequence needed by P2 B4; it does not yet integrate a directional controller,
authorize any motor output, enable P3 DRIVE_TEST, or satisfy B4/B7 acceptance.
Existing MotorGate, Robot, countdown, governor, native code and locked tests
remain unchanged in this slice. No board action is included.

## Public contract

`src/core/stand_sequence.h` declares `stand_sequence::Sequence`. It has no I/O,
clock, allocation, motor permission, sensor synthesis or application receipt.
Its duties are nominal requests, never final electrical duty. A future explicitly
adopted Robot bench profile must consume these through the existing real source,
hold, edge, governor, MotorGate and receipt path. Never edit a RobotResult to use
this helper. Existing DRIVE_TEST remains unavailable.

One `start(t_us)` succeeds per instance and enters segment0. Another start is
passive false, including after completion/failure. The owner must start only at
the actual qualified GO after the full hold; this helper cannot prove that GO.
`report()` is a passive const snapshot. There is no restart/reset method.

The literal segment table has twelve rows, each lasting at least the new
development default `config::STAND_SEGMENT_MS = 500`:

| Index | Phase | Nominal left request | Nominal right request |
|---:|---|---:|---:|
|0|DRIVE|+STAND_DUTY|0|
|1|BRAKE|0|0|
|2|COAST|0|0|
|3|DRIVE|-STAND_DUTY|0|
|4|BRAKE|0|0|
|5|COAST|0|0|
|6|DRIVE|0|+STAND_DUTY|
|7|BRAKE|0|0|
|8|COAST|0|0|
|9|DRIVE|0|-STAND_DUTY|
|10|BRAKE|0|0|
|11|COAST|0|0|

`config::STAND_DUTY = 0.25F` is a development request, not measured usable speed.
These two new tunables do not change or alias any B16 value. The segment count
is fixed protocol structure. Future B4 integration needs an explicitly specified
final electrical cap; this slice neither adds nor bypasses a governor profile.
Shared EN means COAST must ultimately inhibit both sides; during single-side
driving the zero-request side would brake. The helper itself writes no pins.

## Time, preemption and terminal behavior

`step(t_us, edge_required, stop_requested)` returns the current report by value.
Before start and after any terminal result it is passive, ignoring all inputs.
Immediate duplicate timestamps ignore changed inputs and clear only `fresh` and
`phase_changed`. Every admitted distinct active call sets `fresh=true`.

Admission order for a distinct active call:

1. Unsigned delta from the prior admitted timestamp must be below 2^31. Otherwise
   enter FAULT/CLOCK_ORDER with zero requests. This includes backward timestamps.
2. STOP wins over edge and timing gap: INTERRUPTED/STOP, zero requests.
3. Edge preemption: INTERRUPTED/EDGE, zero requests. This is permanent sequence
   cancellation, **not** an escape implementation. Robot must retain existing
   edge priority and own any escape output.
4. A delta greater than or equal to one segment duration is FAULT/CLOCK_GAP,
   zero requests. No catching up across unobserved brake/coast intervals.
5. If elapsed since this segment's actual entry is below its duration, keep it.
   Otherwise advance exactly one row, anchored at this observation's timestamp.
   There is no loop, absolute-grid replay, or shortening of the following row.

After the full final coast interval, publish COMPLETE/NONE, segment12 and zero
requests. A terminal snapshot keeps its last segment (except COMPLETE uses12)
and its original reason, even after later STOP/edge/time inputs. BRAKE and COAST
have zero duties but distinct phases; callers must not infer motor enable from
zero duty. `phase_changed` is true for start, row changes, or terminal entry;
`fresh` is true at successful start and admitted distinct active steps. A refused
start does not alter either flag. Repeated terminal steps clear the two pulses.
At a legal delayed transition the new interval starts now, never retrospectively.

Require STAND_SEGMENT_MS>0, 0<STAND_DUTY<1, and twelve twice-duration intervals
strictly below 2^31 microseconds. With continuing admitted clock observations,
every row is under two durations and the sequence is finite. No invocation means
no software can advance; this helper is not a watchdog or a physical stop proof.
Wrap-safe arithmetic permits a run spanning uint32 wrap.

## Independent validation and next integration

Freeze executable expectations derived only from this contract/public header
before their first execution against implementation. Test the literal table,
exact/adjacent transitions with preceding observations, 6-second nominal finish,
delayed transition anchoring, gap boundary, wrap, backward/half-range clocks,
STOP/edge/gap precedence, duplicate suppression, terminal passivity and refused
restart. Cover finite/bounded outputs and unchanged default config separately.
Run the actual host normal/sanitizer suites; do not amend locked tests.

Then adopt and implement the real B4 Robot/Transaction integration separately:
immutable bench profile; full existing START hold and source admission; existing
edge precedence; true Lifecycle STOP; explicit electrical cap and brake/coast
enable handling; actual MotorGate receipts; preserved default production and
P3 DRIVE_TEST behavior. OPENER-as-bench-script needs visible profile provenance.
Exact target fit must be checked before integration acceptance: D118's default
app has very little modeled loading margin. No powered test or B7 claim follows.
