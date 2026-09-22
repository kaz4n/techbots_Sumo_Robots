# B11 re-flank contract preparation — 2026-09-22 Asia/Dubai

P1 host-only under D-016. D-037/D-038/D-040/D-043 authorize the current
script/side policies; they do not prove implementation or physical performance.
This note prepares the public header before independent tests or source edits.

Side selection uses explicit truthful ages and known-side metadata. A known edge
side with age below RECENT_EDGE_MS wins: swing away from it. Otherwise an unseen
front side is older than a seen side; among two seen sides the larger age wins.
Equal ages or both unseen use the opposite previous actual swing, default RIGHT
when none. Unknown/bilateral edge metadata cannot supply a fabricated side. The
caller owns previous actual swing history across command reset/start.

Reflank.start captures a finite initial/last-known heading and selected direction.
Successful entry means BACK is recorded by the caller at that exact start tick.
BACK is a heading-held reverse for REFLANK_BACK_MS at REFLANK_BACK_DUTY.
Current front plus a current contact cue skips immediately to SWING. The cue is
not an expired ATTACK contact latch. Other front readings do not interrupt BACK.

SWING first pivots REFLANK_PIVOT_DEG toward the selected side at TURN_DUTY.
Then it arcs in the opposite direction at TURN_DUTY/REFLANK_ARC_RATIO for exactly
REFLANK_ARC_MS, independent of yaw sweep. SL/RL for a right swing, SR/RR for left,
interrupt either private SWING segment at once, including its completion tick.
This captures the current finite valid relative bearing for one B7 TURN_IN.
Unconsumed bearing payload is ignored. Missing required bearing invalidates the
command with zero demand; this is API defense, not a new Robot fault policy.

TURN_IN preserves that target even if side readings disappear/change. Current
front or turn completion/timeout ends with zero PERCEPTION intent. Natural arc
completion also exits through D-038 current perception. Front alone does not
interrupt SWING. The caller performs fresh centering qualification/contact.

Public phases BACK/SWING/TURN_IN hide the pivot/arc implementation split.
One-call entry flags preserve both SWING and TURN_IN entries in that order when
they share an observation. No entry is buffered for a later timestamp. A separate
one-call turn-timeout flag survives transitions. New segment timers begin on the
observed transition, never backdated; at most four private stage visits per step.
Use REFLANK_BACK for BACK, REFLANK_TURN for all other motion. Terminals remain
zero until reset/start. Last finite healthy yaw supplies later primitive entries;
unavailable yaw is ignored, and healthy nonfinite yaw invalidates active motion.

Caller owns edge/STOP preemption, start-rate limiter, events, governor and motor
permission. This executor never writes I/O or assigns Robot states. No new pins,
B16 values, locked-test amendment, hardware assumption or phase gate is implied.

Independent spec/header-only author audited this proposal and found it consistent
with the cited decisions, with no new protected choice beyond genuine edge-side
metadata. Final API and tests must keep these boundaries explicit.
