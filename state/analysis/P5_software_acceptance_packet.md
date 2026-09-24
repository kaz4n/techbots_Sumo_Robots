<!-- Maps the original P5 tasks to software and outstanding physical evidence. -->
<!-- Preserves mandatory opener priority and human gate ownership. -->
<!-- Checked against P5_openers.md and the linked source-bound validation records. -->
# P5 software acceptance packet

2026-09-24 Asia/Dubai. P5 software work is complete and scoped-reviewed in
0faf2e6d; **all physical P5 metrics remain pending**. D137 advances only P7
document preparation. The user reports a bare UNO Q and requests no additional
hardware now. No assumed acceptance is a measurement or GATE P5 PASS.

The original priority remains SIDESTEP_R/L, DIRECT, optional ARC_R/L, then WAIT.
The six implementations already exist. D134 makes optional modes removable
through reviewed config values while preserving stable IDs and mandatory modes;
[validation](P5_mode_availability_validation.md) and its separate review pass.
Current ARC/WAIT flags remain1. Software tests do not establish physical passes.
Each physical opener block must pass before the next priority starts; no
pre-angled variant is assumed. MODE_DEFAULT must select an enabled mode, and
historical IDs1..6 remain readable even when an optional mode is removed.

| Original task | Available software | Required real evidence |
|---|---|---|
|5.1 Static box|Actual opener/FSM, governor/contact qualification and edge paths are host-tested.|Ten trials per included opener: at least9/10 eventually ATTACK on the box, zero self-exits. Record every result.|
|5.2 Charger proxy|SIDESTEP phase priorities and WAIT approach/inner sidestep are implemented.|SIDESTEP and WAIT: ten string-pulled charger trials,60fps video; at least8/10 avoid frontal impact and reach the box side.|
|5.3 Abort|D135 actual predicate/phase, current route and applied receipt are implemented and reviewed (70c964a7). D136 analyzer passes93public/19private checks and separate scoped review (5277dec0); original failures are retained.|Ten original trials per included opener, all meet the qualified one-tick bound. Resolve source/clock/transport/run prerequisites; no favorable replacement of exclusions or failures.|
|5.4 Mirror|Mirrored opener logic and host symmetry checks exist.|Actual L/R heading traces agree within10degrees. A host symmetry property is not physical heading accuracy.|
|5.5 Mode UI|Bounded available-mode navigation and matrix projection are implemented/tested.|Operator selects every available mode within5seconds and reads confirmation at arm's length. Bare-board compilation cannot verify operator or display acceptance.|

P5.3 follows D034/D134: a current front cue routes through TRACK and still needs
the configured centered-observation qualification before ATTACK. A side/rear cue
routes to DEFEND_TURN; a saved snapshot alone cannot authorize ATTACK. The trace
bound A-D<=TICK_US concerns qualified logical detection to matched application,
not physical box onset, first PWM edge, mechanical reaction or complete tick WCET.
Periodic25Hz frames and60fps video alone cannot establish that1000us bound.

Read [D135 validation](P5_abort_timing_validation.md) for exact passing checks,
preserved first failures and completed scoped review. Its inert native wrapper compiles
and fits the retained loader model with1328B free; it omits the default native
dump transport. The D134 default app has a32B modeled deficit; two isolated candidates failed
by24/32B and remain unadopted. Unmodified D135default has not been compiled.
The separate unchanged MATCH/Immediate image compiles and has1584B conditional
loader span, with62imports resolved; [validation](P5_match_native_validation.md)
and its independent review pass. These are file/compiler
results, not live stack/RAM acceptance or a deployable motor-run artifact.

Future physical trials need the existing P0-P4 acceptance, actual sensors/button
windows/pin/electrical qualification, a source-bound runnable image, recorder
delivery, calibrated timing and fresh identified RING OK. Current empty setup
grants and compile-only wrappers do not provide those conditions. The user is
not being asked to connect any further hardware during this software session.

Keep source revision/config, original log bundles, full trial order, exclusions,
video and measurement paths in the existing evidence workflow. Any tuning needs
its actual supporting readings in TUNING_LOG; no parameters changed for this packet.
Optional openers must pass or be removed from the menu. The actual end28September
P3 scope cut, P6 eligibility and1October21:00 freeze still apply. Final P5 closure
requires independent review with no BLOCKER and the human's GATE P5 PASS.
If the scope cut applies, record the decision and set both optional availability
flags0, retaining mandatory openers and the recorder. This packet creates no
release tag, rehearsal result or competition qualification.

[D136 final validation](P5_abort_analysis_validation.md) records the93public,
19private and112unchanged-dependency checks. The input grammar, source hashes and
conditional MATCH loader result do not establish real trials or a human P5 gate.
