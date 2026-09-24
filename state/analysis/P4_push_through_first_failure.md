# D131 first execution and fixture adjudication

24 September2026, before any production repair. Original source/oracles remain
in `P4_push_through_raw/original/` and `original_freeze.json`.

Default0: all16 public CTest targets PASS. The runner subsequently returned1
because independently authored private probes used raw doctest REQUIRE with the
project's no-exception mode. The reviewer retained v2 and the compiler output,
then changed only assertion plumbing to the established APP_REQUIRE convention.
No default public or production test failed. The generated RAM build was gone
when the reviewer checked; it was not inferred live or blindly restarted.

Positive20: M0 PASS. M1 reached the later re-flank part of the B11/B9.4 test and
aborted at fixture line137's expected TRACK state at entry+1250000us. The original
result is `positive20.json/txt` and `positive20_build/LastTest.log` (CTest8).

Independent author, without implementation bodies, and fresh reviewer, using
actual source, agreed: initial target0x0A (FC+SL) intentionally avoids phantom
filtering during no-contact deferral. Leaving SL present after the real FL escape
makes it the inner detector of the required RIGHT re-flank. Existing B11/public
Reflank::step gives that detector priority, entering TURN_IN and then current-front
perception early. The later helper assumed uninterrupted natural arc completion.
This is an invalid fixture trajectory, not evidence for changing D131 production.

Approved correction to this new, unaccepted normal test only: clear SL by setting
target2 before the real recovery helper; its361ms observed recovery exceeds the
30ms clear debounce before the later re-flank. Keep every timing, TRACK, contact,
event, safety and limiter assertion. All established and new locked files stay
byte-for-byte unchanged. Preserve original and corrected hashes before rerun.
This is the first fixture correction; no production fix has been attempted.

## Timing evidence policy extension

The first configured20/timing1 sanitizer run later passed all37 M0 cases and
36of37 M1 cases; only the frozen deferred-white exclusion expectation failed.
The original D129 contract excluded actual escape/fault, so its implementation
matched that policy. The new D131 wording was ambiguous. Under D051 the
coordinator explicitly extended positive-duration timing exclusion to admitted
white, including the first eligible arming observation. This changes evidence
qualification only; it does not reinterpret the prior failure as an old defect.

The frozen failed expectation remains unchanged. Five new independent public
cases and two private cases cover first arming, retained white/no retry and
source/receipt precedence. Review found an unconditional predicate could change
the default0 STOP/white tie detail; both added predicates now require positive
duration, preserving the disabled-default classification.

The first source retry passes42 public and14 private cases per M0/M1 with
ASan/UBSan. The unchanged oldD129 suite passes30 cases per M0/M1 with sanitizers.
See configured20_timing_sanitize_retry1 and legacy_timing_sanitize receipts.
No locked assertion, existing failed oracle or motion policy was weakened.
