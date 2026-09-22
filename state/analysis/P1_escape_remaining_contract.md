# Remaining B4 selection/replan decisions — 2026-09-22 Asia/Dubai

Separate spec/header-only audit by p1_filter_contract_audit, recorded by root.
No implementation read or file edit by the auditor. D-047/D-048 are accepted;
the following two exact proposals remain UNAPPROVED until the human answers.

SC-S, B4.3: priority all-white fault, then three-white fault, then qualifying
pushed-out maneuver, then ordinary B4.2 row. Qualify on current centered front
and both previously applied final wheel duties strictly positive. A single rear
white side pivots45 degrees away, then forward per B4.3. Both rear white proposes
the opposite shared opponent-side history (default LEFT). This direction and
forward-duty interpretation need approval. Test all16 masks and all duty signs,
centering, strict zero boundaries, direction mirrors and fault precedence.

B4.4 replan lifecycle: fault masks first. A new white bit on the declared pivot
side requests replanning during PIVOT. In other active phases any newly white
bit requests a replacement. Completed-but-white also requests a replacement.
At most one replacement per fresh observation; simultaneous bits count once.
Initial entry consumes zero; allow EDGE_MAX_REPLANS replacement starts (three),
then D-048 fault on the next/fourth request. Preserve budget until actual escape
exit or reset. These trigger/count/completion details require human approval.
Test additions/clearing/reassertion, same-tick phase deadlines, third/fourth
requests, black-before-completion, persistent white and reset. Alternative: defer
dependent full Escape integration; do not pretend approved policy supplies them.

Implement D-048 in full Escape composition with the existing Guard veto.
Guard's established component API has an all-white-only latch; established locked
tests remain protected. No amendment is inferred from approval of the new policy.

Unblocked next work: D-045/D-046 normal-perception routing/qualification. Losing
centering selects TRACK with SEARCH_FORWARD profile, not ATTACK's approach cap.
The prepared normal-perception contract reflects that correction.
