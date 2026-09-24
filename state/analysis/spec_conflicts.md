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

2026-09-23 D-057/D-058 resolve logical service START routing and MODE gesture
semantics; their independent host tests and scoped reviews are recorded in
P1_start_routing_validation.md and P1_menu_validation.md. Physical A1 decoding
and actual service consumers are still separate dependencies.

D-059 resolves Robot GO coordinate ownership: unreset continuous yaw stays with
Fusion; match motion uses a logical origin established before same-tick entry.
Ordinary IMU absence preserves timed fallback, including a nominal initial
coordinate and one first-recovery anchor when no measured history exists.
Malformed healthy coordinates instead latch an explicit inhibited fault. This
does not authorize provider resets, erase sticky history or prove hardware yaw.
Contract/source review and numerical boundary finding: P1_heading_validation.md;
full production Robot integration remains unfinished. P1_robot_api_proposal.md
is still an unadopted recommendation, not an implicit further decision.

2026-09-23 production resolution: D-060 adopted the Robot transaction and event
contract before implementation. D-061 then explicitly resolved legitimate
unknown-bearing DEFEND entry as an800ms bounded zero-demand wait, with retained
deadline after real capture and unchanged edge/STOP priority. Initial safe-inhibit
failure, exact review correction and independent regressions are preserved in
P1_robot_failure_analysis.md. The complete P1 default core now passes895 cases,
normal+sanitizers, fresh full-core review and actual inert app target compilation.
See P1_robot_validation.md. Older "Robot unfinished/unadopted" descriptions above
are historical, not current blockers. No established locked test was weakened.
SC-A physical button decoding, SC-B physical QTR freshness/timing and SC-I bounded
Bridge transport remain unresolved dependencies; no human phase gate passed.

2026-09-23 SC-I P0-only follow-up: D-062 selects a fixed mon/write notification
through the existing internal UART, never starting stock Bridge. Contracts precede
independent tests/implementation; scoped source and exact binary reviews PASS.
Actual inert upload and counters4..11/56..63 observed: P0_counter_validation.md.
This closes the fixed P0 counter round-trip dependency. Production recorder/
Immediate-mode transport, complete-loop timing, Linux-down/fault behavior and
original physical/human gates remain separate; no R3/R4 exception was taken.

2026-09-23 ADC API dependency — AGENTS R4, P0 0.4, HARDWARE A0/A1 and future
power/UI HAL: installed stock analogRead uses indefinite ownership/completion
waits, including warm calls. Source/binary proof: F-078 and
P0_adc_installed_contract_20260923.md. Consequence: using it directly in the
runtime tick cannot satisfy bounded fault paths. Options: A investigate an
installed-supported bounded acquisition/driver contract with explicit freshness,
ownership and fault behavior when HAL work is eligible; B use stock synchronous
reads and relax R4. Recommend A; B is not authorized. D-063 permits only setup
microbenchmarking, not a runtime solution. F-079's139..140us observed warm costs
do not remove the indefinite-wait proof. A future delegated design decision must
precede dependent HAL. Required regressions include missing conversion interrupt,
contention, invalid/error result, stale sample, wrap, cancellation/recovery and
complete on-target tick WCET. No driver/API behavior or deadline is invented here.


## SC-AG � installed IMU transport versus R4/valid-data requirements (2026-09-23)

Sources: AGENTS R4; P0 G6; BEHAVIOR B7/B14; F-084 and
analysis/P0_imu_installed_contract_20260923.md sections Installed synchronous API,
Installed timeout/fault paths, and Pinned Adafruit source. Installed Wire1 is
now verified as I2C4, but synchronous completion can wait500ms per message and
bus/config ownership waits indefinitely. Wire discards stopBit, causing two
STOP-terminated transfers rather than the requested repeated START. Source and
actual loader disassembly imply a BERR-only wake can return success; not measured.
Adafruit discards burst-read failure, returns success from getEvent, and reset
polling can remain indefinite after BusIO returns0xffffffff for failed reads.

Consequence: successful compilation or a nominal read cannot prove a bounded,
truthful production acquisition. Do not mark repeated/stale/failed data fresh or
put unchanged stock reads inside the required under800us control tick.
Options: A) At the eligible HAL phase, investigate a supported bounded acquisition
path with explicit per-operation deadlines, error propagation and sample-age
semantics. B) Propose a separate, explicit timing/safety requirement change.
Recommendation A; current D-066 only authorizes never-executed compile/link
compatibility, not either runtime policy. No loader/library patch or waiver now.

