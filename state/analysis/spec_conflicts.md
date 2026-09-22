# Open specification conflicts — 2026-09-22

Current resolution index: accepted decisions D-017 through D-046 resolve the
specific conflicts identified in their dated entries below. Earlier "pending"
paragraphs are historical where a later resolution applies. SC-AF and the explicit
SC-R inhibited-recovery option are now approved as D-047/D-048. Their dependent
integration is covered by the D-054 Escape component; full Robot integration is
pending. D-055 resolves SC-G's WAIT policy; physical validation stays open.

Latest D-049/D-050 resolve pushed-out and replanning details. D-051 delegates
remaining engineering choices without further questions; select/document the
recommended course and retain explicit limits and regression requirements.
Missing hardware facts, measurements and phase gates are still not evidence.

Verified against the supplied files, not hardware. Recommendations are UNAPPROVED
except SC-C (D-017), SC-D1 (D-018), SC-J's START anchor (D-019) and SC-D2's
persistent/all-white policy (D-020), SC-M (D-021), SC-N (D-022/D-023), SC-K
(D-024), SC-E1 (D-025), SC-L (D-026/D-027) and SC-E2 (D-028), explicitly approved below. User's later
instruction to proceed assuming hardware works permits
continued eligible software work; it supplies no circuit choice, measurement,
pin approval, motor authorization, or phase gate.

| ID / sources | Consequence | Options and recommendation | Decision needed / regression evidence |
|---|---|---|---|
| SC-A HARDWARE 5.6; BEHAVIOR B1/B13; P2 B6 | START and both buttons short A1 to ground; distinct decoding impossible | A distinct-voltage circuit designed/approved by team; B change STOP interaction. Recommend A if both-held STOP retained | Human approved circuit or interaction, measured voltage windows; all four inputs, noise/bounce/held-at-boot/STOP in every state tests |
| SC-B B4.1/B16; AGENTS R4; HARDWARE 8; P2 B2 | 10+1500=1510 us exceeds both 1000 us period and <800 us execution; stale samples cannot count as fresh | A asynchronous capture with explicit cadence, timestamp/age and stale-fault rules; B measured shorter acquisition only if approved. Recommend investigate A first; full 1500 us acquisition still cannot restart each 1000 us on same pins | Human approves semantics after bare-board validation; fresh/late/stale/all-timeout/wraparound tests and complete 5 min target WCET; no timeout/tick change made |
| SC-C B6/B16; R6; D-012 | At 9 V: opener 0.85*11.1/9=1.04833 -> 1; search 0.30 becomes 0.37; final slew can exceed 0.02/ms | A cap and slew final electrical duty after compensation, immediate brakes exempt; B nominal caps plus a separately specified final envelope. Recommend A | Human decides cap/slew domain; sweep 9.0/11.1/12.6 V, contact/centering loss, reversals, voltage changes, finite output, exact/adjacent limits |
| SC-D1 B2 step 1; B3; B13 | Early return can suppress START/countdown, calibration, warnings/snapshot, cancel/STOP | A update input/state and gated-state services before motor-output gate; B explicit separate service stage. Recommend A with documented order | Human approves tick ordering; 5099/5100 ms, cancel/STOP/boot-held, 1.5–4.5 s calibration, last-300 ms snapshot tests |
| SC-D2 B2 step 3; B4.2–4.4; R5 | All-four-white has no black direction; rising-only trigger misses pre-existing/persistent white and exhausted escape | A inhibit/brake when direction unknowable and require human recovery; B specified bounded last-safe-direction recovery with physical evidence. Recommend A pending ring safety evidence | Human chooses all-white response and persistent-white/replan rules; all 15 nonzero masks, white at GO, sustained/re-entry/replan-limit tests; locked tests authored only after decision |
| SC-E1 B11.3; B6/B9; R5/R6 | ALL_IN unconditional full duty can outlive centered contact and edge eligibility | A ALL_IN suppresses stall detection only; retain centering/contact/governor/edge exits; B separately redesign policy. Recommend A | Human approves transitions; center/contact loss, target loss, every edge mask, bounded/disabled push-through, expiry and wrap tests |
| SC-E2 B15 | Finite 4096-event buffer cannot guarantee unlimited lossless events | A bounded event budget + explicit latched overflow/dropped count and invalidated evidence; B greater capacity with proven bound. Recommend A plus sizing evidence; no silent overwrite | Human approves overflow behavior, retention choice and match-duration bound; 4095/4096/4097, frame independence, simultaneous events, dump, saturation tests |
| SC-F PLAN schedule/P2 early tracks vs AGENTS 8 | Parallel P2 could bypass one-active-phase rule | A keep sequential gates; B specific approved early driver scope. Default A | Scheduling clarification only when early P2 work requested; no strategy/HAL implementation during P0 |
| SC-G B12 WAIT vs PLAN 6.2 | Straight DRIVE without pivot may not evade laterally | Defer to P5 design review; do not invent another opener | Human geometry/behavior decision before WAIT implementation and physical proxy test |
| SC-H P7 7.1 vs R7 | Command labeled build also uploads | User kickoff explicitly resolves build-only command to `tools/flash.sh app --match --compile-only` | Script tests ensure no upload/reset/start for every flag order; actual upload remains separately authorized |
| SC-I P0 0.2 counter + R3/R4; RouterBridge source | Monitor allocates String and RPC can wait; notify mutex can wait indefinitely | A explicit exception for inert P0 diagnostic only; B design/verify bounded transport. Recommend B for firmware, A only if human explicitly scopes diagnostic exception | No blanket R3/R4 waiver inferred. Matrix/RAM-counter demo can be prepared; requested Monitor round trip stays pending. Source evidence: P0_G3.md/P0_G4.md |

