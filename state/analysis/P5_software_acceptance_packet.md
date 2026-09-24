# P5 software and physical acceptance

2026-09-24, Asia/Dubai. Software phase P5 proceeds under D134 and the user's
hardware-at-end instruction. Actual P4/P5 gates and every physical result below
remain pending. This packet requests no connection or motor run now.

SIDESTEP_R/L, DIRECT, ARC_R/L and WAIT already have core implementations and
specification tests from P1. D134 adds optional-mode removal in config, public
entry admission and the actual menu/Robot path. Its implementation passes full ordinary host regression, the four-pair
sanitizer matrix, private probes and tooling checks. Source-bound validation
and separate scoped review are retained; physical results remain pending.
See [the adopted contract](P5_mode_availability_contract.md).

| Original P5 requirement | Software coverage to retain | Physical acceptance still required |
|---|---|---|
|5.1 Static box | Opener phase progression and D034 current-perception handover; ATTACK needs consecutive centered observations and fresh contact for full duty. | Ten runs per accepted opener: at least9/10 ATTACK on the box and zero self-exits. |
|5.2 Charger proxy | SIDESTEP phase-specific aborts and WAIT's ordered approach cue followed by complete SIDESTEP_R under D055. | SIDESTEP/WAIT: actual pulled-box trials filmed at60fps, at least8/10 evade a frontal hit and reach its side. |
|5.3 Abort | Same observation routes current front to TRACK, side/rear to DEFEND_TURN, none to SEARCH. Existing centering qualification precedes ATTACK. Edge/STOP priority remains. | Ten actual path/abort trials with10/10 one-tick handover according to the accepted D034/D134 interpretation. |
|5.4 Mirrors | Existing pure motion/flank mirror tests; both ARC mirrors share one availability switch and retain their IDs. | Real L/R recorded heading traces within10degrees. Synthetic symmetry does not prove mechanics or yaw accuracy. |
|5.5 Mode UI | D134 bounded cycling skips unavailable modes, captures selection at accepted START release, preserves service order and historical display/log identities. | Operator selection under5s and readable matrix at arm's length. |

Physical priority is SIDESTEP_R/L, then DIRECT, then ARC_R/L, then WAIT; each
must pass before proceeding to the next physical block. The software matrix does
not certify that sequence. Parameters change only with actual logged evidence
and the existing tuning/review process. No pre-angled variant is assumed.

Mandatory SIDESTEP and DIRECT must pass. Optional ARC/WAIT must pass or be removed
through their config switches. All six remain enabled development defaults until
an actual acceptance or schedule disposition changes them; default-enabled does
not mean qualified for competition. MODE_DEFAULT must select an enabled mode.
Keep historical mode IDs1..6 readable after removal.

The end28September P3 scope-cut rule remains tied to an actual human gate. If
triggered, set both optional switches0 with a recorded decision; retain mandatory
modes and recorder. P6 needs actual GATE P4 by30September and no stronger cut.
Freeze is1October21:00 Dubai. No v1.0 tag, rehearsal or competition success follows
from this software packet. A later motor-capable run still requires its specific
fresh STAND OK or RING OK, a reviewed artifact and verified setup.

Native image/loader fit, loaded RAM/stack, full-source tick below800us, sensors,
button circuit/calibration and the earlier phase acceptance remain separate
dependencies. Preserve actual logs and outcomes; do not substitute host results
or favorable synthetic traces for required runs.