Decision needed before dependent runtime implementation: concrete supported API,
ownership, transaction semantics, deadline/cancellation, freshness and failure
contract with installed evidence. D-051 delegates engineering selection, while
physical facts and human phase gates remain required. Regressions must include
NACK, BERR, arbitration loss, absent/stuck bus, lost completion, contention,
partial reads, reset failure, duplicate/stale samples, wrap and cancellation;
measure complete worst-case tick and actual waveform/config/sample generation.
These future tests cannot be replaced by this compile-only probe.


## G2 runtime dependencies and SC-B follow-up (2026-09-23)

Installed PWM/IRQ audits F-086/F-087 and D-067 compile-only compatibility do not
resolve SC-B. Arduino interrupt edge notifications have no hardware timestamp
FIFO; pending events can coalesce. attachInterrupt hides native errors, and
detachInterrupt leaves the line configured/owned with a source-level handler
race risk. Low/high level modes fail. Native disable, callback removal, pending
state, ISR/main identity and charge/rearm ordering each require explicit handling.
Source: P0_irq_installed_contract_20260923.md, HARDWARE3, B4.1/B16 and R4/R5.
Options remain measured bounded asynchronous acquisition with explicit age and
cadence versus a separately justified timing change. Recommendation remains to
investigate asynchronous acquisition before selecting semantics; no shortened
timeout/slower tick/stale-as-fresh workaround is adopted. Regressions must cover
already-LOW release, pending/stale/late/simultaneous/coalesced edges, timeout,
configuration errors, ownership, cleanup/rearm, wrap and ISR/main races, followed
by real sensor and full-tick measurements. D-051 delegates engineering choice;
physical proof and original phase eligibility still precede dependent HAL.

Separate later MotorGate dependency: analogWrite's digital fallback and ignored
errors cannot supply a fail-closed write boundary. Native explicit-period PWM
returns status, but exact channel routing, initialized clock/rate, shared periods,
zero/full duty and update/reversal behavior need validation. Whole pinctrl groups
can claim proposed QTR/EN pads. P0_pwm_installed_contract_20260923.md records this
without changing any pin, period or output policy. Recommend a checked native
path only within later eligible MotorGate work, with error-injection tests at
actual write boundary and separately authorized physical waveform/run evidence.
D-067 compiles APIs but selects no production driver or runtime workaround.


## SC-AH - B15 recorder capacity versus installed extension RAM (2026-09-23)

Sources: BEHAVIOR B15/B16, P2 B8, F-032/installed LLEXT evidence,
P2_frame_buffer_contract.md and P2_frame_host_size_20260923.json. At unchanged
LOG_HZ50, 200-second endpoint capacity10001 times26 encoded/status bytes plus
4096 times8 event bytes requires292794 bytes before metadata or application.
This exceeds the installed262144-byte LLEXT pool. Host ABI objects292848B are
a separate measured host result, not MCU allocation or free-memory evidence.
Consequence: offline buffers can be verified, but the default production recorder
cannot be called deployable or B8-passed. Options: A explicitly adopt B15's
conditional25Hz after a complete target memory budget/map; B investigate a
smaller evidence-preserving representation or supported memory placement with
installed proof. Recommend A as the existing specified fallback, conditional on
actual full-image headroom. D-069 selects neither; D-051 delegates a later
engineering decision, not measured evidence or gate acceptance. Required checks:
200-second endpoints/final flush, cadence and lost-slot accounting, event4096
overflow independence, actual target link/load/free RAM including stack/heap,
and complete tick budget. No silent rate/default change or loader patch.

SC-AH follow-up: F-089/P2_memory_budget_followup_20260923.md verifies that
Arduino's dynamic globals figure includes RAM-loaded code sections. Do not
add upload-file size again. Conditional25Hz still needs actual owner/full-image
link/load/metadata/peak/headroom evidence; no rate or build mode was changed.
D-070 offline owner is host-tested/reviewed, not integrated or target-qualified.


