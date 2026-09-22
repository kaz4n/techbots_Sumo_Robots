# Independent CONTACT metadata semantics — 2026-09-23

Owned new `tests/test_robot_event_semantics.cpp` and this note only. Sources:
BEHAVIOR B5.2/B5.4, D-027, public `logframe.h` and the D-060 CONTACT metadata row.
No implementation read, existing-test edit, build, hardware operation or commit.

Three CHECK-only cases:

- A literal eight-row table covers all front masks, including none, against
  close/impact/both details and every combination of the four lower-priority
  side/rear bits: 384 payload combinations. Centered masks are 2/3/5/6/7;
  a close flag additionally requires current front mask 5 or 7. Lower-priority
  bits do not change the valid front classification.
- Absent/reserved cue flags and reserved payload bits remain invalid.
- The two concrete impossible records (close with FC-only; impact with lone FL)
  increment semantic rejection without entering the event batch, followed by
  accepted impact/FC and close/straddle records with preserved order and payload.

This tests truthful metadata, not a change to contact qualification, Robot motion
or wire packing. No state or hardware inference is made from the event alone.
Static checks confirm direct includes, no REQUIRE and no trailing whitespace.
Execution evidence is left to the coordinator's normal/sanitizer runs.

Frozen test SHA-256:
`1A58E8129A4E685A25480345F7B6D6F1A9A9F21EDC58BE0C312417E9299C53A6`.
