# P2 software acceptance checkpoint review

2026-09-24, 05:26 Asia/Dubai. Reviewed software HEAD
`1c2389c9ea0d7d35cad3af63d8a18c2f41382e93`; latest change range
`1c387810..1c2389c9`, including D120 contract `f4a300c5`. Separate same-model
Codex context, read-only production/test review. This is a consolidated readiness
and gap review, not a new exhaustive audit of every historical P2 source line.

## Findings

No new BLOCKER, MAJOR or MINOR **software defect** was established in the
inspected critical paths, D120 diff or acceptance packet. The following are
**open full-phase acceptance blockers**, already acknowledged by the packet;
they are not newly discovered implementation regressions.

- **[BLOCKER, P2-ACCEPT-1] `docs/prompts/P2_hal_bench.md:35`: assembled B1-B8
  acceptance and hardware-checked facts are incomplete.** Opponent polarity,
  ranges and empty-ring false hits; QTR black/white/brown qualification; IMU
  drift/rotation; motor direction/brake/coast/PWM/kill behavior; battery accuracy;
  and real button/display behavior have no complete accepted physical result.
  `docs/HARDWARE.md:53` still labels the pin map proposed, and its electrical
  checklist at line 212 remains open. Obtain and record the original measurements
  before closing these criteria. Preserve the existing bare-board restrictions
  until a separately authorized physical task is available.
- **[BLOCKER, P2-ACCEPT-2] `docs/prompts/P2_hal_bench.md:28`: the five-minute,
  all-sources-live timing result is absent.** D118's recorded 513 us maximum,
  zero sampled missed releases and retained heap are valid limited observations;
  initialization and optional source grants were false. They do not establish
  full-source worst case below 800 us, p99, timeout/fault cost or stack headroom.
  Measure the required configured runtime and retain its source/profile identity,
  timing distribution and memory evidence. See `state/FACTS.md:546` and
  `state/TUNING_LOG.md:350` for the current narrow result.
- **[BLOCKER, P2-ACCEPT-3] `docs/prompts/P2_hal_bench.md:17`: B7 remains
  incompatible with the preserved full-duty authority and is unperformed.** Its
  twenty full-forward/full-reverse cycles cannot be supplied by ordinary reverse
  profiles or D120's 0.25 capped sequence. `src/core/governor.cpp:21` and
  `src/hal/motors.cpp:136` retain centered-contact ATTACK qualification; genuine
  ATTACK does not request full reverse. The packet's D121 disposition correctly
  leaves B7 BLOCKED / NOT ACCEPTED. Preserve the criterion and R6 pending an
  explicit protected resolution; then require the actual specifically authorized
  powered trial and reset evidence. No exception is granted by this review.
- **[BLOCKER, P2-ACCEPT-4] `docs/prompts/P2_hal_bench.md:18`: native B8 delivery
  and live 200-second recording acceptance remain unproved.** The full synthetic
  recorder/strict receiver roundtrip and FIFO model are software evidence.
  `state/analysis/P2_native_dump_prerequisite_followup.md:31` records incomplete
  UART-holder visibility; clean cancel/reopen and framing are also unproved.
  Resolve the actual prerequisites and retain the real complete source/dump
  comparison, loss/lifecycle fields and free-memory result. An open socket,
  ready pin or synthetic stream cannot close this blocker.
- **[BLOCKER, P2-ACCEPT-5] `docs/prompts/P2_hal_bench.md:37`: the complete gate
  prerequisites and human GATE P2 PASS are absent.** Assembled mass/footprint
  (line 31), physical P0/PINMAP acceptance and P1 EXPLAINED/human gate remain
  pending. This checkpoint supplies neither full-phase safety acceptance nor a
  human gate. Complete the original evidence and review requirements, then retain
  the human's actual gate entry; do not promote a scoped software PASS into one.

## Scope and source checks

Read the complete root AGENTS.md, REVIEW_GATE, P2 prompt, current handoff and
execution checklist, relevant PROGRESS/DECISIONS including D051/D075/D119/D120/D121,
PLAN section 3, relevant HARDWARE/BEHAVIOR sections and FACTS/TUNING evidence.
The actual date is Thursday 24 September, the planned bench-preparation day;
neither the 28 September scope-cut deadline nor the 1 October freeze has arrived.
D051/D075 permit current software work and do not supply physical acceptance.
No nested AGENTS.md was found under the reviewed source/test/bench/state paths.

The request is the coordinator's
`state/analysis/P2_software_acceptance_packet.md`. Every linked existing evidence
entry point resolves locally; this review fills its initially absent report link.
The packet expressly claims no assembled-robot exit criterion or phase pass and
correctly retains the B7 conflict. The concurrent D121 ledger entry and SC-AM
record preserve that unresolved requirement without adding an exception.
Earlier scoped review findings were read with
their later closure evidence, including D099/D100 for the earlier app compiler
capacity blocker, D102 for D101-R1 and D106 for D105-R2. Original failed artifacts
remain historical evidence rather than current passing images.

Critical source inspection covered the actual app/Runtime/Transaction route,
MotorGate and native motor callbacks, countdown release qualification, Robot
permission/edge/final-output arbitration, governor, dump authority/native UART,
and representative acquisition/deadline paths. The complete latest production,
profile, host-build and checked-build tooling diff was read.