D-071/F-090 SC-AH follow-up: actual50Hz memory probe fails size check at356608B;
isolated25Hz passes at226584B. No production value changed. Conditional source
model peaks230072B in a pristine pool, not measured free RAM. Actual complete
HAL/loader/200s/dump/WCET evidence remains absent; see P2_memory_compile_validation.md
and P2_memory_loader_budget.md. A separate cadence adoption decision and regression
updates precede production change. Original B8/human gates remain pending.

SC-I/F-091 follow-up: final default ELF retains platform constructors and a loop
hook with indefinite mutex wait/conditional Bridge.update_safe despite inert user
setup/loop. Future eligible runtime integration must resolve actual platform hook/
startup paths as well as application calls, with installed source/ELF, fault-path
and timing evidence. The bench include boundary quarantines Zephyr's EMPTY macro;
future Arduino inclusion must handle that collision explicitly.


D-072/F-092 SC-AH follow-up (2026-09-23): development rate selection RESOLVED
through B15's existing25Hz fallback under D-051, visibly recorded in config/B16.
Actual current production-source probe compiles226584B; exact ELF matches D-071
candidate25.975hostcases normal+ASanUBSan and340tools pass after independent
expectation updates. Only LOG_HZ changed among76defaults; locked files unchanged.
Deployment acceptance remains OPEN: fullHAL/app/loader/freeRAM/200s/no-gap dump
and WCET are unmeasured. SC-I inherited Bridge/initializer paths remain. No
human/physical gate follows. See P2_rate_adoption_validation.md and fresh review.

## SC-AI: Native MotorGate backend and PWM settling (OPEN, D075 software boundary implemented)
References: HARDWARE5.4; AGENTS R1/R4/R6; F086/F088 installed PWM audit;
P2_motor_gate_contract.md and src/hal/motors.h Port contract.
Consequence: checked writes may update timer preload before the waveform changes;
EN HIGH immediately after a successful write cannot be called safe activation.
Arduino analogWrite also hides errors and can fall back HIGH. Host callbacks and
F093 target compilation do not provide native hardware behavior.
Options: implement/validate bounded checked GPIO/PWM+settle callbacks using actual
per-channel periods and exclusive ownership; or retain inhibition until such an
adapter exists. Recommendation: checked backend preparation with compile-only
validation, keeping activation unavailable pending actual latch/waveform evidence.
Decision authority: D051/D075 permit software choices; pin/electrical acceptance
and fresh motor-run authorization remain human. No stub may return success.
Required regressions: every native API failure, shared-timer/channel routing,
latched compare timing on reversal/brake, zero/full-cycle quantization, EN boot/
reset/fault waveforms and complete fault-path tick WCET. Existing MotorGate
37-case locked tests cover the software write boundary only.

D077/F096 SC-AI follow-up (2026-09-23): native software backend IMPLEMENTED,
HOST-TESTED, TARGET-COMPILED and independently REVIEWED. Installed clock/mode
proof and retrieved U585 manual/errata support the bounded fresh-UIF method;
actual callbacks enforce checked EN LOW, four writes, three fresh timer events
and strict deadline before HIGH. The original Gate/core/locked tests remain
unchanged. Final source c35726f4 and P2_motor_native_validation.md preserve tests,
compiled MMIO paths, all failure receipts and source-only inert guard review.
SC-AI physical/runtime acceptance remains OPEN: source/host/register simulation
cannot prove EN voltage, active waveform, real reversal/brake, pin ownership,
frequency or whole-tick worst-case timing. App integration and motor execution
remain unperformed; no physical or human phase gate is inferred.


## SC-AJ: Installed MSI automatic-calibration clock qualification (OPEN)
2026-09-23, references ES0499 Rev12 2.2.27 p16, RM0456 Rev6 pp491/511/916/920,
installed DT clk_msis msi_pll_mode1 and clock_stm32_ll_u5.c840-843.
Installed MSIS auto calibration is enabled. Spurious unlock can degrade clock
accuracy; MSISRDY and clock metadata do not prove lock. W/U expose an EXTI23
event shared with LSECSS; revisionX lacks it. Historical unlock cannot be excluded
by reading an unarmed event flag. This affects global timing/frequency assumptions,
not merely ADC scaling. Hardware revision/live frequency remain unmeasured.
Options: source-verified whole-platform detection/history/recovery with explicit
revision policy; or separately verified clock configuration. Recommendation:
resolve at platform integration before runtime deployment; do not retune clocks
inside a sensor HAL or assert readiness equals frequency accuracy. D078 keeps
stock settings for host/compile-only development and records the conditional
clock premise. No new physical or gate approval is inferred.
Needed before deployment: source/installed ISR ownership and boot-history policy,
silicon revision and clock qualification, tests for unlock before/during samples,
latched invalidity/recovery timing and effects on countdown/PWM/tick. ADC fixtures
must not fabricate an unavailable lock predicate. No human question needed to
continue the authorized software work; unresolved runtime issue stays visible.


