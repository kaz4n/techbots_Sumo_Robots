# D-061: bounded ambiguous DEFEND entry

Selected under D-051 on2026-09-23, before dependent source and new tests.

D-026 permits simultaneous side/rear conflicts with no previous valid bearing.
That is legitimate unknown information, not malformed sensor context. The first
D-060 implementation passed it into DefendTurn's valid-bearing-only start API,
which safely inhibited with SCRIPT_START. The new randomized no-contract-fault
expectation exposed a policy gap; it did not demonstrate unsafe motor motion.
D-061 explicitly changes Robot's handling for this valid ambiguity only.

When normal current perception selects DEFEND_TURN and there is no active defend
executor and Fusion supplies bearing_valid=false, remain in DEFEND_TURN with
immediate governed zero demands. Keep ordinary logical permission (unless edge,
STOP or a genuine contract fault inhibits). Do not invent an angle or latch a
script/contract fault merely for the missing bearing.

The first such admitted observation starts an800ms interval using the existing
DEFEND_TIMEOUT_MS. Immediate duplicates do not advance or restart it. On a later
valid side/rear bearing before expiry, capture the real current heading/bearing
and start the existing DefendTurn executor, without extending the original800ms
deadline. Its B7 terminal zero still waits for perception or the earlier overall
deadline. Existing valid-bearing entry behavior is unchanged.

At age>=DEFEND_TIMEOUT_MS, enter SEARCH for that tick using D-060's existing
defend SEARCH-exit routing. Expiry wins a newly usable side/rear bearing on that
same tick. Normal current front and target-clear selection run before this
deadline check: front enters TRACK with fresh centering qualification, no target
enters SEARCH. Any edge or STOP still preempts immediately. Leaving DEFEND,
including preemption/reset, clears the pending interval. If ambiguity remains on
the next tick after timeout, normal arbitration may enter a new bounded DEFEND
wait; no blind turn is synthesized by this retry.

All finite-input, application-receipt, heading and script-result validation remains
in force. DefendTurn's public valid-bearing-only API is unchanged; Robot owns the
pending interval and does not call that API until it has its required input.
No B16 value, hardware fact, existing locked assertion or human gate changes.

Required new independent Robot regressions: both-side and both-rear initial
ambiguity, lower-priority extra bits, zero demand/no fabricated bearing, delayed
valid capture without deadline extension, exact800ms and adjacent observations,
duplicate/wrap behavior, front/clear exits and edge/STOP preemption. Retain and
rerun the original10000-stream locked property unchanged. Preserve failed
P1_robot_host_20260923_run2.txt and P1_robot_failure_trace_20260923.txt as evidence.