Additional component/source discrepancies (purchased revision, QTR VIN transients,
PWM capabilities and upload transport) are in P0_G1 through P0_G6. They are fact
verification blockers rather than authority to change HARDWARE, config pins, or D-005.

Protected decisions are separate: accepting any one row does not approve the others.
The original question workflow below is historical where D-051 delegates an
engineering choice. Record the selected recommendation and regression scope;
do not manufacture physical evidence, human gates or motor-run authorization.

## P1 contract audit follow-up (2026-09-22)

SC-F scheduling update: D-016 permits P1 host development only while P0 acceptance
remains pending. It does not permit P2 HAL implementation or imply a passed gate.

SC-J (B3/B13, separate-context spec audit): "starts at the release" does not say
whether the hold anchors to the first raw release sample or debounce completion.
Both-held STOP debounce/hold anchoring and recovery interaction are also unspecified.
Options: A anchor accepted START release to debounce completion (conservative extra
20 ms); B anchor to the first sample once stability is proven. Recommend A. Human
decision required before button-to-gate integration. Independent Gate accepts an
explicit logical event time; Buttons exposes both edge and qualification times
without connecting them. Regression: interrupted releases, 19,999/20,000/20,001 us,
5,099,999/5,100,000 us from the approved anchor, boot-held/reset and wraparound.

SC-K (B3): calibration endpoint inclusion, definition of spread, missing/invalid
sample treatment/minimum sample count, warning persistence and snapshot aggregation
(latest versus OR during the final 300 ms) are unspecified. Options: explicitly
define sample eligibility/aggregation and boundaries, or defer those services.
Recommend defining these before integrated B3 work; only the hold timer proceeds.
Human decision needed; regressions cover 1.5/4.5 s boundaries, exactly 2 dps spread,
invalid/no samples, and 4.1/4.8/5.1 s warning/snapshot boundaries.

SC-L (B5.2-B5.4): simultaneous rear-left/rear-right bearing, no-target initial
bearing, impact magnitude interpretation and contact-latch lifetime are not fully
defined. Options: explicit perception policy or defer affected fusion stages.
Recommend retain only unambiguous B5.1 filtering until the relevant contracts are
settled. No policy is approved. Regressions: all 128 masks, group priorities,
opposite-side/rear conflicts, finite angles and contact reset/lifetime.

## Approved resolutions — 2026-09-22

- SC-C RESOLVED by D-017: user "Approve A for the governor". Final electrical
  compensation -> state caps -> acceleration slew; braking/cap reductions immediate;
  full duty requires centered contact. B6 updated visibly; regression work follows.
- SC-D1 RESOLVED by D-018: user "Approve A for tick ordering". Gated-state
  services precede output inhibition. B2 updated; this does not resolve SC-J/K
  service semantics or SC-D2/SC-E arbitration/edge/ALL_IN conflicts.