## SC-B software resolution under D085, 2026-09-23

D051/D075 permit the explicit asynchronous acquisition decision before physical
acceptance. D085/47f4d9a implement finite native calls, conservative RC bounds,
2000us minimum starts/2500us complete-frame budget/6000us source-age expiry, and
separate fresh-line/retained-line/opponent admission. The original10us charge,
1500us timeout and1kHz control remain. Ambiguous timing inhibits; stale frames
cannot confirm/replan/exit or renew age. BEHAVIOR B4.1 and P2B2 visibly preserve
and supersede the incompatible synchronous-every-tick clause.

Host/sanitizer, independent native and actual target compile evidence is in
P2_qtr_native_validation.md/F107. Software semantics and implementation are now
resolved; physical color separation/cadence/uncertainty, pad handoff and full
5minute robot WCET remain pending. IMU600+motor150+ADC100 cannot be assumed to fit
800us; future scheduler must solve resource/timing contention. SC-AJ/F091 and
human gates remain unchanged. This is not physical SC-B acceptance.


D087 SC-A follow-up (2026-09-23): explicit raw-window decoder and fresh gesture
routing are being implemented under D051/D075. Defaults remain unconfigured;
overlap/unknown/provider failure cannot become valid NONE or unique START/BOTH.
The identical nominal START/BOTH circuit input remains OPEN and no wiring or
physical window is approved. Software tests use explicitly synthetic profiles.
See P2_button_routing_contract.md; implementation evidence will be in
P2_button_routing_validation.md. No phase/hardware acceptance follows.


D087 SC-A software follow-up: decoder/gesture routingb69fa12 is implemented, host/sanitizer tested, targetcompiled and independently reviewed. Raw windows remain unconfigured. This does not resolve or approve the physical circuit; SC-A remains OPEN. See P2_button_routing_validation.md.

## SC-AK: decision timestamp versus whole-tick acquisition timing (OPEN software contract)

2026-09-23. P2_imu_integration_contract.md34-36 requires post-acquisition decision
time; P1_robot_contract.md74-78 calls preceding t_us the complete-tick start.
fsm_robot.cpp170-174 enforces execution_us=completed_us-pending decisiontime.
Consequence: acquisition is excluded, or fresh sensor evidence appears future.
OptionsA: additive explicit start metadata preserving legacy default/lockedtests;
B: defer app timing. RecommendA under delegatedD051, with exact contract first.
Validate forward/wrap/half-range ordering, boundaries, duplicate/reset, GO/STOP,
realGate receipts and recorder propagation. Malformed timing alone retains the
existing incomplete-evidence semantics. No physical timing/clock acceptance.
See analysis/P2_app_integration_map.md for exactnextscope and API responsibilities.

D092 SC-AK software contract selected under D051/D075: explicit fixed-lifetime
acquisition start and full ordered duration, preserving legacy defaults and
decision-based sensor age. See P2_tick_timing_contract.md; implementation/tests/
review are pending. This resolves the specification choice, not physical timing.

D092 SC-AK software closure (2026-09-23): explicit complete timing implemented,
independently tested and fresh-reviewed PASS. Fullnormal/san1303main+87Gate cases
and61controlledtooling methods PASS; actual5451e99d target72sourcefiles/3ELFs
verified, no upload. See P2_tick_timing_validation.md. Physical complete800us and
SC-AJ clock calibration remain separate OPEN requirements.


## SC-AL: whole-application acquisition scheduling (OPEN software contract)

