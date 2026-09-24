# D131 proposed contract: bounded B9.4 push-through

PROPOSAL ONLY, prepared after D130 completion. Adopt under D051 before dependent
edits; no positive tuning, physical result, gate or motor authorization follows.
Keep EDGE_PUSH_THROUGH_MS's shipped literal0, with supported range0..100ms.

## Public boundary and eligibility

Integrate with the real Robot and Escape owner, before Escape starts any row.
Changing Guard alone is insufficient: edge.cpp currently starts a row first.
Add default-false `EscapeSample::push_eligible` and a read-only
`Escape::pushThroughActive() const` query. Existing callers gain no authority.
Guard alone continues to demand immediate escape for white even in a positive
fixture, because it has no ATTACK/opponent/timing context. Replace its zero-only
assertion only after bounded integration; reject durations above100ms.

Robot computes eligibility from previous state ATTACK (`tick_.entry`), current
valid sampled opponent perception, current effective centered bearing, effective
confirmed FC, and currently normalized raw FC. FC is bit0x02 after XOR with
OPP_ACTIVE_LOW_MASK; electrical high does not itself mean detection. FL+FR alone
can be centered but cannot qualify without FC. Preserve ordinary permission,
source freshness, fault and full-duty centered-contact requirements.

Escape can enter the exception only with no active escape/fault, a new admitted
line observation, nonzero front-only mask1/2/3, permission and push_eligible.
Three/four-white and rear-white always retain original escape/fault priority.
Retained white may continue an already admitted window while the existing source
owner still regards it as available; it cannot start or renew a window. Timers
advance on supplied time even without a newly completed line sample. No new
sensor reads, clocks, grants, event types, tunables or network controls.

## Finite lifecycle

- Start at the first eligible admitted front-white observation. Keep that anchor;
  changing which front bit is white, repeated observations, mode/bearing changes,
  contact or ALL_IN never restarts it. Unsigned elapsed>=duration closes the
  exception on that call; the exact bound is not another allowed push tick.
- While white persists, raw FC clear, lost eligibility/centering/permission,
  any rear bit, pattern fault or expiry ends the exception. With permission and
  white, run ordinary escape selection on the same observation, preserving true
  mask, row direction, immediate braking and fault priority. No favorable retry.
- A newly admitted all-black observation ends the window without inventing an
  escape row or inward-exit measurement. Expiry while black requires no movement.
  The allowance remains spent: a subsequent white episode must escape normally.
- Rearm only after an actual Escape exit with its existing fresh-all-black plus
  completed-row condition, or reset. Loss of permission consumes an active
  allowance; restoring permission cannot resurrect it. Before GO, no allowance
  or new line fault is created. Existing actual-escape permission-loss latching
  remains unchanged.

This no-renewal policy explicitly bounds repeated white/black chatter; it may
choose an earlier escape on a later edge until a real recovery completes. It
does not claim physical tuning or that a positive duration is safe on this robot.

## Same-tick arbitration and accounting

The exception authorizes ATTACK only. Normal route/stall evaluation follows
runEscape in the current pipeline. If that evaluation would leave ATTACK while
front white is still being deferred, revoke the allowance and enter ordinary
Escape that same tick. In particular, a would-be stall must not start REFLANK,
consume its limiter allowance or emit a false executed-stall transition first.
Do not suppress detection forever or discard the real edge history.

A dedicated revoke path or one bounded second Escape call is acceptable only
after the first call deferred and started no row. It must start at most one actual
row, perform no replacement, and execute no second perception/contact/Governor
pass. Publish only the final state/output. STOP/fault/permission inhibition wins.

Preserve the real line mask and new-white event through fusion, edge history,
stall and recording; do not substitute a black mask to bypass arbitration.
Deferral emits no actual escape-enter/exit/replan or inward-history pulse.
Replans remain0 until actual entry, then follow the unchanged three-replacement
budget. Existing D129 timing exclusion on line evidence remains unchanged.

## Storage, defaults and verification

Prefer reusing Escape's mutually exclusive storage: a named union for the
push-start timestamp versus the existing uint32 replan counter, and a byte enum
for IDLE/ESCAPING/DEFERRED/SPENT replacing active_. Use ESCAPING=1 to retain the
old default boolean representation where possible. Never read the wrong union
member or expose timestamps as a replan count; initialize counter0 on real entry.
This is a proposed implementation choice, not proof of target fit. Adding fields
and relying on if-constexpr to remove their object storage is insufficient.

The proposed input bool may occupy existing sample padding; verify actual host
size/offsets and preserve prior default/profile layouts where possible. No extra
compiler feature option or macro alias for the duration: the existing literal
config.h declaration remains its sole tuning source and registry-compatible.
Native image/loader fit and full-source WCET remain pending until actual builds
and physical measurements; historical default modeled free span is only16bytes.

Independent new spec-derived tests precede execution. Preserve all40 established
locked files and run them with original0. New positive-duration copied-source
fixtures exercise20ms and100ms; explicit101/overflow values must fail admission.
Cover all masks, both front sides, before/at/after deadline, wrap/duplicates,
fresh/retained/stale observations, raw polarity/FC loss, confirmed centering,
missing contact, early black/reappearance, no rearm, actual Escape completion,
STOP/faults, same-tick stall, real Runtime/MotorGate writes and bounded fixed-seed
streams. Test actual Robot integration, not just a pure helper. Native build
policy must retain exact profile flags, defaults and per-run upload guards.

Read-only map supporting this proposal: Robot order fsm_robot.cpp:99; previous
state132; opponent276; runEscape397; checkStall734; final contact/governor770;
publishEdge869; line provenance fsm_line.cpp:24/89; Escape step edge.cpp:378;
existing episode storage edge.h:230; polarity opp_fusion.cpp:23; literal duration
config.h:205. Line numbers describe the D130-complete source, not future edits.