SC-M (B4.2/B6, relevant during governor implementation): B6 specifies an
EDGE_ESCAPE reverse cap, but B4's forward escape rows do not state their base
duty/cap. Options: A explicitly reuse EDGE_BACK_DUTY for the forward segments;
B specify a separate measured/configured forward cap. Recommend decide with the
escape policy before implementing those segments; no value selected. The
governor implements only named, already specified B6 profiles and leaves profile
selection to the future FSM. Regression: forward escape rows at low voltage,
left/right bias, cap/slew limits and all-white behavior. D-017's pipeline approval
does not by itself choose this missing cap.

## Approved continuation — 2026-09-22

- SC-J START anchor RESOLVED by D-019, user "Approve A: after debounce": the
  complete hold starts on the completed release-qualification tick, including
  delayed calls. Both-held STOP timing/recovery and SC-K are still unresolved.
- SC-D2 persistent/all-white policy RESOLVED by D-020, user "Approve A: inhibited
  all-white fault": persistent white after the permission gate requires escape;
  all-white latches zero duty and disabled motors until reset. Other escape exits
  require all black plus script completion. Acquisition, actual scripts, SC-M
  forward duty and direction after exhausting replans remain pending. Default
  push-through stays disabled; this approval does not enable a positive window.
- SC-M RESOLVED by D-021, user "Approve A: reuse 0.80": forward segments request
  EDGE_BACK_DUTY as base and use it as final cap; biased segments request 70% on
  the inner side. The approved governor still compensates/caps/slews each side,
  so final ratio may differ. Pure forward demands and governor profile are
  implemented; timed/heading-held scripts and physical behavior remain pending.

Next relevant motion contract (SC-N, B4.4/B6/B7): `straight` calls for a small P
heading correction without specifying its gain/limit, while timed fallback turns
and escape durations are described as voltage compensated without a duration
formula separate from B6 duty compensation. Options: define the gain/limit and
whether/how duration compensation combines with duty compensation, or defer the
affected timed primitives. Recommend explicit definitions before implementation;
do not invent an additional compensation factor. Needed tests: nominal/low/high
voltage, exact timeouts, wrap, heading signs, saturation and IMU fault transitions.

SC-N RESOLVED by D-022/D-023 (2026-09-22): user approved bounded heading
correction using K_TURN_PER_DEG with min(TURN_MIN_DUTY, abs(base)) limit, and
voltage compensation once through duty with unchanged configured/fallback timing.
These decisions do not establish physical trajectory or measured timing.

SC-K RESOLVED by D-024: [1.5,4.5) s finite IMU-valid samples, max-minus-min
spread, minimum two valid readings, any invalid sample rejects, preserve bias on
rejection; final-second warning latches and final-300ms snapshot retains latest
confirmed mask. Hardware sample freshness and actual calibration remain pending.

SC-E1 RESOLVED by D-025: ALL_IN suppresses stall checks only for ALL_IN_MS;
centered contact still gates full duty, target loss brakes, edge priority remains.
Re-flank/FSM implementation and its required safety regressions are still pending.

SC-L RESOLVED by D-026/D-027: deterministic rear/side conflicts and no-history
bearing validity, front-side recency ties, IMU-valid horizontal impact norm, and
contact latch restricted to centered ATTACK with explicit clearing/re-entry.

SC-E2 RESOLVED by D-028: preserve earliest4096 events; explicit overflow latch,
saturating rejected count, continued frames and incomplete-evidence dump marking;
no motion effect. Recorder buffering/transport implementation remains pending.

## Pending P1 filter/detector decisions — 2026-09-22

These options were presented separately to the human; no approval is recorded.
They do not block the existing B11.3 rolling limiter and D-025 suppression timer.

- SC-O1, B5.5: chase-window anchor and contact history are undefined. A: begin on
  the first front-only TRACK/ATTACK observation, retain across TRACK/ATTACK,
  end when pursuit ends and remember any contact cue; a qualifying edge can
  mark the current valid world bearing within PHANTOM_WINDOW_MS. B: defer.
  Recommend A; human choice required. Test state transitions, contact then lost
  cue, exact window endpoints, absent/invalid headings and edge-tick ordering.
