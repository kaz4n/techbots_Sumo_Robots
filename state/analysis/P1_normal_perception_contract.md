# D-045/D-046 normal perception integration preparation — 2026-09-22

Subsequent eligible P1 task after the current reviewed batch. This is a contract
proposal based on accepted behavior, not an implementation or full Robot claim.
Use the existing FrontQualification in fsm to select normal destination states
from each NEW effective confirmed mask. Current front wins lower groups:
TRACK until the required centered observations, then ATTACK. Off-center front
resets qualification and selects TRACK. No front selects DEFEND_TURN if a current
side/rear remains, otherwise SEARCH.

Fresh entry after any script or safety preemption clears prior qualification
and consumes the current observation once as count one (D-045). A front-loss
observation after TRACK/ATTACK returns an immediate braking directive along with
the new current-perception destination (D-046). The final governor must consume
that directive on this tick; any new state's demand is overridden until at least
the next tick. Losing centering clears the D-027 contact latch and restores the
TRACK SEARCH_FORWARD cap, but does not invent a front-loss brake when a front
still exists. ATTACK's approach profile must not be retained after selecting TRACK.

Caller supplies only fresh Fusion observations, commits contact against the
chosen state once, obtains frontDemand for front states and selects the current
state's governor profile. External gate/edge/script arbitration precedes this
normal selection. Reset qualification on preemption; do not let a helper count
the same observation both on entry and again during that tick.

Required production tests: entry/second/third centered sample, interrupted
qualification, every front/side/rear mask, both prior front states losing to all
residual masks, exact zero from prior full duty on the loss tick, next-tick
script demand, script reacquisition with fresh contact, and gate/edge precedence.
Keep pure state/routing behavior separate from unapproved escape recovery,
hardware sampling and actual MotorGate writes. Full Robot integration must still
exercise those real composition paths; a test-owned harness is not that proof.