D093's fixed ADC owner resolves bounded app-level battery retention only. Current
runtime imu::Acquirer::read and Bus::acquireMotion execute atomic polling transfers
(imu_acquisition.cpp121-149, imu_bus_unoq.cpp464-501); they cannot yield to QTR.
QTR charge release requires [11,100)us, and long discharge sampling gaps can make
color ambiguous. MotorGate failure may invoke two settle passes; IMU source
completion excludes cleanup. See P2_app_schedule_dependencies.md for exact source
references and preserved source-age obligations. Existing per-call guards and a
nominal1kHz loop cannot establish R4's complete worst-case below800us.

Options: A) Audit and adopt resumable native IMU service with one unchanged600us
wall-clock deadline/poll budget, bounded advances and truthful pending/final
evidence, then compose the resource schedule. B) Defer scheduling until a physically
measured atomic schedule can support every guard. Recommendation A under D051/D075;
no new interface/semantic choice is yet frozen by this note. Installed/primary
peripheral-state verification must precede dependent implementation. No timing,
sensor-age or human gate requirement is relaxed.

Required regression evidence: interrupted protocol ordering/STOP, no partial
publication, aggregate deadline/poll budget including interleaved work, cleanup
exactly once, source-age/sequence continuity, QTR release service and complete
D092 timing. Physical color/rate/clock and full800us acceptance remain separate.


2026-09-23 D094 follow-up to SC-AL: bounded native Bus/Acquirer runtime implemented,
independent tests and target compile-only b495f085 pass. Separate pending/source
envelopes and original600us/8192 budgets retained; exact contract/validation in
P2_imu_resume_contract.md and P2_imu_resume_validation.md. This closes the enabling
API dependency only. SC-AL remains OPEN for actual app transaction/resource
admission, QTR sub-tick intervals, complete fault cleanup accounting and measured
full800us. P2_app_schedule_dependencies.md appended integration map/next contract.
No new timing allowance, physical assumption or human gate follows.


2026-09-23 D095 follow-up to SC-AL: actual fixed Transaction owner and terminal
MotorGate.halt implemented, independently tested/reviewed and target-compiled
9d6c0005. Complete real S/D/A/C receipts and real final recorder tail are owned;
ordinary timing overrun remains B14 count/log only. See app_transaction contract/
validation/review. SC-AL remains OPEN for actual native setup, source admission,
QTR/IMU/ADC resource scheduling, expiry/output/cleanup and measured full800us.
app.ino remains inert; no complete scheduler or hardware acceptance is implied.


2026-09-23 D096 SC-AL update: native Runtime/SourcePort composition now implemented; see P2_app_runtime_contract.md and validation.md for exact final host evidence. Explicit setup grants remain absent by default. Actual target final build4cb637f9 FAILS RAM276456>262144,14312B excess. Fresh review retains RAM BLOCKER; linked-source identity is not target acceptance. Next bounded memory dependency work follows P2_app_runtime_ram_audit.md; no recorder reduction, new hardware grant, full800us claim or human gate. NativeUART/localreset/calibration-snippet delivery remains pending.

2026-09-23 D097-D100 SC-AL/static-memory follow-up: passive IMU accessor and
reviewed app-only discovery policy make the actual frozen app compile at248308B
inert/248684B MATCH. Three-mode source/ELF/startup/import audits and independent
review PASS; see P2_app_build_validation.md. The former compile-capacity blocker
is closed for this exact source/policy, without reducing recorder capacity/rate.
SC-AL remains open for measured loadedRAM/stack and complete800us physical timing;
future native dump/local reset/calibration integration needs a new final image audit.

2026-09-23 D101 SC-AL memory update: attaching actual dump paths makes final
cache-source83600858 MATCH compile257784B but its conditional loaderpeak262400B
exceeds262144 by256B. D101-R1 remains BLOCKER; compiler success is insufficient.
P2_app_dump_target_audit.md records allocation order and exact identities. Next
consider lossless frame/status packing with explicit copied-read API, preserving
all5001frames/4096events/25Hz and raw bytes; no physical/load evidence fabricated.

2026-09-23 D102 disposition: D101-R1 conditional loader capacity CLOSED for
exact3bf0da00 source: lossless packed statuses preserve5001frames/4096events/25Hz
and raw evidence, actualtargetFrameBuffer3752B smaller; MATCHpeak258768/262144
fits allorderedallocations. Freshindependentreview and fullnormal/san PASS;
P2_frame_packing_validation.md and targetaudit/review are current evidence.
Historical D101 report remains its original failing checkpoint. SC-AL stillopen
for measured loadedRAM/stack/complete800us and future finalimage qualification.

