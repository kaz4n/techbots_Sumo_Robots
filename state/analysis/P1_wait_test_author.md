# P1 independent WAIT test author

Date: 2026-09-23, Asia/Dubai. P1 host-only under D-016.

Objective: protect public contract 032eedb, B12 O4/O1, B7/B6/B9 and approved
D-033/D-034/D-055 independently of implementation. Owned files are
`tests/test_wait.cpp` and this report. Sources were the specifications, decisions,
public headers and existing test conventions only. No core implementation cpp was
read, and no existing tests, configuration, headers, build files or ledgers were
modified. No build, hardware operation or commit was performed by this author.

Thirty-three new cases assert literal defaults and cover the ordered approach
window at 299999/300000/300001 microseconds; continuous FC; simultaneous first
fronts; pre-held flanks; a different newly rising flank; clear/reassert; clear-only
rearm; and no refresh of an expired episode. Every initial byte mask is checked,
including unused high bits. Front alone retains the hold, while side/rear abort
wins over cue, expiry and an otherwise invalid healthy yaw.

Deadline cases include just before, exactly at and after two seconds, including
a valid cue on the first delayed observation after WAIT expiry. Expired cues do
not revive WAIT. Healthy nonfinite yaw is rejected before cue/expiry when no
side/rear exit exists; unavailable yaw preserves the last finite coordinate.
Finite extreme headings, invalid start, restart/reset, repeated wrap episodes
and the largest legal single uint32 observation gap are covered.

Delegation checks the complete RIGHT50 pivot for either or both approach flanks,
all byte masks in PIVOT/TRAVERSE/TURN_IN, phase-specific front/outer priority,
the 250 ms drive and captured fixed LEFT110 turn, strict five-degree completion,
no retargeting by later bearing payload, per-observation segment time anchors,
100 ms initial pivot fallback with recovery, both 700 ms timeout pulses, and
one-shot terminal/phase/approach behavior. WAIT's timer stops after the cue.
The original Flank is directly exercised by a new mirrored precision regression:
RIGHT50 from raw origin -1e-6F must advance at yaw45F, while zero and positive
origin boundaries remain active. Existing Flank tests are unchanged.

Actual Governor composition at 9 V checks immediate HOLD braking from previous
full ATTACK duty, final pivot/turn cap 0.80, traverse cap 0.85, external permission
inhibition and immediate terminal zero. A separate NormalPerception/frontDemand
composition confirms a script exit counts only its first new centered observation
toward the three-observation threshold and has no contact authorization. This is
component wiring in a test harness, not full Robot/MotorGate, sensor freshness,
physical matador success, motor-run or phase-gate evidence.

Static handoff: 33 cases; CHECK/CHECK_FALSE only; no throwing checks, trailing
whitespace or diff-check findings. Public function/test blocks remain below 60
lines. Tests are frozen for the coordinator's full host/sanitizer builds and
independent review. Runtime validation remains pending. Preserve independent
expectations if an implementation fails.
