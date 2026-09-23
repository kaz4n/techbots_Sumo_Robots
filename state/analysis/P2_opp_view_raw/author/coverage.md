# D107 independent author coverage

Expectations derive from the frozen D107 contract, its pre-test clarifications,
public bench/HAL headers and existing test fixtures. The author previously
implemented D104 and authored D105/D106 tests. This is independence from the new
D107 implementation bodies, not a fresh whole-repository or cross-model review.
No D107 implementation body was read. Opaque copies/hashes are permitted, and
compiler diagnostics may disclose individual implementation lines.

The frozen new files are tests/tooling/opp_view_cases.cc and test_opp_view.py.
The C++ fixture owns actual time observations, callback costs and literal
snapshots. It never seeds or exposes Runner private state. The literal frame
oracle checks every one of 104 bytes for all 128 masks, unknown/error states and
recovery. Configured polarity is applied exactly once; two additional isolated
profiles exercise all-active-high and all-active-low masks.

Twenty-four normal/sanitized Runner cases cover grant truth, copied ports,
constructor/prebegin/disabled silence, unused inner grants, missing callbacks,
one-attempt setup with exact brackets, all seven signed setup/read status
positions, malformed masks/status-bit consistency, source interval boundaries,
first-error preservation, real recovery with a latched error stripe, early and
equal-clock passivity, original release-grid admission and strict completion
skips, measured read and whole-poll costs, display cadence/throttles/status
faults, first-fault retention, global and aggregate clock discontinuities,
matrix-attempt age half-range boundaries and natural wrap. Missed-release
saturation is reached with 2002 actual large forward polls, without private
counter mutation. Other uint32 counter exhaustion is impractical through the
public API and remains a source-review obligation.

Two Native/sketch cases link the actual new binding, pure Runner and unchanged
default sketch to counted substitutes for the existing public Sensors and
UnoQMatrix methods. They verify exact forwarded fields, frame bytes, time,
grants, stable per-instance owner identity, no constructor/port I/O and all-false
setup/loop silence. No old native owner implementation is replaced in its own
established tests: these cases specifically test the new binding's forwarding.
The fixture exposes only micros in Arduino.h; unrelated native owner references
cannot silently acquire dummy implementations. The established native suites
and target source/import/startup audit remain separate evidence.

Six invalid-config profiles require pre-I/O CONFIG refusal while all-disabled
begin remains silent/successful. Three sketch flag profiles require compile-time
refusal for MATCH and/or MOTORS_ALLOWED. malloc/calloc/realloc/free and ordinary
C++ new/delete calls are counted around Runner work and default sketch calls.

Normal/sanitized native runs deliberately filter to the two binding/sketch cases;
the other 24 are run separately in full. Alternate-polarity runs deliberately
filter to the mask case. Their reported skipped counts are filter exclusions,
not untested normal Runner cases or runtime skips.

These are synthetic host callback, forwarding and config checks. They establish
no physical polarity/range, empty-ring observation, electrical or matrix grant,
optical result, actual execution time, full-app WCET, loaded RAM or human gate.
No board/network/upload/reset/native sensor activation occurs in this task.