- SC-O2, B5.5: retained phantom count/replacement is unspecified. A: one marker,
  a new qualified event replaces it and restarts PHANTOM_MS. B: specify another
  bounded retention policy. Recommend A; human choice required. Test replacement,
  expiry, circular angular boundaries, close/side overrides and timestamp wrap.
- SC-P, B5.6/B14: heading change and recovery from a stuck declaration are
  undefined. A: continuous detection for OPP_STUCK_MS with accumulated heading
  span (max minus min) strictly above 360 degrees; unavailable/invalid IMU restarts
  qualification; a declared fault remains ignored until reset. B: defer.
  Recommend A; human choice required. Test exact time/angle limits, oscillation,
  return to the original heading, missing IMU, clear/reassert, fault pulses/reset.
- SC-Q, B11.1: "extra triggers" does not define whether deflection bypasses the
  timer, or which wheel/governor stage supplies "commanded duty". A: STALL_MS of
  continuous qualification OR earlier deflection strictly above STALL_DEFLECT_DEG;
  both require centered ATTACK contact, both forward final electrical duties at
  least STALL_MIN_DUTY, and no edge since contact. Keep displacement disabled.
  B: defer. Recommend A; human choice required. Test exact/adjacent deadlines,
  both wheel thresholds/signs, deflection signs, invalid headings, edge/contact
  histories and D-025 suppression without a hidden additional cooldown.

SC-O1/O2/P/Q RESOLVED later in this session by the explicit human approvals
D-029/D-030/D-031/D-032 respectively. Their recommendations above are now
accepted in those precise scopes. Interfaces are committed before tests/code.

Further script audit (no decision inferred):
- SC-R, B4.2 three-white/B4.4 exhausted replans: "toward the black side" still
  needs an explicit skid-steer direction/command mapping, including multiple
  black corners after exhaustion. Options: human-approved movement table or
  explicitly approved inhibited recovery. Recommend a concrete table supported
  by geometry/bench evidence before movement implementation. Test each 3-bit
  mask, replan-limit boundary, all-white priority and persistent white.
- SC-S, B4.3: both rear bits white supply no unique "away" direction; precedence
  against three-white table rows is also missing. Options: explicit deterministic
  direction/priority or deferred pushed-out recovery. Recommend decide together
  with SC-R; test every rear-containing mask with/without centered forward push.
- SC-T, B12 O1: simultaneous front/outer-side detections request both ATTACK and
  DEFEND_TURN. Options: front priority or outer-side priority; recommend explicit
  per-phase arbitration before SIDESTEP implementation. Test both mirrors and
  every simultaneous mask at each phase boundary. B5 bearing selection alone
  does not approve a script-exit rule.
- SC-U, B12 O2/O3 vs B2/B9: opener FRONT_TARGET exit is currently only an intent;
  the full FSM must reconcile literal ATTACK-on-any-front/snapshot with current
  centering and target-loss braking. Options: current perception selects TRACK/
  ATTACK or explicit opener-specific transition policy. Recommend current
  perception with all safety gates; obtain the protected decision before actual
  state integration. Test stale snapshot, off-center front, lost target and edge.

SC-T/SC-U RESOLVED by D-033/D-034 (2026-09-22): user explicitly approves
phase-specific SIDESTEP front priority and current-perception opener exits.
PIVOT still ignores front; later front outranks outer-side/rear in SIDESTEP.
Actual opener exits select normal TRACK/centered-qualified ATTACK, DEFEND_TURN
or SEARCH from the current target. Snapshot alone cannot authorize ATTACK.
Their dependent script contracts are committed d8f2327/ad0efb0; full Robot
state integration still requires implementation and tests, not another approval.

SC-J remaining logical STOP proposal presented separately: after BOTH qualifies
for BTN_DEBOUNCE_MS, start the entire BTN_LONG_MS; any observed release cancels
an unfinished hold; STOPPED stays latched until reset into normal boot/start.
No approval recorded yet for this proposal. Tests must cover boot-held BOTH,
bounce, qualification/long-hold exact and adjacent ticks, release at the endpoint,
delayed observations, cancellation, wrap and reset without motion permission.
SC-A electrical ability to distinguish BOTH remains a separate human circuit gate.

SC-J logical STOP RESOLVED by accepted D-035: the exact proposal above is now
approved. StopHold/Controller contracts are committed6a15674; implementation and
new locked tests follow. SC-A physical decoding remains unapproved/unverified.

