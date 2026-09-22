# B9 integration boundaries — 2026-09-22

Separate read-only audit by p1_timed_arc_worker, recorded by coordinator. This
agent previously implemented other modules; this is contract analysis, not a
fresh phase-gate review or a human approval.

Unblocked: B9.1 explicitly requires ATTACK_ENTER_TICKS consecutive centered
observations. FrontQualification counts exactly those observations and returns
eligibility. It receives the effective confirmed mask after Fusion filters;
off-center/absent observations reset it. Caller reset on leaving normal perception
prevents stale qualification on D-034/D-038 reacquisition. It has no clock or state
selection. Public contract c0b3ad6 precedes source and independent tests.

Actual integration must consume a new Fusion observation once, select the final
state, commit contact once, obtain frontDemand and apply governor/gates. The
counter itself chooses neither which entry tick to count nor a loss destination.
These genuine full-FSM questions remain:

- SC-AD: BEHAVIOR B9.1 and D-034/D-038 do not explicitly anchor the first count
  when a script exits into normal TRACK. A: count that current eligible centered
  observation as the first of the required three; no script-internal observations
  carry over. B: start counting on the following TRACK tick. Recommend A, using
  the current observation exactly once and requiring three actual observations.
  Human decision needed before the complete state-entry contract. Tests must
  cover entry, second/third observations, preemption, off-center interruption,
  and opener/re-flank reacquisition with stale contact cleared.
- SC-AE: B9.3/B1 say loss of front target goes SEARCH (with immediate braking),
  whereas B2 item8/B10 select DEFEND_TURN if a current side/rear target remains.
  A: request immediate braking on the loss tick, then route by current perception
  (side/rear -> DEFEND_TURN, none -> SEARCH); that tick's brake overrides the new
  state's demand. B: always choose SEARCH for the loss tick, re-arbitrate next
  tick. Recommend A, preserving braking and B2's current-target priority without
  an unnecessary SEARCH detour. Human decision needed; tests for every side/rear
  mask, both TRACK/ATTACK prior states, exact zero output at loss despite previous
  full duty, next-tick state command, fresh contact and edge/STOP precedence.

No decision has been inferred or implemented for SC-AD/AE. Standalone tests
may explicitly choose a harness schedule; that is not production Robot evidence.
