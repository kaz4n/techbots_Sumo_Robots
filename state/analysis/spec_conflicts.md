# Open specification conflicts — 2026-09-22

Verified against the supplied files, not hardware. Recommendations are UNAPPROVED
except SC-C (D-017), SC-D1 (D-018), SC-J's START anchor (D-019) and SC-D2's
persistent/all-white policy (D-020), and SC-M (D-021), explicitly approved below. User's later
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
For the next human decision, present its options using AGENTS section 9 CONFUSION
format and record the exact answer in a new DECISIONS entry before dependent work.

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