| Rule | Current source evidence and review conclusion |
| --- | --- |
| R1 | `src/core/countdown.cpp:142` anchors Gate on the qualified decision tick; Gate at line 11 preserves the full configured hold. `src/hal/motors.cpp:107` independently arms on the actual release, checks the same hold and denies invalid permission. Transaction at `src/app/transaction.cpp:99` applies the genuine Robot result and retains its token receipt. Native EN/PWM callbacks at `src/hal/motor_port_unoq.cpp:288` and line 305 are reached through MotorGate's port operations; no separate motion writer was found. Gate setup writes LOW before PWM setup, and each transaction orders LOW, four PWM writes, settle, optional HIGH. This is source/host evidence, not measured pin behavior. |
| R2/R3 | Source search found no Wi-Fi, Bluetooth, serial or Bridge motion-command input. The native dump path is transmit-only. `src/app/runtime_dump.cpp:27` requires actual inhibited IDLE and a valid applied receipt; native `ready()` and each bounded transmit step check readiness. `src/hal/loop_hook.cpp:4` supplies the empty loop hook instead of stock blocking Bridge update. D120's wrapper has no dump port. Existing pinned startup/native qualification limits remain; no new Linux-availability claim follows. |
| R4 | `src/app/runtime.cpp:315` schedules from unsigned microsecond deadlines and rejects invalid clock ordering. Acquisition, decision, apply, post-work and completion belong to one Transaction lifetime. Runtime service loops, motor settle, ADC polling/cleanup, I2C work and UART transmit have finite count/time guards. The inspected application paths introduce no delay, heap allocation or Arduino String. The async QTR frame may span ticks by approved D085 design; its 2500 us frame bound is not a tick WCET. Bounded source work alone does not prove the 800 us target. |
| R5 | `src/core/fsm_robot.cpp:364` evaluates escape after lifecycle permission and before motion routing. The ordinary route at line 422 and D120 `src/core/fsm_stand.cpp:12` preserve permission/STOP and edge priority. Edge at GO/completion wins; an active or faulted escape is not stopped merely because the sequence was cancelled. |
| R6 | `src/core/fsm_robot.cpp:735` performs the final genuine contact commitment and Governor pass. `src/core/governor.cpp:17` applies compensation before final profile cap and slew, with immediate brake/inhibit/reduction. Nonfinite duty/voltage becomes inhibited output; `src/hal/motors.cpp:14` independently rejects nonfinite duties. D120 uses the final electrical STAND_DUTY cap, while escape retains its existing caps. The Gate independently reserves full duty for centered-contact ATTACK. |

D120's compiler-wide profile defaults off, rejects MATCH, and refuses the D103
service reset. Its dedicated wrapper statically requires MATCH0/M0 and supplies
empty setup grants. The checked tooling diff adds only that literal compile-only
profile; it does not extend upload permission. Natural completion/escape exit
inhibits immediately and requests actual lifecycle STOP on the next distinct
tick. No source, permission, contact or receipt is manufactured. These boundaries
are consistent with the already completed scoped D120 review.

Explainability at the reviewed boundary remains concrete: sensors produce
qualified inputs, Robot chooses one governed request, and MotorGate alone applies
it after hold/receipt checks. The finite stand profile substitutes a bounded
request sequence while keeping that same safety route. Native ownership checks
are substantial, but no new material explainability defect was established in
this bounded review. A student's EXPLAINED OK is still not inferred.

## Evidence reused and additional checks

No host suite, target build, board operation or historical API research was
repeated. The latest source-only inspection gave no concrete reason to rerun
the already completed suites. Reused:

- `state/reviews/P2_stand_integration_review.md` and its archived
  `reviewer/final_evidence.json`: all four normal and ASan/UBSan CTest targets
  passed. Preserved sanitizer counts are main 1496, enabled Gate 187, stand M0
  18 and stand M1 18; configured A1 fixtures passed 19 each in both profiles.
  Normal four-target status/output exists, but its transient LastTest archive
  was lost; do not describe its detailed counts as newly reproduced.
- The same scoped review's 54 policy checks, nine private profile probes and
  `reviewer/target_evidence.json`: default/M0 ELF/ZSK/loader remain byte-identical
  to the D118 loadables. The default conditional pristine-loader free span is
  8 bytes; the separate stand image's span is 13568 bytes. Neither is a measured
  loaded-memory or stack reading. D118's separate actual review supports 4500
  free / 4364 largest retained heap bytes for its exact inhibited image only.
- Direct `git diff --name-status 1c387810..HEAD -- tests/locked` shows only the
  **addition** of `test_stand_integration_safety.cc`; established locked tests
  are unchanged in this range. Its current SHA256 independently matches the
  frozen oracle `4546df243377a915693a52d347ab9e3f0877ad504bf9d087f8667b824425ff1b`.
  Named B3/R1, B4/R5 and B14 cases exercise actual Gate hold/wrap, STOP, edge,
  source/receipt failure and duplicate handling. Ordinary cases cover all
  twelve phases, final caps/slew and actual service-reset refusal. This is
  additive safety coverage, not approval to amend any established locked test.

Historical scopes were reused as stated; this report does not certify every
line of every original artifact anew. No new physical number, board connection,
permission or gate is asserted. Reviewer modifications are limited to this file;
the coordinator's concurrent packet/ledger edits were preserved.

## Verdict

**PASS for this bounded software/readiness checkpoint and the packet's limited
evidence characterization. No new software finding is open in this scope.**

**FAIL for full P2 phase acceptance / GATE P2:** P2-ACCEPT-1 through
P2-ACCEPT-5 remain open. Existing scoped software PASS results remain valid
within their own recorded versions and limits; they do not close these blockers.

Next action: coordinator records and commits the checkpoint, retaining B7
BLOCKED / NOT ACCEPTED and the existing physical/native dependencies. Resume
dependent acceptance work only when its actual prerequisite is supplied. This
review requests no board action and grants no upload, motor run or human gate.
