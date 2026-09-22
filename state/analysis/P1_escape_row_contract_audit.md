# B4.2 next unblocked row executor — 2026-09-22

Read-only audit returned by p1_timed_arc_worker after its Fusion implementation
ended; no new implementation or tests supplied by this audit. Coordinator records
the findings. This identifies partial P1 work, not permission to finish unresolved
escape policies or claim all B4 behavior implemented.

An executor for explicitly caller-selected, fully specified B4.2 rows is unblocked:
- FR0x02/FR+RL0x06: brake one tick, reverse120ms at EDGE_BACK_DUTY, pivot left120°.
- FL0x01/FL+RR0x09: mirror, pivot right120°.
- RR0x08:200ms biased forward, requests(.56,.80) with current D-021 defaults.
- RL0x04: mirror requests(.80,.56).
- RL+RR0x0C:200ms straight forward at EDGE_BACK_DUTY.
- FR+RR0x0A: pivot left45°, then200ms straight forward; FL+RL0x05 mirrors.

Use config values rather than numeric literals above; centralize B4's existing
45° value in config.h with exact source test and non-tuning log entry. Reverse/
straight-forward use B7 Straight; biased forward uses duration-only TimedArc with
EDGE_FWD_INNER_RATIO. Pivot uses B7 Turn at TURN_DUTY. Profiles EDGE_REVERSE,
EDGE_FORWARD and PIVOT respectively; a brake emits zero/immediate braking.
Capture current/last-known finite heading at each primitive entry; do not backdate
new phases after delayed calls. Preserve B7 fallback, finite validation and timeout
pulses. Completion is separate from permission to leave escape: D-020 still
requires all black and completion, and all-white veto always overrides requests.

This row executor must not select pushed-out precedence, replan automatically or
invent movement for unsupported masks. An explicit unsupported API result is
not an approved production fault/recovery behavior. Record inward validity;
timed fallback cannot manufacture a measured final heading.

Remaining dependent policy gaps to resolve before full Escape/Robot integration:
- Head-on0x03 says "Brake" without a duration or last-opponent-side mapping;
  reverse duty is table shorthand. Do not silently introduce timing or a mapping.
- SC-R/S: three-white/exhausted replans and ambiguous pushed-out cases.
- B4.4: new-bit handling during non-pivot segments and finished-but-still-white
  motion. The guard requires staying in escape but does not choose new movement.

Tests for supported rows: every mirror, exact tick/120/200ms boundaries,45/120°
targets, entry heading capture/corrections, fallback/recovery/timeout, delayed
calls/wrap/finite extremes, reset/restart/terminal zeros and governor composition.
Locked guard composition must show all-white inhibition and no escape release
merely because a script finishes while white persists. Unapproved cases remain
explicitly outside the row executor, not silently counted as passing B4 rows.