## OPP-VIEW-1: geometric front-channel display ordering (2026-09-23, OPEN)
B0/HARDWARE3/D076/core frontView define indices0/1/2 as FL15/FC/FR15; D088 matrix contract and ui_display.cpp index0/1 positions as center/left. Consequence: sensor-view geometry can misidentify two channels. Exact references and evidence: P2_opp_view_design.md. Options: A) presentation-only corrected index geometry with explicit decision and literal single-bit regressions; B) defer the geometric view claim. Recommendation A under delegated D051, preserving pin/perception order. Decision needed: scoped correction of D088 presentation and affected unlocked expectations; no wiring or core behavior change. D107 uses an explicitly labeled index strip and does not resolve the production discrepancy.

2026-09-23 D105/D106 SC-AL follow-up: calibration delivery host-reviewed; exactd72bff70 default/Immediate/MATCH loader peaks261688/261688/260056 fit262144 after immutable native-table deduplication. D105-R2 closed within model scope; full-app loadedRAM and complete800us remain physically unmeasured.

2026-09-24 D108 OPP-VIEW-1 disposition: CLOSED in software under contract9ff7405. Only two renderer coordinates and corresponding unlocked oracle positions changed. Fullnormal/san1446main+187Gate PASS; exact618d3a96 default/MATCH target and separate review PASS. FinalELFs change only two read-only bytes; control/pins unchanged. See P2_display_channel_validation.md and review/raw. Optical orientation remains unmeasured; no gate.


## DUMP-RATE-1: full recorder exceeds legacy UART cadence (2026-09-24, OPEN)
Issue: D090 FIFO-disabled native TX, one Transfer step per1kHz epoch and the unchanged300s total limit cannot deliver all5001 frames. Sources: src/hal/dump_uart_unoq.cpp:267-293, src/hal/recorder_dump.cpp:298-331, config.h DUMP_*; full derivation in P2_native_dump_throughput_audit.md.
Consequence: frames alone require at least614013 wire bytes; at most2 bytes per nominal<80us call allows at most600000 bytes in300s. Fast host sinks do not establish native acceptance.
Options: A) explicit setup-only FIFO mode in the existing native owner, preserving legacy default, ownership/readiness/cancel checks and all byte/time budgets; B) leave native delivery blocked. Recommend A under D051/D075. No shorter recording or extended timeout is selected.
Decision needed: a separate D117 interface/setup/ownership contract and independent tests before changing native source. This is an engineering choice, not evidence that UART ownership/framing or measured service rate is qualified.
Regression/acceptance: unchanged legacy tests; serial-time8-entry FIFO reference model with full5001-frame/4096-event worst-width stream, no overflow, actual TC, deadlines and poison; exact target/startup/import/loader checks. Full-capacity source model fits212658 1kHz calls at8 stores,283574 at6; actual<80us/store service and hardware delivery remain unmeasured. Root arithmetic receipt: P2_recorder_transport_raw/coordinator/cadence_arithmetic.json.

DUMP-RATE-1 bound correction before D117 adoption: use unrestricted raw FR170 rather than semantically valid166. Corrected full-capacity217659 calls at8/288575 at6 still fit the300s model;5-store331091 exceeds it. No production budget changed. Original arithmetic retained; see F143 correction and P2_dump_fifo_test_preflight.md.

DUMP-RATE-1 D117 software disposition 2026-09-24T03:47:36.209335+04:00: explicit FIFO8 selection now passes
frozen independent normal/sanitizer native FIFO/serial-time/full-capacity tests,
unchanged legacy/factory/D116 checks, fullhost regressions and exact three-target
conditional fit audits. This resolves the selected software cadence design;
actual effective service rate and native delivery remain HARDWARE-PENDING.
The corrected unrestricted170-byte bound is retained. No budget/capacity reduction,
framing/ownership grant or human gate. P2_dump_fifo_validation.md has evidence.
SC-AL loadedRAM remainsopen; corrected appdefault has only8bytes modeled span.

