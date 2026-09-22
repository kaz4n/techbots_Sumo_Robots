# P1 B7/B15 component contracts - 2026-09-22

Base: 683665b, clean on recovery; P1 host-only under D-016. D-021 is already
implemented. No new behavior approval or hardware evidence is inferred.

`motion.h` defines the unambiguous IMU-valid portion of B7 turnTo and stationary
brake timing. Shortest signed error follows B0's (-180,180] convention; the exact
180-degree tie therefore chooses right. A timeout at the same tick as arrival
reports timeout so the timing fault cannot disappear. Invalid input is reported
with zero demand. These are component requests, not permission or a complete
fault-fallback implementation. SC-N heading correction and moving-duration
semantics have been sent as two distinct decisions; dependent work waits.

`logframe.h` defines only B15 serialization. Little endian, explicit offsets,
nearest/halves-away quantization, and returned invalid/clipping status are local
representation choices; they change no motion rule or tunable. A 25-byte frame
(B15 says about 24) uses signed 32-bit centidegrees so multiple yaw revolutions
are preserved. No ABI packing, heap, transport, buffer, or overflow policy is
introduced. At 50 Hz this payload alone would require 250,000 bytes for 200 s;
that arithmetic is not installed-board memory acceptance. Eight-byte events
preserve the supplied uint32 microsecond tick and a three-byte typed payload.
CSV conversion, frame cadence, buffering, simultaneous event collection and
SC-E2 overflow remain later recorder work. Invalid/clipped data cannot be called
valid evidence by a future caller merely because a byte buffer was produced.

Independent test author will read only specification, public headers and this
contract. Required checks: turn signs/gain/min/max, strict 5-degree boundary,
699999/700000/700001 us, unsigned wrap, invalid finite/nonfinite inputs, reset,
180-degree convention, mirrored turns excluding the tie, stationary brake
boundaries, literal frame/event bytes, quantization/clamps and invalid poisoning.
No existing locked test is edited. Target compilation and robot WCET are pending.
