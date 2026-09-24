# P4.4 bounded push-through preparation

Proposal and source map only, 24 September 2026. Not an adopted behavior change,
implementation, positive tuning value, hardware result or motor permission.

## Existing requirement and actual gap

BEHAVIOR B9.4 permits staying in ATTACK for at most EDGE_PUSH_THROUGH_MS when
only front line bits are white, the opponent is centered and FC is on. FC clearing
requires immediate escape. Default0 disables the exception; maximum100ms.
P4.4's20ms tuning steps require actual4.1 success with zero self-exits.

`src/core/edge.cpp:53` currently rejects every positive configured duration.
`Escape::step` starts a row before invoking Guard; merely changing Guard cannot
implement the exception. `Robot::runEscape` provides current confirmed centering
and line provenance, but not an explicit prior-ATTACK/FC eligibility contract.
Its new line events, source freshness, faults and existing escape lifecycle must
remain visible even if the exception temporarily defers escape entry.

## Decisions to make before dependent edits

1. Specify raw versus confirmed FC clearance. Recommendation: any newly observed
   raw FC clear cancels immediately, while entry requires current confirmed
   centered FC and an already active ATTACK. A saved snapshot or a new TRACK
   observation cannot create exception authority.
2. Specify timer anchor, permitted retained-line behavior, and rearming so white
   chatter, target/state changes or duplicate observations cannot renew the
   window indefinitely. Use wrap-safe supplied time; expiration at the exact
   configured bound must enter ordinary escape. Explicitly define what happens
   when all-black appears before expiration rather than hiding it as a fake mask.
3. Preserve immediate STOP/permission/fault/rear-white and3/4-white priority,
   full-duty centered-contact rules, actual escape/replan accounting and normal
   target-loss braking. Do not infer contact merely because push-through is active.
4. Resolve memory/build admission before choosing storage: the default image's
   historical modeled free span is only16bytes. Prefer no default-off state/layout
   growth if practical; an extra option must not become a competing tuning source.
   Verify actual native fit later rather than treating a desktop sizeof as proof.

## Verification and ownership boundary

Keep config.h's shipped duration0 and all40 established locked files unchanged.
Their immediate-escape expectations are the correct default behavior. New
independent tests should use isolated positive-duration fixtures, actual Robot /
Runtime / MotorGate paths and boundary samples (before/at/after expiry), wrap,
all masks, FC/centering loss, STOP/faults, stale/retained sources, no timer restart,
existing escape priority and bounded randomized streams. Check default regression
and layout/target consequences, as well as tool configuration admission.

Read these original requirements again when adopting the implementation contract;
these recommendations do not replace B9.4 or silently grant tuning authority.