SC-AL D118 actual default-image update 2026-09-24T04:42:52.533106+04:00: exactsourcee820c0e1/defaultM0 now has actual fullflashbracket/resident-sketch/progress and retainedheap evidence, independently reviewed744checks. Two262144B pool snapshots have4500free payload/4364largest; metadata agrees. This closes the narrowly scoped missing actual defaultload/retainedheap observation, preserving the historical8-byte conditional peak model. Stackspace, allsource/full800us timing, MATCH physical qualification and assembledrobot acceptance remain OPEN. Stored513us is not those proofs. See P2_app_default_actual_validation.md/F147; no config/grant/phasegate change.

## SC-AM: P2 B7 full reverse versus R6 authority (OPEN, D121 disposition)
Sources: docs/prompts/P2_hal_bench.md B7 requires20full-forward/full-reverse cycles; AGENTS.md R6 and BEHAVIOR.md B6 reserve full duty for centered contact. src/core/governor.cpp profileCap caps non-ATTACK below full; src/core/fsm.cpp frontDemand does not request full reverse in ATTACK; src/hal/motors.cpp independently checks full-duty ATTACK/centered/contact. Existing analysis: P2_motor_stand_feasibility.md, P2_after_D115_checkpoint.md and D115/D120.
Consequence: current actual Robot/Gate cannot honestly perform the specified full-reversal stress test. Fabricated contact, patched duties, a lower-duty substitute or direct pin path would conceal rather than resolve the conflict. The D1200.25sequence is B4 software evidence only.
Options: A) preserve R6 and the original B7 criterion, leave B7 blocked/unaccepted; B) separately define an explicit protected stress-test resolution, preserving sole MotorGate/full hold/edge/receipts and requiring fresh specific motor-run authorization.
Recommendation/disposition: A selected by D121 under D051/D075. No source, locked test, physical criterion or human gate changed. This is a visible requirements blocker, not grounds to build another controller or rerun solved checks.
Decision needed before dependent B7 work: a supported explicit resolution of the contradictory full-power trial and R6, followed by actual physical setup/run evidence. No exception or test weakening is approved in this checkpoint.
Regression/acceptance required for any later adopted change: independent exact-contract tests of full hold, governor limits/contact, reversal braking/slew, edge and STOP priority, real Gate write boundary and truthful finite cycle/uptime receipts; target fit/timing; the actual required20cycles on an authorized stand with no resets. Preserve all existing locked assertions unless specifically human-amended.

## SC-AN: P3 stopping-distance reference and post-escape rest (OPEN)
Sources: docs/prompts/P3_first_drive.md3.2-3.3 asks for R_room measured from first white to loss, but stopping distance from inner border to the robot front at rest. HARDWARE.md8 compares worst stop to70percent of R_room. BEHAVIOR.mdB4 executes reverse/pivot and sometimes forward escape segments after white.
Consequence: post-escape rest is not maximum outward travel. Different robot reference points or origins also make the numerical comparison invalid. Firmware has no measured translation source that could infer these distances from duty/yaw.
Options: A) retain the original border-to-front rest measurement with identified rest/orientation, and add independently measured maximum outward excursion in the same first-white/reference/direction coordinates as R_room; use that conservative comparison for any proposed search cap. B) retain the ambiguity and defer any cap recommendation.
Recommendation: A under D051, with an explicit decision before dependent measurement analysis. Do not silently replace the original reported metric or manufacture a conversion offset. A command timeout/no-edge trial is not a valid stopping measurement.
Needed decision/evidence: common spatial reference and measured first-white/loss/peak positions, run/build/duty/voltage provenance, and an evidence-backed human tuning approval before production SEARCH_DUTY_MAX changes. A finite isolated trial profile may be prepared without those measurements; it does not close this acceptance issue.
Regression/acceptance: reject missing/mismatched reference data, distinguish peak versus rest and no-edge timeout, preserve actual B4 escape/R1/R6, final electrical trial cap at low voltage, real applied receipts and explicit incomplete evidence. Physical3runs at each specified duty and actual R_room values remain required.

SC-AN software disposition (D126, 2026-09-24T07:48:31.258197+04:00): retain the original border-to-front at-rest measurement with orientation/rest identity, and separately measure peak outward excursion from the same first-white reference/direction used for R_room. No inferred conversion or duty-to-distance estimate. Only compatible measured peak/R_room data support the conservative70percent comparison; no-edge timeouts are excluded. No production cap changes or physical acceptance. Contract and tests: P3_stop_trial_contract.md / P3_stop_trial_validation.md.