Next integration choices presented (not yet approved):
- SC-V, B9.1/B9.2: wheel mixing, the extra15-degree pivot and small ATTACK
  corrections lack numbers. A: left/right=base+/-correction bounded[-1,1];
  TRACK correction=K_TRACK_PER_DEG*bearing plus signed TURN_MIN_DUTY on the
  +/-15 front-only rows, using SEARCH_FORWARD governor. ATTACK correction uses
  that gain limited to min(TURN_MIN_DUTY,base), with the ATTACK governor.
  B: defer to measured gains. Recommend A. Test seven front rows, mirrors,
  centering counts, loss/braking, approach/contact, finite limits and low voltage.
- SC-W, B11.2: SWING arc duty and first alternation direction are absent.
  A: outer request TURN_DUTY, ratio REFLANK_ARC_RATIO and duration-only
  REFLANK_ARC_MS; choose right first when earlier side rules cannot choose,
  then alternate. B: defer. Recommend A. No invented sweep cutoff. Test exact
  BACK/arc times, pivot, charger skip, side-history/edge metadata ties and mirrors.
- SC-X, B11 versus B9: D-034 covers opener exits only; re-flank's literal
  direct ATTACK reacquisition still bypasses centered qualification. A: normal
  current-perception TRACK/qualified ATTACK, DEFEND_TURN or SEARCH, preserving
  D-027 fresh contact. B: defer. Recommend A. Test centered streaks/interruption,
  all current target groups/loss, stale contact and all-edge priority.

SC-V/SC-W/SC-X RESOLVED by accepted D-036/D-037/D-038 on 2026-09-22. The
human explicitly approved all three exact proposals above. Implement and test
their policies; approvals do not constitute test or hardware evidence.
The distinct established locked-test conflict with D-035 is approved for exactly
one documented case by D-039; see P1_stop_locked_conflict.md for the full edit.

Further bounded integration audit (questions pending; no approval inferred):
- SC-Y, B11.2/B2: natural SWING arc completion and TURN_IN continuation are not
  specified. A: arc expiry without inner trigger exits via D-038; TURN_IN retains
  its captured command until front detection/completion/timeout, then D-038.
  Edge/STOP always preempt. B: defer. Recommend A. Test all masks during phases,
  natural/triggered transitions, no retarget, exact expiry, timeout and edge/STOP.
- SC-Z, B8/B5: "last seen side" could be front-sensor history or latest selected
  bearing. A: sign of latest valid nonzero relative bearing, retaining side for
  zero and default right when unknown; existing SIDESTEP hint controls first scan.
  B: last front side only. Recommend A. Test side/rear after opposite front,
  zero/conflicted/invalid bearing, no history, hint precedence and mirrors.
- SC-AA, B8/B7: full-sweep SEARCH fallback on mid-scan IMU loss is unspecified.
  A: directed yaw while valid; on loss latch timed remaining sweep clamped0..360
  at TURN_MS_PER_DEG, starting at that observation; recovery cannot restart it.
  No IMU at entry uses full360 timing; do not inherit the700ms short-turn cutoff.
  B: defer. Recommend A. Test no IMU, partial/opposite progress, recovery, exact
 720ms/remaining-time endpoints, wrap and absence of fabricated heading samples.
- SC-AB, B11 side recency: an unseen front sensor is not ranked against seen.
  A: unseen is least recent; both unseen/equal recency fall through to approved
  alternation. B: any unseen falls through. Recommend A. Test both one-unseen
  orientations, both unseen, ties, known older side and higher-priority edge side.

- SC-AC, B4.2 head-on row: bare "Brake" and omitted reverse duty lack explicit
  values. A: one full TICK_US brake, then EDGE_BACK_LONG_MS at EDGE_BACK_DUTY;
  retain the specified EDGE_TURN_FULL_DEG turn and governor. B: defer row.
  Recommend A; question presented, approval pending. Test exact/adjacent brake
  and reverse endpoints, delayed calls, mirrors, low voltage and immediate brake.
  Last-opponent-side mapping remains an integration choice, not decided here.
Additional B4.4 completion/replan gaps are documented in
P1_escape_row_contract_audit.md; no new movement policy is silently implemented.

