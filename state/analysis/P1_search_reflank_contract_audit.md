# B8/B11 contract audit — 2026-09-22

Read-only separate Codex auditor p1_feature_review inspected specifications and
public headers only. Coordinator records the returned analysis, not an approval.

SEARCH executor: MEMORY_TURN -> SCAN -> ADVANCE -> alternating SCAN. Valid world
memory younger than SEARCH_MEMORY_MS captures one B7 turn on entry; expiry during
that turn does not retarget it. A 360-degree scan cannot use motion::Turn: shortest
angle reduces360 to0, and its700ms deadline is shorter than360*2=720ms fallback.
Scan uses directed continuous yaw at SCAN_DUTY; completion starts a300ms Straight
at SEARCH_DUTY_MAX. At advance entry use the stored inward heading if its age is
under5s; otherwise current/last-known heading. Straight holds the selected heading;
no unrequested extra pivot. Any current target exits with zero to perception,
before phase completion. Caller still supplies governor/edge/STOP authorization.

Use explicit context validity and saturating ages, not raw now-minus-old-time
after arbitrary wraps. Capture/age inward history while searching. Normalize yaw
for captured short turns, preserve continuous yaw for scan displacement. Finite
healthy observations required; unavailable observations do not manufacture yaw.
Bound same-tick phase advancement; new segments begin at the observation tick.
SC-Z decides the upstream last-side mapping; SC-AA decides the scan-loss fallback.
Both remain pending. The standalone executor can accept an explicit known side
without silently choosing between front recency and latest bearing.

Re-flank executor private stages: BACK, SWING_PIVOT, SWING_ARC, TURN_IN. Recorder
public phases remain BACK/SWING/TURN_IN. Side choice uses known recent edge side,
then front recency, then approved right-first alternation (D-037). Unknown/bilateral
edge metadata cannot invent a side. Caller retains previous actual swing direction
outside the command, so reset/start cannot erase alternation history. Nonwrapping
ages/order preserve recency. SC-AB decides ranking when only one side was seen.

BACK uses heading-held reverse and REFLANK_BACK profile. Any front detection plus
current contact cue skips immediately to SWING; this uses cue, not stale ATTACK
latch. Inner SL/RL interrupt applies to all SWING, including pivot ("at once" in
B11). Right swing pivots+60 then arcs LEFT with current default requests(.32,.80);
left mirrors. Pivot/arc/TURN_IN use REFLANK_TURN profile. The arc is genuinely
time-only under D-037. TURN_IN captures one selected bearing, never retargets.
SC-Y decides natural arc exit and TURN_IN continuation; no approval inferred from
D-038, which defines how to route an exit rather than when to exit.

Required tests: exact/adjacent memory/inward-age/deadline thresholds, all masks in
each stage, missing/invalid IMU, fallback recovery, opposite yaw, mirrors and ties,
same-tick transitions, phase notifications, finite extremes and cumulative wraps.
Full Robot qualification, fresh contact, edge/STOP priority and target-loss braking
remain integrated tests, not claims supplied by these standalone executors.