Front-arbitration audit (not approved; see P1_front_arbitration_contract_audit.md):
- SC-AD, B9.1/D-034/D-038: entry observation's count anchor is unstated. A: current
  eligible centered observation at normal TRACK entry is first of three, with no
  script/preempted count carried over. B: begin next tick. Recommend A; requires
  human decision before full FSM, with exact-entry/threshold/reacquisition tests.
- SC-AE, B9.3/B1 versus B2 item8/B10: front loss says SEARCH but a remaining
  side/rear target says DEFEND_TURN. A: immediate zero-duty brake on the loss
  tick; current side/rear routes DEFEND_TURN, none SEARCH; brake overrides that
  tick's new state request. B: SEARCH for loss tick, next tick re-arbitrate.
  Recommend A; human decision needed. Test all residual masks, TRACK/ATTACK
  loss, prior full duty, next tick, fresh contact and edge/STOP precedence.
Standalone FrontQualification does not select either policy.

2026-09-22 human resolution before requested pause: SC-Y/Z/AA/AB/AC/AD/AE are
RESOLVED by D-040/D-041/D-042/D-043/D-044/D-045/D-046 respectively. Exact user
approvals are recorded in DECISIONS.md. Their earlier pending descriptions are
historical. Dependent implementation/tests remain pending; other protected
physical/escape/WAIT issues are unchanged. Do not request these approvals again.

2026-09-22 resumed integration audit:
- SC-AF, B4.2 head-on row versus D-041/B5: D-044 fixes timing/duty only, not
  which history means "last seen opponent side". The existing front-side history
  and latest selected bearing can disagree. A: reuse D-041's latest valid nonzero
  selected relative-bearing sign, retain side at zero, default RIGHT; B: retain
  this as an unresolved dependency. Recommend A for one explicit consistent
  definition. Human decision required before automated head-on side selection.
  Tests: side/rear after opposite front, zero/unknown/conflicting bearings,
  reset/default, mirrored head-on and escape precedence.
- SC-R remains movement-geometry dependent. Proposed bounded safety option:
  three-white or exhausted replans latches an inhibited escape fault until reset,
  preserving all-white priority; alternative is defer those cases for a measured
  movement table. This would replace the specified black-side movement only
  with explicit human approval, never silently. Test four three-white masks,
  exact replan count, all-white, black after fault, reset and zero final duties.
- SC-S retains pushed-out ambiguity for both rear sensors. Proposed explicit
  ordering: all-white/three-white recovery first; among remaining rear-containing
  masks in a centered forward push, a single rear side pivots45 degrees away
  then moves forward per B4.3; both-rear uses the side opposite the latest selected
  opponent side (RIGHT default history means LEFT pivot). Alternative: defer
  ambiguous pushed-out selection. No recommendation is adopted without a human
  decision and physical validation. Test every mask/centering/duty sign, mirrors,
  exact phase limits and low-voltage governor bounds.

2026-09-22 resumed human approvals: SC-AF is RESOLVED by D-047; SC-R's
three-white/exhausted-replan movement policy is RESOLVED by D-048. The exact
proposals were explicitly approved. Selection/inhibited recovery tests and
implementation remain pending; replan trigger/lifecycle and SC-S pushed-out
ambiguities are separate. Do not re-ask these approved policy questions.

2026-09-22 further resolutions: D-049 approves SC-S's exact proposed pushed-out
priority, direction and final-duty predicate. D-050 approves the exact bounded
replanning lifecycle in P1_escape_remaining_contract.md. D-051 delegates remaining
engineering decisions to Codex without further questions. Record future choices
and regression requirements explicitly; unknown facts or absent evidence do not
become verified through this delegation. No additional decision requests pending.

2026-09-23 component resolutions: D-054 defines Escape call-entry replan priority,
permission-loss inhibition, consumed-context validation and current-yaw-only
inward evidence. D-055 RESOLVES SC-G using full SIDESTEP_R after a bounded ordered
cue, visibly amending O4; the physical latency/evasion tradeoff is unmeasured.
D-056 defines pure contact preview before one final commitment so a stall-induced
state change never requires duplicate contact or governor advancement. These
interfaces preceded their independent tests. Full Robot ordering, physical A1
decoding, QTR acquisition/freshness and bounded Bridge transport remain unfinished.
